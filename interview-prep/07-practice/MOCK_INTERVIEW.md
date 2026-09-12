# Mock Interview and Practice Kit

## Practice rules

- Answer aloud, not silently.
- Start with a direct definition before details.
- Draw one diagram for every system-design answer.
- Reference a real Suvyon file/function when discussing the project.
- State current limitations without becoming defensive.
- End deep answers with measurement or an improvement.

## 45-minute GenAI round

1. Explain next-token prediction and self-attention (5 minutes).
2. Compare prompting, RAG, fine-tuning, and tools (5 minutes).
3. Design a RAG pipeline for private company documents (12 minutes).
4. Explain RAG evaluation and diagnose irrelevant answers (8 minutes).
5. Discuss hallucination, prompt injection, and data privacy (8 minutes).
6. Rapid fire: embeddings, chunking, reranking, temperature, context window (7 minutes).

## 45-minute Agentic AI round

1. Define agent versus workflow (4 minutes).
2. Whiteboard the Suvyon tool loop (8 minutes).
3. Design a safe email-and-calendar agent (12 minutes).
4. Explain state, memory, checkpointing, and idempotency (8 minutes).
5. Design agent evaluation (8 minutes).
6. Discuss when not to use agents or multi-agent systems (5 minutes).

## 60-minute Suvyon project round

1. Give the two-minute pitch.
2. Draw runtime architecture.
3. Trace auto chat end-to-end.
4. Trace RAG ingestion and retrieval.
5. Explain provider routing and failure behavior.
6. Explain workspace isolation and tool safety.
7. Identify three limitations and an evolution plan.
8. Walk through one representative test for each AI subsystem.

## Coding drills

Implement these on paper or in an isolated practice branch:

1. A typed tool dispatcher that rejects unknown and malformed arguments.
2. Cosine similarity and a top-k search over in-memory vectors.
3. A chunker with overlap and tests for empty/short/long input.
4. A bounded agent loop with repeated-call detection.
5. Exponential backoff with jitter and retryable-error classification.
6. An LRU/TTL cache keyed by prompt/model/config version.
7. A streaming endpoint that handles cancellation and partial failure.
8. Retrieval metrics: recall@k and MRR from labeled examples.

## Self-scoring rubric (0–2 each)

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| Accuracy | wrong/vague | mostly right | precise and qualified |
| Mechanism | no flow | partial flow | end-to-end explanation |
| Suvyon evidence | none | names component | links exact code/test |
| Trade-offs | none | generic | context-specific and measured |
| Communication | rambling | understandable | concise, structured, confident |

Target at least 8/10 on every core question.

## STAR template for project stories

- **Situation:** user/problem and constraints.
- **Task:** your responsibility and success condition.
- **Action:** decisions, implementation, debugging, collaboration.
- **Result:** measured outcome if available; never invent metrics.
- **Reflection:** what you would improve and why.

Prepare real stories for provider model retirement, RAG retrieval diversity, email confirmation safety, deployment/CORS configuration, and OTP authentication. Use Git history or issue records to recover facts if you do not remember them.

## Final-day checklist

- Rehearse the 30-second and two-minute pitches.
- Redraw chat, RAG, and agent diagrams from memory.
- Review the honest gap analysis.
- Pick two code files and two tests to screen-share.
- Prepare questions about the employer's evaluation, observability, data governance, model strategy, and autonomy boundaries.
- Do not memorize provider SKU names; explain capability and routing principles.

## Advanced GenAI round — 60 minutes

1. Derive scaled dot-product attention and explain long-sequence bottlenecks.
2. Compare pretraining, SFT, RLHF, DPO, LoRA, QLoRA, quantization, and distillation.
3. Explain prefill, decode, KV-cache memory, continuous batching, FlashAttention, PagedAttention, and speculative decoding.
4. Design and evaluate hybrid, permission-aware, multi-hop RAG.
5. Threat-model an agent that reads untrusted documents and can call write tools.
6. Design an offline-to-online evaluation and rollout process for a model change.
7. Explain a multimodal/image-generation request from input processing through original-size delivery.

## Advanced score requirements

Use the 0–4 rubric and practice schedule in the [Interview Readiness Lab](INTERVIEW_READINESS_LAB.md). A strong answer includes definition, mechanism, selection criteria, failure mode, measurement, and relevant project evidence. Pass two consecutive mixed loops with an average of at least 3/4 and no core-area score below 2/4.

Use [Advanced GenAI Q&A](../06-question-bank/ADVANCED_GENAI_QA.md) for follow-up questions and [Evaluation, LLMOps, and Safety](../05-system-design/EVALUATION_LLMOPS_AND_SAFETY.md) for production-depth drills.
