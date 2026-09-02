import { Link } from "react-router-dom";
import {
  ArrowRight,
  Bot,
  BrainCircuit,
  Check,
  ChevronRight,
  FileText,
  Globe2,
  LockKeyhole,
  MailCheck,
  MessageSquare,
  Play,
  ShieldCheck,
  Sparkles,
  Workflow,
} from "lucide-react";
import { AIBackdrop, BrandOrb } from "@/components/AIBackdrop";
import { GuestLink } from "@/components/GuestAuth";

const capabilities = [
  { icon: BrainCircuit, title: "AI that understands your work", text: "Bring conversations, files, and live information into one focused workspace." },
  { icon: Workflow, title: "Agents built around outcomes", text: "Start interview, research, creative, and communication missions in one click." },
  { icon: ShieldCheck, title: "Control every important action", text: "Review and edit sensitive actions before Suvyon is allowed to execute them." },
];

export function LandingPage() {
  return (
    <div className="relative min-h-screen overflow-hidden bg-[#080a12] text-white">
      <AIBackdrop />

      <header className="relative z-20 mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
        <Link to="/" className="flex items-center gap-3 font-display text-lg font-bold tracking-tight">
          <BrandOrb compact />
          SUVYON
        </Link>
        <nav className="hidden items-center gap-8 text-sm font-medium text-slate-300 lg:flex">
          <a href="#platform" className="transition hover:text-white">Platform</a>
          <a href="#agents" className="transition hover:text-white">AI agents</a>
          <a href="#security" className="transition hover:text-white">Trust</a>
        </nav>
        <div className="flex items-center gap-2">
          <Link to="/login" className="rounded-xl px-4 py-2.5 text-sm font-semibold text-slate-200 transition hover:bg-white/10 hover:text-white">Sign in</Link>
          <GuestLink to="/register" className="btn-primary px-5">Start free <ArrowRight size={15} /></GuestLink>
        </div>
      </header>

      <main className="relative z-10">
        <section className="mx-auto max-w-7xl px-6 pb-24 pt-16 text-center lg:pt-24">
          <div className="mx-auto inline-flex items-center gap-2 rounded-full border border-indigo-300/20 bg-indigo-400/10 px-3.5 py-2 text-xs font-semibold text-indigo-200 backdrop-blur-xl">
            <span className="ai-live-dot" /> The trusted AI workspace for real work
          </div>
          <h1 className="text-balance mx-auto mt-7 max-w-5xl font-display text-6xl font-extrabold leading-[.98] tracking-[-.055em] lg:text-[5.6rem]">
            Your work deserves more than <span className="bg-gradient-to-r from-indigo-300 via-white to-cyan-300 bg-clip-text text-transparent">another chatbot.</span>
          </h1>
          <p className="text-balance mx-auto mt-7 max-w-2xl text-lg leading-relaxed text-slate-300 lg:text-xl">
            Suvyon connects your knowledge, conversations, and specialized AI agents—then keeps you in control of every action.
          </p>
          <div className="mt-9 flex flex-wrap items-center justify-center gap-3">
            <GuestLink to="/register" className="btn-primary px-6 py-3.5 text-base">Create your workspace <ArrowRight size={17} /></GuestLink>
            <a href="#platform" className="flex items-center gap-2 rounded-xl border border-white/15 bg-white/5 px-6 py-3.5 text-sm font-semibold text-white backdrop-blur-xl transition hover:bg-white/10"><Play size={15} fill="currentColor" /> See how it works</a>
          </div>
          <div className="mt-5 flex flex-wrap items-center justify-center gap-x-5 gap-y-2 text-xs text-slate-400">
            <span className="flex items-center gap-1.5"><Check size={13} className="text-emerald-400" /> No credit card</span>
            <span className="flex items-center gap-1.5"><Check size={13} className="text-emerald-400" /> Private workspaces</span>
            <span className="flex items-center gap-1.5"><Check size={13} className="text-emerald-400" /> Human-approved actions</span>
          </div>

          <div id="platform" className="ai-float relative mx-auto mt-16 max-w-6xl text-left">
            <div className="absolute -inset-10 bg-gradient-to-r from-indigo-600/20 via-violet-500/10 to-cyan-500/20 blur-3xl" />
            <div className="relative overflow-hidden rounded-[30px] border border-white/15 bg-[#111522]/95 p-2 shadow-[0_50px_140px_rgba(0,0,0,.55)] backdrop-blur-2xl">
              <div className="flex items-center justify-between border-b border-white/10 px-4 py-3">
                <div className="flex items-center gap-2"><span className="h-2.5 w-2.5 rounded-full bg-rose-400" /><span className="h-2.5 w-2.5 rounded-full bg-amber-300" /><span className="h-2.5 w-2.5 rounded-full bg-emerald-400" /></div>
                <div className="rounded-lg border border-white/10 bg-white/5 px-16 py-1.5 text-[10px] text-slate-500">app.suvyon.ai</div>
                <span className="flex items-center gap-1.5 text-[10px] font-semibold text-emerald-300"><span className="ai-live-dot" /> LIVE</span>
              </div>
              <div className="grid min-h-[500px] grid-cols-[82px_1fr]">
                <aside className="border-r border-white/10 p-3">
                  <div className="mx-auto mb-7"><BrandOrb compact /></div>
                  {[MessageSquare, Bot, FileText].map((Icon, index) => <div key={index} className={`mx-auto mb-3 flex h-11 w-11 items-center justify-center rounded-xl ${index === 1 ? "bg-white text-slate-950" : "text-slate-500"}`}><Icon size={18} /></div>)}
                </aside>
                <div className="bg-[#f7f8fc] p-6 text-slate-950">
                  <div className="flex items-center justify-between"><div><p className="text-[10px] font-bold uppercase tracking-[.2em] text-indigo-600">Agent mission</p><h3 className="font-display text-2xl font-bold">Interview intelligence</h3></div><span className="rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-800">Evidence ready</span></div>
                  <div className="mt-6 grid gap-4 lg:grid-cols-[1.2fr_.8fr]">
                    <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
                      <div className="flex items-center gap-3"><span className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-600 text-white"><Sparkles size={18} /></span><div><p className="font-semibold">Suvyon Interview Coach</p><p className="text-xs text-slate-500">Resume + role + live company research</p></div></div>
                      <div className="mt-6 rounded-2xl bg-slate-950 p-4 text-sm leading-relaxed text-slate-200">“Compare my project experience with this role and build a focused interview plan.”</div>
                      <div className="mt-4 space-y-3">
                        {["Reading 4 project documents", "Researching current role expectations", "Building your evidence-backed plan"].map((step, index) => <div key={step} className="flex items-center gap-3 rounded-xl border border-slate-100 px-3 py-2.5 text-sm"><span className={`flex h-6 w-6 items-center justify-center rounded-full ${index < 2 ? "bg-emerald-100 text-emerald-700" : "bg-indigo-100 text-indigo-700"}`}>{index < 2 ? <Check size={13} /> : <Sparkles size={12} />}</span>{step}</div>)}
                      </div>
                    </div>
                    <div className="space-y-4">
                      <div className="rounded-3xl bg-gradient-to-br from-indigo-600 to-violet-700 p-5 text-white shadow-xl"><p className="text-xs text-indigo-200">Readiness score</p><p className="mt-2 font-display text-5xl font-bold">82<span className="text-xl text-indigo-200">%</span></p><div className="mt-4 h-1.5 rounded-full bg-white/20"><div className="h-full w-[82%] rounded-full bg-white" /></div></div>
                      <div className="rounded-3xl border border-slate-200 bg-white p-5"><p className="text-xs font-bold uppercase tracking-wider text-slate-500">Proof layer</p><div className="mt-4 space-y-3 text-sm">{["4 workspace sources", "3 live web sources", "1 action needs approval"].map((item) => <div key={item} className="flex items-center gap-2 text-slate-700"><ChevronRight size={14} className="text-indigo-600" />{item}</div>)}</div></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section id="agents" className="border-y border-white/10 bg-white/[.025] py-24">
          <div className="mx-auto max-w-7xl px-6">
            <div className="grid gap-12 lg:grid-cols-[.8fr_1.2fr] lg:items-end">
              <div><p className="text-xs font-bold uppercase tracking-[.22em] text-indigo-300">One intelligent platform</p><h2 className="text-balance mt-4 font-display text-4xl font-bold tracking-tight lg:text-5xl">From scattered AI tools to one clear workflow.</h2></div>
              <p className="max-w-xl text-lg leading-relaxed text-slate-300">Suvyon gives every workspace its own conversations, knowledge, agent missions, and approval boundaries—without exposing technical complexity to your team.</p>
            </div>
            <div className="mt-12 grid gap-4 md:grid-cols-3">{capabilities.map(({ icon: Icon, title, text }) => <article key={title} className="group rounded-[26px] border border-white/10 bg-white/5 p-6 backdrop-blur-xl transition duration-300 hover:-translate-y-1 hover:border-indigo-300/30 hover:bg-white/[.075]"><span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-indigo-400/10 text-indigo-300 transition group-hover:scale-110"><Icon size={22} /></span><h3 className="mt-7 font-display text-xl font-bold">{title}</h3><p className="mt-3 text-sm leading-relaxed text-slate-400">{text}</p></article>)}</div>
          </div>
        </section>

        <section id="security" className="mx-auto grid max-w-7xl gap-12 px-6 py-24 lg:grid-cols-2 lg:items-center">
          <div className="relative rounded-[30px] border border-white/10 bg-gradient-to-br from-white/10 to-white/[.025] p-7 backdrop-blur-xl"><div className="grid grid-cols-2 gap-3">{[{ icon: Globe2, label: "Live research" }, { icon: FileText, label: "Grounded knowledge" }, { icon: Bot, label: "Specialist agents" }, { icon: MailCheck, label: "Approved actions" }].map(({ icon: Icon, label }) => <div key={label} className="rounded-2xl border border-white/10 bg-[#0d101b]/70 p-5"><Icon className="text-indigo-300" size={20} /><p className="mt-6 text-sm font-semibold">{label}</p></div>)}</div></div>
          <div><span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-400/10 text-emerald-300"><LockKeyhole size={22} /></span><p className="mt-7 text-xs font-bold uppercase tracking-[.22em] text-emerald-300">Human control by design</p><h2 className="text-balance mt-3 font-display text-4xl font-bold tracking-tight">Powerful enough to act. Safe enough to trust.</h2><p className="mt-5 text-lg leading-relaxed text-slate-300">AI can prepare work, but you remain the decision maker. Sensitive operations open as editable approval cards before they execute.</p><GuestLink to="/register" className="mt-8 inline-flex items-center gap-2 text-sm font-bold text-white">Build your first workspace <ArrowRight size={16} /></GuestLink></div>
        </section>

        <section className="mx-auto max-w-7xl px-6 pb-24">
          <div className="relative overflow-hidden rounded-[32px] border border-indigo-300/20 bg-gradient-to-br from-indigo-600 to-violet-800 px-7 py-16 text-center shadow-[0_30px_100px_rgba(79,70,229,.35)]"><div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_0%,rgba(255,255,255,.22),transparent_35%)]" /><div className="relative"><Sparkles className="mx-auto text-indigo-200" size={28} /><h2 className="text-balance mx-auto mt-5 max-w-3xl font-display text-4xl font-bold">Give your best work an intelligent place to happen.</h2><p className="mt-4 text-indigo-100">Create your Suvyon workspace and start with a mission in minutes.</p><GuestLink to="/register" className="mt-8 inline-flex items-center gap-2 rounded-xl bg-white px-6 py-3.5 text-sm font-bold text-indigo-700 transition hover:-translate-y-1 hover:shadow-xl">Get started free <ArrowRight size={16} /></GuestLink></div></div>
        </section>
      </main>

      <footer className="relative z-10 border-t border-white/10 px-6 py-8 text-sm text-slate-500"><div className="mx-auto flex max-w-7xl items-center justify-between"><div className="flex items-center gap-2 text-white"><BrandOrb compact /><span className="font-display font-bold">SUVYON</span></div><p>Intelligence with clarity and control.</p></div></footer>
    </div>
  );
}
