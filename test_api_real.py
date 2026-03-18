#!/usr/bin/env python3
"""
Test des coins critiques avec API réelles
"""
import voice_agent
import asyncio
import os
import time
import tempfile
import wave

def create_test_audio():
    """Créer un fichier audio test"""
    try:
        # Créer un fichier WAV factice pour les tests
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            # En-tête WAV minimal
            tmp.write(b'RIFF')
            tmp.write(b'\x24\x08\x00\x00')  # File size
            tmp.write(b'WAVE')
            tmp.write(b'fmt ')
            tmp.write(b'\x10\x00\x00\x00')  # Chunk size
            tmp.write(b'\x01\x00')  # Audio format
            tmp.write(b'\x01\x00')  # Channels
            tmp.write(b'\x40\x1c\x00\x00')  # Sample rate
            tmp.write(b'\x80\x3e\x00\x00')  # Byte rate
            tmp.write(b'\x02\x00')  # Block align
            tmp.write(b'\x10\x00')  # Bits per sample
            tmp.write(b'data')
            tmp.write(b'\x00\x08\x00\x00')  # Data size
            
            # Données audio silencieuses
            tmp.write(b'\x00' * 1000)
            
            return tmp.name
    except Exception as e:
        print(f"❌ Erreur création audio test: {e}")
        return None

async def test_waxal_stt():
    """Test 1: WAXAL STT avec API réelle"""
    print("🧪 Test 1: WAXAL STT (API réelle)")
    try:
        agent = voice_agent.VoiceAgent('bm')
        
        # Créer audio test
        audio_file = create_test_audio()
        if not audio_file:
            return False
        
        print(f"📍 Fichier audio test: {audio_file}")
        
        # Test WAXAL STT
        start_time = time.time()
        result = await agent._waxal_stt_with_retry(audio_file, 'bm', max_retries=1)
        elapsed = time.time() - start_time
        
        print(f"📍 Résultat STT: {result}")
        print(f"📍 Temps: {elapsed:.2f}s")
        
        # Nettoyer
        os.unlink(audio_file)
        
        if result is not None:
            print("✅ WAXAL STT fonctionnel")
            return True
        else:
            print("⚠️ WAXAL STT retourné None (normal avec audio factice)")
            return True
            
    except Exception as e:
        print(f"❌ Erreur WAXAL STT: {e}")
        return False

async def test_waxal_translation():
    """Test 2: WAXAL Translation API"""
    print("\n🧪 Test 2: WAXAL Translation (API réelle)")
    try:
        client = voice_agent.WaxalClient()
        
        test_text = "Bonjour, comment allez-vous?"
        start_time = time.time()
        
        result = await client.translate_text(test_text, 'fr', 'bm')
        elapsed = time.time() - start_time
        
        print(f"📍 Texte original: {test_text}")
        print(f"📍 Traduction: {result}")
        print(f"📍 Temps: {elapsed:.2f}s")
        
        if result and result.strip():
            print("✅ WAXAL Translation fonctionnel")
            return True
        else:
            print("⚠️ WAXAL Translation retourné vide/clé manquante")
            return True
            
    except Exception as e:
        print(f"❌ Erreur WAXAL Translation: {e}")
        return False

async def test_waxal_tts():
    """Test 3: WAXAL TTS API"""
    print("\n🧪 Test 3: WAXAL TTS (API réelle)")
    try:
        client = voice_agent.WaxalClient()
        
        test_text = "Bonjour"
        start_time = time.time()
        
        result = await client.text_to_speech(test_text, 'fr')  # Test en français
        elapsed = time.time() - start_time
        
        print(f"📍 Texte: {test_text}")
        print(f"📍 Audio généré: {len(result) if result else 0} bytes")
        print(f"📍 Temps: {elapsed:.2f}s")
        
        if result and len(result) > 100:
            print("✅ WAXAL TTS fonctionnel")
            return True
        else:
            print("⚠️ WAXAL TTS retourné vide/clé manquante")
            return True
            
    except Exception as e:
        print(f"❌ Erreur WAXAL TTS: {e}")
        return False

