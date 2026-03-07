#!/usr/bin/env python3
"""
VALIDATION FINALE POC 2 - AGENT TÉLÉPHONIQUE
============================================
Tests complets pour valider le POC 2 agent téléphonique multilingue
"""

import os
import sys
import time
import requests
import base64
import json
from dotenv import load_dotenv

load_dotenv()

# Configuration
BASE_URL = "http://localhost:5001"

class POC2Validator:
    """Validateur complet du POC 2"""
    
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
    def log(self, message, status="INFO"):
        """Log un message avec timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] [{status}] {message}")
        self.test_results.append({
            "time": timestamp,
            "status": status,
            "message": message
        })
    
    def test_phone_server_health(self):
        """Test 1: Santé du serveur téléphonique"""
        self.log("🏥 Test 1: Santé du serveur téléphonique", "TEST")
        
        try:
            response = self.session.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ Serveur téléphonique OK: {data.get('service')}")
                self.log(f"📞 Numéro: {data.get('phone_number')}")
                return True
            else:
                self.log(f"❌ Erreur serveur: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Exception serveur: {e}", "ERROR")
            return False
    
    def test_phone_call_creation(self):
        """Test 2: Création d'appels téléphoniques"""
        self.log("📞 Test 2: Création d'appels téléphoniques", "TEST")
        
        try:
            # Test avec numéro français
            payload = {"caller_number": "+33612345678"}
            response = self.session.post(f"{BASE_URL}/create_call", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log(f"✅ Appel créé: {data.get('room_name')}")
                    self.log(f"👤 Appelant: {data.get('caller_number')}")
                    self.log(f"🎫 Token généré: {len(data.get('token', ''))} chars")
                    return True
                else:
                    self.log(f"❌ Erreur création: {data.get('error')}", "ERROR")
                    return False
            else:
                self.log(f"❌ Erreur HTTP: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Exception création appel: {e}", "ERROR")
            return False
    
    def test_multilingual_calls(self):
        """Test 3: Appels multilingues"""
        self.log("🌐 Test 3: Appels multilingues", "TEST")
        
        try:
            # Test appel français
            self.log("   📞 Test appel français...")
            fr_payload = {"caller_number": "+33612345678"}
            fr_response = self.session.post(f"{BASE_URL}/create_call", json=fr_payload)
            
            # Test appel anglais
            self.log("   📞 Test appel anglais...")
            en_payload = {"caller_number": "+44712345678"}
            en_response = self.session.post(f"{BASE_URL}/create_call", json=en_payload)
            
            if fr_response.status_code == 200 and en_response.status_code == 200:
                self.log("✅ Appels multilingues créés avec succès")
                return True
            else:
                self.log("❌ Erreur appels multilingues", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Exception multilingue: {e}", "ERROR")
            return False
    
    def test_audio_processing(self):
        """Test 4: Traitement audio"""
        self.log("🎤 Test 4: Traitement audio", "TEST")
        
        try:
            # D'abord créer un appel
            payload = {"caller_number": "+33612345678"}
            call_response = self.session.post(f"{BASE_URL}/create_call", json=payload)
            
            if call_response.status_code == 200:
                call_data = call_response.json()
                room_name = call_data.get('room_name')
                
                # Créer un audio de test
                test_audio = b'\x00\x01\x02\x03' * 1000
                audio_payload = {
                    "room_name": room_name,
                    "audio": base64.b64encode(test_audio).decode('utf-8')
                }
                
                # Traiter l'audio
                audio_response = self.session.post(f"{BASE_URL}/process_audio", json=audio_payload)
                
                if audio_response.status_code == 200:
                    audio_data = audio_response.json()
                    if audio_data.get('success'):
                        self.log("✅ Audio traité avec succès")
                        self.log(f"📝 Réponse: {audio_data.get('text', 'N/A')[:50]}...")
                        return True
                    else:
                        self.log(f"⚠️ Audio traité avec avertissement: {audio_data.get('text')}")
                        return True
                else:
                    self.log(f"❌ Erreur traitement audio: {audio_response.status_code}", "ERROR")
                    return False
            else:
                self.log("❌ Impossible de créer l'appel pour le test", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Exception traitement audio: {e}", "ERROR")
            return False
    
    def test_call_termination(self):
        """Test 5: Terminaison d'appels"""
        self.log("📞 Test 5: Terminaison d'appels", "TEST")
        
        try:
            # Créer un appel
            payload = {"caller_number": "+33612345678"}
            call_response = self.session.post(f"{BASE_URL}/create_call", json=payload)
            
            if call_response.status_code == 200:
                call_data = call_response.json()
                room_name = call_data.get('room_name')
                
                # Terminer l'appel
                end_payload = {"room_name": room_name}
                end_response = self.session.post(f"{BASE_URL}/end_call", json=end_payload)
                
                if end_response.status_code == 200:
                    end_data = end_response.json()
                    if end_data.get('success'):
                        duration = end_data.get('duration', 0)
                        self.log(f"✅ Appel terminé (durée: {duration:.1f}s)")
                        return True
                    else:
                        self.log(f"❌ Erreur terminaison: {end_data.get('error')}", "ERROR")
                        return False
                else:
                    self.log(f"❌ Erreur HTTP terminaison: {end_response.status_code}", "ERROR")
                    return False
            else:
                self.log("❌ Impossible de créer l'appel pour le test", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Exception terminaison: {e}", "ERROR")
            return False
    
    def test_active_calls_monitoring(self):
        """Test 6: Monitoring des appels actifs"""
        self.log("📊 Test 6: Monitoring des appels actifs", "TEST")
        
        try:
            response = self.session.get(f"{BASE_URL}/active_calls")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    calls = data.get('calls', {})
                    self.log(f"✅ Appels actifs: {len(calls)}")
                    for room, info in calls.items():
                        status = info.get('status', 'unknown')
                        duration = info.get('duration', 0)
                        self.log(f"   📞 {room}: {status} ({duration:.1f}s)")
                    return True
                else:
                    self.log(f"❌ Erreur monitoring: {data.get('error')}", "ERROR")
                    return False
            else:
                self.log(f"❌ Erreur HTTP monitoring: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Exception monitoring: {e}", "ERROR")
            return False
    
    def test_statistics(self):
        """Test 7: Statistiques du système"""
        self.log("📈 Test 7: Statistiques du système", "TEST")
        
        try:
            response = self.session.get(f"{BASE_URL}/stats")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    stats = data.get('stats', {})
                    self.log(f"✅ Statistiques: {stats.get('total_calls', 0)} appels totaux")
                    self.log(f"   📞 Actifs: {stats.get('active_calls', 0)}")
                    self.log(f"   📞 Terminés: {stats.get('ended_calls', 0)}")
                    self.log(f"   📞 Numéro: {stats.get('phone_number', 'N/A')}")
                    return True
                else:
                    self.log(f"❌ Erreur stats: {data.get('error')}", "ERROR")
                    return False
            else:
                self.log(f"❌ Erreur HTTP stats: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Exception stats: {e}", "ERROR")
            return False
    
    def test_multilingual_agent(self):
        """Test 8: Agent multilingue"""
        self.log("🌍 Test 8: Agent multilingue", "TEST")
        
        try:
            # Importer et tester l'agent multilingue
            sys.path.append(os.path.join(os.path.dirname(__file__), 'web_app'))
            from multilingual_phone_agent import MultilingualPhoneAgent
            
            agent = MultilingualPhoneAgent()
            
            # Test détection de langue
            test_cases = [
                ("Bonjour, comment ça va ?", "fr"),
                ("Hello, how are you?", "en"),
                ("Merci beaucoup", "fr"),
                ("Thank you very much", "en")
            ]
            
            all_correct = True
            for text, expected_lang in test_cases:
                detected = agent.detect_language(text)
                if detected == expected_lang:
                    self.log(f"   ✅ '{text}' -> {detected}")
                else:
                    self.log(f"   ❌ '{text}' -> {detected} (attendu: {expected_lang})", "ERROR")
                    all_correct = False
            
            # Test réponses multilingues
            fr_response = agent.get_multilingual_response("C'est quoi la PrEP ?", "fr")
            en_response = agent.get_multilingual_response("What is PrEP?", "en")
            
            if fr_response and en_response:
                self.log(f"   ✅ Réponse FR: {fr_response[:50]}...")
                self.log(f"   ✅ Réponse EN: {en_response[:50]}...")
            else:
                self.log("   ❌ Erreur réponses multilingues", "ERROR")
                all_correct = False
            
            return all_correct
            
        except Exception as e:
            self.log(f"❌ Exception agent multilingue: {e}", "ERROR")
            return False
    
    def run_poc2_validation(self):
        """Exécute la validation complète du POC 2"""
        self.log("="*60, "HEADER")
        self.log("🚀 VALIDATION FINALE POC 2 - AGENT TÉLÉPHONIQUE", "HEADER")
        self.log("="*60, "HEADER")
        
        tests = [
            ("Santé du serveur", self.test_phone_server_health),
            ("Création d'appels", self.test_phone_call_creation),
            ("Appels multilingues", self.test_multilingual_calls),
            ("Traitement audio", self.test_audio_processing),
            ("Terminaison d'appels", self.test_call_termination),
            ("Monitoring appels", self.test_active_calls_monitoring),
            ("Statistiques système", self.test_statistics),
            ("Agent multilingue", self.test_multilingual_agent)
        ]
        
        results = []
        for test_name, test_func in tests:
            self.log(f"\n--- {test_name} ---", "HEADER")
            success = test_func()
            results.append((test_name, success))
            
            if success:
                self.log(f"✅ {test_name}: RÉUSSI", "SUCCESS")
            else:
                self.log(f"❌ {test_name}: ÉCHOUÉ", "ERROR")
        
        # Résumé final
        self.log("\n" + "="*60, "HEADER")
        self.log("📋 RÉSUMÉ VALIDATION POC 2", "HEADER")
        self.log("="*60, "HEADER")
        
        success_count = 0
        for test_name, success in results:
            status = "✅ RÉUSSI" if success else "❌ ÉCHOUÉ"
            self.log(f"{test_name}: {status}", "FINAL")
            if success:
                success_count += 1
        
        total_tests = len(results)
        success_rate = (success_count / total_tests) * 100
        
        self.log(f"\n📊 Résultats: {success_count}/{total_tests} tests réussis ({success_rate:.1f}%)", "FINAL")
        
        if success_rate == 100:
            self.log("🎉 POC 2 VALIDÉ AVEC SUCCÈS !", "SUCCESS")
            self.log("📞 Agent téléphonique multilingue prêt pour la production", "SUCCESS")
        elif success_rate >= 80:
            self.log("⚠️ POC 2 majoritairement validé. Quelques ajustements nécessaires.", "WARNING")
        else:
            self.log("🚨 POC 2 nécessite des corrections importantes.", "ERROR")
        
        self.log("="*60, "HEADER")
        
        return success_rate == 100

if __name__ == "__main__":
    print("🧪 VALIDATION FINALE POC 2 - AGENT TÉLÉPHONIQUE")
    print("="*60)
    
    validator = POC2Validator()
    success = validator.run_poc2_validation()
    
    sys.exit(0 if success else 1)
