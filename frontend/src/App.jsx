import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/home"; // import home page
import Patient from "./pages/patient"; // import patient page
import Medecin from "./pages/medecin"; // import medecin page
import Dossier from "./pages/dossier"; // import dossier page
import Rendezvous from "./pages/rendezvous"; // import rendezvous page
import Reports from "./pages/reports"; // import reports page
import DossierDetail from "./pages/DossierDetail"; // import dossier detail page

export default function App() {  // <-- must be default export
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/patient" element={<Patient />} />
        <Route path="/medecins" element={<Medecin />} />
        <Route path="/dossiers" element={<Dossier />} />
        <Route path="/rendezvous" element={<Rendezvous />} />
        <Route path="/reports" element={<Reports />} />
        <Route path="/dossiers/:id_patient" element={<DossierDetail />} />
      </Routes>
    </BrowserRouter>
  );
}