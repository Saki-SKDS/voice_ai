import asyncio
import os
import io
import wave
import requests
import json
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
import numpy as np
import time
import threading
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

class VoiceProcessor:
    def __init__(self):
        self.tts_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        self.is_speaking = False  # État de l'agent
        self.interrupted = False  # Flag d'interruption
        self.executor = ThreadPoolExecutor(max_workers=4)  # Pour traitements parallèles
        self.cache = {}  # Cache pour réponses fréquentes
        
    def interrupt_speech(self):
        """Permet d'interrompre la parole de l'agent"""
        if self.is_speaking:
            self.interrupted = True
            self.is_speaking = False
            print("🔇 Agent interrompu par l'utilisateur")
            return True
        return False
    
    def get_cache_key(self, text):
        """Génère une clé de cache pour un texte"""
        return text.lower().strip()[:50]
    
    def get_cached_response(self, text):
        """Récupère une réponse depuis le cache"""
        key = self.get_cache_key(text)
        return self.cache.get(key)
    
    def cache_response(self, text, response):
        """Met en cache une réponse"""
        key = self.get_cache_key(text)
        if len(self.cache) < 100:  # Limiter la taille du cache
            self.cache[key] = response
    
    async def speech_to_text_optimized(self, audio_data):
        """STT optimisé avec timeout et retry"""
        try:
            start_time = time.time()
            print("Transcription Deepgram optimisée...")
            
            # Convertir en WAV bytes
            wav_bytes = self.audio_to_wav_bytes(audio_data)
            print(f"Taille WAV: {len(wav_bytes)} bytes")
            print(f"Type audio: {type(audio_data)}")
            print(f"Shape audio: {audio_data.shape if hasattr(audio_data, 'shape') else 'N/A'}")
            
            # API Deepgram avec timeout
            url = "https://api.deepgram.com/v1/listen?model=nova-2&language=fr&smart_format=true"
            headers = {
                "Authorization": f"Token {DEEPGRAM_API_KEY}",
                "Content-Type": "audio/wav"
            }
            
            # Utiliser ThreadPool pour le réseau
            loop = asyncio.get_event_loop()
            
            def make_request():
                response = requests.post(url, headers=headers, data=wav_bytes, timeout=10)
                return response
            
            response = await loop.run_in_executor(self.executor, make_request)
            
            processing_time = (time.time() - start_time) * 1000
            print(f"STT temps: {processing_time:.0f}ms")
            print(f"Status Deepgram: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                transcript = result["results"]["channels"][0]["alternatives"][0]["transcript"]
                print(f"Transcription: '{transcript}'")
                return transcript
            else:
                print(f"Erreur Deepgram: {response.status_code}")
                print(f"Réponse Deepgram: {response.text}")
                return ""
                
        except Exception as e:
            print(f"Erreur STT optimisée: {e}")
            return ""
    
    def can_be_interrupted(self):
        """Vérifie si l'agent peut être interrompu"""
        return self.is_speaking and not self.interrupted
    
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
    
    async def speech_to_text(self, audio_data):
        """STT avec Deepgram"""
        try:
            print("🔊 Transcription Deepgram...")
            
            # Convertir en WAV bytes
            wav_bytes = self.audio_to_wav_bytes(audio_data)
            
            # API Deepgram
            url = "https://api.deepgram.com/v1/listen?model=nova-2&language=fr"
            headers = {
                "Authorization": f"Token {DEEPGRAM_API_KEY}",
                "Content-Type": "audio/wav"
            }
            
            response = requests.post(url, headers=headers, data=wav_bytes)
            
            if response.status_code == 200:
                result = response.json()
                transcript = result["results"]["channels"][0]["alternatives"][0]["transcript"]
                print(f"Transcription: '{transcript}'")
                return transcript
            else:
                print(f"Erreur Deepgram: {response.status_code}")
                return ""
                
        except Exception as e:
            print(f"Erreur STT: {e}")
            return ""
    
    def get_llm_response(self, text):
        """LLM universel avec recherche web - répond à tout type de questions"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            # Vérifier si la question nécessite des informations fraîches
            needs_web_search = self.needs_web_search(text)
            
            web_context = ""
            if needs_web_search:
                web_context = self.search_web(text)
            
            # Prompt universel pour tout type de questions
            system_prompt = f"""Tu es un assistant IA conversationnel universel et intelligent.
            
            Tu peux répondre à TOUS les types de questions :
            - Science et technologie
            - Culture et histoire  
            - Actualité et politique
            - Sports et divertissement
            - Cuisine et loisirs
            - Éducation et apprentissage
            - Conseils pratiques
            
            Sois naturel, précis et utile. Adapte ton ton à la question.
            Réponds en français de manière claire et concise.
            
            Contexte web récent: {web_context if web_context else "Aucun"}
            
            Utilise les informations fournies si pertinentes, sinon utilise tes connaissances générales."""
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Erreur LLM: {e}")
            # Fallback universel simple
            return f"Je comprends votre question sur '{text}'. Pourriez-vous me la reformuler s'il vous plaît ?"
    
    def needs_web_search(self, text):
        """Détermine si une question nécessite une recherche web"""
        web_keywords = [
            "actualité", "aujourd'hui", "dernier", "récent", "maintenant", "en ce moment",
            "météo", "temps", "quotidien", "journal", "news", "information",
            "prix", "coût", "cours", "bourse", "économie", "politique"
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in web_keywords)
    
    def search_web(self, query):
        """Recherche web simple via Wikipedia API"""
        try:
            # Recherche Wikipedia
            url = f"https://fr.wikipedia.org/api/rest_v1/page/summary/{query}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return f"Source Wikipedia: {data.get('extract', '')[:200]}..."
            
        except Exception as e:
            print(f"Erreur recherche web: {e}")
        
        return ""
    
    async def text_to_speech_optimized(self, text):
        """TTS optimisé avec cache et traitement parallèle"""
        try:
            start_time = time.time()
            print("Génération vocale optimisée...")
            
            # Vérifier le cache d'abord
            cached_audio = self.get_cached_response(text)
            if cached_audio:
                print("Audio récupéré depuis le cache")
                return cached_audio
            
            # Marquer que l'agent commence à parler
            self.is_speaking = True
            self.interrupted = False
            
            # Utiliser ThreadPool pour la génération TTS
            loop = asyncio.get_event_loop()
            
            def generate_audio():
                audio = self.tts_client.text_to_speech.convert(
                    text=text,
                    voice_id="JBFqnCBsd6RMkjVDRZzb",  # Rachel
                    model_id="eleven_multilingual_v2",
                    output_format="mp3_44100_128"
                )
                return b''.join(audio)
            
            # Vérifier interruption avant génération
            if self.interrupted:
                print("🔇 TTS interrompu avant la génération")
                self.is_speaking = False
                return None
            
            # Génération parallèle
            audio_bytes = await loop.run_in_executor(self.executor, generate_audio)
            
            processing_time = (time.time() - start_time) * 1000
            print(f"⏱️ TTS temps: {processing_time:.0f}ms")
            
            # Vérifier interruption après génération
            if self.interrupted:
                print("🔇 TTS interrompu après la génération")
                self.is_speaking = False
                return None
            
            # Mettre en cache
            self.cache_response(text, audio_bytes)
            
            print("Audio généré et mis en cache")
            self.is_speaking = False
            return audio_bytes
            
        except Exception as e:
            print(f"Erreur TTS optimisée: {e}")
            self.is_speaking = False
            return None
    
    async def process_audio_optimized(self, audio_data):
        """Pipeline optimisé avec traitement parallèle et cache"""
        try:
            pipeline_start = time.time()
            print("Pipeline optimisé démarré...")
            
            # 1. STT optimisé
            user_text = await self.speech_to_text_optimized(audio_data)
            
            if not user_text or len(user_text.strip()) < 2:
                return None, "Je n'ai pas bien entendu. Pourriez-vous répéter ou parler plus clairement ?"
            
            # 2. LLM (très rapide)
            response_text = self.get_llm_response(user_text)
            print(f"Réponse: {response_text}")
            
            # 3. TTS optimisé (parallèle)
            audio_response = await self.text_to_speech_optimized(response_text)
            
            total_time = (time.time() - pipeline_start) * 1000
            print(f"Pipeline total: {total_time:.0f}ms")
            
            if audio_response:
                return audio_response, response_text
            else:
                return None, "Désolé, j'ai été interrompu. Réessayez s'il vous plaît."
            
        except Exception as e:
            print(f"Erreur pipeline optimisé: {e}")
            return None, "Désolé, j'ai rencontré une erreur technique. Réessayez dans un instant."

# Instance globale
voice_processor = VoiceProcessor()
