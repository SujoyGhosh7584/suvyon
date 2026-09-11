import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CheckCircle2, Eye, EyeOff, KeyRound, LoaderCircle, Trash2 } from "lucide-react";
import { getErrorMessage } from "@/lib/api";
import { apiKeysApi } from "@/lib/services";
import type { ApiKeyProvider } from "@/types/api";

const PROVIDERS: Array<{ id: ApiKeyProvider; name: string; description: string; placeholder: string }> = [
  { id: "groq", name: "Groq", description: "Fast hosted open models", placeholder: "gsk_..." },
  { id: "openrouter", name: "OpenRouter", description: "Many models through one key", placeholder: "sk-or-v1-..." },
  { id: "gemini", name: "Google Gemini", description: "Gemini models and large context", placeholder: "AIza..." },
  { id: "cerebras", name: "Cerebras", description: "Permanent free tier, very fast inference", placeholder: "csk-..." },
  { id: "sambanova", name: "SambaNova", description: "Free SambaCloud account and open models", placeholder: "Paste SambaCloud key" },
  { id: "huggingface", name: "Hugging Face", description: "Monthly free Inference Provider credits", placeholder: "hf_..." },
  { id: "mistral", name: "Mistral", description: "Limited monthly usage in Free mode", placeholder: "Paste Mistral key" },
  { id: "cohere", name: "Cohere", description: "Free rate-limited trial access", placeholder: "Paste Cohere trial key" },
  { id: "nvidia", name: "NVIDIA NIM", description: "Hosted API Catalog trial access", placeholder: "nvapi-..." },
];

export function ApiKeysSettings() {
  const client = useQueryClient();
  const [values, setValues] = useState<Partial<Record<ApiKeyProvider, string>>>({});
  const [visible, setVisible] = useState<Partial<Record<ApiKeyProvider, boolean>>>({});
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const queryKey = ["user-api-keys"];
  const { data: statuses = [], isLoading } = useQuery({ queryKey, queryFn: apiKeysApi.list });
  const save = useMutation({
    mutationFn: ({ provider, apiKey }: { provider: ApiKeyProvider; apiKey: string }) => apiKeysApi.save(provider, apiKey),
    onSuccess: (_, { provider }) => {
      setValues((current) => ({ ...current, [provider]: "" }));
      setMessage(`${PROVIDERS.find((item) => item.id === provider)?.name} key saved.`);
      setError("");
      client.invalidateQueries({ queryKey });
      client.invalidateQueries({ queryKey: ["models"] });
    },
    onError: (reason) => { setMessage(""); setError(getErrorMessage(reason)); },
  });
  const remove = useMutation({
    mutationFn: apiKeysApi.remove,
    onSuccess: (_, provider) => {
      setMessage(`${PROVIDERS.find((item) => item.id === provider)?.name} key removed.`);
      setError("");
      client.invalidateQueries({ queryKey });
      client.invalidateQueries({ queryKey: ["models"] });
    },
    onError: (reason) => { setMessage(""); setError(getErrorMessage(reason)); },
  });

  return (
    <section className="col-span-full rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex items-start gap-3">
        <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-accent/10 text-accent"><KeyRound size={19} /></span>
        <div><h3 className="font-semibold">Your AI provider keys</h3><p className="mt-1 text-sm leading-relaxed text-slate-500">Use your own quota for AI requests. Keys are encrypted before storage and are never shown again.</p></div>
      </div>
      {message && <p className="mt-4 rounded-xl bg-emerald-50 px-3 py-2 text-sm text-emerald-700">{message}</p>}
      {error && <p className="mt-4 rounded-xl bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}
      <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {PROVIDERS.map((provider) => {
          const status = statuses.find((item) => item.provider === provider.id);
          const value = values[provider.id] || "";
          const saving = save.isPending && save.variables?.provider === provider.id;
          const deleting = remove.isPending && remove.variables === provider.id;
          return <div key={provider.id} className="rounded-2xl border border-slate-200 bg-slate-50/60 p-4">
            <div className="flex items-center justify-between gap-2"><div><div className="font-semibold">{provider.name}</div><div className="text-xs text-slate-500">{provider.description}</div></div>{status?.configured && <span className="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-2 py-1 text-[10px] font-bold text-emerald-700"><CheckCircle2 size={12} /> {status.hint}</span>}</div>
            <div className="relative mt-4">
              <input className="input pr-10" type={visible[provider.id] ? "text" : "password"} value={value} autoComplete="off" spellCheck={false} placeholder={status?.configured ? "Enter a replacement key" : provider.placeholder} onChange={(event) => setValues((current) => ({ ...current, [provider.id]: event.target.value }))} />
              <button type="button" className="absolute right-2 top-1/2 -translate-y-1/2 rounded-lg p-1.5 text-slate-400 hover:text-slate-700" onClick={() => setVisible((current) => ({ ...current, [provider.id]: !current[provider.id] }))} aria-label={`${visible[provider.id] ? "Hide" : "Show"} ${provider.name} key`}>{visible[provider.id] ? <EyeOff size={15} /> : <Eye size={15} />}</button>
            </div>
            <div className="mt-3 flex gap-2">
              <button type="button" className="btn-primary flex-1 !py-2 text-xs" disabled={value.trim().length < 8 || saving} onClick={() => save.mutate({ provider: provider.id, apiKey: value })}>{saving ? <LoaderCircle size={14} className="animate-spin" /> : <KeyRound size={14} />} {status?.configured ? "Replace" : "Save key"}</button>
              {status?.configured && <button type="button" className="btn-outline !px-3 !py-2 text-red-600" disabled={deleting} onClick={() => { if (window.confirm(`Remove your ${provider.name} API key?`)) remove.mutate(provider.id); }} aria-label={`Remove ${provider.name} key`}><Trash2 size={14} /></button>}
            </div>
          </div>;
        })}
      </div>
      {isLoading && <p className="mt-3 text-xs text-slate-400">Loading saved providers...</p>}
      <p className="mt-4 text-xs leading-relaxed text-slate-500">Suvyon never returns the full key to your browser. Provider usage and charges remain attached to your provider account.</p>
    </section>
  );
}
