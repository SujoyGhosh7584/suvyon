# Advanced GenAI Interview Questions and Answers

Use this bank after the foundation, RAG, agent, and production guides. Practice every answer in three forms: a 30-second summary, a two-minute explanation, and a whiteboard design with trade-offs. Do not memorize wording; memorize the reasoning structure.

## Model architecture and training

### 1. Why did Transformers replace recurrent networks for most language-model workloads?

Transformers process tokens in parallel during training and use attention to connect distant tokens without carrying information through every intermediate timestep. This improves optimization and hardware utilization. The trade-off is that standard self-attention requires quadratic work and memory in sequence length, so long contexts need careful kernels, sparse/sliding-window attention, retrieval, or other optimizations.

### 2. Explain scaled dot-product attention.

Queries represent what each position is looking for, keys represent what each position offers, and values contain the information to aggregate. The operation is `softmax(QK^T / sqrt(d_k))V`. Scaling prevents dot products from growing too large as the key dimension increases; the softmax creates normalized relevance weights. Multi-head attention repeats this in different learned subspaces so the model can capture different relationships.

### 3. What is the difference between encoder-only, decoder-only, and encoder-decoder models?

Encoder-only models use bidirectional context and are strong for embeddings, classification, and token labeling. Decoder-only models use causal attention and are optimized for open-ended generation. Encoder-decoder models separately encode an input and autoregressively decode an output, which is useful for translation and transformation tasks. Choose based on the workload, latency, and training ecosystem rather than assuming one architecture wins everywhere.

### 4. What do positional encodings solve?

Attention alone is permutation-invariant, so the model needs a signal for token order. Absolute embeddings attach a position to a token; relative schemes encode token-to-token distance; rotary position embeddings rotate query and key features so relative offsets appear naturally in attention. Position handling affects length extrapolation, but a larger advertised context window does not guarantee that the model uses all positions equally well.

### 5. What are residual connections, normalization, and the MLP block doing?

Residual paths preserve an easy route for information and gradients across deep networks. Normalization stabilizes activation scale. The feed-forward or MLP block transforms each position independently and holds much of the model's parameter capacity. An interview-quality answer should connect each component to optimization stability and information flow, not only define it.

### 6. What is a mixture-of-experts model?

A router selects a small subset of expert feed-forward networks for each token. This increases total parameter capacity without activating every parameter per token. The benefits are compute-efficient scaling and specialization; the costs include routing instability, expert imbalance, communication overhead, larger memory requirements, and more complicated serving.

### 7. What is the difference between pretraining, instruction tuning, and preference optimization?

Pretraining learns next-token prediction from a broad corpus. Supervised instruction tuning teaches the model to follow prompt-response patterns. Preference optimization then shifts behavior toward outputs preferred by people or synthetic judges. RLHF typically trains a reward model and optimizes against it; DPO directly learns from preferred/rejected response pairs with a reference policy, which is simpler operationally but still depends on preference-data quality.

### 8. When would you choose full fine-tuning, LoRA, QLoRA, or prompting?

Start with prompting when behavior can be expressed in instructions. Add retrieval for changing or private knowledge. Use LoRA when repeatable domain behavior or style needs adaptation at lower cost; QLoRA reduces memory further by training adapters over a quantized base. Full fine-tuning is justified when the quality gain is measured, sufficient high-quality data exists, and the operational cost is acceptable. Fine-tuning is not a reliable replacement for frequently changing facts.

### 9. What is catastrophic forgetting, and how do you reduce it?

It is the loss of general capabilities when adapting too aggressively to a narrow dataset. Reduce it with smaller learning rates, parameter-efficient tuning, mixed general/domain training data, regularization, replay, checkpoint evaluation, and explicit regression suites for capabilities that must be preserved.

### 10. How do tokenizers affect a GenAI product?

Tokenization changes cost, latency, context usage, multilingual quality, and how code or unusual terms are represented. A domain with fragmented identifiers can consume far more tokens than plain English. Measure token distributions on real inputs, enforce limits by tokens rather than characters, and never assume equal character counts imply equal model cost.

## Inference and performance

