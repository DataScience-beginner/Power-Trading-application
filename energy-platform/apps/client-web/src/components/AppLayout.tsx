import { Link, Outlet } from "react-router-dom";


// The layout keeps top-level navigation in one place as pages grow.
export function AppLayout() {
  return (
    <div className="app-shell">
      <header className="topbar">
        <Link className="brand" to="/">
          Energy Platform
        </Link>
        <nav className="nav-links">
          <Link to="/login/client">Client Login</Link>
          <Link to="/login/admin">Admin Login</Link>
        </nav>
      </header>
      <Outlet />
    </div>
  );
}
