export type User = {
  id: string;
  full_name: string;
  email: string;
  role: string;
  avatar_url: string | null;
  is_active: boolean;
  is_verified: boolean;
  is_superuser: boolean;
};

export type TokenResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string;
};

export type Workspace = {
  id: string;
  owner_id: string;
  name: string;
  description: string | null;
  is_active: boolean;
  is_archived: boolean;
  is_favourite: boolean;
};

export type Conversation = {
  id: string;
  workspace_id: string;
  title: string;
  provider: string | null;
  model: string | null;
  system_prompt: string | null;
  is_pinned: boolean;
  is_archived: boolean;
};

export type Message = {
  id: string;
  conversation_id: string;
  role: "user" | "assistant" | "system" | "tool";
  content: string;
  provider: string | null;
  model: string | null;
  prompt_tokens: number | null;
  completion_tokens: number | null;
  is_edited: boolean;
};

export type Agent = {
  id: string;
  workspace_id: string;
  name: string;
  description: string | null;
  instructions: string | null;
  provider: string | null;
  model: string | null;
  tools: string | null;
  is_active: boolean;
  is_public: boolean;
};

export type KnowledgeBase = {
  id: string;
  workspace_id: string;
  name: string;
  description: string | null;
  embedding_model: string;
  is_active: boolean;
};

export type Document = {
  id: string;
  workspace_id: string;
  name: string;
  mime_type: string;
  size_bytes: number;
  status: string;
  chunk_count: number | null;
  error_message: string | null;
};

export type ModelInfo = {
  provider: string;
  model_id: string;
  display_name: string;
  context_length: number;
  supports_streaming: boolean;
  cost_per_1k_input: number;
  cost_per_1k_output: number;
  capabilities: string[];
};

export type ChatHistoryItem = {
  role: string;
  content: string;
};
