import { useEffect, useRef, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { LoaderCircle } from "lucide-react";

import { useAuth } from "@/context/AuthContext";
import { getErrorMessage } from "@/lib/api";
import { authApi } from "@/lib/services";

export function OAuthCallbackPage() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const { acceptOAuth } = useAuth();
  const [error, setError] = useState("");
  const started = useRef(false);

  useEffect(() => {
    if (started.current) return;
    started.current = true;
    const ticket = params.get("ticket");
    if (!ticket) {
      setError("The sign-in response is missing its exchange ticket.");
      return;
    }
    authApi.exchangeOAuth(ticket)
      .then(async (tokens) => {
        await acceptOAuth(tokens.access_token, tokens.refresh_token);
        navigate("/app", { replace: true });
      })
      .catch((err) => setError(getErrorMessage(err, "Social sign-in failed.")));
  }, [acceptOAuth, navigate, params]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950 p-6 text-white">
      <div className="rounded-3xl border border-white/10 bg-white/5 p-8 text-center">
        {error ? <><h1 className="font-display text-xl font-bold">Sign-in failed</h1><p className="mt-2 max-w-md text-sm text-rose-300">{error}</p><button className="btn-primary mt-5" onClick={() => navigate("/login")}>Back to login</button></> : <><LoaderCircle className="mx-auto animate-spin" /><p className="mt-3 text-sm text-slate-300">Finishing secure sign-in…</p></>}
      </div>
    </div>
  );
}
