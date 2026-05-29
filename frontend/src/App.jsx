import { Navigate, Route, Routes } from "react-router-dom";

import AppLayout from "./layout/AppLayout.jsx";
import AddMonitor from "./pages/AddMonitor.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Incidents from "./pages/Incidents.jsx";
import MonitorDetails from "./pages/MonitorDetails.jsx";

export default function App() {
  // Главная карта маршрутов: все страницы работают внутри общего layout.
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<Dashboard />} />
        <Route path="monitors/new" element={<AddMonitor />} />
        <Route path="monitors/:monitorId" element={<MonitorDetails />} />
        <Route path="incidents" element={<Incidents />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
