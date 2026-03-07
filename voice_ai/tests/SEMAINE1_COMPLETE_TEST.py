#!/usr/bin/env python3
"""
TEST COMPLET SEMAINE 1 - AGENTS VOCAL AFRICASYS
==================================================
Tests finaux pour valider tous les accomplissements de la semaine
"""

import os
import sys
import time
import requests
import base64
import json
import threading
from dotenv import load_dotenv

load_dotenv()

# Configuration
WEB_URL = "http://localhost:5000"
PHONE_URL = "http://localhost:5001"

class Week1Validator:
    """Validateur complet de la semaine 1"""
    
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
    
    def test_web_agent_health(self):
        """Test 1: Agent web santé"""
        self.log("🌐 Test 1: Agent web santé", "TEST")
        
        try:
            response = self.session.get(f"{WEB_URL}/health")
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ Agent web OK: {data.get('message')}")
                return True
            else:
                self.log(f"❌ Erreur agent web: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Exception agent web: {e}", "ERROR")
            return False
    
    def test_phone_agent_health(self):
        """Test 2: Agent téléphonique santé"""
        self.log("📞 Test 2: Agent téléphonique santé", "TEST")
        
        try:
            response = self.session.get(f"{PHONE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ Agent téléphonique OK: {data.get('service')}")
                self.log(f"📞 Numéro: {data.get('phone_number')}")
                return True
            else:
                self.log(f"❌ Erreur agent téléphonique: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Exception agent téléphonique: {e}", "ERROR")
            return False
    
    def test_web_token_generation(self):
        """Test 3: Génération token web"""
        self.log("🎫 Test 3: Génération token web", "TEST")
        
        try:
            payload = {
                "roomName": "test_semaine1",
                "userIdentity": "test_semaine1_user",
                "userName": "Test Semaine 1"
            }
            
            response = self.session.post(f"{WEB_URL}/token", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('token')
                room = data.get('room')
                user_info = data.get('user_info', {})
                
                if token and room:
                    self.log(f"✅ Token web généré pour room: {room}")
                    self.log(f"👤 Utilisateurs: {user_info.get('user_count', 0)}")
                    return True
                else:
                    self.log("❌ Token ou room manquant", "ERROR")
                    return False
            else:
                self.log(f"❌ Erreur token web: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Exception token web: {e}", "ERROR")
            return False
    
    def test_phone_call_creation(self):
        """Test 4: Création appel téléphonique"""
        self.log("📞 Test 4: Création appel téléphonique", "TEST")
        
        try:
            payload = {"caller_number": "+33612345678"}
            response = self.session.post(f"{PHONE_URL}/create_call", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log(f"✅ Appel téléphonique créé: {data.get('room_name')}")
                    self.log(f"👤 Appelant: {data.get('caller_number')}")
                    return True
                else:
                    self.log(f"❌ Erreur création appel: {data.get('error')}", "ERROR")
                    return False
            else:
                self.log(f"❌ Erreur création appel: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Exception création appel: {e}", "ERROR")
            return False
    
    def test_web_multi_users(self):
        """Test 5: Multi-utilisateurs web"""
        self.log("👥 Test 5: Multi-utilisateurs web", "TEST")
        
        try:
            # Créer plusieurs utilisateurs
            users = []
            for i in range(3):
                payload = {
                    "roomName": "multi_test_semaine1",
                    "userIdentity": f"user_multi_{i}",
                    "userName": f"User Multi {i}"
                }
                
                response = self.session.post(f"{WEB_URL}/token", json=payload)
                if response.status_code == 200:
                    data = response.json()
                    users.append(data['user_info'])
                else:
                    self.log(f"❌ Erreur user {i}: {response.status_code}", "ERROR")
                    return False
            
            # Vérifier la liste des utilisateurs
            response = self.session.get(f"{WEB_URL}/room/multi_test_semaine1/users")
            if response.status_code == 200:
                data = response.json()
                user_count = data.get('user_count', 0)
                self.log(f"✅ Multi-utilisateurs web: {user_count} utilisateurs")
                return True
            else:
                self.log(f"❌ Erreur liste users: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Exception multi-users web: {e}", "ERROR")
            return False
    
    def test_phone_multi_calls(self):
        """Test 6: Multi-appels téléphoniques"""
        self.log("📞 Test 6: Multi-appels téléphoniques", "TEST")
        
        try:
            # Créer plusieurs appels
            calls = []
            for i in range(3):
                payload = {"caller_number": f"+3361234567{i}"}
                response = self.session.post(f"{PHONE_URL}/create_call", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        calls.append(data)
                    else:
                        self.log(f"❌ Erreur appel {i}: {data.get('error')}", "ERROR")
                        return False
                else:
                    self.log(f"❌ Erreur appel {i}: {response.status_code}", "ERROR")
                    return False
            
            # Vérifier les appels actifs
            response = self.session.get(f"{PHONE_URL}/stats")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    stats = data.get('stats', {})
                    total_calls = stats.get('total_calls', 0)
                    self.log(f"✅ Multi-appels téléphoniques: {total_calls} appels totaux")
                    return True
            else:
                self.log(f"❌ Erreur stats appels: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Exception multi-appels: {e}", "ERROR")
            return False
    
    def test_web_stats(self):
        """Test 7: Statistiques web"""
        self.log("📊 Test 7: Statistiques web", "TEST")
        
        try:
            response = self.session.get(f"{WEB_URL}/stats")
            if response.status_code == 200:
                data = response.json()
                total_rooms = data.get('total_rooms', 0)
                total_users = data.get('total_users', 0)
                
                self.log(f"✅ Stats web: {total_rooms} rooms, {total_users} utilisateurs")
                
                # Afficher les rooms actives
                rooms = data.get('rooms', {})
                for room_name, room_info in rooms.items():
                    user_count = room_info.get('user_count', 0)
                    self.log(f"   📍 {room_name}: {user_count} users")
                
                return True
            else:
                self.log(f"❌ Erreur stats web: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Exception stats web: {e}", "ERROR")
            return False
    
    def test_phone_stats(self):
        """Test 8: Statistiques téléphoniques"""
        self.log("📊 Test 8: Statistiques téléphoniques", "TEST")
        
        try:
            response = self.session.get(f"{PHONE_URL}/stats")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    stats = data.get('stats', {})
                    total_calls = stats.get('total_calls', 0)
                    active_calls = stats.get('active_calls', 0)
                    
                    self.log(f"✅ Stats téléphoniques: {total_calls} appels totaux")
                    self.log(f"   📞 Actifs: {active_calls}")
                    self.log(f"   📞 Terminés: {stats.get('ended_calls', 0)}")
                    return True
                else:
                    self.log(f"❌ Erreur stats téléphone: {data.get('error')}", "ERROR")
                    return False
            else:
                self.log(f"❌ Erreur stats téléphone: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Exception stats téléphone: {e}", "ERROR")
            return False
    
    def test_cache_performance(self):
        """Test 9: Performance cache"""
        self.log("⚡ Test 9: Performance cache", "TEST")
        
        try:
            response = self.session.get(f"{WEB_URL}/cache/stats")
            if response.status_code == 200:
                data = response.json()
                cache_size = data.get('cache_size', 0)
                max_cache_size = data.get('max_cache_size', 0)
                
                self.log(f"✅ Cache: {cache_size}/{max_cache_size} entrées")
                
                if data.get('cache_keys'):
                    self.log(f"   📝 Clés cache: {len(data['cache_keys'])}")
                
                return True
            else:
                self.log(f"❌ Erreur cache stats: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Exception cache: {e}", "ERROR")
            return False
    
    def test_multilingual_features(self):
        """Test 10: Fonctionnalités multilingues"""
        self.log("🌍 Test 10: Fonctionnalités multilingues", "TEST")
        
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
            
            correct_detections = 0
            for text, expected_lang in test_cases:
                detected = agent.detect_language(text)
                if detected == expected_lang:
                    correct_detections += 1
                    self.log(f"   ✅ '{text}' -> {detected}")
                else:
                    self.log(f"   ❌ '{text}' -> {detected} (attendu: {expected_lang})", "ERROR")
            
            accuracy = (correct_detections / len(test_cases)) * 100
            self.log(f"✅ Détection multilingue: {accuracy:.0f}% précision")
            
            return accuracy >= 75  # Accepter 75% comme seuil
            
        except Exception as e:
            self.log(f"❌ Exception multilingue: {e}", "ERROR")
            return False
    
    def run_week1_validation(self):
        """Exécute la validation complète de la semaine 1"""
        self.log("="*60, "HEADER")
        self.log("🚀 VALIDATION FINALE SEMAINE 1 - AGENTS VOCAL AFRICASYS", "HEADER")
        self.log("="*60, "HEADER")
        
        tests = [
            ("Agent web santé", self.test_web_agent_health),
            ("Agent téléphonique santé", self.test_phone_agent_health),
            ("Génération token web", self.test_web_token_generation),
            ("Création appel téléphonique", self.test_phone_call_creation),
            ("Multi-utilisateurs web", self.test_web_multi_users),
            ("Multi-appels téléphoniques", self.test_phone_multi_calls),
            ("Statistiques web", self.test_web_stats),
            ("Statistiques téléphoniques", self.test_phone_stats),
            ("Performance cache", self.test_cache_performance),
            ("Fonctionnalités multilingues", self.test_multilingual_features)
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
        self.log("📋 RÉSUMÉ SEMAINE 1", "HEADER")
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
        
        # Analyse par POC
        web_tests = [r for r in results if "web" in r[0].lower() or "token" in r[0].lower() or "cache" in r[0].lower()]
        phone_tests = [r for r in results if "téléphonique" in r[0].lower() or "appel" in r[0].lower() or "multilingue" in r[0].lower()]
        
        web_success = sum(1 for r in web_tests if r[1]) / len(web_tests) * 100 if web_tests else 0
        phone_success = sum(1 for r in phone_tests if r[1]) / len(phone_tests) * 100 if phone_tests else 0
        
        self.log(f"\n🌐 POC 1 - Agent Web: {web_success:.0f}% ({sum(1 for r in web_tests if r[1])}/{len(web_tests)})")
        self.log(f"📞 POC 2 - Agent Téléphonique: {phone_success:.0f}% ({sum(1 for r in phone_tests if r[1])}/{len(phone_tests)})")
        
        if success_rate >= 90:
            self.log("🎉 SEMAINE 1 VALIDÉE AVEC SUCCÈS EXCEPTIONNEL !", "SUCCESS")
            self.log("🚀 Les deux POCs sont fonctionnels et prêts pour la production", "SUCCESS")
        elif success_rate >= 80:
            self.log("⚠️ SEMAINE 1 MAJORITAIREMENT RÉUSSIE", "WARNING")
            self.log("🔧 Quelques ajustements nécessaires pour la perfection", "WARNING")
        else:
            self.log("🚨 SEMAINE 1 NÉCESSITE DES CORRECTIONS", "ERROR")
            self.log("🔧 Révision importante avant de continuer", "ERROR")
        
        self.log("="*60, "HEADER")
        
        return success_rate >= 80

if __name__ == "__main__":
    print("🧪 VALIDATION FINALE SEMAINE 1 - AGENTS VOCAL AFRICASYS")
    print("="*60)
    
    validator = Week1Validator()
    success = validator.run_week1_validation()
    
    sys.exit(0 if success else 1)
