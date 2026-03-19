#!/usr/bin/env python3
"""
Solution complète pour configurer le microphone
"""

import sounddevice as sd
import numpy as np
import asyncio
import voice_agent
import os

def list_microphones():
    """Lister tous les micros disponibles avec détails"""
    print("🎤 LISTE COMPLÈTE DES MICROPHONES")
    print("=" * 60)
    
    devices = sd.query_devices()
    
    print("📋 Microphones disponibles:")
    micro_list = []
    
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            info = {
                'id': i,
                'name': device['name'],
                'channels': device['max_input_channels'],
                'sample_rate': device['default_samplerate']
            }
            micro_list.append(info)
            print(f"  🎤 {i}: {device['name']}")
            print(f"     Canaux: {device['max_input_channels']}")
            print(f"     Taux: {device['default_samplerate']} Hz")
            print()
    
    return micro_list

def test_microphone(micro_id, duration=3):
    """Tester un micro spécifique"""
    print(f"🎧 TEST MICRO #{micro_id}")
    print("=" * 40)
    
    try:
        # Configurer ce micro
        sd.default.device = (micro_id, sd.default.device[1])
        
        device = sd.query_devices(micro_id)
        print(f"🎤 Micro sélectionné: {device['name']}")
        
        print(f"📢 Parlez maintenant pendant {duration} secondes...")
        print("   Comptez à voix haute: 1, 2, 3...")
        
        # Enregistrement
        sample_rate = 16000
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
        
        print(f"\n📊 Analyse audio:")
        print(f"   Volume max: {max_volume:.1f}")
        print(f"   Volume moyen: {avg_volume:.1f}")
        
        # Diagnostic
        if max_volume < 100:
            print("❌ PROBLÈME: Volume trop bas - micro ne capte rien")
            return False
        elif max_volume < 1000:
            print("⚠️  Volume faible - parle plus fort ou rapproche-toi")
        elif max_volume > 20000:
            print("⚠️  Volume saturé - parle moins fort")
        else:
            print("✅ Volume correct")
        
        # Test avec silence
        silence_threshold = 0.1 * max_volume
        non_silent_samples = np.sum(np.abs(audio_data) > silence_threshold)
        speech_ratio = non_silent_samples / len(audio_data)
        
        print(f"🗣️  Ratio parole/silence: {speech_ratio:.2f}")
        
        if speech_ratio < 0.1:
            print("❌ PROBLÈME: Trop de silence - micro ne capte pas la voix")
            return False
        elif speech_ratio > 0.8:
            print("⚠️  Trop de signal -可能有背景噪音")
        else:
            print("✅ Bon ratio parole/silence")
        
        # Sauvegarder pour test STT
        import wave
        with wave.open(f"test_micro_{micro_id}.wav", "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data.tobytes())
        
        print(f"✅ Audio sauvegardé: test_micro_{micro_id}.wav")
        
        # Test STT
        print("🧪 Test STT avec cet audio...")
        success = asyncio.run(test_stt_with_file(f"test_micro_{micro_id}.wav"))
        
        return success
        
    except Exception as e:
        print(f"❌ Erreur test micro #{micro_id}: {e}")
        return False

async def test_stt_with_file(audio_file):
    """Test STT avec fichier audio"""
    try:
        agent = voice_agent.VoiceAgent('fr')
        
        if os.path.exists(audio_file):
            transcription = await agent.speech_to_text(audio_file)
            print(f"📍 Transcription: '{transcription}'")
            
            if transcription and len(transcription.strip()) > 5:
                print("✅ STT fonctionne - micro est bon!")
                return True
            else:
                print("❌ STT ne comprend rien - micro a des problèmes")
                return False
        else:
            print("❌ Fichier audio non trouvé")
            return False
            
    except Exception as e:
        print(f"❌ Erreur STT: {e}")
        return False

def find_best_microphone():
    """Trouver le meilleur micro automatiquement"""
    print("🔍 RECHERCHE AUTOMATIQUE DU MEILLEUR MICRO")
    print("=" * 50)
    
    micro_list = list_microphones()
    
    best_micro = None
    best_score = 0
    
    for micro in micro_list:
        print(f"\n🎤 Test micro: {micro['name']}")
        
        # Test rapide (1 seconde)
        try:
            sd.default.device = (micro['id'], sd.default.device[1])
            
            print("📢 Dites 'test' maintenant...")
            audio_data = sd.rec(
                16000,  # 1 seconde
                samplerate=16000,
                channels=1,
                dtype='int16',
                blocking=True
            )
            
            max_volume = np.max(np.abs(audio_data))
            
            # Scoring simple
            if 1000 < max_volume < 15000:  # Bon volume
                score = 100
                print("✅ Volume excellent")
            elif 500 < max_volume < 20000:  # Volume acceptable
                score = 70
                print("⚠️  Volume acceptable")
            else:
                score = 0
                print("❌ Volume inacceptable")
            
            if score > best_score:
                best_score = score
                best_micro = micro
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    return best_micro, best_score

def fix_micro_settings():
    """Appliquer les corrections pour le micro"""
    print("🔧 APPLICATION DES CORRECTIONS MICRO")
    print("=" * 40)
    
    # 1. Trouver le meilleur micro
    best_micro, score = find_best_microphone()
    
    if best_micro and score > 50:
        print(f"\n✅ Meilleur micro trouvé: {best_micro['name']}")
        print(f"🎯 Configuration recommandée:")
        print(f"   ID: {best_micro['id']}")
        print(f"   Canaux: 1 (mono)")
        print(f"   Taux: 16000 Hz")
        print(f"   Format: int16")
        
        # 2. Configurer ce micro par défaut
        sd.default.device = (best_micro['id'], sd.default.device[1])
        # Note: samplerate et channels se configurent lors de l'enregistrement
        
        print(f"✅ Micro configuré par défaut!")
        
        # 3. Test final
        print(f"\n🧪 Test final...")
        success = test_microphone(best_micro['id'], duration=5)
        
        if success:
            print(f"\n🎉 SUCCÈS! Micro est maintenant configuré!")
            return True
        else:
            print(f"\n❌ Le micro sélectionné a encore des problèmes")
            return False
    else:
        print(f"\n❌ Aucun micro satisfaisant trouvé")
        print(f"💡 Solutions:")
        print(f"   1. Brancher un micro externe")
        print(f"   2. Utiliser micro du casque")
        print(f"   3. Utiliser interface web (micro navigateur)")
        return False

if __name__ == "__main__":
    print("🚀 DÉMARRAGE CONFIGURATION MICRO")
    print("=" * 50)
    
    # Option 1: Test automatique
    print("🔧 Option 1: Configuration automatique")
    auto_success = fix_micro_settings()
    
    if not auto_success:
        print("\n🎤 Option 2: Test manuel des micros")
        
        # Lister tous les micros
        micro_list = list_microphones()
        
        print("\n👆 Choisissez un micro à tester (entrez le numéro):")
        try:
            choice = input("Numéro du micro: ")
            micro_id = int(choice)
            
            if micro_id in [m['id'] for m in micro_list]:
                test_microphone(micro_id, duration=5)
            else:
                print("❌ Numéro invalide")
        except:
            print("❌ Entrée invalide")
    
    print("\n🎯 CONFIGURATION TERMINÉE")
    print("💡 Si ça ne marche toujours pas:")
    print("   1. Utiliser interface web: http://127.0.0.1:5002")
    print("   2. Uploader des fichiers audio")
    print("   3. Utiliser un micro externe")
