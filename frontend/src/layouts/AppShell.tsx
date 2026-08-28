import { useState } from "react";
import { NavLink, Outlet, useLocation, useNavigate, useParams } from "react-router-dom";
import {
  Bot,
  FileText,
  LayoutDashboard,
  LogOut,
  MessageSquare,
  PanelLeftClose,
  Settings,
} from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/context/AuthContext";
import { workspacesApi } from "@/lib/services";
import { SidebarExpandTab } from "@/components/SidebarExpandTab";
import { cn } from "@/lib/utils";

const links = [
  { to: "overview", label: "Overview", icon: LayoutDashboard, hint: "Home" },
  { to: "chat", label: "Chat", icon: MessageSquare, hint: "Talk" },
  { to: "agents", label: "Agents", icon: Bot, hint: "Tools" },
  { to: "knowledge", label: "Knowledge", icon: FileText, hint: "Docs" },
  { to: "settings", label: "Settings", icon: Settings, hint: "You" },
] as const;

const sectionThemes: Record<string, string> = {
  overview: "section-overview",
  chat: "section-chat",
  agents: "section-agents",
  knowledge: "section-knowledge",
  settings: "section-settings",
};

const navActive: Record<string, string> = {
  overview: "bg-indigo-500 text-white shadow-glow",
  chat: "bg-violet-500 text-white shadow-glow",
  agents: "bg-rose-500 text-white shadow-glow",
  knowledge: "bg-amber-500 text-ink-950",
  settings: "bg-slate-100 text-ink-950",
};

export function AppShell() {
  const { workspaceId } = useParams();
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [isCollapsed, setIsCollapsed] = useState(false);
  const currentSection =
    links.find((link) => location.pathname.includes(`/${link.to}`))?.to || "overview";

  const { data: workspace } = useQuery({
    queryKey: ["workspace", workspaceId],
    queryFn: () => workspacesApi.get(workspaceId!),
    enabled: !!workspaceId,
  });

  const initials = (user?.full_name || "S")
    .split(" ")
    .map((p) => p[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  return (
    <div className="min-h-screen bg-ink-950 text-white">
      <div className="relative mx-auto flex min-h-screen max-w-[1680px] gap-3 overflow-visible p-3">
        <aside
          className={cn(
            "sticky top-3 z-20 flex h-[calc(100vh-1.5rem)] shrink-0 flex-col rounded-stage border border-white/10 bg-ink-900/90 px-3 py-5 backdrop-blur-xl transition-all duration-300",
            isCollapsed ? "w-[4.5rem] overflow-visible" : "w-64",
          )}
        >
          {isCollapsed && (
            <div className="mb-3 flex justify-center">
              <SidebarExpandTab
                label="Expand sidebar"
                onClick={() => setIsCollapsed(false)}
              />
            </div>
          )}
          <div className={cn("mb-8 flex items-center px-1", isCollapsed ? "flex-col gap-3" : "justify-between")}>
            <button
              type="button"
              onClick={() => navigate("/app")}
              className={cn("text-left overflow-hidden", isCollapsed && "hidden")}
            >
              <div className="flex items-center gap-2">
                <span className="flex h-9 w-9 items-center justify-center rounded-2xl bg-indigo-500 font-display text-lg font-extrabold">
                  S
                </span>
                <span>
                  <div className="font-display text-lg font-extrabold tracking-tight">Suvyon</div>
                  <div className="truncate text-[11px] uppercase tracking-[0.18em] text-ink-400">
                    {workspace?.name || "Workspace"}
                  </div>
                </span>
              </div>
            </button>
            {isCollapsed && (
              <button
                type="button"
                onClick={() => navigate("/app")}
                className="flex h-9 w-9 items-center justify-center rounded-2xl bg-indigo-500 font-display text-lg font-extrabold"
                title="Suvyon"
              >
                S
              </button>
            )}
            {!isCollapsed && (
              <button
                type="button"
                className="rounded-xl p-1.5 text-ink-400 hover:bg-white/10 hover:text-white"
                title="Collapse sidebar"
                onClick={() => setIsCollapsed(true)}
              >
                <PanelLeftClose size={18} />
              </button>
            )}
          </div>

          <nav className="flex flex-1 flex-col gap-1.5">
            {links.map(({ to, label, icon: Icon, hint }) => (
              <NavLink
                key={to}
                to={`/app/w/${workspaceId}/${to}`}
                title={isCollapsed ? label : undefined}
                className={({ isActive }) =>
                  cn(
                    "flex items-center gap-3 rounded-2xl px-3 py-2.5 text-sm font-medium transition",
                    isActive ? navActive[to] : "text-ink-300 hover:bg-white/10 hover:text-white",
                    isCollapsed && "justify-center px-0",
                  )
                }
              >
                <Icon size={18} />
                {!isCollapsed && (
                  <span className="flex flex-1 items-center justify-between">
                    {label}
                    <span className="text-[10px] uppercase tracking-wider opacity-60">{hint}</span>
                  </span>
                )}
              </NavLink>
            ))}
          </nav>

          <div className="mt-4 border-t border-white/10 pt-4">
            {!isCollapsed && (
              <div className="mb-3 flex items-center gap-3 px-1">
                <div className="flex h-9 w-9 items-center justify-center rounded-full bg-indigo-500/30 text-xs font-bold text-indigo-100">
                  {initials}
                </div>
                <div className="min-w-0">
                  <div className="truncate text-sm font-medium">{user?.full_name}</div>
                  <div className="truncate text-[11px] text-ink-400">{user?.email}</div>
                </div>
              </div>
            )}
            <button
              type="button"
              className={cn(
                "flex w-full items-center gap-2 rounded-2xl px-3 py-2 text-sm text-ink-300 hover:bg-white/10 hover:text-white",
                isCollapsed && "justify-center px-0",
              )}
              title={isCollapsed ? "Sign out" : undefined}
              onClick={async () => {
                await logout();
                navigate("/login");
              }}
            >
              <LogOut size={16} />
              {!isCollapsed && <span>Sign out</span>}
            </button>
          </div>
        </aside>

        <main
          className={cn(
            "min-w-0 flex-1 overflow-hidden rounded-stage border border-white/10",
            sectionThemes[currentSection],
          )}
        >
          <div className="h-[calc(100vh-1.5rem)] overflow-auto p-5 md:p-7">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
