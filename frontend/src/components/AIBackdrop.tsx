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
    <img src="/brand/suvyon-mark.svg" alt="" aria-hidden="true" className={cn("brand-mark shrink-0", compact ? "h-8 w-8" : "h-10 w-10")} />
  );
}
