import { ReactNode } from "react";
import { Link } from "react-router-dom";
import { Bot, FileSearch, Sparkles } from "lucide-react";

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
    <div className="grid min-h-screen bg-mesh lg:grid-cols-2">
      <aside className="relative hidden flex-col justify-between overflow-hidden px-14 py-12 text-white lg:flex">
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(99,102,241,0.35),transparent_35%),radial-gradient(circle_at_80%_80%,rgba(244,63,94,0.22),transparent_40%)]" />
        <Link to="/" className="relative flex items-center gap-2 font-display text-2xl font-extrabold">
          <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-indigo-500">S</span>
          Suvyon
        </Link>
        <div className="relative max-w-lg pb-10">
          <p className="text-xs font-semibold uppercase tracking-[0.28em] text-indigo-200">
            Sign in
          </p>
          <h2 className="mt-4 font-display text-5xl font-extrabold leading-[1.05]">
            Your agents already know the tools.
          </h2>
          <p className="mt-4 text-ink-300">
            Search the live web, retrieve from your files, and keep every workspace
            separate.
          </p>
          <div className="mt-8 space-y-3 text-sm">
            {[
              { icon: Sparkles, text: "Auto-route Groq, Gemini, OpenRouter" },
              { icon: Bot, text: "Web-search agents for scores and news" },
              { icon: FileSearch, text: "Resume and PDF knowledge bases" },
            ].map(({ icon: Icon, text }) => (
              <div
                key={text}
                className="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/5 px-4 py-3"
              >
                <Icon size={18} className="text-indigo-300" />
                {text}
              </div>
            ))}
          </div>
        </div>
      </aside>

      <main className="flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-md rounded-[2rem] border border-white/15 bg-white p-8 text-ink-950 shadow-panel">
          <Link to="/" className="font-display text-2xl font-extrabold lg:hidden">
            Suvyon
          </Link>
          <h1 className="font-display text-3xl font-extrabold tracking-tight">{title}</h1>
          <p className="mt-2 text-sm text-ink-500">{subtitle}</p>
          <div className="mt-6">{children}</div>
          <div className="mt-5 text-sm text-ink-500">{footer}</div>
        </div>
      </main>
    </div>
  );
}
