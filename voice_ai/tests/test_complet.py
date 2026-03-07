#!/usr/bin/env python3
"""
TEST COMPLET - AGENT VOCAL AFRICASYS
=====================================
Tests automatisés pour valider toutes les fonctionnalités
"""

import os
import sys
import time
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# Configuration
BASE_URL = "http://localhost:5000"
LIVEKIT_URL = os.getenv("LIVEKIT_URL")

class TestAgentVocal:
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
    
    def test_api_health(self):
        """Test 1: Vérifier que le serveur est en ligne"""
        self.log("🏥 Test 1: Vérification santé du serveur", "TEST")
        
        try:
            response = self.session.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ Serveur OK: {data.get('message')}", "SUCCESS")
                return True
            else:
                self.log(f"❌ Erreur serveur: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Exception serveur: {e}", "ERROR")
            return False
    
    def test_token_generation(self):
        """Test 2: Génération de token LiveKit"""
        self.log("🎫 Test 2: Génération token LiveKit", "TEST")
        
        try:
            payload = {
                "roomName": "test_room_complete",
                "userIdentity": "test_user_complete",
                "userName": "Test Complet"
            }
            
            response = self.session.post(f"{BASE_URL}/token", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('token')
                room = data.get('room')
                user_info = data.get('user_info', {})
                
                if token and room:
                    self.log(f"✅ Token généré pour room: {room}", "SUCCESS")
                    self.log(f"👤 Utilisateur: {user_info.get('user_name')} ({user_info.get('user_count')} users)", "INFO")
                    return True
                else:
                    self.log("❌ Token ou room manquant", "ERROR")
                    return False
            else:
                self.log(f"❌ Erreur token: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Exception token: {e}", "ERROR")
            return False
    
    def test_room_management(self):
        """Test 3: Gestion des rooms multi-utilisateurs"""
        self.log("🏠 Test 3: Gestion rooms multi-utilisateurs", "TEST")
        
        try:
            # Créer plusieurs utilisateurs dans la même room
            users = []
            for i in range(3):
                payload = {
                    "roomName": "multi_test_room",
                    "userIdentity": f"user_multi_{i}",
                    "userName": f"User Multi {i}"
                }
                
                response = self.session.post(f"{BASE_URL}/token", json=payload)
                if response.status_code == 200:
                    data = response.json()
                    users.append(data['user_info'])
                    self.log(f"✅ User {i} ajouté: {data['user_info']['user_count']} users total", "SUCCESS")
                else:
                    self.log(f"❌ Erreur user {i}: {response.status_code}", "ERROR")
                    return False
            
            # Vérifier la liste des utilisateurs
            response = self.session.get(f"{BASE_URL}/room/multi_test_room/users")
            if response.status_code == 200:
                data = response.json()
                user_count = data.get('user_count', 0)
                self.log(f"✅ Room multi_test_room: {user_count} utilisateurs", "SUCCESS")
                return True
            else:
                self.log(f"❌ Erreur liste users: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Exception room management: {e}", "ERROR")
            return False
    
    def test_system_stats(self):
        """Test 4: Statistiques système"""
        self.log("📊 Test 4: Statistiques système", "TEST")
        
        try:
            response = self.session.get(f"{BASE_URL}/stats")
            if response.status_code == 200:
                data = response.json()
                total_rooms = data.get('total_rooms', 0)
                total_users = data.get('total_users', 0)
                
                self.log(f"✅ Stats: {total_rooms} rooms, {total_users} utilisateurs", "SUCCESS")
                
                # Afficher les rooms actives
                rooms = data.get('rooms', {})
                for room_name, room_info in rooms.items():
                    user_count = room_info.get('user_count', 0)
                    users = room_info.get('users', [])
                    self.log(f"   📍 {room_name}: {user_count} users - {users}", "INFO")
                
                return True
            else:
                self.log(f"❌ Erreur stats: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Exception stats: {e}", "ERROR")
            return False
    
    def test_cache_stats(self):
        """Test 5: Statistiques du cache"""
        self.log("🗄️ Test 5: Statistiques du cache", "TEST")
        
        try:
            response = self.session.get(f"{BASE_URL}/cache/stats")
            if response.status_code == 200:
                data = response.json()
                cache_size = data.get('cache_size', 0)
                max_cache_size = data.get('max_cache_size', 0)
                
                self.log(f"✅ Cache: {cache_size}/{max_cache_size} entrées", "SUCCESS")
                
                if data.get('cache_keys'):
                    self.log(f"   📝 Clés cache: {data['cache_keys'][:3]}...", "INFO")
                
                return True
            else:
                self.log(f"❌ Erreur cache stats: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Exception cache stats: {e}", "ERROR")
            return False
    
    def run_all_tests(self):
        """Exécute tous les tests"""
        self.log("="*60, "HEADER")
        self.log("🚀 DÉMARRAGE DES TESTS COMPLETS - AGENT VOCAL AFRICASYS", "HEADER")
        self.log("="*60, "HEADER")
        
        tests = [
            ("Santé du serveur", self.test_api_health),
            ("Génération token", self.test_token_generation),
            ("Gestion multi-utilisateurs", self.test_room_management),
            ("Statistiques système", self.test_system_stats),
            ("Statistiques cache", self.test_cache_stats)
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
        self.log("📋 RÉSUMÉ DES TESTS", "HEADER")
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
            self.log("🎉 TOUS LES TESTS RÉUSSIS ! L'agent vocal est prêt.", "SUCCESS")
        elif success_rate >= 80:
            self.log("⚠️ Tests majoritairement réussis. Quelques ajustements nécessaires.", "WARNING")
        else:
            self.log("🚨 Tests échoués. Révision nécessaire avant déploiement.", "ERROR")
        
        self.log("="*60, "HEADER")
        
        return success_rate == 100

if __name__ == "__main__":
    print("🧪 TEST COMPLET - AGENT VOCAL AFRICASYS")
    print("="*60)
    
    tester = TestAgentVocal()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)
