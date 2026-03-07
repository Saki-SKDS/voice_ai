import os
import sys
import asyncio
import logging
from dotenv import load_dotenv
from livekit import api

# Ajouter le chemin du web_app pour les imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'web_app'))

from voice_processor import VoiceProcessor

load_dotenv()

# Configuration
LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")

# Configuration SIP (simulation pour le POC)
SIP_SERVER = os.getenv("SIP_SERVER", "sip.africasys.com")
SIP_USERNAME = os.getenv("SIP_USERNAME", "phone_agent")
SIP_PASSWORD = os.getenv("SIP_PASSWORD", "AfricaSys2024!")
PHONE_NUMBER = os.getenv("PHONE_NUMBER", "+33612345678")

class PhoneAgent:
    """Agent vocal téléphonique simplifié pour POC"""
    
    def __init__(self):
        self.voice_processor = VoiceProcessor()
        self.active_calls = {}  # room_name -> call_info
        
        # Configuration logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # LiveKit API sera initialisée plus tard
        self.livekit_api = None
        
    async def simulate_incoming_call(self):
        """Simule un appel entrant pour le POC"""
        try:
            # Initialiser LiveKit API dans le contexte async
            if self.livekit_api is None:
                self.livekit_api = api.LiveKitAPI(LIVEKIT_API_KEY, LIVEKIT_API_SECRET, LIVEKIT_URL)
            
            self.logger.info("📞 Simulation appel entrant...")
            
            # Créer une room pour l'appel
            room_name = f"phone_call_{int(asyncio.get_event_loop().time())}"
            participant_identity = f"phone_user_{int(asyncio.get_event_loop().time())}"
            
            # Créer un token pour la room
            token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET) \
                .with_identity(participant_identity) \
                .with_name("Phone User") \
                .with_grants(api.VideoGrants(
                    room_join=True,
                    room=room_name,
                    can_publish=True,
                    can_subscribe=True,
                    can_publish_data=True
                ))
            
            jwt_token = token.to_jwt()
            
            self.logger.info(f"✅ Room créée: {room_name}")
            self.logger.info(f"👤 Participant: {participant_identity}")
            
            # Marquer l'appel comme actif
            self.active_calls[room_name] = {
                'participant_identity': participant_identity,
                'start_time': asyncio.get_event_loop().time(),
                'room_name': room_name,
                'token': jwt_token
            }
            
            # Envoyer un message d'accueil
            welcome_text = "Bonjour, je suis l'agent vocal AfricaSys. Comment puis-je vous aider ?"
            
            # Générer l'accueil vocal
            audio_response = await self.voice_processor.text_to_speech_optimized(welcome_text)
            
            if audio_response:
                self.logger.info("🎤 Accueil vocal généré")
                self.logger.info(f"📞 Appel simulé prêt dans room: {room_name}")
                self.logger.info(f"🎫 Token: {jwt_token[:50]}...")
                
                # En production, il faudrait utiliser le token pour connecter un client SIP
                return {
                    'success': True,
                    'room_name': room_name,
                    'participant_identity': participant_identity,
                    'token': jwt_token,
                    'welcome_audio': audio_response
                }
            else:
                self.logger.warning("⚠️ Pas d'accueil vocal généré")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Erreur simulation appel: {e}")
            return None
    
    async def process_phone_audio(self, room_name, audio_data):
        """Traite l'audio téléphonique"""
        try:
            self.logger.info(f"🎤 Traitement audio téléphonique: {room_name}")
            
            # Utiliser le pipeline vocal optimisé
            response_audio, response_text = await self.voice_processor.process_audio_optimized(audio_data)
            
            if response_audio:
                self.logger.info(f"🗣️ Réponse générée: {response_text[:50]}...")
                return {
                    'success': True,
                    'text': response_text,
                    'audio': response_audio
                }
            else:
                self.logger.warning("⚠️ Pas de réponse audio générée")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Erreur traitement audio téléphone: {e}")
            return None
    
    async def end_call(self, room_name):
        """Termine un appel"""
        try:
            if room_name in self.active_calls:
                call_info = self.active_calls[room_name]
                duration = asyncio.get_event_loop().time() - call_info['start_time']
                
                self.logger.info(f"📞 Appel terminé: {room_name} (durée: {duration:.1f}s)")
                
                # Envoyer message de fin
                goodbye_text = "Merci pour votre appel. Au revoir !"
                audio_response = await self.voice_processor.text_to_speech_optimized(goodbye_text)
                
                if audio_response:
                    self.logger.info("🎤 Message de fin généré")
                
                # Nettoyer
                del self.active_calls[room_name]
                
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Erreur fin d'appel: {e}")
            return False
    
    def get_active_calls(self):
        """Retourne la liste des appels actifs"""
        return {
            room_name: {
                'participant': info['participant_identity'],
                'duration': asyncio.get_event_loop().time() - info['start_time']
            }
            for room_name, info in self.active_calls.items()
        }

# Instance globale
phone_agent = PhoneAgent()

async def main():
    """Point d'entrée principal pour le POC téléphonique"""
    print("="*60)
    print("📞 AGENT TÉLÉPHONIQUE AFRICASYS - POC")
    print("="*60)
    
    try:
        # Simuler un appel entrant
        call_result = await phone_agent.simulate_incoming_call()
        
        if call_result:
            print("✅ Appel simulé avec succès")
            print(f"📞 Room: {call_result['room_name']}")
            print(f"👤 Participant: {call_result['participant_identity']}")
            print("🎤 Accueil vocal généré")
            print("📡 Token LiveKit disponible")
            
            # Simuler traitement audio (en production, viendrait du flux audio SIP)
            print("\n🎤 En attente de traitement audio...")
            print("(En production, l'audio viendrait du flux SIP)")
            
            # Simuler fin d'appel après 30 secondes
            await asyncio.sleep(30)
            
            await phone_agent.end_call(call_result['room_name'])
            print("✅ Appel terminé avec succès")
            
        else:
            print("❌ Erreur simulation appel")
            
    except KeyboardInterrupt:
        print("\n👋 Arrêt de l'agent téléphonique")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    asyncio.run(main())
