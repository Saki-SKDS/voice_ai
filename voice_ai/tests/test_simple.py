import os
import sounddevice as sd
import numpy as np
import wave
import requests
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import play
import openai

load_dotenv()

# Clés API
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

print("="*50)
print("TEST SIMPLE STT + LLM + TTS")
print("="*50)

# 1. Enregistrement audio
print("\n🎤 Parle dans le micro (5 secondes)...")
fs = 16000
duration = 5
recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
sd.wait()
print("✅ Enregistrement terminé")

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
    print(f"📝 Texte: {text}")
else:
    print(f"❌ Erreur Deepgram: {response.status_code} - {response.text}")
    exit()

if not text:
    print("❌ Aucun texte détecté")
    exit()

# 3. OpenAI LLM
print("\n🧠 Génération réponse...")
client = openai.OpenAI(api_key=OPENAI_API_KEY)
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": text}],
    max_tokens=100
)
reponse = response.choices[0].message.content
print(f"🤖 Réponse: {reponse}")

# 4. ElevenLabs TTS
print("\n🗣️ Synthèse vocale...")
client_tts = ElevenLabs(api_key=ELEVENLABS_API_KEY)
audio = client_tts.generate(
    text=reponse,
    voice="Rachel",
    model="eleven_multilingual_v2"
)
print("🔊 Lecture...")
play(audio)

print("\n✅ Test terminé avec succès !")
