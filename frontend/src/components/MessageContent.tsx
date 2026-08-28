import { useEffect, useMemo, useState } from "react";
import ReactMarkdown from "react-markdown";
import { Pause, Play, Volume2 } from "lucide-react";

const BLOCK_RE = /\[\[suvyon:(storyboard|speak)\]\]([\s\S]*?)\[\[\/suvyon:\1\]\]/g;

type StoryFrame = { url: string; shot?: string; caption?: string };
type Storyboard = { title?: string; frames: StoryFrame[] };

function markdownComponents() {
  return {
    img: ({ src, alt }: { src?: string; alt?: string }) => (
      <img
        src={src}
        alt={alt || ""}
        className="my-3 max-h-[28rem] w-full rounded-2xl object-cover ring-1 ring-ink-100"
      />
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

export function MessageContent({ content }: { content: string }) {
  const parts = useMemo(() => {
    const chunks: Array<
      | { type: "md"; text: string }
      | { type: "storyboard"; board: Storyboard }
      | { type: "speak"; text: string }
    > = [];
    let last = 0;
    const matches = content.matchAll(BLOCK_RE);
    for (const match of matches) {
      if (match.index == null) continue;
      if (match.index > last) {
        chunks.push({ type: "md", text: content.slice(last, match.index) });
      }
      if (match[1] === "storyboard") {
        try {
          const parsed = JSON.parse(match[2]) as Storyboard;
          if (parsed?.frames) chunks.push({ type: "storyboard", board: parsed });
        } catch {
          chunks.push({ type: "md", text: match[0] });
        }
      } else {
        chunks.push({ type: "speak", text: match[2].trim() });
      }
      last = match.index + match[0].length;
    }
    if (last < content.length) chunks.push({ type: "md", text: content.slice(last) });
    return chunks.length ? chunks : [{ type: "md" as const, text: content }];
  }, [content]);

  return (
    <div className="space-y-1 [&_a]:text-indigo-600 [&_p]:mb-2 [&_ul]:list-disc [&_ul]:pl-5">
      {parts.map((part, index) => {
        if (part.type === "storyboard") {
          return <StoryboardPlayer key={index} board={part.board} />;
        }
        if (part.type === "speak") {
          return <SpeakButton key={index} text={part.text} />;
        }
        if (!part.text.trim()) return null;
        return (
          <ReactMarkdown key={index} components={markdownComponents()}>
            {part.text}
          </ReactMarkdown>
        );
      })}
    </div>
  );
}
