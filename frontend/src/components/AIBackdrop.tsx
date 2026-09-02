import { cn } from "@/lib/utils";

export function AIBackdrop({ className }: { className?: string }) {
  return (
    <div className={cn("ai-backdrop", className)} aria-hidden="true">
      <span className="ai-orb ai-orb-one" />
      <span className="ai-orb ai-orb-two" />
      <span className="ai-orb ai-orb-three" />
      <span className="ai-grid" />
      <span className="ai-node ai-node-one" />
      <span className="ai-node ai-node-two" />
      <span className="ai-node ai-node-three" />
    </div>
  );
}

export function BrandOrb({ compact = false }: { compact?: boolean }) {
  return (
    <span className={cn("brand-orb", compact ? "h-9 w-9" : "h-11 w-11")} aria-hidden="true">
      <span className="brand-orb-ring" />
      <span className="brand-orb-core">S</span>
      <span className="brand-orb-pulse" />
    </span>
  );
}
