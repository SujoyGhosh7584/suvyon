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
    <div className="grid min-h-screen lg:grid-cols-[1.05fr_0.95fr]">
      <aside className="relative hidden overflow-hidden bg-ink-950 px-12 py-12 text-sand lg:flex lg:flex-col">
        <div className="pointer-events-none absolute -left-24 top-10 h-80 w-80 rounded-full bg-accent/30 blur-3xl" />
        <div className="pointer-events-none absolute bottom-0 right-0 h-96 w-96 rounded-full bg-violet-500/20 blur-3xl" />
        <Link to="/" className="relative font-display text-3xl font-extrabold tracking-tight">
          Suvyon
        </Link>
        <div className="relative mt-auto max-w-md pb-8">
          <p className="text-sm font-semibold uppercase tracking-[0.22em] text-accent-soft">
            AI workspace
          </p>
          <h2 className="mt-4 font-display text-4xl font-extrabold leading-tight">
            Chat, search, and retrieve — in one place.
          </h2>
          <p className="mt-4 text-sand/70">
            Route questions to live web search or your own documents. Agents handle the
            tools; you get the answer.
          </p>
          <div className="mt-8 grid gap-3 text-sm">
            <div className="flex items-start gap-3 rounded-2xl bg-white/5 px-4 py-3">
              <Sparkles size={18} className="mt-0.5 text-accent-soft" />
              <span>Multi-provider chat with auto routing</span>
            </div>
            <div className="flex items-start gap-3 rounded-2xl bg-white/5 px-4 py-3">
              <Bot size={18} className="mt-0.5 text-accent-soft" />
              <span>Tool-using agents for live scores and news</span>
            </div>
            <div className="flex items-start gap-3 rounded-2xl bg-white/5 px-4 py-3">
              <FileSearch size={18} className="mt-0.5 text-accent-soft" />
              <span>Knowledge bases grounded in your files</span>
            </div>
          </div>
        </div>
      </aside>

      <main className="flex items-center justify-center bg-mesh px-4 py-12">
        <div className="card w-full max-w-md p-8 shadow-panel">
          <Link to="/" className="font-display text-2xl font-extrabold lg:hidden">
            Suvyon
          </Link>
          <h1 className="mt-2 font-display text-3xl font-extrabold tracking-tight lg:mt-0">
            {title}
          </h1>
          <p className="mt-2 text-sm text-ink-500">{subtitle}</p>
          <div className="mt-6">{children}</div>
          <div className="mt-5 text-sm text-ink-500">{footer}</div>
        </div>
      </main>
    </div>
  );
}
