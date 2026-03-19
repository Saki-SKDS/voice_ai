#!/usr/bin/env python3
"""
Test simple de Voice AI en mode texte
Pour tester si le système fonctionne sans les problèmes audio
"""

import asyncio
import sys
import os

# Ajouter le répertoire courant au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from voice_agent import VoiceAgent

async def test_mode_texte():
    """Test du système en mode texte"""
    print("🚀 Test Voice AI - Mode Texte")
    print("=" * 50)
    
    # Initialiser l'agent
    agent = VoiceAgent()
    print(f"✅ Agent initialisé (langue: {agent.current_language})")
    
    # Tests de phrases
    test_phrases = [
        "Bonjour comment allez-vous",
        "Je voudrais un café s'il vous plaît",
        "Quel temps fait-il aujourd'hui",
        "Merci beaucoup",
        "Au revoir"
    ]
    
    print("\n📝 Tests de transcription:")
    print("-" * 30)
    
    for i, phrase in enumerate(test_phrases, 1):
        print(f"\n🎤 Test {i}: '{phrase}'")
        
        try:
            # Étape 1: Simulation STT (on a déjà le texte)
            user_text = phrase
            print(f"✅ STT: '{user_text}'")
            
            # Étape 2: Génération réponse LLM
            response_text = await agent.get_llm_response(user_text)
            print(f"🤖 LLM: '{response_text}'")
            
            # Étape 3: Synthèse vocale (TTS)
            response_audio = await agent.text_to_speech(response_text, agent.current_language)
            
            if response_audio:
                print(f"🗣️ TTS: {len(response_audio)} bytes générés")
                # Sauvegarder l'audio pour test
                with open(f"test_audio_{i}.mp3", "wb") as f:
                    f.write(response_audio)
                print(f"💾 Audio sauvegardé: test_audio_{i}.mp3")
            else:
                print("❌ TTS échoué")
                
        except Exception as e:
            print(f"❌ Erreur test {i}: {e}")
    
    print("\n🎉 Tests terminés !")
    print("📁 Fichiers audio générés dans le dossier courant")

if __name__ == "__main__":
    asyncio.run(test_mode_texte())
