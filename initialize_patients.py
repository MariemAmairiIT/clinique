# initialize_patients.py
"""
Script pour initialiser la base de données avec des patients de test.
À exécuter UNE SEULE FOIS.
"""

import sys
import os

# Ajouter le répertoire parent au chemin pour pouvoir importer les modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.patient_service import PatientService

# Liste des patients à ajouter
PATIENTS = [
    # (nom, prenom, age, adresse, telephone, antecedents)
    ("Dubois", "Sophie", 28, "25 Rue de la République, Paris", "0612345678", "Asthme léger, Allergie aux acariens"),
    ("Martin", "Jean", 45, "14 Avenue des Champs-Élysées, Lyon", "0623456789", "Hypertension artérielle"),
    ("Bernard", "Marie", 32, "8 Rue du Commerce, Marseille", "0634567890", "Migraines chroniques"),
    ("Petit", "Pierre", 56, "32 Boulevard Saint-Germain, Paris", "0645678901", "Diabète type 2, Cholestérol"),
    ("Robert", "Claire", 29, "19 Rue de la Paix, Lille", "0656789012", "Aucun"),
    ("Richard", "Thomas", 38, "7 Place Bellecour, Lyon", "0667890123", "Chirurgie du genou (2019)"),
    ("Durand", "Anne", 42, "56 Rue de Rivoli, Toulouse", "0678901234", "Dépression légère sous traitement"),
    ("Simon", "Luc", 61, "3 Cours Gambetta, Bordeaux", "0689012345", "Hypertension, Arthrose"),
    ("Laurent", "Isabelle", 27, "41 Rue du Bac, Nantes", "0690123456", "Allergie aux pénicillines"),
    ("Moreau", "Philippe", 50, "12 Avenue Foch, Nice", "0601234567", "Tabagisme (arrêté en 2022)"),
    ("Garcia", "Elena", 33, "9 Rue de la Pompe, Strasbourg", "0612345679", "Grossesse à risque"),
    ("Thomas", "Michel", 47, "27 Boulevard Haussmann, Montpellier", "0623456790", "Apnée du sommeil"),
    ("Sanchez", "Carlos", 39, "15 Rue Royale, Rennes", "0634567901", "Asthme sévère"),
    ("Nguyen", "Linh", 26, "22 Avenue Victor Hugo, Tours", "0645679012", "Anémie ferriprive"),
    ("Rossi", "Marco", 52, "5 Place du Capitole, Toulouse", "0656790123", "Ulcère gastrique"),
    ("Schmidt", "Anna", 31, "18 Rue de Strasbourg, Nancy", "0667901234", "Thyroïdite d'Hashimoto"),
    ("Wilson", "David", 43, "11 Rue des Francs-Bourgeois, Metz", "0679012345", "BPCO légère"),
    ("Chen", "Wei", 35, "6 Rue de la Liberté, Dijon", "0689123456", "Aucun"),
    ("Muller", "Klaus", 58, "14 Rue du Faubourg Saint-Honoré, Paris", "0691234567", "Diabète type 1"),
    ("Ivanova", "Natalia", 30, "8 Rue de la Boétie, Lyon", "0602345678", "Allergie saisonnière (pollens)")
]

def initialize_database():
    """Initialise la base de données avec les patients de test"""
    try:
        print("🔍 Vérification des patients existants...")
        
        # Vérifier si des patients existent déjà
        existing_patients = PatientService.get_all()
        
        if existing_patients and len(existing_patients) > 0:
            print(f"⚠️  {len(existing_patients)} patients existent déjà dans la base.")
            
            response = input("Voulez-vous quand même ajouter les patients de test? (oui/non): ").strip().lower()
            if response not in ['oui', 'o', 'yes', 'y']:
                print("❌ Annulation de l'initialisation.")
                return False
        
        print("📝 Ajout des patients...")
        added_count = 0
        
        for nom, prenom, age, adresse, telephone, antecedents in PATIENTS:
            try:
                PatientService.add(nom, prenom, age, adresse, telephone, antecedents)
                added_count += 1
                print(f"  ✅ Ajouté: {prenom} {nom}")
            except Exception as e:
                print(f"  ❌ Erreur pour {prenom} {nom}: {e}")
        
        print(f"\n🎉 Initialisation terminée!")
        print(f"✅ {added_count}/{len(PATIENTS)} patients ajoutés avec succès.")
        
        # Afficher le total des patients
        total_patients = PatientService.get_all()
        print(f"📊 Total patients dans la base: {len(total_patients)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {e}")
        return False

def display_patients():
    """Affiche la liste des patients actuels"""
    try:
        patients = PatientService.get_all()
        print(f"\n📋 Liste des patients ({len(patients)} au total):")
        print("-" * 80)
        
        for i, patient in enumerate(patients, 1):
            print(f"{i:3}. {patient[1]} {patient[2]} - {patient[3]} ans - {patient[4]}")
        
        print("-" * 80)
    except Exception as e:
        print(f"❌ Erreur lors de l'affichage: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("INITIALISATION DE LA BASE DE DONNÉES PATIENTS")
    print("=" * 60)
    
    # Afficher le menu
    print("\nOptions disponibles:")
    print("1. Initialiser avec les patients de test")
    print("2. Afficher les patients actuels")
    print("3. Quitter")
    
    try:
        choice = input("\nVotre choix (1-3): ").strip()
        
        if choice == "1":
            initialize_database()
        elif choice == "2":
            display_patients()
        elif choice == "3":
            print("👋 Au revoir!")
        else:
            print("❌ Choix invalide.")
    
    except KeyboardInterrupt:
        print("\n\n❌ Opération annulée par l'utilisateur.")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")