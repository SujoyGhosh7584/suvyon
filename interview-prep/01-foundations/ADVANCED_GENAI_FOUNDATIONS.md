# Advanced GenAI Foundations

Use this guide after `GENAI_FOUNDATIONS.md`. The goal is to connect model internals to production decisions instead of reciting definitions.

## The complete model lifecycle

Explain a modern generative-AI system as a lifecycle:

1. **Data:** collect, license, filter, deduplicate, classify, redact, and tokenize data.
2. **Pre-training:** predict tokens or other targets at scale to learn representations and capabilities.
3. **Post-training:** use supervised examples and preference or reward signals to improve instruction following, safety, and style.
4. **Evaluation:** measure capability, reliability, safety, domain quality, and regressions on held-out tasks.
5. **Serving:** quantize or shard the model, schedule requests, manage KV cache, batch work, and stream output.
6. **Application:** add prompts, retrieval, tools, memory, policy enforcement, observability, and human approval.
7. **Feedback:** inspect failures, curate datasets, rerun evaluations, and release only measured improvements.

Interview distinction: an LLM is a probabilistic model; a GenAI product is a controlled system around that model.

## Transformer architectures

### Encoder-only

Encoder-only models attend bidirectionally to the full input. They are strong for classification, token labeling, reranking, and embeddings. BERT-style masked-language modeling is the classic example.

### Decoder-only

Decoder-only models use causal attention: token position `t` cannot attend to future positions. They generate autoregressively and dominate general-purpose text generation.

### Encoder-decoder

The encoder represents the input; the decoder generates while attending to both earlier output tokens and encoder states. This is natural for translation, summarization, and other sequence-to-sequence tasks.

### Attention equation

For queries `Q`, keys `K`, and values `V`:

```text
Attention(Q,K,V) = softmax(QK^T / sqrt(d_k))V
```

- `QK^T` measures compatibility.
- division by `sqrt(d_k)` controls variance and prevents saturated softmax values.
- softmax produces weights.
- multiplication by `V` mixes information.
- multi-head attention learns several relation subspaces in parallel.

Vanilla attention over sequence length `n` materializes an `n × n` interaction matrix, giving quadratic time and memory pressure in `n`. FlashAttention improves exact attention by reducing expensive high-bandwidth-memory traffic; it does not change the mathematical result into an approximation.

### Positional information

Attention alone is permutation-invariant. Models add order through learned absolute positions, sinusoidal encodings, relative biases, or rotary position embeddings. For long-context questions, discuss both the advertised context limit and effective retrieval/attention quality within that limit.

### Residuals, normalization, and MLPs

Residual connections improve gradient flow. Layer normalization stabilizes activations. The feed-forward/MLP block applies token-wise nonlinear transformation and holds substantial model capacity. In mixture-of-experts models, a router activates only a subset of expert MLPs per token, increasing total parameters without proportional compute per token; routing balance and communication become new challenges.

## Tokenization

Subword tokenizers trade vocabulary size against sequence length. Byte-pair encoding and unigram tokenization can represent rare words using smaller pieces. Production consequences include:

- cost and latency are token-based, not character-based;
- languages and code can have different token efficiency;
- truncation can silently remove critical instructions or evidence;
- character offsets do not automatically match token offsets;
- special tokens define message boundaries and tool formats;
- adding vocabulary requires updating model embeddings and often training.

Good answer: never estimate a context budget only from word count; measure it with the target model's tokenizer.

## Training objectives and scaling

Decoder LLMs commonly minimize next-token cross-entropy. Teacher forcing exposes the correct previous tokens during training, while inference conditions on the model's own generated tokens; this creates exposure differences.

Scaling is not simply “more parameters is better.” Capability depends on model size, data quantity and quality, compute, optimization, architecture, and post-training. Compute-optimal training asks how to allocate a fixed budget between parameters and training tokens. Data contamination and benchmark leakage can make a larger score misleading.

### Important training terms

- **Epoch:** one pass over the dataset.
- **Batch:** examples used for one optimization step.
- **Gradient accumulation:** simulate a larger effective batch across multiple forward/backward passes.
- **Learning-rate warmup:** gradually increase the learning rate early to reduce instability.
- **Weight decay:** regularization discouraging excessive weights.
- **Mixed precision:** lower-precision compute with safeguards for speed and memory.
- **Gradient checkpointing:** recompute activations during backward pass to save memory.
- **Data parallelism:** replicas process different batches and synchronize gradients.
- **Tensor parallelism:** split tensor operations across devices.
- **Pipeline parallelism:** place model stages on different devices.
- **ZeRO/FSDP:** shard parameters, gradients, and optimizer state.

## Post-training and alignment

### Supervised fine-tuning

SFT trains on demonstrations of desired input-output behavior. It teaches format and instruction following but can overfit narrow examples or reduce general capability if data and optimization are poor.

### RLHF

