import { NavLink, Outlet, useLocation, useNavigate, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  Bot,
  ChevronDown,
  FileText,
  LayoutDashboard,
  LogOut,
  MessageSquare,
  Settings,
  Sparkles,
} from "lucide-react";
import { AIBackdrop, BrandOrb } from "@/components/AIBackdrop";
import { ThemePicker } from "@/components/ThemePicker";
import { useAuth } from "@/context/AuthContext";
import { workspacesApi } from "@/lib/services";
import { cn } from "@/lib/utils";

const navigation = [
  { to: "overview", label: "Home", icon: LayoutDashboard },
  { to: "chat", label: "Chat", icon: MessageSquare },
  { to: "agents", label: "Agents", icon: Bot },
  { to: "knowledge", label: "Knowledge", icon: FileText },
] as const;

const sectionCopy: Record<string, { eyebrow: string; title: string }> = {
  overview: { eyebrow: "Workspace", title: "Command center" },
  chat: { eyebrow: "Intelligence", title: "AI conversation" },
  agents: { eyebrow: "Automation", title: "Agent missions" },
  knowledge: { eyebrow: "Sources", title: "Knowledge library" },
  settings: { eyebrow: "Account", title: "Settings & security" },
};

export function AppShell() {
  const { workspaceId } = useParams();
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const currentSection =
    [...navigation, { to: "settings" as const }].find((item) =>
      location.pathname.includes(`/${item.to}`),
    )?.to || "overview";
  const current = sectionCopy[currentSection];

  const { data: workspace } = useQuery({
    queryKey: ["workspace", workspaceId],
    queryFn: () => workspacesApi.get(workspaceId!),
    enabled: Boolean(workspaceId),
  });

  const initials = (user?.full_name || "S")
    .split(" ")
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  return (
    <div className="relative h-screen overflow-hidden bg-[#080a12] text-slate-950">
      <AIBackdrop />
      <div className="relative z-10 flex h-full p-2.5">
        <aside className="flex w-[88px] shrink-0 flex-col items-center rounded-[24px] border border-white/10 bg-[#0d101b]/90 px-2 py-4 text-white shadow-2xl backdrop-blur-2xl">
          <button type="button" onClick={() => navigate("/app")} aria-label="All workspaces">
            <BrandOrb />
          </button>

          <nav className="mt-8 flex w-full flex-1 flex-col gap-2">
            {navigation.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={`/app/w/${workspaceId}/${to}`}
                className={({ isActive }) =>
                  cn(
                    "group relative flex h-[58px] w-full flex-col items-center justify-center gap-1 rounded-2xl text-[10px] font-semibold transition-all duration-300",
                    isActive
                      ? "bg-white text-slate-950 shadow-[0_12px_30px_rgba(0,0,0,.3)]"
                      : "text-slate-400 hover:bg-white/10 hover:text-white",
                  )
                }
              >
                {({ isActive }) => (
                  <>
                    <Icon size={19} strokeWidth={isActive ? 2.4 : 1.8} className="transition-transform group-hover:scale-110" />
                    <span>{label}</span>
                    {isActive && <span className="absolute -right-2 h-5 w-1 rounded-l-full bg-indigo-500" />}
                  </>
                )}
              </NavLink>
            ))}
          </nav>

          <div className="flex w-full flex-col items-center gap-2 border-t border-white/10 pt-3">
            <NavLink
              to={`/app/w/${workspaceId}/settings`}
              className={({ isActive }) =>
                cn(
                  "flex h-10 w-10 items-center justify-center rounded-xl transition",
                  isActive ? "bg-white text-slate-950" : "text-slate-400 hover:bg-white/10 hover:text-white",
                )
              }
              aria-label="Settings"
            >
              <Settings size={18} />
            </NavLink>
            <button
              type="button"
              className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 text-xs font-bold text-white shadow-lg"
              onClick={() => navigate(`/app/w/${workspaceId}/settings`)}
              title={user?.full_name || "Profile"}
            >
              {initials}
            </button>
          </div>
        </aside>

        <section className="ml-2.5 flex min-w-0 flex-1 flex-col overflow-hidden rounded-[26px] border border-white/15 bg-[#f7f8fc] shadow-2xl">
          <header className="flex h-[76px] shrink-0 items-center justify-between border-b border-slate-200/80 bg-white/90 px-6 backdrop-blur-xl">
            <div className="min-w-0">
              <p className="text-[10px] font-bold uppercase tracking-[.22em] text-indigo-600">{current.eyebrow}</p>
              <h1 className="truncate font-display text-xl font-bold tracking-tight text-slate-950">{current.title}</h1>
            </div>

            <div className="flex items-center gap-3">
              <div className="hidden items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-xs font-semibold text-emerald-800 lg:flex">
                <span className="ai-live-dot" /> AI systems ready
              </div>
              <button
                type="button"
                onClick={() => navigate("/app")}
                className="flex max-w-[260px] items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-left transition hover:border-slate-300 hover:bg-white"
              >
                <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-slate-950 text-white"><Sparkles size={15} /></span>
                <span className="hidden min-w-0 sm:block">
                  <span className="block text-[10px] font-semibold uppercase tracking-wider text-slate-500">Active workspace</span>
                  <span className="block truncate text-sm font-semibold text-slate-900">{workspace?.name || "Workspace"}</span>
                </span>
                <ChevronDown className="hidden text-slate-400 sm:block" size={15} />
              </button>
              <div className="hidden xl:block"><ThemePicker compact /></div>
              <button
                type="button"
                className="flex h-10 w-10 items-center justify-center rounded-xl border border-slate-200 bg-white text-slate-500 transition hover:bg-slate-50 hover:text-rose-600"
                onClick={async () => {
                  await logout();
                  navigate("/login");
                }}
                aria-label="Sign out"
              >
                <LogOut size={17} />
              </button>
            </div>
          </header>

          <main className="app-canvas min-h-0 flex-1 overflow-auto">
            <div key={currentSection} className="page-enter min-h-full p-4 md:p-6 xl:p-7">
              <Outlet />
            </div>
          </main>
        </section>
      </div>
    </div>
  );
}
