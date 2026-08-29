const HTML_TAG = /<\/?[a-z][\s\S]*?>/i;
const MD_LINK = /\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g;
const BARE_URL = /\bhttps?:\/\/[^\s<>)"']+/g;

const SKIP_HOSTS = [
  "image.pollinations.ai",
  "gen.pollinations.ai",
  "pollinations.ai",
  "api.qrserver.com",
  "kroki.io",
];

function decodeEntities(text: string) {
  return text
    .replace(/&nbsp;/gi, " ")
    .replace(/&amp;/gi, "&")
    .replace(/&quot;/gi, '"')
    .replace(/&#39;/gi, "'")
    .replace(/&lt;/gi, "<")
    .replace(/&gt;/gi, ">");
}

export function htmlToMarkdown(input: string) {
  let text = decodeEntities(input);
  if (!HTML_TAG.test(text)) return text;
  text = text.replace(/<pre[^>]*>\s*<code[^>]*>([\s\S]*?)<\/code>\s*<\/pre>/gi, (_, code) => {
    return `\n\n\`\`\`\n${decodeEntities(code.replace(/<[^>]+>/g, ""))}\n\`\`\`\n\n`;
  });
  text = text.replace(/<code[^>]*>([\s\S]*?)<\/code>/gi, (_, code) => {
    return `\`${decodeEntities(code.replace(/<[^>]+>/g, ""))}\``;
  });
  text = text.replace(/<h([1-6])[^>]*>([\s\S]*?)<\/h\1>/gi, (_, level, inner) => {
    return `\n\n${"#".repeat(Number(level))} ${inner.replace(/<[^>]+>/g, "").trim()}\n\n`;
  });
  text = text.replace(/<a\s+[^>]*href=["']([^"']+)["'][^>]*>([\s\S]*?)<\/a>/gi, (_, href, label) => {
    return `[${label.replace(/<[^>]+>/g, "").trim() || href}](${href})`;
  });
  text = text.replace(/<li[^>]*>([\s\S]*?)<\/li>/gi, (_, inner) => `- ${inner.replace(/<[^>]+>/g, "").trim()}\n`);
  text = text.replace(/<\/?(ul|ol)[^>]*>/gi, "\n");
  text = text.replace(/<br\s*\/?>/gi, "\n");
  text = text.replace(/<\/p>/gi, "\n\n");
  text = text.replace(/<(p|div|span|section)[^>]*>/gi, "");
  text = text.replace(/<\/(div|span|section)>/gi, "\n");
  text = text.replace(/<\/?(strong|b)>/gi, "**");
  text = text.replace(/<\/?(em|i)>/gi, "*");
  text = text.replace(/<[^>]+>/g, "");
  return decodeEntities(text).replace(/\n{3,}/g, "\n\n").trim();
}

export type SourceLink = { title: string; url: string };

function hostname(url: string) {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return url;
  }
}

function shouldKeep(url: string) {
  const host = hostname(url);
  return !SKIP_HOSTS.some((skip) => host.includes(skip));
}

export function extractSources(text: string): SourceLink[] {
  const found: SourceLink[] = [];
  const seen = new Set<string>();

  function add(title: string, url: string) {
    const cleaned = url.replace(/[.,;]+$/, "");
    if (!cleaned.startsWith("http") || seen.has(cleaned) || !shouldKeep(cleaned)) return;
    seen.add(cleaned);
    found.push({ title: title.trim() || hostname(cleaned), url: cleaned });
  }

  let match: RegExpExecArray | null;
  const md = new RegExp(MD_LINK);
  while ((match = md.exec(text))) {
    add(match[1], match[2]);
  }

  let title = "Source";
  for (const line of text.split("\n")) {
    if (/^title:/i.test(line)) title = line.replace(/^title:\s*/i, "").trim() || "Source";
    if (/^url:/i.test(line)) add(title, line.replace(/^url:\s*/i, "").trim());
  }

  const bare = new RegExp(BARE_URL);
  while ((match = bare.exec(text))) {
    add(hostname(match[0]), match[0]);
  }

  return found;
}

export function splitProvenance(content: string) {
  const marker = "\n\n---\n";
  const idx = content.indexOf(marker);
  if (idx === -1) return { body: content, provenance: "" };
  return {
    body: content.slice(0, idx),
    provenance: content.slice(idx + marker.length),
  };
}