A common RLHF pipeline collects preference comparisons, trains a reward model, and optimizes the policy against that reward while constraining drift from a reference policy. Benefits include learning preferences not captured by token likelihood. Risks include reward hacking, annotator bias, instability, and high operational complexity.

### DPO

Direct Preference Optimization trains directly from preferred/rejected pairs using a classification-like objective derived from the reward-model formulation. It is operationally simpler than a separate reward-model-plus-RL pipeline, but still depends on representative preference data and a carefully chosen reference/regularization strength.

### RLAIF and constitutional approaches

AI-generated critiques or preferences can reduce human-labeling cost. They increase dependence on the evaluator model and written principles, so bias, correlated errors, and evaluator drift must be measured rather than assumed away.

### LoRA and QLoRA

LoRA freezes base weights and learns low-rank update matrices, reducing trainable parameters and storage. QLoRA combines a quantized frozen base with trainable low-rank adapters. These improve affordability; they do not guarantee quality and do not eliminate activation memory, data quality, evaluation, or serving concerns.

## Fine-tuning decision framework

Use this order:

| Need | First choice | Why |
|---|---|---|
| Better instruction or format | prompt + structured output | Cheapest and easiest to revise |
| Current/private factual knowledge | RAG | Updates knowledge without retraining weights |
| External actions | tools/workflow | Models cannot reliably perform side effects by text generation |
| Stable domain behavior/style | SFT or PEFT | Repeated behavioral pattern can be learned |
| Preference alignment | DPO/RLHF/RLAIF | Optimizes comparative preference signals |
| Lower serving cost | smaller model, distillation, quantization | Fine-tuning alone does not make inference cheap |

Always define a baseline and evaluation set before tuning. Otherwise “the model feels better” is not evidence.

## Inference internals

### Prefill and decode

- **Prefill:** process the input prompt in parallel and create key/value states.
- **Decode:** generate tokens one at a time; each step reuses cached key/value states.

Time to first token is dominated by queueing plus prefill. Inter-token latency is dominated by decode scheduling and memory bandwidth. Optimize them separately.

### KV cache

The KV cache stores attention keys and values from prior tokens so generation does not recompute the entire prefix at each step. Its memory grows with batch size and sequence length. Prefix caching reuses shared prompt prefixes across requests when exact cache keys and isolation rules permit.

### Batching

Static batching waits for a fixed batch and wastes capacity when sequences finish at different times. Continuous batching admits new work as slots become available, improving utilization. Large batches improve throughput but may hurt tail latency.

### PagedAttention

PagedAttention manages KV-cache blocks like virtual-memory pages, reducing fragmentation and enabling flexible sharing. The interview insight is that serving bottlenecks are often memory-management and scheduling problems, not only raw FLOPS.

### Quantization

Quantization represents weights and sometimes activations/KV cache with fewer bits. It reduces memory and can improve throughput, but quality and kernel speed depend on method, hardware, calibration, and workload. Distinguish weight-only quantization from weight-and-activation quantization and quantization-aware training from post-training quantization.

### Speculative decoding

A cheaper draft method proposes tokens and the target model verifies them. Accepted runs reduce target-model decode steps without changing the target distribution when implemented exactly. Speedup depends on acceptance rate, verification overhead, load, and batch size; it is not universally faster.

### Parallelism and serving metrics

- **TTFT:** time to first token.
- **ITL/TPOT:** inter-token latency or time per output token.
- **End-to-end latency:** user-observed completion time.
- **Throughput:** requests or tokens completed per unit time.
- **Goodput:** throughput satisfying latency/service objectives.
- **Utilization:** how effectively accelerators are used.
- **Queue time:** delay before model work begins.

Always report percentiles such as p50, p95, and p99, not only averages.

## Decoding and reasoning

Greedy decoding selects the highest-probability token. Temperature rescales logits; top-k restricts to `k` candidates; top-p selects the smallest candidate set reaching cumulative probability `p`. Beam search tracks high-probability sequences and is useful in constrained sequence tasks, but can reduce diversity and is less common for open-ended chat.

Reasoning quality can improve through decomposition, self-consistency, search, verification, tool use, or additional test-time compute. Do not claim hidden reasoning text proves correctness. Evaluate the final answer, intermediate tool/state invariants where observable, and outcome success.

## Structured output and tool calling

Structured output constrains a response to a schema. Tool calling lets the model propose a named action and arguments; application code validates and executes it.

A safe tool flow is:

1. supply a minimal JSON schema and clear description;
2. parse and validate arguments server-side;
3. authorize against the user and resource;
4. apply timeouts, idempotency, and rate limits;
5. request confirmation for consequential effects;
6. execute outside the model;
7. return a bounded, sanitized observation;
8. log identifiers and outcomes without secrets.

The model never becomes the authorization layer.

## Multimodal systems

Multimodal models map text, image, audio, or video signals into compatible representations. Common patterns include a vision encoder connected to a language decoder, interleaved multimodal tokens, and modality-specific encoders with projection layers.

