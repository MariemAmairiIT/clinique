import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Users, ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";
import {
  getPatients,
  addPatient,
  updatePatient,
  deletePatient,
} from "../api/api";

export default function Patients() {
  const [patients, setPatients] = useState([]);
  const [search, setSearch] = useState("");
  const [selectedId, setSelectedId] = useState(null);

  const [form, setForm] = useState({
    nom: "",
    prenom: "",
    age: "",
    adresse: "",
    telephone: "",
    antecedents: "",
  });

  const navigate = useNavigate();

  const particles = Array.from({ length: 70 }, (_, i) => ({
    id: i,
    x: Math.random() * 100,
    y: Math.random() * 100,
    size: Math.random() * 4 + 1,
    delay: Math.random() * 6,
  }));

  const load = async () => setPatients(await getPatients());
  useEffect(() => { load(); }, []);

  const handleSubmit = async () => {
    selectedId
      ? await updatePatient(selectedId, { ...form, age: Number(form.age) })
      : await addPatient({ ...form, age: Number(form.age) });

    setForm({ nom:"", prenom:"", age:"", adresse:"", telephone:"", antecedents:"" });
    setSelectedId(null);
    load();
  };

  const handleSelect = (p) => { setSelectedId(p.id_patient); setForm(p); };
  const handleDelete = async (id) => { await deletePatient(id); load(); };

  const filteredPatients = patients.filter(p =>
    `${p.nom} ${p.prenom} ${p.telephone}`.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="relative min-h-screen p-10 bg-gradient-to-tr from-blue-900 via-blue-500 to-indigo-700 overflow-hidden text-white">

      {/* FLOATING PARTICLES */}
      {particles.map(p => (
        <motion.div
          key={p.id}
          className="absolute rounded-full bg-white/30"
          style={{ width: p.size, height: p.size, top: `${p.y}%`, left: `${p.x}%` }}
          animate={{ y: [0, -30, 0], opacity: [0.2, 0.8, 0.2] }}
          transition={{ duration: 5 + p.delay, repeat: Infinity }}
        />
      ))}

      {/* BACK */}
      <button
        onClick={() => navigate("/")}
        className="flex items-center gap-2 mb-6 px-6 py-3 bg-white/20 rounded-xl backdrop-blur hover:bg-white/30"
      >
        <ArrowLeft /> Accueil
      </button>

      <h1 className="text-5xl font-extrabold text-center mb-10">
        🧑‍⚕️ Gestion Patients
      </h1>

      {/* SEARCH */}
      <input
        placeholder="🔍 Rechercher patient..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="w-full p-3 mb-6 rounded-xl bg-white/10 border border-white/30"
      />

      {/* FORM */}
      <div className="bg-white/10 backdrop-blur-xl p-6 rounded-3xl shadow-xl mb-10">
        <div className="grid md:grid-cols-2 gap-4">
          {Object.keys(form).map(k => (
            <input
              key={k}
              placeholder={k}
              value={form[k]}
              onChange={e => setForm({ ...form, [k]: e.target.value })}
              className="p-3 rounded-xl bg-white/10 border border-white/30"
            />
          ))}
        </div>

        <div className="mt-6 flex gap-4">
          <button onClick={handleSubmit} className="bg-cyan-500 px-6 py-2 rounded-xl">
            {selectedId ? "Modifier" : "Ajouter"}
          </button>
          {selectedId && (
            <button onClick={() => setSelectedId(null)} className="bg-gray-500 px-6 py-2 rounded-xl">
              Annuler
            </button>
          )}
        </div>
      </div>

      {/* CARDS */}
      <div className="grid md:grid-cols-3 gap-6">
        <AnimatePresence>
          {filteredPatients.map((p, i) => (
            <motion.div
              key={p.id_patient}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="relative bg-white/10 backdrop-blur-xl p-6 rounded-3xl shadow-lg"
              onClick={() => handleSelect(p)}
            >
              <button
                onClick={(e) => { e.stopPropagation(); handleDelete(p.id_patient); }}
                className="absolute top-4 right-4 bg-red-500 w-8 h-8 rounded-full"
              >✕</button>

              <Users className="w-10 h-10 mb-3" />
              <h3 className="font-bold text-xl">{p.nom} {p.prenom}</h3>
              <p>📞 {p.telephone}</p>
              <p>📍 {p.adresse}</p>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}
