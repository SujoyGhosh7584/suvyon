# Interview Questions and Model Answers

Use these as speaking prompts. Give the first sentence, pause, then expand with mechanism, Suvyon evidence, and trade-offs.

## Foundations

1. **What is generative AI?** A class of models that learns a data distribution and produces new content; LLMs generate token sequences conditioned on context.
2. **What does an LLM predict?** A probability distribution over the next token given preceding tokens.
3. **What is self-attention?** A mechanism that lets each token weight and combine information from other tokens using learned query/key/value projections.
4. **Why divide attention scores by `sqrt(d_k)`?** To keep dot-product magnitudes from pushing softmax into saturated, low-gradient regions.
5. **What is a context window?** The maximum combined input/output token capacity of one model call, not permanent memory.
6. **Temperature versus top-p?** Temperature reshapes the full distribution; top-p limits sampling to a cumulative-probability nucleus.
7. **Why do hallucinations occur?** The objective optimizes likely text, not verified truth, and prompts may lack reliable evidence.
8. **How do you reduce hallucinations?** Ground with retrieval/tools, require citations/abstention, validate claims and schemas, and evaluate on representative cases.
9. **Prompting versus fine-tuning?** Prompting changes context per request; fine-tuning updates model parameters to change behavior more persistently.
10. **RAG versus fine-tuning?** RAG is best for inspectable, private, changing facts; fine-tuning is better for stable behavior/style or specialized task patterns.
11. **What is an embedding?** A dense vector representation designed so semantic relationships are reflected by geometric proximity.
12. **Cosine similarity versus Euclidean distance?** Cosine compares direction and ignores magnitude; Euclidean measures absolute geometric distance.
13. **What is quantization?** Lowering weight/activation precision to reduce memory and improve throughput, potentially sacrificing accuracy.
14. **What is LoRA?** Parameter-efficient adaptation using trainable low-rank updates while base model weights remain mostly frozen.
15. **Why validate structured output?** Model-generated JSON can still be malformed or semantically invalid; schemas make the software boundary explicit.

## RAG

16. **Describe a RAG pipeline.** Parse → chunk → embed → index; then embed query → retrieve → optionally rerank → build context → generate → cite/evaluate.
17. **How choose chunk size?** Based on document structure, question granularity, embedding behavior, and measured retrieval/answer quality—not one universal value.
18. **Why overlap chunks?** To preserve facts that cross boundaries, at the cost of storage and duplicate retrieval.
19. **What is hybrid retrieval?** Combining semantic vector search with lexical/BM25 matching, often followed by rank fusion and reranking.
20. **What does a reranker do?** More expensively scores query–candidate pairs after broad retrieval to improve final ordering.
21. **What is recall@k?** Fraction of queries whose relevant evidence appears in the top k retrieved items.
22. **What is MRR?** Mean reciprocal rank of the first relevant result, emphasizing early placement.
23. **What is faithfulness?** Whether answer claims are supported by supplied context, distinct from general factual correctness.
24. **How handle no relevant context?** Apply a calibrated threshold and abstain, ask clarification, or switch to an explicitly labeled alternative source.
25. **Why can top-k fail?** It always returns candidates unless thresholded and may return duplicates, irrelevant nearest neighbors, or one dominant document.
26. **How does Suvyon improve diversity?** It chooses the best chunk per document before filling remaining slots by similarity rank.
27. **Why exact search for small indexes?** Approximate vector indexes can have poor recall or empty results when insufficiently trained/populated; brute-force is cheap at small size.
28. **How prevent cross-tenant RAG leakage?** Enforce authorization and workspace/knowledge-base metadata filters in the database query, not in the prompt.
29. **How update embeddings safely?** Version embedding model/index configuration, build a new index, evaluate it, then atomically switch traffic.
30. **How evaluate RAG?** Measure ingestion, retrieval, generation, citations, latency, and cost separately and end-to-end.

## Agents

31. **What is an AI agent?** A model-controlled loop that selects actions/tools, observes results, updates state, and terminates toward a goal.
32. **Agent versus workflow?** An agent dynamically chooses next actions; a workflow has mostly predefined transitions and is more predictable.
33. **What is tool calling?** The model emits a structured function name and arguments; application code validates and executes it.
34. **Does the LLM execute tools?** No. The orchestrator executes tools and returns observations to the model.
35. **What is ReAct?** A pattern interleaving action decisions with external observations before producing an answer.
36. **How stop infinite loops?** Max steps/time/tokens/cost, detect repeated calls, explicit termination rules, and a fallback synthesis path.
37. **Why are tool descriptions important?** They guide model selection; overlapping or vague descriptions increase wrong calls.
38. **How secure tools?** Validate arguments, authorize per call, apply least privilege, sandbox execution, limit destinations, and require approval for impact.
39. **How make side effects reliable?** Preview/approval, idempotency keys, durable state, audit logs, and compensating operations.
40. **What is human-in-the-loop?** A deliberate pause where a person reviews or authorizes consequential/ambiguous behavior.
41. **How does Suvyon handle email?** It drafts first and gates `send_email` on explicit confirmation, backed by tests.
42. **What is agent memory?** State retained or retrieved across steps/runs; working, episodic, semantic, and procedural memory serve different purposes.
43. **When use multi-agent architecture?** Only when distinct roles, context isolation, or parallel work produce measurable value beyond coordination overhead.
44. **How evaluate agents?** Task success plus trajectory metrics: tool choice, arguments, steps, recoveries, policy adherence, latency, and cost.
45. **What is prompt injection?** Untrusted content attempting to override instructions or induce unsafe actions; treat content as data and enforce controls outside the model.

