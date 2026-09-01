const src = (label, path, line, note = "") => ({ label, path, line, note });

window.SUVYON_GUIDE = {
  finalQuestions: [
    "Explain what happens before FastAPI accepts its first request.",
    "Trace a browser chat request through route, service, model router, provider, and persistence.",
    "Show exactly where workspace ownership is checked and why prompt instructions are not authorization.",
    "Trace document upload, parsing, chunking, embedding, pgvector storage, retrieval, and prompt assembly.",
    "Explain the difference between explicit RAG mode and Auto mode's search_knowledge tool.",
    "Trace one agent tool call and prove that the LLM does not execute Python functions itself.",
    "Explain model selection and failover without claiming dynamic health or cost-based routing.",
    "Explain how SSE streaming changes persistence, cancellation, and provider-failover decisions.",
    "Draw the database ownership tree from User down to Message and DocumentChunk.",
    "Name three implemented safeguards, three current limitations, and three measured next improvements."
  ],
  topics: [
    {
      id: "orientation",
      group: "Start here",
      title: "What Suvyon is—and is not",
      status: "implemented",
      summary: "Build the correct mental model before reading functions. Suvyon is an application-owned AI workspace, not a model and not a multi-agent framework.",
      mentalModel: "Think of Suvyon as an airport. The React UI is the passenger entrance, FastAPI is security and check-in, services coordinate the journey, PostgreSQL remembers the trip, and the router selects an external LLM airline.",
      explanation: [
        "Suvyon combines four user capabilities: provider-independent chat, answers grounded in uploaded documents, live external tools, and saved agent configurations. The application owns users, workspaces, conversations, messages, documents, and agent settings.",
        "The LLM is an external reasoning and generation dependency. It does not own the conversation database, execute tools, or decide authorization. Python code builds the context, validates identity, calls the provider, executes selected tools, and stores results.",
        "The current runtime is a modular monolith: one React frontend, one FastAPI backend, and one PostgreSQL database with pgvector. Groq, Gemini, OpenRouter, search, email, and media services sit outside the core application."
      ],
      bullets: [
        "Implemented: multi-provider chat, JWT authentication, workspaces, RAG, saved agents, tools, streaming, OTP email verification.",
        "Not implemented as claimed architecture: dynamic health/cost model scoring, durable job queue, long-term agent memory, multi-agent orchestration, formal eval platform.",
        "Aspirational architecture documents describe desired behavior; current source code is the interview source of truth."
      ],
      flow: {
        note: "This is the shortest correct end-to-end story.",
        steps: [
          { label: "01 INPUT", title: "User action", copy: "A person logs in, selects a workspace, uploads a file, chats, or runs an agent.", sources: [src("Frontend routes", "frontend/src/App.tsx", 26)] },
          { label: "02 TRANSPORT", title: "React calls API", copy: "Axios sends JSON or multipart data with a bearer token to /api/v1.", sources: [src("API client", "frontend/src/lib/api.ts", 3), src("Endpoint wrappers", "frontend/src/lib/services.ts", 15)] },
          { label: "03 CONTROL", title: "FastAPI handles", copy: "A route authenticates, checks workspace ownership, validates a schema, and calls a service.", sources: [src("API router", "backend/app/api/v1/router.py", 14), src("Current user", "backend/app/api/security.py", 16)] },
          { label: "04 WORK", title: "Service orchestrates", copy: "Business logic reads or writes the database and optionally invokes RAG, tools, or an LLM.", sources: [src("Dependency wiring", "backend/app/api/dependencies.py", 96)] },
          { label: "05 OUTPUT", title: "Response returns", copy: "JSON or SSE reaches React, which updates the screen and query cache.", sources: [src("Chat page", "frontend/src/pages/ChatPage.tsx", 105)] }
        ]
      },
      speak: "Suvyon is a multi-provider AI workspace. React provides the user experience; FastAPI owns authentication and orchestration; PostgreSQL and pgvector own application and retrieval state; provider adapters call external LLMs; and a bounded Python loop executes tools. The key boundary is that the model proposes text or tool calls, while the application enforces permissions, performs side effects, and persists truth.",
      questions: [
        "Why is Suvyon an AI application rather than an LLM?",
        "Which state belongs to Suvyon and which capability comes from providers?",
        "Is Suvyon multi-agent today? Prove your answer from code."
      ],
      truths: [
        { status: "implemented", text: "Multiple saved agent configurations can be created per workspace." },
        { status: "partial", text: "One selected agent runs at a time through a custom bounded loop." },
        { status: "planned", text: "No supervisor/worker multi-agent graph or durable checkpoint engine exists today." }
      ]
    },
    {
      id: "boot",
      group: "Entry points",
      title: "How the application starts",
      status: "implemented",
      summary: "There are two entry points: Vite mounts React in the browser, while Uvicorn imports the FastAPI app in Python.",
      mentalModel: "The frontend boot builds the screen and context providers. The backend boot assembles the API, middleware, exception handling, and routes before serving requests.",
      explanation: [
        "In the browser, index.html contains the root DOM element. Vite loads src/main.tsx. React createRoot mounts App inside QueryClientProvider, BrowserRouter, viewport, theme, workspace, and authentication providers. App.tsx then maps URLs to public or protected pages.",
        "On the backend, the command uvicorn app.main:app imports app/main.py. Module import calls create_application(). That function creates FastAPI, registers global exception handlers and middleware, includes the versioned API router under /api/v1, and returns the app object.",
        "FastAPI's lifespan runs around the application's serving lifetime. It configures structured logging and records startup/shutdown. The root route is outside /api/v1; health and business routes are inside the versioned router."
      ],
      bullets: [
        "Frontend providers are nested; code inside them can access query cache, routing, viewport, theme, workspace, and auth state.",
        "Backend composition happens once at import/startup; per-request dependencies are created later by FastAPI.",
        "Settings are loaded through Pydantic Settings, and the database engine/session factory are module-level infrastructure."
      ],
      flow: {
        note: "Study the browser and server paths separately, then connect them at the HTTP boundary.",
        steps: [
          { label: "FRONTEND 1", title: "index.html", copy: "Vite serves the shell containing #root.", sources: [src("HTML entry", "frontend/index.html", 1)] },
          { label: "FRONTEND 2", title: "main.tsx", copy: "React mounts providers and App into #root.", sources: [src("React entry", "frontend/src/main.tsx", 22)] },
          { label: "FRONTEND 3", title: "App routes", copy: "React Router selects public, protected, desktop, or mobile pages.", sources: [src("Route tree", "frontend/src/App.tsx", 26), src("Protection", "frontend/src/components/ProtectedRoute.tsx", 4)] },
          { label: "BACKEND 1", title: "Uvicorn import", copy: "app.main:app imports the module and obtains the FastAPI object.", sources: [src("App module", "backend/app/main.py", 37)] },
          { label: "BACKEND 2", title: "Compose API", copy: "Exceptions, middleware, and /api/v1 routes are registered.", sources: [src("Application factory", "backend/app/main.py", 37), src("Router composition", "backend/app/api/v1/router.py", 14)] },
          { label: "BACKEND 3", title: "Lifespan", copy: "Logging starts, requests are served, and shutdown is recorded.", sources: [src("Lifespan", "backend/app/main.py", 12)] }
        ]
      },
      speak: "Suvyon has a browser entry and an API entry. Vite loads main.tsx, which mounts React with query, routing, viewport, theme, workspace, and auth providers; App.tsx selects the page. Uvicorn imports app.main:app; create_application registers exceptions, middleware, and the /api/v1 router, while lifespan configures startup and shutdown logging.",
      questions: [
        "Why use an application factory?",
        "Which routes are outside the /api/v1 prefix?",
        "What is created once at startup versus once per request?"
      ],
      truths: [
        { status: "implemented", text: "Both frontend and backend have explicit composition roots." },
        { status: "partial", text: "Startup configures logging but does not run migrations or provider health checks." }
      ]
    },
    {
      id: "frontend",
      group: "Entry points",
      title: "Frontend navigation and state",
      status: "implemented",
      summary: "React Router controls pages, context providers hold cross-page state, TanStack Query manages server data, and a central Axios client talks to FastAPI.",
      mentalModel: "A page does not query PostgreSQL. It calls a typed service wrapper, which calls Axios, which attaches the access token and reaches the backend.",
      explanation: [
        "App.tsx defines public routes for landing, login, registration, verification, and password reset. ProtectedRoute guards /app. Inside a selected workspace, AppShell or MobileShell renders nested pages for overview, chat, agents, knowledge, and settings.",
        "WorkspaceContext stores the selected workspace ID in React state and localStorage. AuthContext stores the current user, performs login/logout/registration, clears workspace and query state when identity changes, and restores the user from /users/me when an access token exists.",
        "services.ts is the browser's API map. It groups auth, users, workspaces, conversations, agents, knowledge bases, documents, and models. api.ts owns the base URL, bearer-token request interceptor, one-in-flight refresh promise, retry-after-401 behavior, and token cleanup."
      ],
      bullets: [
        "VITE_API_BASE_URL is read at build time; production changes require a frontend redeploy.",
        "Tokens and selected workspace are stored in localStorage. This is simple but an interview should acknowledge XSS exposure compared with hardened httpOnly-cookie designs.",
        "TanStack Query owns server-state caching; React context owns identity/theme/selected-workspace state."
      ],
      flow: {
        note: "Example: opening an existing conversation and sending a message.",
        steps: [
          { label: "01 ROUTE", title: "Open chat URL", copy: "React Router reads workspaceId and optional conversationId from the URL.", sources: [src("Chat routes", "frontend/src/App.tsx", 42)] },
          { label: "02 PAGE", title: "ChatPage loads", copy: "Queries fetch conversation lists, messages, models, and knowledge bases.", sources: [src("Chat page", "frontend/src/pages/ChatPage.tsx", 23)] },
          { label: "03 MUTATION", title: "User sends", copy: "The mutation builds content, selected mode, provider/model, and knowledge base fields.", sources: [src("Send mutation", "frontend/src/pages/ChatPage.tsx", 105)] },
          { label: "04 WRAPPER", title: "Service builds URL", copy: "conversationsApi translates UI data into the REST endpoint and payload.", sources: [src("Conversation client", "frontend/src/lib/services.ts", 64), src("sendMessage wrapper", "frontend/src/lib/services.ts", 104)] },
          { label: "05 AXIOS", title: "Token attached", copy: "The interceptor adds Authorization: Bearer and handles a single refresh race.", sources: [src("Axios interceptors", "frontend/src/lib/api.ts", 29)] },
          { label: "06 UI", title: "Cache refreshes", copy: "Mutation success updates or invalidates relevant query state and the response renders.", sources: [src("Chat mutation", "frontend/src/pages/ChatPage.tsx", 105)] }
        ]
      },
      speak: "The frontend separates routing, cross-cutting client state, server state, and HTTP transport. React Router chooses the page, contexts own the user and selected workspace, TanStack Query caches backend state, services.ts provides domain-specific endpoint wrappers, and api.ts attaches and refreshes JWTs.",
      questions: [
        "Why not put all state in React context?",
        "How are simultaneous 401 responses prevented from triggering many refresh calls?",
        "What is the security trade-off of localStorage tokens?"
      ],
      truths: [
        { status: "implemented", text: "Desktop and mobile pages share routing and API services." },
        { status: "partial", text: "Access and refresh tokens persist in localStorage, which needs strong XSS prevention." }
      ]
    },
    {
      id: "http",
      group: "Backend foundation",
      title: "HTTP, middleware, authentication, and OTP",
      status: "implemented",
      summary: "Every protected request passes through middleware and JWT dependencies before feature code can use it. Registration and password reset add hashed, expiring email OTPs.",
      mentalModel: "Middleware wraps every request. Dependencies act like guards at selected routes. The route delegates account rules to services, while repositories perform database operations.",
      explanation: [
        "Middleware adds CORS behavior, a request ID, and structured request logging. Exception handlers translate known application errors into stable HTTP responses. OAuth2PasswordBearer extracts the bearer token from the Authorization header.",
        "get_current_user checks the token's unique ID against an in-memory blacklist, decodes the expected access-token type, loads the user, and rejects an unknown identity. Two additional dependencies reject inactive or unverified users. Feature routes request the appropriate dependency.",
        "AuthService normalizes account operations: register hashes the password and triggers verification OTP, login verifies the hash and returns access/refresh JWTs, refresh requires a refresh token, logout blacklists the access-token JTI, and password changes/deactivation update the user. OtpService issues hashed codes, rate-limits resend, checks expiry and purpose, consumes successful codes, and sends system email.",
        "Authentication email and agent email share one delivery selector. A non-empty Resend key wins, otherwise a SendGrid key wins, otherwise SMTP is used. OTP email intentionally bypasses chat confirmation because registration/resend/reset is already the explicit transactional request; agent email has a separate confirmation boundary."
      ],
      bullets: [
        "Passwords and OTP codes are stored as hashes, not plaintext.",
        "Access and refresh tokens have distinct token_type claims and lifetimes.",
        "OTP codes are six digits, expire after 10 minutes, and are resend-rate-limited for 60 seconds.",
        "The token blacklist is process memory, so logout revocation is not shared across instances and disappears on restart—a production limitation."
      ],
      flow: {
        note: "Protected request path; registration adds the OTP branch after user creation.",
        steps: [
          { label: "01 REQUEST", title: "Middleware wraps", copy: "CORS, request ID, and logging surround the request/response.", sources: [src("Middleware registration", "backend/app/middleware/__init__.py", 8), src("Request ID", "backend/app/middleware/request_id.py", 7), src("Logging", "backend/app/middleware/logging.py", 9)] },
          { label: "02 TOKEN", title: "Bearer extracted", copy: "OAuth2PasswordBearer reads the Authorization header.", sources: [src("Security dependency", "backend/app/api/security.py", 13)] },
          { label: "03 VERIFY", title: "JWT decoded", copy: "JTI blacklist, token type, signature, expiry, and subject are checked.", sources: [src("Current user guard", "backend/app/api/security.py", 16), src("JWT helpers", "backend/app/core/security.py", 30)] },
          { label: "04 LOAD", title: "User loaded", copy: "The repository finds the account; active and verified guards may reject it.", sources: [src("Verified guard", "backend/app/api/security.py", 54), src("User repository", "backend/app/repositories/user_repository.py", 7)] },
          { label: "05 FEATURE", title: "Route executes", copy: "Only now does the protected workspace/chat/agent operation run.", sources: [src("Auth routes", "backend/app/api/v1/routes/auth.py", 25)] }
        ]
      },
      speak: "Authentication is layered. Middleware handles cross-cutting request behavior. A bearer-token dependency validates revocation, token type, signature, expiry, and subject, loads the user, then active and verified guards add policy. AuthService owns account rules; OtpService owns hashed, expiring, rate-limited verification and reset codes. OTP messages call the shared system-email path, whose transport order is Resend, then SendGrid, then SMTP.",
      questions: [
        "What is authentication versus authorization in this project?",
        "Why distinguish access and refresh token types?",
        "What breaks when the backend scales to multiple instances?"
      ],
      truths: [
        { status: "implemented", text: "JWT type checks, password hashing, verified-user gating, and hashed OTPs exist." },
        { status: "partial", text: "Token revocation is an in-memory set, not durable distributed state." },
        { status: "planned", text: "A production design could use short access TTLs and durable/shared refresh-token revocation." }
      ]
    },
    {
      id: "layers",
      group: "Backend foundation",
      title: "Route → dependency → service → repository",
      status: "implemented",
      summary: "FastAPI routes stay thin by receiving wired services. Services own business rules; repositories isolate recurring SQLAlchemy persistence operations.",
      mentalModel: "Route = HTTP translator. Dependency = assembler/guard. Service = use case. Repository = database access. Schema = validated boundary. Model = stored entity.",
      explanation: [
        "A route accepts path/query/body data using Pydantic schemas and asks FastAPI for dependencies. dependencies.py creates repositories from the request-scoped SQLAlchemy Session, then constructs services around those repositories.",
        "The route resolves identity and workspace ownership, invokes one service method, then FastAPI serializes the returned ORM object through a response schema. Services mutate domain entities, call repository create/commit/refresh, and roll back on errors.",
        "BaseRepository contains generic get/create/delete/commit/refresh/rollback mechanics. Feature repositories add scoped queries such as get_by_id_and_workspace or get_by_id_and_owner. That scoping is crucial to tenant isolation."
      ],
      bullets: [
        "Pydantic schemas protect the API boundary; SQLAlchemy models define persistence; they are deliberately different objects.",
        "The session dependency yields one SQLAlchemy Session and closes it after the request.",
        "Business logic sometimes directly queries through the session in ChatService/RAG; the separation is pragmatic rather than perfectly pure."
      ],
      flow: {
        note: "Example: POST /workspaces creates a workspace.",
        steps: [
          { label: "01 SCHEMA", title: "Validate request", copy: "FastAPI converts JSON into WorkspaceCreate or returns a 422 error.", sources: [src("Workspace schemas", "backend/app/schemas/workspace.py", 7)] },
          { label: "02 GUARD", title: "Resolve current user", copy: "The verified-user dependency supplies the authenticated ORM User.", sources: [src("Workspace route", "backend/app/api/v1/routes/workspaces.py", 89)] },
          { label: "03 WIRE", title: "Inject service", copy: "FastAPI builds WorkspaceRepository from Session, then WorkspaceService.", sources: [src("Dependency wiring", "backend/app/api/dependencies.py", 43), src("Service wiring", "backend/app/api/dependencies.py", 78)] },
          { label: "04 RULE", title: "Service creates", copy: "The service applies owner ID and default workspace fields.", sources: [src("Create use case", "backend/app/services/workspace_service.py", 49)] },
          { label: "05 STORE", title: "Repository commits", copy: "SQLAlchemy adds, commits, and refreshes the entity.", sources: [src("Base repository", "backend/app/repositories/base_repository.py", 42)] },
          { label: "06 RESPONSE", title: "Serialize result", copy: "WorkspaceResponse becomes JSON with the declared 201 status.", sources: [src("Create route", "backend/app/api/v1/routes/workspaces.py", 89)] }
        ]
      },
      speak: "Suvyon uses layered request handling. Routes translate HTTP and enforce request-level ownership. FastAPI dependencies assemble request-scoped repositories and services. Services implement use cases and transaction behavior. Repositories encapsulate common SQLAlchemy access, while Pydantic schemas and ORM models keep transport and persistence concerns separate.",
      questions: [
        "Why have schemas separate from models?",
        "Where does a transaction begin and end?",
        "What logic belongs in a route versus a service?"
      ],
      truths: [
        { status: "implemented", text: "Dependency injection builds services around a request-scoped DB session." },
        { status: "partial", text: "Some orchestration accesses the Session directly, so repository abstraction is not universal." }
      ]
    },
    {
      id: "data",
      group: "Backend foundation",
      title: "Database model and workspace isolation",
      status: "implemented",
      summary: "The ownership tree begins at User and Workspace. Conversations, documents, knowledge bases, and agents are workspace-scoped; messages and chunks inherit scope through their parents.",
      mentalModel: "Workspace is the tenant boundary. Never trust a workspace ID just because it appears in the URL—combine it with the authenticated owner in the database query.",
      explanation: [
        "BaseModel gives every entity a UUID plus created_at and updated_at. A User owns many Workspaces. A Workspace owns conversations, documents, knowledge bases, and agents with cascade deletion. A Conversation owns ordered Messages. DocumentChunk references both its source Document and KnowledgeBase and stores a 768-dimensional pgvector embedding.",
        "Routes call WorkspaceService.get_workspace with both workspace ID and current user ID. Child resources are then queried with both child ID and the already-authorized workspace ID. Retrieval filters by knowledge_base_id; ChatService first discovers active knowledge bases for the authorized conversation's workspace.",
        "PostgreSQL provides relational constraints and cascade behavior; Alembic records schema evolution. pgvector adds the vector column and cosine-distance operations while keeping relational filtering in the same query."
      ],
      bullets: [
        "Ownership graph: User → Workspace → Conversation → Message.",
        "Knowledge graph: Workspace → KnowledgeBase; Workspace → Document; Document + KnowledgeBase → DocumentChunk.",
        "Agent graph: Workspace → Agent configuration. Agent execution history is supplied by the caller and is not stored as an agent-run entity."
      ],
      flow: {
        note: "Authorization lookup is a graph traversal constrained by owner and parent IDs.",
        steps: [
          { label: "ROOT", title: "User", copy: "Identity owns workspaces; password and verification flags live here.", sources: [src("User model", "backend/app/models/user.py", 15)] },
          { label: "TENANT", title: "Workspace", copy: "Top-level boundary for conversations, documents, knowledge bases, and agents.", sources: [src("Workspace model", "backend/app/models/workspace.py", 17)] },
          { label: "CHAT", title: "Conversation → Message", copy: "Conversation carries provider/model settings; messages store role, content, and usage metadata.", sources: [src("Conversation model", "backend/app/models/conversation.py", 15), src("Message model", "backend/app/models/message.py", 20)] },
          { label: "KNOWLEDGE", title: "KB + Document", copy: "The KB groups retrieval; document tracks file path and processing status.", sources: [src("Knowledge base", "backend/app/models/knowledge_base.py", 14), src("Document model", "backend/app/models/document.py", 23)] },
          { label: "VECTOR", title: "DocumentChunk", copy: "Text, source IDs, index, page, and 768-value embedding become searchable.", sources: [src("Chunk model", "backend/app/models/chunk.py", 14)] },
          { label: "CONFIG", title: "Agent", copy: "Instructions, provider, model, tool names, and visibility flags are persisted.", sources: [src("Agent model", "backend/app/models/agent.py", 15)] }
        ]
      },
      speak: "Workspace is Suvyon's tenant boundary. Every top-level feature is connected to a workspace, and routes first prove that the authenticated user owns that workspace. Child repositories query by child and workspace IDs. PostgreSQL foreign keys and cascades preserve the ownership graph, while pgvector keeps semantic retrieval and relational filters together.",
      questions: [
        "How does Suvyon prevent horizontal ID guessing?",
        "Why does DocumentChunk carry both document_id and knowledge_base_id?",
        "What data is lost when deleting a workspace?"
      ],
      truths: [
        { status: "implemented", text: "Owner-scoped workspace lookup and workspace-scoped child lookup are used by routes." },
        { status: "partial", text: "The schema is owner-based; shared workspace membership/role ACLs are not modeled." },
        { status: "planned", text: "Enterprise sharing would need membership, role, document ACL, and retrieval-filter changes." }
      ]
    },
    {
      id: "workspace",
      group: "Feature flows",
      title: "Workspace and ordinary CRUD flows",
      status: "implemented",
      summary: "Workspace operations demonstrate the project's standard secure CRUD pattern: verify user, scope query by owner, call service, commit, serialize.",
      mentalModel: "Master this simple path first. Chat, RAG, and agents add AI behavior on top of the same identity, scoping, validation, and persistence foundation.",
      explanation: [
        "The frontend lists and selects workspaces. The selected UUID is stored locally and appears in nested route URLs. The backend never treats that client state as proof of ownership.",
        "Workspace routes provide list, get, create, update, delete, archive, restore, favourite, and unfavourite operations. Each depends on a verified user and WorkspaceService. The repository methods combine owner_id with workspace ID for scoped reads.",
        "Archive and favourite are state changes on an existing authorized entity. Delete relies on database cascade relationships to remove owned conversations, messages, documents, knowledge bases, chunks, and agent configurations."
      ],
      bullets: [
        "List queries can filter archived state and order favourites.",
        "The browser's workspace selection improves UX but the server-side owner predicate provides security.",
        "Cascade delete is convenient but destructive; production systems often add soft-delete, retention, export, and audit policies."
      ],
      flow: {
        note: "The same reusable CRUD skeleton appears in agents and knowledge bases.",
        steps: [
          { label: "01 UI", title: "Workspace page", copy: "TanStack Query requests the user's workspaces and renders selection/create actions.", sources: [src("Workspace page", "frontend/src/pages/WorkspacesPage.tsx", 1), src("Workspace API", "frontend/src/lib/services.ts", 46)] },
          { label: "02 ROUTE", title: "Verified user", copy: "The endpoint receives current_user and WorkspaceService through dependencies.", sources: [src("Workspace endpoints", "backend/app/api/v1/routes/workspaces.py", 22)] },
          { label: "03 SCOPE", title: "Owner predicate", copy: "Repository queries use owner_id, not only the supplied workspace UUID.", sources: [src("Scoped repository", "backend/app/repositories/workspace_repository.py", 16)] },
          { label: "04 USE CASE", title: "Service mutation", copy: "Create/update/archive/restore/favourite applies the business state change.", sources: [src("Workspace service", "backend/app/services/workspace_service.py", 21)] },
          { label: "05 DATABASE", title: "Commit", copy: "Repository transaction helpers persist or roll back changes.", sources: [src("Commit helpers", "backend/app/repositories/base_repository.py", 66)] },
          { label: "06 CLIENT", title: "Cache updates", copy: "The UI invalidates/refetches workspace data and navigates as needed.", sources: [src("Workspace context", "frontend/src/context/WorkspaceContext.tsx", 12)] }
        ]
      },
      speak: "Workspace CRUD is the clearest example of Suvyon's normal application architecture. The client selects a workspace ID, but every backend operation independently resolves the verified user and performs an owner-scoped query. Services mutate authorized entities, repositories commit, and response schemas serialize the result.",
      questions: [
        "Why is localStorage workspaceId not an authorization mechanism?",
        "What is the difference between archive and delete?",
        "How would you add workspace collaboration safely?"
      ],
      truths: [
        { status: "implemented", text: "Owner-scoped CRUD, archive/restore, and favourite state exist." },
        { status: "partial", text: "One owner per workspace; no member invitation or fine-grained role model." }
      ]
    }
  ]
};

