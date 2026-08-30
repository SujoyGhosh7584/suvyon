import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AuthScreen } from "@/components/AuthScreen";
import { getErrorMessage } from "@/lib/api";
import { authApi } from "@/lib/services";

export function ForgotPasswordPage() {
  const navigate = useNavigate();
  const [step, setStep] = useState<"request" | "reset">("request");
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");
  const [submitting, setSubmitting] = useState(false);

  return (
    <AuthScreen
      title={step === "request" ? "Forgot password" : "Set a new password"}
      subtitle={
        step === "request"
          ? "We’ll email a 6-digit code if that account exists."
          : "Enter the code from your email and choose a new password."
      }
      footer={
        <>
          Remembered it?{" "}
          <Link to="/login" className="font-semibold text-accent">
            Sign in
          </Link>
        </>
      }
    >
      {step === "request" ? (
        <form
          className="space-y-4"
          onSubmit={async (e) => {
            e.preventDefault();
            setSubmitting(true);
            setError("");
            try {
              const result = await authApi.forgotPassword(email);
              setInfo(result.message);
              setStep("reset");
            } catch (err) {
              setError(getErrorMessage(err, "Could not send a reset code."));
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
          {error && (
            <div className="rounded-xl bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>
          )}
          <button className="btn-primary w-full" disabled={submitting}>
            {submitting ? "Sending…" : "Send reset code"}
          </button>
        </form>
      ) : (
        <form
          className="space-y-4"
          onSubmit={async (e) => {
            e.preventDefault();
            setSubmitting(true);
            setError("");
            try {
              await authApi.resetPassword(email, code, password);
              navigate("/login", { replace: true });
            } catch (err) {
              setError(getErrorMessage(err, "Could not reset the password."));
            } finally {
              setSubmitting(false);
            }
          }}
        >
          {info && (
            <div className="rounded-xl bg-emerald-50 px-3 py-2 text-sm text-emerald-800">{info}</div>
          )}
          <div>
            <label className="label" htmlFor="code">
              Reset code
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
          <div>
            <label className="label" htmlFor="password">
              New password
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
          <button className="btn-primary w-full" disabled={submitting || code.length !== 6}>
            {submitting ? "Saving…" : "Reset password"}
          </button>
          <button
            type="button"
            className="btn-outline w-full"
            disabled={submitting}
            onClick={() => {
              setStep("request");
              setCode("");
              setPassword("");
              setError("");
              setInfo("");
            }}
          >
            Use a different email
          </button>
        </form>
      )}
    </AuthScreen>
  );
}
