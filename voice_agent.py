import time
import asyncio
import os
import requests
import json
from dotenv import load_dotenv
from deepgram import DeepgramClient
from elevenlabs.client import ElevenLabs
import io
import wave
import numpy as np
import sounddevice as sd

load_dotenv()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
WAXAL_API_KEY = os.getenv("WAXAL_API_KEY", "demo_key")  # Clé API WAXAL

# Mapping des langues WAXAL
WAXAL_LANGUAGES = {
    'fr': 'fr-FR',      # Français
    'bm': 'bm',         # Bambara
    'wo': 'wo',         # Wolof
    'ha': 'ha',         # Hausa
    'yo': 'yo',         # Yoruba
    'ig': 'ig',         # Igbo
    'ff': 'ff',         # Fulfulde
    'tw': 'tw',         # Twi
    'dag': 'dag',       # Dagbani
    'ee': 'ee',         # Ewe
    'gaa': 'gaa',       # Ga
    'gur': 'gur',       # Gurene
    'dga': 'dga',       # Dagaare
    'kus': 'kus',       # Kusaal
    'mos': 'mos',       # Moore
    'bm': 'bm',         # Bambara (alias)
    'dyu': 'dyu',       # Dioula
    'mnk': 'mnk',       # Mandinka
    'sw': 'sw',         # Swahili
    'lg': 'lg',         # Luganda
    'luo': 'luo',       # Luo
    'ach': 'ach',       # Acoli
    'am': 'am',         # Amharic
    'ti': 'ti',         # Tigrinya
    'mg': 'mg',         # Malagasy
}