### 11. Explain prefill, decode, time to first token, and inter-token latency.

Prefill processes the complete input prompt in parallel and builds the key-value cache; it is often compute-heavy. Decode generates one token at a time using that cache and is often memory-bandwidth-bound. Time to first token includes queueing plus prefill, while inter-token latency describes streaming speed after generation begins. Optimize and monitor them separately.

### 12. What is a KV cache, and why can it become a bottleneck?

The cache stores attention keys and values for prior tokens so they are not recomputed for every new token. Its memory grows with concurrent requests, sequence length, layers, heads, and precision. Long contexts can therefore reduce concurrency even if model weights fit. Prefix caching, paged memory management, grouped-query attention, quantization, and context limits can reduce pressure.

### 13. What problem does FlashAttention solve?

It reorganizes exact attention computation to reduce expensive transfers between GPU high-bandwidth memory and faster on-chip memory. It does not change the attention result conceptually; it improves IO efficiency through tiling and recomputation. The lesson is that wall-clock performance depends on memory movement as well as FLOPs.

### 14. What problem does PagedAttention solve?

PagedAttention stores KV-cache blocks in a non-contiguous, virtual-memory-like layout. This reduces fragmentation and enables sharing, improving batching and serving throughput under variable-length requests. It is a serving memory-management technique, not a new model-training objective.

### 15. Continuous batching versus static batching?

Static batching waits for a batch and completes it together, which wastes capacity when generations end at different times. Continuous batching admits and retires sequences between decoding steps, improving GPU utilization and throughput. The trade-off is more scheduling complexity and the need to protect latency-sensitive tenants from large jobs.

### 16. What is speculative decoding?

A smaller draft model proposes several tokens, and the target model verifies them in parallel while preserving the target distribution under the correct algorithm. It reduces latency when draft acceptance is high. Gains depend on model compatibility, request shape, hardware, and verification overhead, so benchmark it on production traffic.

### 17. What are the trade-offs of quantization?

Lower-precision weights reduce memory, bandwidth, and often latency, enabling larger models on the same hardware. The risks are quality regressions, sensitivity in particular layers or tasks, kernel availability, and calibration complexity. Evaluate by slice—languages, code, structured output, tool use—not only with a single aggregate score.

### 18. How would you reduce GenAI latency without immediately switching models?

Measure queue, retrieval, prefill, decode, tool, and network time. Then shorten prompts, trim retrieved context, cache reusable prefixes and retrieval results, stream output, parallelize independent tools, tune batch scheduling, cap unneeded output, use efficient attention/serving, and place services near dependencies. Preserve quality with before-and-after evals.

## Retrieval and knowledge systems

### 19. Why does RAG fail even when the answer exists in the corpus?

The document may be parsed badly, chunk boundaries may separate the evidence, embeddings may not represent the query, metadata filters may exclude it, approximate search may miss it, or reranking may select the wrong passages. The generator can also ignore good evidence. Diagnose retrieval recall first, then context construction, then generation faithfulness.

### 20. Dense, sparse, hybrid retrieval, and reranking—when do they help?

Dense retrieval captures semantic similarity. Sparse retrieval is strong for exact terms, identifiers, and rare names. Hybrid retrieval combines both candidate sets. A reranker applies a more expensive relevance model to a small candidate pool. A common robust pipeline is hybrid recall followed by reranking, with weights and cutoffs tuned on labeled queries.

### 21. How do you choose a chunking strategy?

Match chunks to how users ask questions and how answers are supported. Preserve semantic boundaries, keep useful headings and metadata, add controlled overlap when relationships cross boundaries, and avoid chunks so large that irrelevant text dilutes attention. Evaluate chunking with retrieval recall and end-to-end answer metrics rather than selecting a size by intuition.

### 22. What is query rewriting, and when can it hurt?

It transforms an ambiguous or conversational request into one or more retrieval-friendly queries. It helps with follow-up references, synonyms, decomposition, and acronym expansion. It can hurt by changing intent or removing critical constraints, so retain the original query, log rewrites, limit fan-out, and evaluate both retrieval gain and semantic drift.

