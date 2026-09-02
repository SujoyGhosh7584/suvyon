import { api } from "@/lib/api";
import type {
  Agent,
  Conversation,
  Document,
  KnowledgeBase,
  Message,
  ModelInfo,
  TokenResponse,
  User,
  Workspace,
  ChatHistoryItem,
  AgentRunResponse,
  PendingEmailDraft,
} from "@/types/api";

export const authApi = {
  register: (payload: { full_name: string; email: string; password: string }) =>
    api.post<User>("/auth/register", payload).then((r) => r.data),
  login: async (email: string, password: string) => {
    const body = new URLSearchParams();
    body.set("username", email);
    body.set("password", password);
    const { data } = await api.post<TokenResponse>("/auth/login", body, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
    return data;
  },
  logout: () => api.post("/auth/logout"),
  changePassword: (current_password: string, new_password: string) =>
    api.post("/auth/change-password", { current_password, new_password }),
  verifyEmail: (email: string, code: string) =>
    api.post<User>("/auth/verify-email", { email, code }).then((r) => r.data),
  resendVerification: (email: string) =>
    api.post<{ message: string }>("/auth/resend-verification", { email }).then((r) => r.data),
  forgotPassword: (email: string) =>
    api.post<{ message: string }>("/auth/forgot-password", { email }).then((r) => r.data),
  resetPassword: (email: string, code: string, new_password: string) =>
    api.post("/auth/reset-password", { email, code, new_password }),
};

export const usersApi = {
  me: () => api.get<User>("/users/me").then((r) => r.data),
  updateMe: (payload: { full_name?: string; avatar_url?: string }) =>
    api.patch<User>("/users/me", payload).then((r) => r.data),
};

export const workspacesApi = {
  list: () => api.get<Workspace[]>("/workspaces").then((r) => r.data),
  get: (id: string) => api.get<Workspace>(`/workspaces/${id}`).then((r) => r.data),
  create: (payload: { name: string; description?: string }) =>
    api.post<Workspace>("/workspaces", payload).then((r) => r.data),
  update: (id: string, payload: { name?: string; description?: string }) =>
    api.patch<Workspace>(`/workspaces/${id}`, payload).then((r) => r.data),
  remove: (id: string) => api.delete(`/workspaces/${id}`),
  archive: (id: string) =>
    api.post<Workspace>(`/workspaces/${id}/archive`).then((r) => r.data),
  restore: (id: string) =>
    api.post<Workspace>(`/workspaces/${id}/restore`).then((r) => r.data),
  favourite: (id: string) =>
    api.post<Workspace>(`/workspaces/${id}/favourite`).then((r) => r.data),
  unfavourite: (id: string) =>
    api.delete<Workspace>(`/workspaces/${id}/favourite`).then((r) => r.data),
};

export const conversationsApi = {
  list: (workspaceId: string) =>
    api
      .get<Conversation[]>(`/workspaces/${workspaceId}/conversations`)
      .then((r) => r.data),
  create: (
    workspaceId: string,
    payload: {
      title: string;
      provider?: string | null;
      model?: string | null;
      system_prompt?: string | null;
    },
  ) =>
    api
      .post<Conversation>(`/workspaces/${workspaceId}/conversations`, payload)
      .then((r) => r.data),
  get: (workspaceId: string, conversationId: string) =>
    api
      .get<Conversation>(`/workspaces/${workspaceId}/conversations/${conversationId}`)
      .then((r) => r.data),
  update: (
    workspaceId: string,
    conversationId: string,
    payload: Partial<Conversation>,
  ) =>
    api
      .patch<Conversation>(
        `/workspaces/${workspaceId}/conversations/${conversationId}`,
        payload,
      )
      .then((r) => r.data),
  remove: (workspaceId: string, conversationId: string) =>
    api.delete(`/workspaces/${workspaceId}/conversations/${conversationId}`),
  messages: (workspaceId: string, conversationId: string) =>
    api
      .get<Message[]>(
        `/workspaces/${workspaceId}/conversations/${conversationId}/messages`,
      )
      .then((r) => r.data),
  documents: (workspaceId: string, conversationId: string) =>
    api
      .get<Document[]>(
        `/workspaces/${workspaceId}/conversations/${conversationId}/documents`,
      )
      .then((r) => r.data),
  uploadDocument: (workspaceId: string, conversationId: string, file: File) => {
    const form = new FormData();
    form.append("file", file);
    return api
      .post<Document>(
        `/workspaces/${workspaceId}/conversations/${conversationId}/documents`,
        form,
      )
      .then((r) => r.data);
  },
  sendMessage: (
    workspaceId: string,
    conversationId: string,
    payload: {
      content: string;
      provider?: string | null;
      model?: string | null;
      knowledge_base_id?: string | null;
      knowledge_base_ids?: string[] | null;
      mode?: string | null;
    },
  ) =>
    api
      .post<Message>(
        `/workspaces/${workspaceId}/conversations/${conversationId}/messages`,
        payload,
      )
      .then((r) => r.data),
};

export const agentsApi = {
  list: (workspaceId: string) =>
    api.get<Agent[]>(`/workspaces/${workspaceId}/agents`).then((r) => r.data),
  tools: (workspaceId: string) =>
    api.get<string[]>(`/workspaces/${workspaceId}/agents/tools`).then((r) => r.data),
  get: (workspaceId: string, agentId: string) =>
    api
      .get<Agent>(`/workspaces/${workspaceId}/agents/${agentId}`)
      .then((r) => r.data),
  create: (
    workspaceId: string,
    payload: {
      name: string;
      description?: string | null;
      instructions?: string | null;
      provider?: string | null;
      model?: string | null;
      tools?: string | null;
      is_public?: boolean;
    },
  ) =>
    api
      .post<Agent>(`/workspaces/${workspaceId}/agents`, payload)
      .then((r) => r.data),
  update: (
    workspaceId: string,
    agentId: string,
    payload: Partial<{
      name: string;
      description: string | null;
      instructions: string | null;
      provider: string | null;
      model: string | null;
      tools: string | null;
      is_active: boolean;
      is_public: boolean;
    }>,
  ) =>
    api
      .patch<Agent>(`/workspaces/${workspaceId}/agents/${agentId}`, payload)
      .then((r) => r.data),
  remove: (workspaceId: string, agentId: string) =>
    api.delete(`/workspaces/${workspaceId}/agents/${agentId}`),
  run: (
    workspaceId: string,
    agentId: string,
    payload: { content: string; history?: ChatHistoryItem[] | null },
  ) =>
    api
      .post<AgentRunResponse>(
        `/workspaces/${workspaceId}/agents/${agentId}/run`,
        payload,
      )
      .then((r) => r.data),
  sendEmail: (
    workspaceId: string,
    agentId: string,
    payload: PendingEmailDraft,
  ) =>
    api
      .post<{ message: string }>(
        `/workspaces/${workspaceId}/agents/${agentId}/email/send`,
        { ...payload, confirmed: true },
      )
      .then((r) => r.data),
};

export const knowledgeApi = {
  list: (workspaceId: string) =>
    api
      .get<KnowledgeBase[]>(`/workspaces/${workspaceId}/knowledge-bases`)
      .then((r) => r.data),
  create: (
    workspaceId: string,
    payload: { name: string; description?: string; embedding_model?: string },
  ) =>
    api
      .post<KnowledgeBase>(`/workspaces/${workspaceId}/knowledge-bases`, payload)
      .then((r) => r.data),
  update: (
    workspaceId: string,
    kbId: string,
    payload: { name?: string; description?: string; is_active?: boolean },
  ) =>
    api
      .patch<KnowledgeBase>(
        `/workspaces/${workspaceId}/knowledge-bases/${kbId}`,
        payload,
      )
      .then((r) => r.data),
  remove: (workspaceId: string, kbId: string) =>
    api.delete(`/workspaces/${workspaceId}/knowledge-bases/${kbId}`),
};

export const documentsApi = {
  list: (workspaceId: string) =>
    api
      .get<Document[]>(`/workspaces/${workspaceId}/documents`)
      .then((r) => r.data),
  upload: (workspaceId: string, knowledgeBaseId: string, file: File) => {
    const form = new FormData();
    form.append("knowledge_base_id", knowledgeBaseId);
    form.append("file", file);
    return api
      .post<Document>(`/workspaces/${workspaceId}/documents`, form)
      .then((r) => r.data);
  },
  remove: (workspaceId: string, documentId: string) =>
    api.delete(`/workspaces/${workspaceId}/documents/${documentId}`),
};

export const modelsApi = {
  list: () => api.get<ModelInfo[]>("/models").then((r) => r.data),
};
