import { type FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "../lib/api";
import { saveSession } from "../lib/authStorage";
import type { PortalType } from "../lib/types";

type LoginPageProps = {
  portal: PortalType;
  title: string;
  description: string;
};


// One shared login page keeps the portal experience consistent while allowing role checks.
export function LoginPage({ portal, title, description }: LoginPageProps) {
  const navigate = useNavigate();
  const [email, setEmail] = useState(
    portal === "admin" ? "admin@demo.local" : "client@demo.local",
  );
  const [password, setPassword] = useState(
    portal === "admin" ? "Admin123!" : "Client123!",
  );
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      const result = await login({ email, password, portal });
      saveSession({
        portal,
        token: result.access_token,
        user: result.user,
      });
      navigate(portal === "admin" ? "/admin" : "/client", { replace: true });
    } catch (requestError) {
      setError(
        requestError instanceof Error ? requestError.message : "Login failed.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="page login-grid">
      <section className="hero-card">
        <p className="eyebrow">{portal === "admin" ? "Admin" : "Client"} Portal</p>
        <h1>{title}</h1>
        <p className="muted">{description}</p>
      </section>

      <form className="panel form-panel" onSubmit={handleSubmit}>
        <label className="field">
          Email
          <input
            autoComplete="username"
            onChange={(event) => setEmail(event.target.value)}
            type="email"
            value={email}
          />
        </label>

        <label className="field">
          Password
          <input
            autoComplete="current-password"
            onChange={(event) => setPassword(event.target.value)}
            type="password"
            value={password}
          />
        </label>

        {error ? <p className="error-text">{error}</p> : null}

        <button className="primary-button" disabled={isSubmitting} type="submit">
          {isSubmitting ? "Signing in..." : "Sign in"}
        </button>
      </form>
    </main>
  );
}