Interview design concerns:

- resize and tile images without losing critical detail;
- preserve page/layout information for documents;
- distinguish OCR errors from reasoning errors;
- sample long videos or use temporal encoders;
- measure speech recognition separately from downstream reasoning;
- defend against instructions hidden in images, documents, or audio;
- record modality-specific latency and cost;
- evaluate accessibility and privacy for biometric or sensitive data.

## Long context versus RAG

Long context reduces retrieval infrastructure for small corpora but increases token cost, prefill latency, distraction, and data-exposure risk. RAG selects evidence and supports citations and access control, but introduces ingestion and retrieval failure modes. Hybrid designs retrieve first, then use a larger context for selected evidence.

“Fits in the context window” is not the same as “will be used accurately.” Test position sensitivity, conflicting evidence, distractors, and multi-hop questions.

## Evaluation stack

Use layered evaluation:

1. **Deterministic checks:** schema validity, exact match, executable code tests, citation URL validity, policy rules.
2. **Reference metrics:** precision/recall/F1, retrieval recall@k, nDCG, MRR, ROUGE/BLEU only where appropriate.
3. **Model graders:** rubric-based scoring for properties difficult to encode, calibrated against humans.
4. **Human review:** expert judgment, pairwise preference, severity classification.
5. **Online metrics:** completion rate, correction rate, escalation, abandonment, latency, cost, incidents.

Create datasets from real tasks and failures. Slice by language, length, user group, domain, tool, provider, and risk. Track confidence intervals when sample sizes are limited. A release gate compares the candidate to a fixed baseline and blocks critical safety regressions even if average quality rises.

Model graders can be position-biased, verbose-answer-biased, self-preferential, or vulnerable to injected text. Randomize ordering, use explicit rubrics, require evidence, calibrate against blinded humans, and combine graders with deterministic checks.

## Security and responsible AI

Know these threats:

- direct and indirect prompt injection;
- data exfiltration through tools or retrieved content;
- insecure output handling;
- excessive agency and permissions;
- poisoned knowledge bases or training data;
- model denial of service and unbounded cost;
- sensitive information in prompts, traces, caches, or logs;
- cross-tenant retrieval and broken object authorization;
- unsafe generated code or URLs;
- supply-chain risk in models, adapters, datasets, and plugins.

Defenses are layered: least privilege, content provenance, trust boundaries, sandboxing, schema validation, allow-lists, network egress controls, human approval, retrieval ACLs, rate limits, redaction, audit logs, evaluation, monitoring, and incident response.

Fairness evaluation requires defining affected groups and harms for the use case, measuring relevant slices, testing allocation and representation harms, documenting limitations, and establishing escalation. Generic “the model is unbiased” claims are not credible.

## Math and metrics quick sheet

```text
softmax(z_i) = exp(z_i) / sum_j exp(z_j)
cross_entropy = -sum_i y_i log(p_i)
perplexity = exp(average negative log likelihood)
cosine(a,b) = (a·b) / (||a|| ||b||)
precision = TP / (TP + FP)
recall = TP / (TP + FN)
F1 = 2PR / (P + R)
DCG@k = sum_i relevance_i / log2(i + 1)
```

Perplexity measures predictive likelihood under a tokenizer and dataset; it does not directly measure instruction following, factuality, safety, or product usefulness.

## Primary reading

- [Attention Is All You Need](https://arxiv.org/abs/1706.03762)
- [Retrieval-Augmented Generation](https://arxiv.org/abs/2005.11401)
- [Training language models to follow instructions with human feedback](https://arxiv.org/abs/2203.02155)
- [Direct Preference Optimization](https://arxiv.org/abs/2305.18290)
- [LoRA](https://arxiv.org/abs/2106.09685) and [QLoRA](https://arxiv.org/abs/2305.14314)
- [FlashAttention](https://arxiv.org/abs/2205.14135)
- [PagedAttention and vLLM](https://arxiv.org/abs/2309.06180)
- [Model Context Protocol architecture](https://modelcontextprotocol.io/specification/2025-06-18/architecture)
- [OpenAI grader types](https://platform.openai.com/docs/api-reference/graders)

## Interview proof checklist

- [ ] Derive attention shapes and explain the scaling term.
- [ ] Compare encoder-only, decoder-only, and encoder-decoder models.
- [ ] Explain SFT, RLHF, DPO, LoRA, QLoRA, quantization, and distillation.
- [ ] Separate prefill, decode, TTFT, inter-token latency, throughput, and goodput.
- [ ] Explain KV cache, continuous batching, PagedAttention, and speculative decoding.
- [ ] Design a multimodal ingestion and evaluation flow.
- [ ] Choose prompting, RAG, tools, or fine-tuning from requirements.
- [ ] Build an evaluation set and defend every metric.
- [ ] Threat-model a tool-using RAG system.
