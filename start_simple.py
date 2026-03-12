#!/usr/bin/env python3
"""
Script de démarrage simple pour Voice AI AfricaSys
Utilise des variables d'environnement pour les clés API
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent))

def check_environment():
    """Vérifie que les variables d'environnement nécessaires sont définies"""
    required_vars = ['DEEPGRAM_API_KEY', 'OPENAI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var) or os.getenv(var) == f'votre_cle_{var.lower().replace("_api_key", "")}':
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Variables d'environnement manquantes :")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Solution :")
        print("   1. Créez un fichier .env à la racine du projet")
        print("   2. Ajoutez vos clés API :")
        print("      DEEPGRAM_API_KEY=votre_vraie_clé_deepgram")
        print("      OPENAI_API_KEY=votre_vraie_clé_openai")
        print("      ELEVENLABS_API_KEY=votre_vraie_clé_elevenlabs (optionnel)")
        print("      GROQ_API_KEY=votre_vraie_clé_groq (optionnel)")
        print("   3. Relancez ce script")
        return False
    
    return True

def start_web_app():
    """Démarre l'application web Flask"""
    try:
        from web_app.main import app
        
        print("🚀 Démarrage de Voice AI AfricaSys...")
        print(f"📍 Port : 5002")
        print(f"🌐 URL : http://localhost:5002")
        print("=" * 50)
        
        # Désactiver le debug en production
        app.run(host='0.0.0.0', port=5002, debug=False)
        
    except ImportError as e:
        print(f"❌ Erreur d'importation : {e}")
        print("Assurez-vous que le module web_app.main existe")
        return False
    except Exception as e:
        print(f"❌ Erreur au démarrage : {e}")
        return False
    
    return True

def main():
    """Fonction principale"""
    print("🎤 Voice AI AfricaSys - Script de démarrage")
    print("=" * 50)
    
    # Charger les variables d'environnement depuis .env si disponible
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Fichier .env chargé")
    except ImportError:
        print("⚠️  python-dotbox non installé, utilisez les variables d'environnement système")
    
    # Vérifier les variables d'environnement
    if not check_environment():
        sys.exit(1)
    
    # Démarrer l'application web
    if not start_web_app():
        sys.exit(1)

if __name__ == "__main__":
    main()
