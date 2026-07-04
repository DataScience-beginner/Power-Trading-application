import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { DashboardShell } from "../components/DashboardShell";
import { SparklineChart } from "../components/SparklineChart";
import { downloadCsv } from "../lib/export";
import { fetchAdminOverview, fetchAdminSummary } from "../lib/api";
import { clearSession, getStoredSession } from "../lib/authStorage";
import type { AdminOverviewResponse, PortalSummary } from "../lib/types";


export function AdminDashboardPage() {
  const navigate = useNavigate();
  const [summary, setSummary] = useState<PortalSummary | null>(null);
  const [error, setError] = useState("");
  const [overview, setOverview] = useState<AdminOverviewResponse | null>(null);
  const [workbookFilter, setWorkbookFilter] = useState<"all" | "calculated">("all");

  useEffect(() => {
    const session = getStoredSession();
    if (!session) {
      navigate("/login/admin", { replace: true });
      return;
    }

    fetchAdminSummary(session.token)
      .then(setSummary)
      .catch((requestError: Error) => {
        setError(requestError.message);
      });

    fetchAdminOverview(session.token)
      .then(setOverview)
      .catch((requestError: Error) => {
        setError((current) => current || requestError.message);
      });
  }, [navigate]);

  const metricCards = [
    {
      label: "Tracked Metrics",
      value: String(overview?.metrics.length ?? 0),
      detail: "Headline measures exposed for platform operations.",
      series: overview?.metrics.map((metric) => metric.value) ?? [],
      tone: "neutral" as const,
    },
    {
      label: "Recent Workbooks",
      value: String(overview?.recent_workbooks.length ?? 0),
      detail: "Latest workbook processing events across the platform.",
      series: overview?.recent_workbooks.map((item) => item.solar_working_rows) ?? [],
      tone: "accent" as const,
    },
    {
      label: "Tenant Count",
      value: String(overview?.tenant_codes.length ?? 0),
      detail: "Configured tenant identities in the current environment.",
      series: overview?.tenant_codes.map((_, index) => index + 1) ?? [],
      tone: "neutral" as const,
    },
    {
      label: "User Count",
      value: String(overview?.user_emails.length ?? 0),
      detail: "Known platform and tenant users in the seeded workspace.",
      series: overview?.user_emails.map((_, index) => index + 1) ?? [],
      tone: "warning" as const,
    },
  ];
  const filteredWorkbooks =
    workbookFilter === "all"
      ? overview?.recent_workbooks ?? []
      : (overview?.recent_workbooks ?? []).filter((item) => item.status === "calculated");

  return (
    <DashboardShell
      navItems={[
        { hint: "Active", isActive: true, label: "Operations Hub" },
        { hint: "RBAC", label: "Access Control" },
        { hint: "Tenants", label: "Tenant Registry" },
        { hint: "Roadmap", label: "Service Rollout" },
      ]}
      onSignOut={() => {
        clearSession();
        navigate("/", { replace: true });
      }}
      portalLabel="Admin Portal"
      subtitle="Platform-wide operational view for RBAC, tenant configuration, workbook activity, and future service monitoring."
      title="Operational Control Surface"
      topMeta={[
        { label: "Environment", value: "Development" },
        { label: "Tenants", value: String(overview?.tenant_codes.length ?? 0) },
        { label: "Users", value: String(overview?.user_emails.length ?? 0) },
      ]}
      userEmail={summary?.user.email}
      userName={summary?.user.full_name}
    >
      <section className="dashboard-banner panel span-12">
        <div>
          <p className="eyebrow">Platform Snapshot</p>
          <h3>Administration, monitoring posture, and rollout readiness.</h3>
          <p className="muted">
            This control surface is designed for tenant governance, service
            tracking, and multi-client platform expansion without breaking the
            unified data model.
          </p>
        </div>
        <div className="banner-status">
          <span className="status-badge status-badge-accent">admin scope</span>
          <strong>{overview?.recent_workbooks.length ?? 0} recent workbook events</strong>
        </div>
      </section>

      {metricCards.map((card) => (
        <section className="metric-card panel span-3" key={card.label}>
          <p className="metric-label">{card.label}</p>
          <strong className="metric-value">{card.value}</strong>
          <p className="metric-detail">{card.detail}</p>
          <SparklineChart tone={card.tone} values={card.series} />
        </section>
      ))}

      <section className="panel insight-panel span-4">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">Access Context</p>
            <h3>Current Administrator</h3>
          </div>
          <span className="status-badge">platform</span>
        </div>
        {error ? <p className="error-text">{error}</p> : null}
        {summary ? (
          <div className="detail-list">
            <div>
              <span>Name</span>
              <strong>{summary.user.full_name}</strong>
            </div>
            <div>
              <span>Email</span>
              <strong>{summary.user.email}</strong>
            </div>
            <div>
              <span>Roles</span>
              <strong>{summary.user.role_codes.join(", ")}</strong>
            </div>
          </div>
        ) : (
          <p className="muted">Loading admin summary...</p>
        )}
      </section>

      <section className="panel insight-panel span-4">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">Planned Modules</p>
            <h3>Feature Delivery</h3>
          </div>
        </div>
        <ul className="insight-list">
          {(summary?.capabilities ?? []).map((capability) => (
            <li key={capability}>{capability}</li>
          ))}
        </ul>
      </section>

      <section className="panel insight-panel span-4">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">Identity Coverage</p>
            <h3>Registry Snapshot</h3>
          </div>
        </div>
        <div className="detail-list">
          <div>
            <span>Tenants</span>
            <strong>{overview?.tenant_codes.join(", ") || "none"}</strong>
          </div>
          <div>
            <span>Users</span>
            <strong>{overview?.user_emails.join(", ") || "none"}</strong>
          </div>
        </div>
      </section>

      <section className="panel span-5">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">Platform Metrics</p>
            <h3>Operational Measures</h3>
          </div>
        </div>
        {overview ? (
          <div className="metric-list">
            {overview.metrics.map((metric) => (
              <article className="metric-list-item" key={metric.label}>
                <span>{metric.label}</span>
                <strong>{metric.value}</strong>
              </article>
            ))}
          </div>
        ) : (
          <p className="muted">Loading metrics...</p>
        )}
      </section>

      <section className="panel span-7">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">Recent Workbooks</p>
            <h3>Latest Activity</h3>
          </div>
          <div className="panel-heading-meta">
            <button
              className="secondary-button table-action-button"
              disabled={filteredWorkbooks.length === 0}
              onClick={() =>
                downloadCsv(
                  "admin-recent-workbooks.csv",
                  [
                    { key: "workbook_month", label: "Month" },
                    { key: "file_name", label: "File" },
                    { key: "status", label: "Status" },
                    { key: "solar_working_rows", label: "Rows" },
                    { key: "uploaded_at", label: "Uploaded At" },
                  ],
                  filteredWorkbooks,
                )
              }
              type="button"
            >
              Export CSV
            </button>
          </div>
        </div>
        <div className="filter-chip-row">
          <button
            className={`filter-chip${workbookFilter === "all" ? " is-active" : ""}`}
            onClick={() => setWorkbookFilter("all")}
            type="button"
          >
            All activity
          </button>
          <button
            className={`filter-chip${workbookFilter === "calculated" ? " is-active" : ""}`}
            onClick={() => setWorkbookFilter("calculated")}
            type="button"
          >
            Calculated only
          </button>
        </div>
        {filteredWorkbooks.length > 0 ? (
          <div className="table-wrap">
            <table className="data-table compact-table">
              <thead>
                <tr>
                  <th>Month</th>
                  <th>File</th>
                  <th>Status</th>
                  <th>Rows</th>
                </tr>
              </thead>
              <tbody>
                {filteredWorkbooks.map((item) => (
                  <tr key={item.workbook_id}>
                    <td>{item.workbook_month ?? "unknown"}</td>
                    <td>{item.file_name}</td>
                    <td>
                      <span className="status-badge">{item.status}</span>
                    </td>
                    <td>{item.solar_working_rows}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="muted">No workbook activity yet.</p>
        )}
      </section>
    </DashboardShell>
  );
}
