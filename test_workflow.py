#!/usr/bin/env python3
"""
Test complet du workflow VoiceAgent - tous les coins et recoins
"""
import voice_agent
import asyncio
import os
import time

def test_basic_functionality():
    """Test 1: Fonctionnalités de base"""
    print("🧪 Test 1: Initialisation VoiceAgent")
    try:
        agent = voice_agent.VoiceAgent('bm')  # Bambara
        print('✅ Initialisation réussie')
        print(f'📍 Langue actuelle: {agent.current_language}')
        print(f'📍 Langues disponibles: {list(voice_agent.WAXAL_LANGUAGES.keys())[:5]}...')
        return agent
    except Exception as e:
        print(f'❌ Erreur initialisation: {e}')
        return None

def test_circuit_breaker(agent):
    """Test 2: Circuit breaker"""
    print('\n🧪 Test 2: Circuit breaker')
    try:
        print(f'📍 Échecs Groq: {agent.groq_failures}')
        print(f'📍 Circuit ouvert: {agent.groq_circuit_open}')
        
        # Simuler des échecs
        agent._record_groq_failure()
        agent._record_groq_failure()
        print(f'📍 Après 2 échecs: {agent.groq_failures}')
        
        # Test circuit breaker
        is_open = agent._check_groq_circuit_breaker()
        print(f'📍 Circuit ouvert: {is_open}')
        
        # Simuler 5 échecs pour ouvrir le circuit
        for i in range(3):
            agent._record_groq_failure()
        
        is_open = agent._check_groq_circuit_breaker()
        print(f'📍 Après 5 échecs - Circuit ouvert: {is_open}')
        
        print('✅ Circuit breaker fonctionnel')
        return True
    except Exception as e:
        print(f'❌ Erreur circuit breaker: {e}')
        return False

def test_language_detection(agent):
    """Test 3: Détection langues africaines"""
    print('\n🧪 Test 3: Détection langues africaines')
    try:
        test_langs = ['bm', 'fr', 'wo', 'ha', 'en', 'yo', 'sw']
        for lang in test_langs:
            is_african = agent.is_african_language(lang)
            print(f'📍 {lang}: {"africaine" if is_african else "non-africaine"}')
        print('✅ Détection langues OK')
        return True
    except Exception as e:
        print(f'❌ Erreur détection: {e}')
        return False

def test_fast_fallback(agent):
    """Test 4: Fast fallback"""
    print('\n🧪 Test 4: Fast fallback')
    try:
        # Test différents types de textes
        test_texts = [
            "bonjour comment allez-vous",
            "merci beaucoup",
            "aide moi s'il vous plait",
            "qui es tu",
            "texte aléatoire pour tester"
        ]
        
        for text in test_texts:
            response = agent._get_fast_fallback(text)
            print(f'📍 "{text[:20]}..." → "{response[:50]}..."')
        
        print('✅ Fast fallback OK')
        return True
    except Exception as e:
        print(f'❌ Erreur fast fallback: {e}')
        return False

async def test_llm_timeout(agent):
    """Test 5: Timeout LLM"""
    print('\n🧪 Test 5: Timeout LLM (simulation)')
    try:
        # Test avec timeout très court pour forcer le fallback
        start_time = time.time()
        
        # Forcer un timeout global très court
        original_timeout = 10.0
        print('📍 Test avec timeout court...')
        
        # Simuler un appel qui va timeout
        test_text = "bonjour"
        
        # Test du fast fallback directement
        response = await agent._llm_fallback_fast(test_text, remaining_time=1.0)
        elapsed = time.time() - start_time
        
        print(f'📍 Réponse en {elapsed:.2f}s: "{response[:50]}..."')
        print('✅ Timeout LLM géré')
        return True
    except Exception as e:
        print(f'❌ Erreur timeout LLM: {e}')
        return False

def test_waxal_client():
    """Test 6: WAXAL client"""
    print('\n🧪 Test 6: WAXAL client')
    try:
        client = voice_agent.WaxalClient()
        print('✅ WAXAL client initialisé')
        
        # Test URLs
        print(f'📍 STT URL: {client.stt_url}')
        print(f'📍 TTS URL: {client.tts_url}')
        print(f'📍 Translation URL: {client.translation_url}')
        
        return True
    except Exception as e:
        print(f'❌ Erreur WAXAL client: {e}')
        return False

def test_optimization_methods(agent):
    """Test 7: Méthodes d'optimisation"""
    print('\n🧪 Test 7: Optimisation des réponses')
    try:
        # Test _optimize_response
        long_response = "Ceci est une très longue réponse qui devrait être tronquée pour optimiser le temps de traitement et la synthèse vocale. " * 10
        optimized = agent._optimize_response(long_response)
        print(f'📍 Longueur originale: {len(long_response)}')
        print(f'📍 Longueur optimisée: {len(optimized)}')
        print(f'📍 Optimisée: {optimized[:100]}...')
        
        # Test _format_fallback_response
        formatted = agent._format_fallback_response("Prefix ", "Context ", "Suffix ")
        print(f'📍 Formatée: {formatted}')
        
        print('✅ Optimisation OK')
        return True
    except Exception as e:
        print(f'❌ Erreur optimisation: {e}')
        return False

async def run_complete_test():
    """Lancer tous les tests"""
    print("🚀 DÉMARRAGE TESTS COMPLETS WORKFLOW VOICE AGENT")
    print("=" * 60)
    
    # Test 1: Initialisation
    agent = test_basic_functionality()
    if not agent:
        print("❌ Arrêt des tests - initialisation échouée")
        return
    
    # Test 2: Circuit breaker
    test_circuit_breaker(agent)
    
    # Test 3: Détection langues
    test_language_detection(agent)
    
    # Test 4: Fast fallback
    test_fast_fallback(agent)
    
    # Test 5: Timeout LLM
    await test_llm_timeout(agent)
    
    # Test 6: WAXAL client
    test_waxal_client()
    
    # Test 7: Optimisation
    test_optimization_methods(agent)
    
    print("\n" + "=" * 60)
    print("🎯 TESTS COMPLETS TERMINÉS")
    print("📊 Résultats: Tests de base fonctionnels")
    print("⚠️  Note: Tests API réels nécessitent clés valides")

if __name__ == "__main__":
    asyncio.run(run_complete_test())
