import { PanelLeftOpen } from "lucide-react";
import { cn } from "@/lib/utils";

export function SidebarExpandTab({
  onClick,
  label,
}: {
  onClick: () => void;
  label: string;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      title={label}
      className={cn(
        "flex h-9 w-9 items-center justify-center rounded-xl border border-white/20",
        "bg-white/10 text-white hover:bg-indigo-600",
      )}
    >
      <PanelLeftOpen size={16} />
    </button>
  );
}
