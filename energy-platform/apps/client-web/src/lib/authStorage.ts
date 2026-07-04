import type { AuthSession } from "./types";

const sessionKey = "energy-platform-auth-session";


export function getStoredSession(): AuthSession | null {
  const raw = localStorage.getItem(sessionKey);
  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw) as AuthSession;
  } catch {
    localStorage.removeItem(sessionKey);
    return null;
  }
}


export function saveSession(session: AuthSession): void {
  localStorage.setItem(sessionKey, JSON.stringify(session));
}


export function clearSession(): void {
  localStorage.removeItem(sessionKey);
}
