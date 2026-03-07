import os
from dotenv import load_dotenv
from livekit import api

load_dotenv()

LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
LIVEKIT_URL = os.getenv("LIVEKIT_URL")

print("="*50)
print("TEST SIMPLE LIVEKIT")
print("="*50)

try:
    # Créer un token simple
    token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET) \
        .with_identity("test_user") \
        .with_name("Test User") \
        .with_grants(api.VideoGrants(
            room_join=True,
            room="test_room"
        ))
    
    jwt_token = token.to_jwt()
    print(f"✅ Token LiveKit généré avec succès !")
    print(f"📝 Token (premiers 50 chars): {jwt_token[:50]}...")
    print(f"🔗 URL LiveKit: {LIVEKIT_URL}")
    print(f"🎫 Room: test_room")
    print(f"👤 Utilisateur: test_user")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
