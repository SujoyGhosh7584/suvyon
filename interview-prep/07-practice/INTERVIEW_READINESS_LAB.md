# GenAI Interview Readiness Lab

This is the execution plan for converting the guides into interview performance. It does not promise every interviewer will ask the same questions; it prepares you to reason clearly across fundamentals, coding, RAG, agents, multimodal systems, evaluation, safety, system design, and your own project.

## 1. The three answer modes

Practice each important topic in all three formats:

### 30-second answer

Use: definition, one use case, one trade-off.

> “RAG retrieves external evidence and supplies it to the model at inference time. I use it for private or changing knowledge where citations and freshness matter. Its main failure mode is retrieval quality, so I measure recall and grounded answer quality separately.”

### Two-minute answer

Use: definition, mechanism, decision criteria, trade-off, measurement, project example.

### Whiteboard answer

Use: requirements, scale, data flow, components, failure paths, security, evaluation, cost, and explicit alternatives. State assumptions before drawing.

## 2. Daily practice loop

Run this 90-minute loop during the sprint:

1. **Recall — 15 minutes:** answer ten questions without notes.
2. **Deep explanation — 20 minutes:** teach one topic aloud from first principles.
3. **Coding — 20 minutes:** solve one bounded exercise and explain tests and complexity.
4. **System design — 25 minutes:** draw one subsystem and defend two trade-offs.
5. **Review — 10 minutes:** score yourself, write missing evidence, and schedule weak topics again.

Record audio or video at least every third day. Filler words, vague claims, and missing conclusions are easier to detect in playback.

## 3. Twenty-one-day readiness sprint

| Day | Primary topic | Proof to produce |
|---|---|---|
| 1 | Neural-network and Transformer foundations | Explain attention and architecture families from memory |
| 2 | Tokenization, embeddings, context, decoding | Compare settings using concrete failure cases |
| 3 | Pretraining, SFT, RLHF, DPO | Draw the training lifecycle and selection criteria |
| 4 | LoRA, QLoRA, quantization, distillation, MoE | Make a deployment decision table |
| 5 | Inference: prefill, decode, KV cache | Diagnose a latency and memory scenario |
| 6 | FlashAttention, batching, PagedAttention, speculative decoding | Give a two-minute explanation of each |
| 7 | Mock foundation round | Score and repair the weakest five answers |
| 8 | RAG ingestion, chunking, metadata | Design an ingestion pipeline with versioning |
| 9 | Dense/sparse/hybrid retrieval and reranking | Implement top-k retrieval and evaluate recall |
| 10 | Advanced RAG: rewrite, multi-hop, graph, citations | Diagnose five retrieval failures |
| 11 | Agents, workflows, tools, memory, MCP | Design bounded agent control flow |
| 12 | Tool security, injection, authorization | Threat-model an agent with write access |
| 13 | Evaluation: datasets, graders, online testing | Define a release gate for one Suvyon flow |
| 14 | Mock RAG/agent/LLMOps round | Produce a written scorecard and fixes |
| 15 | Multimodal and image generation | Design generation, storage, preview, and full-size display |
| 16 | APIs, async Python, streaming, queues | Implement one timed coding exercise |
| 17 | Scaling, reliability, observability, cost | Design a high-traffic model gateway |
| 18 | Suvyon architecture and BYOK security | Deliver the project walkthrough in five minutes |
| 19 | Behavioral and incident stories | Prepare six evidence-backed STAR stories |
| 20 | Full interview loop | Foundation, coding, design, project, behavioral rounds |
| 21 | Gap repair and final gate | Pass the readiness checklist below |

If time is limited, compress this into seven days by combining each three consecutive days, but do not skip the two mock rounds or final gate.

## 4. Coding lab

Complete these without copying production code. Use Python unless the role specifies another language.

### Core exercises

1. Implement cosine similarity and top-k selection, including zero vectors.
2. Chunk text with overlap while preserving document ID, section, and offsets.
3. Build an async generator that streams model tokens and handles cancellation.
4. Implement exponential backoff with jitter and a retryable-error allowlist.
5. Validate a model-produced object against a strict schema and return typed errors.
6. Build a per-user token-bucket rate limiter.
7. Execute independent tool calls with bounded concurrency and individual timeouts.
8. Compute retrieval recall@k, MRR, pass rate, confidence intervals, and slice summaries.
9. Implement a small exact cache whose key includes model, prompt version, and tenant scope.
10. Parse server-sent events without assuming each network chunk contains one complete event.

### What to say while coding

- Clarify input size and malformed-input behavior.
- Name time and space complexity.
- Separate pure logic from IO.
- Cover cancellation, timeout, and retry behavior.
- Add tests for empty, large, duplicate, unauthorized, and partial inputs.
- Never log secrets or execute generated content merely because it parsed.

## 5. System-design drills

For each prompt, spend five minutes clarifying, twenty minutes designing, and ten minutes challenging the design.

1. Enterprise RAG over millions of permissioned documents.
2. Multi-provider BYOK chat with model discovery and streaming.
3. Research agent using search, files, code execution, and citations.
4. Support copilot that drafts but cannot send messages without approval.
5. Image-generation product with moderation, job queues, variants, and original files.
6. Evaluation platform that compares prompts and models on fixed and live datasets.
7. Realtime voice agent handling interruptions and tool calls.
8. Coding agent with repository isolation and an auditable edit/test loop.

### Design checklist