window.SUVYON_GUIDE.topics.push(
  {
    id: "chat",
    group: "AI runtime",
    title: "Chat: direct, Auto, Web, and RAG modes",
    status: "implemented",
    summary: "ChatService is the central conversation orchestrator. It persists the user turn, selects a mode, builds provider-neutral messages, gets an answer, appends provenance, and persists the assistant turn.",
    mentalModel: "The conversation decides default provider/model and stores history. The request decides content and optional mode. ChatService turns both into one controlled model interaction.",
    explanation: [
      "The conversation route first proves workspace ownership, then proves the conversation belongs to that workspace. It can update the conversation's provider/model from the request before delegating to ChatService.",
      "send_message persists the user's message before model generation. If the title is still a default, it derives a short title. With no explicit mode, Auto mode offers tool schemas to the LLM. The model may answer directly or request search_knowledge, web_search, Wikipedia, or creative tools. With explicit chat, web, or rag mode, ChatService follows that requested path.",
      "_build_contextual_messages begins with Suvyon's Markdown system instruction, adds an optional conversation system prompt and stored history, then creates the current user message. Web mode performs Wikipedia/search before generation. RAG mode retrieves context and uses build_rag_prompt. Direct chat sends ordinary history.",
      "After generation, ChatService appends a provenance note describing knowledge sources, web links, or provider/model. It stores the assistant message with provider/model and, on the non-Auto non-stream path, token usage."
    ],
    bullets: [
      "Auto mode is an LLM tool-selection path; explicit RAG forces a retrieval attempt.",
      "If explicit RAG finds no source, selected_mode becomes chat, so inspect the fallback behavior when discussing strict grounding.",
      "Application-owned message history enables provider switching because adapters receive neutral LLMMessage objects."
    ],
    flow: {
      note: "Auto chat includes a decision branch at the first model call.",
      steps: [
        { label: "01 HTTP", title: "Conversation route", copy: "Validate workspace + conversation and pass content/mode/KB to ChatService.", sources: [src("Message endpoint", "backend/app/api/v1/routes/conversations.py", 153)] },
        { label: "02 PERSIST", title: "Save user turn", copy: "Create the Message row before generation and auto-title a new conversation.", sources: [src("send_message", "backend/app/services/chat_service.py", 512)] },
        { label: "03 CONTEXT", title: "Build messages", copy: "System prompt, conversation prompt, history, and current content become LLMMessage objects.", sources: [src("Context builder", "backend/app/services/chat_service.py", 388)] },
        { label: "04 DECIDE", title: "Select behavior", copy: "Explicit mode uses its path; Auto exposes tool schemas and lets the model answer or call a tool.", sources: [src("Auto answer loop", "backend/app/services/chat_service.py", 246), src("Mode tools", "backend/app/services/chat_service.py", 190)] },
        { label: "05 GENERATE", title: "Route to provider", copy: "route_chat resolves provider/model, invokes the adapter, and returns a neutral LLMResponse.", sources: [src("Model call", "backend/app/ai/router.py", 102)] },
        { label: "06 PROVENANCE", title: "Explain source", copy: "Knowledge, web, or direct-model source information is appended.", sources: [src("Provenance", "backend/app/services/chat_service.py", 491)] },
        { label: "07 PERSIST", title: "Save assistant", copy: "Content and actual provider/model become a second Message row.", sources: [src("Assistant save", "backend/app/services/chat_service.py", 571)] }
      ]
    },
    speak: "A chat request is authorized against both workspace and conversation, then ChatService saves the user turn and builds neutral messages from system instructions, optional conversation instructions, and persisted history. Explicit chat/web/RAG modes follow fixed paths; Auto mode lets the model request narrow tools. The model router returns a provider-neutral response, provenance is appended, and the assistant turn is persisted with the actual provider and model.",
    questions: [
      "What is the exact difference between explicit RAG and Auto?",
      "Why save the user message before calling the LLM?",
      "What happens when explicit RAG retrieves nothing?",
      "Where is conversation history assembled and why is the current turn removed once?"
    ],
    truths: [
      { status: "implemented", text: "Direct, web-grounded, explicit RAG, and Auto tool-selection paths exist." },
      { status: "partial", text: "Auto tool execution is bounded but does not use durable state/checkpoints." },
      { status: "planned", text: "Formal intent classification, response validation, and evaluation remain improvement areas." }
    ]
  },
  {
    id: "routing",
    group: "AI runtime",
    title: "Model registry, routing, and provider adapters",
    status: "implemented",
    summary: "Business code uses one message/response contract. The router resolves configured providers and models; adapters translate that contract into Groq, Gemini, or OpenRouter HTTP formats.",
    mentalModel: "The router chooses an airline and flight. The adapter translates your common ticket into that airline's format. It cannot erase real differences between airlines.",
    explanation: [
      "base.py defines LLMMessage, LLMResponse, ModelInfo, and the abstract BaseLLMProvider methods chat, stream, list_models, and is_available. These types are the stable boundary used by ChatService and Agent runner.",
      "registry.py constructs the known provider objects and exposes available providers and model listings. Availability generally depends on configured API keys. router.py resolves an explicit provider/model when valid or walks available providers using defaults/aliases. route_chat attempts providers and returns the first successful response; route_stream resolves one provider and yields its stream.",
      "Groq and OpenRouter use OpenAI-style messages and SSE formats. Gemini requires translation for system instructions, message roles, function declarations, function calls/results, and streaming response events. Each adapter owns authentication headers, payload serialization, error translation, response parsing, and model catalog."
    ],
    bullets: [
      "Sequential availability/failure fallback is implemented for chat; dynamic latency, quality, health, cost, or capacity scoring is not.",
      "Model ownership is validated so a model ID is not accidentally sent to the wrong provider.",
      "The provider abstraction leaks capabilities: tool support, model limits, error formats, and streaming behavior differ and must be represented honestly."
    ],
    flow: {
      note: "Follow this every time ChatService or Agent runner calls route_chat.",
      steps: [
        { label: "01 CONTRACT", title: "Neutral messages", copy: "System/user/assistant/tool data is represented by LLMMessage.", sources: [src("Provider contract", "backend/app/ai/providers/base.py", 7)] },
        { label: "02 RESOLVE", title: "Provider + model", copy: "Explicit values, aliases, defaults, availability, and tool needs are considered.", sources: [src("Resolve", "backend/app/ai/router.py", 54)] },
        { label: "03 VALIDATE", title: "Ownership", copy: "The router checks whether the chosen provider lists the requested model.", sources: [src("Model ownership", "backend/app/ai/router.py", 50)] },
        { label: "04 ADAPT", title: "Build vendor payload", copy: "The selected adapter converts messages and tools to the provider's wire format.", sources: [src("Groq payload", "backend/app/ai/providers/groq.py", 92), src("Gemini translation", "backend/app/ai/providers/gemini.py", 74), src("OpenRouter payload", "backend/app/ai/providers/openrouter.py", 73)] },
        { label: "05 NETWORK", title: "External API call", copy: "HTTP request executes with provider key, timeout, and streaming/non-stream semantics.", sources: [src("Groq chat", "backend/app/ai/providers/groq.py", 111), src("Gemini chat", "backend/app/ai/providers/gemini.py", 227)] },
        { label: "06 NORMALIZE", title: "LLMResponse", copy: "Text, tool calls, provider/model, and available token counts return in one shape.", sources: [src("Response contract", "backend/app/ai/providers/base.py", 16)] },
        { label: "07 FALLBACK", title: "Try next", copy: "Non-stream chat can move through configured providers after failure.", sources: [src("route_chat", "backend/app/ai/router.py", 102)] }
      ]
    },
    speak: "Suvyon isolates vendors behind LLMMessage, LLMResponse, ModelInfo, and BaseLLMProvider. The registry knows configured providers and their models. The router resolves and validates provider/model choice, then adapters serialize provider-specific payloads and normalize results. Current resilience is availability checks plus sequential chat fallback—not dynamic health, latency, quality, or cost routing.",
    questions: [
      "How can a conversation switch providers without losing context?",
      "Why is Gemini adapter translation more involved?",
      "Does streaming use the same fallback behavior as non-stream chat?",
      "Which provider differences leak through the abstraction?"
    ],
    truths: [
      { status: "implemented", text: "Provider-neutral domain types, three adapters, model ownership checks, and sequential chat fallback exist." },
      { status: "partial", text: "Streaming pins one resolved provider and does not loop across providers after partial output." },
      { status: "planned", text: "Health-scored, capability/cost/latency-aware routing and circuit breakers are not present." }
    ]
  },
  {
    id: "rag-ingest",
    group: "RAG",
    title: "RAG ingestion: upload to pgvector",
    status: "partial",
    summary: "A document is validated, saved to local disk, parsed, split into overlapping chunks, embedded, and written as DocumentChunk rows. Processing currently happens synchronously.",
    mentalModel: "Ingestion turns an opaque file into searchable evidence units. File → text → chunks → vectors → rows with provenance.",
    explanation: [
      "KnowledgePage uploads multipart form data containing knowledge_base_id and the file. The document route verifies the workspace and passes UploadFile to DocumentService. The service validates size/type, creates an uploads directory, saves the file body, creates a pending Document row, and invokes process_document.",
      "The pipeline sets status to processing, parses according to MIME type, rejects empty text, creates overlapping chunks, and embeds all chunk contents. Parser support includes PDF, DOCX, TXT, Markdown, and CSV; PDF attempts visual block ordering, while DOCX preserves paragraphs, tables, and text boxes.",
      "The chunker targets 800 characters with 150-character overlap. It splits paragraphs, long sentences, and words, packs units, and removes extremely short noise. Embeddings use Gemini embedding configuration first or an OpenAI-compatible configured endpoint, with query/document task distinctions where supported.",
      "save_chunks writes content, chunk index, page metadata, document ID, knowledge-base ID, and a 768-dimensional vector. Success sets ready and chunk_count; exceptions roll back chunk work, set failed/error_message, and re-raise."
    ],
    bullets: [
      "Processing is in the HTTP request, so a large file can block, time out, or leave user experience dependent on one web process.",
      "File bodies are on local/ephemeral deployment disk, although metadata and chunks are in PostgreSQL.",
      "The KnowledgeBase.embedding_model field exists, but verify whether every pipeline choice actually reads it before claiming per-KB embedding selection."
    ],
    flow: {
      note: "This pipeline creates the evidence searched later; generation is not part of ingestion.",
      steps: [
        { label: "01 UI", title: "Multipart upload", copy: "Browser sends KB ID plus File to the workspace document endpoint.", sources: [src("Document client", "frontend/src/lib/services.ts", 206), src("Knowledge UI", "frontend/src/pages/KnowledgePage.tsx", 1)] },
        { label: "02 AUTH", title: "Scope workspace", copy: "Route verifies user owns the workspace before accepting upload.", sources: [src("Upload route", "backend/app/api/v1/routes/documents.py", 40)] },
        { label: "03 STORE FILE", title: "Save local body", copy: "DocumentService validates and writes the upload, then creates Document metadata.", sources: [src("Document upload", "backend/app/services/document_service.py", 33)] },
        { label: "04 PARSE", title: "Extract text", copy: "MIME-specific logic reads PDF/DOCX/text/Markdown/CSV content.", sources: [src("Parser", "backend/app/rag/parser.py", 13)] },
        { label: "05 CHUNK", title: "Create evidence units", copy: "Paragraph-aware splitting, packing, and overlap produce indexed chunks.", sources: [src("Chunker", "backend/app/rag/chunker.py", 24)] },
        { label: "06 EMBED", title: "Generate vectors", copy: "Texts are batched through the configured embedding API into 768 dimensions.", sources: [src("Embedding selection", "backend/app/rag/embeddings.py", 54)] },
        { label: "07 INDEX", title: "Insert chunk rows", copy: "Text, provenance, and vectors are stored in PostgreSQL/pgvector.", sources: [src("save_chunks", "backend/app/rag/vector_store.py", 18), src("Chunk schema", "backend/app/models/chunk.py", 14)] },
        { label: "08 STATUS", title: "Ready or failed", copy: "Document records chunk count or the processing error.", sources: [src("Pipeline", "backend/app/rag/pipeline.py", 23)] }
      ]
    },
    speak: "Suvyon's ingestion path verifies workspace ownership, saves the uploaded file and Document metadata, then synchronously parses, chunks, embeds, and stores DocumentChunk rows with 768-dimensional vectors. Document status moves through pending, processing, ready, or failed. The functional pipeline is implemented, but durable object storage and queued idempotent workers are the important production upgrades.",
    questions: [
      "Why overlap chunks and what can go wrong?",
      "How does failure affect Document status?",
      "Why is synchronous ingestion risky?",
      "How would you change embedding models without mixing vector spaces?"
    ],
    truths: [
      { status: "implemented", text: "MIME parsing, overlap chunking, embeddings, pgvector rows, and status/error handling exist." },
      { status: "partial", text: "Files use local disk and processing runs inside the request." },
      { status: "planned", text: "Object storage, queue/workers, idempotency, malware scanning, and index version cutover are not current runtime behavior." }
    ]
  },
  {
    id: "rag-query",
    group: "RAG",
    title: "RAG query: question to grounded answer",
    status: "implemented",
    summary: "The question becomes a query vector, pgvector ranks nearby chunks inside a knowledge base, diversity logic prevents one document dominating, and a grounded prompt goes to the LLM.",
    mentalModel: "Retrieval finds evidence; generation writes an answer. Debug those as two separate systems.",
    explanation: [
      "For explicit RAG, ChatService determines which active knowledge bases in the conversation's workspace to search. For Auto mode, search_knowledge appears as a tool only when an active knowledge base exists. Both paths call _build_rag_context.",
      "retrieve_context_with_sources embeds the user's query using the query task type, then similarity_search filters rows by knowledge_base_id and orders by cosine distance. It fetches an expanded candidate pool and applies diversity: first select the best chunk from each document, then fill remaining positions by score.",
      "A maximum-distance threshold can exclude weak matches in Auto mode. Retrieved chunks become labeled context sections and source names. build_rag_prompt tells the model to use supplied context, identify sources, avoid invention, and either answer strictly or allow general-knowledge fallback depending on the caller.",
      "RAG quality can fail at parsing, chunking, embedding, query representation, filtering, ranking, thresholding, context assembly, or generation. A good interview answer measures retrieval recall separately from faithfulness."
    ],
    bullets: [
      "Cosine distance is lower when vectors are more similar; do not accidentally describe it as a higher-is-better similarity score.",
      "Knowledge-base filtering is applied in SQL. Workspace isolation is inherited because only KBs from the authorized workspace reach this call.",
      "Current retrieval is dense vector search with diversity; hybrid BM25, reranking, and formal offline metrics are improvements."
    ],
    flow: {
      note: "The decision to use RAG happens before this retrieval pipeline.",
      steps: [
        { label: "01 SELECT", title: "Choose KB scope", copy: "Explicit KB or active workspace KBs determine the allowed search space.", sources: [src("Active KB lookup", "backend/app/services/chat_service.py", 141), src("RAG context", "backend/app/services/chat_service.py", 153)] },
        { label: "02 EMBED", title: "Embed question", copy: "The query task creates a vector in the same 768-dimensional space.", sources: [src("embed_query", "backend/app/rag/embeddings.py", 84)] },
        { label: "03 FILTER", title: "Limit to KB", copy: "SQL filters by knowledge_base_id before ranking.", sources: [src("Similarity search", "backend/app/rag/vector_store.py", 67)] },
        { label: "04 RANK", title: "Cosine distance", copy: "Nearest candidate chunks are ordered; optional max distance removes weak matches.", sources: [src("Vector search", "backend/app/rag/vector_store.py", 67)] },
        { label: "05 DIVERSIFY", title: "Spread documents", copy: "Best chunk per document is selected before filling remaining top-k slots.", sources: [src("Diversity function", "backend/app/rag/vector_store.py", 27), src("Diversity test", "backend/tests/test_rag_diversity.py", 1)] },
        { label: "06 CONTEXT", title: "Attach sources", copy: "Chunk text and document names become prompt context and provenance links.", sources: [src("Retriever", "backend/app/rag/retriever.py", 62)] },
        { label: "07 PROMPT", title: "Ground generation", copy: "The prompt defines strict or fallback behavior around supplied evidence.", sources: [src("RAG prompt", "backend/app/rag/retriever.py", 95)] },
        { label: "08 ANSWER", title: "LLM + provenance", copy: "The routed model generates; ChatService appends source details and stores the message.", sources: [src("Contextual RAG branch", "backend/app/services/chat_service.py", 448), src("Provenance", "backend/app/services/chat_service.py", 491)] }
      ]
    },
    speak: "RAG query processing scopes the search to authorized active knowledge bases, embeds the question, filters DocumentChunk rows by knowledge base, ranks them by cosine distance, and diversifies top results across documents. The retriever builds text plus sources, build_rag_prompt constrains generation, and ChatService appends provenance. Current retrieval is dense-only; hybrid search, reranking, and formal evaluation are next steps.",
    questions: [
      "Where exactly is the tenant boundary enforced?",
      "What does the diversity algorithm solve and what does it not solve?",
      "How do you tell retrieval failure from generation failure?",
      "What is the effect of max_distance in Auto mode?"
    ],
    truths: [
      { status: "implemented", text: "Query embeddings, cosine-distance search, KB filtering, source output, and cross-document diversity exist." },
      { status: "partial", text: "A threshold is used in Auto knowledge search, but calibration/evaluation infrastructure is absent." },
      { status: "planned", text: "BM25 hybrid retrieval, cross-encoder reranking, ACLs below workspace/KB, and golden-set metrics are not implemented." }
    ]
  },
  {
    id: "agents",
    group: "Agents and tools",
    title: "Saved agents and the bounded tool loop",
    status: "implemented",
    summary: "An Agent row stores persona, instructions, provider, model, and allowed tool names. runner.py builds messages, lets the LLM propose tool calls, executes them in Python, and synthesizes a final answer with tools disabled.",
    mentalModel: "The model is the decision-maker inside a fenced loop. The Python runner owns the fence, tool execution, observations, and stopping behavior.",
    explanation: [
      "The Agents page creates or edits a workspace-scoped Agent. AgentService performs ordinary CRUD. Run endpoints verify workspace and agent scope, then call run_agent or stream_agent with user content and optional history.",
      "_get_agent_tools parses the comma-separated names and intersects them with the registry. _build_messages combines agent instructions, safety/tool-specific suffixes, history, and the new user message. get_tool_schemas exposes only the selected tools to the model.",
      "run_agent calls route_chat. If the LLM returns tool calls, _execute_tool_calls appends an assistant tool-call message, invokes Python functions through _call_tool, and appends tool observations. _synthesize_answer then calls the model again without tools, preventing another tool loop. A forced web-search heuristic covers obvious current-information prompts when the model fails to call search.",
      "MAX_ITERATIONS is four, but current control flow normally returns after the first useful model response or first tool batch. This is a bounded single-agent runner, not a planner/executor graph, durable agent runtime, or multi-agent system."
    ],
    bullets: [
      "The LLM proposes a function name and arguments; application code executes the function.",
      "Tool errors are converted to text observations so synthesis can report or recover.",
      "Agent run history is passed in the request; there is no persisted AgentRun/trajectory/checkpoint model."
    ],
    flow: {
      note: "This is the ReAct-style control path, even though hidden reasoning is not stored.",
      steps: [
        { label: "01 LOAD", title: "Authorized agent", copy: "Route proves the agent belongs to the authorized workspace.", sources: [src("Run route", "backend/app/api/v1/routes/agents.py", 106), src("Scoped lookup", "backend/app/repositories/agent_repository.py", 20)] },
        { label: "02 ALLOWLIST", title: "Resolve tools", copy: "Saved comma-separated names are intersected with the real registry.", sources: [src("Allowed tools", "backend/app/agents/runner.py", 63)] },
        { label: "03 PROMPT", title: "Build messages", copy: "Persona instructions, safety suffixes, history, and request are assembled.", sources: [src("Message builder", "backend/app/agents/runner.py", 76)] },
        { label: "04 DECISION", title: "LLM proposes", copy: "The provider returns answer text or structured tool calls.", sources: [src("Agent loop", "backend/app/agents/runner.py", 240)] },
        { label: "05 EXECUTE", title: "Python calls tool", copy: "Arguments normalize; registry function executes; result becomes a tool observation.", sources: [src("Tool dispatch", "backend/app/agents/runner.py", 109), src("Execute calls", "backend/app/agents/runner.py", 175)] },
        { label: "06 SYNTHESIZE", title: "Tools disabled", copy: "A final model call uses observations and cannot request more tools.", sources: [src("Synthesis", "backend/app/agents/runner.py", 213)] },
        { label: "07 RETURN", title: "Answer or fallback", copy: "Useful model text returns; otherwise safe tool output/error becomes the response.", sources: [src("Fallback", "backend/app/agents/runner.py", 201)] }
      ]
    },
    speak: "An Agent is a saved single-agent configuration, not an autonomous process. The run route authorizes it, the runner resolves an allowlisted subset of registry tools, builds instructions and history, and calls a provider. The model may propose structured tool calls; Python validates/normalizes and executes them, appends observations, then makes a tools-disabled synthesis call. The runner is bounded and has safe fallbacks, but lacks durable run state, checkpointing, and trajectory evaluation.",
    questions: [
      "Does the LLM execute the tool?",
      "Why disable tools during synthesis?",
      "Does MAX_ITERATIONS mean four tools always run?",
      "What state would be required for resumable human approval?"
    ],
    truths: [
      { status: "implemented", text: "Workspace-scoped saved agents, selected tool schemas, tool observations, and bounded synthesis exist." },
      { status: "partial", text: "Argument normalization exists, but schemas are simple and execution policy is mostly tool-specific." },
      { status: "planned", text: "Durable checkpoints, repeated-call detection, cost budgets, multi-agent handoffs, and trajectory storage are absent." }
    ]
  },
  {
    id: "tools",
    group: "Agents and tools",
    title: "Tool registry, web search, and email safety",
    status: "partial",
    summary: "The registry maps tool names to Python callables and JSON-like schemas. The runner is the execution boundary; email adds a second confirmation check inside the tool itself.",
    mentalModel: "A schema is a menu shown to the model. The registry is the kitchen map. _call_tool is the waiter who validates and dispatches. The actual Python function performs the work.",
    explanation: [
      "TOOL_REGISTRY contains callable, description, parameter types, and required fields. get_tool_schemas converts selected entries into function schemas understood by LLM providers. Available tools cover search/research, Wikipedia/arXiv/page reading, weather/place lookup, media URLs/speech markers, QR/diagram/brand/event/decision helpers, calculator/time, and email.",
      "_call_tool normalizes dictionary or JSON-string arguments. It has specific adapters for email, images, and web search, then a generic function call with a fallback that removes unexpected keys. Exceptions become Tool error strings rather than crashing the whole agent response.",
      "Web search tries configured providers in priority order and includes free fallbacks. Returned text includes titles, URLs, and snippets for later source extraction. External content must be treated as untrusted; the current prompt guidance is useful but not a complete prompt-injection security boundary.",
      "Email uses defense in depth. Agent instructions require drafting before sending, while send_email independently checks recipient/body and user_confirmed_send against the current user text. Delivery selects Resend first, otherwise SendGrid, otherwise SMTP. Authentication OTP email uses this exact delivery selector through send_system_email but does not use chat confirmation. The tests verify denial without confirmation and successful provider behavior."
    ],
    bullets: [
      "Descriptions influence model choices but do not authorize calls.",
      "send_email's explicit confirmation check is stronger than relying only on a system prompt.",
      "A configured provider is authoritative: the code does not fall through to a lower-priority transport after Resend or SendGrid rejects a request.",
      "A production side-effect design would bind approval to an exact draft hash, persist it, expire it, authorize destinations, and use idempotency keys."
    ],
    flow: {
      note: "Email demonstrates the important difference between model policy and application policy.",
      steps: [
        { label: "01 EXPOSE", title: "Selected schema", copy: "Only an agent's saved tools are translated into model-visible function schemas.", sources: [src("Schema generation", "backend/app/tools/registry.py", 160)] },
        { label: "02 PROPOSE", title: "Model tool call", copy: "The LLM returns name + arguments; no Python has run yet.", sources: [src("Response tool_calls", "backend/app/ai/providers/base.py", 16)] },
        { label: "03 DISPATCH", title: "Normalize + find", copy: "Runner parses arguments and resolves the callable from TOOL_REGISTRY.", sources: [src("Argument normalization", "backend/app/agents/runner.py", 93), src("Dispatch", "backend/app/agents/runner.py", 109)] },
        { label: "04 POLICY", title: "Email confirmation", copy: "send_email rejects first-turn compose requests without explicit send confirmation.", sources: [src("Confirmation parser", "backend/app/tools/email_tool.py", 111), src("send_email", "backend/app/tools/email_tool.py", 153)] },
        { label: "05 PROVIDER", title: "Deliver externally", copy: "Configured HTTP mail provider or SMTP performs the actual side effect.", sources: [src("Delivery selection", "backend/app/tools/email_tool.py", 248), src("Resend", "backend/app/tools/email_tool.py", 280), src("SendGrid", "backend/app/tools/email_tool.py", 308)] },
        { label: "06 OBSERVE", title: "Return truth", copy: "Success/error text is appended as a tool observation for final synthesis.", sources: [src("Tool result message", "backend/app/agents/runner.py", 175), src("Safety tests", "backend/tests/test_email_tools.py", 29)] }
      ]
    },
    speak: "The registry turns narrow Python capabilities into model-visible schemas. The model only proposes calls; runner.py normalizes arguments, resolves the allowlisted callable, executes it, and records the result. Email adds application-level confirmation inside send_email and chooses Resend, SendGrid, or SMTP for delivery. That is defense in depth, though durable approval binding and idempotency are still production gaps.",
    questions: [
      "Why are good tool descriptions necessary but insufficient for safety?",
      "What prevents email from being sent on the initial compose request?",
      "What happens when a model invents an extra argument?",
      "How could a web page attack an agent through its content?"
    ],
    truths: [
      { status: "implemented", text: "Central registry, schemas, dispatch, error conversion, multiple mail transports, and explicit email confirmation checks exist." },
      { status: "partial", text: "Tool input schemas are simple dictionaries and authorization is not a generic per-tool policy engine." },
      { status: "planned", text: "Durable approvals, idempotency/reconciliation, scoped credentials, sandboxing, and injection scanning need further work." }
    ]
  },
  {
    id: "streaming",
    group: "Production behavior",
    title: "SSE streaming and persistence",
    status: "implemented",
    summary: "Streaming resolves tools first when necessary, then yields text chunks over Server-Sent Events while collecting the full response for final database persistence.",
    mentalModel: "Two outputs happen at different times: chunks go to the browser immediately; the complete message is committed only after generation finishes.",
    explanation: [
      "The route returns FastAPI StreamingResponse with media type text/event-stream. Its generator calls ChatService.stream_message and formats each chunk as SSE data. Errors are emitted as stream events because HTTP headers may already be sent.",
      "stream_message saves the user turn first. In Auto mode, _stream_with_tools performs a non-streaming decision call when schemas exist. If tools are requested, Python executes them and then route_stream generates the final synthesis. If the first call already contains an answer, it yields that content directly.",
      "As chunks arrive, ChatService concatenates them into full_content and yields each chunk onward. Only after the provider iterator ends does it append provenance and create the assistant Message. This makes disconnect/cancellation semantics important: an interrupted generator may leave the saved user turn without a saved assistant turn.",
      "The selected provider/model should remain pinned after a tool decision so observations use a compatible continuation. Failover after visible tokens is unsafe unless the product explicitly restarts or marks the response partial."
    ],
    bullets: [
      "SSE is one-way server-to-browser streaming and is simpler than WebSocket for token output.",
      "Time to first token affects perceived latency; total completion time and persistence happen later.",
      "The browser's ordinary Axios send wrapper is distinct from fully parsing SSE; inspect the page behavior before claiming every UI path streams."
    ],
    flow: {
      note: "The database contains the user turn during generation; the assistant turn appears at stream completion.",
      steps: [
        { label: "01 ROUTE", title: "StreamingResponse", copy: "FastAPI prepares an SSE generator after authorization.", sources: [src("Stream endpoint", "backend/app/api/v1/routes/conversations.py", 189)] },
        { label: "02 PERSIST", title: "Save user", copy: "ChatService commits the current user Message before yielding content.", sources: [src("stream_message", "backend/app/services/chat_service.py", 613)] },
        { label: "03 DECIDE", title: "Resolve tools", copy: "Auto mode may make one normal call to decide and execute tools before final streaming.", sources: [src("Auto stream tools", "backend/app/services/chat_service.py", 320)] },
        { label: "04 STREAM", title: "Provider chunks", copy: "route_stream chooses one provider and yields adapter text fragments.", sources: [src("route_stream", "backend/app/ai/router.py", 169), src("Groq stream", "backend/app/ai/providers/groq.py", 170)] },
        { label: "05 SSE", title: "Browser receives", copy: "The route wraps fragments as data events over one open HTTP response.", sources: [src("Event generator", "backend/app/api/v1/routes/conversations.py", 208)] },
        { label: "06 COLLECT", title: "Build full text", copy: "Server concatenates the same fragments while sending them.", sources: [src("Full content collection", "backend/app/services/chat_service.py", 687)] },
        { label: "07 COMMIT", title: "Save assistant", copy: "After normal completion, provenance and the full assistant Message are persisted.", sources: [src("Stream persistence", "backend/app/services/chat_service.py", 700)] }
      ]
    },
    speak: "The stream route returns SSE and delegates to a generator. ChatService commits the user turn, resolves any Auto-mode tools, pins the selected provider, and yields provider chunks while accumulating the full answer. On normal completion it appends provenance and persists the assistant turn. The key failure case is interruption after the user commit but before the final assistant commit.",
    questions: [
      "Why use SSE rather than WebSocket here?",
      "What happens if the browser disconnects halfway?",
      "Can you safely switch providers after emitting tokens?",
      "Why can tool selection add latency before the first streamed answer token?"
    ],
    truths: [
      { status: "implemented", text: "Conversation and agent stream endpoints plus provider stream adapters exist." },
      { status: "partial", text: "Partial completion/cancellation recovery and persisted status are not modeled explicitly." },
      { status: "planned", text: "Resumable streams, durable run state, and formal TTFT/p95 tracing remain improvements." }
    ]
  },
  {
    id: "operations",
    group: "Production behavior",
    title: "Configuration, deployment, tests, and honest gaps",
    status: "partial",
    summary: "Vercel hosts the static frontend, Render hosts FastAPI, and Supabase hosts PostgreSQL. Environment settings connect them; tests protect several high-risk AI and auth behaviors.",
    mentalModel: "Deployment is a three-host contract: browser knows API URL at build time, API allows browser origin at runtime, and API knows database/provider secrets at runtime.",
    explanation: [
      "The frontend build reads VITE_API_BASE_URL and deploys static assets to Vercel. Render starts the Python web service using render.yaml/runtime configuration. Backend Settings reads DATABASE_URL, JWT settings, CORS origins, LLM/search/email credentials, upload limits, and other environment-specific values. Supabase provides persistent PostgreSQL plus pgvector.",
      "CORS must contain the frontend origin, not the backend URL. A changed Vite environment variable needs a rebuild/redeploy because it is embedded in the JavaScript bundle. Alembic migrations evolve tables and vector indexes separately from application startup.",
      "The backend tests cover router selection/ownership/aliases, intent and tool selection, agent behavior and termination, email confirmation/delivery, chunking, RAG diversity, and OTP authentication. These are valuable deterministic tests, but they are not the same as an AI quality evaluation suite over real questions.",
      "The strongest interview answer is honest: the current architecture is suitable for a portfolio/free-tier deployment, while production priorities include durable object storage and async ingestion, distributed rate/revocation state, structured telemetry, a golden evaluation set, stronger generic tool policy/idempotency, and load-tested SLOs."
    ],
    bullets: [
      "Secrets belong in host environment settings, never frontend variables or source control.",
      "Render free instances may sleep; first-request latency is a hosting property, not model latency.",
      "Architecture documents include future goals. Tests and runtime code prove implemented behavior."
    ],
    flow: {
      note: "Production request path and release boundary.",
      steps: [
        { label: "01 BUILD", title: "Vite → Vercel", copy: "Frontend assets compile with VITE_API_BASE_URL baked in.", sources: [src("Frontend package", "frontend/package.json", 1), src("Vercel config", "frontend/vercel.json", 1)] },
        { label: "02 REQUEST", title: "Browser → Render", copy: "HTTPS reaches FastAPI; CORS permits the exact Vercel origin.", sources: [src("CORS", "backend/app/middleware/cors.py", 7), src("Settings", "backend/app/core/config.py", 12)] },
        { label: "03 STATE", title: "Render → Supabase", copy: "SQLAlchemy uses DATABASE_URL for persistent relational/vector state.", sources: [src("Database", "backend/app/core/database.py", 1), src("URL normalization", "backend/app/core/config.py", 151)] },
        { label: "04 AI", title: "Render → providers", copy: "Server-side API keys authorize LLM, embedding, search, and email requests.", sources: [src("Provider registry", "backend/app/ai/registry.py", 1), src("Environment guide", "docs/ENVIRONMENT.md", 1)] },
        { label: "05 MIGRATE", title: "Alembic", copy: "Versioned migrations create and repair relational/vector schemas.", sources: [src("Alembic config", "backend/alembic.ini", 1), src("RAG migration", "backend/alembic/versions/b2c3d4e5f6a7_phase_3_rag.py", 1)] },
        { label: "06 VERIFY", title: "Pytest", copy: "Deterministic tests protect routes and selected AI orchestration invariants.", sources: [src("Agent tests", "backend/tests/test_agent_runner.py", 1), src("Router tests", "backend/tests/test_model_router.py", 1), src("RAG tests", "backend/tests/test_rag_diversity.py", 1), src("OTP tests", "backend/tests/test_otp_auth.py", 1)] }
      ]
    },
    speak: "Suvyon deploys a Vite frontend to Vercel, FastAPI to Render, and PostgreSQL/pgvector to Supabase. The frontend API URL is build-time; CORS, database, providers, and secrets are backend runtime settings. Alembic owns schema evolution, and pytest protects important routing, agent, email, RAG, and OTP invariants. The main production gaps are durable async ingestion, shared operational state, formal evaluation/telemetry, and stronger generic side-effect controls.",
    questions: [
      "Why does changing VITE_API_BASE_URL require redeploy?",
      "What is the difference between unit/integration tests and LLM evaluation?",
      "Which three upgrades would you prioritize and why?",
      "How would you define SLOs for chat, RAG, and ingestion?"
    ],
    truths: [
      { status: "implemented", text: "Vercel/Render/Supabase configuration, Alembic migrations, health endpoint, and focused tests exist." },
      { status: "partial", text: "Free-tier hosting and ephemeral upload storage constrain reliability and cold-start behavior." },
      { status: "planned", text: "Queues/workers, object storage, distributed caching/rate limits, structured traces, golden evals, and autoscaling controls are future work." }
    ]
  }
);

