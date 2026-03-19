#!/usr/bin/env python3
"""
Script de démarrage simple pour Voice AI AfricaSys
Configuration et lancement de l'application web
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Vérifie la version Python"""
    version = sys.version_info
    if version.major < 3 or version.minor < 8:
        print("❌ Python 3.8+ requis")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    """Vérifie les dépendances"""
    try:
        import flask
        print("✅ Flask OK")
    except ImportError:
        print("❌ Flask manquant")
        return False
    
    try:
        import sounddevice
        print("✅ Sounddevice OK")
    except ImportError:
        print("❌ Sounddevice manquant")
        return False
    
    return True

def check_env_file():
    """Vérifie le fichier .env"""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  Fichier .env manquant - création avec template...")
        with open(".env", "w") as f:
            f.write("""# Services IA
DEEPGRAM_API_KEY=your_deepgram_key_here
OPENAI_API_KEY=your_openai_key_here  
ELEVENLABS_API_KEY=your_elevenlabs_key_here

# LiveKit (optionnel)
LIVEKIT_URL=wss://your-serveur.livekit.cloud
LIVEKIT_API_KEY=your_livekit_key
LIVEKIT_API_SECRET=your_livekit_secret
""")
        print("✅ Fichier .env créé - éditez-le avec vos clés API")
        return False
    
    print("✅ Fichier .env trouvé")
    return True

def start_app():
    """Démarre l'application"""
    print("\n🚀 Démarrage de Voice AI AfricaSys...")
    
    # Vérifications
    checks = []
    
    # 1. Version Python
    checks.append(check_python_version())
    
    # 2. Dépendances
    checks.append(check_dependencies())
    
    # 3. Fichier .env
    checks.append(check_env_file())
    
    # 4. Clés API
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        # Configuration depuis .env
        # Les clés doivent être dans le fichier .env :
        # DEEPGRAM_API_KEY=your_key_here
        # OPENAI_API_KEY=your_key_here
        # ELEVENLABS_API_KEY=your_key_here
        # WAXAL_API_KEY=your_key_here
        required_keys = ['DEEPGRAM_API_KEY', 'OPENAI_API_KEY', 'ELEVENLABS_API_KEY']
        missing = [k for k in required_keys if not os.getenv(k)]
        
        if missing:
            print(f"❌ Clés API manquantes: {missing}")
            checks.append(False)
        else:
            print("✅ Clés API OK")
            checks.append(True)
    except Exception as e:
        print(f"❌ Erreur clés API: {e}")
        checks.append(False)
    
    # Si toutes les vérifications sont OK
    if all(checks):
        print("\n✅ Tous les checks sont OK !")
        print("🌐 Ouverture de http://localhost:5000")
        
        # Démarrage de l'app
        try:
            os.chdir("web_app")
            subprocess.run([sys.executable, "main.py"])
        except KeyboardInterrupt:
            print("\n👋 Arrêt de l'application")
        except Exception as e:
            print(f"❌ Erreur démarrage: {e}")
    else:
        print("\n❌ Certains checks ont échoué")
        print("📖 Consultez le README.md pour plus d'informations")
        return False
    
    return True

if __name__ == "__main__":
    start_app()
