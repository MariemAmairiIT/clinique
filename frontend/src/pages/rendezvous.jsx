import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import {
  getRendezvous,
  addRendezvous,
  updateRendezvous,
  deleteRendezvous,
} from "../api/api";
import { ArrowLeft } from "lucide-react";

export default function Rendezvous() {
  const navigate = useNavigate();

  const [rendezvous, setRendezvous] = useState([]);
  const [patients, setPatients] = useState([]);
  const [medecins, setMedecins] = useState([]);
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState(
    new Date().toISOString().split("T")[0]
  );
  const [selectedId, setSelectedId] = useState(null);

  const [form, setForm] = useState({
    id_patient: "",
    id_medecin: "",
    date_rdv: "",
    heure_rdv: "",
    motif: "",
  });

  /* ================= LOAD ================= */
  const load = async () => {
    setRendezvous(await getRendezvous());
    setPatients(await fetch("http://127.0.0.1:8000/patients").then(r => r.json()));
    setMedecins(await fetch("http://127.0.0.1:8000/medecins").then(r => r.json()));
  };

  useEffect(() => {
    load();
  }, []);

  /* ================= CONFLICT CHECK ================= */
  const hasConflict = () =>
    rendezvous.some(
      r =>
        r.id_medecin === Number(form.id_medecin) &&
        r.date_rdv === form.date_rdv &&
        r.heure_rdv === form.heure_rdv &&
        r.id_rdv !== selectedId
    );

  /* ================= SUBMIT ================= */
  const handleSubmit = async () => {
    if (!form.id_patient || !form.id_medecin || !form.date_rdv || !form.heure_rdv) {
      alert("⚠️ Veuillez remplir tous les champs !");
      return;
    }

    if (hasConflict()) {
      alert("❌ Médecin déjà occupé à cette heure !");
      return;
    }

    selectedId
      ? await updateRendezvous(selectedId, form)
      : await addRendezvous(form);

    setForm({ id_patient: "", id_medecin: "", date_rdv: "", heure_rdv: "", motif: "" });
    setSelectedId(null);
    load();
  };

  const handleSelect = (r) => {
    setSelectedId(r.id_rdv);
    setForm(r);
  };

  const handleDelete = async (id) => {
    if (confirm("Supprimer ce rendez-vous ?")) {
      await deleteRendezvous(id);
      load();
    }
  };

  /* ================= CALENDAR ================= */
  const year = currentMonth.getFullYear();
  const month = currentMonth.getMonth();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const dayRDV = rendezvous.filter(r => r.date_rdv === selectedDate);

  /* ================= PARTICLES ================= */
  const particles = Array.from({ length: 60 }, (_, i) => ({
    id: i,
    x: Math.random() * 100,
    y: Math.random() * 100,
    size: Math.random() * 4 + 1,
    delay: Math.random() * 6,
  }));

  return (
    <div className="relative min-h-screen p-8 bg-gradient-to-tr from-blue-900 via-blue-400 to-indigo-600 overflow-hidden text-white">

      {/* FLOATING PARTICLES */}
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
          animate={{
            y: [0, -30, 0],
            x: [0, 15, 0],
            opacity: [0.2, 0.8, 0.2],
          }}
          transition={{
            repeat: Infinity,
            duration: 4 + p.delay,
            delay: p.delay,
          }}
        />
      ))}
      {/* BACK BUTTON */}
      <button onClick={() => navigate("/")} className="flex items-center gap-2 mb-8 bg-white/20 px-6 py-3 rounded-xl">
        <ArrowLeft /> Accueil
      </button>
      {/* HEADER */}
      <div className="flex items-center justify-between mb-8 relative z-10">
        <h1 className="text-4xl items-center font-bold">🗓️ Gestion des Rendez-vous</h1>

        
      </div>
        
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 relative z-10">

        {/* CALENDAR */}
        <div className="bg-white/20 backdrop-blur-xl rounded-2xl p-6 shadow-xl">
          <div className="flex justify-between items-center mb-4">
            <button
              onClick={() => setCurrentMonth(new Date(year, month - 1, 1))}
              className="px-3 py-1 bg-white/20 rounded-lg"
            >◀</button>

            <h2 className="text-xl font-semibold capitalize">
              {currentMonth.toLocaleString("fr", { month: "long", year: "numeric" })}
            </h2>

            <button
              onClick={() => setCurrentMonth(new Date(year, month + 1, 1))}
              className="px-3 py-1 bg-white/20 rounded-lg"
            >▶</button>
          </div>

          <div className="grid grid-cols-7 gap-2">
            {[...Array(daysInMonth)].map((_, i) => {
              const date = `${year}-${String(month + 1).padStart(2, "0")}-${String(i + 1).padStart(2, "0")}`;
              const count = rendezvous.filter(r => r.date_rdv === date).length;

              return (
                <motion.button
                  key={date}
                  whileHover={{ scale: 1.1 }}
                  onClick={() => setSelectedDate(date)}
                  className={`relative p-3 rounded-xl text-sm
                    ${selectedDate === date
                      ? "bg-cyan-400 text-black"
                      : "bg-white/20 hover:bg-white/30"}`}
                >
                  {i + 1}
                  {count > 0 && (
                    <span className="absolute bottom-1 right-1 w-2 h-2 bg-red-400 rounded-full"></span>
                  )}
                </motion.button>
              );
            })}
          </div>
        </div>

        {/* LIST + FORM */}
        <div className="lg:col-span-2 space-y-6">

          {/* LIST */}
          <div className="bg-white/20 backdrop-blur-xl rounded-2xl p-6 shadow-xl">
            <h2 className="text-xl font-semibold mb-4">
              📌 Rendez-vous du {selectedDate}
            </h2>

            {dayRDV.length === 0 && <p className="opacity-70">Aucun rendez-vous</p>}

            <ul className="space-y-3">
              {dayRDV.map(r => (
                <li
                  key={r.id_rdv}
                  className="flex justify-between items-center bg-white/20 p-4 rounded-xl"
                >
                  <div>
                    <p className="font-semibold">{r.patient_nom_complet}</p>
                    <p className="text-sm opacity-80">
                      {r.medecin_nom} — {r.heure_rdv}
                    </p>
                  </div>

                  <div className="flex gap-3">
                    <button onClick={() => handleSelect(r)} className="text-cyan-300">✎</button>
                    <button onClick={() => handleDelete(r.id_rdv)} className="text-red-400">✕</button>
                  </div>
                </li>
              ))}
            </ul>
          </div>

          {/* FORM */}
          <div className="bg-white/20 backdrop-blur-xl rounded-2xl p-6 shadow-xl">
            <h2 className="text-xl font-semibold mb-4">
              {selectedId ? "✏️ Modifier RDV" : "➕ Nouveau RDV"}
            </h2>

            <div className="grid md:grid-cols-3 gap-4">
              <select
                value={form.id_patient}
                onChange={e => setForm({ ...form, id_patient: e.target.value })}
                className="p-3 rounded-xl text-black"
              >
                <option value="">Patient</option>
                {patients.map(p => (
                  <option key={p.id_patient} value={p.id_patient}>
                    {p.nom} {p.prenom}
                  </option>
                ))}
              </select>

              <select
                value={form.id_medecin}
                onChange={e => setForm({ ...form, id_medecin: e.target.value })}
                className="p-3 rounded-xl text-black"
              >
                <option value="">Médecin</option>
                {medecins.map(m => (
                  <option key={m.id_medecin} value={m.id_medecin}>
                    {m.nom}
                  </option>
                ))}
              </select>

              <input
                type="date"
                value={form.date_rdv}
                onChange={e => setForm({ ...form, date_rdv: e.target.value })}
                className="p-3 rounded-xl text-black"
              />

              <input
                type="time"
                value={form.heure_rdv}
                onChange={e => setForm({ ...form, heure_rdv: e.target.value })}
                className="p-3 rounded-xl text-black"
              />

              <input
                placeholder="Motif"
                value={form.motif}
                onChange={e => setForm({ ...form, motif: e.target.value })}
                className="p-3 rounded-xl text-black md:col-span-2"
              />
            </div>

            <button
              onClick={handleSubmit}
              className="mt-6 bg-cyan-400 text-black px-8 py-3 rounded-xl font-semibold hover:bg-cyan-300"
            >
              {selectedId ? "Modifier" : "Ajouter"}
            </button>
          </div>

        </div>
      </div>
    </div>
  );
}
