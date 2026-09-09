import { ReactNode } from "react";
import { Link } from "react-router-dom";
import { ArrowUpRight, Check, GitBranch, ShieldCheck, Sparkles } from "lucide-react";
import { BrandOrb } from "@/components/AIBackdrop";

export function AuthScreen({ title, subtitle, children, footer }: { title: string; subtitle: string; children: ReactNode; footer: ReactNode }) {
  return <div className="auth-layout">
    <aside className="auth-story">
      <Link to="/" className="flex w-fit items-center gap-3 text-xl font-semibold tracking-tight"><BrandOrb />suvyon<span className="brand-tag">WORKSPACE</span></Link>
      <div className="auth-story-content">
        <p className="flex items-center gap-2 text-xs font-medium uppercase tracking-[.18em] text-[#d4fa75]"><span className="h-1.5 w-1.5 rounded-full bg-current" /> A little curiosity. A lot of possibility.</p>
        <h2>Big ideas.<br /><span>Meet your<br />next move.</span></h2>
        <p className="mt-5 max-w-sm text-sm leading-7 text-slate-400">Your models, your knowledge, your agents.<br />One place to turn thinking into doing.</p>
        <div className="auth-demo" aria-label="Example agent workflow">
          <div className="flex items-center justify-between border-b border-white/10 pb-3"><span className="flex items-center gap-2 text-xs font-medium"><Sparkles size={15} className="text-[#b3bfff]" /> From question to next step</span><span className="text-[10px] text-slate-400">EXAMPLE</span></div>
          <p className="my-4 rounded-xl bg-white/[.06] p-3 text-sm text-slate-200">Research the options. Find a better way forward.</p>
          <div className="space-y-3">{["Explore the sources", "Compare the possibilities", "Build a clear recommendation"].map((text, i) => <div key={text} className="flex items-center gap-3 text-xs text-slate-300"><span className="flex h-5 w-5 items-center justify-center rounded-full bg-[#d4fa75]/10 text-[#d4fa75]">{i < 2 ? <Check size={12} /> : <ArrowUpRight size={12} />}</span>{text}</div>)}</div>
          <div className="mt-4 flex items-center gap-2 border-t border-white/10 pt-3 text-[11px] text-slate-400"><GitBranch size={13} /> Explore another direction whenever you want.</div>
        </div>
      </div>
      <p className="flex items-center gap-2 text-xs text-slate-400"><ShieldCheck size={14} /> Your workspace. Your decisions.</p>
      <div className="auth-orbit" aria-hidden="true" />
    </aside>
    <main className="auth-main">
      <Link to="/" className="mb-8 flex items-center gap-2 text-xl font-semibold lg:hidden"><BrandOrb />suvyon</Link>
      <div className="auth-form page-enter">
        <div className="mb-5 inline-flex h-10 w-10 items-center justify-center rounded-xl border border-indigo-100 bg-indigo-50 text-indigo-600"><ArrowUpRight size={20} /></div>
        <h1 className="font-display text-3xl font-bold tracking-[-.045em] text-slate-950">{title}</h1>
        <p className="mt-2 text-sm leading-relaxed text-slate-500">{subtitle}</p>
        <div className="mt-7">{children}</div>
        <div className="mt-6 border-t border-slate-200 pt-5 text-sm text-slate-500">{footer}</div>
        <p className="mt-7 flex items-center gap-2 text-xs text-slate-400"><ShieldCheck size={13} /> Secure sign-in. A space of your own.</p>
      </div>
      <span className="auth-corner" aria-hidden="true">MAKE ROOM FOR WHAT?S NEXT.</span>
    </main>
  </div>;
}
