#!/usr/bin/env python3
"""
Système de questions-réponses en bambara pour Voice AI AfricaSys
"""

import json
import random
from typing import Dict, List, Tuple

class QuestionsBambara:
    def __init__(self):
        self.questions = {
            "salutations": [
                {
                    "question": "I ni sogoma?",
                    "reponse": "N ba sogoma. I ni ce?",
                    "traduction": "Bonjour - Bonjour, comment allez-vous?"
                },
                {
                    "question": "I ka kènè?",
                    "reponse": "N sira bè. N'i don?",
                    "traduction": "Comment allez-vous? - Je vais bien, et vous?"
                },
                {
                    "question": "I ni sira",
                    "reponse": "N sira bè a ye",
                    "traduction": "Salutations - Merci"
                },
                {
                    "question": "I ni wula",
                    "reponse": "N bè wula",
                    "traduction": "Bonsoir - Bonsoir"
                }
            ],
            "presentation": [
                {
                    "question": "I tògò ko?",
                    "reponse": "N tògò Adama",
                    "traduction": "Comment vous appelez-vous? - Je m'appelle Adama"
                },
                {
                    "question": "I bè duguma bò?",
                    "reponse": "N bè Bamako duguma bò",
                    "traduction": "D'où venez-vous? - Je viens de Bamako"
                },
                {
                    "question": "I musa?",
                    "reponse": "N musa ka kònò",
                    "traduction": "Quel est votre âge? - J'ai 25 ans"
                }
            ],
            "quotidien": [
                {
                    "question": "N bè feer?",
                    "reponse": "A bè feer",
                    "traduction": "Quel temps fait-il? - Il fait beau"
                },
                {
                    "question": "I bè min bila?",
                    "reponse": "N bè sòrò",
                    "traduction": "Où allez-vous? - Je vais au marché"
                },
                {
                    "question": "I bè di dò?",
                    "reponse": "N bè di tò",
                    "traduction": "Qu'est-ce que vous faites? - Je travaille"
                }
            ],
            "nourriture": [
                {
                    "question": "I bè di mun?",
                    "reponse": "N bè di tigadègu",
                    "traduction": "Qu'est-ce que vous mangez? - Je mange du riz"
                },
                {
                    "question": "Dòò min bè bon?",
                    "reponse": "Tigadègu bè bon",
                    "traduction": "Quel est bon? - Le riz est bon"
                },
                {
                    "question": "I bè min min?",
                    "reponse": "N bè min dabi",
                    "traduction": "Qu'est-ce que vous buvez? - Je bois de l'eau"
                }
            ],
            "famille": [
                {
                    "question": "I denw bè bɛ?",
                    "reponse": "Ayi, n denw bè bɛ",
                    "traduction": "Avez-vous des enfants? - Oui, j'ai des enfants"
                },
                {
                    "question": "I ba fè?",
                    "reponse": "N ba fè",
                    "traduction": "Êtes-vous marié(e)? - Je suis marié(e)"
                },
                {
                    "question": "I n'fa bè bɛ?",
                    "reponse": "Ayi, n n'fa tè bɛ",
                    "traduction": "Avez-vous des frères? - Non, je n'ai pas de frères"
                }
            ],
            "temps": [
                {
                    "question": "N bè juman?",
                    "reponse": "N bè ladinin",
                    "traduction": "Quel jour sommes-nous? - Nous sommes lundi"
                },
                {
                    "question": "N bè kɔnɔ?",
                    "reponse": "N bè tile kɔnɔ",
                    "traduction": "En quelle saison sommes-nous? - Nous sommes en saison sèche"
                },
                {
                    "question": "N bè lakra?",
                    "reponse": "N bè lakra 10",
                    "traduction": "Quelle heure est-il? - Il est 10 heures"
                }
            ]
        }
        
        self.niveaux = {
            "debutant": ["salutations", "presentation"],
            "intermediaire": ["salutations", "presentation", "quotidien", "nourriture"],
            "avance": ["salutations", "presentation", "quotidien", "nourriture", "famille", "temps"]
        }
    
    def get_question_aleatoire(self, categorie: str = None, niveau: str = "debutant") -> Dict:
        """Retourne une question aléatoire selon la catégorie ou le niveau"""
        if categorie:
            if categorie in self.questions:
                return random.choice(self.questions[categorie])
            else:
                return {"erreur": f"Catégorie '{categorie}' non trouvée"}
        
        # Si pas de catégorie, choisir selon le niveau
        categories_disponibles = self.niveaux.get(niveau, self.niveaux["debutant"])
        categorie_choisie = random.choice(categories_disponibles)
        return random.choice(self.questions[categorie_choisie])
    
    def get_questions_par_categorie(self, categorie: str) -> List[Dict]:
        """Retourne toutes les questions d'une catégorie"""
        return self.questions.get(categorie, [])
    
    def get_categories(self) -> List[str]:
        """Retourne la liste des catégories disponibles"""
        return list(self.questions.keys())
    
    def verifier_reponse(self, question: str, reponse_utilisateur: str) -> Tuple[bool, str]:
        """Vérifie si la réponse de l'utilisateur est correcte"""
        for categorie, questions in self.questions.items():
            for q in questions:
                if q["question"].lower() == question.lower():
                    reponse_correcte = q["reponse"].lower().strip()
                    reponse_user = reponse_utilisateur.lower().strip()
                    
                    if reponse_user == reponse_correcte:
                        return True, "Correct! 🎉"
                    else:
                        return False, f"Incorrect. La bonne réponse est: {q['reponse']}"
        
        return False, "Question non trouvée"
    
    def quiz(self, nombre_questions: int = 5, niveau: str = "debutant") -> List[Dict]:
        """Génère un quiz avec plusieurs questions"""
        quiz_questions = []
        categories = self.niveaux.get(niveau, self.niveaux["debutant"])
        
        for _ in range(nombre_questions):
            categorie = random.choice(categories)
            question = random.choice(self.questions[categorie])
            quiz_questions.append(question)
        
        return quiz_questions
    
    def statistiques(self) -> Dict:
        """Retourne des statistiques sur les questions"""
        stats = {
            "total_categories": len(self.questions),
            "total_questions": sum(len(q) for q in self.questions.values()),
            "categories": {}
        }
        
        for categorie, questions in self.questions.items():
            stats["categories"][categorie] = len(questions)
        
        return stats
    
    def sauvegarder_progression(self, utilisateur: str, score: int, total: int):
        """Sauvegarde la progression d'un utilisateur (simulation)"""
        progression = {
            "utilisateur": utilisateur,
            "score": score,
            "total": total,
            "pourcentage": round((score / total) * 100, 2),
            "date": "2026-03-17"  # Date actuelle
        }
        
        # Dans une vraie application, ceci serait sauvegardé dans une base de données
        print(f"Progression sauvegardée pour {utilisateur}: {score}/{total} ({progression['pourcentage']}%)")
        return progression

