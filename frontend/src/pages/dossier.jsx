import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { getPatients } from "../api/api";
import { ArrowLeft } from "lucide-react";

export default function Dossiers() {
  const [patients, setPatients] = useState([]);
  const [search, setSearch] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    getPatients().then(setPatients);
  }, []);

  const filtered = patients.filter((p) =>
    `${p.nom} ${p.prenom}`.toLowerCase().includes(search.toLowerCase())
  );

  // More particles for magical effect
  const particles = Array.from({ length: 60 }, (_, i) => ({
    id: i,
    x: Math.random() * 100,
    y: Math.random() * 100,
    size: Math.random() * 4 + 1,
    delay: Math.random() * 6,
  }));

  return (
    <div className="relative min-h-screen p-10 bg-gradient-to-tr from-blue-900 via-blue-400 to-indigo-600 overflow-hidden">
      {/* Background floating particles */}
      {particles.map((p) => (
        <motion.div
          key={p.id}
          className="absolute rounded-full bg-white/30"
          style={{ width: p.size, height: p.size, top: `${p.y}%`, left: `${p.x}%` }}
          animate={{ y: [0, -30, 0], x: [0, 15, 0], opacity: [0.2, 0.8, 0.2] }}
          transition={{ repeat: Infinity, duration: 4 + p.delay, delay: p.delay }}
        />
      ))}
       <button onClick={() => navigate("/")} className="flex items-center gap-2 mb-8 bg-white/20 text-white px-6 py-3 rounded-xl">
        <ArrowLeft /> Accueil
      </button>

      {/* TITLE */}
      <motion.h1
        className="text-center text-5xl md:text-6xl font-extrabold mb-10 text-white relative"
        initial={{ y: -50, opacity: 0, scale: 0.9 }}
        animate={{ y: 0, opacity: 1, scale: 1 }}
        transition={{ duration: 1.2, type: "spring", stiffness: 100 }}
      >
        
        📁 Dossiers Médicaux
        {/* Floating glow behind title */}
        <span className="absolute inset-0 blur-3xl bg-gradient-to-r from-yellow-800 via-blue-400 to-yellow-800 opacity-40 animate-pulse rounded-xl"></span>
        {/* Sparkle overlay */}
        <motion.div
          className="absolute w-3 h-3 bg-white rounded-full top-5 left-1/3 opacity-80"
          animate={{ y: [0, -12, 0], x: [0, 6, 0], opacity: [0.2, 1, 0.2] }}
          transition={{ repeat: Infinity, duration: 2.5 }}
        />
        <motion.div
          className="absolute w-2 h-2 bg-white rounded-full bottom-10 right-1/2 opacity-70"
          animate={{ y: [0, 10, 0], x: [0, -6, 0], opacity: [0.2, 1, 0.2] }}
          transition={{ repeat: Infinity, duration: 3 }}
        />
      </motion.h1>
      

      {/* Search */}
      <motion.input
        className="w-full p-3 mb-8 border border-white/30 rounded-xl shadow-lg backdrop-blur-sm bg-white/10 placeholder:text-white/70 text-white font-semibold"
        placeholder="🔍 Rechercher par patient..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1 }}
      />
      
      {/* Dossiers */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        {filtered.map((p) => (
          <motion.div
            key={p.id_patient}
            onClick={() => navigate(`/dossiers/${p.id_patient}`)}
            className="cursor-pointer group relative"
            whileHover={{ scale: 1.06 }}
          >
            {/* Folder */}
            <motion.div
              className="relative w-full h-40 bg-[#e7d494] rounded-lg shadow-2xl"
              whileHover={{ scale: 1.08 }}
            >
              {/* Folder tab */}
              <div className="absolute -top-4 left-4 w-24 h-6 bg-[#f1d060] rounded-t-md shadow-md"></div>

              {/* Floating glow inside folder */}
              <motion.div
                className="absolute inset-0 rounded-lg bg-white/20 blur-3xl"
                animate={{ opacity: [0.2, 0.5, 0.2] }}
                transition={{ duration: 3, repeat: Infinity }}
              />
              {/* Tiny sparkles on each folder */}
              {Array.from({ length: 6 }, (_, i) => (
                <motion.div
                  key={i}
                  className="absolute w-1 h-1 bg-white rounded-full"
                  style={{
                    top: `${Math.random() * 80 + 10}%`,
                    left: `${Math.random() * 80 + 10}%`,
                  }}
                  animate={{
                    y: [0, -8, 0],
                    x: [0, 6, 0],
                    opacity: [0.2, 1, 0.2],
                  }}
                  transition={{
                    repeat: Infinity,
                    duration: 2 + Math.random() * 2,
                    delay: Math.random() * 3,
                  }}
                />
              ))}
            </motion.div>

            {/* Info */}
            <motion.div
              className="mt-3 text-center"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <p className="font-semibold text-white drop-shadow-lg">
                {p.nom} {p.prenom}
              </p>
              <p className="text-sm text-white/80">{p.age} ans</p>
            </motion.div>
          </motion.div>
        ))}
      </div>

      {/* Bottom magical glow */}
      <motion.div
        className="absolute bottom-10 left-1/2 -translate-x-1/2 w-96 h-32 bg-gradient-to-r from-yellow-300 via-white to-yellow-300 blur-3xl opacity-30 rounded-full animate-pulse"
        animate={{ scale: [0.9, 1.1, 0.9], opacity: [0.1, 0.3, 0.1] }}
        transition={{ repeat: Infinity, duration: 5 }}
      />
    </div>
  );
}
