# Detailed Core AI Interview Answers

These are speaking answers, not scripts to memorize. Start with the **30-second answer**. If the interviewer asks for depth, add the mechanism, trade-offs, and example. A strong answer normally takes two to four minutes.

## 1. How does a transformer language model work?

**30-second answer:** A transformer converts tokens into vectors, mixes information across the sequence with self-attention, transforms each position through feed-forward layers, and predicts a probability distribution for the next token. During generation it repeatedly selects a token, appends it to the context, and runs the next step. Training adjusts parameters to reduce next-token prediction loss.

**Deeper answer:** Token IDs are mapped to embeddings and combined with positional information. In each attention head, the model projects every position into query, key, and value vectors. The score between a query and keys determines which value vectors influence that position. Multiple heads learn different relationships. Residual connections and normalization stabilize deep networks, while position-wise feed-forward blocks add nonlinear capacity. A decoder-only LLM uses a causal mask so a token cannot see future tokens during training.

At inference, the model produces logits, converts them to probabilities, and chooses a token using greedy decoding or sampling. A KV cache reuses previous key/value tensors so generation does not recompute the whole prefix at every step.

**Trade-off:** Attention gives flexible long-range interaction but standard attention has quadratic cost in sequence length. A larger context window also does not guarantee that the model will use every fact reliably.

**Likely follow-ups:** Why causal masking? What is the KV cache? Why are residual connections useful? Why can long context still fail?

## 2. Explain self-attention mathematically and intuitively.

**30-second answer:** Self-attention lets each token create a weighted combination of other token representations. Queries express what a token is looking for, keys express what each token offers, and values contain the information to aggregate.

**Deeper answer:** For input matrix `X`, learned projections produce `Q = XWq`, `K = XWk`, and `V = XWv`. Scaled dot-product attention is `softmax(QK^T / sqrt(d_k))V`. A large query-key dot product produces a larger weight after softmax. Division by `sqrt(d_k)` keeps score variance controlled; otherwise large dimensions can make softmax extremely peaked and gradients weak. Multi-head attention performs this operation in different learned subspaces, concatenates the results, and projects them again.

The word “bank,” for example, can attend to “river” or “money” elsewhere in a sentence, producing a context-dependent representation. Attention weights are useful diagnostic signals but should not automatically be treated as faithful explanations of model reasoning.

**Trade-off:** Attention is parallelizable during training and captures global dependencies, but its compute and memory grow quickly with sequence length.

## 3. Why do LLMs hallucinate, and how would you reduce hallucination?

**30-second answer:** An LLM is optimized to generate probable continuations, not to verify truth. Hallucination increases when evidence is missing, ambiguous, stale, or drowned in context. I reduce it with authoritative retrieval or tools, clear abstention rules, citations, structured validation, and evaluations that measure claim support.

**Deeper answer:** There are several failure sources: knowledge absent from parameters, conflicting prompt evidence, retrieval failure, decoding randomness, and a prompt that rewards a fluent answer even when the model is uncertain. The mitigation must match the source. RAG helps with private or changing facts; tools help with calculations and live state; constrained schemas help with format, not truth; lower temperature improves repeatability but does not create knowledge.

For a grounded assistant I would retrieve evidence with tenant filters, rerank it, instruct the model to answer only from supplied sources, attach claim-level citations, and abstain below a calibrated retrieval threshold. I would evaluate retrieval recall separately from answer faithfulness so I know whether the retriever or generator failed.

**Trade-off:** Aggressive abstention improves precision but can reduce answer coverage. The threshold should reflect the cost of a wrong answer.

## 4. Compare prompting, RAG, fine-tuning, and tools.

**30-second answer:** Prompting changes instructions and examples at request time. RAG supplies external facts at request time. Fine-tuning changes model behavior through parameter updates. Tools let the system read live state or take deterministic actions. I choose based on whether the problem is behavior, knowledge, or action.

