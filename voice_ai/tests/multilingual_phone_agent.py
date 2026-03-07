import os
import sys
import asyncio
import logging
import re
from dotenv import load_dotenv
from livekit import api

# Ajouter le chemin du web_app pour les imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'web_app'))

from voice_processor import VoiceProcessor

load_dotenv()

class MultilingualPhoneAgent:
    """Agent vocal téléphonique multilingue"""
    
    def __init__(self):
        self.voice_processor = VoiceProcessor()
        self.active_calls = {}
        
        # Configuration logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Configuration multilingue
        self.supported_languages = {
            'fr': {
                'name': 'Français',
                'voice_id': 'JBFqnCBsd6RMkjVDRZzb',  # Rachel
                'greeting': 'Bonjour, je suis l\'agent vocal AfricaSys. Comment puis-je vous aider ?',
                'goodbye': 'Merci pour votre appel. Au revoir !',
                'error': 'Désolé, je n\'ai pas bien compris. Pouvez-vous répéter ?',
                'keywords': {
                    'prep': 'La PrEP ou Prophylaxie Pré-Exposition est un médicament préventif qui réduit considérablement le risque de contracter le VIH.',
                    'comment': 'La PrEP se prend sous forme d\'un comprimé par jour, de préférence à la même heure.',
                    'effet': 'Les effets secondaires de la PrEP sont généralement légers et temporaires : nausées, maux de tête.',
                    'prix': 'En France, la PrEP est remboursée à 100% par l\'Assurance Maladie sur prescription médicale.',
                    'qui': 'La PrEP est destinée aux personnes à risque élevé d\'exposition au VIH.',
                    'efficace': 'La PrEP est très efficace : plus de 99% de réduction du risque quand elle est prise correctement.',
                    'bonjour': 'Bonjour ! Je suis votre assistant spécialisé sur la PrEP. Que souhaitez-vous savoir ?',
                    'merci': 'Je vous en prie ! N\'hésitez pas si vous avez d\'autres questions.'
                }
            },
            'en': {
                'name': 'English',
                'voice_id': 'JBFqnCBsd6RMkjVDRZzb',  # Rachel
                'greeting': 'Hello, I am the AfricaSys voice agent. How can I help you?',
                'goodbye': 'Thank you for your call. Goodbye!',
                'error': 'Sorry, I didn\'t understand. Could you please repeat?',
                'keywords': {
                    'prep': 'PrEP or Pre-Exposure Prophylaxis is a preventive medication that significantly reduces the risk of contracting HIV.',
                    'how': 'PrEP is taken as a daily pill, preferably at the same time each day.',
                    'effect': 'PrEP side effects are generally mild and temporary: nausea, headache, fatigue.',
                    'price': 'In France, PrEP is 100% reimbursed by health insurance with medical prescription.',
                    'who': 'PrEP is intended for people at high risk of HIV exposure.',
                    'effective': 'PrEP is very effective: over 99% risk reduction when taken correctly.',
                    'hello': 'Hello! I am your PrEP specialist assistant. What would you like to know?',
                    'thanks': 'You\'re welcome! Feel free to ask if you have other questions.'
                }
            }
        }
        
        # Patterns de détection de langue
        self.language_patterns = {
            'fr': r'\b(bonjour|merci|comment|c\'est|quoi|prep|effet|prix|qui|efficace)\b',
            'en': r'\b(hello|thanks|how|what|prep|effect|price|who|effective|goodbye)\b'
        }
    
    def detect_language(self, text):
        """Détecte la langue du texte"""
        text_lower = text.lower()
        
        # Compter les mots par langue
        language_scores = {}
        for lang, pattern in self.language_patterns.items():
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            language_scores[lang] = len(matches)
        
        # Retourner la langue avec le plus de matches
        if language_scores:
            best_lang = max(language_scores, key=language_scores.get)
            if language_scores[best_lang] > 0:
                return best_lang
        
        # Par défaut, français
        return 'fr'
    
    def get_multilingual_response(self, text, language='fr'):
        """Génère une réponse multilingue"""
        if language not in self.supported_languages:
            language = 'fr'
        
        lang_config = self.supported_languages[language]
        text_lower = text.lower()
        
        # Réponses basées sur les mots-clés
        for keyword, response in lang_config['keywords'].items():
            if keyword in text_lower:
                return response
        
        # Réponse par défaut
        if language == 'fr':
            return f"J'ai bien entendu votre question: {text}. Je suis spécialisé sur la PrEP. Vous pouvez me demander : c'est quoi la PrEP, comment la prendre, quels sont les effets secondaires."
        else:
            return f"I heard your question: {text}. I specialize in PrEP. You can ask me: what is PrEP, how to take it, what are the side effects."
    
    async def text_to_speech_multilingual(self, text, language='fr'):
        """Génère du TTS multilingue"""
        try:
            if language not in self.supported_languages:
                language = 'fr'
            
            lang_config = self.supported_languages[language]
            voice_id = lang_config['voice_id']
            
            print(f"🗣️ Génération vocale ({lang_config['name']})...")
            
            # Utiliser le processeur vocal existant avec la voix appropriée
            # Note: Pour un vrai multilingue, il faudrait changer la voix selon la langue
            audio = self.voice_processor.tts_client.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128"
            )
            
            audio_bytes = b''.join(audio)
            print(f"✅ Audio généré en {lang_config['name']}")
            
            return audio_bytes
            
        except Exception as e:
            print(f"❌ Erreur TTS multilingue: {e}")
            return None
    
    async def simulate_multilingual_call(self, caller_language='fr'):
        """Simule un appel multilingue"""
        try:
            self.logger.info(f"📞 Simulation appel multilingue ({caller_language})...")
            
            # Créer une room
            room_name = f"multilingual_call_{int(asyncio.get_event_loop().time())}"
            participant_identity = f"caller_{caller_language}_{int(asyncio.get_event_loop().time())}"
            
            # Créer un token
            token = api.AccessToken(
                os.getenv("LIVEKIT_API_KEY"), 
                os.getenv("LIVEKIT_API_SECRET")
            ) \
                .with_identity(participant_identity) \
                .with_name(f"Caller ({caller_language})") \
                .with_grants(api.VideoGrants(
                    room_join=True,
                    room=room_name,
                    can_publish=True,
                    can_subscribe=True,
                    can_publish_data=True
                ))
            
            jwt_token = token.to_jwt()
            
            # Générer l'accueil dans la langue détectée
            lang_config = self.supported_languages[caller_language]
            welcome_audio = await self.text_to_speech_multilingual(lang_config['greeting'], caller_language)
            
            self.logger.info(f"✅ Appel multilingue prêt: {room_name}")
            self.logger.info(f"🌐 Langue: {lang_config['name']}")
            self.logger.info(f"🎫 Token: {jwt_token[:50]}...")
            
            return {
                'success': True,
                'room_name': room_name,
                'language': caller_language,
                'greeting': lang_config['greeting'],
                'welcome_audio': welcome_audio,
                'token': jwt_token
            }
            
        except Exception as e:
            self.logger.error(f"❌ Erreur simulation appel multilingue: {e}")
            return None
    
    async def process_multilingual_audio(self, room_name, audio_data, detected_language=None):
        """Traite l'audio multilingue"""
        try:
            self.logger.info(f"🎤 Traitement audio multilingue: {room_name}")
            
            # Utiliser le pipeline STT existant (Deepgram détecte automatiquement la langue)
            user_text = await self.voice_processor.speech_to_text_optimized(audio_data)
            
            if not user_text or len(user_text.strip()) < 2:
                error_text = self.supported_languages[detected_language or 'fr']['error']
                audio_error = await self.text_to_speech_multilingual(error_text, detected_language or 'fr')
                return audio_error, error_text
            
            # Détecter la langue si non spécifiée
            if not detected_language:
                detected_language = self.detect_language(user_text)
            
            self.logger.info(f"🌐 Langue détectée: {self.supported_languages[detected_language]['name']}")
            self.logger.info(f"📝 Texte: '{user_text}'")
            
            # Générer la réponse multilingue
            response_text = self.get_multilingual_response(user_text, detected_language)
            
            # Générer l'audio multilingue
            response_audio = await self.text_to_speech_multilingual(response_text, detected_language)
            
            if response_audio:
                self.logger.info(f"🗣️ Réponse générée en {self.supported_languages[detected_language]['name']}")
                return response_audio, response_text
            else:
                return None, response_text
                
        except Exception as e:
            self.logger.error(f"❌ Erreur traitement audio multilingue: {e}")
            return None, "Désolé, j'ai rencontré une erreur technique."

