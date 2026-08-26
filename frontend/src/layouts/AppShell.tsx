import { useState } from "react";
import { NavLink, Outlet, useLocation, useNavigate, useParams } from "react-router-dom";
import {
  Bot,
  FileText,
  LayoutDashboard,
  LogOut,
  MessageSquare,
  PanelLeftClose,
  PanelLeftOpen,
  Settings,
} from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/context/AuthContext";
import { workspacesApi } from "@/lib/services";
import { cn } from "@/lib/utils";

const links = [
  { to: "overview", label: "Overview", icon: LayoutDashboard },
  { to: "chat", label: "Chat", icon: MessageSquare },
  { to: "agents", label: "Agents", icon: Bot },
  { to: "knowledge", label: "Knowledge", icon: FileText },
  { to: "settings", label: "Settings", icon: Settings },
] as const;

const sectionThemes: Record<string, string> = {
  overview: "section-overview",
  chat: "section-chat",
  agents: "section-agents",
  knowledge: "section-knowledge",
  settings: "section-settings",
};

const navActive: Record<string, string> = {
  overview: "bg-sky-700 text-white",
  chat: "bg-violet-700 text-white",
  agents: "bg-teal-700 text-white",
  knowledge: "bg-amber-700 text-white",
  settings: "bg-slate-800 text-white",
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

  return (
    <div className="min-h-screen bg-mesh text-ink-950">
      <div className="mx-auto flex min-h-screen max-w-[1600px]">
        <aside
          className={cn(
            "sticky top-0 flex h-screen shrink-0 flex-col border-r border-ink-200/70 bg-white/55 px-3 py-5 backdrop-blur transition-all duration-300",
            isCollapsed ? "w-16" : "w-64",
          )}
        >
          <div className="mb-6 flex items-center justify-between px-1">
            <button
              type="button"
              onClick={() => navigate("/app")}
              className={cn("text-left overflow-hidden", isCollapsed && "w-0 hidden")}
            >
              <div className="font-display text-2xl font-extrabold tracking-tight">
                Suvyon
              </div>
              <div className="truncate text-xs text-ink-500">
                {workspace?.name || "Workspace"}
              </div>
            </button>
            {isCollapsed && (
              <button
                type="button"
                onClick={() => navigate("/app")}
                className="font-display text-xl font-extrabold text-brand-600 px-1"
                title="Suvyon"
              >
                S
              </button>
            )}
            <button
              type="button"
              onClick={() => setIsCollapsed((prev) => !prev)}
              className="rounded-lg p-1.5 text-ink-500 hover:bg-ink-100 hover:text-ink-900 transition"
              title={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
            >
              {isCollapsed ? <PanelLeftOpen size={18} /> : <PanelLeftClose size={18} />}
            </button>
          </div>

          <nav className="flex flex-1 flex-col gap-1">
            {links.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={`/app/w/${workspaceId}/${to}`}
                title={isCollapsed ? label : undefined}
                className={({ isActive }) =>
                  cn(
                    "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition",
                    isActive
                      ? navActive[to]
                      : "text-ink-700 hover:bg-ink-100",
                    isCollapsed && "justify-center px-0",
                  )
                }
              >
                <Icon size={18} />
                {!isCollapsed && <span>{label}</span>}
              </NavLink>
            ))}
          </nav>

          <div className="mt-4 border-t border-ink-200/80 pt-4">
            {!isCollapsed && (
              <div className="mb-3 truncate px-2 text-sm font-medium">
                {user?.full_name}
              </div>
            )}
            <button
              type="button"
              className={cn(
                "btn-ghost w-full justify-start",
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
            "min-w-0 flex-1 p-6 md:p-8",
            sectionThemes[currentSection],
          )}
        >
          <Outlet />
        </main>
      </div>
    </div>
  );
}

