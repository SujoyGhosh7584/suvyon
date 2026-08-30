import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Archive, Plus, Star } from "lucide-react";
import { MobileMascot } from "@/components/MobileMascot";
import { useAuth } from "@/context/AuthContext";
import { useWorkspace } from "@/context/WorkspaceContext";
import { getErrorMessage } from "@/lib/api";
import { workspacesApi } from "@/lib/services";

function greeting() {
  const hour = new Date().getHours();
  if (hour < 12) return "Good morning";
  if (hour < 18) return "Good afternoon";
  return "Good evening";
}

export function MobileWorkspacesPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user, logout } = useAuth();
  const { setWorkspaceId } = useWorkspace();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState("");
  const [showCreate, setShowCreate] = useState(false);

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

  const active = workspaces.filter((w) => !w.is_archived);
  const archived = workspaces.filter((w) => w.is_archived);
  const firstName = (user?.full_name || "there").split(" ")[0];

  return (
    <div className="min-h-[100dvh] bg-mesh px-5 pb-10 pt-[max(1rem,env(safe-area-inset-top))] text-white">
      <div className="mb-2 flex items-center justify-between">
        <span className="brand-mark flex h-10 w-10 items-center justify-center rounded-2xl font-display text-lg font-extrabold">
          S
        </span>
        <button
          type="button"
          className="text-sm text-ink-300"
          onClick={async () => {
            await logout();
            navigate("/login");
          }}
        >
          Sign out
        </button>
      </div>
      <MobileMascot className="mt-4" />
      <p className="mt-3 text-center text-xs font-semibold uppercase tracking-[0.2em] text-indigo-200">
        {greeting()}
      </p>
      <h1 className="mt-2 text-center font-display text-3xl font-extrabold">
        Hey {firstName}
      </h1>
      <p className="mt-2 text-center text-sm text-ink-300">Pick a little world to play in.</p>

      <button
        type="button"
        className="btn-primary mt-6 w-full py-3"
        onClick={() => setShowCreate((v) => !v)}
      >
        <Plus size={16} />
        New workspace
      </button>

      {showCreate && (
        <form
          className="mt-4 space-y-3 rounded-[1.6rem] bg-white p-4 text-ink-950"
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
          {error && <p className="text-sm text-red-600">{error}</p>}
          <button className="btn-primary w-full" disabled={createMutation.isPending}>
            Create
          </button>
        </form>
      )}

      <div className="mt-6 space-y-3">
        {isLoading && <p className="text-center text-sm text-ink-400">Loading…</p>}
        {active.map((ws) => (
          <button
            key={ws.id}
            type="button"
            className="flex w-full items-start justify-between gap-3 rounded-[1.5rem] bg-white p-4 text-left text-ink-950 shadow-panel"
            onClick={() => {
              setWorkspaceId(ws.id);
              navigate(`/app/w/${ws.id}/overview`);
            }}
          >
            <span>
              <span className="block text-lg font-semibold">{ws.name}</span>
              <span className="mt-1 block text-sm text-ink-500">
                {ws.description || "Tap to open"}
              </span>
            </span>
            {ws.is_favourite && <Star size={16} className="text-amber-500" fill="currentColor" />}
          </button>
        ))}
      </div>

      {archived.length > 0 && (
        <div className="mt-8">
          <div className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-ink-400">
            <Archive size={14} />
            Archived
          </div>
          {archived.map((ws) => (
            <div key={ws.id} className="mb-2 rounded-2xl bg-white/10 px-4 py-3 text-sm opacity-70">
              {ws.name}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
