import type { ReactElement } from "react";
import { Navigate } from "react-router-dom";
import { getStoredSession } from "../lib/authStorage";
import type { PortalType } from "../lib/types";

type ProtectedRouteProps = {
  allowedPortals: PortalType[];
  element: ReactElement;
};


// Route guards are kept small and explicit so role-based navigation stays easy to follow.
export function ProtectedRoute({
  allowedPortals,
  element,
}: ProtectedRouteProps) {
  const session = getStoredSession();
  if (!session) {
    return <Navigate to="/login/client" replace />;
  }

  if (!allowedPortals.includes(session.portal)) {
    return <Navigate to="/" replace />;
  }

  return element;
}
