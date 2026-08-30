import { NavLink, Outlet, useLocation, useNavigate, useParams } from "react-router-dom";
import { Bot, FileText, LayoutDashboard, MessageSquare, Sparkles } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/context/AuthContext";
import { workspacesApi } from "@/lib/services";
import { cn } from "@/lib/utils";

const links: Array<{
  to: string;
  label: string;
  icon: typeof LayoutDashboard;
  featured?: boolean;
}> = [
  { to: "overview", label: "Home", icon: LayoutDashboard },
  { to: "chat", label: "Chat", icon: MessageSquare, featured: true },
  { to: "agents", label: "Agents", icon: Bot },
  { to: "knowledge", label: "Docs", icon: FileText },
  { to: "settings", label: "You", icon: Sparkles },
];

const sectionThemes: Record<string, string> = {
  overview: "section-overview",
  chat: "section-chat",
  agents: "section-agents",
  knowledge: "section-knowledge",
  settings: "section-settings",
};

export function MobileShell() {
  const { workspaceId } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const currentSection =
    links.find((link) => location.pathname.includes(`/${link.to}`))?.to || "overview";
  const immersive = currentSection === "chat" || currentSection === "agents";

  const { data: workspace } = useQuery({
    queryKey: ["workspace", workspaceId],
    queryFn: () => workspacesApi.get(workspaceId!),
    enabled: !!workspaceId,
  });

  const firstName = (user?.full_name || "there").split(" ")[0];

  return (
    <div className="mobile-app flex h-[100dvh] flex-col bg-ink-950 text-ink-950">
      <header className="flex shrink-0 items-center justify-between gap-3 px-4 pb-2 pt-[max(0.75rem,env(safe-area-inset-top))] text-white">
        <button
          type="button"
          className="flex min-w-0 items-center gap-2.5 text-left"
          onClick={() => navigate("/app")}
        >
          <span className="brand-mark flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl font-display text-lg font-extrabold">
            S
          </span>
          <span className="min-w-0">
            <div className="truncate font-display text-base font-extrabold tracking-tight">
              {workspace?.name || "Suvyon"}
            </div>
            <div className="truncate text-[11px] text-ink-300">Hi, {firstName}</div>
          </span>
        </button>
        <button
          type="button"
          className="flex h-10 w-10 items-center justify-center rounded-full bg-white/10 text-xs font-bold"
          onClick={() => navigate(`/app/w/${workspaceId}/settings`)}
          title="You"
        >
          {(user?.full_name || "S")
            .split(" ")
            .map((p) => p[0])
            .join("")
            .slice(0, 2)
            .toUpperCase()}
        </button>
      </header>

      <main
        className={cn(
          "min-h-0 flex-1 text-ink-950",
          sectionThemes[currentSection],
          immersive ? "overflow-hidden" : "overflow-y-auto",
        )}
      >
        <div className={cn("h-full", immersive ? "overflow-hidden" : "px-4 pb-4 pt-2")}>
          <Outlet />
        </div>
      </main>

      <nav className="shrink-0 border-t border-white/10 bg-ink-900/95 px-2 pb-[max(0.5rem,env(safe-area-inset-bottom))] pt-2 backdrop-blur-xl">
        <div className="mx-auto flex max-w-md items-end justify-around">
          {links.map(({ to, label, icon: Icon, featured }) => (
            <NavLink
              key={to}
              to={`/app/w/${workspaceId}/${to}`}
              className={({ isActive }) =>
                cn(
                  "flex min-w-[3.4rem] flex-col items-center gap-0.5 px-1 text-[10px] font-semibold tracking-wide",
                  featured && "-mt-5",
                  isActive ? "text-white" : "text-ink-400",
                )
              }
            >
              {({ isActive }) => (
                <>
                  <span
                    className={cn(
                      "flex items-center justify-center transition",
                      featured
                        ? cn(
                            "h-14 w-14 rounded-[1.35rem] shadow-glow",
                            isActive ? "bg-[var(--primary)] text-white" : "bg-white/15 text-white",
                          )
                        : cn(
                            "h-9 w-9 rounded-2xl",
                            isActive && "bg-white/15",
                          ),
                    )}
                  >
                    <Icon size={featured ? 22 : 18} />
                  </span>
                  {label}
                </>
              )}
            </NavLink>
          ))}
        </div>
      </nav>
    </div>
  );
}
