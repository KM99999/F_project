import { NavLink, Outlet } from "react-router-dom";

import { useAuth } from "../auth/AuthContext.jsx";

// App shell shown after login: top nav linking the three screens + logout.
export default function Layout() {
  const { user, logout } = useAuth();

  return (
    <div className="app-shell">
      <header className="app-header">
        <span className="app-title">Verificación de Recibos</span>
        <nav className="app-nav">
          <NavLink to="/carga">Carga</NavLink>
          <NavLink to="/recibos">Lista</NavLink>
        </nav>
        <div className="app-user">
          <span>{user?.usuario}</span>
          <button onClick={logout} className="link-button">
            Cerrar sesión
          </button>
        </div>
      </header>
      <main className="app-main">
        <Outlet />
      </main>
    </div>
  );
}
