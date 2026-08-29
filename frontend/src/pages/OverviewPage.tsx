import { Link, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ArrowUpRight, Bot, FileText, MessageSquare, Sparkles } from "lucide-react";
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
      className: "from-violet-600 to-indigo-600",
    },
    {
      label: "Agents",
      value: agents.length,
      to: `/app/w/${workspaceId}/agents`,
      icon: Bot,
      className: "from-rose-500 to-orange-400",
    },
    {
      label: "Knowledge bases",
      value: knowledgeBases.length,
      to: `/app/w/${workspaceId}/knowledge`,
      icon: FileText,
      className: "from-amber-500 to-yellow-400",
    },
    {
      label: "Documents",
      value: documents.length,
      to: `/app/w/${workspaceId}/knowledge`,
      icon: FileText,
      className: "from-sky-500 to-cyan-400",
    },
  ];

  return (
    <div className="space-y-8">
      <div className="relative overflow-hidden rounded-[2rem] bg-ink-950 p-8 text-white shadow-panel">
        <div className="pointer-events-none absolute -right-10 -top-16 h-56 w-56 rounded-full bg-indigo-500/40 blur-3xl" />
        <div className="pointer-events-none absolute bottom-0 left-1/2 h-40 w-40 rounded-full bg-rose-500/30 blur-3xl" />
        <div className="relative">
          <div className="mb-3 inline-flex items-center gap-2 rounded-full bg-white/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-indigo-200">
            <Sparkles size={12} />
            Overview
          </div>
          <h1 className="font-display text-4xl font-extrabold tracking-tight md:text-5xl">
            {workspace?.name || "Workspace"}
          </h1>
          <p className="mt-3 max-w-2xl text-ink-300">
            {workspace?.description || "Chat, run search or email agents, and ground answers in your files."}
          </p>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {cards.map(({ label, value, to, icon: Icon, className }) => (
          <Link
            key={label}
            to={to}
            className={`group relative overflow-hidden rounded-[1.6rem] bg-gradient-to-br ${className} p-5 text-white shadow-panel transition hover:-translate-y-0.5`}
          >
            <Icon className="mb-8 opacity-80" size={22} />
            <div className="font-display text-4xl font-extrabold">{value}</div>
            <div className="mt-1 flex items-center justify-between text-sm text-white/85">
              {label}
              <ArrowUpRight size={16} className="opacity-0 transition group-hover:opacity-100" />
            </div>
          </Link>
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-[1.6rem] bg-white p-6 text-ink-950 shadow-panel">
          <div className="mb-4 font-display text-lg font-bold text-ink-950">Recent conversations</div>
          <div className="space-y-1">
            {conversations.slice(0, 5).map((c) => (
              <Link
                key={c.id}
                to={`/app/w/${workspaceId}/chat/${c.id}`}
                className="block rounded-2xl px-3 py-2.5 text-sm text-ink-800 hover:bg-violet-50"
              >
                {c.title}
              </Link>
            ))}
            {conversations.length === 0 && (
              <p className="text-sm text-ink-500">No conversations yet.</p>
            )}
          </div>
        </div>
        <div className="rounded-[1.6rem] bg-white p-6 text-ink-950 shadow-panel">
          <div className="mb-4 font-display text-lg font-bold text-ink-950">Agents</div>
          <div className="space-y-1">
            {agents.slice(0, 5).map((a) => (
              <Link
                key={a.id}
                to={`/app/w/${workspaceId}/agents/${a.id}`}
                className="block rounded-2xl px-3 py-2.5 text-sm text-ink-800 hover:bg-rose-50"
              >
                {a.name}
                <span className="ml-2 text-ink-500">{a.tools || "no tools"}</span>
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
