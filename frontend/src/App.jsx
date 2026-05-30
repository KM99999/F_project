import { Navigate, Route, Routes } from "react-router-dom";

import Layout from "./components/Layout.jsx";
import ProtectedRoute from "./components/ProtectedRoute.jsx";
import CargaPage from "./pages/CargaPage.jsx";
import DetallePage from "./pages/DetallePage.jsx";
import ListaPage from "./pages/ListaPage.jsx";
import LoginPage from "./pages/LoginPage.jsx";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      {/* Everything below requires authentication. */}
      <Route
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route path="/carga" element={<CargaPage />} />
        <Route path="/recibos" element={<ListaPage />} />
        <Route path="/recibos/:id" element={<DetallePage />} />
      </Route>

      <Route path="/" element={<Navigate to="/carga" replace />} />
      <Route path="*" element={<Navigate to="/carga" replace />} />
    </Routes>
  );
}
