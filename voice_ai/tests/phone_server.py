import os
import sys
import asyncio
import logging
import base64
import numpy as np
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from livekit import api

# Ajouter le chemin du web_app pour les imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'web_app'))

from voice_processor import VoiceProcessor

load_dotenv()

# Configuration
LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")

# Configuration SIP
SIP_SERVER = os.getenv("SIP_SERVER", "sip.africasys.com")
SIP_USERNAME = os.getenv("SIP_USERNAME", "phone_agent")
SIP_PASSWORD = os.getenv("SIP_PASSWORD", "AfricaSys2024!")
PHONE_NUMBER = os.getenv("PHONE_NUMBER", "+33612345678")

app = Flask(__name__)
CORS(app)

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PhoneCallManager:
    """Gestionnaire des appels téléphoniques"""
    
    def __init__(self):
        self.voice_processor = VoiceProcessor()
        self.active_calls = {}  # room_name -> call_info
        self.livekit_api = None
        
    async def initialize(self):
        """Initialise l'API LiveKit"""
        self.livekit_api = api.LiveKitAPI(LIVEKIT_API_KEY, LIVEKIT_API_SECRET, LIVEKIT_URL)
        logger.info("✅ LiveKit API initialisée")
        
    async def create_phone_call(self, caller_number):
        """Crée un nouvel appel téléphonique"""
        try:
            # Créer une room pour l'appel
            room_name = f"phone_call_{int(asyncio.get_event_loop().time())}"
            participant_identity = f"caller_{caller_number}_{int(asyncio.get_event_loop().time())}"
            
            # Créer un token pour la room
            token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET) \
                .with_identity(participant_identity) \
                .with_name(f"Caller {caller_number}") \
                .with_grants(api.VideoGrants(
                    room_join=True,
                    room=room_name,
                    can_publish=True,
                    can_subscribe=True,
                    can_publish_data=True
                ))
            
            jwt_token = token.to_jwt()
            
            # Marquer l'appel comme actif
            self.active_calls[room_name] = {
                'caller_number': caller_number,
                'participant_identity': participant_identity,
                'start_time': asyncio.get_event_loop().time(),
                'room_name': room_name,
                'token': jwt_token,
                'status': 'active'
            }
            
            logger.info(f"📞 Appel créé: {caller_number} -> {room_name}")
            
            return {
                'success': True,
                'room_name': room_name,
                'participant_identity': participant_identity,
                'token': jwt_token,
                'caller_number': caller_number
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur création appel: {e}")
            return {'success': False, 'error': str(e)}
    
    async def process_phone_audio(self, room_name, audio_data):
        """Traite l'audio téléphonique avec le pipeline vocal"""
        try:
            if room_name not in self.active_calls:
                return {'success': False, 'error': 'Appel non trouvé'}
            
            logger.info(f"🎤 Traitement audio téléphonique: {room_name}")
            
            # Convertir l'audio en numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            # Utiliser le pipeline vocal optimisé
            response_audio, response_text = await self.voice_processor.process_audio_optimized(audio_array)
            
            if response_audio:
                logger.info(f"🗣️ Réponse générée: {response_text[:50]}...")
                
                # Encoder l'audio réponse en base64
                response_audio_b64 = base64.b64encode(response_audio).decode('utf-8')
                
                return {
                    'success': True,
                    'text': response_text,
                    'audio': response_audio_b64,
                    'room_name': room_name
                }
            else:
                logger.warning("⚠️ Pas de réponse audio générée")
                return {
                    'success': False,
                    'text': response_text if response_text else "Désolé, je n'ai pas pu générer de réponse.",
                    'audio': None
                }
                
        except Exception as e:
            logger.error(f"❌ Erreur traitement audio téléphone: {e}")
            return {'success': False, 'error': str(e)}
    
    async def end_phone_call(self, room_name):
        """Termine un appel téléphonique"""
        try:
            if room_name not in self.active_calls:
                return {'success': False, 'error': 'Appel non trouvé'}
            
            call_info = self.active_calls[room_name]
            duration = asyncio.get_event_loop().time() - call_info['start_time']
            
            # Générer message de fin
            goodbye_text = "Merci pour votre appel. Au revoir !"
            audio_response = await self.voice_processor.text_to_speech_optimized(goodbye_text)
            
            # Marquer comme terminé
            call_info['status'] = 'ended'
            call_info['end_time'] = asyncio.get_event_loop().time()
            call_info['duration'] = duration
            
            logger.info(f"📞 Appel terminé: {room_name} (durée: {duration:.1f}s)")
            
            result = {
                'success': True,
                'duration': duration,
                'caller_number': call_info['caller_number'],
                'goodbye_text': goodbye_text
            }
            
            if audio_response:
                result['goodbye_audio'] = base64.b64encode(audio_response).decode('utf-8')
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur fin d'appel: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_active_calls(self):
        """Retourne la liste des appels actifs"""
        return {
            room_name: {
                'caller_number': info['caller_number'],
                'status': info['status'],
                'duration': asyncio.get_event_loop().time() - info['start_time'] if info['status'] == 'active' else info.get('duration', 0)
            }
            for room_name, info in self.active_calls.items()
        }
    
    def get_call_stats(self):
        """Retourne les statistiques des appels"""
        total_calls = len(self.active_calls)
        active_calls = len([c for c in self.active_calls.values() if c['status'] == 'active'])
        
        return {
            'total_calls': total_calls,
            'active_calls': active_calls,
            'ended_calls': total_calls - active_calls,
            'phone_number': PHONE_NUMBER,
            'sip_server': SIP_SERVER
        }

# Instance globale
call_manager = PhoneCallManager()

@app.route('/')
def index():
    """Page d'accueil du serveur téléphonique"""
    return jsonify({
        'service': 'Agent Téléphonique AfricaSys',
        'status': 'running',
        'phone_number': PHONE_NUMBER,
        'endpoints': [
            '/create_call',
            '/process_audio',
            '/end_call',
            '/active_calls',
            '/stats'
        ]
    })

@app.route('/create_call', methods=['POST'])
def create_call():
    """Crée un nouvel appel téléphonique"""
    try:
        data = request.get_json()
        caller_number = data.get('caller_number', '+33600000000')
        
        # Créer l'appel de manière asynchrone
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(call_manager.create_phone_call(caller_number))
        loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Erreur endpoint create_call: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/process_audio', methods=['POST'])
def process_audio():
    """Traite l'audio téléphonique"""
    try:
        data = request.get_json()
        room_name = data.get('room_name')
        audio_base64 = data.get('audio')
        
        if not room_name or not audio_base64:
            return jsonify({'success': False, 'error': 'room_name et audio requis'}), 400
        
        # Décoder l'audio
        audio_bytes = base64.b64decode(audio_base64)
        
        # Traiter l'audio de manière asynchrone
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(call_manager.process_phone_audio(room_name, audio_bytes))
        loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Erreur endpoint process_audio: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/end_call', methods=['POST'])
def end_call():
    """Termine un appel téléphonique"""
    try:
        data = request.get_json()
        room_name = data.get('room_name')
        
        if not room_name:
            return jsonify({'success': False, 'error': 'room_name requis'}), 400
        
        # Terminer l'appel de manière asynchrone
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(call_manager.end_phone_call(room_name))
        loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Erreur endpoint end_call: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/active_calls', methods=['GET'])
def get_active_calls():
    """Retourne la liste des appels actifs"""
    try:
        return jsonify({
            'success': True,
            'calls': call_manager.get_active_calls()
        })
    except Exception as e:
        logger.error(f"❌ Erreur endpoint active_calls: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Retourne les statistiques des appels"""
    try:
        return jsonify({
            'success': True,
            'stats': call_manager.get_call_stats()
        })
    except Exception as e:
        logger.error(f"❌ Erreur endpoint stats: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health')
def health():
    """Vérifie la santé du serveur"""
    return jsonify({
        'status': 'ok',
        'service': 'Agent Téléphonique AfricaSys',
        'phone_number': PHONE_NUMBER
    })

async def initialize_server():
    """Initialise le serveur"""
    await call_manager.initialize()
    logger.info("🚀 Serveur téléphonique initialisé")

if __name__ == '__main__':
    print("="*60)
    print("📞 SERVEUR AGENT TÉLÉPHONIQUE AFRICASYS")
    print("="*60)
    print(f"📍 URL: http://localhost:5001")
    print(f"📞 Numéro: {PHONE_NUMBER}")
    print(f"🔗 SIP: {SIP_SERVER}")
    print("🎤 Pipeline vocal: Deepgram + ElevenLabs")
    print("="*60)
    
    # Initialiser le serveur
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(initialize_server())
    loop.close()
    
    # Démarrer le serveur Flask
    app.run(debug=True, host='0.0.0.0', port=5001)
