import { BookOpen, CloudSun, Mail, Search, Sparkles } from "lucide-react";

export const AGENT_TEMPLATES = [
  {
    id: "search",
    name: "Search Agent",
    description: "Live web search for news, scores, and prices.",
    instructions:
      "You are a helpful assistant with web search capability. Always use web_search for current prices, news, scores, and live facts.",
    tools: ["web_search"],
  },
  {
    id: "email",
    name: "Email Agent",
    description: "Draft emails, then send only after you confirm.",
    instructions:
      "You are an email assistant. Draft, edit, and send messages for the user. Always call draft_email first with to, subject, and body. Show the draft and ask if they want changes. Call send_email only after they explicitly confirm (for example “send it”). Never claim an email was sent unless send_email reports success.",
    tools: ["draft_email", "send_email"],
  },
  {
    id: "studio",
    name: "Studio Agent",
    description: "Free images, storyboard clips, voiceover, brand kits, QR, and diagrams.",
    instructions:
      "You are Suvyon Studio. Create images with generate_image, videos/clips with generate_storyboard, voiceover with generate_speech, logos with brand_kit, QR codes with qr_code, and flowcharts with draw_diagram. Always keep [[suvyon:storyboard]] and [[suvyon:speak]] markers in your reply and include markdown images.",
    tools: [
      "generate_image",
      "generate_storyboard",
      "generate_speech",
      "brand_kit",
      "qr_code",
      "draw_diagram",
    ],
  },
  {
    id: "research",
    name: "Research Agent",
    description: "Wikipedia, arXiv, page reading, HN pulse, and web search.",
    instructions:
      "You are a research analyst. Use wikipedia and arxiv_search for grounded summaries, read_page for a specific URL, tech_pulse for live HN headlines, and web_search for current events. Cite sources.",
    tools: ["web_search", "wikipedia", "arxiv_search", "read_page", "tech_pulse"],
  },
  {
    id: "field",
    name: "Field Agent",
    description: "Weather, places, calendar files, and decision canvases.",
    instructions:
      "You help with real-world ops. Use weather and lookup_place for locations, create_event for calendar files, decision_canvas for tradeoffs, plus calculator and datetime when needed.",
    tools: ["weather", "lookup_place", "create_event", "decision_canvas", "calculator", "datetime"],
  },
] as const;

export const TEMPLATE_ICONS = {
  search: Search,
  email: Mail,
  studio: Sparkles,
  research: BookOpen,
  field: CloudSun,
} as const;
