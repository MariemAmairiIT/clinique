import axios from "axios";

// Axios instance
const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

// -------------------- PATIENTS -------------------- //
export const getPatients = async () => {
  const res = await API.get("/patients");
  return res.data;
};

export const addPatient = async (data) => {
  const res = await API.post("/patients", data);
  return res.data;
};

export const updatePatient = async (id, data) => {
  const res = await API.put(`/patients/${id}`, data);
  return res.data;
};

export const deletePatient = async (id) => {
  const res = await API.delete(`/patients/${id}`);
  return res.data;
};

// -------------------- MEDECINS -------------------- //
export const getMedecins = async () => {
  const res = await API.get("/medecins");
  return res.data;
};

export const addMedecin = async (data) => {
  const res = await API.post("/medecins", data);
  return res.data;
};

export const updateMedecin = async (id, data) => {
  const res = await API.put(`/medecins/${id}`, data);
  return res.data;
};

export const deleteMedecin = async (id) => {
  const res = await API.delete(`/medecins/${id}`);
  return res.data;
};

export const searchMedecin = async (keyword) => {
  const res = await API.get(`/medecins/search?keyword=${keyword}`);
  return res.data;
};
// -------------------- DOSSIERS -------------------- //
export const getDossiers = async () => {
  const res = await API.get("/dossiers");
  return res.data;
};

export const getDossiersByPatient = async (id) => {
  const res = await API.get(`/dossiers/patient/${id}`);
  return res.data;
};

export const addDossier = async (data) => {
  const res = await API.post("/dossiers", data);
  return res.data;
};

export const updateDossier = async (id, data) => {
  const res = await API.put(`/dossiers/${id}`, data);
  return res.data;
};

export const deleteDossier = async (id) => {
  const res = await API.delete(`/dossiers/${id}`);
  return res.data;
};

export const searchDossiers = async (keyword) => {
  const res = await API.get(`/dossiers/search?keyword=${keyword}`);
  return res.data;
};

// -------------------- RENDEZVOUS -------------------- //
export const getRendezvous = async () => {
  const res = await API.get("/rendezvous");
  return res.data;
};

export const addRendezvous = async (data) => {
  const res = await API.post("/rendezvous", data);
  return res.data;
};

export const updateRendezvous = async (id, data) => {
  const res = await API.put(`/rendezvous/${id}`, data);
  return res.data;
};

export const deleteRendezvous = async (id) => {
  const res = await API.delete(`/rendezvous/${id}`);
  return res.data;
};

export const searchRendezvous = async (keyword) => {
  const res = await API.get(`/rendezvous/search?keyword=${keyword}`);
  return res.data;
};

export const getRendezvousById = async (id) => {
  const res = await API.get(`/rendezvous/${id}`);
  return res.data;
};

export const checkMedecinAvailable = async (id_medecin, date_rdv, heure_rdv, exclude_rdv_id) => {
  const res = await API.get(
    `/rendezvous/available?id_medecin=${id_medecin}&date_rdv=${date_rdv}&heure_rdv=${heure_rdv}${exclude_rdv_id ? `&exclude_rdv_id=${exclude_rdv_id}` : ""}`
  );
  return res.data;
};
// Reports / Statistics
export const getClinicStats = async () => {
  const res = await API.get("/reports/statistics");
  return res.data;
};
