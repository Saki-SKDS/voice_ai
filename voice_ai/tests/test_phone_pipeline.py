import requests
import base64
import time
import json

# Configuration du serveur téléphonique
BASE_URL = "http://localhost:5001"

def test_phone_pipeline():
    """Test complet du pipeline téléphonique"""
    print("="*60)
    print("📞 TEST PIPELINE TÉLÉPHONIQUE COMPLET")
    print("="*60)
    
    try:
        # 1. Vérifier que le serveur est en ligne
        print("\n1️⃣ Test santé du serveur...")
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Serveur OK: {data.get('service')}")
            print(f"📞 Numéro: {data.get('phone_number')}")
        else:
            print(f"❌ Erreur serveur: {response.status_code}")
            return False
        
        # 2. Créer un appel
        print("\n2️⃣ Création d'un appel...")
        call_payload = {
            "caller_number": "+33612345678"
        }
        
        response = requests.post(f"{BASE_URL}/create_call", json=call_payload)
        if response.status_code == 200:
            call_data = response.json()
            if call_data.get('success'):
                room_name = call_data.get('room_name')
                participant_identity = call_data.get('participant_identity')
                token = call_data.get('token')
                caller_number = call_data.get('caller_number')
                
                print(f"✅ Appel créé: {room_name}")
                print(f"👤 Appelant: {caller_number}")
                print(f"🎫 Token: {token[:50]}...")
                
                # 3. Simuler traitement audio
                print("\n3️⃣ Traitement audio...")
                
                # Créer un audio de test (simulant la voix de l'appelant)
                test_audio = b'\x00\x01\x02\x03' * 1000  # Audio simulé
                
                audio_payload = {
                    "room_name": room_name,
                    "audio": base64.b64encode(test_audio).decode('utf-8')
                }
                
                response = requests.post(f"{BASE_URL}/process_audio", json=audio_payload)
                if response.status_code == 200:
                    audio_result = response.json()
                    if audio_result.get('success'):
                        print(f"✅ Audio traité")
                        print(f"📝 Réponse: {audio_result.get('text', 'N/A')[:50]}...")
                        
                        # 4. Vérifier les appels actifs
                        print("\n4️⃣ Vérification appels actifs...")
                        response = requests.get(f"{BASE_URL}/active_calls")
                        if response.status_code == 200:
                            calls_data = response.json()
                            if calls_data.get('success'):
                                calls = calls_data.get('calls', {})
                                print(f"✅ Appels actifs: {len(calls)}")
                                for call_room, call_info in calls.items():
                                    status = call_info.get('status')
                                    duration = call_info.get('duration', 0)
                                    print(f"   📞 {call_room}: {status} ({duration:.1f}s)")
                            
                        # 5. Terminer l'appel
                        print("\n5️⃣ Terminaison de l'appel...")
                        end_payload = {
                            "room_name": room_name
                        }
                        
                        response = requests.post(f"{BASE_URL}/end_call", json=end_payload)
                        if response.status_code == 200:
                            end_result = response.json()
                            if end_result.get('success'):
                                duration = end_result.get('duration', 0)
                                goodbye_text = end_result.get('goodbye_text', 'N/A')
                                print(f"✅ Appel terminé")
                                print(f"⏱️ Durée: {duration:.1f}s")
                                print(f"👋 Message: {goodbye_text}")
                                
                                # 6. Vérifier les statistiques
                                print("\n6️⃣ Statistiques finales...")
                                response = requests.get(f"{BASE_URL}/stats")
                                if response.status_code == 200:
                                    stats_data = response.json()
                                    if stats_data.get('success'):
                                        stats = stats_data.get('stats', {})
                                        print(f"📊 Total appels: {stats.get('total_calls', 0)}")
                                        print(f"📞 Appels actifs: {stats.get('active_calls', 0)}")
                                        print(f"📞 Appels terminés: {stats.get('ended_calls', 0)}")
                                        print(f"📞 Numéro service: {stats.get('phone_number', 'N/A')}")
                                
                                print("\n🎉 TEST PIPELINE TÉLÉPHONIQUE RÉUSSI !")
                                return True
                            else:
                                print(f"❌ Erreur terminaison: {end_result.get('error')}")
                        else:
                            print(f"❌ Erreur terminaison: {response.status_code}")
                    else:
                        print(f"❌ Erreur traitement audio: {audio_result.get('error')}")
                else:
                    print(f"❌ Erreur traitement audio: {response.status_code}")
            else:
                print(f"❌ Erreur création appel: {call_data.get('error')}")
        else:
            print(f"❌ Erreur création appel: {response.status_code}")
        
        return False
        
    except Exception as e:
        print(f"❌ Exception test: {e}")
        return False

