import { useEffect, useMemo, useState, type ReactNode } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Check, Copy, ExternalLink, Pause, Play, Volume2 } from "lucide-react";
import { extractSources, htmlToMarkdown, type SourceLink } from "@/lib/messageFormat";
import { cn } from "@/lib/utils";

const BLOCK_RE = /\[\[suvyon:(storyboard|speak|weather)\]\]([\s\S]*?)\[\[\/suvyon:\1\]\]/g;

type StoryFrame = { url: string; shot?: string; caption?: string };
type Storyboard = { title?: string; frames: StoryFrame[] };
type WeatherDay = { date: string; high: string | number; low: string | number; precip: string | number };
type WeatherPayload = {
  label: string;
  temperature?: string | number;
  wind?: string | number;
  days?: WeatherDay[];
};

function CodeBlock({ code, language }: { code: string; language?: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <div className="my-3 overflow-hidden rounded-2xl bg-ink-950 text-ink-50">
      <div className="flex items-center justify-between border-b border-white/10 px-3 py-1.5 text-[11px] uppercase tracking-wider text-ink-300">
        <span>{language || "code"}</span>
        <button
          type="button"
          className="inline-flex items-center gap-1 rounded-lg px-2 py-0.5 hover:bg-white/10"
          onClick={async () => {
            await navigator.clipboard.writeText(code);
            setCopied(true);
            window.setTimeout(() => setCopied(false), 1200);
          }}
        >
          {copied ? <Check size={12} /> : <Copy size={12} />}
          {copied ? "Copied" : "Copy"}
        </button>
      </div>
      <pre className="overflow-x-auto p-4 text-[13px] leading-relaxed">
        <code>{code}</code>
      </pre>
    </div>
  );
}

function markdownComponents() {
  return {
    img: ({ src, alt }: { src?: string; alt?: string }) => (
      <img
        src={src}
        alt={alt || ""}
        className="my-3 max-h-[28rem] w-full rounded-2xl object-cover ring-1 ring-ink-100"
      />
    ),
    a: ({ href, children }: { href?: string; children?: ReactNode }) => (
      <a
        href={href}
        target="_blank"
        rel="noreferrer"
        className="font-medium text-indigo-600 underline decoration-indigo-200 underline-offset-2 hover:text-indigo-800"
      >
        {children}
      </a>
    ),
    pre: ({ children }: { children?: ReactNode }) => <>{children}</>,
    code: ({ className, children }: { className?: string; children?: ReactNode }) => {
      const text = String(children ?? "").replace(/\n$/, "");
      const language = /language-([^\s]+)/.exec(className || "")?.[1];
      if (className?.includes("language-") || text.includes("\n")) {
        return <CodeBlock code={text} language={language} />;
      }
      return (
        <code className="rounded-md bg-ink-100 px-1.5 py-0.5 font-mono text-[12px] text-ink-800">
          {text}
        </code>
      );
    },
    table: ({ children }: { children?: ReactNode }) => (
      <div className="my-3 overflow-x-auto rounded-2xl ring-1 ring-ink-100">
        <table className="min-w-full text-left text-sm">{children}</table>
      </div>
    ),
    th: ({ children }: { children?: ReactNode }) => (
      <th className="bg-ink-50 px-3 py-2 font-semibold text-ink-700">{children}</th>
    ),
    td: ({ children }: { children?: ReactNode }) => (
      <td className="border-t border-ink-100 px-3 py-2">{children}</td>
    ),
    h1: ({ children }: { children?: ReactNode }) => (
      <h1 className="mb-2 mt-3 text-xl font-bold">{children}</h1>
    ),
    h2: ({ children }: { children?: ReactNode }) => (
      <h2 className="mb-2 mt-3 text-lg font-semibold">{children}</h2>
    ),
    h3: ({ children }: { children?: ReactNode }) => (
      <h3 className="mb-1.5 mt-3 text-base font-semibold">{children}</h3>
    ),
    ul: ({ children }: { children?: ReactNode }) => (
      <ul className="my-2 list-disc space-y-1 pl-5">{children}</ul>
    ),
    ol: ({ children }: { children?: ReactNode }) => (
      <ol className="my-2 list-decimal space-y-1 pl-5">{children}</ol>
    ),
    blockquote: ({ children }: { children?: ReactNode }) => (
      <blockquote className="my-3 border-l-4 border-indigo-300 bg-indigo-50/70 px-3 py-2 text-ink-700">
        {children}
      </blockquote>
    ),
  };
}

function StoryboardPlayer({ board }: { board: Storyboard }) {
  const frames = board.frames.filter((frame) => frame.url);
  const [index, setIndex] = useState(0);
  const [playing, setPlaying] = useState(true);

  useEffect(() => {
    if (!playing || frames.length < 2) return;
    const timer = window.setInterval(() => {
      setIndex((current) => (current + 1) % frames.length);
    }, 1400);
    return () => window.clearInterval(timer);
  }, [playing, frames.length]);

  if (!frames.length) return null;
  const frame = frames[index];

  return (
    <div className="my-3 overflow-hidden rounded-2xl bg-ink-950 text-white">
      <div className="relative">
        <img src={frame.url} alt={frame.shot || "Storyboard frame"} className="aspect-video w-full object-cover" />
        <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/70 to-transparent p-3 text-xs">
          {board.title && <div className="mb-1 font-semibold">{board.title}</div>}
          <div className="text-white/80">
            {frame.shot || `Shot ${index + 1}`} · {index + 1}/{frames.length}
          </div>
        </div>
      </div>
      <div className="flex items-center justify-between px-3 py-2 text-xs">
        <button type="button" className="inline-flex items-center gap-1" onClick={() => setPlaying((v) => !v)}>
          {playing ? <Pause size={14} /> : <Play size={14} />}
          {playing ? "Pause clip" : "Play clip"}
        </button>
        <span className="text-white/60">Free storyboard clip · not a paid video model</span>
      </div>
    </div>
  );
}

