# GenAI project roadmap for stronger applications

Do not add these projects to the resume until each feature can be demonstrated, explained, and defended. Suvyon already proves broad end-to-end development; the next projects should close specific market gaps rather than duplicate another chatbot.

## Priority 1: Enterprise RAG with RBAC, Evaluation, Monitoring, and Guardrails

Upgrade the existing **RAG-RBAC with Monitoring and Guardrails** project into the second resume project.

### Recommended capabilities

- Enforce document- and chunk-level access at retrieval time using tenant, role, and group metadata filters.
- Combine dense vector retrieval with BM25 hybrid search and a reranking stage.
- Build a labeled evaluation dataset and report retrieval recall@k, MRR/nDCG, groundedness, faithfulness, answer relevance, latency, and cost.
- Add prompt-injection detection, PII redaction, source allowlists, output validation, and refusal behavior.
- Trace ingestion, retrieval, reranking, model calls, guardrail decisions, latency, tokens, and cost with OpenTelemetry plus Langfuse, Phoenix, or LangSmith.
- Package the API with Docker and add GitHub Actions for tests, linting, security checks, and deployment.
- Create a threat model, architecture diagram, benchmark report, live demo, and concise README.

### Suggested stack

Python, FastAPI, LangGraph or LlamaIndex, PostgreSQL/pgvector, OpenSearch or rank-bm25, cross-encoder reranker, Ragas or DeepEval, OpenTelemetry, Langfuse/Phoenix, Docker, GitHub Actions, and Azure.

### Resume bullet template after completion

- Built a multi-tenant enterprise RAG service with retrieval-time RBAC, hybrid search, reranking, prompt-injection defenses, and PII controls; evaluated retrieval and answer quality on **[N] labeled questions**, improving **[metric] from X to Y** while maintaining **[latency]**.

## Priority 2: Stateful Agentic Workflow for Enterprise Operations

Build one narrow, realistic workflow instead of a generic collection of agents. A strong example is an incident-resolution or service-request copilot.

### Recommended capabilities

- Use LangGraph for planner, retriever, executor, validator, and human-approval nodes.
- Integrate tools through MCP or typed APIs for ticket lookup, knowledge retrieval, change proposal, and notification drafting.
- Add durable checkpoints, retries, idempotency keys, time/token budgets, cancellation, and resumable human approval.
- Evaluate task completion, tool-selection accuracy, trajectory validity, safety violations, latency, and cost on a fixed test set.
- Add least-privilege authorization, audit logs, prompt/version tracking, and distributed traces.
- Deploy the FastAPI service using Docker and Azure, with CI/CD and operational dashboards.

### Suggested stack

Python, FastAPI, LangGraph, MCP, PostgreSQL, Redis, Azure AI Foundry or Azure OpenAI, OpenTelemetry, Docker, GitHub Actions, and React.

### Resume bullet template after completion

- Developed a stateful enterprise operations agent using LangGraph and MCP with durable checkpoints, typed tools, human approval, and trace-based evaluation; achieved **[X% task completion]** across **[N scenarios]** with **[zero/N] unauthorized side effects**.

## Optional Priority 3: Secure Text-to-SQL Analytics Agent

Build this only after the first two are complete.

- Add schema retrieval, business glossary grounding, SQL generation, static validation, read-only execution, row-level security, query timeouts, and result explanation.
- Evaluate execution accuracy, semantic correctness, unsafe-query rejection, latency, and cost on a versioned benchmark.
- Demonstrate defenses against prompt injection, data exfiltration, cross-tenant access, and expensive queries.

## What to measure before adding any project to the resume

- Dataset size and composition.
- Baseline versus final retrieval or task metrics.
- P50/P95 latency and token/cost per request.
- Test count and coverage of critical paths.
- Safety and authorization test results.
- Deployment architecture and observed uptime only after enough monitoring time.

Never invent users, accuracy, savings, latency, or business impact. A smaller measured result is stronger than a large number that cannot survive interview follow-up.
