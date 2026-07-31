import { NavLink, Outlet, useNavigate, useParams } from "react-router-dom";
import {
  Bot,
  FileText,
  LayoutDashboard,
  LogOut,
  MessageSquare,
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
];

export function AppShell() {
  const { workspaceId } = useParams();
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const { data: workspace } = useQuery({
    queryKey: ["workspace", workspaceId],
    queryFn: () => workspacesApi.get(workspaceId!),
    enabled: !!workspaceId,
  });

  return (
    <div className="min-h-screen bg-mesh text-ink-950">
      <div className="mx-auto flex min-h-screen max-w-[1600px]">
        <aside className="sticky top-0 flex h-screen w-64 shrink-0 flex-col border-r border-ink-200/70 bg-white/55 px-4 py-5 backdrop-blur">
          <button
            type="button"
            onClick={() => navigate("/app")}
            className="mb-8 text-left"
          >
            <div className="font-display text-2xl font-extrabold tracking-tight">Suvyon</div>
            <div className="mt-1 truncate text-xs text-ink-500">
              {workspace?.name || "Workspace"}
            </div>
          </button>

          <nav className="flex flex-1 flex-col gap-1">
            {links.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={`/app/w/${workspaceId}/${to}`}
                className={({ isActive }) =>
                  cn(
                    "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition",
                    isActive
                      ? "bg-ink-950 text-white"
                      : "text-ink-700 hover:bg-ink-100",
                  )
                }
              >
                <Icon size={18} />
                {label}
              </NavLink>
            ))}
          </nav>

          <div className="mt-4 border-t border-ink-200/80 pt-4">
            <div className="mb-3 truncate px-2 text-sm font-medium">{user?.full_name}</div>
            <button
              type="button"
              className="btn-ghost w-full justify-start"
              onClick={async () => {
                await logout();
                navigate("/login");
              }}
            >
              <LogOut size={16} />
              Sign out
            </button>
          </div>
        </aside>

        <main className="min-w-0 flex-1 p-6 md:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
