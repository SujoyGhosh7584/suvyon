import { useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { FileText, LoaderCircle, Paperclip, X } from "lucide-react";
import { getErrorMessage } from "@/lib/api";
import { conversationsApi, documentsApi } from "@/lib/services";

type Props = { workspaceId: string; conversationId: string };

export function ChatAttachments({ workspaceId, conversationId }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [open, setOpen] = useState(false);
  const queryClient = useQueryClient();
  const queryKey = ["chat-documents", workspaceId, conversationId];
  const { data: documents = [] } = useQuery({ queryKey, queryFn: () => conversationsApi.documents(workspaceId, conversationId) });
  const upload = useMutation({
    mutationFn: (file: File) => conversationsApi.uploadDocument(workspaceId, conversationId, file),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey }); setOpen(true); },
    onSettled: () => queryClient.invalidateQueries({ queryKey }),
  });
  const remove = useMutation({
    mutationFn: (documentId: string) => documentsApi.remove(workspaceId, documentId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey }),
  });

  return (
    <div className="relative shrink-0">
      <input ref={inputRef} type="file" className="hidden" accept=".pdf,.docx,.txt,.md,.csv,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain,text/markdown,text/csv" onChange={(event) => { const file = event.target.files?.[0]; if (file) upload.mutate(file); event.target.value = ""; }} />
      <button type="button" className="relative flex h-11 w-11 items-center justify-center rounded-2xl border border-slate-200 bg-white text-slate-600 transition hover:border-indigo-300 hover:text-indigo-700 disabled:opacity-50" onClick={() => inputRef.current?.click()} disabled={upload.isPending} title="Attach a file only to this chat">
        {upload.isPending ? <LoaderCircle className="animate-spin" size={18} /> : <Paperclip size={18} />}
      </button>
      {documents.length > 0 && <button type="button" className="absolute -right-1.5 -top-1.5 flex h-5 min-w-5 items-center justify-center rounded-full bg-indigo-600 px-1 text-[9px] font-bold text-white ring-2 ring-white" onClick={() => setOpen((current) => !current)} title="Manage chat attachments">{documents.length}</button>}
      {open && documents.length > 0 && (
        <div className="absolute bottom-full left-0 z-40 mb-2 w-72 rounded-2xl border border-slate-200 bg-white p-3 text-slate-900 shadow-2xl">
          <div className="mb-2 flex items-center justify-between"><p className="text-xs font-bold">Files in this chat</p><button type="button" className="rounded-lg p-1 text-slate-400 hover:bg-slate-100" onClick={() => setOpen(false)} aria-label="Close attachments"><X size={14} /></button></div>
          <div className="max-h-48 space-y-1 overflow-y-auto">
            {documents.map((document) => (
              <div key={document.id} className="flex items-center gap-2 rounded-xl bg-slate-50 px-2.5 py-2 text-xs">
                <FileText className={document.status === "ready" ? "text-emerald-600" : document.status === "failed" ? "text-red-600" : "text-amber-600"} size={14} />
                <span className="min-w-0 flex-1 truncate" title={document.error_message || document.name}>{document.name}</span>
                <button type="button" className="rounded-lg p-1 text-slate-400 hover:bg-red-50 hover:text-red-600" onClick={() => remove.mutate(document.id)} aria-label={`Remove ${document.name} from this chat`}><X size={13} /></button>
              </div>
            ))}
          </div>
        </div>
      )}
      {upload.error && <span className="absolute bottom-full left-0 z-40 mb-2 w-64 rounded-xl bg-red-50 p-2 text-[11px] font-medium text-red-600 shadow-lg">{getErrorMessage(upload.error)}</span>}
    </div>
  );
}