### 23. How would you design multi-hop RAG?

Decompose the question into dependent subquestions, retrieve evidence for each, maintain citations and intermediate entities, and synthesize only after the evidence graph is sufficient. Set hop and cost limits, detect repeated queries, and expose uncertainty. Compare this against a simpler single-pass baseline because decomposition adds latency and new failure modes.

### 24. When should you use a knowledge graph or GraphRAG-style approach?

Use graph structure when relationships, paths, communities, and entity disambiguation are central—for example ownership chains or dependency impact. It is less useful when questions are mostly local semantic lookup. Graph extraction introduces schema, entity-resolution, freshness, and operational costs, so prove that graph-aware retrieval improves the target question set.

### 25. Long context or RAG?

Long context simplifies some tasks and preserves global relationships, but it increases prefill cost and may suffer position-dependent retrieval quality. RAG is cheaper for large, changing corpora and gives explicit evidence boundaries, but retrieval can miss facts. A production system often uses RAG to select evidence and a moderate context window to reason over it.

### 26. How do you make RAG citations trustworthy?

Store stable source identifiers and offsets during ingestion, attach them to retrieved passages, and require the answer to map claims to supplied evidence. Validate that citations actually entail claims instead of merely appearing relevant. Treat citation rendering separately from citation correctness, and test permissions before retrieval so a citation never leaks an inaccessible source.

## Agents, tools, and protocols

### 27. When is an agent unnecessary?

If the steps are known in advance, a deterministic workflow is easier to test, cheaper, faster, and safer. Use an agent only when the system must choose tools or adapt a plan based on intermediate results. Even then, keep deterministic boundaries around permissions, budgets, schemas, and irreversible actions.

### 28. What separates an agent from ordinary function calling?

Function calling produces a structured tool request. An agent adds a control loop that observes results, updates state, decides the next action, handles failure, and stops under defined conditions. The difficult engineering work is the loop policy, state management, authorization, observability, and termination—not the function-call syntax.

### 29. How do you prevent an agent from looping or overspending?

Use maximum step, time, token, and monetary budgets; detect repeated states and identical tool calls; require progress signals; impose tool-specific timeouts; and define explicit success and failure conditions. Persist a trace that explains why the agent continued or stopped. For high-impact actions, require confirmation even if budget remains.

### 30. What is MCP, and what does it not solve?

The Model Context Protocol standardizes how hosts, clients, and servers expose tools, resources, and prompts. It can reduce one-off integration work and improve portability. It does not automatically provide trust, least privilege, prompt-injection defense, correct tool behavior, or business authorization; the host still needs consent, validation, isolation, and audit controls.

### 31. How should tool calls be secured?

Allowlist tools and arguments, validate every generated payload against a schema, bind permissions to the authenticated user, isolate credentials, and separate read from write capabilities. Treat tool output as untrusted data, use idempotency keys for retryable writes, require approval for consequential actions, and log the decision without exposing secrets.

### 32. How do you design agent memory?

Separate working state for the current run, conversational history, user preferences, and durable knowledge. Give each type a retention policy, source, scope, and deletion mechanism. Summarize with provenance, retrieve only relevant memories, protect cross-tenant boundaries, and avoid storing speculative model output as fact.

## Evaluation, safety, and operations

### 33. What makes a useful GenAI evaluation suite?

It represents real tasks and important failure slices, has clear grading criteria, records versions of prompts/models/data, and supports regression comparison. Include deterministic checks where possible, semantic graders where necessary, human calibration for subjective cases, and production feedback. A single benchmark score is not a release gate.

### 34. How would you evaluate RAG end to end?

Evaluate retrieval recall at `k`, ranking quality, context precision, answer correctness, groundedness, citation validity, refusal when evidence is absent, latency, and cost. Slice by document type, language, query class, freshness, and permissions. End-to-end accuracy without retrieval diagnostics makes failures hard to repair.

### 35. Can an LLM be used as a judge?

Yes, especially for scalable pairwise or rubric-based review, but it can have position, verbosity, style, and self-preference biases. Use a precise rubric, randomize ordering, require evidence, calibrate against expert human labels, measure agreement, and keep deterministic graders for properties such as JSON validity or exact citations.

