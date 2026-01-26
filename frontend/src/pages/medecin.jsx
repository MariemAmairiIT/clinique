import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Stethoscope,
  Phone,
  UserRound,
  Trash2,
  Edit3,
  ArrowLeft,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { getMedecins, deleteMedecin } from "../api/api";

export default function Medecins() {
  const [medecins, setMedecins] = useState([]);
  const [search, setSearch] = useState("");
  const [selectedId, setSelectedId] = useState(null);

  const [form, setForm] = useState({
    nom: "",
    specialite: "",
    telephone: "",
  });

  const navigate = useNavigate();

  const load = async () => {
    const data = await getMedecins();
    setMedecins(data);
  };

  useEffect(() => {
    load();
  }, []);

  const handleSubmit = async () => {
    const method = selectedId ? "PUT" : "POST";
    const url = selectedId
      ? `http://127.0.0.1:8000/medecins/${selectedId}`
      : `http://127.0.0.1:8000/medecins`;

    await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    });

    setForm({ nom: "", specialite: "", telephone: "" });
    setSelectedId(null);
    load();
  };

  const handleSelect = (m) => {
    setSelectedId(m.id_medecin);
    setForm(m);
  };

  const handleDelete = async (id) => {
    if (confirm("Supprimer ce médecin ?")) {
      await deleteMedecin(id);
      load();
    }
  };

  const filtered = medecins.filter((m) =>
    `${m.nom} ${m.specialite} ${m.telephone}`
      .toLowerCase()
      .includes(search.toLowerCase())
  );

  return (
    <div className="min-h-screen p-10 bg-gradient-to-br from-blue-800 via-sky-200 to-cyan-200">
      
      {/* TOP BAR */}
      <div className="flex items-center justify-between mb-10">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="flex items-center gap-4"
        >
          <div className="p-4 bg-blue-500 rounded-2xl shadow-lg">
            <Stethoscope className="text-white w-8 h-8" />
          </div>
          <h1 className="text-4xl font-extrabold text-blue-50 via-blue-800 to-indigo-600 bg-clip-text text-transparent bg-gradient-to-r">
            Équipe Médicale
          </h1>
        </motion.div>

        {/* BACK HOME BUTTON */}
        <motion.button
          whileHover={{ scale: 1.08 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => navigate("/")}
          className="flex items-center gap-2 px-6 py-3 rounded-2xl
            bg-white text-blue-600 font-semibold shadow-md
            hover:bg-blue-50 transition"
        >
          <ArrowLeft className="w-5 h-5" />
          Accueil
        </motion.button>
      </div>

      {/* SEARCH */}
      <input
        placeholder="🔍 Rechercher un médecin..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="w-full mb-8 p-4 rounded-2xl border border-blue-200
          shadow focus:outline-none focus:ring-2 focus:ring-blue-400"
      />

      {/* FORM */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="bg-white rounded-3xl shadow-xl p-6 mb-10"
      >
        <h2 className="text-xl font-bold text-blue-600 mb-4">
          {selectedId ? "Modifier Médecin" : "Ajouter Médecin"}
        </h2>

        <div className="grid md:grid-cols-3 gap-4">
          {Object.keys(form).map((k) => (
            <input
              key={k}
              placeholder={k.charAt(0).toUpperCase() + k.slice(1)}
              value={form[k]}
              onChange={(e) =>
                setForm({ ...form, [k]: e.target.value })
              }
              className="p-3 rounded-xl border border-blue-200
                focus:outline-none focus:ring-2 focus:ring-blue-400"
            />
          ))}
        </div>

        <div className="mt-6 flex gap-4">
          <button
            onClick={handleSubmit}
            className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-xl shadow"
          >
            {selectedId ? "Modifier" : "Ajouter"}
          </button>

          {selectedId && (
            <button
              onClick={() => {
                setForm({ nom: "", specialite: "", telephone: "" });
                setSelectedId(null);
              }}
              className="bg-gray-200 hover:bg-gray-300 px-6 py-2 rounded-xl"
            >
              Annuler
            </button>
          )}
        </div>
      </motion.div>

      {/* MEDECIN CARDS */}
      <div className="grid md:grid-cols-3 gap-6">
        <AnimatePresence>
          {filtered.map((m) => (
            <motion.div
              key={m.id_medecin}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className={`relative bg-white rounded-3xl shadow-lg p-6 border-l-8 
                ${selectedId === m.id_medecin ? "border-blue-500" : "border-cyan-400"}
              `}
            >
              {/* ACTIONS */}
              <div className="absolute top-4 right-4 flex gap-2">
                <button
                  onClick={() => handleSelect(m)}
                  className="p-2 rounded-full bg-blue-100 hover:bg-blue-200"
                >
                  <Edit3 className="w-4 h-4 text-blue-600" />
                </button>
                <button
                  onClick={() => handleDelete(m.id_medecin)}
                  className="p-2 rounded-full bg-red-100 hover:bg-red-200"
                >
                  <Trash2 className="w-4 h-4 text-red-600" />
                </button>
              </div>

              <h3 className="text-xl font-bold text-blue-700 mb-2 flex items-center gap-2">
                <UserRound className="w-5 h-5" />
                Dr. {m.nom}
              </h3>

              <p className="text-gray-600 mb-1">
                🩺 Spécialité : <span className="font-medium">{m.specialite}</span>
              </p>

              <p className="text-gray-600 flex items-center gap-2">
                <Phone className="w-4 h-4" />
                {m.telephone}
              </p>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}
