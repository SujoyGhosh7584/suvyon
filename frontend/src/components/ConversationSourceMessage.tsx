type Source = { title: string; conversation_id: string; messages: { role: string; content: string }[] };

/** Keep a merge's full evidence available without filling the chat with raw JSON. */
export function ConversationSourceMessage({ content }: { content: string }) {
  const marker = "\n\nSource conversations (JSON):\n";
  const index = content.indexOf(marker);
  if (!content.startsWith("Merge focus: ") || index < 0) return <>{content}</>;
  let sources: Source[];
  try {
    sources = JSON.parse(content.slice(index + marker.length));
    if (!Array.isArray(sources) || !sources.every((source) =>
      source && typeof source.title === "string" && typeof source.conversation_id === "string" &&
      Array.isArray(source.messages) && source.messages.every((m) => m && typeof m.role === "string" && typeof m.content === "string")
    )) return <>{content}</>;
  } catch {
    return <>{content}</>;
  }
  return <div className="space-y-3">
    <p className="font-semibold">{content.slice(0, index)}</p>
    <details className="rounded-xl border border-current/20 p-3">
      <summary className="cursor-pointer text-xs">View {sources.length} source snapshots</summary>
      <div className="mt-3 max-h-80 space-y-4 overflow-y-auto">
        {sources.map((source, i) => <section key={i}>
          <h3 className="mb-2 font-semibold">{source.title}</h3>
          {source.messages.map((message, j) => <div key={j} className="mb-3 text-xs">
            <p className="mb-1 font-semibold capitalize opacity-70">{message.role}</p>
            <p className="whitespace-pre-wrap break-words">{message.content}</p>
          </div>)}
        </section>)}
      </div>
    </details>
  </div>;
}
