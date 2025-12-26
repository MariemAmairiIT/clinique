# services/patient_service.py
from db.connection import get_connection

def ajouter_patient(nom, prenom, age, adresse, telephone, antecedents):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO patients (nom, prenom, age, adresse, telephone, antecedents)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (nom, prenom, age, adresse, telephone, antecedents))
    conn.commit()
    conn.close()

def get_all_patients():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_patient, nom, prenom, age, adresse, telephone, antecedents FROM patients")
    result = cursor.fetchall()
    conn.close()
    return result

def modifier_patient(id_patient, nom, prenom, age, adresse, telephone, antecedents):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE patients
        SET nom=?, prenom=?, age=?, adresse=?, telephone=?, antecedents=?
        WHERE id_patient=?
    """, (nom, prenom, age, adresse, telephone, antecedents, id_patient))
    conn.commit()
    conn.close()

def supprimer_patient(id_patient):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM patients WHERE id_patient=?", (id_patient,))
    conn.commit()
    conn.close()