**Deeper answer:** Use prompting first for output style, task framing, and decomposition because it is fast to change. Use RAG when knowledge is private, large, frequently changing, or must be cited. Use fine-tuning when many examples define stable behavior that prompts cannot reliably induce, or when a smaller model needs task specialization. Use tools for exact arithmetic, database lookups, web search, or actions such as sending email.

A common mistake is fine-tuning a model to memorize a changing company handbook. That creates stale facts and weak provenance; RAG is a better fit. Another mistake is asking an LLM to calculate financial totals instead of calling deterministic code.

**Decision criteria:** quality, freshness, explainability, latency, cost, privacy, maintenance, and available training data. These approaches can be combined: a fine-tuned model can choose tools while RAG provides evidence.

## 5. What are embeddings and cosine similarity?

**30-second answer:** An embedding maps an object such as text into a dense vector whose geometry captures useful relationships. Cosine similarity compares the angle between two vectors, so it emphasizes direction rather than magnitude.

**Deeper answer:** For vectors `a` and `b`, cosine similarity is `(a dot b) / (||a|| ||b||)`, ranging from -1 to 1 mathematically, though text embeddings often occupy a narrower range. If embeddings are normalized to unit length, ranking by cosine similarity is equivalent to ranking by dot product, and squared Euclidean distance is monotonically related.

Embedding similarity is learned, not symbolic truth. Two texts can be semantically close but differ in a critical number, negation, date, or permission. That is why enterprise retrieval often combines dense vectors with lexical search, metadata filtering, and reranking.

**Suvyon evidence:** document chunks are embedded and stored in PostgreSQL/pgvector; retrieval uses cosine distance in `backend/app/rag/vector_store.py`.

**Likely follow-ups:** Why normalize? What happens when embedding models change? How do you evaluate an embedding model for your domain?

## 6. Explain temperature, top-k, and top-p.

**30-second answer:** Temperature rescales logits before softmax; lower values make the distribution sharper and outputs more deterministic. Top-k samples only from the k highest-probability tokens. Top-p samples from the smallest token set whose cumulative probability reaches p.

**Deeper answer:** With temperature `T`, probabilities are based on `softmax(logits/T)`. As `T` approaches zero, selection approaches greedy decoding; higher temperature flattens the distribution. Top-k uses a fixed candidate count regardless of uncertainty. Top-p adapts the candidate set: it may be small for a confident next token and larger for an uncertain one.

For extraction, classification, and tool arguments I favor low randomness plus schema validation. For brainstorming I allow more diversity. Exact behavior differs across providers, and setting temperature to zero does not guarantee identical output because serving systems and floating-point kernels can still introduce variation.

**Important distinction:** Sampling controls variability, not factuality. A deterministic hallucination is still a hallucination.

## 7. What is tokenization and why does it matter in production?

**30-second answer:** Tokenization converts text into vocabulary IDs the model can process. Token boundaries affect context usage, latency, cost, multilingual performance, and how much text fits in a request.

**Deeper answer:** Modern LLMs generally use subword tokenization, so common strings may be one token while rare names, code, or some languages split into many. The context budget includes system instructions, history, retrieved evidence, tool schemas/results, and generated output. Character count is therefore an unreliable proxy.

In production I count tokens with the model-compatible tokenizer, reserve output capacity, truncate deliberately rather than accidentally, summarize old history when appropriate, and monitor input/output tokens by feature. I never cut retrieved context blindly because truncation may remove citations or split facts.

**Trade-off:** More context can improve recall but increases latency and cost and may lower answer quality through distraction or lost-in-the-middle effects.

## 8. What is fine-tuning, and what are LoRA and quantization?

**30-second answer:** Fine-tuning continues training a pretrained model on task-specific examples. LoRA learns small low-rank weight updates while keeping base weights frozen, reducing training memory. Quantization stores or computes weights and activations at lower precision to reduce memory and improve throughput.

**Deeper answer:** Full fine-tuning updates most parameters and can be expensive. LoRA represents an update as the product of two much smaller matrices and applies it to selected layers. QLoRA combines a quantized frozen base model with trainable adapters. Quantization formats such as 8-bit or 4-bit trade numerical precision for efficiency; quality impact depends on the model, task, and calibration.

