import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AuthScreen } from "@/components/AuthScreen";
import { SignedInNotice } from "@/components/GuestAuth";
import { useAuth } from "@/context/AuthContext";
import { getErrorMessage } from "@/lib/api";

export function RegisterPage() {
  const { user, register } = useAuth();
  const navigate = useNavigate();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  return (
    <AuthScreen
      title="Create your workspace"
      subtitle="Set up an account to chat, run agents, and upload knowledge."
      footer={
        <>
          Already registered?{" "}
          <Link to="/login" className="font-semibold text-accent">
            Sign in
          </Link>
        </>
      }
    >
      <SignedInNotice intent="register" />
      {!user && (
      <form
        className="space-y-4"
        onSubmit={async (e) => {
          e.preventDefault();
          setSubmitting(true);
          setError("");
          try {
            await register(fullName, email, password);
            navigate("/app");
          } catch (err) {
            setError(getErrorMessage(err, "Registration failed."));
          } finally {
            setSubmitting(false);
          }
        }}
      >
        <div>
          <label className="label" htmlFor="fullName">
            Full name
          </label>
          <input
            id="fullName"
            className="input"
            required
            minLength={2}
            autoComplete="name"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
          />
        </div>
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
            autoComplete="new-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        {error && (
          <div className="rounded-xl bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>
        )}
        <button className="btn-primary w-full" disabled={submitting}>
          {submitting ? "Creating…" : "Create account"}
        </button>
      </form>
      )}
    </AuthScreen>
  );
}
