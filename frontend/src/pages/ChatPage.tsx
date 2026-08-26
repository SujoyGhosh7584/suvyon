import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import ReactMarkdown from "react-markdown";
import {
  Check,
  Edit2,
  PanelLeftClose,
  PanelLeftOpen,
  Plus,
  Send,
  Trash2,
  X,
} from "lucide-react";
import { getErrorMessage } from "@/lib/api";
import { conversationsApi, modelsApi } from "@/lib/services";
import type { Message } from "@/types/api";
import { cn } from "@/lib/utils";

export function ChatPage() {
  const { workspaceId = "", conversationId } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const bottomRef = useRef<HTMLDivElement>(null);

  const [content, setContent] = useState("");
  const [provider, setProvider] = useState("");
  const [model, setModel] = useState("");
  const [mode, setMode] = useState<"auto" | "chat" | "rag" | "web">("auto");
  const [error, setError] = useState("");
  const [optimistic, setOptimistic] = useState<Message[]>([]);
  const [isSending, setIsSending] = useState(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  const [editingId, setEditingId] = useState<string | null>(null);
  const [editingTitle, setEditingTitle] = useState("");

  const { data: conversations = [] } = useQuery({
    queryKey: ["conversations", workspaceId],
    queryFn: () => conversationsApi.list(workspaceId),
  });
  const { data: messages = [], isLoading: messagesLoading } = useQuery({
    queryKey: ["messages", workspaceId, conversationId],
    queryFn: () => conversationsApi.messages(workspaceId, conversationId!),
    enabled: !!conversationId,
  });
  const { data: models = [] } = useQuery({
    queryKey: ["models"],
    queryFn: modelsApi.list,
  });

  const activeConversation = useMemo(
    () => conversations.find((c) => c.id === conversationId),
    [conversations, conversationId],
  );

  const providers = useMemo(
    () => Array.from(new Set(models.map((m) => m.provider))),
    [models],
  );
  const providerModels = models.filter((m) => !provider || m.provider === provider);

  useEffect(() => {
    setOptimistic([]);
  }, [conversationId]);

  useEffect(() => {
    if (!conversationId || !activeConversation) return;
    setProvider(activeConversation.provider || "");
    setModel(activeConversation.model || "");
  }, [conversationId, activeConversation?.id]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, optimistic]);

  const createConversation = useMutation({
    mutationFn: () =>
      conversationsApi.create(workspaceId, {
        title: "New chat",
        provider: provider || null,
        model: model || null,
      }),
    onSuccess: (c) => {
      queryClient.invalidateQueries({ queryKey: ["conversations", workspaceId] });
      navigate(`/app/w/${workspaceId}/chat/${c.id}`);
    },
  });

  const renameConversation = useMutation({
    mutationFn: ({ id, title }: { id: string; title: string }) =>
      conversationsApi.update(workspaceId, id, { title }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["conversations", workspaceId] });
      setEditingId(null);
    },
    onError: (err) => {
      setError(getErrorMessage(err));
    },
  });

  const sendMessage = useMutation({
    mutationFn: async () => {
      if (!conversationId) throw new Error("Select a conversation first.");
      const text = content.trim();
      if (!text) throw new Error("Message cannot be empty.");
      setContent("");
      setOptimistic((prev) => [
        ...prev,
        {
          id: `temp-${Date.now()}`,
          conversation_id: conversationId,
          role: "user",
          content: text,
          provider: null,
          model: null,
          prompt_tokens: null,
          completion_tokens: null,
          is_edited: false,
        },
      ]);
      return conversationsApi.sendMessage(workspaceId, conversationId, {
        content: text,
        provider: provider || null,
        model: model || null,
        knowledge_base_id: null,
        mode: mode === "auto" ? null : mode,
      });
    },
    onSuccess: () => {
      setOptimistic([]);
      queryClient.invalidateQueries({
        queryKey: ["messages", workspaceId, conversationId],
      });
      queryClient.invalidateQueries({
        queryKey: ["conversations", workspaceId],
      });
    },
    onError: (err) => {
      setOptimistic([]);
      setError(getErrorMessage(err));
    },
  });

  const deleteConversation = useMutation({
    mutationFn: (id: string) => conversationsApi.remove(workspaceId, id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ["conversations", workspaceId] });
      if (id === conversationId) navigate(`/app/w/${workspaceId}/chat`);
    },
  });

  const visibleMessages = [...messages, ...optimistic];

  function renderMessageContent(content: string) {
    const marker = "\n\n---\n";
    const idx = content.indexOf(marker);
    if (idx === -1) {
      return { body: content, provenance: "" };
    }
    return {
      body: content.slice(0, idx),
      provenance: content.slice(idx + marker.length),
    };
  }

  function startRename(id: string, currentTitle: string) {
    setEditingId(id);
    setEditingTitle(currentTitle);
  }

  function handleSaveRename(id: string) {
    const trimmed = editingTitle.trim();
    if (!trimmed) {
      setEditingId(null);
      return;
    }
    renameConversation.mutate({ id, title: trimmed });
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    if (!conversationId) {
      const created = await createConversation.mutateAsync();
      navigate(`/app/w/${workspaceId}/chat/${created.id}`);
      const text = content.trim();
      if (!text) return;
      setContent("");
      setIsSending(true);
      try {
        await conversationsApi.sendMessage(workspaceId, created.id, {
          content: text,
          provider: provider || null,
          model: model || null,
          knowledge_base_id: null,
          mode: mode === "auto" ? null : mode,
        });
        queryClient.invalidateQueries({
          queryKey: ["messages", workspaceId, created.id],
        });
        queryClient.invalidateQueries({
          queryKey: ["conversations", workspaceId],
        });
      } catch (err) {
        setError(getErrorMessage(err));
      } finally {
        setIsSending(false);
      }
      return;
    }
    sendMessage.mutate();
  }

  return (
    <div className="flex h-[calc(100vh-4rem)] gap-4">
      <aside
        className={cn(
          "panel flex shrink-0 flex-col overflow-hidden transition-all duration-300",
          isSidebarCollapsed ? "w-14" : "w-72",
        )}
      >
        <div className="flex items-center justify-between border-b border-ink-200/70 p-3">
          {!isSidebarCollapsed && <div className="font-semibold px-1">Chats</div>}
          <div className="flex items-center gap-1">
            <button
              type="button"
              className="btn-ghost px-2 py-2"
              onClick={() => createConversation.mutate()}
              title="New chat"
            >
              <Plus size={16} />
            </button>
            <button
              type="button"
              className="btn-ghost px-2 py-2 text-ink-500 hover:text-ink-900"
              onClick={() => setIsSidebarCollapsed((prev) => !prev)}
              title={isSidebarCollapsed ? "Expand chats panel" : "Collapse chats panel"}
            >
              {isSidebarCollapsed ? (
                <PanelLeftOpen size={16} />
              ) : (
                <PanelLeftClose size={16} />
              )}
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-2">
          {!isSidebarCollapsed &&
            conversations.map((c) => (
              <div
                key={c.id}
                className={cn(
                  "group mb-1 flex items-center gap-1 rounded-xl px-2 py-2 text-sm",
                  c.id === conversationId ? "bg-ink-950 text-white" : "hover:bg-ink-50",
                )}
              >
                {editingId === c.id ? (
                  <div className="flex flex-1 items-center gap-1">
                    <input
                      type="text"
                      className="w-full rounded border border-ink-300 bg-white px-2 py-0.5 text-xs text-ink-900 focus:outline-none"
                      value={editingTitle}
                      onChange={(e) => setEditingTitle(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") handleSaveRename(c.id);
                        if (e.key === "Escape") setEditingId(null);
                      }}
                      autoFocus
                    />
                    <button
                      type="button"
                      className="p-1 text-green-600 hover:text-green-800"
                      onClick={() => handleSaveRename(c.id)}
                    >
                      <Check size={14} />
                    </button>
                    <button
                      type="button"
                      className="p-1 text-red-500 hover:text-red-700"
                      onClick={() => setEditingId(null)}
                    >
                      <X size={14} />
                    </button>
                  </div>
                ) : (
                  <>
                    <Link
                      to={`/app/w/${workspaceId}/chat/${c.id}`}
                      className="min-w-0 flex-1 truncate"
                    >
                      {c.title}
                    </Link>
                    <button
                      type="button"
                      className={cn(
                        "rounded-lg p-1 opacity-0 transition group-hover:opacity-100",
                        c.id === conversationId ? "hover:bg-white/10" : "hover:bg-ink-100",
                      )}
                      title="Rename chat"
                      onClick={() => startRename(c.id, c.title)}
                    >
                      <Edit2 size={13} />
                    </button>
                    <button
                      type="button"
                      className={cn(
                        "rounded-lg p-1 opacity-0 transition group-hover:opacity-100",
                        c.id === conversationId ? "hover:bg-white/10" : "hover:bg-ink-100",
                      )}
                      title="Delete chat"
                      onClick={() => deleteConversation.mutate(c.id)}
                    >
                      <Trash2 size={13} />
                    </button>
                  </>
                )}
              </div>
            ))}
          {isSidebarCollapsed &&
            conversations.map((c) => (
              <Link
                key={c.id}
                to={`/app/w/${workspaceId}/chat/${c.id}`}
                title={c.title}
                className={cn(
                  "mb-2 flex h-9 w-9 items-center justify-center rounded-xl font-medium text-xs transition",
                  c.id === conversationId
                    ? "bg-ink-950 text-white"
                    : "bg-ink-100 text-ink-700 hover:bg-ink-200",
                )}
              >
                {c.title.charAt(0).toUpperCase()}
              </Link>
            ))}
          {!isSidebarCollapsed && conversations.length === 0 && (
            <p className="px-2 py-4 text-sm text-ink-500">No chats yet.</p>
          )}
        </div>
      </aside>

      <section className="card flex min-w-0 flex-1 flex-col overflow-hidden">
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-ink-200/70 p-3 md:px-4">
          <div className="flex items-center gap-2">
            {activeConversation && editingId !== activeConversation.id ? (
              <div className="flex items-center gap-2">
                <span className="font-semibold text-ink-900 max-w-[200px] truncate">
                  {activeConversation.title}
                </span>
                <button
                  type="button"
                  onClick={() =>
                    startRename(activeConversation.id, activeConversation.title)
                  }
                  className="text-ink-400 hover:text-ink-700 transition"
                  title="Rename title"
                >
                  <Edit2 size={14} />
                </button>
              </div>
            ) : activeConversation && editingId === activeConversation.id ? (
              <div className="flex items-center gap-1">
                <input
                  type="text"
                  className="rounded border border-ink-300 bg-white px-2 py-1 text-sm font-semibold text-ink-900 focus:outline-none"
                  value={editingTitle}
                  onChange={(e) => setEditingTitle(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") handleSaveRename(activeConversation.id);
                    if (e.key === "Escape") setEditingId(null);
                  }}
                  autoFocus
                />
                <button
                  type="button"
                  className="p-1 text-green-600 hover:text-green-800"
                  onClick={() => handleSaveRename(activeConversation.id)}
                >
                  <Check size={16} />
                </button>
                <button
                  type="button"
                  className="p-1 text-red-500 hover:text-red-700"
                  onClick={() => setEditingId(null)}
                >
                  <X size={16} />
                </button>
              </div>
            ) : null}
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <select
              className="input max-w-[150px] text-xs py-1.5"
              value={provider}
              onChange={(e) => {
                setError("");
                const nextProvider = e.target.value;
                setProvider(nextProvider);
                const first = models.find((m) =>
                  nextProvider ? m.provider === nextProvider : true,
                );
                setModel(nextProvider && first ? first.model_id : "");
              }}
            >
              <option value="">Auto provider</option>
              {providers.map((p) => (
                <option key={p} value={p}>
                  {p}
                </option>
              ))}
            </select>
            <select
              className="input max-w-[200px] text-xs py-1.5"
              value={model}
              onChange={(e) => {
                setError("");
                const selModel = e.target.value;
                setModel(selModel);
                if (selModel && !provider) {
                  const found = models.find((m) => m.model_id === selModel);
                  if (found) setProvider(found.provider);
                }
              }}
            >
              <option value="">Default model</option>
              {providerModels.map((m) => (
                <option key={`${m.provider}-${m.model_id}`} value={m.model_id}>
                  {m.display_name} ({m.provider})
                </option>
              ))}
            </select>
            <select
              className="input max-w-[130px] text-xs py-1.5"
              value={mode}
              onChange={(e) => setMode(e.target.value as "auto" | "chat" | "rag" | "web")}
            >
              <option value="auto">Auto</option>
              <option value="chat">General</option>
              <option value="rag">RAG</option>
              <option value="web">Web</option>
            </select>
          </div>
        </div>

        <div className="flex-1 space-y-4 overflow-y-auto p-5">
          {!conversationId && (
            <div className="flex h-full items-center justify-center text-sm text-ink-500">
              Start a new chat or select one from the sidebar.
            </div>
          )}
          {conversationId && messagesLoading && (
            <div className="text-sm text-ink-500">Loading messages…</div>
          )}
          {visibleMessages.map((m) => (
            <div
              key={m.id}
              className={cn(
                "max-w-3xl rounded-2xl px-4 py-3 text-sm leading-relaxed",
                m.role === "user"
                  ? "ml-auto bg-ink-950 text-white"
                  : "bg-ink-50 text-ink-900",
              )}
            >
              {m.role === "assistant" ? (
                (() => {
                  const { body, provenance } = renderMessageContent(m.content);
                  return (
                    <div className="space-y-2">
                      {body ? <ReactMarkdown>{body}</ReactMarkdown> : null}
                      {provenance ? (
                        <div className="rounded-lg border border-ink-200/70 bg-white/70 px-3 py-2 text-xs text-ink-600">
                          <span className="font-semibold text-ink-700">Source:</span> {provenance}
                        </div>
                      ) : null}
                    </div>
                  );
                })()
              ) : (
                m.content
              )}
            </div>
          ))}
          {(sendMessage.isPending || isSending) && (
            <div className="max-w-3xl rounded-2xl bg-ink-50 px-4 py-3 text-sm text-ink-500">
              Thinking…
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        <form onSubmit={onSubmit} className="border-t border-ink-200/70 p-4">
          {error && (
            <div className="mb-3 rounded-xl bg-red-50 px-3 py-2 text-sm text-red-700">
              {error}
            </div>
          )}
          <div className="mb-3 text-xs text-ink-500">
            Auto mode automatically searches web topics or queries your knowledge base documents when relevant.
          </div>
          <div className="flex gap-2">
            <textarea
              className="input min-h-[52px] resize-none"
              placeholder="Ask about your docs, the web, or anything else…"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  const form = e.currentTarget.form;
                  if (form) form.requestSubmit();
                }
              }}
            />
            <button
              className="btn-primary px-4"
              disabled={
                sendMessage.isPending ||
                createConversation.isPending ||
                isSending ||
                !content.trim()
              }
            >
              <Send size={16} />
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}

