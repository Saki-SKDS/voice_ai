#!/usr/bin/env python3
"""
Test de qualité audio et diagnostic du micro
"""

import asyncio
import voice_agent
import numpy as np
import sounddevice as sd
import wave
import os

def test_microphone():
    """Test complet du microphone"""
    print("🎤 TEST MICROPHONE ET QUALITÉ AUDIO")
    print("=" * 50)
    
    # 1. Détecter micros disponibles
    try:
        devices = sd.query_devices()
        print("📋 Micros disponibles:")
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                print(f"  {i}: {device['name']} (entrées: {device['max_input_channels']})")
        
        default_input = sd.default.device[0]
        print(f"🎯 Micro par défaut: {devices[default_input]['name']}")
        
    except Exception as e:
        print(f"❌ Erreur détection micro: {e}")
        return False
    
    # 2. Test enregistrement
    print("\n🎤 Test enregistrement (3 secondes)...")
    print("Parlez maintenant...")
    
    try:
        sample_rate = 16000
        duration = 3
        
        # Enregistrement
        audio_data = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype='int16',
            blocking=True
        )
        
        # Analyse qualité
        max_volume = np.max(np.abs(audio_data))
        avg_volume = np.mean(np.abs(audio_data))
        
        print(f"🔊 Volume max: {max_volume:.3f}")
        print(f"🔊 Volume moyen: {avg_volume:.3f}")
        
        if max_volume < 0.01:
            print("❌ Volume trop bas - micro ne fonctionne pas?")
        elif max_volume < 0.1:
            print("⚠️ Volume faible - parle plus fort")
        elif max_volume > 0.95:
            print("⚠️ Volume saturé - parle moins fort")
        else:
            print("✅ Volume correct")
        
        # Sauvegarder pour test
        with wave.open("test_micro.wav", "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data.tobytes())
        
        print("✅ Audio sauvegardé: test_micro.wav")
        
        # 3. Test STT avec cet audio
        print("\n🧪 Test STT avec audio enregistré...")
        asyncio.run(test_stt_with_audio())
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur enregistrement: {e}")
        return False

async def test_stt_with_audio():
    """Test STT avec le fichier audio enregistré"""
    try:
        agent = voice_agent.VoiceAgent('fr')
        
        if os.path.exists("test_micro.wav"):
            transcription = await agent.speech_to_text("test_micro.wav")
            print(f"📍 Transcription: {transcription}")
            
            if transcription and len(transcription.strip()) > 0:
                print("✅ STT fonctionne avec ton audio")
            else:
                print("❌ STT n'a rien compris - problème audio")
        else:
            print("❌ Fichier audio non trouvé")
            
    except Exception as e:
        print(f"❌ Erreur test STT: {e}")

def test_existing_audio():
    """Test avec fichier audio existant"""
    print("\n🎧 Test avec audio existant...")
    
    audio_files = [
        "web_app/static/demo_input.mp3",
        "demo_input.mp3", 
        "test_micro.wav"
    ]
    
    for audio_file in audio_files:
        if os.path.exists(audio_file):
            print(f"📍 Test avec: {audio_file}")
            asyncio.run(test_stt_with_file(audio_file))
            break
    else:
        print("❌ Aucun fichier audio trouvé")

async def test_stt_with_file(audio_file):
    """Test STT avec fichier spécifique"""
    try:
        agent = voice_agent.VoiceAgent('fr')
        transcription = await agent.speech_to_text(audio_file)
        print(f"📍 Transcription: {transcription}")
        
        if transcription and len(transcription.strip()) > 0:
            print("✅ STT fonctionne avec cet audio")
        else:
            print("❌ STT ne comprend pas cet audio")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    print("🚀 DÉMARRAGE TEST AUDIO")
    print("=" * 50)
    
    # Test 1: Microphone
    test_microphone()
    
    # Test 2: Audio existant
    test_existing_audio()
    
    print("\n🎯 TEST AUDIO TERMINÉ")
    print("💡 Si ça ne marche pas, le problème est:")
    print("   - Microphone défectueux")
    print("   - Volume trop bas/élevé") 
    print("   - Bruit de fond")
    print("   - Format audio incompatible")
