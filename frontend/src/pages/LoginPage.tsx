import { useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { AuthScreen } from "@/components/AuthScreen";
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
    <AuthScreen
      title="Welcome back"
      subtitle="Sign in to continue to your workspace."
      footer={
        <>
          No account?{" "}
          <Link to="/register" className="font-semibold text-accent">
            Create one
          </Link>
        </>
      }
    >
      <form
        className="space-y-4"
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
            autoComplete="email"
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
            autoComplete="current-password"
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
    </AuthScreen>
  );
}
