import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import {
  Users,
  Stethoscope,
  CalendarDays,
  Folder,
  BarChart3,
} from "lucide-react";

import bg from "../assets/27f45db4a3041d1d9b60b58f9f8b7b7e.jpg";
import { getPatients, getMedecins, getRendezvous } from "../api/api";

export default function Home() {
  const navigate = useNavigate();

  const [stats, setStats] = useState({
    patients: 0,
    medecins: 0,
    rendezvous: 0,
  });

  useEffect(() => {
    Promise.all([getPatients(), getMedecins(), getRendezvous()]).then(
      ([p, m, r]) =>
        setStats({
          patients: p?.length || 0,
          medecins: m?.length || 0,
          rendezvous: r?.length || 0,
        })
    );
  }, []);

  const actions = [
    { label: "Patients", icon: Users, path: "/patient" },
    { label: "Médecins", icon: Stethoscope, path: "/medecins" },
    { label: "Rendez-vous", icon: CalendarDays, path: "/rendezvous" },
    { label: "Dossiers médicaux", icon: Folder, path: "/dossiers" },
    { label: "Rapports & stats", icon: BarChart3, path: "/reports" },
  ];

  return (
    <div
      className="relative min-h-screen bg-cover bg-center overflow-hidden"
      style={{ backgroundImage: `url(${bg})` }}
    >
      {/* subtle animated overlay */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-tr from-indigo-400/10 via-purple-300/10 to-pink-300/10"
        animate={{ opacity: [0.2, 0.5, 0.2] }}
        transition={{ duration: 10, repeat: Infinity }}
      />

      {/* MAIN CONTENT */}
      <div className="relative z-10 min-h-screen">
        {/* TITLE CENTER TOP  */}
<motion.h1
  className="mt-8 text-center text-6xl md:text-7xl font-extrabold leading-tight relative
             bg-gradient-to-r from-indigo-400 via-blue-400 to-cyan-400
             bg-clip-text text-transparent"
  initial={{ y: -60, opacity: 0, scale: 0.9 }}
  animate={{ y: 0, opacity: 1, scale: 1 }}
  transition={{ duration: 1, type: "spring", stiffness: 100 }}
>
  {/* Floating glow behind title */}
  <span className="absolute inset-0 blur-3xl bg-gradient-to-r from-blue-400 via-cyan-400 to-indigo-400 opacity-30 animate-pulse rounded-xl"></span>

  Clinique Médicale Magique

  {/* Shimmer overlay */}
  <span className="absolute inset-0 bg-gradient-to-r from-white/50 via-white/20 to-white/50 bg-clip-text text-transparent animate-[shine_3s_linear_infinite]"></span>
</motion.h1>

        {/* DESCRIPTION ON LEFT SIDE OF PAGE */}
   <motion.div
  className="absolute top-80 left-20 max-w-sm bg-white/10 backdrop-blur-2xl border border-white/20 rounded-3xl p-6 shadow-[0_0_60px_rgba(255,255,255,0.2)] overflow-hidden"
  initial={{ opacity: 0, x: -100 }}
  animate={{ opacity: 1, x: 0 }}
  transition={{ delay: 0.6, duration: 1.2, type: "spring", stiffness: 80 }}
>
  {/* Sparkles / floating particles */}
  <motion.div
    className="absolute w-2 h-2 bg-white rounded-full top-4 left-6 opacity-50"
    animate={{ y: [0, -10, 0], x: [0, 5, 0], opacity: [0.3, 1, 0.3] }}
    transition={{ repeat: Infinity, duration: 3 }}
  />
  <motion.div
    className="absolute w-1.5 h-1.5 bg-cyan-400 rounded-full bottom-3 right-5 opacity-60"
    animate={{ y: [0, 8, 0], x: [0, -5, 0], opacity: [0.3, 1, 0.3] }}
    transition={{ repeat: Infinity, duration: 4 }}
  />

  {/* Main text */}
  <p className="text-white text-lg leading-relaxed font-semibold">
    Une plateforme{" "}
    <span className="bg-gradient-to-r from-indigo-400 via-blue-400 to-cyan-400 bg-clip-text text-transparent font-bold">
      intelligente
    </span>{" "}
    pour gérer vos{" "}
    <span className="bg-gradient-to-r from-pink-400 via-purple-400 to-indigo-400 bg-clip-text text-transparent font-bold">
      patients
    </span>
    , votre équipe et votre clinique avec élégance.votre confort et votre sécurité sont nos priorités. Nous nous efforçons de créer un environnement accueillant et chaleureux, où chaque patient se sent écouté et pris en charge.
  </p>

  {/* Floating glow under text */}
  <motion.div
    className="absolute -bottom-6 -left-6 w-40 h-20 bg-blue-400/20 blur-3xl rounded-full"
    animate={{ opacity: [0.2, 0.6, 0.2], scale: [0.9, 1.1, 0.9] }}
    transition={{ repeat: Infinity, duration: 5 }}
  />
</motion.div>


       {/* FLOATING STATS */}
<div className="absolute bottom-16 left-1/2 -translate-x-1/2 flex gap-8">
  {[
    { label: "Patients", value: stats.patients, color: "from-white-400 to-cyan-400" },
    { label: "Médecins", value: stats.medecins, color: "from-white-400 to-teal-400" },
    { label: "Rendez-vous", value: stats.rendezvous, color: "from-white-400 to-rose-400" },
  ].map((s, i) => (
    <motion.div
      key={s.label}
      initial={{ y: 30, opacity: 0, scale: 0.8 }}
      animate={{ y: [0, -10, 0], opacity: 1, scale: [1, 1.05, 1] }}
      transition={{ repeat: Infinity, duration: 4 + i, delay: i * 0.2 }}
      className={`relative px-8 py-6 rounded-3xl bg-gradient-to-br ${s.color} shadow-2xl text-center cursor-pointer`}
    >
      {/* Glow behind orb */}
      <div className="absolute -inset-3 rounded-3xl bg-white/10 blur-2xl animate-pulse"></div>
      
      <div className="relative z-10 text-3xl font-extrabold text-white drop-shadow-lg">
        {s.value}
      </div>
      <div className="relative z-10 mt-1 text-white/80 uppercase text-sm tracking-wider">
        {s.label}
      </div>
    </motion.div>
  ))}
</div>


        {/* RIGHT SIDE BIG BUTTONS */}
<div className="absolute right-32 top-1/2 -translate-y-1/2 flex flex-col gap-6">
  {actions.map((a, i) => {
    const Icon = a.icon;
    return (
      <motion.button
        key={a.label}
        onClick={() => navigate(a.path)}
        initial={{ x: 80, opacity: 0, scale: 0.9 }}
        animate={{ x: 0, opacity: 1, scale: 1 }}
        transition={{ delay: i * 0.15, type: "spring", stiffness: 100 }}
        whileHover={{
          scale: 1.15,
          rotate: [0, 2, -2, 0],
          boxShadow: "0 0 40px rgba(0,255,255,0.6), 0 0 80px rgba(0,180,255,0.3)",
        }}
        className="relative flex items-center gap-6 px-16 py-6 rounded-3xl bg-gradient-to-br from-indigo-500 via-blue-400 to-cyan-400
                   text-white text-2xl font-bold shadow-2xl overflow-hidden border border-white/20 cursor-pointer"
      >
        {/* Animated gradient glow behind button */}
        <span className="absolute inset-0 bg-gradient-to-r from-purple-400 via-pink-400 to-red-400 opacity-20 blur-xl animate-pulse rounded-3xl"></span>

        <span className="relative z-10 bg-clip-text text-transparent bg-gradient-to-r from-white via-cyan-200 to-white">
          {a.label}
        </span>
        <Icon className="relative z-10 w-8 h-8 text-white" />
      </motion.button>
    );
  })}
</div>

      </div>
    </div>
  );
}
