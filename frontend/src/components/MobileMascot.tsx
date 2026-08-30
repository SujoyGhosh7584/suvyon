import { cn } from "@/lib/utils";

export function MobileMascot({
  className,
}: {
  className?: string;
}) {
  return (
    <div
      className={cn("relative mx-auto flex h-24 w-24 items-center justify-center", className)}
      aria-hidden
    >
      <span className="absolute h-24 w-24 rounded-full bg-[var(--primary)]/30 blur-2xl" />
      <span className="relative flex h-[4.5rem] w-[4.5rem] items-center justify-center rounded-[1.75rem] bg-[var(--primary)] shadow-glow">
        <span className="font-display text-3xl font-extrabold text-white">S</span>
      </span>
      <span className="absolute right-1 top-2 text-lg">✨</span>
    </div>
  );
}
