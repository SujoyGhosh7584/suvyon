import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Archive, Plus, Star } from "lucide-react";
import { useWorkspace } from "@/context/WorkspaceContext";
import { getErrorMessage } from "@/lib/api";
import { workspacesApi } from "@/lib/services";

export function WorkspacesPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { setWorkspaceId } = useWorkspace();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState("");

  const { data: workspaces = [], isLoading } = useQuery({
    queryKey: ["workspaces"],
    queryFn: workspacesApi.list,
  });

  const createMutation = useMutation({
    mutationFn: () => workspacesApi.create({ name, description: description || undefined }),
    onSuccess: (ws) => {
      queryClient.invalidateQueries({ queryKey: ["workspaces"] });
      setWorkspaceId(ws.id);
      navigate(`/app/w/${ws.id}/overview`);
    },
    onError: (err) => setError(getErrorMessage(err)),
  });

  const active = workspaces.filter((w) => !w.is_archived);
  const archived = workspaces.filter((w) => w.is_archived);

  return (
    <div className="min-h-screen bg-mesh px-6 py-10 text-white">
      <div className="mx-auto max-w-5xl">
        <div className="mb-8">
          <div className="font-display text-4xl font-extrabold">Your workspaces</div>
          <p className="mt-2 text-ink-300">
            Pick a space for chat, agents, and knowledge — each with its own files and history.
          </p>
        </div>

        <div className="mb-8 rounded-[1.75rem] bg-white p-6 text-ink-950 shadow-panel">
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
              <button
                key={ws.id}
                type="button"
                className="rounded-[1.6rem] bg-white p-6 text-left text-ink-950 shadow-panel transition hover:-translate-y-1 hover:shadow-glow"
                onClick={() => {
                  setWorkspaceId(ws.id);
                  navigate(`/app/w/${ws.id}/overview`);
                }}
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="text-lg font-semibold">{ws.name}</div>
                    <p className="mt-1 line-clamp-2 text-sm text-ink-500">
                      {ws.description || "No description"}
                    </p>
                  </div>
                  {ws.is_favourite && <Star size={16} className="text-amber-500" fill="currentColor" />}
                </div>
              </button>
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
                <div key={ws.id} className="panel p-4 opacity-70">
                  <div className="font-medium">{ws.name}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
