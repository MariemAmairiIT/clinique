from db.connection import get_connection

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # Patients
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id_patient INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        prenom TEXT NOT NULL,
        age INTEGER,
        adresse TEXT,
        telephone TEXT,
        antecedents TEXT
    )
    """)

    # Medecins
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS medecins (
        id_medecin INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        specialite TEXT NOT NULL,
        telephone TEXT
    )
    """)

    # Rendez-vous
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rendezvous (
        id_rdv INTEGER PRIMARY KEY AUTOINCREMENT,
        id_patient INTEGER,
        id_medecin INTEGER,
        date_rdv TEXT,
        heure_rdv TEXT,
        motif TEXT,
        FOREIGN KEY(id_patient) REFERENCES patients(id_patient),
        FOREIGN KEY(id_medecin) REFERENCES medecins(id_medecin)
    )
    """)

    # Dossiers médicaux
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dossiers (
        id_dossier INTEGER PRIMARY KEY AUTOINCREMENT,
        id_patient INTEGER,
        observations TEXT,
        traitement TEXT,
        date_derniere_visite TEXT,
        FOREIGN KEY(id_patient) REFERENCES patients(id_patient)
    )
    """)

    conn.commit()
    conn.close()

create_tables()
