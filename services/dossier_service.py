from db.connection import get_connection
from datetime import datetime

class DossierService:
    
    @staticmethod
    def get_all():
        """Récupère tous les dossiers avec informations patients"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT d.id_dossier, d.id_patient, d.observations, d.traitement, d.date_derniere_visite,
                   p.nom || ' ' || p.prenom as patient_nom_complet,
                   p.age
            FROM dossiers d
            JOIN patients p ON d.id_patient = p.id_patient
            ORDER BY d.date_derniere_visite DESC
        """)
        data = cursor.fetchall()
        conn.close()
        return data

    @staticmethod
    def get_by_patient(id_patient):
        """Récupère tout l'historique d'un patient spécifique"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT d.id_dossier, d.id_patient, d.observations, d.traitement, d.date_derniere_visite,
                   p.nom || ' ' || p.prenom as patient_nom_complet,
                   p.age
            FROM dossiers d
            JOIN patients p ON d.id_patient = p.id_patient
            WHERE d.id_patient = ?
            ORDER BY d.date_derniere_visite DESC
        """, (id_patient,))
        data = cursor.fetchall()
        conn.close()
        return data

    @staticmethod
    def add(id_patient, observations, traitement, date_visite):
        """Ajoute une nouvelle entrée au dossier"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO dossiers (id_patient, observations, traitement, date_derniere_visite)
            VALUES (?, ?, ?, ?)
        """, (id_patient, observations, traitement, date_visite))
        conn.commit()
        conn.close()

    @staticmethod
    def update(id_dossier, observations, traitement):
        """Modifie une entrée existante du dossier"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE dossiers
            SET observations = ?, traitement = ?
            WHERE id_dossier = ?
        """, (observations, traitement, id_dossier))
        conn.commit()
        conn.close()

    @staticmethod
    def delete(id_dossier):
        """Supprime une entrée du dossier"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM dossiers WHERE id_dossier = ?", (id_dossier,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_patients_with_dossiers():
        """Liste des patients ayant des dossiers médicaux"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT p.id_patient, p.nom, p.prenom, p.age
            FROM patients p
            JOIN dossiers d ON p.id_patient = d.id_patient
            ORDER BY p.nom
        """)
        data = cursor.fetchall()
        conn.close()
        return data

    @staticmethod
    def search_patients(keyword):
        """Recherche de patients dans les dossiers"""
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            SELECT DISTINCT p.id_patient, p.nom, p.prenom, p.age
            FROM patients p
            JOIN dossiers d ON p.id_patient = d.id_patient
            WHERE p.nom LIKE ? OR p.prenom LIKE ? OR p.telephone LIKE ?
            ORDER BY p.nom
        """
        search_pattern = f"%{keyword}%"
        cursor.execute(query, (search_pattern, search_pattern, search_pattern))
        data = cursor.fetchall()
        conn.close()
        return data