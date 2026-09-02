import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Archive, ArrowUpRight, Plus, Sparkles, Star, Trash2 } from "lucide-react";
import { AIBackdrop, BrandOrb } from "@/components/AIBackdrop";
import { useAuth } from "@/context/AuthContext";
import { useWorkspace } from "@/context/WorkspaceContext";
import { getErrorMessage } from "@/lib/api";
import { workspacesApi } from "@/lib/services";

export function WorkspacesPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const { workspaceId: currentWorkspaceId, setWorkspaceId } = useWorkspace();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState("");

  const { data: workspaces = [], isLoading } = useQuery({
    queryKey: ["workspaces", user?.id],
    queryFn: workspacesApi.list,
    enabled: !!user,
  });

  const createMutation = useMutation({
    mutationFn: () => workspacesApi.create({ name, description: description || undefined }),
    onSuccess: (ws) => {
      queryClient.invalidateQueries({ queryKey: ["workspaces", user?.id] });
      setWorkspaceId(ws.id);
      navigate(`/app/w/${ws.id}/overview`);
    },
    onError: (err) => setError(getErrorMessage(err)),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => workspacesApi.remove(id),
    onSuccess: (_, id) => {
      queryClient.setQueryData(
        ["workspaces", user?.id],
        workspaces.filter((workspace) => workspace.id !== id),
      );
      queryClient.invalidateQueries({ queryKey: ["workspaces", user?.id] });
      if (currentWorkspaceId === id) setWorkspaceId(null);
    },
    onError: (err) => setError(getErrorMessage(err)),
  });

  function requestDelete(id: string, workspaceName: string) {
    if (!window.confirm(`Delete workspace “${workspaceName}” and all of its chats, agents, and documents? This cannot be undone.`)) return;
    setError("");
    deleteMutation.mutate(id);
  }

  const active = workspaces.filter((w) => !w.is_archived);
  const archived = workspaces.filter((w) => w.is_archived);

  return (
    <div className="relative min-h-screen overflow-hidden bg-mesh px-6 py-10 text-white">
      <AIBackdrop />
      <div className="page-enter relative mx-auto max-w-5xl">
        <div className="mb-8 flex items-start justify-between gap-6">
          <div>
          <div className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-[.2em] text-accent-soft"><Sparkles size={13} /> Command center</div>
          <div className="font-display text-4xl font-extrabold md:text-5xl">Your workspaces</div>
          <p className="mt-2 text-ink-300">
            Pick a space for chat, agents, and knowledge — each with its own files and history.
          </p>
          </div>
          <BrandOrb />
        </div>

        <div className="glass-dark mb-8 rounded-[1.75rem] p-6 text-white">
          <div className="mb-4 flex items-center gap-2 font-semibold">
            <Plus size={18} />
            Create workspace
          </div>
          <form
            className="grid gap-3 md:grid-cols-[1fr_1.2fr_auto]"
            onSubmit={(e) => {
              e.preventDefault();
              setError("");
              createMutation.mutate();
            }}
          >
            <input
              className="input"
              placeholder="Name"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
            <input
              className="input"
              placeholder="Description (optional)"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
            <button className="btn-primary" disabled={createMutation.isPending}>
              Create
            </button>
          </form>
          {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
        </div>

        {isLoading ? (
          <div className="panel p-6 text-sm text-ink-500">Loading workspaces…</div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            {active.map((ws) => (
              <div
                key={ws.id}
                className="group relative overflow-hidden rounded-[1.6rem] border border-white/70 bg-white/[.82] text-ink-950 shadow-panel backdrop-blur-xl transition-all duration-300 hover:-translate-y-1 hover:shadow-glow"
              >
                <button type="button" className="w-full p-6 pr-14 text-left" onClick={() => { setWorkspaceId(ws.id); navigate(`/app/w/${ws.id}/overview`); }}>
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="text-lg font-semibold">{ws.name}</div>
                    <p className="mt-1 line-clamp-2 text-sm text-ink-500">
                      {ws.description || "No description"}
                    </p>
                  </div>
                  {ws.is_favourite && <Star size={16} className="text-amber-500" fill="currentColor" />}
                  {!ws.is_favourite && <ArrowUpRight size={17} className="text-ink-300 transition group-hover:-translate-y-0.5 group-hover:translate-x-0.5 group-hover:text-accent" />}
                </div>
                </button>
                <button type="button" className="absolute bottom-4 right-4 rounded-xl p-2 text-slate-400 transition hover:bg-red-50 hover:text-red-600" onClick={() => requestDelete(ws.id, ws.name)} disabled={deleteMutation.isPending} title={`Delete ${ws.name}`}><Trash2 size={16} /></button>
              </div>
            ))}
          </div>
        )}

        {archived.length > 0 && (
          <div className="mt-10">
            <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-ink-300">
              <Archive size={16} />
              Archived
            </div>
            <div className="grid gap-3 md:grid-cols-2">
              {archived.map((ws) => (
                <div key={ws.id} className="panel flex items-center justify-between gap-3 p-4 opacity-70">
                  <div className="font-medium">{ws.name}</div>
                  <button type="button" className="rounded-xl p-2 text-slate-400 hover:bg-red-50 hover:text-red-600" onClick={() => requestDelete(ws.id, ws.name)} title={`Delete ${ws.name}`}><Trash2 size={15} /></button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
