# Detailed RAG and Agent Interview Answers

Use each answer in layers: direct answer, mechanism, production trade-off, and Suvyon evidence. Do not claim that a design idea is already implemented unless the code proves it.

## 1. Design an end-to-end RAG system.

**30-second answer:** I separate RAG into ingestion, retrieval, and generation. Ingestion parses, cleans, chunks, embeds, and indexes documents with permissions and version metadata. At query time I authorize first, retrieve broadly, rerank, build a bounded evidence context, generate with citations and abstention, then log and evaluate every stage.

**Deeper answer:** Uploads go to durable object storage and create an idempotent asynchronous job. Workers scan files, parse structure, normalize text, preserve page/section metadata, chunk, deduplicate, embed in batches, and write a versioned index. States such as queued, parsing, indexing, ready, and failed make recovery visible.

At query time I resolve the user's tenant and ACLs before search. I may rewrite the query, run dense and BM25 retrieval, fuse candidates, and apply a cross-encoder reranker. Context construction removes duplicates, preserves source boundaries, and fits a token budget. The generation prompt treats documents as untrusted data, asks for source-backed answers, and abstains when evidence is insufficient.

I measure retrieval recall@k/MRR/nDCG, answer faithfulness/relevance, citation correctness, p95 latency, and cost. Failures are labeled as ingestion, retrieval, context, or generation failures.

**Suvyon evidence:** inspect `backend/app/rag/pipeline.py`, `retriever.py`, and `vector_store.py`; Suvyon currently provides the core path, while durable queued ingestion and formal evaluation are improvement areas.

## 2. How do you choose chunk size and overlap?

**30-second answer:** I treat chunking as a measured retrieval parameter, not a universal constant. I begin from document structure and expected question granularity, then compare configurations on labeled query-evidence pairs.

**Deeper answer:** Small chunks improve localization and reduce irrelevant context, but can lose surrounding definitions or table headers. Large chunks preserve coherence but dilute embedding signals, consume more tokens, and can retrieve irrelevant text. Overlap protects boundary-spanning facts but increases storage and can fill top-k with duplicates.

I prefer structure-aware splitting by heading, paragraph, table, or code unit, with maximum token limits. I preserve parent/section metadata and may retrieve a small child chunk but expand to its parent for generation. For each candidate strategy I measure retrieval recall, redundancy, faithfulness, context tokens, latency, and cost—not just whether a few demos look good.

**Suvyon evidence:** `backend/app/rag/chunker.py` contains the current policy and `backend/tests/test_chunker.py` defines edge behavior.

## 3. Dense, sparse, hybrid retrieval, and reranking—when do you use each?

**30-second answer:** Dense retrieval is strong for semantic paraphrases; sparse BM25 is strong for exact names, identifiers, and rare terms. Hybrid retrieval combines their candidate sets, and reranking spends more compute to order a smaller set accurately.

**Deeper answer:** Dense search embeds queries and chunks into a shared space, but may blur numbers, negation, or product codes. BM25 relies on lexical overlap and inverse document frequency, so it handles exact terminology but misses paraphrases. I retrieve from both and combine ranks with a robust method such as reciprocal rank fusion because raw scores are not directly comparable. A cross-encoder then reads each query-document pair jointly and reranks perhaps 20–100 candidates before the best few enter the prompt.

**Trade-off:** Hybrid retrieval and reranking usually improve quality but add infrastructure, latency, and cost. I introduce them only after a labeled set shows the simpler baseline's failure modes. Metadata/ACL filters must be applied inside every retrieval path.

## 4. How do you evaluate and debug a RAG system?

**30-second answer:** I first separate retrieval from generation. If the gold evidence is absent, it is a retrieval failure; if evidence is present but the answer is wrong or unsupported, it is a context or generation failure.

**Deeper answer:** I build a dataset of question, acceptable evidence, expected answer or rubric, permissions, and cases where the system should abstain. Retrieval metrics include recall@k, precision@k, MRR, and nDCG. Generation metrics include faithfulness, relevance, completeness, citation correctness, and refusal quality. Operational metrics include ingestion failures, p50/p95 latency, time to first token, tokens, and cost.

For a bad result I inspect: source parsing, chunk boundaries, embedding/version mismatch, query wording, filters, top-k scores, duplicates, reranking, context order/truncation, and the final prompt. I use error categories and compare changes against a fixed baseline. LLM judges can assist, but I calibrate them against human labels.

