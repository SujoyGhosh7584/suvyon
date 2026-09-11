import { useEffect, useRef, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { AlertCircle, CheckCircle2, LoaderCircle, Square } from "lucide-react";
import { agentsApi } from "@/lib/services";
import { getErrorMessage } from "@/lib/api";
import type { Agent, ModelInfo, PendingEmailDraft } from "@/types/api";

const active = (status: string) => ["queued", "running", "stopping"].includes(status);

export function useAgentExecution(workspaceId: string, agentId: string | undefined, agent: Agent | undefined, onDraft: (draft: PendingEmailDraft | null) => void) {
  const client = useQueryClient();
  const [choice, setChoice] = useState("");
  const [error, setError] = useState("");
  const [draftRunId, setDraftRunId] = useState<string>();
  const draftSeen = useRef("");
  const key = ["agent-runs", workspaceId, agentId];
  const query = useQuery({
    queryKey: key, enabled: !!agentId,
    queryFn: () => agentsApi.runs(workspaceId, agentId!),
    refetchInterval: (q) => q.state.data?.some((r) => active(r.status)) ? 1500 : false,
  });
  const runs = query.data || [];
  const latest = runs[0];
  const running = runs.some((r) => active(r.status));
  useEffect(() => {
    setChoice(agent?.provider || agent?.model ? `${agent?.provider || ""}|${agent?.model || ""}` : "");
    setError("");
  }, [agent?.id, agent?.provider, agent?.model]);
  useEffect(() => { onDraft(null); setDraftRunId(undefined); draftSeen.current = ""; }, [workspaceId, agentId, onDraft]);
  useEffect(() => {
    if (!latest) return;
    void client.invalidateQueries({ queryKey: ["agent-messages", workspaceId, agentId] });
    if (latest.status === "awaiting_approval" && latest.pending_email && draftSeen.current !== latest.id) {
      draftSeen.current = latest.id;
      setDraftRunId(latest.id);
      onDraft(latest.pending_email);
    }
  }, [latest?.id, latest?.status, workspaceId, agentId, client, onDraft]);
  async function start(content: string) {
    const [provider, model] = choice.split("|");
    const run = await agentsApi.startRun(workspaceId, agentId!, { content, provider: provider || null, model: model || null });
    client.setQueryData(key, [run, ...runs]);
    return run;
  }
  async function stop() {
    const current = runs.find((r) => active(r.status));
    if (!current) return;
    try {
      await agentsApi.stopRun(workspaceId, agentId!, current.id);
      await client.invalidateQueries({ queryKey: key });
    } catch (err) { setError(getErrorMessage(err)); }
  }
  function reviewDraft(id: string) {
    const run = runs.find((r) => r.id === id);
    if (run?.status === "awaiting_approval" && run.pending_email) {
      setDraftRunId(id);
      onDraft(run.pending_email);
    }
  }
  return { runs, running, start, stop, choice, setChoice, draftRunId, reviewDraft, error: error || (query.error ? getErrorMessage(query.error) : "") };
}

export function AgentActivity({ execution, models }: { execution: ReturnType<typeof useAgentExecution>; models: ModelInfo[] }) {
  const { runs, running, choice, setChoice } = execution;
  const knownChoice = !choice || models.some((m) => `${m.provider}|${m.model_id}` === choice);
  return <section aria-label="Agent execution" className="message-bubble-assistant w-full space-y-3 rounded-2xl border border-accent/20 bg-white p-3 text-slate-900">
    <label className="block text-xs font-semibold">Model for the next task
      <select className="input mt-1 text-sm" value={choice} disabled={running} onChange={(e) => setChoice(e.target.value)}>
        <option value="">Auto · choose an available model</option>
        {!knownChoice && <option value={choice}>{choice.replace("|", " / ")} · saved selection</option>}
        {models.map((m) => <option key={`${m.provider}|${m.model_id}`} value={`${m.provider}|${m.model_id}`}>{m.provider} · {m.display_name}</option>)}
      </select>
    </label>
    {execution.error && <p role="alert" className="text-sm text-red-700">{execution.error}</p>}
    {running && <button type="button" className="btn-outline text-sm" onClick={() => void execution.stop()}><Square size={14} /> Stop task</button>}
    {runs.filter((run) => active(run.status) || run.status === "awaiting_approval").slice(0, 1).map((run) => <details key={run.id} open className="rounded-xl border border-accent/20 p-3">
      <summary className="cursor-pointer text-sm font-medium">
        <span className="inline-flex items-center gap-2">{active(run.status) ? <LoaderCircle size={14} className="animate-spin" /> : run.status === "completed" ? <CheckCircle2 size={14} /> : <AlertCircle size={14} />}{run.status.replace(/_/g, " ")}</span>
        <span className="ml-2 font-normal text-slate-500">{run.input.slice(0, 70)}</span>
      </summary>
      {run.status === "stopping" && <p role="status" className="mt-2 text-xs">Stopping after the in-flight request returns. No further tools will start.</p>}
      {run.status === "awaiting_approval" && <button type="button" className="btn-outline mt-2 text-xs" onClick={() => execution.reviewDraft(run.id)}>Review email draft</button>}
      <p className="mt-2 text-xs text-slate-500">Requested: {run.config.provider || "Auto"} / {run.config.model || "default"}{run.provider && <> · Responded: {run.provider} / {run.model}</>}</p>
      <ol className="mt-3 max-h-72 space-y-2 overflow-y-auto border-l border-teal-200 pl-3">
        {run.events.map((event, i) => <li key={i} className="text-xs">
          <span className={event.kind.includes("failed") || event.kind === "error" ? "text-red-700" : "text-slate-700"}>{event.summary}</span>
          {event.model && <span className="ml-1 text-slate-500">({event.provider}/{event.model})</span>}
          {(event.arguments || event.output) && <details className="mt-1"><summary className="cursor-pointer text-teal-700">Details</summary><pre className="max-h-48 overflow-auto whitespace-pre-wrap break-words rounded bg-slate-50 p-2">{event.output || JSON.stringify(event.arguments, null, 2)}</pre></details>}
        </li>)}
      </ol>
      {!active(run.status) && run.content && <p className="mt-3 whitespace-pre-wrap text-xs text-slate-600">{run.content.slice(0, 400)}{run.content.length > 400 ? "… See the full answer in chat." : ""}</p>}
    </details>)}
  </section>;
}