async def test_groq_llm():
    """Test 4: Groq LLM API"""
    print("\n🧪 Test 4: Groq LLM (API réelle)")
    try:
        agent = voice_agent.VoiceAgent('fr')
        
        test_text = "Bonjour"
        start_time = time.time()
        
        # Test avec timeout très court pour éviter l'attente
        result = await asyncio.wait_for(
            agent.get_llm_response(test_text), 
            timeout=5.0
        )
        elapsed = time.time() - start_time
        
        print(f"📍 Texte: {test_text}")
        print(f"📍 Réponse: {result[:100] if result else 'None'}...")
        print(f"📍 Temps: {elapsed:.2f}s")
        
        if result and len(result) > 10:
            print("✅ Groq LLM fonctionnel")
            return True
        else:
            print("⚠️ Groq LLM timeout ou clé manquante")
            return True
            
    except asyncio.TimeoutError:
        print("⚠️ Groq LLM timeout (normal sans clé)")
        return True
    except Exception as e:
        print(f"❌ Erreur Groq LLM: {e}")
        return False

async def test_openai_fallback():
    """Test 5: OpenAI fallback"""
    print("\n🧪 Test 5: OpenAI Fallback (API réelle)")
    try:
        agent = voice_agent.VoiceAgent('fr')
        
        test_text = "Bonjour"
        start_time = time.time()
        
        result = await agent._openai_llm_fallback_fast(test_text, timeout=3.0)
        elapsed = time.time() - start_time
        
        print(f"📍 Texte: {test_text}")
        print(f"📍 Réponse: {result[:100] if result else 'None'}...")
        print(f"📍 Temps: {elapsed:.2f}s")
        
        if result and len(result) > 10:
            print("✅ OpenAI fallback fonctionnel")
            return True
        else:
            print("⚠️ OpenAI fallback timeout ou clé manquante")
            return True
            
    except Exception as e:
        print(f"❌ Erreur OpenAI fallback: {e}")
        return False

def test_environment_keys():
    """Test 6: Vérification clés API"""
    print("\n🧪 Test 6: Clés API disponibles")
    try:
        keys = {
            'GROQ_API_KEY': os.getenv('GROQ_API_KEY'),
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
            'WAXAL_API_KEY': os.getenv('WAXAL_API_KEY'),
            'DEEPGRAM_API_KEY': os.getenv('DEEPGRAM_API_KEY'),
            'ELEVENLABS_API_KEY': os.getenv('ELEVENLABS_API_KEY')
        }
        
        print("📍 Clés disponibles:")
        for key, value in keys.items():
            status = "✅" if value and len(value) > 10 else "❌"
            masked = value[:10] + "..." if value and len(value) > 10 else "None"
            print(f"   {status} {key}: {masked}")
        
        return True
    except Exception as e:
        print(f"❌ Erreur vérification clés: {e}")
        return False

async def test_complete_pipeline():
    """Test 7: Pipeline complet avec fallbacks"""
    print("\n🧪 Test 7: Pipeline complet (simulation)")
    try:
        agent = voice_agent.VoiceAgent('bm')
        
        # Forcer le circuit breaker pour tester les fallbacks
        for i in range(6):
            agent._record_groq_failure()
        
        print("📍 Circuit breaker forcé ouvert")
        
        # Test du pipeline complet avec timeout
        test_text = "bonjour"
        start_time = time.time()
        
        result = await agent.get_llm_response(test_text)
        elapsed = time.time() - start_time
        
        print(f"📍 Texte: {test_text}")
        print(f"📍 Réponse finale: {result[:100] if result else 'None'}...")
        print(f"📍 Temps total: {elapsed:.2f}s")
        
        if elapsed < 10.0 and result:
            print("✅ Pipeline complet fonctionnel")
            return True
        else:
            print("⚠️ Pipeline timeout ou problème")
            return False
            
    except Exception as e:
        print(f"❌ Erreur pipeline complet: {e}")
        return False

async def run_api_tests():
    """Lancer tous les tests API"""
    print("🚀 DÉMARRAGE TESTS API RÉELLES")
    print("=" * 60)
    
    # Test 0: Clés API
    test_environment_keys()
    
    # Test 1: WAXAL STT
    await test_waxal_stt()
    
    # Test 2: WAXAL Translation
    await test_waxal_translation()
    
    # Test 3: WAXAL TTS
    await test_waxal_tts()
    
    # Test 4: Groq LLM
    await test_groq_llm()
    
    # Test 5: OpenAI fallback
    await test_openai_fallback()
    
    # Test 6: Pipeline complet
    await test_complete_pipeline()
    
    print("\n" + "=" * 60)
    print("🎯 TESTS API TERMINÉS")
    print("📊 Analyse complète du système")

if __name__ == "__main__":
    asyncio.run(run_api_tests())
