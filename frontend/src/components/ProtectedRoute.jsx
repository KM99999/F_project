import { Navigate } from "react-router-dom";

import { useAuth } from "../auth/AuthContext.jsx";

// Guards private routes: redirects to /login when there is no authenticated user.
export default function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) return <div className="centered">Cargando…</div>;
  if (!user) return <Navigate to="/login" replace />;
  return children;
}
