import { useEffect, useState, useRef } from "react";
import { motion } from "framer-motion";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line
} from "recharts";
import { getClinicStats } from "../api/api";
import { useNavigate } from "react-router-dom";
import { ArrowLeft } from "lucide-react";

// 📦 Export
import jsPDF from "jspdf";
import html2canvas from "html2canvas";
import * as XLSX from "xlsx";

export default function Rapport() {
  const [stats, setStats] = useState(null);
  const reportRef = useRef(); // <- Référence pour capture PDF
  const navigate = useNavigate();
  
  const particles = Array.from({ length: 120 }, (_, i) => ({
    id: i,
    x: Math.random() * 100,
    y: Math.random() * 100,
    s: Math.random() * 3 + 1,
    d: Math.random() * 6,
  }));

  useEffect(() => {
    getClinicStats().then(setStats);
  }, []);

  if (!stats) return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-tr from-indigo-900 to-cyan-700 text-white text-xl">
      Loading Rapport...
    </div>
  );

  // ================= EXPORT FUNCTIONS =================
 const exportPDF = async () => {
  if (!reportRef.current) return;

  // Sauvegarder l’ancien style
  const originalBg = reportRef.current.style.background;
  const originalOverflow = reportRef.current.style.overflow;

  // Appliquer un fond clair pour PDF
  reportRef.current.style.background = "#395c99"; 
  reportRef.current.style.overflow = "visible"; // Pour que tout soit capturé

  // Capture
  const canvas = await html2canvas(reportRef.current, { scale: 3, useCORS: true });
  const imgData = canvas.toDataURL("image/png");

  const pdf = new jsPDF("p", "mm", "a4");
  const pdfWidth = pdf.internal.pageSize.getWidth();
  const pdfHeight = (canvas.height * pdfWidth) / canvas.width;

  let remainingHeight = pdfHeight;
  let position = 0;

  while (remainingHeight > 0) {
    pdf.addImage(imgData, "PNG", 0, position, pdfWidth, pdfHeight);
    remainingHeight -= pdf.internal.pageSize.getHeight();
    position -= pdf.internal.pageSize.getHeight();
    if (remainingHeight > 0) pdf.addPage();
  }

  pdf.save("rapport_clinique.pdf");

  // Restaurer le style original
  reportRef.current.style.background = originalBg;
  reportRef.current.style.overflow = originalOverflow;
};



  const exportExcel = () => {
    const wb = XLSX.utils.book_new();

    // Feuille KPI
    const kpiData = [
      { Indicateur: "Patients", Valeur: stats.total_patients },
      { Indicateur: "Médecins", Valeur: stats.total_medecins },
      { Indicateur: "Rendez-vous", Valeur: stats.total_rendezvous },
    ];
    const wsKPI = XLSX.utils.json_to_sheet(kpiData);
    XLSX.utils.book_append_sheet(wb, wsKPI, "KPI");

    // Feuille RDV
    const rdvData = stats.derniers_rdv.map(rdv => ({
      Patient: rdv[0],
      Medecin: rdv[1],
      Date: rdv[2],
      Heure: rdv[3],
      Motif: rdv[4],
    }));
    const wsRDV = XLSX.utils.json_to_sheet(rdvData);
    XLSX.utils.book_append_sheet(wb, wsRDV, "Derniers RDV");

    // Feuille RDV par mois
    const rdvMoisData = stats.rdv_par_mois.map(([m, n]) => ({ Mois: m, RendezVous: n }));
    const wsMois = XLSX.utils.json_to_sheet(rdvMoisData);
    XLSX.utils.book_append_sheet(wb, wsMois, "RDV par mois");

    // Feuille Spécialités
    const specData = stats.specialites.map(([s, n]) => ({ Specialite: s, RendezVous: n }));
    const wsSpec = XLSX.utils.json_to_sheet(specData);
    XLSX.utils.book_append_sheet(wb, wsSpec, "Spécialités");

    XLSX.writeFile(wb, "rapport_clinique.xlsx");
  };

  return (
    <div className="relative min-h-screen p-10 bg-gradient-to-tr from-indigo-900 via-blue-700 to-cyan-600 overflow-hidden text-white">

      {/* 🌌 BACKGROUND PARTICLES */}
      {particles.map(p => (
        <motion.div
          key={p.id}
          className="absolute rounded-full bg-white/30"
          style={{ width: p.s, height: p.s, top: `${p.y}%`, left: `${p.x}%` }}
          animate={{ y: [0, -50, 0], opacity: [0.2, 0.8, 0.2] }}
          transition={{ duration: 6 + p.d, repeat: Infinity }}
        />
      ))}
       <button onClick={() => navigate("/")} className="flex items-center gap-2 mb-8 bg-white/20 px-6 py-3 rounded-xl">
        <ArrowLeft /> Accueil
      </button>
      {/* 🧾 PAGE TITLE */}
      <motion.h1
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-5xl font-extrabold mb-6"
      >
        Rapport Général
      </motion.h1>

      {/* ========== EXPORT BUTTONS ========== */}
      <div className="flex gap-4 mb-12">
        <button onClick={exportPDF} className="bg-blue-500 hover:bg-blue-600 px-6 py-3 rounded-xl font-semibold shadow-lg">Export PDF</button>
        <button onClick={exportExcel} className="bg-green-500 hover:bg-green-600 px-6 py-3 rounded-xl font-semibold shadow-lg">Export Excel</button>
      </div>

      {/* ================= RAPPORT CONTENT ================= */}
      <div ref={reportRef}>
      

      {/* ================= KPI SECTION ================= */}
      <h2 className="text-2xl font-semibold mb-6">
        Indicateurs Clés (KPI)
      </h2>

      <div className="grid md:grid-cols-3 gap-10 mb-20">
        {[
          { label: "Patients", value: stats.total_patients },
          { label: "Médecins", value: stats.total_medecins },
          { label: "Rendez-vous", value: stats.total_rendezvous },
        ].map((item, i) => (
          <motion.div
            key={i}
            initial={{ scale: 0.7, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="bg-white/10 backdrop-blur-xl rounded-3xl p-10 shadow-2xl relative overflow-hidden"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-cyan-400/20 to-blue-600/10 blur-2xl" />
            <div className="relative text-sm uppercase tracking-widest opacity-80 mb-2">
              {item.label}
            </div>
            <div className="relative text-7xl font-extrabold">
              {item.value}
            </div>
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${Math.min(item.value, 100)}%` }}
              className="h-2 bg-gradient-to-r from-cyan-400 to-blue-500 mt-6 rounded-full"
            />
          </motion.div>
        ))}
      </div>

      {/* ================= ACTIVITY SECTION ================= */}
      <h2 className="text-2xl font-semibold mb-6">
        Activité des Rendez-vous
      </h2>

      <div className="grid md:grid-cols-2 gap-14 mb-20">

        {/* RDV DENSITY */}
        <div className="bg-white/10 backdrop-blur-xl rounded-3xl p-8 shadow-xl">
          <h3 className="mb-4 text-lg font-medium opacity-90">
            Densité des rendez-vous par mois
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={stats.rdv_par_mois.map(([m, n]) => ({ m, n }))}>
              <XAxis dataKey="m" stroke="#fff" />
              <YAxis stroke="#fff" />
              <Tooltip />
              <Bar dataKey="n" fill="#22d3ee" radius={[10, 10, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* GROWTH */}
        <div className="bg-white/10 backdrop-blur-xl rounded-3xl p-8 shadow-xl">
          <h3 className="mb-4 text-lg font-medium opacity-90">
            Évolution des rendez-vous
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={stats.rdv_par_mois.map(([m, n]) => ({ m, n }))}>
              <XAxis dataKey="m" stroke="#fff" />
              <YAxis stroke="#fff" />
              <Tooltip />
              <Line type="monotone" dataKey="n" stroke="#34d399" strokeWidth={3} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* ================= SPECIALITIES ================= */}
      <h2 className="text-2xl font-semibold mb-6">
        Répartition par Spécialité
      </h2>

      <div className="bg-white/10 backdrop-blur-xl rounded-3xl p-10 shadow-2xl">
        <ResponsiveContainer width="100%" height={300}>
          <BarChart layout="vertical" data={stats.specialites.map(([s, n]) => ({ s, n }))}>
            <XAxis type="number" stroke="#fff" />
            <YAxis type="category" dataKey="s" stroke="#fff" />
            <Tooltip />
            <Bar dataKey="n" fill="#818cf8" radius={[0, 12, 12, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
      
    </div>
    </div>
  );
}