class WaxalClient:
    """Client WAXAL pour les langues africaines"""
    
    def __init__(self, api_key=WAXAL_API_KEY):
        self.api_key = api_key
        self.stt_url = "https://api.waxal-speech.ai/stt"
        self.tts_url = "https://api.waxal-speech.ai/tts"
        self.translation_url = "https://api.waxal-speech.ai/translate"  # API traduction WAXAL
        
    async def speech_to_text(self, audio_file_path, language_code):
        """STT avec WAXAL pour langues africaines"""
        try:
            with open(audio_file_path, 'rb') as audio_file:
                response = requests.post(
                    self.stt_url,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    files={"file": audio_file},
                    data={"language": language_code}
                )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("text", "")
            else:
                print(f"❌ Erreur WAXAL STT: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Erreur WAXAL STT: {e}")
            return None
    
    async def text_to_speech(self, text, language_code, voice_type="female_standard"):
        """TTS avec WAXAL pour langues africaines"""
        try:
            payload = {
                "text": text,
                "language": language_code,
                "voice": voice_type
            }
            
            response = requests.post(
                self.tts_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload
            )
            
            if response.status_code == 200:
                return response.content  # Audio bytes
            else:
                print(f"❌ Erreur WAXAL TTS: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Erreur WAXAL TTS: {e}")
            return None
    
    async def translate_text(self, text, from_lang, to_lang):
        """Traduction avec WAXAL API - meilleure qualité culturelle"""
        try:
            payload = {
                "text": text,
                "from_language": from_lang,
                "to_language": to_lang
            }
            
            response = requests.post(
                self.translation_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                translated_text = result.get("translated_text", "")
                print(f"✅ WAXAL Traduction {from_lang}→{to_lang}: '{text}' → '{translated_text}'")
                return translated_text
            else:
                print(f"❌ Erreur WAXAL Traduction: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Erreur WAXAL Traduction: {e}")
            return None

class VoiceAgent:
    def __init__(self, current_language='fr'):
        self.deepgram = DeepgramClient(api_key=DEEPGRAM_API_KEY)
        self.tts_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        self.waxal_client = WaxalClient()
        self.current_language = current_language  # Langue actuelle
        self.is_recording = False
        self.audio_buffer = []
        
        # 🛡️ Circuit Breaker niveau production
        self.groq_failures = 0
        self.groq_last_failure = 0
        self.groq_circuit_open = False
        self.groq_circuit_timeout = 60  # 60 secondes
        
        print(f"🌍 VoiceAgent initialisé avec langue: {current_language}")
        print(f"📝 Langues disponibles: {list(WAXAL_LANGUAGES.keys())}")
    
    def set_language(self, language_code):
        """Change la langue de traitement"""
        if language_code in WAXAL_LANGUAGES:
            self.current_language = language_code
            print(f"🌍 Langue changée vers: {language_code}")
            return True
        else:
            print(f"❌ Langue non supportée: {language_code}")
            return False
    
    def is_african_language(self, language_code):
        """Vérifie si c'est une langue africaine supportée par WAXAL"""
        return language_code in WAXAL_LANGUAGES and language_code != 'fr'
    
    async def detect_language_from_audio(self, audio_file_path):
        """Détecter automatiquement la langue depuis l'audio"""
        try:
            # Utiliser Deepgram avec détection de langue
            with open(audio_file_path, 'rb') as audio_file:
                wav_bytes = audio_file.read()
            
            import requests
            
            # URL Deepgram avec détection de langue
            url = "https://api.deepgram.com/v1/listen?model=nova-2&detect_language=true"
            headers = {
                "Authorization": f"Token {DEEPGRAM_API_KEY}",
                "Content-Type": "audio/wav"
            }
            
            response = requests.post(url, headers=headers, data=wav_bytes)
            
            if response.status_code == 200:
                result = response.json()
                
                # Récupérer la langue détectée
                if "results" in result and "channels" in result["results"]:
                    channel = result["results"]["channels"][0]
                    
                    # Langue détectée
                    if "detected_language" in channel:
                        detected_lang = channel["detected_language"]
                        confidence = channel.get("language_confidence", 0)
                        
                        # Mapping des langues Deepgram vers nos codes
                        lang_mapping = {
                            'fr': 'fr',
                            'en': 'en',
                            'es': 'es',
                            'de': 'de',
                            'it': 'it',
                            'pt': 'pt'
                        }
                        
                        mapped_lang = lang_mapping.get(detected_lang, 'fr')
                        print(f"🎯 Langue détectée: {detected_lang} → {mapped_lang} (confiance: {confidence:.2f})")
                        
                        return mapped_lang, confidence
            
            print("⚠️ Détection de langue échouée, fallback français")
            return 'fr', 0.0
            
        except Exception as e:
            print(f"❌ Erreur détection langue: {e}")
            return 'fr', 0.0

    async def speech_to_text(self, audio_file_path, language=None):
        """STT intelligent avec détection automatique de langue"""
        lang = language or self.current_language
        
        # Si pas de langue spécifiée, détecter automatiquement
        if not language:
            print("🔍 Détection automatique de langue...")
            detected_lang, confidence = await self.detect_language_from_audio(audio_file_path)
            
            # Si confiance élevée et langue africaine, utiliser cette langue
            if confidence > 0.7 and detected_lang in WAXAL_LANGUAGES:
                lang = detected_lang
                print(f"✅ Langue automatique: {lang} (confiance: {confidence:.2f})")
                self.current_language = lang  # Mettre à jour la langue actuelle
            else:
                lang = self.current_language  # Garder la langue actuelle
                print(f"🔄 Conservation langue actuelle: {lang}")
        
        if self.is_african_language(lang):
            print(f"🎤 WAXAL STT pour langue africaine: {lang}")
            # 1. Transcrire avec WAXAL (retry optimisé)
            african_text = await self._waxal_stt_with_retry(audio_file_path, lang)
            if not african_text:
                print("❌ WAXAL STT échoué - Fallback Deepgram")
                return await self._deepgram_stt(audio_file_path, 'fr')
            
            print(f"✅ WAXAL transcription: '{african_text}'")
            
            # 2. PAS DE TRADUCTION - garder en langue africaine !
            print(f"🌍 Conservation langue: {african_text}")
            return african_text  # RETOURNER DIRECTEMENT en langue africaine
        else:
            print(f"🎤 Deepgram STT pour langue: {lang}")
            return await self._deepgram_stt(audio_file_path, lang)
    
    async def _waxal_stt_with_retry(self, audio_file_path, language, max_retries=3):
        """STT WAXAL avec retry automatique"""
        for attempt in range(max_retries):
            try:
                result = await self.waxal_client.speech_to_text(audio_file_path, language)
                if result and result.strip():
                    return result.strip()
            except Exception as e:
                print(f"⚠️ WAXAL tentative {attempt + 1}/{max_retries}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(0.5)  # Pause entre tentatives
        return None
    
    async def _translate_with_retry(self, text, from_lang, to_lang, max_retries=3):
        """Traduction avec WAXAL API uniquement - pas de fallback incorrect"""
        for attempt in range(max_retries):
            try:
                # Utiliser WAXAL Translation API uniquement
                result = await self.waxal_client.translate_text(text, from_lang, to_lang)
                if result and result.strip():
                    return result.strip()
            except Exception as e:
                print(f"⚠️ WAXAL Traduction tentative {attempt + 1}/{max_retries}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(0.5)  # Pause plus longue entre tentatives
        
        # Si WAXAL échoue complètement, retourner le texte original (pas de traduction incorrecte)
        print("❌ WAXAL Traduction échoué - Conservation texte original")
        return text  # Pas de traduction plutôt que traduction incorrecte
    
    async def _deepgram_stt(self, audio_file_path, language):
        """STT avec Deepgram (fallback pour français) - VERSION CORRIGÉE"""
        try:
            with open(audio_file_path, 'rb') as audio_file:
                wav_bytes = audio_file.read()
            
            # Utiliser l'API REST de Deepgram (qui marche !)
            import requests
            
            url = f"https://api.deepgram.com/v1/listen?model=nova-2&language={language}"
            headers = {
                "Authorization": f"Token {DEEPGRAM_API_KEY}",
                "Content-Type": "audio/wav"
            }
            
            response = requests.post(url, headers=headers, data=wav_bytes)
            
            if response.status_code == 200:
                result = response.json()
                transcript = result["results"]["channels"][0]["alternatives"][0]["transcript"]
                print(f"✅ Transcription Deepgram: {transcript}")
                return transcript
            else:
                print(f"❌ Erreur Deepgram HTTP: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Erreur Deepgram STT: {e}")
            return None
    
    async def text_to_speech(self, text, language='fr'):
        """TTS multilingue avec WAXAL pour accents africains authentiques"""
        try:
            if self.is_african_language(language):
                print(f"🗣️ WAXAL TTS pour accent {language} authentique: {language}")
                # 1. WAXAL TTS - meilleur accent africain authentique
                waxal_audio = await self.waxal_client.text_to_speech(text, language)
                if waxal_audio:
                    print(f"✅ WAXAL TTS généré: {len(waxal_audio)} bytes")
                    return waxal_audio
                else:
                    print(f"⚠️ WAXAL TTS échoué - Fallback OpenAI")
                
                # 2. Fallback OpenAI TTS
                return await self._openai_tts(text, language)
            else:
                print(f"🗣️ ElevenLabs TTS pour français: {language}")
                # Utiliser ElevenLabs pour le français (meilleur que gTTS)
                return await self._elevenlabs_tts(text, language)
        except Exception as e:
            print(f"❌ Erreur TTS: {e}")
            # Fallback vers gTTS en dernier recours
            return await self._gtts_tts(text, language)
    
    async def _openai_tts(self, text, language):
        """TTS avec OpenAI pour accent africain authentique"""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            # Mapping des langues pour OpenAI TTS
            voice_mapping = {
                'bm': 'alloy',      # Bambara → voix neutre multilingue
                'wo': 'alloy',      # Wolof → voix neutre multilingue  
                'ha': 'alloy',      # Haoussa → voix neutre multilingue
                'yo': 'alloy',      # Yoruba → voix neutre multilingue
                'ig': 'alloy',      # Igbo → voix neutre multilingue
                'sw': 'alloy',      # Swahili → voix multilingue
                'am': 'alloy',      # Amharique → voix multilingue
                'ti': 'alloy',      # Tigrinya → voix multilingue
                'mg': 'alloy',      # Malgache → voix multilingue
            }
            
            voice = voice_mapping.get(language, 'alloy')
            print(f"🎤 OpenAI TTS: {language} → voix {voice}")
            
            response = client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text,
                response_format="mp3"
            )
            
            # Convertir en bytes
            audio_bytes = b''.join([chunk for chunk in response.iter_bytes()])
            
            print(f"✅ OpenAI TTS généré: {len(audio_bytes)} bytes")
            return audio_bytes
            
        except Exception as e:
            print(f"❌ Erreur OpenAI TTS: {e}")
            # Fallback vers gTTS
            return await self._gtts_tts(text, language)

    async def _elevenlabs_tts(self, text, language):
        """TTS avec ElevenLabs (fallback pour français)"""
        try:
            # Voix française pour ElevenLabs
            voice_id = "CwhRBWXzGAHq8TQ4Fs17" if language == 'fr' else "EXAVITQu4vr4xnSDxMaL"  # Roger ou Sarah
            
            # Utiliser la nouvelle API ElevenLabs v2
            response = self.tts_client.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128"
            )
            
            # Convertir le générateur en bytes
            audio_bytes = b''.join(response)
            
            print(f"✅ Audio ElevenLabs généré: {len(audio_bytes)} bytes")
            return audio_bytes
            
        except Exception as e:
            print(f"❌ Erreur ElevenLabs TTS: {e}")
            return None
    
    async def _gtts_tts(self, text, language):
        """TTS ultra-rapide avec Google Text-to-Speech"""
        try:
            from gtts import gTTS
            import io
            
            # Mapping des langues pour gTTS optimisé
            lang_mapping = {
                'fr': 'fr',
                'bm': 'fr',  # Bambara: utilise français (meilleure prononciation)
                'wo': 'fr',  # Wolof: utilise français
                'ha': 'ha',  # Haoussa: supporté par gTTS !
                'yo': 'yo',  # Yoruba: supporté par gTTS !
                'ig': 'ig',  # Igbo: supporté par gTTS !
                'sw': 'sw',  # Swahili: supporté par gTTS !
                'lg': 'sw',  # Luganda: utilise swahili
                'am': 'am',  # Amharique: supporté par gTTS !
                'ti': 'ti',  # Tigrinya: supporté par gTTS !
                'mg': 'mg',  # Malgache: supporté par gTTS !
            }
            
            gtts_lang = lang_mapping.get(language, 'fr')
            print(f" gTTS avec langue: {language} → {gtts_lang}")
            
            # Créer l'audio
            from gtts import gTTS
            tts = gTTS(text=text, lang=gtts_lang, slow=False)
            
            # Sauvegarder en mémoire
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            audio_bytes = audio_buffer.getvalue()
            
            # Compression audio si nécessaire
            if len(audio_bytes) > 50000:  # 50KB max
                audio_bytes = self._compress_audio(audio_bytes)
            
            print(f"✅ Audio gTTS optimisé: {len(audio_bytes)} bytes")
            return audio_bytes
            
        except Exception as e:
            print(f"❌ Erreur gTTS: {e}")
            return None
    
    def _optimize_text_for_tts(self, text):
        """Optimiser le texte pour la synthèse vocale"""
        # Nettoyer le texte
        cleaned = text.strip()
        
        # Remplacer les caractères problématiques
        replacements = {
            '&': 'et',
            '%': 'pour cent',
            '@': 'arobase',
            '#': 'dièse',
            '*': 'étoile',
            '+': 'plus',
            '=': 'égal',
            '/': 'slash',
        }
        
        for old, new in replacements.items():
            cleaned = cleaned.replace(old, new)
        
        # Limiter la longueur pour TTS optimal
        if len(cleaned) > 250:
            cleaned = cleaned[:250] + "."
        
        return cleaned
    
    def _compress_audio(self, audio_bytes):
        """Compresser l'audio pour optimiser la taille"""
        # Pour l'instant, retourner l'audio tel quel
        # Future implémentation avec compression MP3
        return audio_bytes
        
    def record_audio(self, duration=5, sample_rate=16000):
        """Enregistre l'audio depuis le micro"""
        print(f"🎤 Enregistrement pour {duration} secondes...")
        
        self.audio_buffer = sd.rec(
            int(duration * sample_rate), 
            samplerate=sample_rate, 
            channels=1, 
            dtype='int16'
        )
        sd.wait()
        
        print("✅ Enregistrement terminé")
        return self.audio_buffer
    
    def audio_to_wav_bytes(self, audio_data, sample_rate=16000):
        """Convertit les données audio en bytes WAV"""
        wav_buffer = io.BytesIO()
        
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data.tobytes())
        
        wav_buffer.seek(0)
        return wav_buffer.getvalue()
    
    async def speech_to_text_from_bytes(self, audio_bytes, language=None):
        """STT intelligent depuis bytes audio avec routing selon langue"""
        lang = language or self.current_language
        
        # Sauvegarder temporairement les bytes pour traitement
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_file_path = tmp_file.name
        
        try:
            # Utiliser la méthode STT multilingue
            return await self.speech_to_text(tmp_file_path, lang)
        finally:
            # Nettoyer le fichier temporaire
            try:
                os.unlink(tmp_file_path)
            except:
                pass

    async def speech_to_text_legacy(self, audio_data):
        """STT avec Deepgram - méthode legacy pour compatibilité"""
        try:
            print("🔊 Transcription avec Deepgram...")
            
            # Convertir en WAV bytes
            wav_bytes = self.audio_to_wav_bytes(audio_data)
            
            # Utiliser l'API REST de Deepgram (plus simple)
            import requests
            
            url = "https://api.deepgram.com/v1/listen?model=nova-2&language=fr"
            headers = {
                "Authorization": f"Token {DEEPGRAM_API_KEY}",
                "Content-Type": "audio/wav"
            }
            
            response = requests.post(url, headers=headers, data=wav_bytes)
            
            if response.status_code == 200:
                result = response.json()
                transcript = result["results"]["channels"][0]["alternatives"][0]["transcript"]
                print(f" Transcription: {transcript}")
                return transcript
            else:
                print(f" Erreur Deepgram: {response.status_code}")
                return ""
            
        except Exception as e:
            print(f" Erreur STT: {e}")
            return ""
    
    def play_audio(self, audio_bytes):
        """Joue l'audio"""
        try:
            import tempfile
            import os
            
            # Sauvegarder temporairement
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
                tmp_file.write(audio_bytes)
                tmp_file_path = tmp_file.name
            
            # Jouer avec le lecteur système
            os.system(f"start {tmp_file_path}")
            
            # Nettoyer après un délai
            import threading
            def cleanup():
                import time
                time.sleep(5)
                try:
                    os.unlink(tmp_file_path)
                except:
                    pass
            
            threading.Thread(target=cleanup, daemon=True).start()
            
        except Exception as e:
            print(f"❌ Erreur lecture: {e}")
    
    async def get_llm_response(self, text):
        """LLM multilingue avec timeout global et résilience niveau production"""
        import time
        
        max_retries = 3
        retry_delay = 1.0
        TOTAL_TIMEOUT = 10.0  # ⚡ Timeout global MAX 10 secondes
        start_time = time.time()
        
        for attempt in range(max_retries):
            try:
                # ⚠️ Vérifier timeout global
                if time.time() - start_time > TOTAL_TIMEOUT:
                    print(f"⏰ Timeout global atteint ({TOTAL_TIMEOUT}s) - Fast fallback")
                    return self._get_fast_fallback(text)
                
                # 🛡️ Circuit breaker check
                if self._check_groq_circuit_breaker():
                    print("⚡ Circuit breaker Groq ouvert - Skip vers fallback rapide")
                    return await self._llm_fallback_fast(text, remaining_time=max(3.0, 10.0 - (time.time() - start_time)))
                
                print(f"🤖 Tentative LLM {attempt + 1}/{max_retries}")
                
                # Détecter la langue du texte
                if self.is_african_language(self.current_language):
                    context = f"""Tu es un assistant IA spécialisé dans les langues africaines. 
L'utilisateur te parle en {self.current_language} (langue africaine).
Réponds DIRECTEMENT en {self.current_language}, PAS en français.
Utilise les expressions et la culture {self.current_language}.
Sois naturel et authentique."""
                else:
                    context = f"""Tu es un assistant IA multilingue spécialisé dans les langues africaines."""
                
                # Timeout adaptatif selon le temps restant
                remaining_time = TOTAL_TIMEOUT - (time.time() - start_time)
                timeout = min(8.0, max(2.0, remaining_time))  # 2-8s max
                
                response = requests.post(
                    'https://api.groq.com/openai/v1/chat/completions',
                    headers={
                        'Authorization': f'Bearer {os.getenv("GROQ_API_KEY")}',
                        'Content-Type': 'application/json'
                    },
                    json={
                        'model': 'llama-3.1-8b-instant',
                        'messages': [
                            {"role": "system", "content": context},
                            {"role": "user", "content": text}
                        ],
                        'max_tokens': 300,  # Réduit pour vitesse
                        'temperature': 0.7,
                        'top_p': 0.9,
                        'stream': False
                    },
                    timeout=timeout  # Timeout adaptatif
                )
                
                if response.status_code == 200:
                    result = response.json()
                    response_text = result['choices'][0]['message']['content']
                    
                    cleaned_response = self._optimize_response(response_text)
                    elapsed = time.time() - start_time
                    print(f"✅ Réponse LLM en {elapsed:.2f}s: '{cleaned_response}'")
                    
                    # 🛡️ Enregistrer succès
                    self._record_groq_success()
                    return cleaned_response
                else:
                    print(f"❌ Erreur Groq HTTP: {response.status_code}")
                    # 🛡️ Enregistrer échec
                    self._record_groq_failure()
                    
                    if time.time() - start_time > TOTAL_TIMEOUT:
                        break
                    if attempt < max_retries - 1:
                        await asyncio.sleep(min(retry_delay, 2.0))  # Max 2s
                        retry_delay = min(retry_delay * 1.5, 3.0)  # Backoff limité
                    continue
                    
            except requests.exceptions.Timeout:
                print(f"⏰ Timeout LLM (tentative {attempt + 1})")
                # 🛡️ Enregistrer échec
                self._record_groq_failure()
                
                if time.time() - start_time > TOTAL_TIMEOUT:
                    break
                if attempt < max_retries - 1:
                    await asyncio.sleep(min(retry_delay, 1.5))
                    retry_delay = min(retry_delay * 1.5, 2.5)
                continue
                    
            except Exception as e:
                print(f"❌ Erreur LLM (tentative {attempt + 1}): {e}")
                # 🛡️ Enregistrer échec
                self._record_groq_failure()
                
                if time.time() - start_time > TOTAL_TIMEOUT:
                    break
                if attempt < max_retries - 1:
                    await asyncio.sleep(min(retry_delay, 1.0))
                    retry_delay = min(retry_delay * 1.5, 2.0)
                continue
        
        # Fallback rapide si timeout global dépassé
        elapsed = time.time() - start_time
        print(f"🚨 Échec LLM après {elapsed:.2f}s - Fast fallback")
        return await self._llm_fallback_fast(text, remaining_time=max(3.0, 10.0 - elapsed))
    
    def _check_groq_circuit_breaker(self):
        """Vérifie si le circuit breaker Groq est ouvert"""
        import time
        
        # Si circuit ouvert, vérifier si on peut le refermer
        if self.groq_circuit_open:
            if time.time() - self.groq_last_failure > self.groq_circuit_timeout:
                print("🔄 Circuit breaker Groq refermé")
                self.groq_circuit_open = False
                self.groq_failures = 0
                return False
            else:
                return True  # Circuit toujours ouvert
        
        # Si trop d'échecs, ouvrir le circuit
        if self.groq_failures >= 5:
            print(f"🚨 Circuit breaker Groq ouvert ({self.groq_failures} échecs)")
            self.groq_circuit_open = True
            self.groq_last_failure = time.time()
            return True
        
        return False
    
    def _record_groq_success(self):
        """Enregistrer un succès Groq"""
        if self.groq_failures > 0:
            self.groq_failures = max(0, self.groq_failures - 1)
            print(f"✅ Succès Groq - Failures réduits à {self.groq_failures}")
    
    def _record_groq_failure(self):
        """Enregistrer un échec Groq"""
        self.groq_failures += 1
        print(f"❌ Échec Groq enregistré - Total failures: {self.groq_failures}")
    
    def _get_fast_fallback(self, text):
        """Fallback ultra-rapide (<100ms) pour timeout critique"""
        text_lower = text.lower().strip()
        
        # Réponses ultra-rapides basées sur les premiers mots
        if any(word in text_lower[:20] for word in ["bonjour", "salut", "n ba", "sannu"]):
            return f"Bonjour! Je suis votre assistant IA. Comment puis-je vous aider en {self.current_language}?"
        
        elif any(word in text_lower[:20] for word in ["merci", "i ni", "nagode", "jerejef"]):
            return "Avec plaisir! Je suis là pour vous aider. Autre chose?"
        
        elif any(word in text_lower[:20] for word in ["aide", "help", "problème"]):
            return f"Je comprends. Décrivez-moi votre besoin en {self.current_language} ou français."
        
        else:
            return f"Je suis votre assistant vocal multilingue. En quoi puis-je vous aider?"
    
    async def _llm_fallback_fast(self, text, remaining_time=3.0):
        """Fallback LLM optimisé pour vitesse"""
        import time
        start_time = time.time()
        
        # 🛡️ Vérifier circuit breaker
        if self._check_groq_circuit_breaker():
            print("⚡ Circuit breaker Groq ouvert - Skip direct vers OpenAI")
        else:
            # Tentative OpenAI rapide
            try:
                print(f"⚡ Fast fallback OpenAI ({remaining_time:.1f}s max)")
                openai_response = await self._openai_llm_fallback_fast(text, timeout=min(2.5, remaining_time))
                if openai_response:
                    self._record_groq_failure()  # Quand même compter l'échec Groq
                    return openai_response
            except Exception as e:
                print(f"❌ Fast fallback OpenAI échoué: {e}")
        
        # Fallback ultra-rapide
        elapsed = time.time() - start_time
        print(f"⚡ Fast fallback rules après {elapsed:.2f}s")
        return self._get_fast_fallback(text)
    
    async def _openai_llm_fallback_fast(self, text, timeout=2.5):
        """Fallback OpenAI optimisé pour vitesse"""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            # Contexte ultra-simple
            if self.is_african_language(self.current_language):
                context = f"Réponds brièvement en {self.current_language}. Maximum 2 phrases."
            else:
                context = "Réponds brièvement en français. Maximum 2 phrases."
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": context},
                    {"role": "user", "content": text}
                ],
                max_tokens=100,  # Ultra-court pour vitesse
                temperature=0.7,
                timeout=timeout
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ Fast OpenAI error: {e}")
            return None
    
    async def _llm_fallback_chain(self, text):
        """Cascade de fallback LLM niveau entreprise"""
        
        # 1. Fallback OpenAI (si Groq échoue)
        try:
            print("🔄 Fallback LLM 1: OpenAI")
            openai_response = await self._openai_llm_fallback(text)
            if openai_response:
                return openai_response
        except Exception as e:
            print(f"❌ Fallback OpenAI échoué: {e}")
        
        # 2. Fallback Hugging Face (si OpenAI échoue)
        try:
            print("🔄 Fallback LLM 2: Hugging Face")
            hf_response = await self._huggingface_fallback(text)
            if hf_response:
                return hf_response
        except Exception as e:
            print(f"❌ Fallback Hugging Face échoué: {e}")
        
        # 3. Dernier recours: règles intelligentes
        print("🔄 Fallback 3: Règles intelligentes")
        return self._get_intelligent_fallback(text)
    
    async def _openai_llm_fallback(self, text):
        """Fallback OpenAI GPT"""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            # Contexte adapté
            if self.is_african_language(self.current_language):
                context = f"Réponds en {self.current_language} (langue africaine) de manière simple et utile."
            else:
                context = "Réponds en français de manière simple et utile."
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": context},
                    {"role": "user", "content": text}
                ],
                max_tokens=300,
                temperature=0.7,
                timeout=10
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ OpenAI fallback error: {e}")
            return None
    
    async def _huggingface_fallback(self, text):
        """Fallback Hugging Face (local/plus rapide)"""
        try:
            import requests
            
            # Modèle léger et rapide
            API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
            headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY', '')}"}
            
            payload = {"inputs": text}
            
            response = requests.post(API_URL, headers=headers, json=payload, timeout=8)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", text)
            
            return None
            
        except Exception as e:
            print(f"❌ Hugging Face fallback error: {e}")
            return None
    
    def _get_intelligent_fallback(self, text):
        """Fallback intelligent avec gestion d'erreurs"""
        text_lower = text.lower().strip()
        
        try:
            # Analyse du type de demande
            if any(word in text_lower for word in ["bonjour", "salut", "hello", "n ba", "sannu"]):
                return self._format_fallback_response(
                    f"Je suis votre assistant vocal pour les langues africaines. ",
                    f"Je peux vous aider en {self.current_language} ou en français. ",
                    "Comment puis-je vous assister aujourd'hui ?"
                )
            
            elif any(word in text_lower for word in ["merci", "thank", "i ni ɲɛ", "nagode", "jerejef"]):
                return self._format_fallback_response(
                    "Avec plaisir ! ",
                    f"C'est un honneur de converser avec vous en {self.current_language}. ",
                    "Y a-t-il autre chose dont vous avez besoin ?"
                )
            
            elif any(word in text_lower for word in ["aide", "aide", "help", "problème", "erreur"]):
                return self._format_fallback_response(
                    "Je comprends que vous avez besoin d'aide. ",
                    f"Je suis là pour vous assister en {self.current_language}. ",
                    "Pouvez-vous me décrire plus précisément votre besoin ?"
                )
            
            elif any(word in text_lower for word in ["qui es", "comment", "ton nom", "identité"]):
                return self._format_fallback_response(
                    f"Je suis votre assistant IA spécialisé dans les langues africaines. ",
                    f"Je fonctionne en {self.current_language} et en français. ",
                    "Mon rôle est de vous aider avec vos questions quotidiennes."
                )
            
            else:
                # Fallback générique mais informatif
                return self._format_fallback_response(
                    f"Je suis votre assistant vocal multilingue. ",
                    f"Je traite actuellement le {self.current_language}. ",
                    "Je suis là pour vous aider. Pouvez-vous reformuler votre question ?"
                )
                
        except Exception as e:
            print(f"❌ Erreur fallback intelligent: {e}")
            return "Désolé, je rencontre des difficultés techniques. Veuillez réessayer dans un instant."
    
    def _format_fallback_response(self, prefix, context, suffix):
        """Formate une réponse fallback avec contexte culturel"""
        if self.is_african_language(self.current_language):
            # Ajouter une touche culturelle selon la langue
            cultural_touches = {
                'bm': " I ni bɛ !",  # Bambara
                'wo': " Maa ngi fi !",  # Wolof  
                'ha': " Lafiya !",  # Haoussa
                'yo': " Pẹlẹ o !",  # Yoruba
                'sw': " Nzuri sana !",  # Swahili
            }
            touch = cultural_touches.get(self.current_language, "")
            return f"{prefix}{context}{suffix}{touch}"
        else:
            return f"{prefix}{context}{suffix}"
    
    def _get_optimized_context(self, text):
        """Contexte optimisé selon la langue détectée"""
        if self.is_african_language(self.current_language):
            return f"""Tu es un assistant IA multilingue spécialisé dans les langues africaines. 
Langue actuelle: {self.current_language}
Réponds de manière claire, utile et culturellement appropriée. 
Sois concis mais complet. Utilise un français simple et accessible."""
        else:
            return """Tu es un assistant IA utile et amical. 
Réponds de manière claire, utile et naturelle. 
Sois concis mais complet."""
    
    def _optimize_response(self, response):
        """Optimiser la réponse pour la synthèse vocale"""
        # Nettoyer les caractères problématiques
        cleaned = response.strip()
        
        # Limiter la longueur pour TTS optimal
        if len(cleaned) > 300:
            cleaned = cleaned[:300] + "..."
        
        # Remplacer les abréviations
        replacements = {
            "c'est": "c'est",
            "j'ai": "j'ai", 
            "n'est": "n'est",
            "d'": "d'",
        }
        
        for old, new in replacements.items():
            cleaned = cleaned.replace(old, new)
        
        return cleaned
    
    async def process_conversation(self):
        """Pipeline complet de conversation"""
        print("\n" + "="*50)
        print("🚀 DÉMARRAGE CONVERSATION AGENT VOCAL")
        print("="*50)
        
        # 1. Enregistrer l'audio utilisateur
        audio_data = self.record_audio(duration=5)
        
        # 2. Transcrire (STT)
        user_text = await self.speech_to_text(audio_data)
        
        if not user_text:
            print("❌ Aucun texte détecté")
            return
        
        # 3. Générer réponse (LLM)
        response_text = self.get_llm_response(user_text)
        print(f"🤖 Réponse: {response_text}")
        
        # 4. Synthétiser la voix (TTS)
        audio_response = await self.text_to_speech(response_text)
        
        if audio_response:
            # 5. Jouer la réponse
            self.play_audio(audio_response)
        
        print("\n✅ Conversation terminée")

async def main():
    agent = VoiceAgent()
    
    print("🎤 Agent Vocal PrEP - POC AfricaSys")
    print("Parlez dans le micro quand l'enregistrement commence...")
    
    while True:
        try:
            await agent.process_conversation()
            
            choice = input("\nContinuer ? (o/n): ").lower()
            if choice != 'o':
                break
                
        except KeyboardInterrupt:
            print("\n👋 Au revoir !")
            break
        except Exception as e:
            print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    asyncio.run(main())
