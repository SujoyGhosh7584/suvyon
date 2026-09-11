import { useEffect, useMemo, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import {
  Bot,
  Check,
  FileText,
  Github,
  LayoutDashboard,
  MessageSquare,
  Palette,
  Search,
  Settings,
  Sparkles,
  X,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { useTheme } from "@/context/ThemeContext";
import { THEMES, type ThemeId } from "@/lib/themes";
import { cn } from "@/lib/utils";

type Command = {
  id: string;
  label: string;
  hint: string;
  icon: LucideIcon;
  active?: boolean;
  run: () => void;
};

export function WorkspaceCommandPalette({ compact = false }: { compact?: boolean }) {
  const { workspaceId = "" } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const { theme, setTheme } = useTheme();
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  const commands = useMemo<Command[]>(() => {
    const go = (path: string) => () => navigate(`/app/w/${workspaceId}/${path}`);
    const destinations = [
      ["overview", "Overview", "Workspace home", LayoutDashboard],
      ["chat", "Chat", "Start or continue a conversation", MessageSquare],
      ["agents", "Agents", "Run an agent mission", Bot],
      ["knowledge", "Knowledge", "Manage connected documents", FileText],
      ["github", "GitHub", "Open connected projects", Github],
      ["settings", "Settings", "Account and appearance", Settings],
    ] as const;
    return [
      ...destinations.map(([path, label, hint, icon]) => ({
        id: `go-${path}`,
        label,
        hint,
        icon,
        active: location.pathname.includes(`/${path}`),
        run: go(path),
      })),
      ...THEMES.map((item) => ({
        id: `theme-${item.id}`,
        label: `${item.label} theme`,
        hint: item.hint,
        icon: Palette,
        active: theme === item.id,
        run: () => setTheme(item.id as ThemeId),
      })),
    ];
  }, [location.pathname, navigate, setTheme, theme, workspaceId]);

  const filtered = commands.filter((command) =>
    `${command.label} ${command.hint}`.toLowerCase().includes(query.trim().toLowerCase()),
  );

  useEffect(() => {
    const onShortcut = (event: KeyboardEvent) => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setOpen((current) => !current);
      }
    };
    window.addEventListener("keydown", onShortcut);
    return () => window.removeEventListener("keydown", onShortcut);
  }, []);

  useEffect(() => {
    if (!open) return;
    setQuery("");
    setSelected(0);
    window.setTimeout(() => inputRef.current?.focus(), 0);
  }, [open]);

  function choose(command: Command | undefined) {
    if (!command) return;
    command.run();
    setOpen(false);
  }

  return (
    <>
      <button
        type="button"
        className={compact ? "flex h-9 w-9 items-center justify-center rounded-xl border border-white/10 bg-white/10 text-white" : "rail-link"}
        onClick={() => setOpen(true)}
        aria-label="Open quick switcher"
        title="Quick switcher (Ctrl+K)"
      >
        <Search size={compact ? 17 : 18} />
        {!compact && <span>Quick</span>}
      </button>
      {open && createPortal(
        <div className="fixed inset-0 z-[110] flex items-start justify-center bg-slate-950/55 px-3 pt-[max(10vh,env(safe-area-inset-top))] backdrop-blur-sm" role="presentation" onMouseDown={() => setOpen(false)}>
          <section className="w-full max-w-xl overflow-hidden rounded-3xl border border-white/20 bg-white text-slate-950 shadow-2xl" role="dialog" aria-modal="true" aria-label="Quick switcher" onMouseDown={(event) => event.stopPropagation()}>
            <div className="flex items-center gap-3 border-b border-slate-200 px-4">
              <Sparkles size={18} className="shrink-0 text-accent" />
              <input
                ref={inputRef}
                value={query}
                onChange={(event) => { setQuery(event.target.value); setSelected(0); }}
                onKeyDown={(event) => {
                  if (event.key === "Escape") setOpen(false);
                  if (event.key === "ArrowDown") { event.preventDefault(); setSelected((value) => Math.min(value + 1, filtered.length - 1)); }
                  if (event.key === "ArrowUp") { event.preventDefault(); setSelected((value) => Math.max(value - 1, 0)); }
                  if (event.key === "Enter") { event.preventDefault(); choose(filtered[selected]); }
                }}
                className="h-14 min-w-0 flex-1 bg-transparent text-sm outline-none placeholder:text-slate-400"
                placeholder="Go somewhere or change the theme..."
                aria-label="Search commands"
              />
              <button type="button" className="rounded-xl p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-700" onClick={() => setOpen(false)} aria-label="Close quick switcher"><X size={17} /></button>
            </div>
            <div className="max-h-[min(60vh,28rem)] overflow-y-auto p-2">
              {filtered.map((command, index) => {
                const Icon = command.icon;
                return (
                  <button
                    key={command.id}
                    type="button"
                    className={cn("flex w-full items-center gap-3 rounded-2xl px-3 py-2.5 text-left", selected === index ? "bg-accent/10" : "hover:bg-slate-50")}
                    onMouseEnter={() => setSelected(index)}
                    onClick={() => choose(command)}
                  >
                    <span className={cn("flex h-9 w-9 shrink-0 items-center justify-center rounded-xl", selected === index ? "bg-[var(--primary)] text-white" : "bg-slate-100 text-slate-600")}><Icon size={17} /></span>
                    <span className="min-w-0 flex-1"><span className="block text-sm font-semibold">{command.label}</span><span className="block truncate text-xs text-slate-500">{command.hint}</span></span>
                    {command.active && <Check size={16} className="text-accent" />}
                  </button>
                );
              })}
              {!filtered.length && <p className="px-4 py-10 text-center text-sm text-slate-500">No matching command.</p>}
            </div>
            <footer className="flex items-center justify-between border-t border-slate-100 px-4 py-2 text-[10px] text-slate-400"><span>↑↓ Navigate · Enter Select</span><kbd className="rounded-md border border-slate-200 bg-slate-50 px-1.5 py-0.5">Ctrl K</kbd></footer>
          </section>
        </div>,
        document.body,
      )}
    </>
  );
}
