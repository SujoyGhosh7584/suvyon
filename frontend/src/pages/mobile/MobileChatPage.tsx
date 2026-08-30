import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, Check, Edit2, MessageCircleHeart, Plus, Send, SlidersHorizontal, Trash2, X } from "lucide-react";
import { MobileMascot } from "@/components/MobileMascot";
import { MessageContent } from "@/components/MessageContent";
import { StatusBubble } from "@/components/StatusBubble";
import { getErrorMessage } from "@/lib/api";
import { sendOnEnter } from "@/lib/keyboard";
import { splitProvenance } from "@/lib/messageFormat";
import { conversationsApi, modelsApi } from "@/lib/services";
import type { Message } from "@/types/api";
import { cn } from "@/lib/utils";

const BUBBLE_COLORS = [
  "from-violet-500 to-indigo-500",
  "from-rose-400 to-orange-400",
  "from-teal-400 to-sky-500",
  "from-amber-400 to-pink-400",
];

export function MobileChatPage() {
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
  const [showTune, setShowTune] = useState(false);
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
    onError: (err) => setError(getErrorMessage(err)),
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
      queryClient.invalidateQueries({ queryKey: ["messages", workspaceId, conversationId] });
      queryClient.invalidateQueries({ queryKey: ["conversations", workspaceId] });
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
        queryClient.invalidateQueries({ queryKey: ["messages", workspaceId, created.id] });
        queryClient.invalidateQueries({ queryKey: ["conversations", workspaceId] });
      } catch (err) {
        setError(getErrorMessage(err));
      } finally {
        setIsSending(false);
      }
      return;
    }
    sendMessage.mutate();
  }

  if (!conversationId) {
    return (
      <div className="relative flex h-full flex-col px-4 pb-4 pt-1">
        <div className="mb-4 text-center">
          <MobileMascot />
          <h1 className="mt-2 font-display text-2xl font-extrabold text-ink-950">Your chats</h1>
          <p className="mt-1 text-sm text-ink-500">Little threads. Big answers.</p>
        </div>
        <div className="min-h-0 flex-1 space-y-2 overflow-y-auto pb-20">
          {conversations.map((c, i) => (
            <div
              key={c.id}
              className="flex items-center gap-2 rounded-[1.4rem] bg-white/90 p-2 shadow-sm ring-1 ring-violet-100"
            >
              <Link
                to={`/app/w/${workspaceId}/chat/${c.id}`}
                className="flex min-w-0 flex-1 items-center gap-3 px-1 py-1"
              >
                <span
                  className={cn(
                    "flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br text-sm font-bold text-white",
                    BUBBLE_COLORS[i % BUBBLE_COLORS.length],
                  )}
                >
                  {c.title.charAt(0).toUpperCase()}
                </span>
                <span className="min-w-0">
                  <span className="block truncate font-semibold text-ink-900">{c.title}</span>
                  <span className="text-[11px] text-ink-400">Tap to keep talking</span>
                </span>
              </Link>
              <button
                type="button"
                className="rounded-xl p-2 text-ink-400"
                onClick={() => deleteConversation.mutate(c.id)}
                title="Delete chat"
              >
                <Trash2 size={16} />
              </button>
            </div>
          ))}
          {conversations.length === 0 && (
            <div className="rounded-[1.6rem] bg-white/80 px-5 py-8 text-center text-sm text-ink-500">
              No chats yet. Tap the plus — say hi.
            </div>
          )}
        </div>
        <button
          type="button"
          className="absolute bottom-6 right-5 flex h-14 w-14 items-center justify-center rounded-full bg-[var(--primary)] text-white shadow-glow"
          onClick={() => createConversation.mutate()}
          title="New chat"
        >
          <Plus size={24} />
        </button>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col bg-white/70">
      <div className="flex items-center gap-2 border-b border-violet-100 bg-white/90 px-3 py-2.5">
        <button
          type="button"
          className="rounded-xl p-2 text-ink-600"
          onClick={() => navigate(`/app/w/${workspaceId}/chat`)}
          title="All chats"
        >
          <ArrowLeft size={20} />
        </button>
        {editingId === activeConversation?.id ? (
          <div className="flex min-w-0 flex-1 items-center gap-1">
            <input
              className="input py-1.5 text-sm"
              value={editingTitle}
              onChange={(e) => setEditingTitle(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleSaveRename(activeConversation.id);
                if (e.key === "Escape") setEditingId(null);
              }}
              autoFocus
            />
            <button type="button" className="p-1 text-emerald-600" onClick={() => handleSaveRename(activeConversation.id)}>
              <Check size={16} />
            </button>
            <button type="button" className="p-1 text-ink-400" onClick={() => setEditingId(null)}>
              <X size={16} />
            </button>
          </div>
        ) : (
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-1">
              <h2 className="truncate font-display text-base font-bold">{activeConversation?.title || "Chat"}</h2>
              {activeConversation && (
                <button
                  type="button"
                  className="p-1 text-ink-400"
                  onClick={() => startRename(activeConversation.id, activeConversation.title)}
                >
                  <Edit2 size={13} />
                </button>
              )}
            </div>
            <p className="text-[11px] text-ink-400">
              {mode === "web" ? "Web search on" : mode === "rag" ? "Your docs on" : "Auto mode"}
            </p>
          </div>
        )}
        <button
          type="button"
          className="rounded-xl p-2 text-ink-600"
          onClick={() => setShowTune((v) => !v)}
          title="Tune chat"
        >
          <SlidersHorizontal size={18} />
        </button>
      </div>

      {showTune && (
        <div className="grid grid-cols-3 gap-2 border-b border-violet-100 bg-violet-50/80 px-3 py-2">
          <select
            className="input py-1.5 text-xs"
            value={provider}
            onChange={(e) => {
              const nextProvider = e.target.value;
              setProvider(nextProvider);
              const first = models.find((m) => (nextProvider ? m.provider === nextProvider : true));
              setModel(nextProvider && first ? first.model_id : "");
            }}
          >
            <option value="">Auto</option>
            {providers.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
          <select
            className="input py-1.5 text-xs"
            value={model}
            onChange={(e) => {
              const selModel = e.target.value;
              setModel(selModel);
              if (selModel && !provider) {
                const found = models.find((m) => m.model_id === selModel);
                if (found) setProvider(found.provider);
              }
            }}
          >
            <option value="">Model</option>
            {providerModels.map((m) => (
              <option key={`${m.provider}-${m.model_id}`} value={m.model_id}>
                {m.display_name}
              </option>
            ))}
          </select>
          <select
            className="input py-1.5 text-xs"
            value={mode}
            onChange={(e) => setMode(e.target.value as "auto" | "chat" | "rag" | "web")}
          >
            <option value="auto">Auto</option>
            <option value="chat">Chat</option>
            <option value="rag">RAG</option>
            <option value="web">Web</option>
          </select>
        </div>
      )}

      <div className="flex-1 space-y-3 overflow-y-auto px-3 py-4">
        {messagesLoading && <p className="text-center text-sm text-ink-500">Loading…</p>}
        {!messagesLoading && visibleMessages.length === 0 && (
          <div className="flex flex-col items-center px-6 py-10 text-center">
            <MessageCircleHeart className="mb-3 text-[var(--primary)]" size={36} />
            <p className="font-display text-lg font-bold text-ink-900">What’s on your mind?</p>
            <p className="mt-1 text-sm text-ink-500">Docs, the web, or just a thought. Type below.</p>
          </div>
        )}
        {visibleMessages.map((m) => (
          <div
            key={m.id}
            className={cn(
              "max-w-[88%] rounded-[1.35rem] px-3.5 py-2.5 text-sm leading-relaxed",
              m.role === "user"
                ? "ml-auto rounded-br-md bg-[var(--primary)] text-white"
                : "rounded-bl-md bg-white text-ink-900 shadow-sm ring-1 ring-violet-100",
            )}
          >
            {m.role === "assistant" ? (
              (() => {
                const { body, provenance } = splitProvenance(m.content);
                return (
                  <MessageContent content={provenance ? `${body}\n\n${provenance}` : body} />
                );
              })()
            ) : (
              m.content
            )}
          </div>
        ))}
        {(sendMessage.isPending || isSending) && (
          <StatusBubble
            active
            steps={
              mode === "web"
                ? ["Searching the web…", "Reading sources…", "Writing an answer…"]
                : mode === "rag"
                  ? ["Searching your documents…", "Writing an answer…"]
                  : ["Thinking…", "Writing an answer…"]
            }
          />
        )}
        <div ref={bottomRef} />
      </div>

      <form onSubmit={onSubmit} className="border-t border-violet-100 bg-white px-3 py-2.5">
        {error && (
          <div className="mb-2 rounded-xl bg-red-50 px-3 py-2 text-xs text-red-700">{error}</div>
        )}
        <div className="flex items-end gap-2">
          <textarea
            className="input min-h-[46px] max-h-32 resize-none py-2.5"
            placeholder="Ask Suvyon…"
            rows={1}
            value={content}
            onChange={(e) => setContent(e.target.value)}
            onKeyDown={sendOnEnter}
          />
          <button
            className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-[var(--primary)] text-white shadow-glow disabled:opacity-50"
            type="submit"
            disabled={
              sendMessage.isPending ||
              createConversation.isPending ||
              isSending ||
              !content.trim()
            }
          >
            <Send size={18} />
          </button>
        </div>
      </form>
    </div>
  );
}
