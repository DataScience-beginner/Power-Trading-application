import { type ReactNode, useEffect, useState } from "react";

export type DashboardNavItem = {
  label: string;
  hint: string;
  isActive?: boolean;
};

type DashboardShellProps = {
  portalLabel: string;
  title: string;
  subtitle: string;
  userName?: string;
  userEmail?: string;
  navItems: DashboardNavItem[];
  topMeta: Array<{ label: string; value: string }>;
  onSignOut: () => void;
  children: ReactNode;
};

type DashboardTheme = "light" | "dark";

const themeStorageKey = "energy-platform-dashboard-theme";

// Shared shell keeps admin and client pages visually consistent as more services arrive.
export function DashboardShell({
  portalLabel,
  title,
  subtitle,
  userName,
  userEmail,
  navItems,
  topMeta,
  onSignOut,
  children,
}: DashboardShellProps) {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [theme, setTheme] = useState<DashboardTheme>("light");

  useEffect(() => {
    const storedTheme = window.localStorage.getItem(themeStorageKey);
    if (storedTheme === "light" || storedTheme === "dark") {
      setTheme(storedTheme);
      document.documentElement.dataset.theme = storedTheme;
      return;
    }

    const preferredTheme = window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
    setTheme(preferredTheme);
    document.documentElement.dataset.theme = preferredTheme;
  }, []);

  function handleThemeToggle() {
    const nextTheme = theme === "light" ? "dark" : "light";
    setTheme(nextTheme);
    document.documentElement.dataset.theme = nextTheme;
    window.localStorage.setItem(themeStorageKey, nextTheme);
  }

  return (
    <div
      className={`dashboard-shell${isSidebarCollapsed ? " sidebar-collapsed" : ""}`}
    >
      <aside className="dashboard-sidebar">
        <div className="sidebar-top">
          <div>
            <p className="sidebar-kicker">Energy Platform</p>
            <h1 className="sidebar-title">{portalLabel}</h1>
          </div>
          <button
            aria-label={isSidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
            className="sidebar-toggle"
            onClick={() => setIsSidebarCollapsed((current) => !current)}
            type="button"
          >
            {isSidebarCollapsed ? ">" : "<"}
          </button>
        </div>

        <div className="sidebar-user">
          <div className="sidebar-avatar">{portalLabel.slice(0, 1)}</div>
          <div className="sidebar-user-copy">
            <strong>{userName ?? "Loading user"}</strong>
            <span>{userEmail ?? "Fetching account context"}</span>
          </div>
        </div>

        <nav className="sidebar-nav" aria-label={`${portalLabel} navigation`}>
          {navItems.map((item) => (
            <button
              className={`sidebar-nav-item${item.isActive ? " is-active" : ""}`}
              key={item.label}
              type="button"
            >
              <span>{item.label}</span>
              <small>{item.hint}</small>
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          <p className="sidebar-footer-label">Workspace</p>
          <p className="sidebar-footer-copy">
            Service-oriented workbook operations with tenant-safe processing.
          </p>
          <button className="secondary-button sidebar-signout" onClick={onSignOut} type="button">
            Sign out
          </button>
        </div>
      </aside>

      <main className="dashboard-main">
        <header className="dashboard-header">
          <div>
            <p className="eyebrow">{portalLabel}</p>
            <h2>{title}</h2>
            <p className="muted dashboard-subtitle">{subtitle}</p>
          </div>

          <div className="dashboard-header-side">
            <button
              className="secondary-button theme-toggle"
              onClick={handleThemeToggle}
              type="button"
            >
              {theme === "light" ? "Dark mode" : "Light mode"}
            </button>

            <div className="dashboard-top-meta">
              {topMeta.map((item) => (
                <div className="top-meta-chip" key={item.label}>
                  <span>{item.label}</span>
                  <strong>{item.value}</strong>
                </div>
              ))}
            </div>
          </div>
        </header>

        <div className="dashboard-content">{children}</div>
      </main>
    </div>
  );
}
