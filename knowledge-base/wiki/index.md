# Knowledge Base Wiki

A concept-oriented reference synthesized from articles, summaries, and notes. Each page collects everything known about a concept across all sources.

---

## Architecture

| Page | What it covers |
|---|---|
| [[architecture/transformer]] | Decoder-only transformer, blocks, LayerNorm, residual connections |
| [[architecture/attention]] | Self-attention, QKV, causal masking, multi-head, cross-attention |
| [[architecture/positional-embeddings]] | Learned, sinusoidal, RoPE, ALiBi |
| [[architecture/vision-transformers]] | ViT, DeiT, CLIP, ViT vs CNN |
| [[architecture/pre-transformer-architectures]] | CNN, RNN, LSTM, GRU, GAN |
| [[architecture/graph-neural-networks]] | GCN, GAT, graph-based reasoning |
| [[architecture/mixture-of-experts]] | MoE layers, routing, load balancing, expert capacity, MLA, MTP, MoE LLMs |

---

## Training

| Page | What it covers |
|---|---|
| [[training/pretraining]] | Next token prediction, self-supervised learning, language modeling objective |
| [[training/tokenization]] | BPE, BBPE, token embeddings, context window |
| [[training/fine-tuning]] | SFT, RLHF, DPO, PEFT, imitation learning |
| [[training/distributed-training]] | DDP, FSDP, gradient accumulation, AMP |
| [[training/optimization]] | Learning rate schedules, gradient clipping, weight initialization |
| [[training/reasoning-models]] | Long CoT, RLVR, GRPO, DeepSeek-R1, inference-time scaling, distillation |
| [[training/continual-learning]] | Catastrophic forgetting, RL vs SFT, RL's Razor, on-policy data, EAFT |
| [[training/peft-and-lora]] | LoRA low-rank decomposition, rank hyperparameter, adapter targets, QLoRA, forgetting prevention |

---

## Inference & Prompting

| Page | What it covers |
|---|---|
| [[inference/decoding-strategies]] | Autoregressive generation, temperature, top-K, nucleus sampling |
| [[inference/prompting-and-reasoning]] | Zero/few-shot, CoT, Self-Consistency, ToT, GoT |

---

## Evaluation

| Page | What it covers |
|---|---|
| [[evaluation/benchmarks]] | MMLU, GPQA, BIG-Bench, IFEval, AlpacaEval, math benchmarks, IRT |
| [[evaluation/statistical-evaluation]] | Standard errors, CIs, CLT, clustered errors, variance reduction, power analysis |
| [[evaluation/llm-as-a-judge]] | LLM-as-a-Judge, MT-Bench, Chatbot Arena, AlpacaEval, bias types, G-Eval, RLAIF |
| [[evaluation/alignment-evaluation]] | Agentic misalignment evaluation, SHADE-Arena, behavioral auditing agents, cross-lab findings |

---

## Concepts

| Page | What it covers |
|---|---|
| [[concepts/scaling-and-the-bitter-lesson]] | The Bitter Lesson, scaling laws, GPT scaling trajectory |
| [[concepts/foundation-models]] | Pretrain-then-adapt paradigm, transfer learning |
| [[concepts/agi-and-intelligence]] | AGI timelines, cognitive deficits, cognitive core, model collapse, RL limitations, LLM culture |
| [[concepts/distillation]] | Knowledge distillation, DeiT distillation token, capability distillation (DeepSeek-R1) — three distinct uses disambiguated |

---

## Applications

| Page | What it covers |
|---|---|
| [[applications/rag]] | RAG, vector databases, retrieval techniques, reranking, FiD, RETRO, HyDE |
| [[applications/agentic-patterns]] | Agentic patterns, MCP, A2A, memory, tool use |
| [[applications/prompt-injection]] | Prompt injection attacks, indirect injection, exfiltration, mitigations, architectural defense patterns |
| [[applications/guardrails]] | Structural, syntactic, semantic, safety, and input guardrails; Guidance, NeMo-Guardrails, SelfCheckGPT |
| [[applications/agent-harness]] | Agent Harness engineering: ReAct loops, tool systems, context compression, sub-agents, permissions, hooks |
