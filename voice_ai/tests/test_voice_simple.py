import os
import sounddevice as sd
import numpy as np
import wave
import requests
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

load_dotenv()

# Clés API
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

print("="*50)
print("TEST SIMPLE STT + TTS (sans OpenAI)")
print("="*50)

# 1. Enregistrement audio
print("\n🎤 Parle dans le micro (5 secondes)...")
fs = 16000
duration = 5
recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
sd.wait()
print("✅ Enregistrement terminé")

# Calculer le niveau audio pour vérifier
audio_level = np.sqrt(np.mean(recording**2))
print(f"📊 Niveau audio: {audio_level:.2f}")

if audio_level < 100:
    print("⚠️ Audio très faible, parlez plus fort !")

# Sauvegarder en WAV
with wave.open("temp.wav", 'wb') as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(fs)
    wf.writeframes(recording.tobytes())

# 2. Deepgram STT avec requête directe
print("\n🔊 Transcription avec Deepgram...")

url = "https://api.deepgram.com/v1/listen?model=nova-2&language=fr"
headers = {
    "Authorization": f"Token {DEEPGRAM_API_KEY}",
    "Content-Type": "audio/wav"
}

with open("temp.wav", "rb") as audio:
    response = requests.post(url, headers=headers, data=audio)

if response.status_code == 200:
    result = response.json()
    text = result["results"]["channels"][0]["alternatives"][0]["transcript"]
    print(f"📝 Texte: '{text}'")
    
    if text.strip():
        # 3. Réponse simple (fallback sans OpenAI)
        responses = {
            "bonjour": "Bonjour ! Je suis votre assistant vocal PrEP.",
            "prep": "La PrEP est un traitement préventif contre le VIH.",
            "comment": "La PrEP se prend en comprimé quotidien.",
            "effet": "Les effets secondaires sont généralement légers.",
        }
        
        text_lower = text.lower()
        response_text = "Je suis un assistant d'information sur la PrEP."
        
        for keyword, resp in responses.items():
            if keyword in text_lower:
                response_text = resp
                break
        
        print(f"🤖 Réponse: {response_text}")
        
        # 4. ElevenLabs TTS
        print("\n🗣️ Synthèse vocale...")
        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        
        audio = client.text_to_speech.convert(
            text=response_text,
            voice_id="JBFqnCBsd6RMkjVDRZzb",  # Rachel
            model_id="eleven_multilingual_v2"
        )
        
        # Sauvegarder et jouer
        audio_bytes = b''.join(audio)
        with open("response.mp3", "wb") as f:
            f.write(audio_bytes)
        
        print("🔊 Lecture de la réponse...")
        os.system("start response.mp3")
        
        print("\n✅ Test terminé avec succès !")
        
    else:
        print("❌ Aucun texte détecté - parlez plus clairement")
        
else:
    print(f"❌ Erreur Deepgram: {response.status_code} - {response.text}")
