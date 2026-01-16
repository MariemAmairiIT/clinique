# initialize_medecins.py
"""
Script pour initialiser la base de données avec des médecins de test.
À exécuter UNE SEULE FOIS.
"""

import sys
import os

# Ajouter le répertoire parent au chemin pour pouvoir importer les modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.medecin_service import MedecinService

# Liste des médecins à ajouter
MEDECINS = [
    # (nom_complet, specialite, telephone)
    ("Dr. Jean Martin", "Cardiologie", "+216 71 123 45 67"),
    ("Dr. Sophie Dubois", "Pédiatrie", "+216 71 234 56 78"),
    ("Dr. Pierre Laurent", "Chirurgie", "+216 71 345 67 89"),
    ("Dr. Marie Robert", "Gynécologie", "+216 71 456 78 90"),
    ("Dr. Thomas Bernard", "Dermatologie", "+216 71 567 89 01"),
    ("Dr. Claire Petit", "Neurologie", "+216 71 678 90 12"),
    ("Dr. Antoine Richard", "Orthopédie", "+216 71 789 01 23"),
    ("Dr. Émilie Durand", "Psychiatrie", "+216 71 890 12 34"),
    ("Dr. Philippe Moreau", "Ophtalmologie", "+216 71 901 23 45"),
    ("Dr. Catherine Simon", "Médecine générale", "+216 71 012 34 56")
]

def initialize_medecins():
    """Initialise la base de données avec les médecins de test"""
    try:
        print("🔍 Vérification des médecins existants...")
        
        # Vérifier si des médecins existent déjà
        existing_medecins = MedecinService.get_all()
        
        if existing_medecins and len(existing_medecins) > 0:
            print(f"⚠️  {len(existing_medecins)} médecins existent déjà dans la base.")
            
            response = input("Voulez-vous quand même ajouter les médecins de test? (oui/non): ").strip().lower()
            if response not in ['oui', 'o', 'yes', 'y']:
                print("❌ Annulation de l'initialisation.")
                return False
        
        print("📝 Ajout des médecins...")
        added_count = 0
        
        for nom, specialite, telephone in MEDECINS:
            try:
                MedecinService.add(nom, specialite, telephone)
                added_count += 1
                print(f"  ✅ Ajouté: {nom} - {specialite}")
            except Exception as e:
                print(f"  ❌ Erreur pour {nom}: {e}")
        
        print(f"\n🎉 Initialisation terminée!")
        print(f"✅ {added_count}/{len(MEDECINS)} médecins ajoutés avec succès.")
        
        # Afficher le total des médecins
        total_medecins = MedecinService.get_all()
        print(f"📊 Total médecins dans la base: {len(total_medecins)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {e}")
        return False

def display_medecins():
    """Affiche la liste des médecins actuels"""
    try:
        medecins = MedecinService.get_all()
        print(f"\n📋 Liste des médecins ({len(medecins)} au total):")
        print("-" * 80)
        
        for i, med in enumerate(medecins, 1):
            print(f"{i:3}. {med[1]} - {med[2]} - {med[3]}")
        
        print("-" * 80)
    except Exception as e:
        print(f"❌ Erreur lors de l'affichage: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("INITIALISATION DE LA BASE DE DONNÉES MÉDECINS")
    print("=" * 60)
    
    # Afficher le menu
    print("\nOptions disponibles:")
    print("1. Initialiser avec les médecins de test")
    print("2. Afficher les médecins actuels")
    print("3. Quitter")
    
    try:
        choice = input("\nVotre choix (1-3): ").strip()
        
        if choice == "1":
            initialize_medecins()
        elif choice == "2":
            display_medecins()
        elif choice == "3":
            print("👋 Au revoir!")
        else:
            print("❌ Choix invalide.")
    
    except KeyboardInterrupt:
        print("\n\n❌ Opération annulée par l'utilisateur.")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")