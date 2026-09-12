# Evaluation, LLMOps, and Safety

This guide is the production-quality layer of GenAI interview preparation. A strong candidate can explain not only how to call a model, but also how to decide whether a change is better, deploy it safely, investigate failures, and control actions performed on behalf of users.

## 1. Start with an evaluation contract

Before changing a prompt, model, retriever, or tool, define:

- The user task and expected outcome.
- The unit being graded: response, claim, citation, retrieval result, tool trajectory, image, or session.
- Mandatory constraints such as valid JSON, correct citations, no secret leakage, and allowed latency.
- Quality dimensions and which one wins when they conflict.
- Important slices: language, tenant, document type, query complexity, risk level, model, and provider.
- Release thresholds and rollback conditions.

An evaluation contract prevents teams from optimizing a convenient metric that does not represent user success.

## 2. Build the dataset deliberately

Use a mixture of:

1. Curated golden cases for critical behavior.
2. Anonymized production cases representing actual traffic.
3. Adversarial and boundary cases.
4. Synthetic cases for coverage, reviewed against real distributions.
5. Regression cases from every important incident.

Every case should have a stable ID, input, necessary context, expected properties, grading rubric, tags, and provenance. Separate the development set from a final holdout so repeated prompt editing does not silently overfit the evaluation.

## 3. Match the grader to the property

| Property | Preferred grader | Caution |
|---|---|---|
| JSON/schema validity | Deterministic parser and schema validator | Valid JSON can still be semantically wrong |
| Exact identifiers/calculations | Programmatic comparison | Normalize only when normalization is allowed |
| Retrieval relevance | Human labels or calibrated relevance model | Similarity score alone is not relevance |
| Factual/grounded answer | Claim-level evidence check plus human calibration | Reference answers may allow multiple correct forms |
| Style/helpfulness | Rubric-based human or LLM judge | Watch verbosity and position bias |
| Tool use | State/trajectory assertions | A correct final answer can hide unsafe actions |
| Safety | Policy-specific classifier plus red-team review | Avoid one universal “safe” score |
| Images | Task-specific human review plus supporting automated metrics | Aesthetic scores do not prove prompt adherence |

Use model-based graders for scale, not as unquestioned truth. Calibrate them against expert labels, randomize response order for pairwise comparisons, and monitor disagreement by slice.

## 4. Evaluate each system layer

### Retrieval

- Recall@k: was sufficient evidence retrieved?
- MRR or NDCG: was relevant evidence ranked early?
- Context precision: how much retrieved context was actually useful?
- Filter correctness: were tenant, permission, date, and source constraints respected?
- Freshness: did the active index contain the current source version?

### Generation

- Task correctness and completeness.
- Groundedness at claim level.
- Citation entailment and citation coverage.
- Refusal correctness when evidence is missing.
- Instruction following and output-schema compliance.

### Agent behavior

- Task success and partial progress.
- Correct tool selection and argument accuracy.
- Unnecessary steps, repeated states, and termination behavior.
- Permission and confirmation compliance.
- Side effects, recovery, token usage, latency, and cost.

### Product behavior

- User completion and correction rates.
- Time to first useful result.
- Abandonment, retry, and escalation rates.
- Availability, p50/p95/p99 latency, and cost per successful task.
- Quality and safety metrics by provider, model, and traffic slice.

## 5. Offline-to-online release pipeline

```text
Proposed change
      |
      v
Unit and contract tests
      |
      v
Fixed regression suite ----> reject on quality/safety regression
      |
      v
Shadow or replay traffic
      |
      v
Small canary with kill switch
      |
      v
Guarded rollout by cohort
      |
      v
Production monitoring and feedback -> new regression cases
```

Pin model, prompt, evaluator, embedding, parser, index, and tool versions. A prompt change is a software release and should have a diff, owner, evaluation result, rollout plan, and rollback path.

## 6. Observability and reproducibility

A trace should make a failed response reproducible without leaking sensitive data. Record:

- Request and trace IDs, time, environment, and authorization scope.
- Provider/model, generation settings, prompt-template version, and token counts.
- Retrieval query, filters, scores, document/version IDs, and reranking results.
- Tool calls, safe arguments or hashes, timings, results, retries, and approvals.
- Guardrail decisions, schema-validation results, latency breakdown, and cost.
- Feedback and the evaluation-suite case created from the incident.

Apply redaction before logs are stored. Restrict access, define retention, and sample raw content only when consent and policy permit it.

## 7. Reliability patterns

