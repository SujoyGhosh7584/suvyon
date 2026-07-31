import { Link } from "react-router-dom";
import { ArrowRight, Bot, Layers, Sparkles } from "lucide-react";

export function LandingPage() {
  return (
    <div className="min-h-screen bg-mesh">
      <div className="relative overflow-hidden">
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_70%_30%,rgba(20,184,166,0.22),transparent_35%)]" />
        <header className="relative mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
          <div className="font-display text-2xl font-extrabold tracking-tight">Suvyon</div>
          <div className="flex items-center gap-3">
            <Link to="/login" className="btn-ghost">
              Sign in
            </Link>
            <Link to="/register" className="btn-primary">
              Get started
            </Link>
          </div>
        </header>

        <section className="relative mx-auto grid max-w-6xl gap-10 px-6 pb-20 pt-10 md:grid-cols-[1.1fr_0.9fr] md:items-center md:pt-16">
          <div>
            <p className="mb-4 text-sm font-semibold uppercase tracking-[0.2em] text-accent">
              AI operating workspace
            </p>
            <h1 className="font-display text-5xl font-extrabold leading-[1.05] tracking-tight text-ink-950 md:text-6xl">
              Suvyon
            </h1>
            <p className="mt-5 max-w-xl text-lg leading-relaxed text-ink-600">
              Research, chat, and orchestrate tool-using agents in one workspace —
              with multi-provider LLM routing and grounded knowledge retrieval.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link to="/register" className="btn-accent">
                Create workspace
                <ArrowRight size={16} />
              </Link>
              <Link to="/login" className="btn-outline">
                I already have an account
              </Link>
            </div>
          </div>

          <div className="relative">
            <div className="absolute -inset-6 rounded-[2rem] bg-gradient-to-br from-accent-soft/30 via-transparent to-ink-200/40 blur-2xl" />
            <div className="relative overflow-hidden rounded-[2rem] border border-ink-200/70 bg-ink-950 p-6 text-sand shadow-panel">
              <div className="mb-6 flex items-center justify-between">
                <span className="font-display text-lg">Live orchestration</span>
                <Sparkles size={18} className="text-accent-soft" />
              </div>
              <div className="space-y-3 text-sm">
                <div className="rounded-xl bg-white/5 p-3">User asks about latest AI agents</div>
                <div className="rounded-xl border border-accent-soft/30 bg-accent/20 p-3">
                  Agent selects <strong>web_search</strong>
                </div>
                <div className="rounded-xl bg-white/5 p-3">
                  Tool returns sources → model writes grounded answer
                </div>
              </div>
              <div className="mt-6 grid grid-cols-3 gap-3 text-xs text-sand/80">
                <div className="rounded-xl bg-white/5 p-3">
                  <Bot size={16} className="mb-2 text-accent-soft" />
                  Agents
                </div>
                <div className="rounded-xl bg-white/5 p-3">
                  <Layers size={16} className="mb-2 text-accent-soft" />
                  RAG
                </div>
                <div className="rounded-xl bg-white/5 p-3">
                  <Sparkles size={16} className="mb-2 text-accent-soft" />
                  Routing
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
