import { Link } from "react-router-dom";
import { ArrowRight, Bot, FileText, Sparkles } from "lucide-react";
import { GuestLink } from "@/components/GuestAuth";
import { MobileMascot } from "@/components/MobileMascot";
import { ThemePicker } from "@/components/ThemePicker";

export function MobileLandingPage() {
  return (
    <div className="min-h-[100dvh] bg-mesh px-5 pb-10 pt-[max(1rem,env(safe-area-inset-top))] text-white">
      <header className="mb-8 flex items-center justify-between">
        <div className="flex items-center gap-2 font-display text-xl font-extrabold">
          <span className="brand-mark flex h-9 w-9 items-center justify-center rounded-2xl">S</span>
          Suvyon
        </div>
        <Link to="/login" className="text-sm font-semibold text-white/80">
          Sign in
        </Link>
      </header>

      <MobileMascot />
      <p className="mt-5 text-center text-xs font-semibold uppercase tracking-[0.22em] text-indigo-200">
        Pocket workspace
      </p>
      <h1 className="mt-3 text-center font-display text-[2.4rem] font-extrabold leading-[1.05] tracking-tight">
        Ask anything.
        <span className="hero-title-accent mt-1 block bg-clip-text text-transparent">Cute answers.</span>
      </h1>
      <p className="mx-auto mt-4 max-w-sm text-center text-[15px] leading-relaxed text-ink-300">
        Chat, search the web, and talk to your files — same account as on your computer.
      </p>

      <div className="mt-8 space-y-3">
        <GuestLink to="/register" className="btn-primary flex w-full justify-center py-3.5 text-base">
          Get started
          <ArrowRight size={16} />
        </GuestLink>
        <Link
          to="/login"
          className="flex w-full items-center justify-center rounded-full border border-white/20 py-3.5 text-sm font-semibold"
        >
          I already have an account
        </Link>
      </div>

      <div className="mt-8 grid grid-cols-3 gap-2 text-center text-[11px] text-ink-300">
        <div className="rounded-[1.2rem] bg-white/10 px-2 py-4">
          <Sparkles size={16} className="mx-auto mb-2 text-indigo-300" />
          Chat
        </div>
        <div className="rounded-[1.2rem] bg-white/10 px-2 py-4">
          <Bot size={16} className="mx-auto mb-2 text-rose-300" />
          Agents
        </div>
        <div className="rounded-[1.2rem] bg-white/10 px-2 py-4">
          <FileText size={16} className="mx-auto mb-2 text-amber-300" />
          Docs
        </div>
      </div>

      <div className="mt-8">
        <p className="mb-2 text-center text-[10px] uppercase tracking-[0.18em] text-ink-400">Theme</p>
        <ThemePicker compact />
      </div>
    </div>
  );
}