## Architecture and production

46. **Why a provider abstraction?** It isolates vendor formats/SDKs and lets routing/business logic operate on stable domain types.
47. **What is abstraction leakage here?** Providers differ in tool calling, streaming, errors, context, and safety; the interface must expose capabilities or adapters become brittle.
48. **How does Suvyon route models?** Explicit provider/model takes priority, ownership is validated, defaults/aliases are applied, and failures fall through configured providers.
49. **What routing is missing?** Dynamic health, latency, quality, cost, capacity, circuit-breaker, and request-capability scoring.
50. **Why own conversation state?** It allows switching providers, auditing history, applying retention policies, and recovering independently of vendor sessions.
51. **Why FastAPI?** Typed validation, dependency injection, async support, OpenAPI generation, and a strong Python AI ecosystem.
52. **Why modular monolith?** Lower operational complexity while preserving internal boundaries; split only when scale or team ownership demands it.
53. **Why PostgreSQL + pgvector?** Relational and vector data share transactions, tenant filters, operations, and backups; it is pragmatic before extreme vector scale.
54. **When use a dedicated vector database?** When vector volume/QPS, specialized indexes, geo-distribution, or independent scaling exceeds the database's practical envelope.
55. **How scale ingestion?** Durable object storage, queued idempotent jobs, worker autoscaling, checkpoints/retries, dead-letter queue, and progress states.
56. **How stream safely?** Track cancellation/disconnects, timeouts, partial output semantics, provider pinning, and final persistence/commit behavior.
57. **What is time to first token?** Latency until the first streamed token; it affects perceived responsiveness even when total completion time is unchanged.
58. **How handle provider failure?** Classify errors, retry transient failures with jitter, trip circuit breakers, fall back to compatible providers, and surface honest partial failure.
59. **What should traces include?** Request/run ID, versions, retrieval IDs/scores, model/tool calls, tokens, timing, outcome, with sensitive content redacted.
60. **How manage GenAI cost?** Budgets, smaller-model routing, compact context/tool results, caching where safe, summarization, and measuring cost per successful task.

## Suvyon-specific

61. **What problem does Suvyon solve?** One workspace for provider-independent chat, private-document grounding, live tools, and configured agents.
62. **Trace document upload.** Route/service validate and persist; pipeline parses, chunks, embeds, inserts pgvector rows, and updates document status.
63. **Trace auto chat.** Load history and tool schemas, call routed model, execute requested tools, append observations, synthesize, attach provenance, persist answer.
64. **Explicit RAG versus auto mode?** Explicit RAG forces document grounding; auto mode lets the model decide whether `knowledge_search` or other tools are required.
65. **How are citations handled?** Retrieval/tool sources are gathered and provenance is appended/rendered; citation correctness still needs formal evaluation.
66. **How does model failover preserve context?** Messages use provider-neutral application objects and are resent to the alternate adapter.
67. **How are tools registered?** A central dictionary maps name to function, description, parameters, and required fields, then emits function schemas.
68. **Why cap agent iterations?** To bound cost/latency and prevent repeated tool calls; final synthesis uses tools disabled.
69. **What tests best demonstrate AI reliability?** Model-router ownership/aliases, intent tool selection, agent loop termination, email confirmation, chunking, and RAG diversity tests.
70. **Biggest production gap?** A strong answer can choose async durable ingestion, formal evaluation, or agent/tool security and justify it with expected risk.
71. **Is Suvyon multi-agent?** Not currently in the orchestration sense; it supports multiple saved agent configurations but runs one agent at a time.
72. **Does it use LangGraph?** The dependency may exist in an environment, but current core runner is a custom bounded loop; never infer usage from installed packages.
73. **Does it have long-term memory?** Models exist for memory, but active behavior is primarily persisted conversation history and RAG; avoid overstating unconnected schema.
74. **Why is ephemeral file storage a problem?** Deploy restarts can remove uploaded bodies, breaking reprocessing/audit even if database metadata remains.
75. **Your first three upgrades?** Durable queued ingestion, evaluation/observability, and hardened tool authorization/idempotency; explain priorities by user impact and risk.

## Behavioral and ownership

76. **Tell me about a trade-off.** Use modular monolith or Postgres+pgvector: explain constraints, decision, benefit, downside, and trigger for reconsideration.
77. **Tell me about a failure.** Choose a real test/bug from repository history if you know it; describe symptom, hypothesis, evidence, fix, test, and prevention without inventing details.
78. **How do you learn an unfamiliar AI API?** Start from the provider contract, build a thin adapter, record fixtures, test errors/streaming/tools, then integrate behind abstraction.
79. **How prioritize quality versus latency?** Define task risk and SLOs, measure both, route by use case, and optimize the Pareto frontier rather than one global setting.
80. **What would you do differently?** Introduce evaluation and structured traces earlier, because AI behavior changes across prompts/models even when code types still pass.

