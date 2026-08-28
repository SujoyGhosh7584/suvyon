import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import type { ReactNode } from "react";

export function GuestLink({
  to,
  className,
  children,
}: {
  to: string;
  className?: string;
  children: ReactNode;
}) {
  const { user, logout, loading } = useAuth();
  const navigate = useNavigate();

  return (
    <Link
      to={to}
      className={className}
      onClick={async (event) => {
        if (loading) {
          event.preventDefault();
          return;
        }
        if (!user) return;
        event.preventDefault();
        await logout();
        navigate(to);
      }}
    >
      {children}
    </Link>
  );
}

export function SignedInNotice({ intent }: { intent: "login" | "register" }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  if (!user) return null;

  return (
    <div className="mb-5 rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-ink-800">
      This browser is already signed in as <strong>{user.full_name}</strong> ({user.email}).
      That is why workspaces from that account appeared without a new login.
      <div className="mt-3 flex flex-wrap gap-2">
        <button type="button" className="btn-primary" onClick={() => navigate("/app")}>
          Continue as {user.full_name.split(" ")[0]}
        </button>
        <button
          type="button"
          className="btn-outline"
          onClick={async () => {
            await logout();
          }}
        >
          {intent === "register" ? "Sign out and create a new account" : "Use a different account"}
        </button>
      </div>
    </div>
  );
}
