import { useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { getErrorMessage } from "@/lib/api";

export function LoginPage() {
  const { user, login, loading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  if (!loading && user) {
    const redirect = (location.state as { from?: string } | null)?.from || "/app";
    return <Navigate to={redirect} replace />;
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-mesh px-4">
      <div className="card w-full max-w-md p-8">
        <Link to="/" className="font-display text-2xl font-extrabold">
          Suvyon
        </Link>
        <h1 className="mt-6 text-2xl font-semibold">Sign in</h1>
        <p className="mt-1 text-sm text-ink-500">Continue to your AI workspace.</p>

        <form
          className="mt-6 space-y-4"
          onSubmit={async (e) => {
            e.preventDefault();
            setSubmitting(true);
            setError("");
            try {
              await login(email, password);
              navigate("/app");
            } catch (err) {
              setError(getErrorMessage(err, "Login failed."));
            } finally {
              setSubmitting(false);
            }
          }}
        >
          <div>
            <label className="label" htmlFor="email">
              Email
            </label>
            <input
              id="email"
              className="input"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div>
            <label className="label" htmlFor="password">
              Password
            </label>
            <input
              id="password"
              className="input"
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          {error && (
            <div className="rounded-xl bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>
          )}
          <button className="btn-primary w-full" disabled={submitting}>
            {submitting ? "Signing in…" : "Sign in"}
          </button>
        </form>

        <p className="mt-5 text-sm text-ink-500">
          No account?{" "}
          <Link to="/register" className="font-semibold text-accent">
            Create one
          </Link>
        </p>
      </div>
    </div>
  );
}