- Use timeouts for provider, database, retrieval, and tool calls.
- Retry transient failures with exponential backoff and jitter; do not retry unsafe non-idempotent actions blindly.
- Add circuit breakers for failing providers and dependencies.
- Use idempotency keys for operations that can be repeated.
- Apply concurrency and token quotas per tenant.
- Degrade explicitly: retrieval-only response, smaller context, queued image job, or actionable error.
- Treat provider failover as a product and privacy decision because billing, model quality, and data processing may change.

## 8. Threat model for LLM applications

### Prompt injection

Untrusted documents, web pages, tool results, or users can contain instructions that compete with the application's intent. Keep data and instructions distinguishable, restrict tools by default, validate proposed actions, and enforce permissions outside the model.

### Data leakage

Leakage can occur through prompts, retrieval, logs, caches, model-provider requests, generated links, or cross-tenant memory. Filter retrieval by authorization before ranking, isolate cache keys by tenant and access scope, minimize transmitted data, redact logs, and test with canary secrets.

### Excessive agency

An agent should not gain broad permissions simply because a task is broad. Give narrowly scoped tools, cap steps and spending, require confirmation for consequential changes, and make actions attributable and reversible where possible.

### Insecure output handling

Model output is untrusted. Escape rendered content, validate URLs, never execute generated code in the application process, validate structured arguments, sandbox code execution, and enforce business rules independently of the model.

### Supply-chain and model changes

Track provider, model, dependency, prompt, and dataset versions. Re-run evaluations before upgrades, verify artifact sources, and define behavior when a provider retires or silently changes a model alias.

## 9. BYOK security design

For user-provided provider keys:

1. Receive keys only in an authenticated session over TLS.
2. Validate provider identity and minimally verify the credential when practical.
3. Encrypt at rest with authenticated encryption and a server-held master key or managed key service.
4. Store key metadata and a masked suffix separately from ciphertext.
5. Never return the plaintext key after the initial request.
6. Decrypt only in the backend immediately before use.
7. Redact request headers, exception messages, traces, and analytics.
8. Allow replacement and deletion and record a safe audit event.
9. Isolate every lookup by authenticated user/tenant.
10. Design master-key rotation and behavior for undecryptable legacy values.

The model-routing layer should never infer a credential from another tenant or silently send data to an unapproved provider.

## 10. Cost engineering

Model cost is driven by more than request count. Track input, cached-input, reasoning where exposed, output, embedding, reranking, tool, storage, and image-generation costs. Useful controls include:

- Token-aware quotas and output limits.
- Retrieval/context compaction.
- Exact or carefully scoped semantic caching.
- Model routing based on measured task difficulty.
- Batching for offline workloads.
- Smaller specialized models for classification, extraction, and moderation.
- Cost per successful task, not only cost per call.

Never optimize cost without watching the quality and safety slices affected by the change.

## 11. Incident-response answer framework

When asked how you would handle a quality or safety incident, answer in this order:

1. Contain: disable the feature, model, prompt, tool, or traffic slice with a kill switch.
2. Preserve: retain safe trace metadata and affected version IDs.
3. Diagnose: separate retrieval, prompt, model, tool, provider, and infrastructure causes.
4. Restore: roll back or use an evaluated fallback.
5. Communicate: identify affected users and obligations without speculating.
6. Prevent: add regression cases, monitoring, ownership, and a safer rollout gate.

## 12. Interview design exercises

Practice these on a whiteboard in 35 minutes each:

1. A multi-tenant enterprise RAG assistant with document permissions and citations.
2. A code agent allowed to edit a repository but not deploy without approval.
3. A multi-provider BYOK chat gateway with streaming, quotas, and provider outages.
4. An image-generation service with asynchronous jobs, moderation, original-size downloads, and cleanup.
5. A production evaluation platform comparing model and prompt versions.
6. A voice assistant with interruption handling and a sub-second responsiveness target.

For every design cover requirements, scale assumptions, API/data flow, storage, evaluation, security, failure modes, observability, cost, and one explicit trade-off.

## 13. Release checklist

- [ ] The task and risk level are documented.
- [ ] The evaluation dataset represents important production slices.
- [ ] Deterministic, model-based, and human graders are calibrated appropriately.
- [ ] Quality, safety, latency, and cost thresholds pass.
- [ ] Permission, prompt-injection, and data-leakage tests pass.
- [ ] Traces are useful and secrets are redacted.
- [ ] Rate limits, budgets, timeouts, retries, and circuit breakers are configured.
- [ ] A canary cohort, kill switch, and rollback are ready.
- [ ] Version metadata is sufficient to reproduce behavior.
- [ ] Production feedback can become regression cases.

