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
    <div className="flex max-w-3xl items-center gap-3 rounded-2xl border border-accent/20 bg-accent-muted/60 px-4 py-3 text-sm text-ink-800">
      <span className="relative flex h-8 w-8 items-center justify-center rounded-full bg-white text-accent">
        <Globe size={16} />
        <Loader2 size={28} className="absolute animate-spin text-accent/40" />
      </span>
      <div>
        <div className="font-medium">{steps[index]}</div>
        <div className="text-xs text-ink-500">This can take a little while for live search.</div>
      </div>
    </div>
  );
}
