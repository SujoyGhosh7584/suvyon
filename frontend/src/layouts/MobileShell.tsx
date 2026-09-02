import { NavLink, Outlet, useLocation, useNavigate, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Bot, ChevronDown, FileText, LayoutDashboard, MessageSquare, UserRound } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { AIBackdrop, BrandOrb } from "@/components/AIBackdrop";
import { useAuth } from "@/context/AuthContext";
import { workspacesApi } from "@/lib/services";
import { cn } from "@/lib/utils";

const links: Array<{ to: string; label: string; icon: LucideIcon; primary?: boolean }> = [
  { to: "overview", label: "Home", icon: LayoutDashboard },
  { to: "agents", label: "Agents", icon: Bot },
  { to: "chat", label: "Ask AI", icon: MessageSquare, primary: true },
  { to: "knowledge", label: "Knowledge", icon: FileText },
  { to: "settings", label: "You", icon: UserRound },
];

export function MobileShell() {
  const { workspaceId } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const currentSection = links.find((link) => location.pathname.includes(`/${link.to}`))?.to || "overview";
  const immersive = currentSection === "chat" || currentSection === "agents";

  const { data: workspace } = useQuery({
    queryKey: ["workspace", workspaceId],
    queryFn: () => workspacesApi.get(workspaceId!),
    enabled: Boolean(workspaceId),
  });

  const initials = (user?.full_name || "S").split(" ").map((part) => part[0]).join("").slice(0, 2).toUpperCase();

  return (
    <div className="mobile-app relative flex h-[100dvh] flex-col overflow-hidden bg-[#080a12] text-slate-950">
      <AIBackdrop />
      <header className="relative z-20 flex h-[68px] shrink-0 items-center justify-between px-4 pt-[env(safe-area-inset-top)] text-white">
        <button type="button" className="flex min-w-0 items-center gap-3" onClick={() => navigate("/app")}>
          <BrandOrb compact />
          <span className="min-w-0 text-left">
            <span className="block text-[10px] font-semibold uppercase tracking-[.18em] text-indigo-300">Suvyon workspace</span>
            <span className="flex items-center gap-1 truncate font-display text-sm font-bold">
              {workspace?.name || "Workspace"}<ChevronDown size={13} className="text-slate-400" />
            </span>
          </span>
        </button>
        <div className="flex items-center gap-2">
          <span className="flex items-center gap-1.5 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-2.5 py-1 text-[10px] font-semibold text-emerald-200">
            <span className="ai-live-dot" /> Ready
          </span>
          <button
            type="button"
            className="flex h-9 w-9 items-center justify-center rounded-xl border border-white/10 bg-white/10 text-xs font-bold"
            onClick={() => navigate(`/app/w/${workspaceId}/settings`)}
          >
            {initials}
          </button>
        </div>
      </header>

      <main className="relative z-10 min-h-0 flex-1 overflow-hidden rounded-t-[26px] bg-[#f7f8fc] pb-[78px] shadow-[0_-20px_70px_rgba(0,0,0,.25)]">
        <div className={cn("h-full", immersive ? "overflow-hidden" : "overflow-y-auto px-4 pb-5 pt-4")}>
          <Outlet />
        </div>
      </main>

      <nav className="absolute inset-x-3 bottom-[max(.6rem,env(safe-area-inset-bottom))] z-30 rounded-[22px] border border-slate-200/80 bg-white/90 px-2 py-1.5 shadow-[0_18px_60px_rgba(15,23,42,.22)] backdrop-blur-2xl">
        <div className="grid grid-cols-5 items-end">
          {links.map(({ to, label, icon: Icon, ...item }) => (
            <NavLink
              key={to}
              to={`/app/w/${workspaceId}/${to}`}
              className={({ isActive }) => cn("group flex flex-col items-center justify-end gap-1 text-[9px] font-bold", isActive ? "text-indigo-700" : "text-slate-500")}
            >
              {({ isActive }) => (
                <>
                  <span className={cn(
                    "flex items-center justify-center transition-all duration-300",
                    item.primary
                      ? "-mt-3 h-12 w-12 rounded-2xl bg-gradient-to-br from-indigo-600 to-violet-600 text-white shadow-[0_10px_24px_rgba(79,70,229,.34)]"
                      : "h-9 w-10 rounded-xl",
                    isActive && !item.primary && "bg-indigo-50 text-indigo-700",
                    isActive && item.primary && "-translate-y-1 scale-105",
                  )}>
                    <Icon size={item.primary ? 19 : 18} strokeWidth={isActive ? 2.5 : 2} />
                  </span>
                  <span>{label}</span>
                </>
              )}
            </NavLink>
          ))}
        </div>
      </nav>
    </div>
  );
}
