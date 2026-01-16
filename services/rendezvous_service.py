from db.connection import get_connection

class RendezVousService:
    
    @staticmethod
    def get_all():
        """
        Récupère tous les rendez-vous avec les informations des patients et médecins
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.id_rdv, r.id_patient, r.id_medecin, r.date_rdv, r.heure_rdv, r.motif,
                   p.nom || ' ' || p.prenom as patient_nom_complet,
                   m.nom as medecin_nom, m.specialite
            FROM rendezvous r
            JOIN patients p ON r.id_patient = p.id_patient
            JOIN medecins m ON r.id_medecin = m.id_medecin
            ORDER BY r.date_rdv DESC, r.heure_rdv DESC
        """)
        data = cursor.fetchall()
        conn.close()
        return data

    @staticmethod
    def add(id_patient, id_medecin, date_rdv, heure_rdv, motif):
        """
        Ajoute un nouveau rendez-vous
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO rendezvous (id_patient, id_medecin, date_rdv, heure_rdv, motif)
            VALUES (?, ?, ?, ?, ?)
        """, (id_patient, id_medecin, date_rdv, heure_rdv, motif))
        conn.commit()
        conn.close()

    @staticmethod
    def update(id_rdv, id_patient, id_medecin, date_rdv, heure_rdv, motif):
        """
        Met à jour un rendez-vous existant
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE rendezvous
            SET id_patient=?, id_medecin=?, date_rdv=?, heure_rdv=?, motif=?
            WHERE id_rdv=?
        """, (id_patient, id_medecin, date_rdv, heure_rdv, motif, id_rdv))
        conn.commit()
        conn.close()

    @staticmethod
    def delete(id_rdv):
        """
        Supprime un rendez-vous
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM rendezvous WHERE id_rdv=?", (id_rdv,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_by_id(id_rdv):
        """
        Récupère un rendez-vous par son ID
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.id_rdv, r.id_patient, r.id_medecin, r.date_rdv, r.heure_rdv, r.motif,
                   p.nom || ' ' || p.prenom as patient_nom_complet,
                   m.nom as medecin_nom
            FROM rendezvous r
            JOIN patients p ON r.id_patient = p.id_patient
            JOIN medecins m ON r.id_medecin = m.id_medecin
            WHERE r.id_rdv = ?
        """, (id_rdv,))
        data = cursor.fetchone()
        conn.close()
        return data

    @staticmethod
    def is_medecin_available(id_medecin, date_rdv, heure_rdv, exclude_rdv_id=None):
        """
        Vérifie si un médecin est disponible à une date et heure donnée
        exclude_rdv_id: ID du rendez-vous à exclure (pour les modifications)
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        if exclude_rdv_id:
            cursor.execute("""
                SELECT COUNT(*) FROM rendezvous 
                WHERE id_medecin = ? AND date_rdv = ? AND heure_rdv = ? AND id_rdv != ?
            """, (id_medecin, date_rdv, heure_rdv, exclude_rdv_id))
        else:
            cursor.execute("""
                SELECT COUNT(*) FROM rendezvous 
                WHERE id_medecin = ? AND date_rdv = ? AND heure_rdv = ?
            """, (id_medecin, date_rdv, heure_rdv))
        
        count = cursor.fetchone()[0]
        conn.close()
        return count == 0

    @staticmethod
    def search_by_name(keyword):
        """
        Recherche des rendez-vous par NOM DE PATIENT uniquement
        """
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            SELECT r.id_rdv, r.id_patient, r.id_medecin, r.date_rdv, r.heure_rdv, r.motif,
                   p.nom || ' ' || p.prenom as patient_nom_complet,
                   m.nom as medecin_nom, m.specialite
            FROM rendezvous r
            JOIN patients p ON r.id_patient = p.id_patient
            JOIN medecins m ON r.id_medecin = m.id_medecin
            WHERE p.nom LIKE ? OR p.prenom LIKE ?
            ORDER BY r.date_rdv DESC, r.heure_rdv DESC
        """
        search_pattern = f"%{keyword}%"
        cursor.execute(query, (search_pattern, search_pattern))
        data = cursor.fetchall()
        conn.close()
        return data

    @staticmethod
    def search_by_date(date_rdv):
        """
        Recherche des rendez-vous par date spécifique
        """
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            SELECT r.id_rdv, r.id_patient, r.id_medecin, r.date_rdv, r.heure_rdv, r.motif,
                   p.nom || ' ' || p.prenom as patient_nom_complet,
                   m.nom as medecin_nom, m.specialite
            FROM rendezvous r
            JOIN patients p ON r.id_patient = p.id_patient
            JOIN medecins m ON r.id_medecin = m.id_medecin
            WHERE r.date_rdv = ?
            ORDER BY r.heure_rdv ASC
        """
        cursor.execute(query, (date_rdv,))
        data = cursor.fetchall()
        conn.close()
        return data

    @staticmethod
    def search_all(keyword):
        """
        Recherche des rendez-vous dans tous les champs (patient, médecin, motif)
        """
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            SELECT r.id_rdv, r.id_patient, r.id_medecin, r.date_rdv, r.heure_rdv, r.motif,
                   p.nom || ' ' || p.prenom as patient_nom_complet,
                   m.nom as medecin_nom, m.specialite
            FROM rendezvous r
            JOIN patients p ON r.id_patient = p.id_patient
            JOIN medecins m ON r.id_medecin = m.id_medecin
            WHERE p.nom LIKE ? OR p.prenom LIKE ? OR m.nom LIKE ? OR r.motif LIKE ?
            ORDER BY r.date_rdv DESC, r.heure_rdv DESC
        """
        search_pattern = f"%{keyword}%"
        cursor.execute(query, (search_pattern, search_pattern, search_pattern, search_pattern))
        data = cursor.fetchall()
        conn.close()
        return data

    @staticmethod
    def get_patients():
        """
        Récupère tous les patients pour les dropdowns
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_patient, nom, prenom FROM patients ORDER BY nom")
        data = cursor.fetchall()
        conn.close()
        return data

    @staticmethod
    def get_medecins():
        """
        Récupère tous les médecins pour les dropdowns
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_medecin, nom, specialite FROM medecins ORDER BY nom")
        data = cursor.fetchall()
        conn.close()
        return data