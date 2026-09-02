import { useEffect, useState } from "react";
import { Mail, Save, Send, ShieldCheck, X } from "lucide-react";
import type { PendingEmailDraft } from "@/types/api";

type Props = {
  draft: PendingEmailDraft;
  sending?: boolean;
  error?: string;
  onSend: (draft: PendingEmailDraft) => void;
  onSaveDraft: (draft: PendingEmailDraft) => void;
  onReject: () => void;
};

export function EmailApprovalDialog({
  draft,
  sending = false,
  error = "",
  onSend,
  onSaveDraft,
  onReject,
}: Props) {
  const [value, setValue] = useState(draft);

  useEffect(() => setValue(draft), [draft]);

  const valid = Boolean(value.to.trim() && value.subject.trim() && value.body.trim());

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center bg-ink-950/65 p-0 backdrop-blur-sm sm:items-center sm:p-5"
      role="dialog"
      aria-modal="true"
      aria-labelledby="email-approval-title"
    >
      <div className="max-h-[94vh] w-full max-w-2xl overflow-y-auto rounded-t-[2rem] border border-white/70 bg-white shadow-2xl sm:rounded-[2rem]">
        <header className="sticky top-0 z-10 flex items-start justify-between border-b border-ink-100 bg-white/95 px-5 py-4 backdrop-blur sm:px-6">
          <div className="flex gap-3">
            <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-accent/10 text-accent">
              <Mail size={20} />
            </span>
            <div>
              <h2 id="email-approval-title" className="font-display text-xl font-bold text-ink-950">
                Review email before sending
              </h2>
              <p className="mt-1 text-sm text-ink-500">
                Nothing is sent until you press <strong>Approve & send</strong>.
              </p>
            </div>
          </div>
          <button type="button" className="btn-quiet h-9 w-9 p-0" onClick={onReject} aria-label="Close">
            <X size={18} />
          </button>
        </header>

        <div className="space-y-4 px-5 py-5 sm:px-6">
          <div className="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
            <div className="flex items-center gap-2 font-semibold">
              <ShieldCheck size={17} /> Explicit approval required
            </div>
            <p className="mt-1 text-emerald-800">Edit any field below. The AI cannot approve this action for you.</p>
          </div>
          <div>
            <label className="label" htmlFor="approval-to">Recipient</label>
            <input
              id="approval-to"
              className="input"
              type="email"
              value={value.to}
              onChange={(e) => setValue({ ...value, to: e.target.value })}
            />
          </div>
          <div>
            <label className="label" htmlFor="approval-subject">Subject</label>
            <input
              id="approval-subject"
              className="input"
              maxLength={255}
              value={value.subject}
              onChange={(e) => setValue({ ...value, subject: e.target.value })}
            />
          </div>
          <div>
            <label className="label" htmlFor="approval-body">Message</label>
            <textarea
              id="approval-body"
              className="input min-h-52 resize-y leading-relaxed"
              value={value.body}
              onChange={(e) => setValue({ ...value, body: e.target.value })}
            />
          </div>
          <div>
            <label className="label" htmlFor="approval-regards">Regards / signature</label>
            <textarea
              id="approval-regards"
              className="input min-h-20 resize-y"
              placeholder={"Regards,\nYour name"}
              value={value.regards}
              onChange={(e) => setValue({ ...value, regards: e.target.value })}
            />
          </div>
          {error && <div className="rounded-2xl bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}
        </div>

        <footer className="sticky bottom-0 flex flex-col-reverse gap-2 border-t border-ink-100 bg-white/95 px-5 py-4 backdrop-blur sm:flex-row sm:justify-between sm:px-6">
          <button type="button" className="btn-quiet" disabled={sending} onClick={onReject}>
            <X size={16} /> Reject
          </button>
          <div className="flex flex-col gap-2 sm:flex-row">
            <button type="button" className="btn-outline" disabled={!valid || sending} onClick={() => onSaveDraft(value)}>
              <Save size={16} /> Keep as draft
            </button>
            <button type="button" className="btn-primary" disabled={!valid || sending} onClick={() => onSend(value)}>
              {sending ? <Mail className="animate-pulse" size={16} /> : <Send size={16} />}
              {sending ? "Sending..." : "Approve & send"}
            </button>
          </div>
        </footer>
      </div>
    </div>
  );
}
