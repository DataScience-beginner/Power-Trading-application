import { Navigate, Route, Routes } from "react-router-dom";
import { AppLayout } from "../components/AppLayout";
import { ProtectedRoute } from "../components/ProtectedRoute";
import { AdminDashboardPage } from "../pages/AdminDashboardPage";
import { ClientDashboardPage } from "../pages/ClientDashboardPage";
import { HomePage } from "../pages/HomePage";
import { LoginPage } from "../pages/LoginPage";

export function AppRouter() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<HomePage />} />
        <Route
          path="/login/admin"
          element={
            <LoginPage
              portal="admin"
              title="Admin Login"
              description="Operational access for platform and tenant administrators."
            />
          }
        />
        <Route
          path="/login/client"
          element={
            <LoginPage
              portal="client"
              title="Client Login"
              description="Tenant-facing access for workbook upload and Solar Working dashboards."
            />
          }
        />
        <Route
          path="/admin"
          element={
            <ProtectedRoute
              allowedPortals={["admin"]}
              element={<AdminDashboardPage />}
            />
          }
        />
        <Route
          path="/client"
          element={
            <ProtectedRoute
              allowedPortals={["client", "admin"]}
              element={<ClientDashboardPage />}
            />
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
