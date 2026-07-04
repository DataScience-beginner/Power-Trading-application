import { Link } from "react-router-dom";


export function HomePage() {
  return (
    <main className="page home-grid">
      <section className="hero-card">
        <p className="eyebrow">Energy Platform</p>
        <h1>Service-Oriented Energy Workbook Processing</h1>
        <p className="muted">
          The first service converts uploaded energy workbooks into backend
          calculated Solar Working results, with unified models, tenant
          isolation, and future AI expansion built into the platform shape.
        </p>
        <div className="action-row">
          <Link className="primary-button" to="/login/client">
            Client Login
          </Link>
          <Link className="secondary-button" to="/login/admin">
            Admin Login
          </Link>
        </div>
      </section>

      <section className="panel">
        <h2>Demo Accounts</h2>
        <ul className="flat-list">
          <li>`admin@demo.local` / `Admin123!`</li>
          <li>`tenantadmin@demo.local` / `Tenant123!`</li>
          <li>`client@demo.local` / `Client123!`</li>
        </ul>
      </section>

      <section className="panel">
        <h2>Current Product Direction</h2>
        <ul className="flat-list">
          <li>Tenant-aware workbook upload flow</li>
          <li>Backend-generated Solar Working calculation</li>
          <li>RBAC-enabled admin and client portals</li>
          <li>SQLite now, PostgreSQL later</li>
        </ul>
      </section>
    </main>
  );
}
