import { FormEvent, useMemo, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CheckCircle2, FileText, FileUp, Plus, Search, Trash2, UploadCloud } from "lucide-react";
import { getErrorMessage } from "@/lib/api";
import { documentsApi, knowledgeApi } from "@/lib/services";
import { formatBytes } from "@/lib/utils";

export function KnowledgePage() {
  const { workspaceId = "" } = useParams();
  const queryClient = useQueryClient();

  const [kbName, setKbName] = useState("");
  const [kbDescription, setKbDescription] = useState("");
  const [selectedKb, setSelectedKb] = useState("");
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [dragging, setDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const { data: knowledgeBases = [], isLoading: kbLoading } = useQuery({
    queryKey: ["knowledge-bases", workspaceId],
    queryFn: () => knowledgeApi.list(workspaceId),
  });
  const { data: documents = [], isLoading: docsLoading } = useQuery({
    queryKey: ["documents", workspaceId],
    queryFn: () => documentsApi.list(workspaceId),
  });
  const filteredDocuments = useMemo(
    () => documents.filter((document) => document.name.toLowerCase().includes(search.toLowerCase())),
    [documents, search],
  );
  const readyDocuments = documents.filter((document) => document.status === "ready").length;

  const createKb = useMutation({
    mutationFn: () =>
      knowledgeApi.create(workspaceId, {
        name: kbName,
        description: kbDescription || undefined,
      }),
    onSuccess: (kb) => {
      queryClient.invalidateQueries({ queryKey: ["knowledge-bases", workspaceId] });
      setKbName("");
      setKbDescription("");
      setSelectedKb(kb.id);
    },
    onError: (err) => setError(getErrorMessage(err)),
  });

  const deleteKb = useMutation({
    mutationFn: (id: string) => knowledgeApi.remove(workspaceId, id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["knowledge-bases", workspaceId] });
    },
  });

  const uploadDoc = useMutation({
    mutationFn: (file: File) => {
      if (!selectedKb) throw new Error("Select a knowledge base first.");
      return documentsApi.upload(workspaceId, selectedKb, file);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents", workspaceId] });
    },
    onError: (err) => setError(getErrorMessage(err)),
  });

  const deleteDoc = useMutation({
    mutationFn: (id: string) => documentsApi.remove(workspaceId, id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents", workspaceId] });
    },
  });

  function onCreateKb(e: FormEvent) {
    e.preventDefault();
    setError("");
    createKb.mutate();
  }

  function chooseFile(file?: File) {
    if (!file) return;
    setError("");
    uploadDoc.mutate(file);
  }

  return (
    <div className="page-enter space-y-6 text-slate-950">
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div><p className="text-[10px] font-bold uppercase tracking-[.2em] text-indigo-600">Ground your AI</p><h2 className="mt-1 font-display text-3xl font-bold tracking-tight">Trusted knowledge, organized.</h2><p className="mt-2 max-w-2xl text-sm text-slate-600">Create focused collections and make project documents available directly inside Chat.</p></div>
        <div className="flex gap-2 text-xs font-semibold"><span className="rounded-full border border-slate-200 bg-white px-3 py-1.5 text-slate-700">{knowledgeBases.length} collections</span><span className="rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-emerald-800">{readyDocuments}/{documents.length} ready</span></div>
      </div>

      {error && (
        <div className="rounded-xl bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>
      )}

      <div className="grid gap-5 xl:grid-cols-[.75fr_1.25fr]">
        <div className="rounded-[24px] border border-slate-200 bg-white p-5 shadow-sm">
          <div className="mb-4 flex items-center gap-2 font-semibold text-slate-950">
            <Plus size={16} />
            New knowledge base
          </div>
          <form className="space-y-3" onSubmit={onCreateKb}>
            <input
              className="input"
              placeholder="Name"
              required
              value={kbName}
              onChange={(e) => setKbName(e.target.value)}
            />
            <input
              className="input"
              placeholder="Description (optional)"
              value={kbDescription}
              onChange={(e) => setKbDescription(e.target.value)}
            />
            <button className="btn-primary" disabled={createKb.isPending}>
              Create
            </button>
          </form>

          <div className="mt-6 space-y-2">
            {kbLoading && <p className="text-sm text-ink-500">Loading…</p>}
            {knowledgeBases.map((kb) => (
              <div
                key={kb.id}
                className="flex items-center justify-between rounded-xl border border-ink-100 px-3 py-2"
              >
                <button
                  type="button"
                  className="text-left"
                  onClick={() => setSelectedKb(kb.id)}
                >
                  <div className="font-medium text-ink-950">{kb.name}</div>
                  <div className="text-xs text-ink-400">
                    {kb.embedding_model}
                    {selectedKb === kb.id ? " · selected for upload" : ""}
                  </div>
                </button>
                <button
                  type="button"
                  className="btn-quiet px-2 py-2"
                  onClick={() => {
                    if (window.confirm(`Delete ${kb.name} and its stored knowledge?`)) deleteKb.mutate(kb.id);
                  }}
                  aria-label={`Delete ${kb.name}`}
                >
                  <Trash2 size={14} />
                </button>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-[24px] border border-slate-200 bg-white p-5 shadow-sm">
          <div className="mb-4 flex items-center gap-2 font-semibold text-slate-950">
            <FileUp size={16} />
            Upload document
          </div>
          <select
            className="input mb-3"
            value={selectedKb}
            onChange={(e) => setSelectedKb(e.target.value)}
          >
            <option value="">Select knowledge base</option>
            {knowledgeBases.map((kb) => (
              <option key={kb.id} value={kb.id}>
                {kb.name}
              </option>
            ))}
          </select>
          <input
            ref={fileInputRef}
            type="file"
            className="sr-only"
            accept=".pdf,.docx,.txt,.md,.csv,application/pdf,text/plain,text/markdown,text/csv"
            onChange={(e) => {
              chooseFile(e.target.files?.[0]);
              e.target.value = "";
            }}
          />
          <button
            type="button"
            className={`flex w-full flex-col items-center justify-center rounded-[1.75rem] border-2 border-dashed px-5 py-8 text-center transition ${dragging ? "border-accent bg-accent/10" : "border-amber-200 bg-amber-50/50 hover:border-amber-400"}`}
            onClick={() => fileInputRef.current?.click()}
            onDragOver={(event) => { event.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onDrop={(event) => {
              event.preventDefault();
              setDragging(false);
              chooseFile(event.dataTransfer.files?.[0]);
            }}
            disabled={!selectedKb || uploadDoc.isPending}
          >
            <UploadCloud className="text-amber-700" size={28} />
            <span className="mt-3 font-semibold text-ink-900">Drop a document here or browse</span>
            <span className="mt-1 text-xs text-ink-500">PDF, DOCX, TXT, Markdown, or CSV · up to 25 MB</span>
            {!selectedKb && <span className="mt-2 text-xs font-medium text-amber-700">Select a knowledge base first</span>}
          </button>
          {uploadDoc.isPending && (
            <p className="mt-2 text-sm text-ink-500">Uploading & processing…</p>
          )}

          <div className="mt-6 space-y-2">
            <div className="flex items-center justify-between gap-3">
              <div className="text-sm font-semibold text-ink-950">Documents</div>
              <label className="relative max-w-56">
                <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-ink-400" size={14} />
                <input className="input py-1.5 pl-8 text-xs" placeholder="Search files" value={search} onChange={(event) => setSearch(event.target.value)} />
              </label>
            </div>
            {docsLoading && <p className="text-sm text-ink-500">Loading…</p>}
            {filteredDocuments.map((doc) => (
              <div
                key={doc.id}
                className="flex items-center justify-between rounded-xl border border-ink-100 px-3 py-2"
              >
                <div className="flex min-w-0 items-start gap-3">
                  <span className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-amber-100 text-amber-800"><FileText size={17} /></span>
                  <div className="min-w-0">
                  <div className="truncate font-medium text-ink-950">{doc.name}</div>
                  <div className="text-xs text-ink-400">
                    {doc.status} · {formatBytes(doc.size_bytes)}
                    {doc.chunk_count != null ? ` · ${doc.chunk_count} chunks` : ""}
                  </div>
                  {doc.error_message && (
                    <div className="text-xs text-red-600">{doc.error_message}</div>
                  )}
                  </div>
                </div>
                <button
                  type="button"
                  className="btn-quiet px-2 py-2"
                  onClick={() => {
                    if (window.confirm(`Delete ${doc.name}?`)) deleteDoc.mutate(doc.id);
                  }}
                  aria-label={`Delete ${doc.name}`}
                >
                  <Trash2 size={14} />
                </button>
              </div>
            ))}
            {filteredDocuments.length === 0 && !docsLoading && (
              <div className="rounded-2xl border border-dashed border-ink-200 px-4 py-8 text-center">
                <CheckCircle2 className="mx-auto text-ink-300" size={24} />
                <p className="mt-2 text-sm text-ink-500">{search ? "No documents match your search." : "No documents uploaded yet."}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