function SpeakButton({ text }: { text: string }) {
  const [speaking, setSpeaking] = useState(false);

  function toggle() {
    if (!("speechSynthesis" in window)) return;
    if (speaking) {
      window.speechSynthesis.cancel();
      setSpeaking(false);
      return;
    }
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.onend = () => setSpeaking(false);
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);
    setSpeaking(true);
  }

  return (
    <div className="my-3 rounded-2xl border border-ink-200 bg-ink-50 px-3 py-3">
      <button type="button" className="btn-outline" onClick={toggle}>
        <Volume2 size={16} />
        {speaking ? "Stop voiceover" : "Play voiceover"}
      </button>
      <p className="mt-2 text-sm text-ink-600">{text}</p>
    </div>
  );
}

function WeatherCard({ data }: { data: WeatherPayload }) {
  return (
    <div className="my-3 overflow-hidden rounded-2xl bg-gradient-to-br from-sky-500 to-indigo-600 p-4 text-white shadow-panel">
      <div className="text-xs uppercase tracking-[0.18em] text-white/80">Weather</div>
      <div className="mt-1 font-display text-2xl font-bold">{data.label}</div>
      <div className="mt-2 text-lg">
        {data.temperature != null ? `${data.temperature}°C` : "—"}
        {data.wind != null && (
          <span className="ml-2 text-sm text-white/80">wind {data.wind} km/h</span>
        )}
      </div>
      {!!data.days?.length && (
        <div className="mt-4 grid grid-cols-3 gap-2">
          {data.days.map((day) => (
            <div key={day.date} className="rounded-xl bg-white/15 px-2 py-2 text-center text-xs">
              <div className="font-semibold">{day.date.slice(5)}</div>
              <div className="mt-1 text-sm">
                {day.high}° / {day.low}°
              </div>
              <div className="text-white/75">{day.precip} mm</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function SourceList({ sources }: { sources: SourceLink[] }) {
  if (!sources.length) return null;
  return (
    <div className="mt-4 rounded-2xl border border-indigo-100 bg-white/80 p-3">
      <div className="mb-2 text-xs font-semibold uppercase tracking-[0.16em] text-ink-500">
        Sources · {sources.length}
      </div>
      <div className="flex flex-col gap-1.5">
        {sources.map((source) => (
          <a
            key={source.url}
            href={source.url}
            target="_blank"
            rel="noreferrer"
            className="group flex items-center gap-2 rounded-xl px-2 py-1.5 text-sm text-indigo-700 hover:bg-indigo-50"
          >
            <ExternalLink size={14} className="shrink-0 text-indigo-400 group-hover:text-indigo-600" />
            <span className="min-w-0 truncate font-medium">{source.title}</span>
            <span className="ml-auto hidden max-w-[40%] truncate text-[11px] text-ink-400 sm:block">
              {source.url.replace(/^https?:\/\//, "")}
            </span>
          </a>
        ))}
      </div>
    </div>
  );
}

export function MessageContent({ content }: { content: string }) {
  const prepared = useMemo(() => htmlToMarkdown(content), [content]);
  const sources = useMemo(() => extractSources(prepared), [prepared]);
  const parts = useMemo(() => {
    const chunks: Array<
      | { type: "md"; text: string }
      | { type: "storyboard"; board: Storyboard }
      | { type: "speak"; text: string }
      | { type: "weather"; data: WeatherPayload }
    > = [];
    let last = 0;
    for (const match of prepared.matchAll(BLOCK_RE)) {
      if (match.index == null) continue;
      if (match.index > last) chunks.push({ type: "md", text: prepared.slice(last, match.index) });
      if (match[1] === "storyboard") {
        try {
          const parsed = JSON.parse(match[2]) as Storyboard;
          if (parsed?.frames) chunks.push({ type: "storyboard", board: parsed });
        } catch {
          chunks.push({ type: "md", text: match[0] });
        }
      } else if (match[1] === "weather") {
        try {
          chunks.push({ type: "weather", data: JSON.parse(match[2]) as WeatherPayload });
        } catch {
          chunks.push({ type: "md", text: match[0] });
        }
      } else {
        chunks.push({ type: "speak", text: match[2].trim() });
      }
      last = match.index + match[0].length;
    }
    if (last < prepared.length) chunks.push({ type: "md", text: prepared.slice(last) });
    return chunks.length ? chunks : [{ type: "md" as const, text: prepared }];
  }, [prepared]);

  return (
    <div className={cn("space-y-1 text-sm leading-relaxed")}>
      {parts.map((part, index) => {
        if (part.type === "storyboard") return <StoryboardPlayer key={index} board={part.board} />;
        if (part.type === "speak") return <SpeakButton key={index} text={part.text} />;
        if (part.type === "weather") return <WeatherCard key={index} data={part.data} />;
        if (!part.text.trim()) return null;
        return (
          <ReactMarkdown key={index} remarkPlugins={[remarkGfm]} components={markdownComponents()}>
            {part.text}
          </ReactMarkdown>
        );
      })}
      <SourceList sources={sources} />
    </div>
  );
}
