import { useEffect, useRef, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { BrandOrb } from "@/components/AIBackdrop";
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
    <div className="flex min-h-screen items-center justify-center bg-[#f5f6fa] p-6 text-slate-950">
      <div className="rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm">
        <div className="mb-6 flex justify-center"><BrandOrb /></div>
        {error ? <><h1 className="font-display text-xl font-bold">Sign-in failed</h1><p className="mt-2 max-w-md text-sm text-rose-700">{error}</p><button className="btn-primary mt-5" onClick={() => navigate("/login")}>Back to login</button></> : <><LoaderCircle className="mx-auto animate-spin" /><p className="mt-3 text-sm text-slate-600">Finishing secure sign-in…</p></>}
      </div>
    </div>
  );
}