def interface_interactive():
    """Interface interactive pour pratiquer le bambara"""
    qb = QuestionsBambara()
    
    print("🎓 Système d'Apprentissage du Bambara")
    print("=" * 50)
    
    while True:
        print("\n📋 Menu:")
        print("1. Question aléatoire")
        print("2. Quiz")
        print("3. Questions par catégorie")
        print("4. Vérifier une réponse")
        print("5. Statistiques")
        print("6. Quitter")
        
        choix = input("\nChoisissez une option (1-6): ")
        
        if choix == "1":
            niveau = input("Niveau (debutant/intermediaire/avance) [debutant]: ") or "debutant"
            q = qb.get_question_aleatoire(niveau=niveau)
            print(f"\n❓ Question: {q['question']}")
            print(f"💡 Traduction: {q['traduction']}")
            input("Appuyez sur Entrée pour voir la réponse...")
            print(f"✅ Réponse: {q['reponse']}")
        
        elif choix == "2":
            nombre = int(input("Nombre de questions [5]: ") or "5")
            niveau = input("Niveau (debutant/intermediaire/avance) [debutant]: ") or "debutant"
            
            questions_quiz = qb.quiz(nombre, niveau)
            score = 0
            
            print(f"\n🎯 Quiz de {len(questions_quiz)} questions")
            print("-" * 30)
            
            for i, q in enumerate(questions_quiz, 1):
                print(f"\nQuestion {i}: {q['question']}")
                reponse = input("Votre réponse: ")
                
                correcte, feedback = qb.verifier_reponse(q['question'], reponse)
                if correcte:
                    score += 1
                    print(f"✅ {feedback}")
                else:
                    print(f"❌ {feedback}")
            
            print(f"\n📊 Score final: {score}/{len(questions_quiz)}")
            qb.sauvegarder_progression("utilisateur_demo", score, len(questions_quiz))
        
        elif choix == "3":
            categories = qb.get_categories()
            print("\n📚 Catégories disponibles:")
            for i, cat in enumerate(categories, 1):
                print(f"{i}. {cat}")
            
            try:
                choix_cat = int(input("\nChoisissez une catégorie: ")) - 1
                if 0 <= choix_cat < len(categories):
                    categorie_choisie = categories[choix_cat]
                    questions = qb.get_questions_par_categorie(categorie_choisie)
                    
                    print(f"\n📖 Questions dans la catégorie '{categorie_choisie}':")
                    for i, q in enumerate(questions, 1):
                        print(f"\n{i}. {q['question']}")
                        print(f"   Traduction: {q['traduction']}")
                        print(f"   Réponse: {q['reponse']}")
            except (ValueError, IndexError):
                print("❌ Choix invalide")
        
        elif choix == "4":
            question = input("Entrez la question: ")
            reponse = input("Entrez votre réponse: ")
            
            correcte, feedback = qb.verifier_reponse(question, reponse)
            if correcte:
                print(f"✅ {feedback}")
            else:
                print(f"❌ {feedback}")
        
        elif choix == "5":
            stats = qb.statistiques()
            print("\n📊 Statistiques:")
            print(f"Total catégories: {stats['total_categories']}")
            print(f"Total questions: {stats['total_questions']}")
            print("\nPar catégorie:")
            for cat, count in stats['categories'].items():
                print(f"  {cat}: {count} questions")
        
        elif choix == "6":
            print("👋 À bientôt!")
            break
        
        else:
            print("❌ Option invalide. Réessayez.")

if __name__ == "__main__":
    interface_interactive()