## 5. How do you prevent data leakage and prompt injection in RAG?

**30-second answer:** Authorization must be enforced in the data query, not requested in a prompt. Retrieved text is untrusted content, so it cannot grant permissions or redefine system instructions.

**Deeper answer:** Every chunk carries tenant, document, ACL, and version metadata. The authenticated identity is resolved server-side and incorporated into the database search predicate. I test cross-tenant and revoked-access cases. Storage, logs, caches, and evaluation traces follow the same isolation and retention rules; cache keys include authorization scope.

For indirect prompt injection, I delimit source content, instruct the model to treat it as evidence rather than commands, minimize tool privileges, validate every tool request outside the model, and require human approval for consequential actions. I can scan or flag suspicious documents, but a classifier is defense-in-depth, not the security boundary. Secrets are never placed in model context, and tool outputs are size-limited and sanitized before reuse.

## 6. How do you update or delete documents safely?

**30-second answer:** I version the document and index artifacts, make ingestion idempotent, build new embeddings without corrupting the active version, and switch atomically after validation. Deletion must remove source objects, chunks, embeddings, caches, and derived artifacts according to policy.

**Deeper answer:** An ingestion job uses a stable document/version key and content hash to prevent duplicate work. New versions are written separately and marked ready only when parsing and indexing finish. Readers use the active version pointer, so partial jobs are invisible. For a new embedding model, I create a parallel index, evaluate it on a fixed set, and cut over with rollback available.

Deletion is an auditable workflow rather than a single SQL statement. It propagates to vector rows, object storage, lexical indexes, cached answers, and backups according to retention rules. ACL changes should invalidate access immediately even if physical deletion is asynchronous.

## 7. What is an AI agent, and when should you not use one?

**30-second answer:** An agent is a bounded loop where a model chooses actions, observes tool results, updates state, and decides when to finish. I use it when the next step depends on runtime information and cannot be modeled cheaply as a fixed workflow. I avoid it when deterministic logic is sufficient.

**Deeper answer:** The orchestrator—not the LLM—owns the loop. It supplies instructions and tool schemas, validates the model's structured request, authorizes and executes the tool, appends the observation, and calls the model again. It enforces limits on steps, time, tokens, cost, repeated actions, and side effects.

A workflow is preferable for stable business processes, strict compliance paths, or high-volume operations where predictability matters. Agent flexibility brings nondeterminism, harder testing, longer tail latency, and new security risks. Often the best design is a deterministic state machine with model decisions only at narrow ambiguous nodes.

**Suvyon evidence:** `backend/app/agents/runner.py` implements a custom bounded tool loop. It is not evidence of LangGraph or multi-agent orchestration.

## 8. Explain tool calling end to end.

**30-second answer:** The application sends tool names, descriptions, and argument schemas to the model. The model returns a structured tool request. Application code validates, authorizes, executes, and records it, then sends the result back to the model for the next decision or final response.

**Deeper answer:** Good schemas use narrow names, unambiguous descriptions, enums and bounds, and separate read from write actions. Arguments are treated as untrusted input and validated with typed models. Authorization uses the real user identity and resource, not the model's claim. Execution has timeouts, retries only when safe, output-size limits, audit logs, and redaction.

For side effects I use preview/approval and idempotency keys. The model should never be trusted to assert that an action occurred; the orchestrator records the actual result. Tool errors become structured observations, allowing retry, alternative action, clarification, or honest failure.

**Suvyon evidence:** schemas and callable mappings live in `backend/app/tools/registry.py`; execution logic is in `backend/app/agents/runner.py`.

## 9. How do you prevent infinite loops and control agent cost?

**30-second answer:** I enforce hard budgets for steps, wall time, tokens, and cost; detect repeated or cyclic tool calls; define explicit terminal states; and return a safe partial result when limits are reached.

**Deeper answer:** I canonicalize each tool name and validated argument set to create a call signature. Repeated identical signatures without new state are blocked or escalated. The state machine tracks attempts and distinguishes retryable infrastructure errors from permanent validation or authorization errors. Network retries use bounded exponential backoff with jitter and respect overall deadlines.

I limit tool-result size, summarize only when evidence preservation is acceptable, route simple steps to smaller models, and expose remaining budget to the policy. Final synthesis can run with tools disabled so the model cannot restart the loop.

**Evaluation:** include adversarial trajectories: a tool always fails, the model repeats a call, two tools bounce state, a result contains injection text, or no terminal answer is possible.

