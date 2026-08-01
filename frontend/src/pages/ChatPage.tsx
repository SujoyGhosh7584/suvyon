import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import ReactMarkdown from "react-markdown";
import { Plus, Send, Trash2 } from "lucide-react";
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

  const providers = useMemo(
    () => Array.from(new Set(models.map((m) => m.provider))),
    [models],
  );
  const providerModels = models.filter((m) => !provider || m.provider === provider);

  useEffect(() => {
    setOptimistic([]);
  }, [conversationId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, optimistic]);

  const createConversation = useMutation({
    mutationFn: () =>
      conversationsApi.create(workspaceId, {
        title: "New conversation",
        provider: provider || null,
        model: model || null,
      }),
    onSuccess: (c) => {
      queryClient.invalidateQueries({ queryKey: ["conversations", workspaceId] });
      navigate(`/app/w/${workspaceId}/chat/${c.id}`);
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

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    if (!conversationId) {
      const created = await createConversation.mutateAsync();
      navigate(`/app/w/${workspaceId}/chat/${created.id}`);
      // send after navigation by storing content - simpler: send after create in same flow
      const text = content.trim();
      if (!text) return;
      setContent("");
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
      } catch (err) {
        setError(getErrorMessage(err));
      }
      return;
    }
    sendMessage.mutate();
  }

  return (
    <div className="flex h-[calc(100vh-4rem)] gap-4">
      <aside className="panel flex w-72 shrink-0 flex-col overflow-hidden">
        <div className="flex items-center justify-between border-b border-ink-200/70 p-4">
          <div className="font-semibold">Chats</div>
          <button
            type="button"
            className="btn-ghost px-2 py-2"
            onClick={() => createConversation.mutate()}
            title="New chat"
          >
            <Plus size={16} />
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-2">
          {conversations.map((c) => (
            <div
              key={c.id}
              className={cn(
                "group mb-1 flex items-center gap-1 rounded-xl px-2 py-2 text-sm",
                c.id === conversationId ? "bg-ink-950 text-white" : "hover:bg-ink-50",
              )}
            >
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
                onClick={() => deleteConversation.mutate(c.id)}
              >
                <Trash2 size={14} />
              </button>
            </div>
          ))}
          {conversations.length === 0 && (
            <p className="px-2 py-4 text-sm text-ink-500">No chats yet.</p>
          )}
        </div>
      </aside>

      <section className="card flex min-w-0 flex-1 flex-col overflow-hidden">
        <div className="flex flex-wrap items-center gap-2 border-b border-ink-200/70 p-4">
          <select
            className="input max-w-[160px]"
            value={provider}
            onChange={(e) => {
              setProvider(e.target.value);
              setModel("");
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
            className="input max-w-[220px]"
            value={model}
            onChange={(e) => setModel(e.target.value)}
          >
            <option value="">Default model</option>
            {providerModels.map((m) => (
              <option key={`${m.provider}-${m.model_id}`} value={m.model_id}>
                {m.display_name}
              </option>
            ))}
          </select>
          <select
            className="input max-w-[140px]"
            value={mode}
            onChange={(e) => setMode(e.target.value as "auto" | "chat" | "rag" | "web")}
          >
            <option value="auto">Auto</option>
            <option value="chat">General</option>
            <option value="rag">RAG</option>
            <option value="web">Web</option>
          </select>
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
          <div ref={bottomRef} />
        </div>

        <form onSubmit={onSubmit} className="border-t border-ink-200/70 p-4">
          {error && (
            <div className="mb-3 rounded-xl bg-red-50 px-3 py-2 text-sm text-red-700">
              {error}
            </div>
          )}
          <div className="mb-3 text-xs text-ink-500">
            Auto will use web search for current topics and your uploaded documents for document questions.
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
              disabled={sendMessage.isPending || createConversation.isPending || !content.trim()}
            >
              <Send size={16} />
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}
