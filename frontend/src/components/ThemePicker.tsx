import { THEMES } from "@/lib/themes";
import { useTheme } from "@/context/ThemeContext";
import { cn } from "@/lib/utils";

export function ThemePicker({ compact = false }: { compact?: boolean }) {
  const { theme, setTheme } = useTheme();

  return (
    <div className={cn("grid gap-2", compact ? "grid-cols-5" : "grid-cols-1 sm:grid-cols-5")}>
      {THEMES.map((item) => (
        <button
          key={item.id}
          type="button"
          title={item.label}
          onClick={() => setTheme(item.id)}
          className={cn(
            "overflow-hidden rounded-2xl border text-left text-ink-900 transition",
            theme === item.id
              ? "border-accent ring-2 ring-accent/40"
              : compact
                ? "border-white/15 hover:border-white/40"
                : "border-ink-200 hover:border-ink-400",
            compact ? "h-8" : "p-3",
          )}
        >
          <span
            className={cn(
              "theme-swatch block rounded-xl",
              `theme-swatch-${item.id}`,
              compact ? "h-full w-full" : "mb-2 h-10",
            )}
          />
          {!compact && (
            <>
              <div className="text-sm font-semibold">{item.label}</div>
              <div className="text-[11px] text-ink-500">{item.hint}</div>
            </>
          )}
        </button>
      ))}
    </div>
  );
}
