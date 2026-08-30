import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, Bot, Plus, Send, Trash2 } from "lucide-react";
import { MessageContent } from "@/components/MessageContent";
import { MobileMascot } from "@/components/MobileMascot";
import { StatusBubble } from "@/components/StatusBubble";
import { getErrorMessage } from "@/lib/api";
import { sendOnEnter } from "@/lib/keyboard";
import { AGENT_TEMPLATES, TEMPLATE_ICONS } from "@/lib/agentTemplates";
import { agentsApi, modelsApi } from "@/lib/services";
import type { ChatHistoryItem } from "@/types/api";
import { cn } from "@/lib/utils";

export function MobileAgentsPage() {
  const { workspaceId = "", agentId } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [showCreate, setShowCreate] = useState(false);
  const [templateId, setTemplateId] = useState<(typeof AGENT_TEMPLATES)[number]["id"]>("search");
  const [name, setName] = useState<string>(AGENT_TEMPLATES[0].name);
  const [instructions, setInstructions] = useState<string>(AGENT_TEMPLATES[0].instructions);
  const [description, setDescription] = useState<string>(AGENT_TEMPLATES[0].description);
  const [provider, setProvider] = useState("groq");
  const [model, setModel] = useState("openai/gpt-oss-20b");
  const [selectedTools, setSelectedTools] = useState<string[]>([...AGENT_TEMPLATES[0].tools]);
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
  const usesEmail =
    (selectedAgent?.tools || "").includes("draft_email") ||
    (selectedAgent?.tools || "").includes("send_email");
  const usesStudio =
    (selectedAgent?.tools || "").includes("generate_image") ||
    (selectedAgent?.tools || "").includes("generate_storyboard");
  const statusSteps = usesStudio
    ? ["Directing the scene…", "Rendering visuals…", "Packaging the reply…"]
    : usesEmail
      ? ["Drafting the email…", "Checking send approval…", "Writing a reply…"]
      : usesWebSearch
        ? ["Searching the web…", "Reading sources…", "Writing an answer…"]
        : ["Thinking…", "Preparing a reply…"];

  function applyTemplate(id: (typeof AGENT_TEMPLATES)[number]["id"]) {
    const template = AGENT_TEMPLATES.find((item) => item.id === id);
    if (!template) return;
    setTemplateId(template.id);
    setName(template.name);
    setDescription(template.description);
    setInstructions(template.instructions);
    setSelectedTools([...template.tools]);
  }

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

  if (showCreate) {
    return (
      <div className="flex h-full flex-col bg-white/80">
        <div className="flex items-center gap-2 border-b border-rose-100 px-3 py-2.5">
          <button type="button" className="rounded-xl p-2" onClick={() => setShowCreate(false)}>
            <ArrowLeft size={20} />
          </button>
          <h2 className="font-display text-lg font-bold">New agent</h2>
        </div>
        <form
          className="flex-1 space-y-4 overflow-y-auto px-4 py-4"
          onSubmit={(e) => {
            e.preventDefault();
            setError("");
            createAgent.mutate();
          }}
        >
          <div className="grid grid-cols-2 gap-2">
            {AGENT_TEMPLATES.map((template) => {
              const active = templateId === template.id;
              const Icon = TEMPLATE_ICONS[template.id];
              return (
                <button
                  key={template.id}
                  type="button"
                  className={cn(
                    "rounded-[1.2rem] border px-3 py-3 text-left",
                    active ? "border-accent bg-accent/10" : "border-ink-200 bg-white",
                  )}
                  onClick={() => applyTemplate(template.id)}
                >
                  <Icon size={16} className="mb-1" />
                  <span className="block text-xs font-bold">{template.name}</span>
                </button>
              );
            })}
          </div>
          <input className="input" required value={name} onChange={(e) => setName(e.target.value)} />
          <input
            className="input"
            placeholder="Description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
          <textarea
            className="input min-h-[90px]"
            value={instructions}
            onChange={(e) => setInstructions(e.target.value)}
          />
          <div className="grid grid-cols-2 gap-2">
            <select
              className="input"
              value={provider}
              onChange={(e) => {
                const next = e.target.value;
                setProvider(next);
                const first = models.find((m) => (next ? m.provider === next : false));
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
            <select className="input" value={model} onChange={(e) => setModel(e.target.value)}>
              <option value="">Default</option>
              {providerModels.map((m) => (
                <option key={m.model_id} value={m.model_id}>
                  {m.display_name}
                </option>
              ))}
            </select>
          </div>
          <div className="flex flex-wrap gap-2">
            {tools.map((tool) => {
              const active = selectedTools.includes(tool);
              return (
                <button
                  key={tool}
                  type="button"
                  className={cn(
                    "rounded-full px-3 py-1.5 text-xs font-medium",
                    active ? "bg-accent text-white" : "bg-ink-100 text-ink-700",
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
          {error && <div className="rounded-xl bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>}
          <button className="btn-primary w-full" disabled={createAgent.isPending}>
            Create agent
          </button>
        </form>
      </div>
    );
  }

  if (!agentId) {
    return (
      <div className="relative flex h-full flex-col px-4 pb-4 pt-1">
        <div className="mb-4 text-center">
          <MobileMascot />
          <h1 className="mt-2 font-display text-2xl font-extrabold">Your agents</h1>
          <p className="mt-1 text-sm text-ink-500">Tiny helpers with tools.</p>
        </div>
        <div className="min-h-0 flex-1 space-y-2 overflow-y-auto pb-20">
          {agents.map((a) => (
            <div
              key={a.id}
              className="flex items-center gap-2 rounded-[1.4rem] bg-white/90 p-2 shadow-sm ring-1 ring-rose-100"
            >
              <Link
                to={`/app/w/${workspaceId}/agents/${a.id}`}
                className="flex min-w-0 flex-1 items-center gap-3 px-1 py-1"
                onClick={() => setHistory([])}
              >
                <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-rose-500 text-white">
                  <Bot size={18} />
                </span>
                <span className="min-w-0">
                  <span className="block truncate font-semibold">{a.name}</span>
                  <span className="block truncate text-[11px] text-ink-400">{a.tools || "no tools"}</span>
                </span>
              </Link>
              <button
                type="button"
                className="rounded-xl p-2 text-ink-400"
                onClick={() => deleteAgent.mutate(a.id)}
              >
                <Trash2 size={16} />
              </button>
            </div>
          ))}
          {agents.length === 0 && (
            <div className="rounded-[1.6rem] bg-white/80 px-5 py-8 text-center text-sm text-ink-500">
              No agents yet. Make a search buddy or an email helper.
            </div>
          )}
        </div>
        <button
          type="button"
          className="absolute bottom-6 right-5 flex h-14 w-14 items-center justify-center rounded-full bg-rose-500 text-white shadow-glow"
          onClick={() => setShowCreate(true)}
        >
          <Plus size={24} />
        </button>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col bg-white/70">
      <div className="flex items-center gap-2 border-b border-rose-100 bg-white/90 px-3 py-2.5">
        <button
          type="button"
          className="rounded-xl p-2"
          onClick={() => {
            setHistory([]);
            navigate(`/app/w/${workspaceId}/agents`);
          }}
        >
          <ArrowLeft size={20} />
        </button>
        <div className="min-w-0 flex-1">
          <div className="truncate font-display font-bold">{selectedAgent?.name || "Agent"}</div>
          <div className="truncate text-[11px] text-ink-400">{selectedAgent?.tools || "no tools"}</div>
        </div>
      </div>
      <div className="flex-1 space-y-3 overflow-y-auto px-3 py-4">
        {history.length === 0 && !running && (
          <p className="px-2 text-center text-sm text-ink-500">
            Say hi to this agent.
            {usesWebSearch ? " It can search the live web." : ""}
            {usesEmail ? " Emails send only after you confirm." : ""}
            {usesStudio ? " Ask for images, clips, or a brand kit." : ""}
          </p>
        )}
        {history.map((item, idx) => (
          <div
            key={`${item.role}-${idx}`}
            className={cn(
              "max-w-[88%] rounded-[1.35rem] px-3.5 py-2.5 text-sm leading-relaxed",
              item.role === "user"
                ? "ml-auto rounded-br-md bg-rose-500 text-white"
                : "rounded-bl-md bg-white text-ink-900 shadow-sm ring-1 ring-rose-100",
            )}
          >
            {item.role === "assistant" ? <MessageContent content={item.content} /> : item.content}
          </div>
        ))}
        <StatusBubble active={running} steps={statusSteps} />
        <div ref={bottomRef} />
      </div>
      <form onSubmit={runAgent} className="border-t border-rose-100 bg-white px-3 py-2.5">
        {error && (
          <div className="mb-2 rounded-xl bg-red-50 px-3 py-2 text-xs text-red-700">{error}</div>
        )}
        <div className="flex items-end gap-2">
          <textarea
            className="input min-h-[46px] max-h-32 resize-none py-2.5"
            placeholder="Message this agent…"
            rows={1}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={sendOnEnter}
          />
          <button
            type="submit"
            className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-rose-500 text-white disabled:opacity-50"
            disabled={running || !message.trim()}
          >
            <Send size={18} />
          </button>
        </div>
      </form>
    </div>
  );
}
