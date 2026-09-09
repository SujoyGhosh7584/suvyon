import { NavLink, Outlet, useLocation, useNavigate, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Bot, ChevronDown, ChevronRight, FileText, Github, LayoutDashboard, LogOut, MessageSquare, Plus, Settings } from "lucide-react";
import { BrandOrb } from "@/components/AIBackdrop";
import { useAuth } from "@/context/AuthContext";
import { workspacesApi } from "@/lib/services";
import { cn } from "@/lib/utils";

const navigation = [
  { to: "overview", label: "Overview", icon: LayoutDashboard },
  { to: "chat", label: "Chat", icon: MessageSquare },
  { to: "agents", label: "Agents", icon: Bot },
  { to: "knowledge", label: "Knowledge", icon: FileText },
  { to: "github", label: "GitHub", icon: Github },
];

export function AppShell() {
  const { workspaceId } = useParams();
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const section = [...navigation, { to: "settings", label: "Settings" }].find((item) => location.pathname.includes(`/${item.to}`)) || navigation[0];
  const immersive = section.to === "chat" || section.to === "agents";
  const { data: workspace } = useQuery({ queryKey: ["workspace", workspaceId], queryFn: () => workspacesApi.get(workspaceId!), enabled: !!workspaceId });
  const initials = (user?.full_name || "S").split(" ").map((part) => part[0]).join("").slice(0, 2).toUpperCase();
  return <div className="workspace-frame">
    <a href="#workspace-content" className="skip-link">Skip to content</a>
    <aside className="workspace-rail">
      <button type="button" className="mb-7 mt-1" onClick={() => navigate("/app")} aria-label="Suvyon: all workspaces"><BrandOrb /></button>
      <nav aria-label="Workspace navigation" className="flex w-full flex-1 flex-col gap-1">
        {navigation.map(({ to, label, icon: Icon }) => <NavLink key={to} to={`/app/w/${workspaceId}/${to}`} title={label}
          className={({ isActive }) => cn("rail-link", isActive && "rail-link-active")}><Icon size={19} strokeWidth={1.8} /><span>{label}</span></NavLink>)}
      </nav>
      <NavLink to={`/app/w/${workspaceId}/settings`} className={({ isActive }) => cn("rail-link", isActive && "rail-link-active")}><Settings size={18} /><span>Settings</span></NavLink>
      <button type="button" className="rail-link" onClick={async () => { await logout(); navigate("/login"); }} aria-label="Sign out"><LogOut size={17} /><span>Sign out</span></button>
      <button type="button" className="profile-chip mt-3" onClick={() => navigate(`/app/w/${workspaceId}/settings`)} aria-label={`Account settings for ${user?.full_name || "you"}`}>{initials}</button>
    </aside>
    <section className="flex min-w-0 flex-1 flex-col overflow-hidden">
      <header className="workspace-toolbar">
        <div className="flex min-w-0 items-center gap-3">
          <button type="button" onClick={() => navigate("/app")} className="workspace-switch" title="Switch workspace"><span className="max-w-[200px] truncate">{workspace?.name || "Workspace"}</span><ChevronDown size={13} /></button>
          <ChevronRight size={12} className="text-slate-300" /><h1 className="text-sm font-semibold text-slate-900">{section.label}</h1>
        </div>
        <div className="flex items-center gap-3"><span className="hidden text-xs text-slate-400 lg:block">A space for your next big thing.</span><button type="button" className="btn-primary !py-2 !text-xs" onClick={() => navigate(`/app/w/${workspaceId}/chat`)}><Plus size={14} /> New chat</button></div>
      </header>
      <main id="workspace-content" className={cn("workspace-content", immersive && "workspace-content-immersive")}>
        <div key={section.to} className={cn("workspace-page page-enter", immersive && "workspace-page-immersive")}><Outlet /></div>
      </main>
    </section>
  </div>;
}