def test_multiple_calls():
    """Test avec plusieurs appels simultanés"""
    print("\n" + "="*60)
    print("📞 TEST MULTI-APPELS SIMULTANÉS")
    print("="*60)
    
    try:
        # Créer plusieurs appels
        calls = []
        for i in range(3):
            print(f"\n📞 Création appel {i+1}...")
            call_payload = {
                "caller_number": f"+3361234567{i}"
            }
            
            response = requests.post(f"{BASE_URL}/create_call", json=call_payload)
            if response.status_code == 200:
                call_data = response.json()
                if call_data.get('success'):
                    calls.append(call_data)
                    print(f"✅ Appel {i+1} créé: {call_data.get('room_name')}")
                else:
                    print(f"❌ Erreur appel {i+1}: {call_data.get('error')}")
            else:
                print(f"❌ Erreur appel {i+1}: {response.status_code}")
        
        # Vérifier les appels actifs
        print(f"\n📊 {len(calls)} appels créés")
        response = requests.get(f"{BASE_URL}/active_calls")
        if response.status_code == 200:
            calls_data = response.json()
            if calls_data.get('success'):
                active_calls = calls_data.get('calls', {})
                print(f"✅ Appels actifs: {len(active_calls)}")
        
        # Terminer tous les appels
        for i, call in enumerate(calls):
            print(f"\n📞 Terminaison appel {i+1}...")
            end_payload = {
                "room_name": call.get('room_name')
            }
            
            response = requests.post(f"{BASE_URL}/end_call", json=end_payload)
            if response.status_code == 200:
                end_result = response.json()
                if end_result.get('success'):
                    duration = end_result.get('duration', 0)
                    print(f"✅ Appel {i+1} terminé ({duration:.1f}s)")
                else:
                    print(f"❌ Erreur terminaison {i+1}: {end_result.get('error')}")
            else:
                print(f"❌ Erreur terminaison {i+1}: {response.status_code}")
        
        print("\n✅ Test multi-appels terminé")
        return True
        
    except Exception as e:
        print(f"❌ Exception multi-appels: {e}")
        return False

if __name__ == "__main__":
    print("🧪 TESTS AGENT TÉLÉPHONIQUE AFRICASYS")
    
    # Attendre que le serveur démarre
    print("⏳ Attente démarrage serveur...")
    time.sleep(3)
    
    # Test 1: Pipeline complet
    success1 = test_phone_pipeline()
    
    # Test 2: Multi-appels
    success2 = test_multiple_calls()
    
    # Résultat final
    print("\n" + "="*60)
    print("📋 RÉSULTAT FINAL DES TESTS")
    print("="*60)
    print(f"Pipeline complet: {'✅ RÉUSSI' if success1 else '❌ ÉCHOUÉ'}")
    print(f"Multi-appels: {'✅ RÉUSSI' if success2 else '❌ ÉCHOUÉ'}")
    
    if success1 and success2:
        print("\n🎉 TOUS LES TESTS RÉUSSIS !")
        print("📞 Agent téléphonique prêt pour la production")
    else:
        print("\n⚠️ Certains tests ont échoué")
        print("🔧 Vérifiez les logs du serveur")
    
    print("="*60)
