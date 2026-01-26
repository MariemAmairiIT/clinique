import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowLeft } from "lucide-react";

import {
  getDossiersByPatient,
  getRendezvous,
  addDossier,
  updateDossier,
  deleteDossier,
} from "../api/api";

export default function DossierDetail() {
  const { id_patient } = useParams();
  const navigate = useNavigate();

  const [observations, setObservations] = useState([]);
  const [rendezvous, setRendezvous] = useState([]);
  const [editId, setEditId] = useState(null);

  const [form, setForm] = useState({
    observations: "",
    traitement: "",
    date_derniere_visite: new Date().toISOString().split("T")[0],
  });

  const load = async () => {
    setObservations(await getDossiersByPatient(id_patient));
    setRendezvous(
      (await getRendezvous()).filter(r => r.id_patient == id_patient)
    );
  };

  useEffect(() => {
    load();
  }, []);

  const handleSave = async () => {
    if (editId) {
      await updateDossier(editId, { ...form, id_patient: Number(id_patient) });
      setEditId(null);
    } else {
      await addDossier({ ...form, id_patient: Number(id_patient) });
    }

    setForm({
      observations: "",
      traitement: "",
      date_derniere_visite: new Date().toISOString().split("T")[0],
    });

    load();
  };

  const handleEdit = (o) => {
    setEditId(o.id_dossier);
    setForm({
      observations: o.observations,
      traitement: o.traitement,
      date_derniere_visite: o.date_derniere_visite,
    });
  };

  /* particles */
  const particles = Array.from({ length: 50 }, (_, i) => ({
    id: i,
    x: Math.random() * 100,
    y: Math.random() * 100,
    size: Math.random() * 4 + 1,
    delay: Math.random() * 5,
  }));

  return (
    <div className="relative min-h-screen p-10 bg-gradient-to-tr from-blue-900 via-blue-400 to-indigo-600 overflow-hidden">

      {/* particles */}
      {particles.map(p => (
        <motion.div
          key={p.id}
          className="absolute rounded-full bg-white/30"
          style={{
            width: p.size,
            height: p.size,
            top: `${p.y}%`,
            left: `${p.x}%`,
          }}
          animate={{ y: [0, -30, 0], opacity: [0.2, 0.8, 0.2] }}
          transition={{ repeat: Infinity, duration: 4 + p.delay }}
        />
      ))}

      {/* Header */}
      <motion.div
        initial={{ y: -40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="flex justify-between items-center mb-10"
      >
        <h1 className="text-5xl font-extrabold text-white drop-shadow">
          📂 Dossier Médical
        </h1>

        <button onClick={() => navigate("/dossiers")} className="flex items-center gap-2 mb-8 bg-white/20 px-6 py-3 rounded-xl">
        <ArrowLeft /> Dossiers
      </button>
      </motion.div>

      {/* Rendez-vous */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white/20 backdrop-blur-xl rounded-2xl shadow-xl p-6 mb-8"
      >
        <h2 className="text-xl font-bold text-white mb-4">
          🗓️ Historique des rendez-vous
        </h2>

        {rendezvous.length === 0 && (
          <p className="text-white/70 italic">Aucun rendez-vous</p>
        )}

        <ul className="space-y-2">
          {rendezvous.map(r => (
            <li
              key={r.id_rdv}
              className="bg-white/80 p-3 rounded-xl"
            >
              <strong>{r.date_rdv}</strong> à {r.heure_rdv} — {r.motif}
            </li>
          ))}
        </ul>
      </motion.div>

      {/* Observations */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white/20 backdrop-blur-xl rounded-2xl shadow-xl p-6"
      >
        <h2 className="text-xl font-bold text-white mb-4">
          🧠 Observations médicales
        </h2>

        {observations.length === 0 && (
          <p className="text-white/70 italic mb-4">
            Aucun contenu médical
          </p>
        )}

        <div className="space-y-4 mb-6">
          {observations.map(o => (
            <motion.div
              key={o.id_dossier}
              whileHover={{ scale: 1.02 }}
              className="bg-white/90 p-4 rounded-xl shadow"
            >
              <p className="text-sm text-gray-500">
                📅 {o.date_derniere_visite}
              </p>

              <p><strong>Observation :</strong> {o.observations}</p>
              <p><strong>Traitement :</strong> {o.traitement}</p>

              <div className="flex gap-4 mt-3">
                <button
                  onClick={() => handleEdit(o)}
                  className="text-blue-600 font-semibold"
                >
                  ✏️ Modifier
                </button>

                <button
                  onClick={() =>
                    confirm("Supprimer cette observation ?") &&
                    deleteDossier(o.id_dossier).then(load)
                  }
                  className="text-red-500 font-semibold"
                >
                  🗑️ Supprimer
                </button>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Form */}
        <div className="border-t border-white/30 pt-4">
          <h3 className="font-bold text-lg text-white mb-3">
            {editId ? "✏️ Modifier observation" : "➕ Nouvelle observation"}
          </h3>

          <input
            type="date"
            className="w-full p-2 rounded mb-2"
            value={form.date_derniere_visite}
            onChange={e => setForm({ ...form, date_derniere_visite: e.target.value })}
          />

          <textarea
            className="w-full p-2 rounded mb-2"
            placeholder="Observation médicale"
            value={form.observations}
            onChange={e => setForm({ ...form, observations: e.target.value })}
          />

          <textarea
            className="w-full p-2 rounded mb-4"
            placeholder="Traitement"
            value={form.traitement}
            onChange={e => setForm({ ...form, traitement: e.target.value })}
          />

          <button
            onClick={handleSave}
            className={`w-full py-3 rounded-xl text-white font-bold transition ${
              editId
                ? "bg-blue-600 hover:bg-blue-700"
                : "bg-green-500 hover:bg-green-600"
            }`}
          >
            {editId ? "💾 Enregistrer" : "➕ Ajouter"}
          </button>
        </div>
      </motion.div>
    </div>
  );
}
