import { useState } from "react";
import { Check, ChevronDown, Database, X } from "lucide-react";
import type { KnowledgeBase } from "@/types/api";
import { cn } from "@/lib/utils";

type Props = { knowledgeBases: KnowledgeBase[]; value: string[] | null; onChange: (value: string[] | null) => void; compact?: boolean };

export function KnowledgeScopePicker({ knowledgeBases, value, onChange, compact = false }: Props) {
  const [open, setOpen] = useState(false);
  const active = knowledgeBases.filter((item) => item.is_active);
  const selected = value === null ? active.map((item) => item.id) : value;
  const label = value === null ? "All knowledge" : value.length === 0 ? "No knowledge" : value.length === 1 ? active.find((item) => item.id === value[0])?.name || "1 collection" : `${value.length} collections`;

  function toggle(id: string) {
    const current = value === null ? active.map((item) => item.id) : value;
    onChange(current.includes(id) ? current.filter((item) => item !== id) : [...current, id]);
  }

  return (
    <div className="relative shrink-0">
      <button type="button" className={cn("relative flex h-11 items-center justify-center gap-1.5 rounded-2xl border text-xs font-semibold transition", compact ? "w-11 px-0" : "max-w-[165px] px-3", value?.length === 0 ? "border-slate-200 bg-white text-slate-500" : "border-indigo-200 bg-indigo-50 text-indigo-800")} onClick={() => setOpen((current) => !current)} title={`Knowledge: ${label}`} aria-label={`Knowledge: ${label}`} aria-expanded={open}>
        <Database size={15} className="shrink-0" /><span className={compact ? "sr-only" : "truncate"}>{label}</span>{!compact && <ChevronDown size={13} className="shrink-0" />}
        {compact && <span className="absolute -right-1 -top-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-indigo-600 px-1 text-[8px] font-bold text-white ring-2 ring-white">{value === null ? "A" : value.length}</span>}
      </button>
      {open && (
        <div className="absolute bottom-full left-0 z-40 mb-2 w-72 rounded-2xl border border-slate-200 bg-white p-3 text-slate-900 shadow-2xl">
          <div className="mb-2 flex items-start justify-between gap-3">
            <div><p className="text-xs font-bold">Knowledge for this chat</p><p className="mt-0.5 text-[10px] leading-relaxed text-slate-500">Chat attachments remain private to this conversation.</p></div>
            <button type="button" className="rounded-lg p-1 text-slate-400 hover:bg-slate-100" onClick={() => setOpen(false)} aria-label="Close knowledge selection"><X size={14} /></button>
          </div>
          <div className="mb-2 grid grid-cols-2 gap-2">
            <button type="button" className={cn("rounded-xl border px-2 py-2 text-[11px] font-bold", value === null ? "border-indigo-300 bg-indigo-50 text-indigo-800" : "border-slate-200 text-slate-600")} onClick={() => onChange(null)}>All</button>
            <button type="button" className={cn("rounded-xl border px-2 py-2 text-[11px] font-bold", value?.length === 0 ? "border-indigo-300 bg-indigo-50 text-indigo-800" : "border-slate-200 text-slate-600")} onClick={() => onChange([])}>None</button>
          </div>
          <div className="max-h-52 space-y-1 overflow-y-auto">
            {active.map((item) => { const checked = selected.includes(item.id); return (
              <button key={item.id} type="button" className="flex w-full items-center gap-2 rounded-xl px-2 py-2 text-left text-xs hover:bg-slate-50" onClick={() => toggle(item.id)}>
                <span className={cn("flex h-4 w-4 shrink-0 items-center justify-center rounded border", checked ? "border-indigo-600 bg-indigo-600 text-white" : "border-slate-300 bg-white")}>{checked && <Check size={11} />}</span><span className="truncate font-medium">{item.name}</span>
              </button>
            ); })}
            {active.length === 0 && <p className="px-2 py-3 text-center text-[11px] text-slate-500">No active knowledge bases yet.</p>}
          </div>
        </div>
      )}
    </div>
  );
}
