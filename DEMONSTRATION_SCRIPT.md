# SCRIPT DE DÉMONSTRATION - VOICE AI AFRICASYS

## 🎯 OBJECTIF DE LA DÉMO
Présenter un agent vocal intelligent capable de comprendre et répondre aux questions sur la PrEP (Prophylaxie Pré-Exposition) via une interface web moderne.

## 📋 DÉROULÉ DE LA DÉMONSTRATION (5-7 minutes)

### 1. INTRODUCTION (1 minute)
"Bonjour, je vais vous présenter notre agent vocal intelligent développé par AfricaSys. C'est une solution innovante qui permet aux utilisateurs d'obtenir des informations sur la PrEP simplement en parlant à leur navigateur web."

### 2. PRÉSENTATION DE L'INTERFACE (30 secondes)
- **Pointez l'interface web professionnelle**
- "Voici notre interface web moderne et intuitive"
- "Elle propose deux modes : conversation vocale et appel téléphonique"

### 3. DÉMONSTRATION MODE CONVERSATION VOCALE (2 minutes)

#### Étape 1 : Démarrage
"Cliquez sur le bouton Démarrer, puis choisissez Conversation Vocale"

#### Étape 2 : Première question
"Maintenant, je vais poser une question simple en maintenant le micro enfoncé"
- **Action : Maintenir le micro et dire** "Bonjour, qu'est-ce que la PrEP ?"
- **Résultat attendu** : L'agent répond avec une explication claire de la PrEP

#### Étape 3 : Question spécifique
"Testons maintenant une question plus précise"
- **Action : Maintenir le micro et dire** "Quels sont les effets secondaires de la PrEP ?"
- **Résultat attendu** : L'agent liste les effets secondaires courants

### 4. DÉMONSTRATION MODE APPEL TÉLÉPHONIQUE (1 minute)

#### Étape 1 : Changement de mode
"Notre application simule également un appel téléphonique"
- **Action : Retourner au menu, choisir Appel Téléphonique**

#### Étape 2 : Simulation d'appel
"Cette interface reproduit une expérience d'appel réaliste"
- **Action : Composer un numéro et lancer l'appel**
- **Résultat attendu** : Interface d'appel avec timer et contrôles

### 5. POINTS TECHNIQUES CLÉS (1 minute)

#### Architecture
"Notre solution repose sur une architecture robuste :"
- **Frontend** : HTML5, JavaScript moderne avec LiveKit pour l'audio temps réel
- **Backend** : Flask Python avec gestion multi-utilisateurs
- **Services IA** : 
  - Deepgram pour la reconnaissance vocale (STT)
  - ElevenLabs pour la synthèse vocale (TTS)
  - Réponses intelligentes sur la PrEP

#### Fonctionnalités avancées
"Nous avons implémenté plusieurs optimisations :"
- Gestion multi-utilisateurs avec rooms isolées
- Cache intelligent pour réduire la latence
- Fallback automatique en cas d'échec de reconnaissance
- Interface responsive et accessible

### 6. CAS D'USAGE ET IMPACT (30 secondes)

#### Applications concrètes
"Cette solution peut être déployée pour :"
- **Centres de santé** : Information disponible 24/7
- **Associations** : Support aux personnes concernées par le VIH
- **Plateformes mobiles** : Accessibilité via smartphone
- **Services publics** : Information santé dématérialisée

#### Impact social
"L'impact est significatif :"
- Réduction de la stigmatisation (anonymat)
- Accessibilité pour les personnes illettrées
- Information disponible en plusieurs langues
- Support psychologique immédiat

### 7. CONCLUSION ET QUESTIONS (1 minute)

#### Résumé
"Pour résumer, notre agent vocal AfricaSys :"
- ✅ Est facile à utiliser (interface intuitive)
- ✅ Fournit des informations fiables sur la PrEP
- ✅ Est accessible 24/7 depuis n'importe quel appareil
- ✅ Respecte la confidentialité des utilisateurs
- ✅ Est techniquement robuste et évolutif

#### Perspectives
"Nous envisageons d'étendre les fonctionnalités :"
- Ajout d'autres langues (anglais, arabe, langues locales)
- Intégration avec les systèmes de santé
- Version mobile native
- Personnalisation selon les profils utilisateurs

#### Questions
"Merci de votre attention. Avez-vous des questions sur notre solution ?"

---

## 🎤 PHRASES TEST POUR LA DÉMO

### Questions simples :
1. "Bonjour, qu'est-ce que la PrEP ?"
2. "Comment prendre la PrEP ?"
3. "Est-ce que la PrEP est efficace ?"
4. "Où trouver la PrEP ?"

### Questions complexes :
1. "Quels sont les effets secondaires courants de la PrEP ?"
2. "Est-ce que la PrEP est remboursée en France ?"
3. "Combien de temps faut-il pour que la PrEP soit efficace ?"
4. "Est-ce que je peux arrêter la PrEP ?"

## 🔧 VÉRIFICATION TECHNIQUE PRÉ-DÉMO

### Checklist :
- [ ] Serveur Flask démarré (`python server.py`)
- [ ] Accès web sur http://localhost:5000
- [ ] Micro du navigateur fonctionnel
- [ ] Haut-parleurs configurés
- [ ] Connexion internet stable (pour les APIs)
- [ ] Clés API valides dans .env

### Commandes de test :
```bash
cd web_app
python server.py
# Vérifier que le serveur démarre sans erreur
```

### Test rapide :
1. Ouvrir http://localhost:5000
2. Cliquer sur "Tester" pour vérifier le pipeline
3. Vérifier les logs dans la console

---

## 🚨 DÉPANNAGE RAPIDE

### Si le serveur ne démarre pas :
1. Vérifier les dépendances : `pip install flask flask-cors`
2. Vérifier le fichier .env
3. Redémarrer le terminal

### Si l'audio ne fonctionne pas :
1. Vérifier les permissions du micro
2. Tester avec un autre navigateur
3. Vérifier les haut-parleurs

### Si la reconnaissance vocale échoue :
1. Vérifier la clé Deepgram
2. Parler plus clairement
3. Réduire le bruit ambiant

---

*Bon courage pour votre démonstration !*