### 36. Offline evaluation versus online experimentation?

Offline evaluation is fast, repeatable, and safe for regressions but may not reflect real behavior. Online A/B or interleaving tests measure user outcomes but are noisy and expose users to variants. Use offline gates first, then guarded online experiments with quality, safety, latency, and cost metrics.

### 37. How do you detect model or retrieval drift?

Track input distributions, token counts, retrieval scores, selected sources, answer metrics, refusal patterns, latency, cost, and user feedback over time. Run a fixed canary set on every model, prompt, embedding, index, or parser change. Alert on slice-level movement and retain enough version metadata to reproduce a response.

### 38. What is prompt injection, and why is it not solved by a system prompt?

Prompt injection is untrusted content attempting to change the model's instructions or induce unsafe actions. A system prompt is still interpreted by the same model and cannot enforce authorization. Mitigate with data/instruction separation, least-privilege tools, output validation, content provenance, confirmation boundaries, sandboxing, and controls outside the model.

### 39. How do you handle secrets and user-supplied API keys?

Accept keys over authenticated encrypted transport, encrypt them at rest with a server-held master key or managed key service, mask them in UI and logs, and decrypt only immediately before provider use. Never send raw secrets back to the client after storage. Support replacement and deletion, isolate tenants, redact errors, rotate encryption keys, and document that provider-side usage charges remain the user's responsibility.

### 40. What should be in an LLM production trace?

Record a correlation ID, tenant and user authorization context, model/provider and version, prompt-template version, safe token counts, retrieval/query metadata, source IDs, tool names and timings, retries, guardrail decisions, output schema status, latency breakdown, and cost. Do not log raw secrets or sensitive content by default; use redaction and access-controlled sampling.

## Multimodal and image generation

### 41. How is a multimodal model different from a text-only LLM?

It represents one or more additional modalities—such as image or audio—and aligns them with the language model through modality encoders, projectors, cross-attention, or unified tokenization. The design must address resolution, temporal sampling, grounding, modality-specific hallucinations, accessibility, and much larger input payloads.

### 42. How do diffusion image models generate an image?

Training teaches a network to reverse a gradual noising process, typically in a compressed latent space. At inference, the system starts from noise and iteratively denoises while conditioning on the prompt and optional image/control inputs. The sampling steps, guidance, scheduler, resolution, and seed affect quality, diversity, and latency.

### 43. How would you optimize image generation and display in a web application?

Run generation asynchronously, return job progress, constrain unsupported dimensions, and store the original artifact plus display derivatives. Show a responsive preview with preserved aspect ratio, allow a full-screen or lightbox view, and offer the original for download. Use thumbnails in history, lazy-load large assets, avoid base64 payloads in JSON when object storage URLs are appropriate, and clean up failed or abandoned jobs.

### 44. How do you evaluate an image-generation feature?

Combine prompt adherence, visual quality, text rendering where relevant, identity or style consistency when authorized, diversity, safety, latency, failure rate, and user preference. Automated embedding or aesthetic scores are supporting signals, not complete judgments. Maintain challenging prompt suites and human review calibrated to the product's use cases.

## System design and coding

### 45. Design a multi-provider LLM gateway.

Expose one normalized request contract, then adapt it to provider-specific authentication, model names, streaming formats, errors, rate limits, and capabilities. Resolve credentials per user without logging them, validate that the selected model belongs to the selected provider, and implement bounded retries only for safe transient failures. Track latency, cost, availability, and quality by provider/model, but require user consent before failover that could change billing or data handling.

### 46. How would you serve high traffic with unpredictable prompt lengths?

Classify requests by size and priority, enforce token and concurrency quotas, use admission control, continuous batching, separate latency-sensitive from batch queues, and stream responses. Autoscale on queue depth and token throughput rather than request count alone. Apply backpressure and return actionable retry information instead of allowing cascading timeouts.

### 47. How would you design a semantic cache?

