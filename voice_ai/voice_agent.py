import asyncio
import os
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

class VoiceAgent:
    def __init__(self):
        self.deepgram = DeepgramClient(api_key=DEEPGRAM_API_KEY)
        self.tts_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        self.is_recording = False
        self.audio_buffer = []
        
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
    
    async def speech_to_text(self, audio_data):
        """STT avec Deepgram"""
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
                print(f"📝 Transcription: {transcript}")
                return transcript
            else:
                print(f"❌ Erreur Deepgram: {response.status_code}")
                return ""
            
        except Exception as e:
            print(f"❌ Erreur STT: {e}")
            return ""
    
    async def text_to_speech(self, text):
        """TTS avec ElevenLabs"""
        try:
            print("🗣️ Génération vocale avec ElevenLabs...")
            
            audio = self.tts_client.text_to_speech.convert(
                text=text,
                voice_id="JBFqnCBsd6RMkjVDRZzb",  # Rachel
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128"
            )
            
            # Convertir le générateur en bytes
            audio_bytes = b''.join(audio)
            
            print("✅ Audio généré")
            return audio_bytes
            
        except Exception as e:
            print(f"❌ Erreur TTS: {e}")
            return None
    
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
        """LLM fallback simple (sans OpenAI)"""
        # Réponses prédéfinies pour le POC
        responses = {
            "bonjour": "Bonjour ! Je suis votre assistant vocal pour l'information sur la PrEP. Comment puis-je vous aider ?",
            "prep": "La PrEP (Prophylaxie Pré-Exposition) est un traitement préventif qui réduit le risque de contracter le VIH. Il est destiné aux personnes à risque élevé.",
            "comment": "La PrEP se prend sous forme de comprimé quotidien, de préférence à la même heure chaque jour.",
            "effet": "Les effets secondaires sont généralement légers et temporaires : nausées, maux de tête, fatigue. Consultez votre médecin en cas de doute.",
            "prix": "Le coût de la PrEP varie selon les pays et les assurances. En France, elle est remboursée à 100% sur prescription médicale.",
        }
        
        text_lower = text.lower()
        
        for keyword, response in responses.items():
            if keyword in text_lower:
                return response
        
        return "Je suis un assistant d'information sur la PrEP. Pourriez-vous reformuler votre question ? Vous pouvez me demander : qu'est-ce que la PrEP, comment la prendre, quels sont les effets secondaires, ou quel est son prix."
    
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
