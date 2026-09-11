import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { AuthScreen } from "@/components/AuthScreen";
import { SignedInNotice } from "@/components/GuestAuth";
import { useAuth } from "@/context/AuthContext";
import { apiUrl, getErrorMessage } from "@/lib/api";
import { Github, Mail } from "lucide-react";
import { PasswordField } from "@/components/PasswordField";
import { authApi } from "@/lib/services";

export function LoginPage() {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const oauthError = new URLSearchParams(location.search).get("oauth_error");
  const { data: oauthProviders, isLoading: oauthLoading } = useQuery({
    queryKey: ["oauth-providers"],
    queryFn: authApi.oauthProviders,
  });

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
      <SignedInNotice intent="login" />
      {!user && (
      <>
      {(oauthLoading || oauthProviders?.google || oauthProviders?.github) && (
        <div className="mb-5 space-y-2">
          {oauthProviders?.google && <button type="button" className="btn-outline w-full justify-center py-3" onClick={() => { window.location.href = apiUrl("/auth/oauth/google/start"); }}><span className="text-base font-black text-blue-600">G</span> Continue with Google</button>}
          {(oauthLoading || oauthProviders?.github) && <button type="button" className="btn-outline w-full justify-center py-3" disabled={oauthLoading} onClick={() => { window.location.href = apiUrl("/auth/oauth/github/start"); }}><Github size={18} /> {oauthLoading ? "Loading GitHub sign-in..." : "Continue with GitHub"}</button>}
          <div className="flex items-center gap-3 py-2 text-xs text-slate-400"><span className="h-px flex-1 bg-slate-200" />or use email<span className="h-px flex-1 bg-slate-200" /></div>
        </div>
      )}
      {oauthError && <div className="mb-4 rounded-xl bg-red-50 px-3 py-2 text-sm text-red-700">{oauthError}</div>}
      <form
        className="space-y-4"
        onSubmit={async (e) => {
          e.preventDefault();
          setSubmitting(true);
          setError("");
          try {
            await login(email, password);
            const destination = (location.state as { from?: string } | null)?.from || "/app";
            navigate(destination, { replace: true });
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
          <div className="relative">
          <Mail className="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-ink-400" size={17} />
          <input
            id="email"
            className="input pl-10"
            type="email"
            required
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          </div>
        </div>
        <div>
          <PasswordField id="password" label="Password" value={password} onChange={setPassword} autoComplete="current-password" />
          <p className="mt-2 text-right text-sm">
            <Link to="/forgot-password" className="font-semibold text-accent">
              Forgot password?
            </Link>
          </p>
        </div>
        {error && (
          <div className="rounded-xl bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>
        )}
        <button className="btn-primary w-full py-3" disabled={submitting || !email || password.length < 8}>
          {submitting ? "Signing in…" : "Sign in"}
        </button>
      </form>
      </>
      )}
    </AuthScreen>
  );
}
