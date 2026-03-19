#!/usr/bin/env python3
"""
Test Voice AI avec gTTS (gratuit) au lieu d'ElevenLabs
"""

import asyncio
import sys
import os

# Ajouter le répertoire courant au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from voice_agent import VoiceAgent

async def test_gtts():
    """Test avec gTTS gratuit"""
    print("🚀 Test Voice AI - gTTS (gratuit)")
    print("=" * 50)
    
    # Initialiser l'agent
    agent = VoiceAgent()
    print(f"✅ Agent initialisé (langue: {agent.current_language})")
    
    # Test simple
    test_phrase = "Bonjour comment allez-vous aujourd'hui"
    
    print(f"\n🎤 Test: '{test_phrase}'")
    
    try:
        # Étape 1: Simulation STT
        user_text = test_phrase
        print(f"✅ STT: '{user_text}'")
        
        # Étape 2: Génération réponse LLM
        response_text = await agent.get_llm_response(user_text)
        print(f"🤖 LLM: '{response_text[:100]}...'")  # Premiers 100 caractères
        
        # Étape 3: TTS avec gTTS directement
        print("🗣️ Test TTS avec gTTS...")
        try:
            from gtts import gTTS
            import io
            
            tts = gTTS(text=response_text, lang='fr', slow=False)
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            audio_bytes = audio_buffer.getvalue()
            
            print(f"✅ gTTS généré: {len(audio_bytes)} bytes")
            
            # Sauvegarder
            with open("test_gtts_output.mp3", "wb") as f:
                f.write(audio_bytes)
            print("💾 Audio sauvegardé: test_gtts_output.mp3")
            
            # Succès !
            print("\n🎉 SUCCÈS ! Le système fonctionne avec gTTS")
            return True
            
        except Exception as tts_error:
            print(f"❌ Erreur gTTS: {tts_error}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_gtts())
    if success:
        print("\n✅ Solution trouvée : utiliser gTTS dans l'application web")
    else:
        print("\n❌ Problème persiste")