Normalize the request, retrieve nearby cached queries using an embedding, and reuse an answer only when similarity, tenant scope, model/prompt version, freshness, permissions, and generation settings are compatible. Exact caching is safer; semantic caching needs a conservative threshold and task-specific correctness tests. Never share private responses across users merely because queries look similar.

### 48. What coding exercises should a GenAI engineer expect?

Expect text chunking with overlap and metadata, cosine similarity and top-k retrieval, an async streaming endpoint, exponential backoff with jitter, JSON-schema validation, a token-aware rate limiter, bounded parallel tool execution, and evaluation metric aggregation. Explain complexity, failure behavior, security boundaries, and tests while coding.

### 49. How would you implement reliable structured output?

Prefer provider-supported schema-constrained generation when available. Define a strict schema, validate server-side, distinguish syntax errors from semantic errors, and retry with a bounded repair path only when safe. Do not execute a tool merely because JSON parsed; authorize the operation and validate business rules separately.

### 50. What is your process when a GenAI system's quality suddenly drops?

Freeze uncontrolled changes and compare versions of model, prompt, retrieval index, embedding model, parser, tools, and dependencies. Reproduce failures from traces, determine whether the issue is input drift, retrieval, generation, safety filtering, or infrastructure, and inspect slice-level evals. Roll back or route around the responsible change, then add the incident cases to regression tests.

## Project and behavioral answers

### 51. How should you present a GenAI project?

Use: user problem, constraints, architecture, your decisions, one difficult trade-off, evaluation evidence, production safeguards, measured result, failure or incident, and the next improvement. Be explicit about what you personally implemented. Interviewers trust quantified limitations more than unqualified claims.

### 52. How do you answer a question when you do not know the exact detail?

State what you know, identify the missing assumption, reason from first principles, and propose how you would verify it. For example: “I have not implemented that kernel, but its goal is to reduce attention IO; I would confirm hardware and framework support, then benchmark latency and memory against the current path.” Do not invent API names or benchmark numbers.

### 53. What trade-off story should you prepare from Suvyon?

Prepare at least three: deterministic workflow versus agent autonomy, retrieval quality versus latency/cost, and provider flexibility versus credential/security complexity. For each, explain the initial constraint, alternatives considered, measured signal, selected design, failure mode, and what would cause you to revisit the choice.

### 54. What should your final answer to “Why should we hire you for GenAI?” contain?

Connect breadth to proof: model and retrieval fundamentals, production engineering, evaluation and safety, and one shipped system you can defend deeply. Explain how you convert uncertain model behavior into measurable product behavior through tests, observability, fallbacks, and explicit trade-offs. Keep it specific to the role and supported by examples.

## Rapid-fire distinctions

- **Temperature vs top-p:** temperature rescales logits; top-p samples from the smallest token set reaching a cumulative probability threshold.
- **Embedding vs reranker:** an embedding enables scalable candidate recall; a reranker scores query-document pairs more precisely at higher cost.
- **Hallucination vs stale knowledge:** hallucination is unsupported generation; stale knowledge may have once been correct but is no longer current.
- **Guardrail vs authorization:** a guardrail classifies or transforms content; authorization decides whether an authenticated actor may perform an action.
- **Retry vs fallback:** retry repeats an operation, usually after a transient failure; fallback changes model, provider, data path, or behavior.
- **Context window vs output limit:** the context window bounds input plus generated tokens; an output limit caps generation within that budget.
- **Data parallel vs tensor parallel:** data parallel replicas process different batches; tensor parallelism splits model operations across devices.
- **Distillation vs quantization:** distillation trains a smaller model to imitate behavior; quantization stores or computes an existing model at lower precision.
- **Calibration vs accuracy:** accuracy measures correctness; calibration measures whether confidence matches the observed likelihood of correctness.
- **Workflow vs agent:** a workflow follows predefined control flow; an agent selects actions dynamically within enforced boundaries.

## Strong-answer checklist

For every technical answer, include as many of these as the question supports:

1. A one-sentence definition.
2. The mechanism or data flow.
3. When you would use it.
4. A meaningful trade-off or failure mode.
5. How you would measure it.
6. A concrete example from Suvyon or another project.