Before fine-tuning, I establish a held-out evaluation set and a prompt/RAG baseline. Training data must be representative, permissioned, deduplicated, and checked for leakage. I evaluate both target-task improvement and regressions in safety or general capability.

**Trade-off:** Fine-tuning adds dataset, training, deployment, and version-management complexity. It is not the preferred way to inject frequently changing facts.

## 9. Explain overfitting, bias-variance, and data leakage.

**30-second answer:** Overfitting means learning training-specific patterns that do not generalize. High bias underfits; high variance is too sensitive to the training sample. Leakage occurs when training features or evaluation data contain information unavailable at real prediction time, producing misleading metrics.

**Deeper answer:** I diagnose overfitting through a growing training-versus-validation performance gap. Remedies include more representative data, simpler models, regularization, early stopping, augmentation, and correct cross-validation. Leakage can be direct, such as including a post-outcome field, or subtle, such as splitting near-duplicate documents across train and test or fitting preprocessing on all data.

For RAG and LLM evaluation, I split by document, customer, or time when those boundaries match deployment. I keep prompt and model selection away from the final test set. Synthetic queries derived from the same source can inflate results, so I include real user queries and adversarial cases.

## 10. Precision, recall, F1, ROC-AUC, or PR-AUC—which would you use?

**30-second answer:** The metric depends on error cost and class balance. Precision asks whether predicted positives are correct; recall asks whether actual positives were found; F1 balances them. PR-AUC is usually more informative than ROC-AUC for rare positive classes.

**Deeper answer:** In a safety filter, missing harmful content may make recall the priority, while wrongly blocking legitimate users creates a precision constraint. In retrieval, recall@k measures whether evidence was found; precision@k measures how much retrieved content is relevant. ROC-AUC summarizes true-positive versus false-positive rates across thresholds, but can look optimistic when negatives dominate. PR-AUC focuses on positive predictions and is more revealing for imbalance.

I do not choose a threshold from an abstract metric alone. I translate errors into product cost, inspect calibration, select the operating point on validation data, and report uncertainty and subgroup performance.

## 11. What is backpropagation and why does optimization fail?

**30-second answer:** Backpropagation applies the chain rule from loss to each parameter, and an optimizer uses those gradients to update weights. Training can fail through poor learning rates, vanishing/exploding gradients, bad initialization, noisy data, unstable precision, or an unsuitable objective.

**Deeper answer:** A forward pass computes predictions and loss. Reverse-mode automatic differentiation efficiently accumulates partial derivatives through the computation graph. Gradient descent updates parameters opposite the gradient; Adam adapts per-parameter step sizes using running moments. Mini-batches give noisy but efficient gradient estimates.

I monitor training and validation loss, gradient norms, learning-rate schedule, numerical overflows, throughput, and representative task metrics. Normalization, residual connections, gradient clipping, warm-up, and mixed-precision loss scaling address different failure modes.

## 12. How do you evaluate an LLM feature?

**30-second answer:** I define task-specific success, build a versioned evaluation set, score deterministic and model-judged dimensions, inspect failures, and connect offline results to online outcomes. I evaluate components separately as well as end-to-end.

**Deeper answer:** For RAG I measure ingestion success, retrieval recall/MRR, faithfulness, answer relevance, and citation correctness. For an agent I also evaluate tool selection, argument validity, policy adherence, steps, recovery, latency, and cost. The dataset includes normal, edge, adversarial, and abstention cases from real traffic when allowed.

Exact checks cover schemas, forbidden actions, citations, and known answers. Human rubrics handle nuance. An LLM judge can scale evaluation, but I calibrate it against human labels, randomize answer order for pairwise tests, and watch position or verbosity bias. Every run records prompt, model, retrieval, tool, and dataset versions.

**Release rule:** define thresholds before seeing results, compare against a baseline, inspect regressions, then canary or shadow the change online with rollback criteria.
