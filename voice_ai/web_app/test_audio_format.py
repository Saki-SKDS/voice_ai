#!/usr/bin/env python3
"""
Script pour tester le format audio et comprendre pourquoi la transcription échoue
"""
import base64
import numpy as np
import wave
import io

def analyze_audio_file(file_path):
    """Analyse un fichier audio existant"""
    print(f"\n=== Analyse du fichier: {file_path} ===")
    
    with open(file_path, 'rb') as f:
        audio_data = f.read()
    
    print(f"Taille totale: {len(audio_data)} bytes")
    
    # Si c'est un WAV, analyser l'en-tête
    if audio_data.startswith(b'RIFF'):
        print("Format: WAV")
        
        # Créer un objet wav en mémoire
        wav_buffer = io.BytesIO(audio_data)
        with wave.open(wav_buffer, 'rb') as wav_file:
            channels = wav_file.getnchannels()
            sample_rate = wav_file.getframerate()
            sample_width = wav_file.getsampwidth()
            frames = wav_file.getnframes()
            
            print(f"Canaux: {channels}")
            print(f"Échantillonnage: {sample_rate} Hz")
            print(f"Taille échantillon: {sample_width} bytes")
            print(f"Nombre d'échantillons: {frames}")
            print(f"Durée: {frames/sample_rate:.2f} secondes")
            
            # Lire les données PCM
            pcm_data = wav_file.readframes(frames)
            print(f"Taille PCM: {len(pcm_data)} bytes")
            
            # Convertir en numpy array
            if sample_width == 2:
                audio_array = np.frombuffer(pcm_data, dtype=np.int16)
            else:
                audio_array = np.frombuffer(pcm_data, dtype=np.int8)
            
            print(f"Array shape: {audio_array.shape}")
            print(f"Array dtype: {audio_array.dtype}")
            
            # Calculer les métriques
            rms = np.sqrt(np.mean(audio_array.astype(float)**2))
            peak = np.max(np.abs(audio_array))
            
            print(f"RMS: {rms:.1f}")
            print(f"Peak: {peak:.1f}")
            print(f"RMS dB: {20*np.log10(rms+1e-10):.1f} dB")
            print(f"Peak dB: {20*np.log10(peak+1e-10):.1f} dB")
            
            # Vérifier si l'audio est trop faible
            if rms < 1000:
                print("⚠️  AUDIO TROP FAIBLE !")
            if peak < 10000:
                print("⚠️  PEAK TROP FAIBLE !")
                
    else:
        print("Format: Inconnu (pas WAV)")

if __name__ == "__main__":
    # Analyser les fichiers démo qui fonctionnent
    analyze_audio_file("static/demo_input.mp3")
    analyze_audio_file("static/demo_response.mp3")
    
    print("\n" + "="*60)
    print("Analyse terminée. Comparez ces métriques avec votre audio enregistré.")
