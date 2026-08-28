import { Link } from "react-router-dom";
import { ArrowRight, Bot, Layers, Sparkles } from "lucide-react";

export function LandingPage() {
  return (
    <div className="min-h-screen bg-mesh text-white">
      <header className="relative mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
        <div className="flex items-center gap-2 font-display text-2xl font-extrabold tracking-tight">
          <span className="flex h-9 w-9 items-center justify-center rounded-2xl bg-indigo-500">S</span>
          Suvyon
        </div>
        <div className="flex items-center gap-3">
          <Link to="/login" className="btn-ghost">
            Sign in
          </Link>
          <Link to="/register" className="btn-primary">
            Get started
          </Link>
        </div>
      </header>

      <section className="relative mx-auto grid max-w-6xl gap-12 px-6 pb-24 pt-10 md:grid-cols-[1.15fr_0.85fr] md:items-center md:pt-20">
        <div>
          <p className="mb-5 inline-flex rounded-full border border-white/15 bg-white/5 px-3 py-1 text-xs font-semibold uppercase tracking-[0.22em] text-indigo-200">
            Live search · RAG · Agents
          </p>
          <h1 className="font-display text-5xl font-extrabold leading-[1.02] tracking-tight md:text-7xl">
            Ask anything.
            <span className="mt-2 block bg-gradient-to-r from-indigo-300 via-white to-rose-300 bg-clip-text text-transparent">
              Grounded answers.
            </span>
          </h1>
          <p className="mt-6 max-w-xl text-lg leading-relaxed text-ink-300">
            One workspace for chat, web-search agents, and documents. Route across Groq,
            Gemini, and OpenRouter without leaving the thread.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link to="/register" className="btn-primary">
              Create a workspace
              <ArrowRight size={16} />
            </Link>
            <Link
              to="/login"
              className="rounded-full border border-white/20 px-4 py-2.5 text-sm font-semibold text-white hover:bg-white/10"
            >
              I already have an account
            </Link>
          </div>
        </div>

        <div className="relative">
          <div className="absolute -inset-8 rounded-[2.2rem] bg-gradient-to-br from-indigo-500/40 via-transparent to-rose-500/30 blur-3xl" />
          <div className="relative overflow-hidden rounded-[2rem] border border-white/15 bg-ink-900/80 p-6 shadow-panel backdrop-blur">
            <div className="mb-5 flex items-center justify-between text-sm text-ink-300">
              <span className="font-display text-lg text-white">Tonight’s run</span>
              <Sparkles size={18} className="text-indigo-300" />
            </div>
            <div className="space-y-3 text-sm">
              <div className="rounded-2xl bg-white/5 px-4 py-3">What’s the IND vs SL Day 4 score?</div>
              <div className="rounded-2xl border border-rose-400/30 bg-rose-500/15 px-4 py-3 text-rose-100">
                Agent → <strong>web_search</strong> · Tavily
              </div>
              <div className="rounded-2xl bg-indigo-500/15 px-4 py-3 text-indigo-100">
                Grounded answer with sources, not a blank wait.
              </div>
            </div>
            <div className="mt-6 grid grid-cols-3 gap-3 text-xs text-ink-300">
              <div className="rounded-2xl bg-white/5 p-3">
                <Bot size={16} className="mb-2 text-rose-300" />
                Agents
              </div>
              <div className="rounded-2xl bg-white/5 p-3">
                <Layers size={16} className="mb-2 text-amber-300" />
                Knowledge
              </div>
              <div className="rounded-2xl bg-white/5 p-3">
                <Sparkles size={16} className="mb-2 text-indigo-300" />
                Routing
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
