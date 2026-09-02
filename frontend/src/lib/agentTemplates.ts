import { BookOpen, BrainCircuit, BriefcaseBusiness, CloudSun, Mail, Search, Sparkles } from "lucide-react";

export const AGENT_TEMPLATES = [
  {
    id: "blindspot",
    name: "Blindspot Agent",
    description: "Stress-test a plan, expose hidden assumptions, and design the cheapest proof before you commit.",
    instructions:
      "You are Suvyon Blindspot Agent. When the user shares a plan, decision, product idea, strategy, or important claim: (1) restate the intended outcome, (2) identify hidden assumptions and rank them by impact and uncertainty, (3) build a realistic pre-mortem describing how the plan could fail, (4) use web_search or read_page to test external claims and cite evidence, (5) use decision_canvas or calculator where useful, and (6) recommend the smallest reversible experiments that can validate the riskiest assumptions. Be constructive, specific, and never manufacture certainty. Finish with a decision checkpoint: proceed, revise, or pause, plus the evidence that would change that recommendation.",
    tools: ["web_search", "read_page", "decision_canvas", "calculator", "datetime"],
  },
  {
    id: "interview",
    name: "Interview Coach",
    description: "Research roles, practise questions, and improve answers with evidence.",
    instructions:
      "You are Suvyon Interview Coach. Help the user prepare from their target role and experience. Ask one focused interview question at a time, evaluate the answer constructively, provide an improved example, and track weak topics in the conversation. Use web_search for current company or role research and cite sources. Use calculator when a technical answer needs verification.",
    tools: ["web_search", "read_page", "calculator", "datetime"],
  },
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
      "You are an email assistant. Always call draft_email with to, subject, and body. Suvyon opens an editable approval card. Never call send_email and never claim a message was sent; only the approval dialog can authorize delivery.",
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
  blindspot: BrainCircuit,
  interview: BriefcaseBusiness,
  search: Search,
  email: Mail,
  studio: Sparkles,
  research: BookOpen,
  field: CloudSun,
} as const;

export const TOOL_DETAILS: Record<string, { name: string; description: string; category: string }> = {
  web_search: { name: "Live web search", description: "Current facts and sources", category: "Research" },
  wikipedia: { name: "Wikipedia", description: "Background summaries", category: "Research" },
  arxiv_search: { name: "Academic papers", description: "Find papers on arXiv", category: "Research" },
  read_page: { name: "Read a web page", description: "Extract content from a URL", category: "Research" },
  tech_pulse: { name: "Technology pulse", description: "Current technology discussions", category: "Research" },
  draft_email: { name: "Draft email", description: "Prepare an editable email", category: "Communication" },
  send_email: { name: "Send with approval", description: "Deliver only after your approval", category: "Communication" },
  generate_image: { name: "Generate image", description: "Create an image from a prompt", category: "Creative" },
  generate_storyboard: { name: "Create storyboard", description: "Build a visual shot sequence", category: "Creative" },
  generate_speech: { name: "Voiceover", description: "Prepare speech for playback", category: "Creative" },
  brand_kit: { name: "Brand kit", description: "Create a visual identity", category: "Creative" },
  qr_code: { name: "QR code", description: "Create a scannable code", category: "Creative" },
  draw_diagram: { name: "Diagram", description: "Render a flowchart or mind map", category: "Creative" },
  weather: { name: "Weather", description: "Live forecast for a place", category: "Utilities" },
  lookup_place: { name: "Place lookup", description: "Find an address and coordinates", category: "Utilities" },
  create_event: { name: "Calendar event", description: "Create a downloadable event", category: "Utilities" },
  decision_canvas: { name: "Decision canvas", description: "Compare options with criteria", category: "Utilities" },
  calculator: { name: "Calculator", description: "Verify calculations", category: "Utilities" },
  datetime: { name: "Date and time", description: "Use the current date and time", category: "Utilities" },
};
