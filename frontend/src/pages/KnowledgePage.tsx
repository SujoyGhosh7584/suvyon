import { FormEvent, useState } from "react";
import { useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { FileUp, Plus, Trash2 } from "lucide-react";
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

  const { data: knowledgeBases = [], isLoading: kbLoading } = useQuery({
    queryKey: ["knowledge-bases", workspaceId],
    queryFn: () => knowledgeApi.list(workspaceId),
  });
  const { data: documents = [], isLoading: docsLoading } = useQuery({
    queryKey: ["documents", workspaceId],
    queryFn: () => documentsApi.list(workspaceId),
  });

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

  return (
    <div className="space-y-8">
      <div className="relative overflow-hidden rounded-[2rem] bg-amber-950 p-8 text-amber-50 shadow-panel">
        <p className="mb-2 text-xs font-semibold uppercase tracking-[0.22em] text-amber-200">
          Library
        </p>
        <h1 className="font-display text-4xl font-extrabold">Knowledge</h1>
        <p className="mt-2 max-w-2xl text-amber-100/80">
          Create knowledge bases and upload files so chat can answer from them.
        </p>
      </div>

      {error && (
        <div className="rounded-xl bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>
      )}

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="card border-amber-100 p-5">
          <div className="mb-4 flex items-center gap-2 font-semibold text-amber-950">
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
                  <div className="font-medium">{kb.name}</div>
                  <div className="text-xs text-ink-400">
                    {kb.embedding_model}
                    {selectedKb === kb.id ? " · selected for upload" : ""}
                  </div>
                </button>
                <button
                  type="button"
                  className="btn-quiet px-2 py-2"
                  onClick={() => deleteKb.mutate(kb.id)}
                >
                  <Trash2 size={14} />
                </button>
              </div>
            ))}
          </div>
        </div>

        <div className="card border-amber-100 p-5">
          <div className="mb-4 flex items-center gap-2 font-semibold text-amber-950">
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
            type="file"
            className="block w-full text-sm text-ink-600"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) {
                setError("");
                uploadDoc.mutate(file);
              }
            }}
          />
          {uploadDoc.isPending && (
            <p className="mt-2 text-sm text-ink-500">Uploading & processing…</p>
          )}

          <div className="mt-6 space-y-2">
            <div className="text-sm font-semibold">Documents</div>
            {docsLoading && <p className="text-sm text-ink-500">Loading…</p>}
            {documents.map((doc) => (
              <div
                key={doc.id}
                className="flex items-center justify-between rounded-xl border border-ink-100 px-3 py-2"
              >
                <div>
                  <div className="font-medium">{doc.name}</div>
                  <div className="text-xs text-ink-400">
                    {doc.status} · {formatBytes(doc.size_bytes)}
                    {doc.chunk_count != null ? ` · ${doc.chunk_count} chunks` : ""}
                  </div>
                  {doc.error_message && (
                    <div className="text-xs text-red-600">{doc.error_message}</div>
                  )}
                </div>
                <button
                  type="button"
                  className="btn-quiet px-2 py-2"
                  onClick={() => deleteDoc.mutate(doc.id)}
                >
                  <Trash2 size={14} />
                </button>
              </div>
            ))}
            {documents.length === 0 && !docsLoading && (
              <p className="text-sm text-ink-500">No documents uploaded yet.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
