from db.connection import get_connection

class MedecinService:

    @staticmethod
    def get_all():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM medecins")
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
