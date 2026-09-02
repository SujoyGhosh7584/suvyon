import { Link, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ArrowRight, ArrowUpRight, Bot, FileText, MessageSquare, Plus, Sparkles, Zap } from "lucide-react";
import { agentsApi, conversationsApi, documentsApi, knowledgeApi, workspacesApi } from "@/lib/services";
import { TOOL_DETAILS } from "@/lib/agentTemplates";

export function OverviewPage() {
  const { workspaceId = "" } = useParams();
  const { data: workspace } = useQuery({ queryKey: ["workspace", workspaceId], queryFn: () => workspacesApi.get(workspaceId) });
  const { data: conversations = [] } = useQuery({ queryKey: ["conversations", workspaceId], queryFn: () => conversationsApi.list(workspaceId) });
  const { data: agents = [] } = useQuery({ queryKey: ["agents", workspaceId], queryFn: () => agentsApi.list(workspaceId) });
  const { data: knowledgeBases = [] } = useQuery({ queryKey: ["knowledge-bases", workspaceId], queryFn: () => knowledgeApi.list(workspaceId) });
  const { data: documents = [] } = useQuery({ queryKey: ["documents", workspaceId], queryFn: () => documentsApi.list(workspaceId) });

  const metrics = [
    { label: "Conversations", value: conversations.length, icon: MessageSquare, color: "bg-indigo-50 text-indigo-700" },
    { label: "Active agents", value: agents.filter((agent) => agent.is_active).length, icon: Bot, color: "bg-violet-50 text-violet-700" },
    { label: "Knowledge spaces", value: knowledgeBases.length, icon: FileText, color: "bg-cyan-50 text-cyan-700" },
    { label: "Indexed documents", value: documents.filter((document) => document.status === "ready").length, icon: Zap, color: "bg-emerald-50 text-emerald-700" },
  ];

  return (
    <div className="space-y-5 text-slate-950">
      <section className="grid gap-4 xl:grid-cols-[1.45fr_.55fr]">
        <div className="relative overflow-hidden rounded-[28px] bg-[#111522] p-6 text-white shadow-xl md:p-8">
          <div className="absolute -right-16 -top-24 h-72 w-72 rounded-full bg-indigo-500/30 blur-3xl" />
          <div className="absolute bottom-0 left-1/3 h-40 w-40 rounded-full bg-cyan-400/10 blur-3xl" />
          <div className="relative">
            <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-[.22em] text-indigo-300"><span className="ai-live-dot" /> Workspace intelligence ready</div>
            <h2 className="text-balance mt-5 max-w-2xl font-display text-3xl font-bold tracking-tight md:text-4xl">What will you move forward in {workspace?.name || "this workspace"}?</h2>
            <p className="mt-3 max-w-xl text-sm leading-relaxed text-slate-300">Start a conversation, launch a specialist mission, or add trusted knowledge for more precise answers.</p>
            <div className="mt-7 flex flex-wrap gap-2">
              <Link to={`/app/w/${workspaceId}/chat`} className="btn-primary"><MessageSquare size={16} /> Ask Suvyon</Link>
              <Link to={`/app/w/${workspaceId}/agents`} className="rounded-xl border border-white/15 bg-white/10 px-4 py-2.5 text-sm font-semibold transition hover:bg-white/15"><Bot className="mr-2 inline" size={16} />Launch agent</Link>
            </div>
          </div>
        </div>
        <Link to={`/app/w/${workspaceId}/knowledge`} className="group flex min-h-[220px] flex-col justify-between overflow-hidden rounded-[28px] border border-indigo-100 bg-gradient-to-br from-indigo-50 via-white to-cyan-50 p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-xl">
          <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white text-indigo-700 shadow-sm"><Plus size={20} /></span>
          <div><p className="text-[10px] font-bold uppercase tracking-[.2em] text-indigo-600">Improve answer quality</p><h3 className="mt-2 font-display text-2xl font-bold">Add knowledge</h3><p className="mt-2 text-sm text-slate-600">Upload project files, guides, or research.</p><ArrowUpRight className="mt-5 text-indigo-700 transition group-hover:-translate-y-1 group-hover:translate-x-1" size={20} /></div>
        </Link>
      </section>

      <section className="grid grid-cols-2 gap-3 xl:grid-cols-4">
        {metrics.map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="rounded-2xl border border-slate-200/80 bg-white p-4 shadow-sm md:p-5">
            <div className="flex items-start justify-between"><span className={`flex h-9 w-9 items-center justify-center rounded-xl ${color}`}><Icon size={17} /></span><span className="font-display text-3xl font-bold tracking-tight text-slate-950">{value}</span></div>
            <p className="mt-5 text-xs font-semibold text-slate-500">{label}</p>
          </div>
        ))}
      </section>

      <section className="grid gap-4 xl:grid-cols-[1.15fr_.85fr]">
        <div className="rounded-[24px] border border-slate-200/80 bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between"><div><p className="text-[10px] font-bold uppercase tracking-[.18em] text-slate-500">Continue working</p><h3 className="mt-1 font-display text-lg font-bold">Recent conversations</h3></div><Link to={`/app/w/${workspaceId}/chat`} className="text-xs font-bold text-indigo-700">View all</Link></div>
          <div className="mt-5 space-y-2">
            {conversations.slice(0, 4).map((conversation) => <Link key={conversation.id} to={`/app/w/${workspaceId}/chat/${conversation.id}`} className="group flex items-center gap-3 rounded-2xl border border-transparent px-3 py-3 transition hover:border-slate-200 hover:bg-slate-50"><span className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-100 text-slate-600"><MessageSquare size={17} /></span><span className="min-w-0 flex-1 truncate text-sm font-semibold">{conversation.title}</span><ArrowRight size={15} className="text-slate-300 transition group-hover:translate-x-1 group-hover:text-indigo-600" /></Link>)}
            {conversations.length === 0 && <EmptyBlock icon={MessageSquare} text="Your conversations will appear here." action="Start a chat" to={`/app/w/${workspaceId}/chat`} />}
          </div>
        </div>

        <div className="rounded-[24px] border border-slate-200/80 bg-white p-5 shadow-sm">
          <div><p className="text-[10px] font-bold uppercase tracking-[.18em] text-slate-500">Your AI team</p><h3 className="mt-1 font-display text-lg font-bold">Agent missions</h3></div>
          <div className="mt-5 space-y-2">
            {agents.slice(0, 4).map((agent) => {
              const firstTool = (agent.tools || "").split(",").filter(Boolean)[0];
              return <Link key={agent.id} to={`/app/w/${workspaceId}/agents/${agent.id}`} className="group flex items-center gap-3 rounded-2xl px-3 py-3 transition hover:bg-slate-50"><span className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-600 to-violet-600 text-white"><Sparkles size={16} /></span><span className="min-w-0 flex-1"><span className="block truncate text-sm font-semibold">{agent.name}</span><span className="block truncate text-[11px] text-slate-500">{TOOL_DETAILS[firstTool]?.name || agent.description || "Conversation agent"}</span></span><span className={`h-2 w-2 rounded-full ${agent.is_active ? "bg-emerald-400" : "bg-slate-300"}`} /></Link>;
            })}
            {agents.length === 0 && <EmptyBlock icon={Bot} text="Create a specialist agent for repeatable work." action="Explore agents" to={`/app/w/${workspaceId}/agents`} />}
          </div>
        </div>
      </section>
    </div>
  );
}

function EmptyBlock({ icon: Icon, text, action, to }: { icon: typeof Bot; text: string; action: string; to: string }) {
  return <div className="rounded-2xl border border-dashed border-slate-200 bg-slate-50/70 p-6 text-center"><Icon className="mx-auto text-slate-300" size={24} /><p className="mt-2 text-sm text-slate-500">{text}</p><Link to={to} className="mt-3 inline-flex items-center gap-1 text-xs font-bold text-indigo-700">{action}<ArrowRight size={13} /></Link></div>;
}
