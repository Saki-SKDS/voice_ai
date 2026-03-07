import os
import requests
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

load_dotenv()

# Clés API
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

print("="*50)
print("TEST STT/TTS AVEC FICHIER AUDIO EXISTANT")
print("="*50)

# Utiliser le fichier temp.wav existant
if os.path.exists("temp.wav"):
    print("✅ Fichier temp.wav trouvé")
    
    # 1. Deepgram STT
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
            # 2. Réponse simple
            response_text = f"J'ai entendu: {text}. C'est une bonne question sur la PrEP !"
            print(f"🤖 Réponse: {response_text}")
            
            # 3. ElevenLabs TTS
            print("\n🗣️ Synthèse vocale...")
            client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
            
            audio = client.text_to_speech.convert(
                text=response_text,
                voice_id="JBFqnCBsd6RMkjVDRZzb",
                model_id="eleven_multilingual_v2"
            )
            
            audio_bytes = b''.join(audio)
            with open("response_file.mp3", "wb") as f:
                f.write(audio_bytes)
            
            print("🔊 Lecture de la réponse...")
            os.system("start response_file.mp3")
            print("\n✅ Test terminé avec succès !")
            
        else:
            print("❌ Le fichier audio ne contient pas de parole détectable")
            
    else:
        print(f"❌ Erreur Deepgram: {response.status_code}")
        print(f"Détails: {response.text}")
        
else:
    print("❌ Fichier temp.wav non trouvé")
    print("💡 Créons un fichier de test...")
    
    # Créer un fichier audio de test avec ElevenLabs
    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    
    test_text = "Bonjour, je voudrais des informations sur la PrEP"
    print(f"🎤 Génération audio de test: '{test_text}'")
    
    audio = client.text_to_speech.convert(
        text=test_text,
        voice_id="JBFqnCBsd6RMkjVDRZzb",
        model_id="eleven_multilingual_v2"
    )
    
    audio_bytes = b''.join(audio)
    
    # Convertir en WAV (nécessite une bibliothèque supplémentaire)
    with open("test_input.mp3", "wb") as f:
        f.write(audio_bytes)
    
    print("✅ Fichier test_input.mp3 créé")
    print("🔊 Lecture du fichier de test...")
    os.system("start test_input.mp3")
