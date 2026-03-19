#!/usr/bin/env python3
"""
Test micro avec vraie parole - compte à rebours
"""

import sounddevice as sd
import numpy as np
import asyncio
import voice_agent
import os
import time

def test_micro_avec_parole():
    """Test micro avec temps pour parler"""
    print("🎤 TEST MICRO AVEC VRAIE PAROLE")
    print("=" * 50)
    
    # Compte à rebours pour préparation
    print("⏳ Prépare-toi à parler...")
    for i in range(3, 0, -1):
        print(f"   {i}...")
        time.sleep(1)
    
    print("📢 PARLE MAINTENANT ! (dis 'bonjour comment allez-vous')")
    print("   Tu as 5 secondes...")
    
    try:
        # Enregistrement
        sample_rate = 16000
        duration = 5
        
        audio_data = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype='int16',
            blocking=True
        )
        
        # Analyse
        max_volume = np.max(np.abs(audio_data))
        avg_volume = np.mean(np.abs(audio_data))
        
        print(f"\n📊 Analyse audio:")
        print(f"   Volume max: {max_volume:.1f}")
        print(f"   Volume moyen: {avg_volume:.1f}")
        
        # Diagnostic
        if max_volume < 500:
            print("❌ PROBLÈME: Trop silencieux - as-tu bien parlé ?")
            return False
        elif max_volume < 2000:
            print("⚠️  Volume faible - parle un peu plus fort")
        elif max_volume > 20000:
            print("⚠️  Volume saturé - parle moins fort")
        else:
            print("✅ Volume parfait !")
        
        # Analyse parole vs silence
        silence_threshold = 0.1 * max_volume
        non_silent_samples = np.sum(np.abs(audio_data) > silence_threshold)
        speech_ratio = non_silent_samples / len(audio_data)
        
        print(f"🗣️  Ratio parole/silence: {speech_ratio:.2f}")
        
        if speech_ratio < 0.2:
            print("❌ PROBLÈME: Trop de silence - as-tu parlé continuellement ?")
            return False
        elif speech_ratio > 0.9:
            print("⚠️  Trop de signal -可能有背景噪音")
        else:
            print("✅ Bon ratio parole/silence")
        
        # Sauvegarder
        import wave
        with wave.open("test_vraie_parole.wav", "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data.tobytes())
        
        print("✅ Audio sauvegardé: test_vraie_parole.wav")
        
        # Test STT
        print("\n🧪 Test STT avec ta vraie parole...")
        success = asyncio.run(test_stt_with_audio("test_vraie_parole.wav"))
        
        return success
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

async def test_stt_with_audio(audio_file):
    """Test STT avec fichier audio"""
    try:
        agent = voice_agent.VoiceAgent('fr')
        
        if os.path.exists(audio_file):
            print(f"🎤 Fichier: {audio_file}")
            transcription = await agent.speech_to_text(audio_file)
            print(f"📍 Transcription: '{transcription}'")
            
            if transcription and len(transcription.strip()) > 3:
                print("✅ SUCCÈS ! STT a compris ta parole")
                print("🎉 Le micro fonctionne !")
                return True
            else:
                print("❌ STT n'a rien compris")
                print("💡 Essaie de parler plus fort ou plus clairement")
                return False
        else:
            print("❌ Fichier audio non trouvé")
            return False
            
    except Exception as e:
        print(f"❌ Erreur STT: {e}")
        return False

if __name__ == "__main__":
    print("🚀 DÉMARRAGE TEST MICRO VRAIE PAROLE")
    print("=" * 50)
    print("💡 Ce test te donne le temps de parler")
    print("💡 Dis: 'bonjour comment allez-vous'")
    print()
    
    success = test_micro_avec_parole()
    
    if success:
        print("\n🎉 SUCCÈS TOTAL !")
        print("✅ Micro fonctionne")
        print("✅ STT fonctionne") 
        print("✅ VoiceAgent est prêt !")
    else:
        print("\n❌ PROBLÈME DÉTECTÉ")
        print("💡 Solutions:")
        print("   1. Parle plus fort")
        print("   2. Rapproche-toi du micro")
        print("   3. Réduis le bruit de fond")
        print("   4. Utilise un micro externe")
        print("   5. Utilise interface web (micro navigateur)")
