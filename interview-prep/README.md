# Suvyon GenAI and Agentic AI Interview Playbook

This folder is a code-linked interview curriculum. Its goal is not memorization: you should be able to explain a concept, locate it in Suvyon, discuss its trade-offs, and propose a production improvement.

## How to use this material

For each topic, practice four levels:

1. **Definition** — explain it in one or two sentences.
2. **Mechanism** — draw the flow and explain why it works.
3. **Suvyon evidence** — point to the implementation.
4. **Engineering judgment** — describe limitations, metrics, and the next improvement.

Use this order:

| Phase | Read | Outcome |
|---|---|---|
| 0. Plan | [Complete 12-week study plan](00-study-plan/COMPLETE_STUDY_PLAN.md) | Cover the full interview surface beyond Suvyon |
| 1. Core | [GenAI foundations](01-foundations/GENAI_FOUNDATIONS.md) | Explain transformers, inference, prompting, embeddings, and hallucination |
| 2. Grounding | [RAG guide](02-rag/RAG_INTERVIEW_GUIDE.md) | Design and evaluate an ingestion/retrieval pipeline |
| 3. Agency | [Agentic AI guide](03-agents/AGENTIC_AI_INTERVIEW_GUIDE.md) | Explain tool calling, agent loops, state, safety, and failure handling |
| 4. Project | [Suvyon deep dive](04-suvyon-deep-dive/SUVYON_ARCHITECTURE.md) | Give a confident project walkthrough backed by code |
| 4a. Explore | [Interactive Suvyon project explorer](project-explorer/README.md) | Click through every runtime flow and open exact source lines |
| 5. Design | [Production system design](05-system-design/PRODUCTION_DESIGN.md) | Scale, secure, observe, and evaluate the system |
| 6. Engineering | [Python/API/data guide](05-system-design/ENGINEERING_FOUNDATIONS.md) | Defend backend, async, database, and testing decisions |
| 7. Drill | [Quick question bank](06-question-bank/QUESTIONS_AND_ANSWERS.md) | Rehearse 30-second answers and identify weak topics |
| 8. Deep answers | [Core AI](06-question-bank/DETAILED_CORE_QA.md), [RAG and agents](06-question-bank/DETAILED_RAG_AGENT_QA.md), [production and project](06-question-bank/DETAILED_PRODUCTION_PROJECT_QA.md) | Deliver two-to-five-minute answers and handle follow-ups |
| 9. Perform | [Mock interview kit](07-practice/MOCK_INTERVIEW.md) | Practice project pitches and interview rounds |

## The answer framework

Use **C-M-E-T** for technical questions:

- **Concept:** precise definition.
- **Mechanism:** data/control flow.
- **Evidence:** an example from Suvyon.
- **Trade-off:** limitation and improvement.

Example: “RAG retrieves external evidence and puts it into the model context before generation. In Suvyon, upload processing parses, chunks, embeds, and stores document chunks in pgvector; a query is embedded and searched by cosine distance. This improves grounding and freshness, but retrieval quality depends on chunking and thresholds, so I would measure recall@k, faithfulness, and answer relevance.”

## Four-week schedule

| Week | Focus | Deliverable |
|---|---|---|
| 1 | Foundations, prompting, embeddings | Explain every term without notes; draw transformer and inference flow |
| 2 | RAG, vector search, evaluation | Whiteboard Suvyon ingestion and query paths; diagnose five RAG failures |
| 3 | Agents, tools, routing, safety | Trace the Suvyon agent loop and discuss human approval and idempotency |
| 4 | System design and mocks | Deliver 30-second, 2-minute, and 10-minute project explanations |

Daily routine: 30 minutes study, 30 minutes code tracing, 20 minutes speaking aloud, and 10 minutes reviewing weak answers.

The four-week schedule is a revision sprint. For full preparation, use the [12-week plan and readiness gates](00-study-plan/COMPLETE_STUDY_PLAN.md).

## How to drill the detailed answers for 12 weeks

Do not read all answers repeatedly. Use this loop for five questions per study day:

1. Answer closed-book in 30 seconds.
2. Expand for two minutes using Concept, Mechanism, Evidence, and Trade-off.
3. Answer two follow-ups without notes.
4. Compare with the detailed answer and write only the missing ideas on a flashcard.
5. Repeat the same question after 1, 3, 7, 14, and 30 days.

| Weeks | Primary detailed bank | Required performance |
|---|---|---|
| 1-4 | Core AI | Accurate definition, mechanism, math intuition, and metric choice |
| 5-6 | RAG | Diagnose retrieval versus generation failures and design secure retrieval |
| 7-8 | Agents | Explain the loop, controls, memory, MCP, and evaluation without buzzwords |
| 9-10 | Production | Handle scale, security, outage, observability, latency, and cost |
| 11 | Suvyon project | Give 30-second, two-minute, and ten-minute walkthroughs backed by code |
| 12 | Mixed mocks | Score at least 8/10 on random questions and recover from follow-ups |

## Readiness checklist

- [ ] Explain attention, tokens, context windows, temperature, and hallucination.
- [ ] Compare prompting, RAG, fine-tuning, and agents.
- [ ] Design chunking, embedding, retrieval, reranking, citations, and evaluation.
- [ ] Explain tool schemas, the agent loop, state, termination, and human approval.
- [ ] Trace a Suvyon chat request and document upload end-to-end.
- [ ] Explain multi-LLM routing and failover with the actual code.
- [ ] Identify what Suvyon implements today versus what architecture documents propose.
- [ ] Discuss latency, cost, security, observability, and failure recovery.
- [ ] Give evidence-based answers using tests and code paths.
- [ ] Complete at least three timed mock interviews.

## Important accuracy rule

Existing files in `docs/architecture/` contain both implemented design and aspirational design. In an interview, say “implemented” only when the current code supports it. For example, Suvyon implements provider availability checks and sequential failover, but it does not yet implement health-score-, latency-, or cost-based dynamic routing.