# Instance globale
multilingual_agent = MultilingualPhoneAgent()

async def test_multilingual_features():
    """Test des fonctionnalités multilingues"""
    print("="*60)
    print("🌐 TEST AGENT MULTILINGUE")
    print("="*60)
    
    # Test 1: Appel français
    print("\n1️⃣ Test appel français...")
    french_call = await multilingual_agent.simulate_multilingual_call('fr')
    if french_call:
        print(f"✅ Appel français: {french_call['greeting']}")
    
    # Test 2: Appel anglais
    print("\n2️⃣ Test appel anglais...")
    english_call = await multilingual_agent.simulate_multilingual_call('en')
    if english_call:
        print(f"✅ Appel anglais: {english_call['greeting']}")
    
    # Test 3: Détection de langue
    print("\n3️⃣ Test détection de langue...")
    test_texts = [
        ("Bonjour, c'est quoi la PrEP ?", "fr"),
        ("Hello, what is PrEP?", "en"),
        ("Merci pour votre aide", "fr"),
        ("Thanks for your help", "en")
    ]
    
    for text, expected_lang in test_texts:
        detected = multilingual_agent.detect_language(text)
        status = "✅" if detected == expected_lang else "❌"
        print(f"{status} '{text}' -> {detected} (attendu: {expected_lang})")
    
    # Test 4: Réponses multilingues
    print("\n4️⃣ Test réponses multilingues...")
    questions = [
        ("C'est quoi la PrEP ?", "fr"),
        ("What is PrEP?", "en"),
        ("Quels sont les effets ?", "fr"),
        ("What are the side effects?", "en")
    ]
    
    for question, lang in questions:
        response = multilingual_agent.get_multilingual_response(question, lang)
        print(f"📝 {lang.upper()}: {question}")
        print(f"🤖 {response[:50]}...")
        print()
    
    print("🎉 TEST MULTILINGUE TERMINÉ")

if __name__ == "__main__":
    asyncio.run(test_multilingual_features())
