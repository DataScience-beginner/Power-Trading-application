import { useEffect, useRef } from 'react';
import { AUTO_LOGOUT_ENABLED, IDLE_TIMEOUT_MS, clearAuthSession } from '../security/session';

const ACTIVITY_EVENTS: Array<keyof WindowEventMap> = [
  'mousemove',
  'mousedown',
  'keydown',
  'scroll',
  'touchstart',
  'click',
];

/** Log out an authenticated browser session after configurable inactivity. */
export function useIdleLogout(onLogout: () => void, authenticated: boolean): void {
  const callbackRef = useRef(onLogout);
  callbackRef.current = onLogout;

  useEffect(() => {
    if (!authenticated || !AUTO_LOGOUT_ENABLED) return undefined;

    let lastActivityAt = Date.now();
    const markActivity = () => { lastActivityAt = Date.now(); };
    const timer = window.setInterval(() => {
      if (Date.now() - lastActivityAt < IDLE_TIMEOUT_MS) return;
      clearAuthSession();
      callbackRef.current();
    }, 10_000);

    ACTIVITY_EVENTS.forEach((eventName) => window.addEventListener(eventName, markActivity, { passive: true }));
    return () => {
      window.clearInterval(timer);
      ACTIVITY_EVENTS.forEach((eventName) => window.removeEventListener(eventName, markActivity));
    };
  }, [authenticated]);
}
