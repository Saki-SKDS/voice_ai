import os
from dotenv import load_dotenv
from livekit import api
import asyncio
import json

load_dotenv()

LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")

print("="*50)
print("🚀 SERVEUR TOKEN LIVEKIT")
print("="*50)
print(f"✅ LiveKit URL: {LIVEKIT_URL}")
print("="*50)

async def generate_token():
    # Créer un token pour l'utilisateur
    token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET) \
        .with_identity("web_user") \
        .with_name("Web User") \
        .with_grants(api.VideoGrants(
            room_join=True,
            room="test_room"
        ))
    
    return token.to_jwt()

if __name__ == "__main__":
    token = asyncio.run(generate_token())
    print("\n🎫 Token généré :")
    print(token)
    print("\n📝 Copie ce token dans index.html")
