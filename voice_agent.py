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

class VoiceAgent:
    def __init__(self, current_language='fr'):
        self.deepgram = DeepgramClient(api_key=DEEPGRAM_API_KEY)
        self.tts_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        self.waxal_client = WaxalClient()
        self.current_language = current_language  # Langue actuelle
        self.is_recording = False
        self.audio_buffer = []
        
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
    
    async def _translate_with_retry(self, text, from_lang, to_lang, max_retries=2):
        """Traduction avec retry automatique"""
        for attempt in range(max_retries):
            try:
                # Utiliser un service de traduction simple
                result = await self._simple_translate(text, from_lang, to_lang)
                if result:
                    return result
            except Exception as e:
                print(f"⚠️ Traduction tentative {attempt + 1}/{max_retries}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(0.3)
        return None
    
    async def _simple_translate(self, text, from_lang, to_lang):
        """Traduction simple avec mapping"""
        # Dictionnaire de traductions de base
        translations = {
            'bm': {'fr': {
                'n ba': 'bonjour', 'i ni cɛ': 'ça va', 'n bɛ to': 'je vais bien',
                'i ni ba': 'au revoir', 'i ni ɲɛ': 'merci', 'wè to': 'et toi',
                'n bɛ fɛ': 'ça va bien', 'n bɛ tɛmɛ': 'j\'ai faim', 'n bɛ min': 'j\'ai soif',
                'n bɛ sɔrɔ': 'je suis content', 'i ka kènè': 'comment vas-tu', 'n bɛ': 'je suis',
                'i bɛ': 'tu es', 'a bɛ': 'il/elle est', 'an bɛ': 'nous sommes',
                'aw bɛ': 'vous êtes', 'i bɛ': 'ils/elles sont'
            }},
            'fr': {'bm': {
                'bonjour': 'n ba', 'ça va': 'i ni cɛ', 'je vais bien': 'n bɛ to',
                'au revoir': 'i ni ba', 'merci': 'i ni ɲɛ', 'et toi': 'wè to',
                'ça va bien': 'n bɛ fɛ', 'j\'ai faim': 'n bɛ tɛmɛ', 'j\'ai soif': 'n bɛ min',
                'je suis content': 'n bɛ sɔrɔ', 'comment vas-tu': 'i ka kènè', 'je suis': 'n bɛ',
                'tu es': 'i bɛ', 'il est': 'a bɛ', 'elle est': 'a bɛ', 'nous sommes': 'an bɛ',
                'vous êtes': 'aw bɛ', 'ils sont': 'i bɛ', 'elles sont': 'i bɛ',
                'salut': 'n ba', 'comment': 'comment', 'puis-je': 'ni bɛ se ka',
                'vous aider': 'ka i fo', 'bienvenue': 'n bɛna', 's\'il vous plaît': 'a ɲɛ',
                'excusez-moi': 'i ka bɔn', 'désolé': 'n bɛ wèrè', 'oui': 'ayiwa', 'non': 'non'
            }},
            'wo': {'fr': {
                'salaam aleikum': 'bonjour', 'na nga def': 'ça va', 'ma ngi fi': 'je vais bien',
                'jerejef': 'merci', 'ci nga def': 'et toi'
            }},
            'fr': {'wo': {
                'bonjour': 'salaam aleikum', 'ça va': 'na nga def', 'je vais bien': 'ma ngi fi',
                'merci': 'jerejef', 'et toi': 'ci nga def'
            }},
            'ha': {'fr': {
                'sannu': 'bonjour', 'yaya': 'ça va', 'lafiya': 'je vais bien',
                'nagode': 'merci', 'kana lafiya': 'et toi'
            }},
            'fr': {'ha': {
                'bonjour': 'sannu', 'ça va': 'yaya', 'je vais bien': 'lafiya',
                'merci': 'nagode', 'et toi': 'kana lafiya'
            }},
        }
        
        text_lower = text.lower().strip()
        
        # Chercher traduction exacte (pas seulement "contains")
        if from_lang in translations and to_lang in translations[from_lang]:
            # D'abord chercher une correspondance exacte
            if text_lower in translations[from_lang][to_lang]:
                return translations[from_lang][to_lang][text_lower]
            
            # Ensuite chercher si le texte contient une phrase à traduire
            for original, translated in translations[from_lang][to_lang].items():
                if original in text_lower:
                    return text_lower.replace(original, translated)
        
        # Retourner le texte original si pas de traduction
        return text
    
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
        """TTS multilingue avec OpenAI pour meilleur accent africain"""
        try:
            if self.is_african_language(language):
                print(f"🗣️ OpenAI TTS pour langue africaine: {language}")
                # Utiliser OpenAI TTS pour meilleur accent
                return await self._openai_tts(text, language)
            else:
                print(f"🗣️ gTTS pour langue: {language}")
                # Utiliser gTTS pour le français
                return await self._gtts_tts(text, language)
        except Exception as e:
            print(f"❌ Erreur TTS: {e}")
            # Fallback vers gTTS en cas d'erreur
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
    
    def get_llm_response(self, text):
        """LLM multilingue qui comprend et répond dans la langue du texte"""
        try:
            import requests
            
            # Détecter la langue du texte
            if self.is_african_language(self.current_language):
                # Si langue africaine, demander réponse dans cette langue
                context = f"""Tu es un assistant IA spécialisé dans les langues africaines. 
L'utilisateur te parle en {self.current_language} (langue africaine).
Réponds DIRECTEMENT en {self.current_language}, PAS en français.
Utilise les expressions et la culture {self.current_language}.
Sois naturel et authentique."""
            else:
                # Si français, répondre en français
                context = f"""Tu es un assistant IA multilingue spécialisé dans les langues africaines."""
            
            # Utiliser Groq API avec paramètres optimisés
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
                    'max_tokens': 500,
                    'temperature': 0.7,
                    'top_p': 0.9,
                    'stream': False
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result['choices'][0]['message']['content']
                
                # Nettoyage et optimisation de la réponse
                cleaned_response = self._optimize_response(response_text)
                print(f"✅ Réponse LLM en {self.current_language}: '{cleaned_response}'")
                return cleaned_response
            else:
                print(f"❌ Erreur Groq: {response.status_code}")
                raise Exception("Groq API failed")
            
        except Exception as e:
            print(f"❌ Erreur LLM: {e}")
            raise Exception(f"LLM failed: {str(e)}")
    
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
    
    def _get_fallback_response(self, text):
        """Fallback intelligent avec réponses contextuelles variées"""
        
        import random
        
        # Réponses contextuelles basées sur le texte utilisateur
        text_lower = text.lower()
        
        # Salutations - réponses variées
        if any(word in text_lower for word in ["bonjour", "salut", "hello", "hi"]):
            responses = [
                "Bonjour ! Comment puis-je vous aider aujourd'hui ?",
                "Salut ! Ravie de vous entendre ! Comment ça va ?",
                "Bonjour ! Quelle belle journée ! En quoi puis-je vous assister ?",
                "Hello ! Comment se passe votre journée ?"
            ]
            return random.choice(responses)
        
        # Questions sur l'identité - réponses variées
        if any(word in text_lower for word in ["qui es-tu", "comment tu t'appelles", "ton nom"]):
            responses = [
                "Je suis votre assistant vocal intelligent. Je suis là pour vous aider avec vos questions et tâches quotidiennes.",
                "Je suis une IA conversationnelle conçue pour vous assister. Comment puis-je vous être utile ?",
                "Je suis votre compagnon vocal personnel. N'hésitez pas à me poser des questions !"
            ]
            return random.choice(responses)
        
        # Comment ça va - réponses variées
        if any(word in text_lower for word in ["comment ça va", "ça va", "tu vas bien"]):
            responses = [
                "Je vais très bien, merci ! Je suis prêt à vous aider. Et vous ?",
                "Tout va parfaitement ! Je suis là pour vous. Comment allez-vous ?",
                "Je suis en pleine forme ! Merci de demander. Et vous, comment allez-vous ?"
            ]
            return random.choice(responses)
        
        # Questions éducatives - réponses intelligentes
        if any(word in text_lower for word in ["qu'est-ce que", "c'est quoi", "défini"]):
            if "banque" in text_lower:
                responses = [
                    "Une banque est une institution financière qui gère l'argent, propose des crédits et protège vos économies. Elle facilite les transactions et investissements.",
                    "La banque est un établissement qui conserve votre argent en sécurité, offre des prêts et des services financiers adaptés à vos besoins.",
                    "Une banque sert d'intermédiaire financier : elle garde vos fonds, accorde des prêts et simplifie vos transactions quotidiennes."
                ]
            elif "paludisme" in text_lower:
                responses = [
                    "Le paludisme est une maladie infectieuse transmise par les moustiques. Elle provoque de la fièvre et peut être grave sans traitement rapide.",
                    "Le paludisme est causé par un parasite transmis par la piqûre de moustique anophèle. Il est prévenable et traitable avec des médicaments adaptés.",
                    "Le paludisme est une maladie tropicale grave qui se manifeste par des fièvres cycliques. La prévention inclut les moustiquaires et médicaments."
                ]
            else:
                responses = [
                    "C'est une excellente question ! Permettez-moi de vous expliquer cela en détail.",
                    "Je comprends votre curiosité. C'est un sujet intéressant qui mérite quelques précisions.",
                    "Bonne question ! Voici ce que vous devez savoir à ce sujet..."
                ]
            return random.choice(responses)
        
        # Remerciements - réponses variées
        if any(word in text_lower for word in ["merci", "thank"]):
            responses = [
                "De rien ! C'est toujours un plaisir de vous aider. Y a-t-il autre chose ?",
                "Avec plaisir ! N'hésitez pas si vous avez besoin d'autre chose.",
                "Je vous en prie ! C'est ma mission de vous assister. Comment puis-je encore vous aider ?"
            ]
            return random.choice(responses)
        
        # Au revoir - réponses variées
        if any(word in text_lower for word in ["au revoir", "bye", "à plus"]):
            responses = [
                "Au revoir ! Passez une excellente journée et n'hésitez pas à revenir si vous avez besoin d'aide.",
                "À bientôt ! Prenez soin de vous et revenez quand vous voulez !",
                "Au plaisir de vous revoir ! Bonne continuation et excellente journée !"
            ]
            return random.choice(responses)
        
        # Réponse générique intelligente et variée
        if len(text.split()) > 3:  # Question complexe
            responses = [
                "C'est une question très intéressante ! Laissez-moi réfléchir à la meilleure façon de vous répondre...",
                "Je comprends votre interrogation. C'est un sujet qui mérite qu'on s'y attarde.",
                "Excellente question ! Voici ma perspective sur ce sujet...",
                "Votre question est pertinente ! Permettez-moi de vous donner une réponse complète."
            ]
        else:
            responses = [
                "Je suis là pour vous aider ! Dites-moi ce dont vous avez besoin.",
                "Comment puis-je vous être utile aujourd'hui ?",
                "Je suis votre assistant personnel. En quoi puis-je vous assister ?",
                "N'hésitez pas à me poser vos questions, je suis là pour ça !"
            ]
        
        return random.choice(responses)
    
    def _get_default_response(self, text):
        """Dernier recours si tout échoue"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["bonjour", "salut"]):
            return "Bonjour ! Comment puis-je vous aider ?"
        elif any(word in text_lower for word in ["merci"]):
            return "De rien ! Je suis là pour aider."
        else:
            return "Je suis votre assistant vocal. Comment puis-je vous aider aujourd'hui ?"
    
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
