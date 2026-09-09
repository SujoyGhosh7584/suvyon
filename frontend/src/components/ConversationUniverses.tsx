import { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useQueries, useQueryClient } from "@tanstack/react-query";
import { ArrowUpRight, GitBranch, GitMerge, LoaderCircle, X } from "lucide-react";
import { conversationsApi } from "@/lib/services";
import { getErrorMessage } from "@/lib/api";
import { MessageContent } from "@/components/MessageContent";
import type { Conversation, Message } from "@/types/api";

type Props = {
  workspaceId: string;
  conversation: Conversation;
  conversations: Conversation[];
  messages: Message[];
  provider: string;
  model: string;
  disabled: boolean;
};

export function ConversationUniverses({ workspaceId, conversation, conversations, messages, provider, model, disabled }: Props) {
  const dialog = useRef<HTMLDialogElement>(null);
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(false);
  const [tab, setTab] = useState<"branch" | "merge">("branch");
  const [title, setTitle] = useState(`${conversation.title.slice(0, 235)} · Alternative`);
  const [point, setPoint] = useState("");
  const [selected, setSelected] = useState<string[]>([conversation.id]);
  const [focus, setFocus] = useState("Find the strongest approach and a concrete next step.");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const parent = conversations.find((c) => c.id === conversation.parent_conversation_id);
  const children = conversations.filter((c) => c.parent_conversation_id === conversation.id);
  const previews = useQueries({ queries: selected.map((id) => ({
    queryKey: ["messages", workspaceId, id],
    queryFn: () => conversationsApi.messages(workspaceId, id),
    enabled: open && tab === "merge",
  })) });

  useEffect(() => {
    if (open) dialog.current?.showModal();
    else dialog.current?.close();
  }, [open]);

  async function submit() {
    if (busy) return;
    setBusy(true);
    setError("");
    try {
      const result = tab === "branch"
        ? await conversationsApi.branch(workspaceId, conversation.id, { title: title.trim(), through_message_id: point || null })
        : await conversationsApi.merge(workspaceId, {
          conversation_ids: selected, title: "Merged perspectives", focus: focus.trim(),
          provider: provider || null, model: model || null,
        });
      await queryClient.invalidateQueries({ queryKey: ["conversations", workspaceId] });
      setOpen(false);
      navigate(`/app/w/${workspaceId}/chat/${result.id}`);
    } catch (err) {
      setError(getErrorMessage(err, "Could not create this universe. Please try again."));
    } finally {
      setBusy(false);
    }
  }

  return <div className="flex flex-wrap items-center gap-3 border-b border-violet-100 bg-violet-50/60 px-4 py-2 text-xs">
    <button type="button" disabled={disabled} onClick={() => setOpen(true)} className="flex items-center gap-2 rounded-lg px-2 py-1.5 font-semibold text-violet-700 hover:bg-violet-100 disabled:opacity-40">
      <GitBranch size={16} /> Parallel universes
    </button>
    {parent && <Link className="flex items-center gap-1 text-slate-600 hover:text-violet-700" to={`/app/w/${workspaceId}/chat/${parent.id}`}><ArrowUpRight size={13} /> Source: {parent.title.slice(0, 35)}</Link>}
    {children.length > 0 && <span className="text-slate-500">{children.length} {children.length === 1 ? "branch" : "branches"}</span>}
    <dialog ref={dialog} onCancel={(e) => { if (busy) e.preventDefault(); }} onClose={() => setOpen(false)} aria-labelledby="universes-title"
      className="m-auto max-h-[85dvh] w-[calc(100%_-_24px)] max-w-[900px] overflow-y-auto rounded-3xl border border-violet-200 bg-white p-0 text-slate-900 shadow-2xl backdrop:bg-slate-950/60">
      <div className="bg-gradient-to-br from-violet-950 via-indigo-950 to-slate-900 p-6 text-white">
        <div className="flex items-start justify-between gap-4">
          <div><p className="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-violet-300">One conversation. More possibilities.</p>
            <h2 id="universes-title" className="text-2xl font-bold">Parallel universes</h2>
            <p className="mt-2 text-sm text-violet-200">Explore a different direction. Bring the best ideas back together.</p></div>
          <button type="button" aria-label="Close parallel universes" disabled={busy} onClick={() => setOpen(false)} className="rounded-full p-2 hover:bg-white/10 disabled:opacity-40"><X size={20} /></button>
        </div>
        <div className="mt-5 flex gap-2">
          {(["branch", "merge"] as const).map((value) => <button type="button" key={value} aria-pressed={tab === value} disabled={busy}
            onClick={() => { setTab(value); setError(""); }} className={`flex items-center gap-2 rounded-xl px-4 py-2 text-sm ${tab === value ? "bg-white text-violet-950" : "bg-white/10 text-violet-100"}`}>
            {value === "branch" ? <GitBranch size={16} /> : <GitMerge size={16} />}{value === "branch" ? "Branch & explore" : "Compare & merge"}
          </button>)}
        </div>
      </div>
      <form className="space-y-5 p-6" onSubmit={(e) => { e.preventDefault(); void submit(); }}>
        <fieldset disabled={busy} className="min-w-0 space-y-4">
          {tab === "branch" ? <>
            <label className="block text-sm font-medium">Name this direction
              <input className="input mt-2" maxLength={255} required value={title} onChange={(e) => setTitle(e.target.value)} />
            </label>
            <div className="flex flex-wrap gap-2">{["Bold approach", "Devil's advocate", "Simplest solution"].map((name) => <button type="button" key={name} className="rounded-full border border-violet-200 px-3 py-1.5 text-xs text-violet-700 hover:bg-violet-50" onClick={() => setTitle(`${conversation.title.slice(0, 225)} · ${name}`)}>{name}</button>)}</div>
            <label className="block text-sm font-medium">Branch point
              <select className="input mt-2" value={point} onChange={(e) => setPoint(e.target.value)}>
                <option value="">Latest message · keep the full conversation</option>
                {messages.map((m, i) => <option key={m.id} value={m.id}>{i + 1}. {m.role}: {m.content.slice(0, 85)}</option>)}
              </select>
            </label>
            <p className="text-sm leading-relaxed text-slate-500">Messages through this point and the saved model settings are copied into an independent chat. Continue with your own “what if” question. Attachments stay in the source chat; upload them again if needed.</p>
            {children.length > 0 && <div className="space-y-2 border-t pt-3"><p className="text-xs font-semibold uppercase text-slate-500">Existing directions</p>{children.map((child) => <Link onClick={() => setOpen(false)} key={child.id} to={`/app/w/${workspaceId}/chat/${child.id}`} className="flex items-center gap-2 text-sm text-violet-700"><GitBranch size={14} />{child.title}</Link>)}</div>}
          </> : <>
            <p className="text-sm text-slate-600">Choose 2–4 conversations. Preview their latest answers, then generate a synthesis using {model || provider || "your automatic model selection"}.</p>
            <div className="max-h-40 space-y-1 overflow-y-auto rounded-xl border p-2">
              {conversations.filter((c) => !c.is_archived || selected.includes(c.id)).map((c) => <label key={c.id} className="flex cursor-pointer items-center gap-2 rounded-lg p-2 text-sm hover:bg-violet-50">
                <input type="checkbox" checked={selected.includes(c.id)} disabled={!selected.includes(c.id) && selected.length >= 4}
                  onChange={(e) => setSelected((ids) => e.target.checked ? [...ids, c.id] : ids.filter((id) => id !== c.id))} />
                <span className="truncate">{c.title}</span>{c.parent_conversation_id && <GitBranch size={13} className="shrink-0 text-violet-500" />}
              </label>)}
            </div>
            <div className="grid gap-3 sm:grid-cols-2">{selected.map((id, index) => {
              const preview = previews[index];
              const answers = preview.data?.filter((m) => m.role === "assistant") || [];
              const answer = answers[answers.length - 1];
              return <div key={id} className="min-w-0 rounded-xl border border-violet-100 bg-violet-50/40 p-3">
                <p className="mb-2 truncate text-xs font-bold text-violet-800">{conversations.find((c) => c.id === id)?.title}</p>
                <div className="max-h-48 overflow-auto text-sm">{preview.isError ? <p role="alert">Could not load preview.</p> : preview.isLoading ? <p>Loading preview…</p> : answer ? <MessageContent content={answer.content} /> : <p className="text-slate-500">No assistant answer yet.</p>}</div>
              </div>;
            })}</div>
            <label className="block text-sm font-medium">What should the merge optimize for?
              <textarea className="input mt-2 min-h-20" maxLength={2000} required value={focus} onChange={(e) => setFocus(e.target.value)} />
            </label>
            <p className="text-xs text-slate-500">Creates a new chat with the source transcripts and synthesis. Conflicting claims are compared, not independently fact-checked.</p>
          </>}
        </fieldset>
        {error && <p role="alert" className="rounded-xl bg-red-50 p-3 text-sm text-red-700">{error}</p>}
        <button type="submit" disabled={busy || (tab === "branch" ? !messages.length || !title.trim() : selected.length < 2 || !focus.trim())} className="btn-primary w-full justify-center py-3">
          {busy ? <><LoaderCircle size={16} className="animate-spin" /><span role="status">{tab === "merge" ? "Comparing your universes…" : "Creating branch…"}</span></> : tab === "branch" ? "Create branch" : `Merge ${selected.length} universes`}
        </button>
      </form>
    </dialog>
  </div>;
}
