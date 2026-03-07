// LiveKit Client simplifié pour l'interface web
// Cette version utilise le serveur comme proxy pour LiveKit

class Room {
    constructor() {
        this.state = 'disconnected';
        this.participants = new Map();
        this.localParticipant = new LocalParticipant();
        this.tracks = new Map();
        this.eventListeners = new Map();
        
        // Lier le localParticipant à la room
        this.localParticipant.room = this;
    }

    async connect(url, token) {
        try {
            // Utiliser le serveur comme proxy pour LiveKit
            const response = await fetch('/livekit/connect', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url, token })
            });

            if (!response.ok) {
                throw new Error('Erreur connexion LiveKit');
            }

            const result = await response.json();
            
            if (result.success) {
                this.state = 'connected';
                this.emit('connected');
                return true;
            } else {
                throw new Error(result.error || 'Erreur connexion');
            }
        } catch (error) {
            this.state = 'disconnected';
            this.emit('disconnected');
            throw error;
        }
    }

    disconnect() {
        this.state = 'disconnected';
        this.emit('disconnected');
    }

    async publishTrack(track) {
        try {
            // Simuler la publication de track
            const response = await fetch('/livekit/publish', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    trackKind: track.kind,
                    trackId: track.id 
                })
            });

            if (response.ok) {
                this.emit('trackPublished', { track });
                return true;
            }
        } catch (error) {
            console.error('Erreur publication track:', error);
        }
        return false;
    }

    on(event, callback) {
        if (!this.eventListeners.has(event)) {
            this.eventListeners.set(event, []);
        }
        this.eventListeners.get(event).push(callback);
    }

    emit(event, data) {
        const listeners = this.eventListeners.get(event) || [];
        listeners.forEach(callback => callback(data));
    }
}

class LocalParticipant {
    constructor() {
        this.tracks = new Map();
    }

    async publishTrack(track) {
        // Créer un AudioTrack wrapper
        const audioTrack = new AudioTrack(track.id, 'audio');
        this.tracks.set(track.id, audioTrack);
        
        // Notifier la room
        if (this.room) {
            this.room.emit('trackPublished', { track: audioTrack });
        }
        
        return audioTrack;
    }
}

class AudioTrack {
    constructor(id, kind = 'audio') {
        this.id = id || 'track_' + Date.now();
        this.kind = kind;
        this.enabled = true;
    }
}

// Export pour compatibilité avec l'import dynamique
export { Room, AudioTrack };
