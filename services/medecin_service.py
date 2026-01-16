# services/medecin_service.py
from db.connection import get_connection

class MedecinService:

    @staticmethod
    def get_all():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM medecins ORDER BY id_medecin")
        data = cursor.fetchall()
        conn.close()
        return data

    @staticmethod
    def add(nom, specialite, telephone):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO medecins (nom, specialite, telephone) VALUES (?, ?, ?)",
            (nom, specialite, telephone)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def update(id_medecin, nom, specialite, telephone):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE medecins
            SET nom=?, specialite=?, telephone=?
            WHERE id_medecin=?
        """, (nom, specialite, telephone, id_medecin))
        conn.commit()
        conn.close()

    @staticmethod
    def delete(id_medecin):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM medecins WHERE id_medecin=?",
            (id_medecin,)
        )
        conn.commit()
        conn.close()
        
        # Réorganiser les IDs après suppression
        MedecinService.reorder_ids()

    @staticmethod
    def reorder_ids():
        """
        Réorganise tous les IDs pour qu'ils soient séquentiels (1, 2, 3, 4...)
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            # 1. Récupérer tous les médecins triés par ID actuel
            cursor.execute("SELECT id_medecin, nom, specialite, telephone FROM medecins ORDER BY id_medecin")
            medecins = cursor.fetchall()
            
            if not medecins:
                conn.close()
                return
            
            # 2. Créer une table temporaire pour stocker les données
            cursor.execute("DROP TABLE IF EXISTS medecins_temp")
            cursor.execute("""
                CREATE TABLE medecins_temp (
                    id_medecin INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom TEXT NOT NULL,
                    specialite TEXT NOT NULL,
                    telephone TEXT
                )
            """)
            
            # 3. Insérer les médecins dans la table temporaire (les IDs seront réorganisés automatiquement)
            for med in medecins:
                cursor.execute(
                    "INSERT INTO medecins_temp (nom, specialite, telephone) VALUES (?, ?, ?)",
                    (med[1], med[2], med[3])
                )
            
            # 4. Supprimer l'ancienne table et renommer la temporaire
            cursor.execute("DROP TABLE medecins")
            cursor.execute("ALTER TABLE medecins_temp RENAME TO medecins")
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    # AJOUTER CETTE MÉTHODE DE RECHERCHE
    @staticmethod
    def search(keyword):
        """
        Recherche des médecins par nom, spécialité ou téléphone
        """
        conn = get_connection()
        cursor = conn.cursor()
        # Recherche dans tous les champs pertinents
        query = """
            SELECT * FROM medecins 
            WHERE nom LIKE ? OR specialite LIKE ? OR telephone LIKE ?
            ORDER BY id_medecin
        """
        # Ajout des wildcards pour la recherche partielle
        search_pattern = f"%{keyword}%"
        cursor.execute(query, (search_pattern, search_pattern, search_pattern))
        data = cursor.fetchall()
        conn.close()
        return data