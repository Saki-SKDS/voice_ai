import os
import asyncio
import logging
from dotenv import load_dotenv
from livekit import api
from livekit.protocol.sip import (
    SipIngressInfo,
    SipTrunkInfo,
    CreateSipTrunkRequest,
    CreateSipTrunkResponse,
    DeleteSipTrunkRequest,
    DeleteSipTrunkResponse,
    ListSipTrunkRequest,
    ListSipTrunkResponse,
    SendSipMessageRequest,
    SendSipMessageResponse,
)
from voice_processor import VoiceProcessor

load_dotenv()

# Configuration
LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")

# Configuration SIP
SIP_SERVER = os.getenv("SIP_SERVER", "sip.example.com")
SIP_USERNAME = os.getenv("SIP_USERNAME", "phone_agent")
SIP_PASSWORD = os.getenv("SIP_PASSWORD", "password123")
PHONE_NUMBER = os.getenv("PHONE_NUMBER", "+33612345678")

class PhoneAgent:
    """Agent vocal téléphonique avec LiveKit SIP Bridge"""
    
    def __init__(self):
        self.livekit_api = api.LiveKitAPI(LIVEKIT_API_KEY, LIVEKIT_API_SECRET, LIVEKIT_URL)
        self.voice_processor = VoiceProcessor()
        self.active_calls = {}  # room_name -> call_info
        self.sip_trunk_id = None
        
        # Configuration logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    async def setup_sip_trunk(self):
        """Configure le SIP trunk pour recevoir les appels"""
        try:
            self.logger.info("🔧 Configuration du SIP trunk...")
            
            # Créer le SIP trunk
            request = CreateSipTrunkRequest(
                sip_trunk_name="phone_agent_trunk",
                sip_address=SIP_SERVER,
                sip_username=SIP_USERNAME,
                sip_password=SIP_PASSWORD,
                numbers=[PHONE_NUMBER]
            )
            
            response = self.livekit_api.sip.create_sip_trunk(request)
            
            if response.sip_trunk_info:
                self.sip_trunk_id = response.sip_trunk_info.sip_trunk_id
                self.logger.info(f"✅ SIP trunk créé: {self.sip_trunk_id}")
                self.logger.info(f"📞 Numéro configuré: {PHONE_NUMBER}")
                return True
            else:
                self.logger.error("❌ Erreur création SIP trunk")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Exception setup SIP trunk: {e}")
            return False
    
    async def handle_incoming_call(self, room_name, participant_identity):
        """Gère un appel entrant"""
        try:
            self.logger.info(f"📞 Appel entrant dans room: {room_name}")
            self.logger.info(f"👤 Participant: {participant_identity}")
            
            # Marquer l'appel comme actif
            self.active_calls[room_name] = {
                'participant_identity': participant_identity,
                'start_time': asyncio.get_event_loop().time(),
                'room_name': room_name
            }
            
            # Envoyer un message d'accueil
            welcome_text = "Bonjour, je suis l'agent vocal AfricaSys. Comment puis-je vous aider ?"
            
            # Générer l'accueil vocal
            audio_response = await self.voice_processor.text_to_speech_optimized(welcome_text)
            
            if audio_response:
                # Envoyer l'accueil via LiveKit
                await self.send_audio_to_room(room_name, audio_response)
                self.logger.info("🎤 Accueil vocal envoyé")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur gestion appel entrant: {e}")
            return False
    
    async def process_phone_audio(self, room_name, audio_data):
        """Traite l'audio téléphonique"""
        try:
            self.logger.info(f"🎤 Traitement audio téléphonique: {room_name}")
            
            # Utiliser le pipeline vocal optimisé
            response_audio, response_text = await self.voice_processor.process_audio_optimized(audio_data)
            
            if response_audio:
                # Envoyer la réponse vocale
                await self.send_audio_to_room(room_name, response_audio)
                self.logger.info(f"🗣️ Réponse envoyée: {response_text[:50]}...")
                return True
            else:
                self.logger.warning("⚠️ Pas de réponse audio générée")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erreur traitement audio téléphone: {e}")
            return False
    
    async def send_audio_to_room(self, room_name, audio_data):
        """Envoie l'audio à la room LiveKit"""
        try:
            # Pour l'instant, nous allons logger l'envoi
            # En production, il faudrait utiliser le data channel LiveKit
            self.logger.info(f"📡 Envoi audio à room: {room_name} ({len(audio_data)} bytes)")
            
            # TODO: Implémenter l'envoi réel via LiveKit data channel
            # Cela nécessite une connexion WebSocket à la room
            
        except Exception as e:
            self.logger.error(f"❌ Erreur envoi audio: {e}")
    
    async def end_call(self, room_name):
        """Termine un appel"""
        try:
            if room_name in self.active_calls:
                call_info = self.active_calls[room_name]
                duration = asyncio.get_event_loop().time() - call_info['start_time']
                
                self.logger.info(f"📞 Appel terminé: {room_name} (durée: {duration:.1f}s)")
                
                # Envoyer message de fin
                goodbye_text = "Merci pour votre appel. Au revoir !"
                audio_response = await self.voice_processor.text_to_speech_optimized(goodbye_text)
                
                if audio_response:
                    await self.send_audio_to_room(room_name, audio_response)
                
                # Nettoyer
                del self.active_calls[room_name]
                
        except Exception as e:
            self.logger.error(f"❌ Erreur fin d'appel: {e}")
    
    def get_active_calls(self):
        """Retourne la liste des appels actifs"""
        return {
            room_name: {
                'participant': info['participant_identity'],
                'duration': asyncio.get_event_loop().time() - info['start_time']
            }
            for room_name, info in self.active_calls.items()
        }
    
    async def cleanup(self):
        """Nettoie les ressources"""
        try:
            if self.sip_trunk_id:
                self.logger.info("🧹 Suppression du SIP trunk...")
                delete_request = DeleteSipTrunkRequest(sip_trunk_id=self.sip_trunk_id)
                self.livekit_api.sip.delete_sip_trunk(delete_request)
                self.sip_trunk_id = None
                
            self.logger.info("✅ Nettoyage terminé")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur nettoyage: {e}")

# Instance globale
phone_agent = PhoneAgent()

async def main():
    """Point d'entrée principal"""
    print("="*60)
    print("📞 AGENT TÉLÉPHONIQUE AFRICASYS")
    print("="*60)
    
    try:
        # Configuration du SIP trunk
        if await phone_agent.setup_sip_trunk():
            print("✅ Agent téléphonique prêt à recevoir les appels")
            print(f"📞 Numéro: {PHONE_NUMBER}")
            print("🎤 En attente d'appels entrants...")
            
            # Boucle principale (en production, utiliser des webhooks)
            while True:
                await asyncio.sleep(10)
                calls = phone_agent.get_active_calls()
                if calls:
                    print(f"📞 Appels actifs: {len(calls)}")
                
        else:
            print("❌ Erreur configuration SIP trunk")
            
    except KeyboardInterrupt:
        print("\n👋 Arrêt de l'agent téléphonique")
    finally:
        await phone_agent.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
