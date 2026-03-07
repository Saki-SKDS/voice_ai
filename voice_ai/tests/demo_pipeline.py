import os
import requests
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

load_dotenv()

# Clés API
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

print("="*60)
print("🎤 DÉMONSTRATION PIPELINE VOCAL COMPLET")
print("="*60)

# Étape 1: Générer un audio de test avec ElevenLabs
print("\n1️⃣ Génération audio de test...")
client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

test_text = "Bonjour, je voudrais savoir ce qu'est la PrEP et comment ça fonctionne"
print(f"📝 Texte: '{test_text}'")

# Générer l'audio
audio = client.text_to_speech.convert(
    text=test_text,
    voice_id="JBFqnCBsd6RMkjVDRZzb",  # Rachel
    model_id="eleven_multilingual_v2"
)

# Sauvegarder l'audio généré
audio_bytes = b''.join(audio)
with open("demo_input.mp3", "wb") as f:
    f.write(audio_bytes)

print("✅ Audio de test généré: demo_input.mp3")

# Étape 2: Transcrire avec Deepgram
print("\n2️⃣ Transcription Deepgram...")

# Pour Deepgram, il faut convertir en WAV ou utiliser le bon format
# Utilisons un endpoint qui accepte plus de formats
url = "https://api.deepgram.com/v1/listen?model=nova-2&language=fr"
headers = {
    "Authorization": f"Token {DEEPGRAM_API_KEY}",
    "Content-Type": "audio/mpeg"  # MP3
}

with open("demo_input.mp3", "rb") as audio_file:
    response = requests.post(url, headers=headers, data=audio_file)

if response.status_code == 200:
    result = response.json()
    transcript = result["results"]["channels"][0]["alternatives"][0]["transcript"]
    print(f"📝 Transcription: '{transcript}'")
    
    # Étape 3: Générer une réponse
    print("\n3️⃣ Génération réponse...")
    
    # Réponses intelligentes basées sur le contenu
    if "prep" in transcript.lower() or "prép" in transcript.lower():
        response_text = "La PrEP ou Prophylaxie Pré-Exposition est un médicament préventif qui réduit considérablement le risque de contracter le VIH. Il s'agit d'un comprimé à prendre quotidiennement."
    elif "comment" in transcript.lower():
        response_text = "La PrEP se prend sous forme d'un comprimé par jour, de préférence à la même heure. Il est important de ne pas oublier de prise pour maintenir l'efficacité."
    else:
        response_text = f"J'ai bien entendu votre question: {transcript}. Je suis un assistant spécialisé sur la PrEP, puis-je vous aider sur ce sujet ?"
    
    print(f"🤖 Réponse: {response_text}")
    
    # Étape 4: Synthèse vocale de la réponse
    print("\n4️⃣ Synthèse vocale de la réponse...")
    
    response_audio = client.text_to_speech.convert(
        text=response_text,
        voice_id="JBFqnCBsd6RMkjVDRZzb",
        model_id="eleven_multilingual_v2"
    )
    
    response_bytes = b''.join(response_audio)
    with open("demo_response.mp3", "wb") as f:
        f.write(response_bytes)
    
    print("✅ Audio réponse généré: demo_response.mp3")
    
    # Étape 5: Lecture automatique
    print("\n5️⃣ Lecture des fichiers audio...")
    
    print("🔊 Lecture audio original...")
    os.system("start demo_input.mp3")
    
    import time
    time.sleep(3)  # Attendre un peu
    
    print("🔊 Lecture réponse vocale...")
    os.system("start demo_response.mp3")
    
    print("\n" + "="*60)
    print("🎉 PIPELINE VOCAL COMPLET FONCTIONNEL !")
    print("="*60)
    print("✅ STT: Deepgram fonctionne")
    print("✅ TTS: ElevenLabs fonctionne") 
    print("✅ Pipeline: Audio → Texte → Réponse → Audio")
    print("\n📝 Prochaine étape: Intégrer avec l'interface web LiveKit")
    
else:
    print(f"❌ Erreur Deepgram: {response.status_code}")
    try:
        error_details = response.json()
        print(f"Détails: {error_details}")
    except:
        print(f"Response: {response.text[:200]}")
