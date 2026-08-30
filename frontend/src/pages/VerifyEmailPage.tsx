import { useEffect, useState } from "react";
import { Link, Navigate, useNavigate, useSearchParams } from "react-router-dom";
import { AuthScreen } from "@/components/AuthScreen";
import { useAuth } from "@/context/AuthContext";
import { getErrorMessage } from "@/lib/api";
import { authApi } from "@/lib/services";

export function VerifyEmailPage() {
  const { user, refreshUser, logout } = useAuth();
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const [email, setEmail] = useState(user?.email || params.get("email") || "");
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [resending, setResending] = useState(false);

  useEffect(() => {
    if (user?.email) setEmail(user.email);
  }, [user?.email]);

  if (user?.is_verified) {
    return <Navigate to="/app" replace />;
  }

  return (
    <AuthScreen
      title="Verify your email"
      subtitle="Enter the 6-digit code we sent to your inbox. It expires in 10 minutes."
      footer={
        <>
          Wrong account?{" "}
          <button
            type="button"
            className="font-semibold text-accent"
            onClick={async () => {
              await logout();
              navigate("/login");
            }}
          >
            Sign out
          </button>
        </>
      }
    >
      <form
        className="space-y-4"
        onSubmit={async (e) => {
          e.preventDefault();
          setSubmitting(true);
          setError("");
          setInfo("");
          try {
            await authApi.verifyEmail(email, code);
            if (user) {
              await refreshUser();
              navigate("/app");
            } else {
              navigate("/login");
            }
          } catch (err) {
            setError(getErrorMessage(err, "Could not verify that code."));
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
          <label className="label" htmlFor="code">
            Verification code
          </label>
          <input
            id="code"
            className="input tracking-[0.4em] text-center font-semibold"
            inputMode="numeric"
            autoComplete="one-time-code"
            required
            minLength={6}
            maxLength={6}
            value={code}
            onChange={(e) => setCode(e.target.value.replace(/\D/g, "").slice(0, 6))}
          />
        </div>
        {info && (
          <div className="rounded-xl bg-emerald-50 px-3 py-2 text-sm text-emerald-800">{info}</div>
        )}
        {error && (
          <div className="rounded-xl bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>
        )}
        <button className="btn-primary w-full" disabled={submitting || code.length !== 6}>
          {submitting ? "Verifying…" : "Verify email"}
        </button>
        <button
          type="button"
          className="btn-outline w-full"
          disabled={resending || !email}
          onClick={async () => {
            setResending(true);
            setError("");
            setInfo("");
            try {
              const result = await authApi.resendVerification(email);
              setInfo(result.message);
            } catch (err) {
              setError(getErrorMessage(err, "Could not resend the code."));
            } finally {
              setResending(false);
            }
          }}
        >
          {resending ? "Sending…" : "Resend code"}
        </button>
      </form>
      <p className="mt-4 text-sm text-ink-500">
        Already verified?{" "}
        <Link to="/login" className="font-semibold text-accent">
          Sign in
        </Link>
      </p>
    </AuthScreen>
  );
}
