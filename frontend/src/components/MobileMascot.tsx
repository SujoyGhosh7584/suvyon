import { cn } from "@/lib/utils";

export function MobileMascot({
  className,
}: {
  className?: string;
}) {
  return (
    <div
      className={cn("relative mx-auto flex h-28 w-28 items-center justify-center", className)}
      aria-hidden
    >
      <span className="absolute h-24 w-24 rounded-full bg-[var(--primary)]/40 blur-2xl animate-pulse" />
      <span className="absolute inset-1 rounded-full border border-white/15 [animation:spin-slow_12s_linear_infinite]">
        <span className="absolute left-2 top-3 h-2 w-2 rounded-full bg-cyan-300 shadow-[0_0_12px_#67e8f9]" />
        <span className="absolute bottom-2 right-5 h-1.5 w-1.5 rounded-full bg-rose-300 shadow-[0_0_12px_#fda4af]" />
      </span>
      <span className="glass-dark relative flex h-[4.8rem] w-[4.8rem] items-center justify-center rounded-[1.75rem]">
        <span className="brand-mark flex h-[3.65rem] w-[3.65rem] items-center justify-center rounded-[1.35rem] font-display text-2xl font-extrabold text-white">S</span>
      </span>
      <span className="absolute right-1 top-3 h-3 w-3 rounded-full bg-emerald-300 shadow-[0_0_18px_#6ee7b7] [animation:live-dot_2s_ease-in-out_infinite]" />
    </div>
  );
}
