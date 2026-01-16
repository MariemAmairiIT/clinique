# services/patient_service.py
from db.connection import get_connection

class PatientService:
    
    @staticmethod
    def get_all():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients ORDER BY id_patient")
        data = cursor.fetchall()
        conn.close()
        return data

    @staticmethod
    def add(nom, prenom, age, adresse, telephone, antecedents):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO patients (nom, prenom, age, adresse, telephone, antecedents)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (nom, prenom, age, adresse, telephone, antecedents))
        conn.commit()
        conn.close()

    @staticmethod
    def update(id_patient, nom, prenom, age, adresse, telephone, antecedents):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE patients
            SET nom=?, prenom=?, age=?, adresse=?, telephone=?, antecedents=?
            WHERE id_patient=?
        """, (nom, prenom, age, adresse, telephone, antecedents, id_patient))
        conn.commit()
        conn.close()

    @staticmethod
    def delete(id_patient):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM patients WHERE id_patient=?", (id_patient,))
        conn.commit()
        conn.close()
        
        # Réorganiser les IDs après suppression
        PatientService.reorder_ids()

    @staticmethod
    def reorder_ids():
        """
        Réorganise tous les IDs pour qu'ils soient séquentiels (1, 2, 3, 4...)
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            # 1. Récupérer tous les patients triés par ID actuel
            cursor.execute("SELECT id_patient, nom, prenom, age, adresse, telephone, antecedents FROM patients ORDER BY id_patient")
            patients = cursor.fetchall()
            
            if not patients:
                conn.close()
                return
            
            # 2. Créer une table temporaire pour stocker les données
            cursor.execute("DROP TABLE IF EXISTS patients_temp")
            cursor.execute("""
                CREATE TABLE patients_temp (
                    id_patient INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom TEXT NOT NULL,
                    prenom TEXT NOT NULL,
                    age INTEGER NOT NULL,
                    adresse TEXT NOT NULL,
                    telephone TEXT,
                    antecedents TEXT
                )
            """)
            
            # 3. Insérer les patients dans la table temporaire (les IDs seront réorganisés automatiquement)
            for patient in patients:
                cursor.execute(
                    """INSERT INTO patients_temp (nom, prenom, age, adresse, telephone, antecedents) 
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (patient[1], patient[2], patient[3], patient[4], patient[5], patient[6])
                )
            
            # 4. Supprimer l'ancienne table et renommer la temporaire
            cursor.execute("DROP TABLE patients")
            cursor.execute("ALTER TABLE patients_temp RENAME TO patients")
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def search(keyword):
        """
        Recherche des patients par nom, prénom, adresse ou téléphone
        """
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            SELECT * FROM patients 
            WHERE nom LIKE ? OR prenom LIKE ? OR adresse LIKE ? OR telephone LIKE ?
            ORDER BY id_patient
        """
        search_pattern = f"%{keyword}%"
        cursor.execute(query, (search_pattern, search_pattern, search_pattern, search_pattern))
        data = cursor.fetchall()
        conn.close()
        return data