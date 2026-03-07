import os
from dotenv import load_dotenv

# Deepgram
from deepgram import DeepgramClient

# ElevenLabs - imports corrigés
from elevenlabs.client import ElevenLabs
from elevenlabs import play

# Charger les clés API
load_dotenv()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")

print("=" * 50)
print("VÉRIFICATION DES CLÉS API")
print("=" * 50)
print(f"DEEPGRAM_API_KEY: {DEEPGRAM_API_KEY[:10]}... (présente)")
print(f"OPENAI_API_KEY: {OPENAI_API_KEY[:10]}... (présente)")
print(f"ELEVENLABS_API_KEY: {ELEVENLABS_API_KEY[:10]}... (présente)")
print(f"LIVEKIT_URL: {LIVEKIT_URL}")
print("=" * 50)

# --- TEST 1: Deepgram STT ---
def test_deepgram():
    print("\n🔊 TEST 1: Deepgram Speech-to-Text")
    
    try:
        deepgram = DeepgramClient(api_key=DEEPGRAM_API_KEY)
        print("✅ Client Deepgram créé avec la clé API")
        return True
    except Exception as e:
        print(f"❌ Erreur Deepgram: {e}")
        return False

# --- TEST 2: ElevenLabs TTS ---
def test_elevenlabs():
    print("\n🗣️ TEST 2: ElevenLabs Text-to-Speech")
    
    try:
        from elevenlabs.client import ElevenLabs
        
        # Créer le client
        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        
        texte = "Bonjour, je suis un agent vocal en test."
        print(f"📝 Texte: {texte}")
        
        # Utiliser la méthode text_to_speech.convert
        print("🎤 Génération de la voix...")
        audio = client.text_to_speech.convert(
            text=texte,
            voice_id="JBFqnCBsd6RMkjVDRZzb",  # ID de "Rachel" (anglaise) - change pour "Domi" si besoin
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )
        
        # Convertir le générateur en bytes
        audio_bytes = b''.join(audio)
        
        # Sauvegarder temporairement pour lecture
        with open("test_audio.mp3", "wb") as f:
            f.write(audio_bytes)
        
        print("🔊 Lecture...")
        # Lire avec un lecteur système (alternative simple)
        import os
        os.system("start test_audio.mp3")  # Windows
        # os.system("open test_audio.mp3")  # Mac
        # os.system("xdg-open test_audio.mp3")  # Linux
        
        print("✅ TEST ELEVENLABS RÉUSSI")
        return True
    except Exception as e:
        print(f"❌ Erreur ElevenLabs: {e}")
        return False

# --- TEST 3: OpenAI LLM ---
def test_openai():
    print("\n🤖 TEST 3: OpenAI LLM")
    
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Bonjour"}],
            max_tokens=50
        )
        
        print(f"✅ Réponse OpenAI: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"❌ Erreur OpenAI: {e}")
        return False

# --- TEST 4: LiveKit ---
def test_livekit():
    print("\n🔗 TEST 4: LiveKit")
    
    try:
        from livekit import api
        
        # Créer le client API
        livekit_api = api.LiveKitAPI(LIVEKIT_API_KEY, LIVEKIT_API_SECRET, LIVEKIT_URL)
        print("✅ Client LiveKit créé")
        
        # Tester la création d'un token
        token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET) \
            .with_identity("test_user") \
            .with_name("Test User") \
            .with_grants(api.VideoGrants(
                room_join=True,
                room="test_room"
            ))
        
        jwt_token = token.to_jwt()
        print(f"✅ Token LiveKit généré: {jwt_token[:50]}...")
        
        # Fermer le client
        livekit_api.close()
        return True
    except Exception as e:
        print(f"❌ Erreur LiveKit: {e}")
        return False

def main():
    print("\n🚀 DÉBUT DES TESTS\n")
    
    dg_ok = test_deepgram()
    el_ok = test_elevenlabs()
    oa_ok = test_openai()
    lk_ok = test_livekit()
    
    print("\n" + "=" * 50)
    print("RÉSUMÉ DES TESTS")
    print("=" * 50)
    print(f"Deepgram:   {'✅' if dg_ok else '❌'}")
    print(f"ElevenLabs: {'✅' if el_ok else '❌'}")
    print(f"OpenAI:     {'✅' if oa_ok else '❌'}")
    print(f"LiveKit:    {'✅' if lk_ok else '❌'}")
    
    if dg_ok and el_ok and oa_ok and lk_ok:
        print("\n🎉 TOUS LES TESTS RÉUSSIS !")
    else:
        print("\n⚠️ Corrigeons ensemble")
    print("=" * 50)

if __name__ == "__main__":
    main()
