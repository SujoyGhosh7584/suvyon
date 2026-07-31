import { Link, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Bot, FileText, MessageSquare } from "lucide-react";
import {
  agentsApi,
  conversationsApi,
  documentsApi,
  knowledgeApi,
  workspacesApi,
} from "@/lib/services";

export function OverviewPage() {
  const { workspaceId = "" } = useParams();

  const { data: workspace } = useQuery({
    queryKey: ["workspace", workspaceId],
    queryFn: () => workspacesApi.get(workspaceId),
  });
  const { data: conversations = [] } = useQuery({
    queryKey: ["conversations", workspaceId],
    queryFn: () => conversationsApi.list(workspaceId),
  });
  const { data: agents = [] } = useQuery({
    queryKey: ["agents", workspaceId],
    queryFn: () => agentsApi.list(workspaceId),
  });
  const { data: knowledgeBases = [] } = useQuery({
    queryKey: ["knowledge-bases", workspaceId],
    queryFn: () => knowledgeApi.list(workspaceId),
  });
  const { data: documents = [] } = useQuery({
    queryKey: ["documents", workspaceId],
    queryFn: () => documentsApi.list(workspaceId),
  });

  const cards = [
    {
      label: "Conversations",
      value: conversations.length,
      to: `/app/w/${workspaceId}/chat`,
      icon: MessageSquare,
    },
    {
      label: "Agents",
      value: agents.length,
      to: `/app/w/${workspaceId}/agents`,
      icon: Bot,
    },
    {
      label: "Knowledge bases",
      value: knowledgeBases.length,
      to: `/app/w/${workspaceId}/knowledge`,
      icon: FileText,
    },
    {
      label: "Documents",
      value: documents.length,
      to: `/app/w/${workspaceId}/knowledge`,
      icon: FileText,
    },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="font-display text-3xl font-extrabold tracking-tight">
          {workspace?.name || "Workspace"}
        </h1>
        <p className="mt-2 max-w-2xl text-ink-600">
          {workspace?.description || "Your AI operating surface for chat, agents, and knowledge."}
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {cards.map(({ label, value, to, icon: Icon }) => (
          <Link key={label} to={to} className="card p-5 transition hover:border-accent/40">
            <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-xl bg-accent-muted text-accent">
              <Icon size={18} />
            </div>
            <div className="text-3xl font-semibold">{value}</div>
            <div className="mt-1 text-sm text-ink-500">{label}</div>
          </Link>
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="card p-5">
          <div className="mb-4 font-semibold">Recent conversations</div>
          <div className="space-y-2">
            {conversations.slice(0, 5).map((c) => (
              <Link
                key={c.id}
                to={`/app/w/${workspaceId}/chat/${c.id}`}
                className="block rounded-xl px-3 py-2 text-sm hover:bg-ink-50"
              >
                {c.title}
              </Link>
            ))}
            {conversations.length === 0 && (
              <p className="text-sm text-ink-500">No conversations yet.</p>
            )}
          </div>
        </div>
        <div className="card p-5">
          <div className="mb-4 font-semibold">Agents</div>
          <div className="space-y-2">
            {agents.slice(0, 5).map((a) => (
              <Link
                key={a.id}
                to={`/app/w/${workspaceId}/agents/${a.id}`}
                className="block rounded-xl px-3 py-2 text-sm hover:bg-ink-50"
              >
                {a.name}
                <span className="ml-2 text-ink-400">{a.tools || "no tools"}</span>
              </Link>
            ))}
            {agents.length === 0 && (
              <p className="text-sm text-ink-500">Create an agent to get started.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
