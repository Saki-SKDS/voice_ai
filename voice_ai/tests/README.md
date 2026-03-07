# 📁 DOSSIER TESTS - AGENTS VOCAL AFRICASYS

## 🎯 **Contenu du dossier**

Ce dossier contient tous les fichiers de test, démo et validation pour votre projet d'agents vocaux.

---

## 🧪 **TESTS AUTOMATISÉS**

### **Tests complets**
- **`SEMAINE1_COMPLETE_TEST.py`** - Validation finale de toute la semaine 1
- **`test_complet.py`** - Test complet du système web
- **`POC2_VALIDATION.py`** - Validation du POC 2 agent téléphonique

### **Tests unitaires**
- **`test_apis.py`** - Test individuel des APIs (Deepgram, ElevenLabs, OpenAI, LiveKit)
- **`test_phone_pipeline.py`** - Test du pipeline téléphonique
- **`test_livekit_simple.py`** - Test simple de LiveKit

### **Tests rapides**
- **`test_simple.py`** - Test rapide avec micro
- **`test_voice_simple.py`** - Test STT+TTS simple
- **`test_with_file.py`** - Test avec fichier audio

---

## 🎬 **DÉMONSTRATIONS**

### **Pipeline vocal**
- **`demo_pipeline.py`** - Démonstration complète du pipeline vocal
- **`demo_input.mp3`** - Audio d'entrée généré
- **`demo_response.mp3`** - Audio de réponse généré

### **Agents spécifiques**
- **`phone_agent_simple.py`** - Démonstration agent téléphonique
- **`multilingual_phone_agent.py`** - Agent multilingue

---

## 🔧 **SERVEURS DE TEST**

### **Serveur téléphonique**
- **`phone_server.py`** - Serveur API pour l'agent téléphonique
- **`phone_agent.py`** - Agent téléphonique complet

### **Utilitaires**
- **`generate_token.py`** - Génération de tokens LiveKit
- **`web_agent.py`** - Agent web simple

---

## 📊 **RAPPORTS ET DOCUMENTATION**

### **Bilans**
- **`BILAN_SEMAINE1.md`** - Bilan complet de la semaine 1
- **`RAPPORT_PHASE3.md`** - Rapport de la Phase 3

---

## 🎵 **FICHIERS AUDIO**

### **Tests audio**
- **`temp.wav`** - Fichier audio temporaire
- **`test_audio.mp3`** - Audio de test

---

## 🚀 **UTILISATION**

### **Pour tester le projet complet :**
```bash
cd Tests
python SEMAINE1_COMPLETE_TEST.py
```

### **Pour tester uniquement le web :**
```bash
cd Tests
python test_complet.py
```

### **Pour tester uniquement le téléphone :**
```bash
cd Tests
python POC2_VALIDATION.py
```

### **Pour une démo rapide :**
```bash
cd Tests
python demo_pipeline.py
```

### **Pour tester les APIs :**
```bash
cd Tests
python test_apis.py
```

---

## 📋 **STRUCTURE ORGANISÉE**

```
Tests/
├── 🧪 Tests/
│   ├── SEMAINE1_COMPLETE_TEST.py    # Validation finale
│   ├── test_complet.py              # Test web complet
│   ├── POC2_VALIDATION.py           # Validation POC 2
│   ├── test_apis.py                 # Test APIs
│   └── test_phone_pipeline.py       # Test téléphone
├── 🎬 Démos/
│   ├── demo_pipeline.py             # Démo pipeline
│   ├── phone_agent_simple.py        # Démo téléphone
│   └── multilingual_phone_agent.py  # Agent multilingue
├── 🔧 Serveurs/
│   ├── phone_server.py              # Serveur téléphone
│   └── generate_token.py            # Tokens LiveKit
├── 📊 Rapports/
│   ├── BILAN_SEMAINE1.md            # Bilan semaine 1
│   └── RAPPORT_PHASE3.md            # Rapport Phase 3
└── 🎵 Audio/
    ├── demo_input.mp3               # Audio démo
    ├── demo_response.mp3            # Réponse démo
    └── temp.wav                     # Audio temporaire
```

---

## 🎯 **RECOMMANDATIONS**

### **Avant de lancer les tests :**
1. **Assurez-vous que les serveurs sont démarrés** :
   - Serveur web : `python web_app/server.py` (port 5000)
   - Serveur téléphone : `python Tests/phone_server.py` (port 5001)

2. **Vérifiez les clés API** dans le fichier `.env`

3. **Lancez les tests dans l'ordre** :
   - D'abord : `test_apis.py` (vérifier les connexions)
   - Ensuite : `test_complet.py` (tester le web)
   - Puis : `POC2_VALIDATION.py` (tester le téléphone)
   - Enfin : `SEMAINE1_COMPLETE_TEST.py` (validation finale)

### **Pour déboguer :**
- Utilisez `test_apis.py` pour vérifier chaque API individuellement
- Utilisez `demo_pipeline.py` pour vérifier le pipeline vocal
- Consultez les logs des serveurs pour plus de détails

---

**Ce dossier est votre boîte à outils complète pour tester, valider et démontrer votre système d'agents vocaux !** 🚀
