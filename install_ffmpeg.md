# Installation de FFmpeg pour Voice AI

FFmpeg est nécessaire pour la conversion audio WebM vers WAV.

## Windows

### Option 1: Téléchargement manuel
1. Téléchargez FFmpeg depuis : https://ffmpeg.org/download.html
2. Choisissez Windows -> Build
3. Décompressez le fichier ZIP
4. Ajoutez le dossier `bin` à votre PATH Windows

### Option 2: Avec Chocolatey
```bash
choco install ffmpeg
```

### Option 3: Avec Winget
```bash
winget install ffmpeg
```

## Vérification de l'installation

Ouvrez un nouveau terminal et vérifiez :
```bash
ffmpeg -version
```

## Alternative (sans FFmpeg)

L'application Voice AI fonctionne maintenant même sans FFmpeg installé.
Elle utilisera des méthodes alternatives pour traiter les fichiers audio.
