import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import ReactMarkdown from "react-markdown";
import { Bot, Plus, Send, Trash2 } from "lucide-react";
import { StatusBubble } from "@/components/StatusBubble";
import { getErrorMessage } from "@/lib/api";
import { sendOnEnter } from "@/lib/keyboard";
import { agentsApi, modelsApi } from "@/lib/services";
import type { ChatHistoryItem } from "@/types/api";
import { cn } from "@/lib/utils";

export function AgentsPage() {
  const { workspaceId = "", agentId } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [showCreate, setShowCreate] = useState(false);
  const [name, setName] = useState("Search Agent");
  const [instructions, setInstructions] = useState(
    "You are a helpful assistant with web search capability. Always use web_search for current prices, news, scores, and live facts.",
  );
  const [description, setDescription] = useState("");
  const [provider, setProvider] = useState("groq");
  const [model, setModel] = useState("openai/gpt-oss-20b");
  const [selectedTools, setSelectedTools] = useState<string[]>(["web_search"]);
  const [error, setError] = useState("");

  const [message, setMessage] = useState("");
  const [history, setHistory] = useState<ChatHistoryItem[]>([]);
  const [running, setRunning] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  const { data: agents = [] } = useQuery({
    queryKey: ["agents", workspaceId],
    queryFn: () => agentsApi.list(workspaceId),
  });
  const { data: tools = [] } = useQuery({
    queryKey: ["agent-tools", workspaceId],
    queryFn: () => agentsApi.tools(workspaceId),
  });
  const { data: models = [] } = useQuery({
    queryKey: ["models"],
    queryFn: modelsApi.list,
  });
  const { data: selectedAgent } = useQuery({
    queryKey: ["agent", workspaceId, agentId],
    queryFn: () => agentsApi.get(workspaceId, agentId!),
    enabled: !!agentId,
  });

  const providers = useMemo(
    () => Array.from(new Set(models.map((m) => m.provider))),
    [models],
  );
  const providerModels = models.filter((m) => !provider || m.provider === provider);
  const usesWebSearch = (selectedAgent?.tools || "").includes("web_search");
  const statusSteps = usesWebSearch
    ? ["Searching the web…", "Reading sources…", "Writing an answer…"]
    : ["Thinking…", "Preparing a reply…"];

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [history, running]);

  const createAgent = useMutation({
    mutationFn: () =>
      agentsApi.create(workspaceId, {
        name,
        description: description || null,
        instructions,
        provider: provider || null,
        model: model || null,
        tools: selectedTools.join(",") || null,
      }),
    onSuccess: (agent) => {
      queryClient.invalidateQueries({ queryKey: ["agents", workspaceId] });
      setShowCreate(false);
      setHistory([]);
      navigate(`/app/w/${workspaceId}/agents/${agent.id}`);
    },
    onError: (err) => setError(getErrorMessage(err)),
  });

  const deleteAgent = useMutation({
    mutationFn: (id: string) => agentsApi.remove(workspaceId, id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ["agents", workspaceId] });
      if (id === agentId) {
        setHistory([]);
        navigate(`/app/w/${workspaceId}/agents`);
      }
    },
  });

  async function runAgent(e: FormEvent) {
    e.preventDefault();
    if (!agentId || !message.trim()) return;
    setRunning(true);
    setError("");
    const userMessage = message.trim();
    setMessage("");
    setHistory((prev) => [...prev, { role: "user", content: userMessage }]);
    try {
      const result = await agentsApi.run(workspaceId, agentId, {
        content: userMessage,
        history,
      });
      setHistory((prev) => [...prev, { role: "assistant", content: result.content }]);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setRunning(false);
    }
  }

  return (
    <div className="flex h-[calc(100vh-4rem)] gap-4">
      <aside className="panel flex w-72 shrink-0 flex-col overflow-hidden">
        <div className="flex items-center justify-between border-b border-ink-200/70 p-4">
          <div className="font-semibold">Agents</div>
          <button
            type="button"
            className="btn-ghost px-2 py-2"
            onClick={() => setShowCreate((v) => !v)}
          >
            <Plus size={16} />
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-2">
          {agents.map((a) => (
            <div
              key={a.id}
              className={cn(
                "group mb-1 flex items-center gap-1 rounded-xl px-2 py-2 text-sm",
                a.id === agentId ? "bg-ink-950 text-white" : "hover:bg-ink-50",
              )}
            >
              <Link
                to={`/app/w/${workspaceId}/agents/${a.id}`}
                className="min-w-0 flex-1"
                onClick={() => setHistory([])}
              >
                <div className="truncate font-medium">{a.name}</div>
                <div
                  className={cn(
                    "truncate text-xs",
                    a.id === agentId ? "text-white/70" : "text-ink-400",
                  )}
                >
                  {a.tools || "no tools"}
                </div>
              </Link>
              <button
                type="button"
                className="rounded-lg p-1 opacity-0 group-hover:opacity-100"
                onClick={() => deleteAgent.mutate(a.id)}
              >
                <Trash2 size={14} />
              </button>
            </div>
          ))}
        </div>
      </aside>

      <section className="card flex min-w-0 flex-1 flex-col overflow-hidden">
        {showCreate ? (
          <div className="overflow-y-auto p-6">
            <h2 className="text-xl font-semibold">Create agent</h2>
            <p className="mt-1 text-sm text-ink-500">
              Configure instructions, model, and tools. Users chat with the agent —
              the backend sends tool schemas to the model automatically.
            </p>
            <form
              className="mt-6 grid max-w-2xl gap-4"
              onSubmit={(e) => {
                e.preventDefault();
                setError("");
                createAgent.mutate();
              }}
            >
              <div>
                <label className="label">Name</label>
                <input className="input" required value={name} onChange={(e) => setName(e.target.value)} />
              </div>
              <div>
                <label className="label">Description</label>
                <input
                  className="input"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                />
              </div>
              <div>
                <label className="label">Instructions</label>
                <textarea
                  className="input min-h-[110px]"
                  value={instructions}
                  onChange={(e) => setInstructions(e.target.value)}
                />
              </div>
              <div className="grid gap-3 md:grid-cols-2">
                <div>
                  <label className="label">Provider</label>
                  <select
                    className="input"
                    value={provider}
                    onChange={(e) => {
                      const next = e.target.value;
                      setProvider(next);
                      const first = models.find((m) =>
                        next ? m.provider === next : false,
                      );
                      setModel(first?.model_id || "");
                    }}
                  >
                    <option value="">Auto</option>
                    {providers.map((p) => (
                      <option key={p} value={p}>
                        {p}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="label">Model</label>
                  <select
                    className="input"
                    value={model}
                    onChange={(e) => setModel(e.target.value)}
                  >
                    <option value="">Default</option>
                    {providerModels.map((m) => (
                      <option key={m.model_id} value={m.model_id}>
                        {m.display_name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <div>
                <label className="label">Tools</label>
                <div className="flex flex-wrap gap-2">
                  {tools.map((tool) => {
                    const active = selectedTools.includes(tool);
                    return (
                      <button
                        key={tool}
                        type="button"
                        className={cn(
                          "rounded-full px-3 py-1.5 text-sm font-medium",
                          active
                            ? "bg-accent text-white"
                            : "bg-ink-100 text-ink-700",
                        )}
                        onClick={() =>
                          setSelectedTools((prev) =>
                            active ? prev.filter((t) => t !== tool) : [...prev, tool],
                          )
                        }
                      >
                        {tool}
                      </button>
                    );
                  })}
                </div>
              </div>
              {error && (
                <div className="rounded-xl bg-red-50 px-3 py-2 text-sm text-red-700">
                  {error}
                </div>
              )}
              <div className="flex gap-2">
                <button className="btn-primary" disabled={createAgent.isPending}>
                  Create agent
                </button>
                <button
                  type="button"
                  className="btn-outline"
                  onClick={() => setShowCreate(false)}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        ) : !agentId ? (
          <div className="flex flex-1 flex-col items-center justify-center gap-3 p-8 text-center">
            <Bot className="text-accent" size={36} />
            <div className="text-lg font-semibold">Select or create an agent</div>
            <p className="max-w-md text-sm text-ink-500">
              Agents are reusable personas with instructions and tools. Create one,
              then chat with it here.
            </p>
            <button className="btn-accent" onClick={() => setShowCreate(true)}>
              <Plus size={16} />
              New agent
            </button>
          </div>
        ) : (
          <>
            <div className="border-b border-teal-100 bg-gradient-to-r from-teal-50 to-white p-4">
              <div className="flex items-center gap-2">
                <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-teal-600 text-white">
                  <Bot size={16} />
                </span>
                <div>
                  <div className="text-lg font-semibold">{selectedAgent?.name || "Agent"}</div>
                  <div className="text-sm text-ink-500">
                    {selectedAgent?.provider || "auto"} / {selectedAgent?.model || "default"} · tools:{" "}
                    {selectedAgent?.tools || "none"}
                  </div>
                </div>
              </div>
            </div>
            <div className="flex-1 space-y-4 overflow-y-auto bg-[radial-gradient(circle_at_top_right,rgba(13,148,136,0.08),transparent_40%)] p-5">
              {history.length === 0 && !running && (
                <p className="text-sm text-ink-500">
                  Ask this agent something. Press Enter to send, Shift+Enter for a new line.
                  {usesWebSearch ? " Live questions will search the web first." : ""}
                </p>
              )}
              {history.map((item, idx) => (
                <div
                  key={`${item.role}-${idx}`}
                  className={cn(
                    "max-w-3xl rounded-2xl px-4 py-3 text-sm leading-relaxed",
                    item.role === "user"
                      ? "ml-auto bg-teal-800 text-white"
                      : "bg-white text-ink-900 shadow-sm ring-1 ring-teal-100",
                  )}
                >
                  {item.role === "assistant" ? (
                    <ReactMarkdown>{item.content}</ReactMarkdown>
                  ) : (
                    item.content
                  )}
                </div>
              ))}
              <StatusBubble active={running} steps={statusSteps} />
              <div ref={bottomRef} />
            </div>
            <form onSubmit={runAgent} className="border-t border-teal-100 bg-white/80 p-4">
              {error && (
                <div className="mb-3 rounded-xl bg-red-50 px-3 py-2 text-sm text-red-700">
                  {error}
                </div>
              )}
              <div className="flex gap-2">
                <textarea
                  className="input min-h-[52px] resize-none"
                  placeholder="Message this agent… (Enter to send)"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyDown={sendOnEnter}
                />
                <button
                  type="submit"
                  className="btn-primary px-4"
                  disabled={running || !message.trim()}
                >
                  <Send size={16} />
                </button>
              </div>
            </form>
          </>
        )}
      </section>
    </div>
  );
}
