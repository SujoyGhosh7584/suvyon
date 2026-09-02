import { Link } from "react-router-dom";
import { ArrowRight, Bot, Check, FileText, MailCheck, MessageSquare, ShieldCheck, Sparkles } from "lucide-react";
import { AIBackdrop, BrandOrb } from "@/components/AIBackdrop";
import { GuestLink } from "@/components/GuestAuth";

export function MobileLandingPage() {
  return (
    <div className="relative min-h-[100dvh] overflow-hidden bg-[#080a12] text-white">
      <AIBackdrop />
      <header className="relative z-20 flex items-center justify-between px-5 pb-3 pt-[max(1rem,env(safe-area-inset-top))]">
        <Link to="/" className="flex items-center gap-2.5 font-display text-sm font-bold tracking-wide"><BrandOrb compact /> SUVYON</Link>
        <Link to="/login" className="rounded-xl border border-white/10 bg-white/5 px-3.5 py-2 text-xs font-semibold">Sign in</Link>
      </header>

      <main className="relative z-10">
        <section className="px-5 pb-16 pt-12 text-center">
          <div className="inline-flex items-center gap-2 rounded-full border border-indigo-300/20 bg-indigo-400/10 px-3 py-1.5 text-[10px] font-bold uppercase tracking-[.16em] text-indigo-200"><span className="ai-live-dot" /> Trusted AI workspace</div>
          <h1 className="text-balance mt-6 font-display text-[2.85rem] font-extrabold leading-[.98] tracking-[-.05em]">More than chat. <span className="bg-gradient-to-r from-indigo-300 via-white to-cyan-300 bg-clip-text text-transparent">AI that moves work forward.</span></h1>
          <p className="mx-auto mt-5 max-w-md text-[15px] leading-relaxed text-slate-300">Bring your knowledge, conversations, and specialist agents together—while you stay in control.</p>
          <GuestLink to="/register" className="btn-primary mt-7 flex w-full py-3.5 text-base">Create free workspace <ArrowRight size={17} /></GuestLink>
          <div className="mt-4 flex items-center justify-center gap-4 text-[10px] text-slate-400"><span className="flex items-center gap-1"><Check size={11} className="text-emerald-400" /> No card</span><span className="flex items-center gap-1"><Check size={11} className="text-emerald-400" /> Private</span><span className="flex items-center gap-1"><Check size={11} className="text-emerald-400" /> You approve</span></div>

          <div className="ai-float relative mt-12 overflow-hidden rounded-[26px] border border-white/15 bg-[#111522]/95 p-2 text-left shadow-2xl">
            <div className="flex items-center justify-between border-b border-white/10 px-3 py-2"><div className="flex gap-1.5"><span className="h-2 w-2 rounded-full bg-rose-400" /><span className="h-2 w-2 rounded-full bg-amber-300" /><span className="h-2 w-2 rounded-full bg-emerald-400" /></div><span className="text-[9px] font-semibold text-emerald-300">● AI READY</span></div>
            <div className="rounded-b-[20px] bg-[#f7f8fc] p-4 text-slate-950">
              <div className="flex items-center gap-3"><span className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-600 text-white"><Bot size={18} /></span><div><p className="text-sm font-bold">Interview Coach</p><p className="text-[10px] text-slate-500">Grounded in your workspace</p></div></div>
              <div className="mt-4 rounded-2xl bg-slate-950 p-3 text-xs leading-relaxed text-slate-200">Build my interview plan from this role and my project experience.</div>
              <div className="mt-3 grid grid-cols-3 gap-2">{[{ value: "82%", label: "Ready" }, { value: "7", label: "Sources" }, { value: "12", label: "Topics" }].map((item) => <div key={item.label} className="rounded-xl border border-slate-200 bg-white p-2 text-center"><p className="font-display text-lg font-bold text-indigo-700">{item.value}</p><p className="text-[9px] text-slate-500">{item.label}</p></div>)}</div>
            </div>
          </div>
        </section>

        <section className="border-y border-white/10 bg-white/[.03] px-5 py-16">
          <p className="text-xs font-bold uppercase tracking-[.18em] text-indigo-300">Everything connected</p>
          <h2 className="text-balance mt-3 font-display text-3xl font-bold">One place for your AI-powered work.</h2>
          <div className="mt-7 space-y-3">{[{ icon: MessageSquare, title: "Grounded conversations", text: "Talk with your documents and current web information." }, { icon: Bot, title: "Outcome-focused agents", text: "Start useful missions without technical setup." }, { icon: ShieldCheck, title: "Visible, approved actions", text: "Review sensitive work before it executes." }].map(({ icon: Icon, title, text }) => <div key={title} className="rounded-2xl border border-white/10 bg-white/5 p-4"><div className="flex gap-3"><span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-indigo-400/10 text-indigo-300"><Icon size={18} /></span><div><p className="font-semibold">{title}</p><p className="mt-1 text-xs leading-relaxed text-slate-400">{text}</p></div></div></div>)}</div>
        </section>

        <section className="px-5 py-16">
          <div className="rounded-[26px] border border-indigo-300/20 bg-gradient-to-br from-indigo-600 to-violet-800 p-6 text-center shadow-2xl"><Sparkles className="mx-auto text-indigo-200" size={24} /><h2 className="mt-4 font-display text-2xl font-bold">Start doing your best work with AI.</h2><p className="mt-3 text-sm text-indigo-100">Your first workspace is only a minute away.</p><GuestLink to="/register" className="mt-6 flex w-full items-center justify-center gap-2 rounded-xl bg-white px-5 py-3 text-sm font-bold text-indigo-700">Get started free <ArrowRight size={15} /></GuestLink></div>
          <div className="mt-8 grid grid-cols-3 gap-2 text-center text-[10px] text-slate-400">{[{ icon: FileText, label: "Knowledge" }, { icon: MailCheck, label: "Approvals" }, { icon: Bot, label: "Agents" }].map(({ icon: Icon, label }) => <div key={label}><Icon className="mx-auto mb-1.5 text-slate-300" size={16} />{label}</div>)}</div>
        </section>
      </main>
    </div>
  );
}
