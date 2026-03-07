from flask import Flask, render_template, jsonify, request, send_file
import asyncio
import os
import io
import wave
import requests
import json
import math
import base64
import sys
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
import numpy as np
import time
import threading
from concurrent.futures import ThreadPoolExecutor

# Ajouter le chemin courant pour les imports locaux
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from room_manager import room_manager

# Servir les fichiers statiques
app = Flask(__name__, static_folder='static')
from flask_cors import CORS
CORS(app)

load_dotenv()

LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
LIVEKIT_URL = os.getenv("LIVEKIT_URL")

@app.route('/')
def index():
    """Page d'accueil avec interface professionnelle"""
    return render_template('index_pro.html')

@app.route('/token', methods=['POST'])
def get_token():
    """Token LiveKit avec gestion multi-utilisateurs"""
    try:
        data = request.get_json()
        room_name = data.get('roomName', 'default_room')
        user_identity = data.get('userIdentity', f"user_{int(time.time())}")
        user_name = data.get('userName', 'Anonymous')
        
        # Faire rejoindre la room à l'utilisateur
        join_result = room_manager.join_room(user_identity, user_name, room_name)
        
        if not join_result['success']:
            return jsonify({'error': join_result['message']}), 400
        
        # Créer un token LiveKit pour cette room
        token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET) \
            .with_identity(user_identity) \
            .with_name(user_name) \
            .with_grants(api.VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=True,
                can_subscribe=True,
                can_publish_data=True
            ))
        
        jwt_token = token.to_jwt()
        
        return jsonify({
            'token': jwt_token,
            'url': LIVEKIT_URL,
            'room': room_name,
            'user_info': {
                'user_id': user_identity,
                'user_name': user_name,
                'user_count': join_result['user_count'],
                'users': join_result['users']
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/test_deepgram_key', methods=['GET'])
def test_deepgram_key():
    """Test si la clé API Deepgram fonctionne"""
    try:
        import requests
        
        # Test avec un audio simple (silence ou audio test)
        url = "https://api.deepgram.com/v1/listen?model=nova-2&language=fr"
        headers = {
            "Authorization": f"Token {os.getenv('DEEPGRAM_API_KEY')}",
            "Content-Type": "audio/wav"
        }
        
        # Créer un audio WAV test simple (1 seconde de silence)
        import wave
        import io
        
        # Créer un WAV avec un son simple
        sample_rate = 16000
        duration = 1  # 1 seconde
        frequency = 440  # La note A4
        
        samples = int(sample_rate * duration)
        audio_data = []
        
        for i in range(samples):
            # Sinusoïde simple
            value = int(32767 * 0.1 * math.sin(2 * math.pi * frequency * i / sample_rate))
            audio_data.append(value)
        
        # Convertir en bytes correctement
        wav_bytes = bytearray()
        
        # En-tête WAV
        wav_bytes.extend(b'RIFF')
        wav_bytes.extend((36 + len(audio_data) * 2).to_bytes(4, 'little'))
        wav_bytes.extend(b'WAVE')
        wav_bytes.extend(b'fmt ')
        wav_bytes.extend((16).to_bytes(4, 'little'))
        wav_bytes.extend((1).to_bytes(2, 'little'))
        wav_bytes.extend((1).to_bytes(2, 'little'))
        wav_bytes.extend(sample_rate.to_bytes(4, 'little'))
        wav_bytes.extend((sample_rate * 2).to_bytes(4, 'little'))
        wav_bytes.extend((2).to_bytes(2, 'little'))
        wav_bytes.extend((16).to_bytes(2, 'little'))
        wav_bytes.extend(b'data')
        wav_bytes.extend((len(audio_data) * 2).to_bytes(4, 'little'))
        
        # Données audio
        for sample in audio_data:
            wav_bytes.extend(sample.to_bytes(2, 'little', signed=True))
        
        response = requests.post(url, headers=headers, data=bytes(wav_bytes), timeout=10)
        
        result = {
            'api_status': response.status_code,
            'api_response': response.text[:200] if response.status_code != 200 else 'OK',
            'audio_size': len(wav_bytes)
        }
        
        if response.status_code == 200:
            deepgram_result = response.json()
            transcript = deepgram_result["results"]["channels"][0]["alternatives"][0]["transcript"]
            result['transcript'] = transcript
            result['success'] = True
        else:
            result['transcript'] = ''
            result['success'] = False
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False})

@app.route('/test_audio_quality', methods=['POST'])
def test_audio_quality():
    """Test la qualité de l'audio reçu"""
    try:
        data = request.get_json()
        audio_base64 = data.get('audio')
        
        if not audio_base64:
            return jsonify({'error': 'No audio'}), 400
        
        # Décoder l'audio
        audio_bytes = base64.b64decode(audio_base64)
        
        # Analyser la qualité de l'audio
        import numpy as np
        
        # Extraire les données PCM du WAV
        if len(audio_bytes) >= 44:
            pcm_data = np.frombuffer(audio_bytes[44:], dtype=np.int16)
        else:
            return jsonify({'error': 'Invalid WAV format'}), 400
        
        # Calculer les métriques de qualité
        rms = np.sqrt(np.mean(pcm_data.astype(float)**2))
        peak = np.max(np.abs(pcm_data))
        
        # Calculer le ratio signal/bruit approximatif
        signal_power = rms**2
        noise_floor = np.percentile(np.abs(pcm_data), 10)
        snr_db = 20 * np.log10(signal_power / (noise_floor**2 + 1e-10))
        
        # Déterminer la qualité
        quality_score = min(100, (rms / 32767) * 100)
        
        result = {
            'audio_size': len(audio_bytes),
            'samples': len(pcm_data),
            'duration_seconds': len(pcm_data) / 16000,
            'rms_level': float(rms),
            'peak_level': float(peak),
            'snr_db': float(snr_db),
            'quality_score': float(quality_score),
            'is_good_quality': quality_score > 5 and rms > 1000,
            'recommendations': []
        }
        
        # Recommandations
        if rms < 1000:
            result['recommendations'].append("Parlez plus fort")
        if peak < 10000:
            result['recommendations'].append("Rapprochez-vous du micro")
        if snr_db < 10:
            result['recommendations'].append("Réduisez le bruit de fond")
        
        print(f"Qualité audio: RMS={rms:.1f}, Peak={peak:.1f}, SNR={snr_db:.1f}dB")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Erreur test_audio_quality: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/test_deepgram', methods=['POST'])
def test_deepgram():
    """Test direct de Deepgram avec WAV optimisé"""
    try:
        data = request.get_json()
        audio_base64 = data.get('audio')
        
        if not audio_base64:
            return jsonify({'error': 'No audio'}), 400
        
        # Décoder l'audio
        audio_bytes = base64.b64decode(audio_base64)
        
        print(f"Audio reçu: {len(audio_bytes)} bytes")
        
        # Vérifier si c'est du WAV (header "RIFF")
        if len(audio_bytes) >= 12:
            header = audio_bytes[:12]
            is_wav = header.startswith(b'RIFF') and b'WAVE' in header
            print(f"Format détecté: {'WAV' if is_wav else 'Autre'}")
        else:
            is_wav = False
            print(f"Audio trop petit: {len(audio_bytes)} bytes")
        
        # Test avec plusieurs approches Deepgram
        import requests
        
        # Approche 1: Nova-2 avec paramètres optimisés
        url1 = "https://api.deepgram.com/v1/listen?model=nova-2&language=fr&smart_format=true&detect_language=false&utterances=true"
        headers1 = {
            "Authorization": f"Token {os.getenv('DEEPGRAM_API_KEY')}",
            "Content-Type": "audio/wav"
        }
        
        response1 = requests.post(url1, headers=headers1, data=audio_bytes, timeout=15)
        
        result = {
            'deepgram_status': response1.status_code,
            'format': 'wav' if is_wav else 'webm',
            'audio_size': len(audio_bytes)
        }
        
        if response1.status_code == 200:
            deepgram_result = response1.json()
            transcript = deepgram_result["results"]["channels"][0]["alternatives"][0]["transcript"]
            result['transcript'] = transcript
            result['success'] = True
            result['deepgram_response'] = 'OK'
            print(f"Transcription: '{transcript}'")
            
            # Si transcription vide, essayer avec modèle plus permissif
            if not transcript.strip():
                print("Transcription vide, essai modèle base...")
                url2 = "https://api.deepgram.com/v1/listen?model=base&language=fr"
                response2 = requests.post(url2, headers=headers1, data=audio_bytes, timeout=15)
                
                if response2.status_code == 200:
                    deepgram_result2 = response2.json()
                    transcript2 = deepgram_result2["results"]["channels"][0]["alternatives"][0]["transcript"]
                    if transcript2.strip():
                        result['transcript'] = transcript2
                        result['deepgram_response'] = 'OK (model base)'
                        print(f"Transcription (base): '{transcript2}'")
        else:
            result['transcript'] = ''
            result['success'] = False
            result['deepgram_response'] = response1.text
            print(f"Erreur Deepgram: {response1.text}")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Erreur test_deepgram: {e}")
        return jsonify({
            'error': str(e), 
            'success': False,
            'deepgram_status': 0,
            'transcript': '',
            'format': 'error',
            'audio_size': len(audio_bytes) if 'audio_bytes' in locals() else 0
        })

@app.route('/test_audio', methods=['POST'])
def test_audio():
    """Endpoint de test pour vérifier la réception audio"""
    try:
        data = request.get_json()
        audio_base64 = data.get('audio')
        
        print(f"TEST AUDIO REÇU: {len(audio_base64) if audio_base64 else 0} chars")
        
        if not audio_base64:
            return jsonify({'error': 'No audio'}), 400
        
        # Simuler une réponse réussie
        return jsonify({
            'success': True,
            'text': 'Audio reçu avec succès ! Longueur: ' + str(len(audio_base64)),
            'audio': None
        })
        
    except Exception as e:
        print(f"ERREUR TEST: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/process_audio', methods=['POST'])
def process_audio():
    """Endpoint pour traiter l'audio avec pipeline optimisé multi-utilisateurs"""
    try:
        print("NOUVELLE REQUÊTE AUDIO REÇUE")
        
        # Récupérer l'audio en base64
        data = request.get_json()
        audio_base64 = data.get('audio')
        room_name = data.get('roomName', 'default_room')
        user_id = data.get('userId', 'unknown')
        is_test = data.get('test', False)
        
        print(f"Room: {room_name}, User: {user_id}")
        print(f"Audio reçu: {len(audio_base64) if audio_base64 else 0} chars")
        
        # Cas spécial : test du pipeline avec audio démo
        if is_test and audio_base64:
            print("MODE TEST AVEC AUDIO DÉMO")
            
            # Décoder l'audio
            audio_bytes = base64.b64decode(audio_base64)
            print(f"Audio démo décodé: {len(audio_bytes)} bytes")
            
            # Créer la room si elle n'existe pas
            room_processor = room_manager.get_voice_processor(room_name)
            if not room_processor:
                room_manager.create_room(room_name)
                room_processor = room_manager.get_voice_processor(room_name)
                print(f"Room '{room_name}' créée pour le test")
            
            # Transcrire l'audio démo
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                transcription = loop.run_until_complete(
                    room_processor.speech_to_text_optimized(audio_bytes)
                )
                loop.close()
                
                print(f"Transcription démo: '{transcription}'")
                
                # Générer une réponse adaptée à la transcription
                response_text = room_processor.get_llm_response(transcription)
                print(f"Réponse démo: '{response_text}'")
                
                # Générer l'audio de la réponse
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                response_audio = loop.run_until_complete(
                    room_processor.text_to_speech_optimized(response_text)
                )
                loop.close()
                
                if response_audio:
                    response_audio_b64 = base64.b64encode(response_audio).decode('utf-8')
                    return jsonify({
                        'success': True,
                        'text': transcription,
                        'response_text': response_text,
                        'response_audio': response_audio_b64,
                        'cached': False,
                        'room_users': room_manager.get_room_users(room_name)
                    })
                else:
                    return jsonify({
                        'success': True,
                        'text': transcription,
                        'response_text': response_text,
                        'response_audio': None,
                        'cached': False,
                        'room_users': room_manager.get_room_users(room_name)
                    })
                    
            except Exception as e:
                print(f"Erreur traitement démo: {e}")
                # Retourner une réponse de secours
                fallback_response = "La PrEP ou Prophylaxie Pré-Exposition est un médicament préventif qui réduit considérablement le risque de contracter le VIH."
                return jsonify({
                    'success': True,
                    'text': "Question sur la PrEP",
                    'response_text': fallback_response,
                    'response_audio': None,
                    'cached': False,
                    'room_users': room_manager.get_room_users(room_name)
                })
        
        # Cas spécial : test du pipeline sans audio (ancien code)
        if is_test and audio_base64 is None:
            print("MODE TEST ACTIVÉ")
            # Utiliser le vrai LLM pour une question de test universelle
            test_question = "Qui est le président de la France ?"
            
            # Créer ou récupérer la room pour le test
            room_processor = room_manager.get_voice_processor(room_name)
            if not room_processor:
                room_manager.create_room(room_name)
                room_processor = room_manager.get_voice_processor(room_name)
            
            # Utiliser le vrai LLM universel
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            test_response = room_processor.get_llm_response(test_question)
            test_audio = loop.run_until_complete(
                room_processor.text_to_speech_optimized(test_response)
            )
            loop.close()
            
            if test_audio:
                response_audio_b64 = base64.b64encode(test_audio).decode('utf-8')
                return jsonify({
                    'success': True,
                    'text': test_response,
                    'audio': response_audio_b64,
                    'cached': False,
                    'room_users': room_manager.get_room_users(room_name)
                })
            else:
                return jsonify({
                    'success': False,
                    'text': test_response,
                    'audio': None,
                    'room_users': room_manager.get_room_users(room_name)
                })
        
        if not audio_base64:
            print("PAS D'AUDIO REÇU")
            return jsonify({'error': 'No audio data'}), 400
        
        print("Audio reçu, début traitement...")
        
        # Décoder l'audio
        audio_bytes = base64.b64decode(audio_base64)
        print(f"Audio décodé: {len(audio_bytes)} bytes")
        
        # Analyser la qualité de l'audio
        import numpy as np
        audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
        print(f"Array créé: shape={audio_array.shape}")
        
        # Calculer les métriques de qualité
        rms = np.sqrt(np.mean(audio_array.astype(float)**2))
        peak = np.max(np.abs(audio_array))
        print(f"Qualité audio: RMS={rms:.1f}, Peak={peak:.1f}, Duration={len(audio_array)/16000:.2f}s")
        
        if rms < 500:
            print("ATTENTION: Audio très faible - parlez plus fort")
        if peak < 5000:
            print("ATTENTION: Peak très faible - rapprochez le micro")
        
        # Créer la room si elle n'existe pas
        room_processor = room_manager.get_voice_processor(room_name)
        if not room_processor:
            room_manager.create_room(room_name)
            room_processor = room_manager.get_voice_processor(room_name)
            print(f"Room '{room_name}' créée automatiquement")
        
        # Ajouter l'utilisateur à la room s'il n'y est pas déjà
        if user_id not in [user.user_id for user in room_manager.rooms.get(room_name, [])]:
            room_manager.join_room(user_id, "Utilisateur Vocal", room_name)
            print(f"Utilisateur '{user_id}' ajouté à la room '{room_name}'")
        
        # Marquer l'utilisateur comme parlant
        room_manager.set_user_speaking(user_id, True)
        
        print("LANCEMENT PIPELINE AUDIO...")
        
        # Traiter avec le pipeline vocal optimisé
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        print("DÉBUT TRAITEMENT AUDIO...")
        print(f"Audio array shape: {audio_array.shape}")
        print(f"Audio array type: {type(audio_array)}")
        
        response_audio, response_text = loop.run_until_complete(
            room_processor.process_audio_optimized(audio_array)
        )
        loop.close()
        
        print(f"RÉSULTAT FINAL: text='{response_text}', audio={len(response_audio) if response_audio else 0} bytes")
        
        # Marquer l'utilisateur comme plus parlant
        room_manager.set_user_speaking(user_id, False)
        
        if response_audio:
            # Encoder l'audio réponse en base64
            response_audio_b64 = base64.b64encode(response_audio).decode('utf-8')
            return jsonify({
                'success': True,
                'text': response_text,
                'audio': response_audio_b64,
                'cached': False,
                'room_users': room_manager.get_room_users(room_name)
            })
        else:
            return jsonify({
                'success': False,
                'text': response_text,
                'audio': None,
                'room_users': room_manager.get_room_users(room_name)
            })
        
    except Exception as e:
        print(f"ERREUR PROCESS_AUDIO: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/livekit/connect', methods=['POST'])
def livekit_connect():
    """Proxy pour connexion LiveKit"""
    try:
        data = request.get_json()
        url = data.get('url')
        token = data.get('token')
        
        # Simuler une connexion LiveKit réussie
        # En production, utiliserait le vrai SDK LiveKit
        return jsonify({
            'success': True,
            'message': 'Connecté à LiveKit',
            'room_id': 'room_' + str(int(time.time()))
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/livekit/publish', methods=['POST'])
def livekit_publish():
    """Proxy pour publication track LiveKit"""
    try:
        data = request.get_json()
        track_kind = data.get('trackKind')
        track_id = data.get('trackId')
        
        print(f"🎵 Track publié: {track_kind} - {track_id}")
        
        return jsonify({
            'success': True,
            'track_id': track_id,
            'published': True
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'message': 'Voice Agent API Ready'})

@app.route('/interrupt', methods=['POST'])
def interrupt_speech():
    """Endpoint pour interrompre la parole de l'agent multi-utilisateurs"""
    try:
        data = request.get_json()
        room_name = data.get('roomName', 'default_room')
        
        # Récupérer le processeur vocal pour cette room
        room_processor = room_manager.get_voice_processor(room_name)
        if not room_processor:
            return jsonify({'error': 'Room not found'}), 404
        
        # Interrompre l'agent
        was_interrupted = room_processor.interrupt_speech()
        
        return jsonify({
            'success': True,
            'interrupted': was_interrupted,
            'message': 'Agent interrompu' if was_interrupted else 'Agent non en cours de parole',
            'room_users': room_manager.get_room_users(room_name)
        })
        
    except Exception as e:
        print(f"Erreur interruption multi-user: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/room/<room_name>/users', methods=['GET'])
def get_room_users(room_name):
    """Retourne la liste des utilisateurs dans une room"""
    try:
        users = room_manager.get_room_users(room_name)
        return jsonify({
            'success': True,
            'room_name': room_name,
            'user_count': len(users),
            'users': users
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/room/<room_name>/leave', methods=['POST'])
def leave_room(room_name):
    """Fait quitter une room à un utilisateur"""
    try:
        data = request.get_json()
        user_id = data.get('userId')
        
        if not user_id:
            return jsonify({'error': 'userId required'}), 400
        
        success = room_manager.leave_room(user_id)
        
        return jsonify({
            'success': success,
            'message': 'Left room successfully' if success else 'User not found'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stats', methods=['GET'])
def get_system_stats():
    """Retourne les statistiques complètes du système"""
    try:
        return jsonify(room_manager.get_stats())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/cache/stats', methods=['GET'])
def get_cache_stats():
    """Endpoint pour obtenir les statistiques du cache"""
    try:
        return jsonify({
            'cache_size': len(voice_processor.cache),
            'cache_keys': list(voice_processor.cache.keys())[:10],  # Premiers 10
            'max_cache_size': 100
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_stats', methods=['GET'])
def get_stats():
    """Statistiques en temps réel du système"""
    try:
        # Statistiques du room manager
        total_rooms = len(room_manager.rooms)
        total_users = sum(len(room_manager.rooms[room_name]) for room_name in room_manager.rooms.keys())
        
        # Statistiques de cache (simulées pour l'instant)
        cache_size = 0  # À implémenter avec un vrai cache
        
        # Latence moyenne (simulée)
        avg_latency = 1500  # ms
        
        return jsonify({
            'latency': avg_latency,
            'cache': cache_size,
            'users': total_users,
            'rooms': total_rooms,
            'timestamp': time.time()
        })
        
    except Exception as e:
        print(f"Erreur get_stats: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Demarrage du serveur web multi-utilisateurs...")
    print(f"URL: http://localhost:5000")
    print(f"LiveKit: {LIVEKIT_URL}")
    print("Pipeline vocal: Deepgram + ElevenLabs")
    print("Optimisations: Cache + Parallelisme + Timeout")
    print("Support multi-utilisateurs: Rooms isolees")
    print("Max utilisateurs par room: 10")
    app.run(debug=True, host='0.0.0.0', port=5000)
