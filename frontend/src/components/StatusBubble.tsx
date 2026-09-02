import { useEffect, useState } from "react";
import { Globe, Loader2 } from "lucide-react";

export function StatusBubble({
  active,
  steps,
}: {
  active: boolean;
  steps: string[];
}) {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    if (!active) {
      setIndex(0);
      return;
    }
    const id = window.setInterval(() => {
      setIndex((prev) => (prev + 1) % steps.length);
    }, 4500);
    return () => window.clearInterval(id);
  }, [active, steps.length]);

  if (!active) return null;

  return (
    <div className="shimmer-line flex max-w-3xl items-center gap-3 rounded-2xl border border-accent/20 bg-white/75 px-4 py-3 text-sm text-ink-800 shadow-sm backdrop-blur-xl">
      <span className="relative flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-accent to-violet-700 text-white shadow-glow">
        <Globe size={16} />
        <Loader2 size={28} className="absolute animate-spin text-accent/40" />
      </span>
      <div>
        <div className="font-medium">{steps[index]}</div>
        <div className="mt-0.5 flex items-center gap-1.5 text-xs text-ink-500"><span className="ai-live-dot" /> Suvyon is working</div>
      </div>
    </div>
  );
}
