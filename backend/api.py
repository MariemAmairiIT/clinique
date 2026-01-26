from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from services.patient_service import PatientService
from services.medecin_service import MedecinService
from services.dossier_service import DossierService
from services.rendezvous_service import RendezVousService
from services.report_service import ReportService

app = FastAPI(title="Clinique API")

origins = [
    "http://localhost:5173",  # Vite dev server
    "http://127.0.0.1:5173",  # fallback
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # autoriser le frontend
    allow_credentials=True,
    allow_methods=["*"],          # autoriser GET, POST, PUT, DELETE
    allow_headers=["*"],          # autoriser tous les headers
)
# ------------------ MODELS ------------------
class PatientIn(BaseModel):
    nom: str
    prenom: str
    age: int
    adresse: str
    telephone: str = ""
    antecedents: str = ""

class MedecinIn(BaseModel):
    nom: str
    specialite: str
    telephone: str = ""

class DossierIn(BaseModel):
    id_patient: int
    observations: str
    traitement: str
    date_derniere_visite: str  # "yyyy-MM-dd"

class RendezVousIn(BaseModel):
    id_patient: int
    id_medecin: int
    date_rdv: str  # "yyyy-MM-dd"
    heure_rdv: str  # "HH:mm"
    motif: str

# ------------------ PATIENTS ------------------
@app.get("/patients")
def get_patients():
    return PatientService.get_all()

@app.post("/patients")
def add_patient(p: PatientIn):
    PatientService.add(p.nom, p.prenom, p.age, p.adresse, p.telephone, p.antecedents)
    return {"message": "Patient added"}

@app.put("/patients/{id_patient}")
def update_patient(id_patient: int, p: PatientIn):
    PatientService.update(id_patient, p.nom, p.prenom, p.age, p.adresse, p.telephone, p.antecedents)
    return {"message": "Patient updated"}

@app.delete("/patients/{id_patient}")
def delete_patient(id_patient: int):
    PatientService.delete(id_patient)
    return {"message": "Patient deleted"}

# ------------------ MEDECINS ------------------
@app.get("/medecins")
def api_get_medecins():
    medecins = MedecinService.get_all()
    return [{"id_medecin": m[0], "nom": m[1], "specialite": m[2], "telephone": m[3]} for m in medecins]

@app.post("/medecins")
def api_add_medecin(m: MedecinIn):
    MedecinService.add(m.nom, m.specialite, m.telephone)
    return {"message": "Médecin ajouté"}

@app.put("/medecins/{id_medecin}")
def api_update_medecin(id_medecin: int, m: MedecinIn):
    MedecinService.update(id_medecin, m.nom, m.specialite, m.telephone)
    return {"message": "Médecin modifié"}

@app.delete("/medecins/{id_medecin}")
def api_delete_medecin(id_medecin: int):
    MedecinService.delete(id_medecin)
    return {"message": "Médecin supprimé"}

@app.get("/medecins/search")
def api_search_medecin(keyword: str):
    results = MedecinService.search(keyword)
    return [{"id_medecin": m[0], "nom": m[1], "specialite": m[2], "telephone": m[3]} for m in results]

# ------------------ DOSSIERS ------------------
@app.get("/dossiers")
def get_dossiers():
    data = DossierService.get_all()
    return [
        {
            "id_dossier": d[0],
            "id_patient": d[1],
            "observations": d[2],
            "traitement": d[3],
            "date_derniere_visite": d[4],
            "patient_nom_complet": d[5],
            "age": d[6]
        }
        for d in data
    ]

@app.get("/dossiers/patient/{id_patient}")
def get_dossiers_by_patient(id_patient: int):
    data = DossierService.get_by_patient(id_patient)
    return [
        {
            "id_dossier": d[0],
            "id_patient": d[1],
            "observations": d[2],
            "traitement": d[3],
            "date_derniere_visite": d[4],
            "patient_nom_complet": d[5],
            "age": d[6]
        }
        for d in data
    ]

@app.post("/dossiers")
def add_dossier(d: DossierIn):
    DossierService.add(d.id_patient, d.observations, d.traitement, d.date_derniere_visite)
    return {"message": "Dossier ajouté"}

@app.put("/dossiers/{id_dossier}")
def update_dossier(id_dossier: int, d: DossierIn):
    DossierService.update(id_dossier, d.observations, d.traitement)
    return {"message": "Dossier modifié"}

@app.delete("/dossiers/{id_dossier}")
def delete_dossier(id_dossier: int):
    DossierService.delete(id_dossier)
    return {"message": "Dossier supprimé"}

@app.get("/dossiers/search")
def search_dossiers(keyword: str):
    patients = DossierService.search_patients(keyword)
    results = []
    for p in patients:
        dossiers = DossierService.get_by_patient(p[0])
        for d in dossiers:
            results.append({
                "id_dossier": d[0],
                "id_patient": d[1],
                "observations": d[2],
                "traitement": d[3],
                "date_derniere_visite": d[4],
                "patient_nom_complet": d[5],
                "age": d[6]
            })
    return results

# ------------------ RENDEZ-VOUS ------------------
@app.get("/rendezvous")
def get_rendezvous():
    return RendezVousService.get_all()

@app.post("/rendezvous")
def add_rendezvous(r: RendezVousIn):
    RendezVousService.add(r.id_patient, r.id_medecin, r.date_rdv, r.heure_rdv, r.motif)
    return {"message": "Rendez-vous ajouté"}

@app.put("/rendezvous/{id_rdv}")
def update_rendezvous(id_rdv: int, r: RendezVousIn):
    RendezVousService.update(id_rdv, r.id_patient, r.id_medecin, r.date_rdv, r.heure_rdv, r.motif)
    return {"message": "Rendez-vous modifié"}

@app.delete("/rendezvous/{id_rdv}")
def delete_rendezvous(id_rdv: int):
    RendezVousService.delete(id_rdv)
    return {"message": "Rendez-vous supprimé"}

@app.get("/rendezvous/search")
def search_rendezvous(keyword: str):
    data = RendezVousService.search_all(keyword)
    return data

@app.get("/rendezvous/{id_rdv}")
def get_rendezvous_by_id(id_rdv: int):
    rdv = RendezVousService.get_by_id(id_rdv)
    if not rdv:
        raise HTTPException(status_code=404, detail="Rendez-vous non trouvé")
    return rdv

@app.get("/rendezvous/available")
def check_medecin_available(id_medecin: int, date_rdv: str, heure_rdv: str, exclude_rdv_id: int = None):
    available = RendezVousService.is_medecin_available(id_medecin, date_rdv, heure_rdv, exclude_rdv_id)
    return {"available": available}


@app.get("/reports/statistics")
async def get_reports_statistics():
    """Retourne toutes les statistiques de la clinique pour le frontend"""
    stats = ReportService.get_clinic_statistics()
    # Convert tuples to lists for JSON serialization
    stats['specialites'] = [list(t) for t in stats.get('specialites', [])]
    stats['derniers_rdv'] = [list(t) for t in stats.get('derniers_rdv', [])]
    stats['rdv_par_mois'] = [list(t) for t in stats.get('rdv_par_mois', [])]
    stats['prochains_rdv'] = [list(t) for t in stats.get('prochains_rdv', [])]
    stats['liste_medecins'] = [list(t) for t in stats.get('liste_medecins', [])]
    return stats