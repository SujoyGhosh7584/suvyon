import { FormEvent, useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { BookOpen, CheckCircle2, Code2, ExternalLink, Github, GitPullRequest, Link2, LoaderCircle, Trash2 } from "lucide-react";
import { useParams } from "react-router-dom";
import { MessageContent } from "@/components/MessageContent";
import { getErrorMessage } from "@/lib/api";
import { githubApi } from "@/lib/services";
import type { GitHubProposal } from "@/types/api";
import { cn } from "@/lib/utils";

type Mode = "ask" | "docs" | "change";

export function GitHubProjectsPage() {
  const { workspaceId = "" } = useParams();
  const queryClient = useQueryClient();
  const [selectedId, setSelectedId] = useState("");
  const [repositoryId, setRepositoryId] = useState("");
  const [mode, setMode] = useState<Mode>("ask");
  const [input, setInput] = useState("");
  const [answer, setAnswer] = useState("");
  const [files, setFiles] = useState<string[]>([]);
  const [proposal, setProposal] = useState<GitHubProposal | null>(null);
  const [error, setError] = useState("");
  const projectsQuery = useQuery({ queryKey: ["github-projects", workspaceId], queryFn: () => githubApi.projects(workspaceId) });
  const repositoriesQuery = useQuery({ queryKey: ["github-repositories"], queryFn: githubApi.repositories, retry: false });
  const projects = projectsQuery.data || [];
  const selected = projects.find((project) => project.id === selectedId) || projects[0];
  useEffect(() => { if (!selectedId && projects[0]) setSelectedId(projects[0].id); }, [projects, selectedId]);
  const connectedIds = useMemo(() => new Set(projects.map((project) => project.full_name)), [projects]);
  const available = (repositoriesQuery.data || []).filter((repo) => !connectedIds.has(repo.full_name));
  const install = useMutation({ mutationFn: () => githubApi.installUrl(workspaceId), onSuccess: (url) => { window.location.href = url; }, onError: (err) => setError(getErrorMessage(err)) });
  const connect = useMutation({ mutationFn: () => { const repository = available.find((item) => `${item.installation_id}:${item.github_repo_id}` === repositoryId); if (!repository) throw new Error("Choose a repository first."); return githubApi.connect(workspaceId, repository); }, onSuccess: (project) => { queryClient.invalidateQueries({ queryKey: ["github-projects", workspaceId] }); setSelectedId(project.id); setRepositoryId(""); }, onError: (err) => setError(getErrorMessage(err)) });
  const disconnect = useMutation({ mutationFn: (id: string) => githubApi.disconnect(workspaceId, id), onSuccess: () => { setSelectedId(""); queryClient.invalidateQueries({ queryKey: ["github-projects", workspaceId] }); queryClient.invalidateQueries({ queryKey: ["github-repositories"] }); } });
  const run = useMutation({ mutationFn: async () => { if (!selected || !input.trim()) throw new Error("Select a repository and enter a request."); if (mode === "ask") return { kind: "answer" as const, value: await githubApi.ask(workspaceId, selected.id, input.trim()) }; if (mode === "docs") return { kind: "answer" as const, value: await githubApi.documentation(workspaceId, selected.id, input.trim()) }; return { kind: "proposal" as const, value: await githubApi.propose(workspaceId, selected.id, input.trim()) }; }, onSuccess: (result) => { setError(""); if (result.kind === "proposal") { setProposal(result.value); setAnswer(""); setFiles([]); } else { setAnswer(result.value.content); setFiles(result.value.files); setProposal(null); } }, onError: (err) => setError(getErrorMessage(err)) });
  const approve = useMutation({ mutationFn: () => githubApi.approve(workspaceId, selected!.id, proposal!.id), onSuccess: setProposal, onError: (err) => setError(getErrorMessage(err, "Pull request could not be created.")) });
  function submit(event: FormEvent) { event.preventDefault(); setError(""); run.mutate(); }

  return <div className="page-enter mx-auto max-w-6xl space-y-5 text-slate-950">
    <div className="flex flex-wrap items-start justify-between gap-3"><div><p className="text-[10px] font-bold uppercase tracking-[.2em] text-indigo-600">Repository intelligence</p><h2 className="mt-1 font-display text-3xl font-bold">Build with your GitHub projects</h2><p className="mt-2 text-sm text-slate-600">Ask grounded questions, create documentation, and review every change before Suvyon opens a pull request.</p></div><button className="btn-outline" onClick={() => install.mutate()} disabled={install.isPending}><Github size={17} /> {install.isPending ? "Opening GitHub…" : "Install GitHub App"}</button></div>
    {error && <div className="rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}
    <div className="grid gap-4 lg:grid-cols-[280px_1fr]">
      <aside className="rounded-[24px] border border-slate-200 bg-white p-3 shadow-sm"><div className="p-2 text-xs font-bold uppercase tracking-wider text-slate-500">Connected repositories</div><div className="space-y-1">{projects.map((project) => <button key={project.id} className={cn("w-full rounded-xl px-3 py-2.5 text-left text-sm", selected?.id === project.id ? "bg-indigo-50 text-indigo-950 ring-1 ring-indigo-100" : "hover:bg-slate-50")} onClick={() => { setSelectedId(project.id); setAnswer(""); setProposal(null); }}><span className="block truncate font-semibold">{project.full_name}</span><span className="text-[11px] text-slate-500">{project.default_branch} · {project.is_private ? "Private" : "Public"}</span></button>)}{!projects.length && <p className="px-3 py-5 text-sm text-slate-500">No repository connected yet.</p>}</div>{available.length > 0 && <div className="mt-4 border-t border-slate-100 pt-3"><select className="input text-sm" value={repositoryId} onChange={(event) => setRepositoryId(event.target.value)}><option value="">Choose installed repository</option>{available.map((repo) => <option key={`${repo.installation_id}:${repo.github_repo_id}`} value={`${repo.installation_id}:${repo.github_repo_id}`}>{repo.full_name}</option>)}</select><button className="btn-primary mt-2 w-full justify-center" disabled={!repositoryId || connect.isPending} onClick={() => connect.mutate()}><Link2 size={15} /> Connect</button></div>}</aside>
      <section className="min-w-0 rounded-[24px] border border-slate-200 bg-white p-5 shadow-sm">{!selected ? <div className="py-16 text-center"><Github className="mx-auto text-slate-300" size={38} /><h3 className="mt-3 font-semibold">Install and connect a repository</h3><p className="mt-1 text-sm text-slate-500">You decide exactly which repositories Suvyon can access.</p></div> : <>
        <div className="flex flex-wrap items-center gap-2 border-b border-slate-100 pb-4"><div className="mr-auto min-w-0"><h3 className="truncate font-display text-xl font-bold">{selected.full_name}</h3><p className="text-xs text-slate-500">Changes always require confirmation and use a new branch.</p></div><button className="rounded-xl p-2 text-slate-400 hover:bg-rose-50 hover:text-rose-700" title="Disconnect repository" onClick={() => { if (window.confirm(`Disconnect ${selected.full_name}?`)) disconnect.mutate(selected.id); }}><Trash2 size={17} /></button></div>
        <div className="mt-4 flex flex-wrap gap-2">{([{ id: "ask", label: "Ask", icon: Code2 }, { id: "docs", label: "Documentation", icon: BookOpen }, { id: "change", label: "Propose change", icon: GitPullRequest }] as const).map(({ id, label, icon: Icon }) => <button key={id} className={cn("rounded-xl px-3 py-2 text-sm font-semibold", mode === id ? "bg-slate-950 text-white" : "bg-slate-100 text-slate-600")} onClick={() => { setMode(id); setAnswer(""); setProposal(null); }}><Icon className="mr-1.5 inline" size={15} />{label}</button>)}</div>
        <form className="mt-4" onSubmit={submit}><textarea className="input min-h-[110px]" value={input} onChange={(event) => setInput(event.target.value)} placeholder={mode === "ask" ? "How does authentication work in this project?" : mode === "docs" ? "Create an onboarding guide with setup and architecture." : "Add validation and tests for…"} /><button className="btn-primary mt-2" disabled={!input.trim() || run.isPending}>{run.isPending ? <LoaderCircle className="animate-spin" size={16} /> : mode === "change" ? <GitPullRequest size={16} /> : <Code2 size={16} />} {run.isPending ? "Reading repository…" : mode === "change" ? "Generate proposal" : "Run"}</button></form>
        {answer && <div className="mt-5 rounded-2xl bg-slate-50 p-5"><MessageContent content={answer} />{files.length > 0 && <details className="mt-4 text-xs text-slate-500"><summary className="cursor-pointer font-semibold">Files consulted ({files.length})</summary><div className="mt-2 space-y-1">{files.map((file) => <code key={file} className="block">{file}</code>)}</div></details>}</div>}
        {proposal && <div className="mt-5 rounded-2xl border border-amber-200 bg-amber-50 p-5"><div className="flex items-center gap-2"><GitPullRequest size={18} /><h3 className="font-bold">{proposal.title}</h3></div><p className="mt-2 text-sm text-slate-700">{proposal.description}</p><div className="mt-4 space-y-2">{proposal.changes.map((change) => <details key={change.path} className="rounded-xl border border-amber-200 bg-white p-3"><summary className="cursor-pointer font-mono text-xs font-semibold">{change.path}</summary><p className="mt-2 text-xs text-slate-500">{change.reason}</p><pre className="mt-3 max-h-72 overflow-auto whitespace-pre-wrap rounded-lg bg-slate-950 p-3 text-xs text-slate-100">{change.content}</pre></details>)}</div>{proposal.status === "opened" && proposal.pull_request_url ? <a className="btn-primary mt-4 inline-flex" href={proposal.pull_request_url} target="_blank" rel="noreferrer"><CheckCircle2 size={16} /> View pull request <ExternalLink size={14} /></a> : <button className="mt-4 rounded-xl bg-emerald-700 px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-50" disabled={approve.isPending} onClick={() => { if (window.confirm("Create a branch, commit these exact files, and open a pull request?")) approve.mutate(); }}>{approve.isPending ? "Creating pull request…" : "Approve and create pull request"}</button>}</div>}
      </>}</section>
    </div>
  </div>;
}