## 10. State, memory, and checkpoints—what is the difference?

**30-second answer:** State is the current run's explicit data. Memory is selected information retained or retrieved across steps or runs. A checkpoint is a durable snapshot that lets execution resume, replay, or wait for human input.

**Deeper answer:** Working state can include messages, tool results, plan, permissions, budget, and current node. Episodic memory stores past events; semantic memory stores extracted facts; procedural memory stores stable instructions or learned procedures. Persisting every conversation verbatim is not automatically useful memory—it may be noisy, stale, sensitive, or too large.

Memory writes need provenance, user scope, consent/retention, deduplication, and update/delete semantics. Retrieval should be relevance- and permission-aware. Checkpoints record deterministic state at safe boundaries, especially before and after side effects, so retries do not duplicate an action.

**Trade-off:** More memory can personalize results but raises privacy, relevance, poisoning, and cost risks.

## 11. How do you make an email or payment agent safe?

**30-second answer:** I separate preparation from execution. The agent can draft or preview freely, but a consequential action requires explicit user approval of the exact target and content, fresh authorization, an idempotency key, and an auditable executor.

**Deeper answer:** The workflow captures intent, produces a structured preview, validates recipient/account, amount or content, then enters an `awaiting_approval` state. Approval is bound to a hash of the exact action and expires. Any material edit invalidates it. The executor checks permissions again, performs the call once, records provider response IDs, and returns verified status. Retries use the same idempotency key; ambiguous timeouts are reconciled with the provider before retrying.

Limits, allowlists, anomaly detection, and step-up authentication depend on risk. The LLM never handles secrets or bypasses policy. A compensating operation may exist, but it is not a substitute for pre-action control.

**Suvyon evidence:** `backend/tests/test_agent_runner.py` and `backend/tests/test_email_tools.py` test explicit confirmation before `send_email`.

## 12. Single-agent versus multi-agent architecture?

**30-second answer:** I begin with one agent or workflow. Multiple agents are justified when specialization, context isolation, ownership boundaries, or genuinely parallel independent work produce measured gains greater than coordination overhead.

**Deeper answer:** Common patterns include supervisor-and-workers, handoffs, map-reduce, and debate. They add message passing, duplicated context, conflicting outputs, harder termination, more latency and cost, and more complex evaluation. A “researcher” and “writer” prompt does not require separate agents if two deterministic stages work.

I evaluate multi-agent designs against a single-agent baseline using task success, unique useful work, error recovery, steps, tokens, latency, and policy adherence. Shared state must have clear ownership and merge rules; permissions should be per agent/tool; every handoff needs provenance.

**Suvyon accuracy:** it supports multiple saved agent configurations but runs one selected agent at a time. Calling it a multi-agent orchestration platform would overstate the implementation.

## 13. What is MCP, and how is it different from function calling?

**30-second answer:** Function calling is a model/API mechanism for emitting structured calls. MCP is an interoperability protocol through which hosts discover and use server-provided tools, resources, and prompts. An MCP tool may still be presented to an LLM through function calling.

**Deeper answer:** MCP standardizes the boundary between a host application, MCP client, and server, including capability discovery and transport. It reduces bespoke integrations, but does not eliminate authorization or trust decisions. The host must decide which servers and capabilities a user may access, constrain credentials, validate tool inputs/outputs, and defend against malicious descriptions or returned content.

I would use MCP when interoperability across clients/data systems is valuable. For three stable internal functions, a local registry may be simpler. Migrating Suvyon's registry would be justified by reuse or ecosystem access, not by the protocol name alone.

## 14. How do you evaluate an agent?

**30-second answer:** I evaluate both final task success and the trajectory used to reach it. A correct final sentence is not enough if the agent used an unauthorized tool, fabricated success, or spent ten times the budget.

**Deeper answer:** Cases include normal goals, ambiguous requests, malformed arguments, tool errors, repeated calls, permission denial, prompt injection in observations, and side-effect approval. Deterministic assertions check selected tool, schema validity, call order, budgets, citations, and forbidden actions. Rubrics or calibrated judges assess answer usefulness and recovery quality.

I record prompt/model/tool versions, state transitions, arguments, redacted observations, tokens, latency, cost, and outcome. Offline replay catches regressions; shadow/canary deployment measures real behavior. The release threshold is risk-based: a small relevance regression may be acceptable, but an authorization regression is a hard stop.