- Functional and non-functional requirements.
- Traffic, data size, latency target, and risk assumptions.
- API, data flow, state ownership, and storage.
- Model, retrieval, tool, and orchestration choices.
- Authentication, authorization, tenancy, secrets, and deletion.
- Timeouts, retry safety, idempotency, fallback, and backpressure.
- Offline and online evaluation.
- Traceability, alerting, cost, rollout, and rollback.
- One simpler alternative and why it is insufficient or preferable.

## 6. Mock interview rounds

### Round A: foundations — 45 minutes

- Derive attention and discuss complexity.
- Compare encoder-only, decoder-only, and encoder-decoder architectures.
- Explain SFT, RLHF, DPO, LoRA, QLoRA, and quantization.
- Diagnose long-context performance and generation latency.
- Discuss hallucination without claiming it can be completely eliminated.

### Round B: RAG and agents — 45 minutes

- Diagnose a corpus where the answer exists but retrieval fails.
- Design permission-aware hybrid retrieval with citations.
- Decide between a deterministic workflow and an agent.
- Secure tools against injection and excessive permissions.
- Evaluate final answers and intermediate trajectories.

### Round C: coding — 60 minutes

- Complete one retrieval/data-processing problem.
- Complete one async/reliability problem.
- Add tests and discuss production hardening.

### Round D: system design — 60 minutes

- Choose one drill, state assumptions, and draw the end-to-end design.
- Expect requirement changes halfway through.
- Finish with bottlenecks, metrics, costs, and rollback.

### Round E: project and behavioral — 45 minutes

- Present Suvyon in five minutes.
- Defend three architectural decisions.
- Explain one failure and the resulting engineering change.
- Tell stories about ambiguity, disagreement, ownership, and learning.
- Identify what you would redesign with more time or scale.

## 7. Scoring rubric

Score every answer from 0 to 4.

| Score | Evidence |
|---:|---|
| 0 | Cannot answer or gives incorrect information |
| 1 | Recognizes the term but cannot explain the mechanism |
| 2 | Correct definition and basic example |
| 3 | Explains mechanism, use case, and meaningful trade-off |
| 4 | Adds measurement, failure handling, alternatives, and project evidence |

Also score delivery separately:

- Structure: conclusion first, then evidence.
- Precision: no vague “AI magic” or invented measurements.
- Relevance: answers the question before adding context.
- Ownership: distinguishes personal work from team or library behavior.
- Adaptability: responds calmly when assumptions change.

Target an average of at least 3, no zeroes, and no score below 2 in the role's core areas.

## 8. Gap tracker

Copy this table for every mock:

| Question/topic | Knowledge 0–4 | Delivery 0–4 | Missing detail | Next proof | Retest date |
|---|---:|---:|---|---|---|
| Example: KV-cache pressure | 2 | 3 | Memory-growth factors | Calculate one serving scenario | Tomorrow |

Fix gaps by producing evidence: a diagram, calculation, code exercise, benchmark plan, or concise answer. Re-reading alone is not a retest.

## 9. Project-story preparation

Prepare these six stories from real experience:

1. A difficult technical decision with alternatives and evidence.
2. A production failure or severe bug and the prevention added afterward.
3. A performance or cost improvement with before/after measurement.
4. A security or privacy risk you identified.
5. Ambiguous requirements you converted into a shipped outcome.
6. A disagreement where new evidence changed either your decision or someone else's.

Use `Situation -> constraint -> your action -> measured result -> lesson`. Never invent metrics. If measurement was missing, say what you would instrument now.

## 10. Suvyon demonstration route

Keep the walkthrough under five minutes:

1. State the user problem and who benefits.
2. Show the full-width responsive chat workspace and collapsed drawers.
3. Explain document ingestion, retrieval, reranking, citations, and permission boundaries.
4. Show provider/model selection and explain encrypted per-user API keys.
5. Describe agent execution, current-task progress visibility, and history behavior.
6. Show image-generation progress, responsive display, full-size viewing, and download.
7. Finish with evaluation, observability, a known limitation, and the next measured improvement.

Have a backup architecture diagram and screenshots in case the live environment or a provider fails.

## 11. Interview-day operating procedure

- Repeat the question in your own words and state necessary assumptions.
- Lead with the direct answer; expand only to the requested depth.
- Think aloud during design and coding, especially at decision points.
- Name trade-offs and measurements instead of calling a design “best.”
- If unsure, bound the uncertainty and explain how you would verify it.
- Test code with representative and adversarial inputs.
- Reserve the final minutes to summarize and invite challenge.

## 12. Final readiness gate

You are ready to schedule interviews when you can do all of the following without notes:

- [ ] Explain Transformer attention, training stages, adaptation methods, and inference bottlenecks.
- [ ] Compare prompting, RAG, tools, agents, and fine-tuning using decision criteria.
- [ ] Diagnose retrieval separately from answer generation.
- [ ] Design and secure an agent with external tools and bounded autonomy.
- [ ] Define an evaluation dataset, rubric, grader strategy, release threshold, and online experiment.
- [ ] Threat-model prompt injection, leakage, insecure output handling, and user API keys.
- [ ] Explain a multimodal or image-generation pipeline from request to full-size artifact delivery.
- [ ] Complete two coding exercises in 60 minutes with tests and complexity analysis.
- [ ] Design a scalable GenAI system in 35 minutes and defend alternatives.
- [ ] Present Suvyon in five minutes with architecture, ownership, evidence, failure, and next step.
- [ ] Deliver six genuine behavioral stories in under three minutes each.
- [ ] Score at least 3/4 overall in two consecutive full mock loops.

