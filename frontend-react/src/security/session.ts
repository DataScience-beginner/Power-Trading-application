export const AUTO_LOGOUT_ENABLED = (import.meta.env.VITE_AUTO_LOGOUT_ENABLED ?? 'true').toLowerCase() !== 'false';

const configuredMinutes = Number(import.meta.env.VITE_IDLE_TIMEOUT_MINUTES ?? '30');
export const IDLE_TIMEOUT_MS = Number.isFinite(configuredMinutes) && configuredMinutes > 0
  ? configuredMinutes * 60 * 1000
  : 30 * 60 * 1000;

export function clearAuthSession(): void {
  sessionStorage.removeItem('innowatt_access_token');
  sessionStorage.removeItem('innowatt_user');
  sessionStorage.removeItem('ai_foundation_key');
}
