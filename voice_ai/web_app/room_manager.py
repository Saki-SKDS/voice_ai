import asyncio
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from voice_processor import VoiceProcessor

@dataclass
class UserSession:
    """Session utilisateur dans une room"""
    user_id: str
    user_name: str
    room_name: str
    joined_at: float
    is_speaking: bool = False
    last_activity: float = 0
    
    def update_activity(self):
        """Met à jour la dernière activité"""
        self.last_activity = time.time()

class RoomManager:
    """Gestionnaire des rooms multi-utilisateurs"""
    
    def __init__(self):
        self.rooms: Dict[str, List[UserSession]] = {}
        self.user_sessions: Dict[str, UserSession] = {}  # user_id -> session
        self.voice_processors: Dict[str, VoiceProcessor] = {}  # room_name -> processor
        self.max_users_per_room = 10
        self.session_timeout = 3600  # 1 heure
        
    def create_room(self, room_name: str) -> bool:
        """Crée une nouvelle room"""
        if room_name not in self.rooms:
            self.rooms[room_name] = []
            self.voice_processors[room_name] = VoiceProcessor()
            print(f"Room créée: {room_name}")
            return True
        return False
    
    def join_room(self, user_id: str, user_name: str, room_name: str) -> dict:
        """Fait rejoindre une room à un utilisateur"""
        try:
            # Créer la room si elle n'existe pas
            if room_name not in self.rooms:
                self.create_room(room_name)
            
            # Vérifier si l'utilisateur n'est pas déjà dans la room
            if user_id in self.user_sessions:
                existing_session = self.user_sessions[user_id]
                if existing_session.room_name == room_name:
                    return {"success": False, "message": "Déjà dans cette room"}
                else:
                    # Quitter l'ancienne room
                    self.leave_room(user_id)
            
            # Vérifier la capacité de la room
            if len(self.rooms[room_name]) >= self.max_users_per_room:
                return {"success": False, "message": "Room pleine"}
            
            # Créer la session
            session = UserSession(
                user_id=user_id,
                user_name=user_name,
                room_name=room_name,
                joined_at=time.time()
            )
            session.update_activity()
            
            # Ajouter à la room
            self.rooms[room_name].append(session)
            self.user_sessions[user_id] = session
            
            print(f"{user_name} a rejoint la room {room_name}")
            
            return {
                "success": True,
                "room_name": room_name,
                "user_count": len(self.rooms[room_name]),
                "users": [s.user_name for s in self.rooms[room_name]]
            }
            
        except Exception as e:
            print(f"Erreur join_room: {e}")
            return {"success": False, "message": str(e)}
    
    def leave_room(self, user_id: str) -> bool:
        """Fait quitter une room à un utilisateur"""
        try:
            if user_id not in self.user_sessions:
                return False
            
            session = self.user_sessions[user_id]
            room_name = session.room_name
            
            # Retirer de la room
            if room_name in self.rooms:
                self.rooms[room_name] = [s for s in self.rooms[room_name] if s.user_id != user_id]
                
                # Supprimer la room si vide
                if len(self.rooms[room_name]) == 0:
                    del self.rooms[room_name]
                    if room_name in self.voice_processors:
                        del self.voice_processors[room_name]
                    print(f"Room supprimée: {room_name}")
            
            # Supprimer la session
            del self.user_sessions[user_id]
            
            print(f"Utilisateur {user_id} a quitté la room {room_name}")
            return True
            
        except Exception as e:
            print(f"Erreur leave_room: {e}")
            return False
    
    def get_room_users(self, room_name: str) -> List[dict]:
        """Retourne la liste des utilisateurs dans une room"""
        if room_name not in self.rooms:
            return []
        
        return [
            {
                "user_id": s.user_id,
                "user_name": s.user_name,
                "is_speaking": s.is_speaking,
                "joined_at": s.joined_at
            }
            for s in self.rooms[room_name]
        ]
    
    def get_voice_processor(self, room_name: str) -> Optional[VoiceProcessor]:
        """Retourne le processeur vocal pour une room"""
        return self.voice_processors.get(room_name)
    
    def set_user_speaking(self, user_id: str, is_speaking: bool):
        """Met à jour l'état de parole d'un utilisateur"""
        if user_id in self.user_sessions:
            self.user_sessions[user_id].is_speaking = is_speaking
            self.user_sessions[user_id].update_activity()
    
    def cleanup_inactive_sessions(self):
        """Nettoie les sessions inactives"""
        current_time = time.time()
        inactive_users = []
        
        for user_id, session in self.user_sessions.items():
            if current_time - session.last_activity > self.session_timeout:
                inactive_users.append(user_id)
        
        for user_id in inactive_users:
            self.leave_room(user_id)
            print(f"🧹 Session inactive supprimée: {user_id}")
    
    def get_stats(self) -> dict:
        """Retourne les statistiques du système"""
        return {
            "total_rooms": len(self.rooms),
            "total_users": len(self.user_sessions),
            "rooms": {
                room_name: {
                    "user_count": len(users),
                    "users": [s.user_name for s in users]
                }
                for room_name, users in self.rooms.items()
            }
        }

# Instance globale
room_manager = RoomManager()
