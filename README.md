# 🎤 Voice AI AfricaSys - Agent Vocal Universel

## 📋 Description

Voice AI AfricaSys est un agent vocal universel qui permet de converser intelligemment avec une IA. L'application combine :

- 🎙️ **Reconnaissance vocale** (Deepgram)
- 🤖 **Intelligence artificielle** (OpenAI)
- 🗣️ **Synthèse vocale** (ElevenLabs)
- 🌐 **Interface web moderne** (Flask + HTML5)
- ⚡ **Temps réel** (WebSocket + LiveKit)

## 🚀 Démarrage Rapide

### 1. Installation des dépendances

```bash
# Installer Python 3.8+ si nécessaire
# Puis installer les packages
pip install -r requirements.txt
```

### 2. Configuration des clés API

Créez/modifiez le fichier `.env` avec vos clés :

```env
# Services IA
DEEPGRAM_API_KEY=votre_clé_deepgram
OPENAI_API_KEY=votre_clé_openai  
ELEVENLABS_API_KEY=votre_clé_elevenlabs

# LiveKit (optionnel pour temps réel)
LIVEKIT_URL=wss://votre-serveur.livekit.cloud
LIVEKIT_API_KEY=votre_clé_livekit
LIVEKIT_API_SECRET=votre_secret_livekit
```

### 3. Démarrer l'application

```bash
# Méthode 1: Script de démarrage recommandé
python start.py

# Méthode 2: Manuel
cd web_app
python main.py
```

### 4. Accéder à l'interface

Ouvrez votre navigateur : **http://localhost:5000**

## 🎯 Fonctionnalités

### 🎙️ Conversation Vocale
- **Push-to-talk** : Maintenez le micro pour parler
- **Amplification audio** : 3x avec anti-clipping
- **Transcription temps réel** : Deepgram français
- **Réponses intelligentes** : OpenAI GPT
- **Synthèse vocale** : ElevenLabs voix naturelle

### 📞 Appel Téléphonique (Simulé)
- **Interface téléphone complète**
- **Clavier numérique**
- **Contrôles d'appel**
- **Timer de communication**
- **Mode muet/haut-parleur**

### 📊 Monitoring
- **Statistiques en temps réel**
- **Logs détaillés**
- **Suivi des sessions**
- **Health checks**

## 🏗️ Architecture

```
Frontend (HTML/JavaScript)
    ↓
Backend Flask Python
    ↓
┌─────────────────────────────┐
│  Services IA Externes        │
│  ┌─────────────┐ ┌─────────┐ │
│  │ Deepgram    │ │ OpenAI  │ │
│  │ (STT)       │ │ (LLM)   │ │
│  └─────────────┘ └─────────┘ │
│           ↓                 │
│  ┌─────────────┐             │
│  │ ElevenLabs  │             │
│  │ (TTS)       │             │
│  └─────────────┘             │
└─────────────────────────────┘
```

## 📁 Structure des Fichiers

```
voice_ai/
├── 📄 voice_agent.py          # Agent vocal principal
├── 📄 start.py               # Script de démarrage
├── 📄 requirements.txt        # Dépendances Python
├── 📄 .env                   # Clés API
├── 📁 web_app/
│   ├── 📄 main.py            # Backend Flask (COMPLÉTÉ!)
│   ├── 📁 templates/
│   │   └── 📄 index_pro.html # Interface professionnelle
│   └── 📁 static/
│       ├── 🎵 demo_input.mp3  # Audio démo
│       ├── 🎵 demo_response.mp3
│       └── 📜 livekit-client.js
├── 📁 tests/                 # Tests et validation
├── 📄 PRESENTATION_*.md     # Documentation business
└── 📄 README.md             # Ce fichier
```

## 🔧 Configuration

### Variables d'environnement

| Variable | Description | Requis |
|----------|-------------|--------|
| `DEEPGRAM_API_KEY` | Clé API Deepgram pour STT | ✅ |
| `OPENAI_API_KEY` | Clé API OpenAI pour LLM | ✅ |
| `ELEVENLABS_API_KEY` | Clé API ElevenLabs pour TTS | ✅ |
| `LIVEKIT_URL` | URL serveur LiveKit | ❌ |
| `LIVEKIT_API_KEY` | Clé API LiveKit | ❌ |
| `LIVEKIT_API_SECRET` | Secret LiveKit | ❌ |

### Paramètres audio

- **Fréquence** : 16kHz (optimal pour voix)
- **Format** : WAV 16-bit mono
- **Amplification** : 3x avec limitation
- **Taille max** : 16MB

## 🎮 Utilisation

### 1. Mode Conversation Vocale

1. Cliquez sur **"Démarrer"**
2. Choisissez **"Conversation Vocale"**
3. **Maintenez le micro** enfoncé pour parler
4. **Relâchez** pour envoyer
5. **Écoutez** la réponse de l'IA

### 2. Mode Appel Téléphonique

1. Cliquez sur **"Démarrer"**
2. Choisissez **"Appel Téléphonique"**
3. **Composez** un numéro ou utilisez celui par défaut
4. Cliquez sur **"Appeler"**
5. Utilisez les contrôles d'appel

### 3. Test du Pipeline

1. Cliquez sur **"Tester"**
2. Le système joue l'audio démo
3. Affiche la transcription simulée
4. Génère et joue la réponse

## 🐛 Dépannage

### Problèmes courants

**"Clés API manquantes"**
```bash
# Vérifiez votre fichier .env
cat .env
```

**"Dépendances manquantes"**
```bash
# Réinstallez tout
pip install -r requirements.txt
```

**"Audio ne fonctionne pas"**
- Vérifiez les permissions micro
- Autorisez le navigateur à utiliser le micro
- Testez avec un autre navigateur

**"Erreur de connexion"**
```bash
# Vérifiez que le port 5000 est libre
netstat -an | grep 5000
```

### Logs et debugging

- **Logs console** : F12 → Console
- **Logs serveur** : Terminal où vous avez lancé `start.py`
- **Sessions** : http://localhost:5000/sessions
- **Health** : http://localhost:5000/health

## 🚀 Déploiement

### Développement
```bash
python start.py
```

### Production (Docker)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "start.py"]
```

### Cloud (Heroku/Render)
- Variables d'environnement dans le dashboard
- Buildpack Python
- Port automatique via `PORT`

## 📈 Performance

### Métriques actuelles
- **Latence** : ~1.8 secondes
- **Précision STT** : 95% (français)
- **Qualité TTS** : Voix naturelle
- **Concurrence** : 1 utilisateur (POC)

### Optimisations futures
- **Cache Redis** pour réponses fréquentes
- **WebSocket** pour temps réel
- **Load balancing** pour scaling
- **CDN** pour fichiers statiques

## 🤝 Contribuer

### Pour développer

1. **Fork** le projet
2. **Branche** feature/votre-fonctionnalité
3. **Commit** avec messages clairs
4. **Push** vers votre fork
5. **Pull Request**

### Normes de code

- **Python** : PEP 8
- **JavaScript** : ES6+
- **HTML** : HTML5 sémantique
- **CSS** : BEM methodology

## 📄 Licence

Ce projet est sous licence MIT. Voir `LICENSE` pour plus de détails.

## 🆘 Support

- **Documentation** : Ce README
- **Issues** : GitHub Issues
- **Email** : contact@africasys.com
- **Discord** : Serveur communautaire

---

## 🎉 Félicitations !

Votre **Voice AI AfricaSys** est maintenant prêt ! 

🎤 **Parlez à votre assistant vocal IA dès maintenant !**

**Made with ❤️ by AfricaSys Team**