window.SUVYON_GUIDE.apiCatalog = [
  {
    group: "Application root",
    source: src("Root endpoint", "backend/app/main.py", 66),
    endpoints: [
      ["GET", "/ (outside /api/v1)", "Return application name, version, and running status"]
    ]
  },
  {
    group: "Health and model discovery",
    source: src("Health endpoint", "backend/app/api/v1/endpoints/health.py", 11),
    endpoints: [
      ["GET", "/health", "Database-aware API health check"],
      ["GET", "/models", "List models from available configured providers"],
      ["GET", "/models/{provider}", "List one provider's models"]
    ]
  },
  {
    group: "Authentication",
    source: src("Auth routes", "backend/app/api/v1/routes/auth.py", 25),
    endpoints: [
      ["POST", "/auth/register", "Create account and issue verification OTP"],
      ["POST", "/auth/login", "Verify credentials and return access + refresh JWTs"],
      ["POST", "/auth/refresh", "Exchange valid refresh JWT for a new token pair"],
      ["POST", "/auth/logout", "Blacklist current access-token JTI"],
      ["POST", "/auth/change-password", "Verify current password and set a new hash"],
      ["POST", "/auth/deactivate", "Deactivate current account"],
      ["POST", "/auth/verify-email", "Consume verification OTP"],
      ["POST", "/auth/resend-verification", "Rate-limited new verification OTP"],
      ["POST", "/auth/forgot-password", "Issue reset OTP without exposing account existence"],
      ["POST", "/auth/reset-password", "Consume reset OTP and replace password hash"]
    ]
  },
  {
    group: "Current user",
    source: src("User routes", "backend/app/api/v1/routes/users.py", 14),
    endpoints: [
      ["GET", "/users/me", "Return authenticated profile"],
      ["PATCH", "/users/me", "Update profile fields"]
    ]
  },
  {
    group: "Workspaces",
    source: src("Workspace routes", "backend/app/api/v1/routes/workspaces.py", 22),
    endpoints: [
      ["GET", "/workspaces", "List owned workspaces"],
      ["GET", "/workspaces/{workspace_id}", "Get one owned workspace"],
      ["POST", "/workspaces", "Create workspace"],
      ["PATCH", "/workspaces/{workspace_id}", "Update workspace"],
      ["DELETE", "/workspaces/{workspace_id}", "Delete workspace and cascaded children"],
      ["POST", "/workspaces/{workspace_id}/archive", "Archive workspace"],
      ["POST", "/workspaces/{workspace_id}/restore", "Restore workspace"],
      ["POST", "/workspaces/{workspace_id}/favourite", "Favourite workspace"],
      ["DELETE", "/workspaces/{workspace_id}/favourite", "Remove favourite"]
    ]
  },
  {
    group: "Conversations and messages",
    source: src("Conversation routes", "backend/app/api/v1/routes/conversations.py", 60),
    endpoints: [
      ["GET", "/workspaces/{wid}/conversations", "List workspace conversations"],
      ["POST", "/workspaces/{wid}/conversations", "Create conversation with provider/model settings"],
      ["GET", "/workspaces/{wid}/conversations/{cid}", "Get scoped conversation"],
      ["PATCH", "/workspaces/{wid}/conversations/{cid}", "Update title, prompt, provider, model, flags"],
      ["DELETE", "/workspaces/{wid}/conversations/{cid}", "Delete conversation and messages"],
      ["GET", "/workspaces/{wid}/conversations/{cid}/messages", "Read ordered history"],
      ["POST", "/workspaces/{wid}/conversations/{cid}/messages", "Generate and persist ordinary response"],
      ["POST", "/workspaces/{wid}/conversations/{cid}/messages/stream", "Generate SSE response and persist on completion"]
    ]
  },
  {
    group: "Knowledge bases and documents",
    source: src("Knowledge routes", "backend/app/api/v1/routes/knowledge_bases.py", 38),
    endpoints: [
      ["GET", "/workspaces/{wid}/knowledge-bases", "List knowledge bases"],
      ["POST", "/workspaces/{wid}/knowledge-bases", "Create knowledge base"],
      ["GET", "/workspaces/{wid}/knowledge-bases/{kb}", "Get scoped knowledge base"],
      ["PATCH", "/workspaces/{wid}/knowledge-bases/{kb}", "Update metadata or active state"],
      ["DELETE", "/workspaces/{wid}/knowledge-bases/{kb}", "Delete knowledge base and vector chunks"],
      ["GET", "/workspaces/{wid}/documents", "List uploaded documents"],
      ["POST", "/workspaces/{wid}/documents", "Upload and synchronously process document"],
      ["DELETE", "/workspaces/{wid}/documents/{doc}", "Delete metadata, chunks, and local file when present"]
    ]
  },
  {
    group: "Agents",
    source: src("Agent routes", "backend/app/api/v1/routes/agents.py", 34),
    endpoints: [
      ["GET", "/workspaces/{wid}/agents", "List saved agent configurations"],
      ["POST", "/workspaces/{wid}/agents", "Create agent configuration"],
      ["GET", "/workspaces/{wid}/agents/tools", "List registry tool names"],
      ["GET", "/workspaces/{wid}/agents/{aid}", "Get scoped agent"],
      ["PATCH", "/workspaces/{wid}/agents/{aid}", "Update instructions/model/tools/flags"],
      ["DELETE", "/workspaces/{wid}/agents/{aid}", "Delete agent configuration"],
      ["POST", "/workspaces/{wid}/agents/{aid}/run", "Run bounded agent and return JSON"],
      ["POST", "/workspaces/{wid}/agents/{aid}/run/stream", "Resolve tools then stream final answer"]
    ]
  },
  {
    group: "Media proxy",
    source: src("Media route", "backend/app/api/v1/routes/media.py", 16),
    endpoints: [
      ["GET", "/media/image?u=...", "Validate and proxy an allowed Pollinations image URL"]
    ]
  }
];
