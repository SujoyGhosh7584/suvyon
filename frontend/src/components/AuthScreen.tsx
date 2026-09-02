import { ReactNode } from "react";
import { Link } from "react-router-dom";
import { Bot, FileSearch, Mail, ShieldCheck, Sparkles } from "lucide-react";
import { AIBackdrop, BrandOrb } from "@/components/AIBackdrop";

export function AuthScreen({
  title,
  subtitle,
  children,
  footer,
}: {
  title: string;
  subtitle: string;
  children: ReactNode;
  footer: ReactNode;
}) {
  return (
    <div className="relative grid min-h-screen overflow-hidden bg-mesh lg:grid-cols-2">
      <AIBackdrop />
      <aside className="relative hidden flex-col justify-between overflow-hidden px-14 py-12 text-white lg:flex">
        <div className="pointer-events-none absolute inset-0 auth-glow" />
        <Link to="/" className="relative flex items-center gap-2 font-display text-2xl font-extrabold">
          <BrandOrb />
          Suvyon
        </Link>
        <div className="relative max-w-lg pb-10">
          <p className="hero-kicker text-xs font-semibold uppercase tracking-[0.28em]">
            Sign in
          </p>
          <h2 className="mt-4 font-display text-5xl font-extrabold leading-[1.05]">
            Move from questions to trusted action.
          </h2>
          <p className="mt-4 text-ink-300">
            Research the live web, work from your documents, and review every important
            action before it happens.
          </p>
          <div className="mt-8 space-y-3 text-sm">
            {[
              { icon: Sparkles, text: "Auto-route Groq, Gemini, OpenRouter" },
              { icon: Bot, text: "Web-search agents for scores and news" },
              { icon: Mail, text: "Editable email approval before anything is sent" },
              { icon: FileSearch, text: "Resume and PDF knowledge bases" },
            ].map(({ icon: Icon, text }) => (
              <div
                key={text}
                className="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/5 px-4 py-3"
              >
                <Icon size={18} className="text-accent-soft" />
                {text}
              </div>
            ))}
          </div>
        </div>
      </aside>

      <main className="flex items-center justify-center px-4 py-12 pt-[max(3rem,env(safe-area-inset-top))]">
        <div className="page-enter relative w-full max-w-md overflow-hidden rounded-[2rem] border border-white/70 bg-white/[.82] p-6 text-ink-950 shadow-2xl backdrop-blur-2xl sm:p-8">
          <div className="pointer-events-none absolute inset-x-8 top-0 h-px bg-gradient-to-r from-transparent via-accent to-transparent" />
          <Link to="/" className="mb-5 flex items-center gap-2 lg:hidden">
            <BrandOrb />
            <span className="font-display text-xl font-extrabold">Suvyon</span>
          </Link>
          <h1 className="font-display text-3xl font-extrabold tracking-tight">{title}</h1>
          <p className="mt-2 text-sm text-ink-500">{subtitle}</p>
          <div className="mt-6">{children}</div>
          <div className="mt-5 text-sm text-ink-500">{footer}</div>
          <div className="mt-6 flex items-center justify-center gap-2 border-t border-ink-100 pt-5 text-xs text-ink-400">
            <ShieldCheck size={14} /> Secure sign-in · private workspaces
          </div>
        </div>
      </main>
    </div>
  );
}
