# Knowledge Base Q&A Index

A compact index of all processed sources. Loaded in full for Q&A — keep each entry brief.

---

## The Bitter Lesson

**File:** `summaries/The Bitter Lesson.md`  
**Type:** article  
**Topics:** scaling, bitter-lesson, pretraining, general-methods

Rich Sutton's 2019 essay arguing that 70 years of AI research consistently show one pattern: general methods that scale with computation always beat hand-crafted, knowledge-based approaches — eventually and by a large margin. Chess, Go, speech, vision all follow the same arc. The philosophical foundation of the LLM scaling era.

---

## Language Models: GPT and GPT-2

**File:** `summaries/Language Models GPT and GPT-2 - by Cameron R. Wolfe, Ph.D..md`  
**Type:** article  
**Topics:** pretraining, decoder-transformer, foundation-models, scaling, zero-shot

Cameron Wolfe overview of GPT (2018) and GPT-2 (2019) — the origin of the pretrain-then-adapt paradigm. GPT introduced fine-tuning from a pretrained decoder-only transformer; GPT-2 showed that scale alone enables zero-shot task solving without any fine-tuning. Establishes the scaling trajectory toward GPT-3 and modern LLMs.

---

## Language Model Training and Inference From Concept to Code

**File:** `summaries/Language Model Training and Inference From Concept to Code.md`  
**Type:** article  
**Topics:** pretraining, tokenization, inference, distributed-training, NanoGPT

Ground-up walkthrough of how causal LMs are built and trained, using Andrej Karpathy's NanoGPT (clean GPT-2 reimplementation) as the reference. Covers BPE tokenization, next-token prediction objective, autoregressive inference, temperature/Top-K/nucleus sampling, DDP vs FSDP, AMP, and gradient accumulation.

---

## Understanding and Using Supervised Fine-Tuning (SFT) for Language Models

**File:** `summaries/Understanding and Using Supervised Fine-Tuning (SFT) for Language Models.md`  
**Type:** article  
**Topics:** fine-tuning, SFT, alignment, PEFT, LoRA

Cameron Wolfe overview of SFT — the first alignment step after pretraining. Trains on curated (prompt, response) pairs using the same next-token objective. Key finding from LIMA: 1,000 high-quality examples beats 50K+ mediocre ones. Produces the reference policy for downstream DPO/RLHF. Includes practical guidance on `trl.SFTTrainer` and LoRA.

---

## Direct Preference Optimization (DPO)

**File:** `summaries/Direct Preference Optimization (DPO).md`  
**Type:** article  
**Topics:** fine-tuning, DPO, RLHF, alignment, preference-learning

Cameron Wolfe deep-dive on DPO — the preference-alignment algorithm that eliminates the separate reward model and RL loop required by RLHF. Derives the DPO loss from the RLHF objective in 4 steps; explains the gradient weighting that makes it work. Competitive with PPO-based RLHF at lower compute and complexity. Key hyperparameter: β ∈ [0,1] controlling KL constraint strength.

---

## Demystifying Reasoning Models

**File:** `summaries/Demystifying Reasoning Models - by Cameron R. Wolfe, Ph.D..md`  
**Type:** article  
**Topics:** reasoning-models, RLVR, GRPO, long-CoT, DeepSeek-R1, inference-scaling

Cameron Wolfe overview of the reasoning model paradigm: LLMs that produce long chains of thought (thousands of tokens) before answering, trained via RL with verifiable rewards (RLVR). Covers OpenAI o-series benchmarks, DeepSeek-R1's 4-stage pipeline (cold-start SFT → RL → rejection sampling → RLHF), GRPO, and distillation to smaller models. o3 achieves 87.5% on ARC-AGI (first to beat human baseline).

---

## Continual Learning with RL for LLMs

**File:** `summaries/Continual Learning with RL for LLMs.md`  
**Type:** article  
**Topics:** continual-learning, catastrophic-forgetting, RL, SFT, on-policy, EAFT

Cameron Wolfe survey of recent work showing that on-policy RL naturally resists catastrophic forgetting while SFT consistently degrades prior capabilities. The mechanism is on-policy data generation, not KL regularization — coined "RL's Razor." Also covers EAFT: a lightweight SFT modification (entropy-weighted loss) that nearly matches RL's forgetting resistance without running RL.

---

## Vision Transformers

**File:** `summaries/Vision Transformers - by Cameron R. Wolfe, Ph.D..md`  
**Type:** article  
**Topics:** vision-transformers, ViT, DeiT, CLIP, architecture, multimodal

Cameron Wolfe overview of applying transformers to vision: ViT (patch-based image encoding), DeiT (data-efficient training via CNN knowledge distillation), and CLIP (contrastive multimodal pretraining on 400M image-caption pairs enabling 76.2% zero-shot ImageNet accuracy). ViTs lack CNN inductive biases but scale better with data and compute.

---

## Graph-Based Prompting and Reasoning with Language Models

**File:** `summaries/Graph-Based Prompting and Reasoning with Language Models.md`  
**Type:** article  
**Topics:** prompting, graph-of-thought, CoT, reasoning, GNN

Cameron Wolfe survey of graph-based prompting as a generalization of CoT and ToT. Covers two approaches: GOTR (fine-tuned encoder-decoder with GAT-encoded entity graphs, outperforms GPT-4+CoT on ScienceQA) and GoT (pure prompting framework using thought aggregation/refinement/generation). Graph-based methods enable merging of separate reasoning threads, which linear CoT/ToT cannot express.

---

## The Anatomy of an LLM Benchmark

**File:** `summaries/The Anatomy of an LLM Benchmark.md`  
**Type:** article  
**Topics:** evaluation, benchmarks, MMLU, GPQA, IRT, BIG-Bench, AlpacaEval

Cameron Wolfe survey of how major LLM benchmarks are constructed: MMLU/MMLU-Pro/Redux, GPQA (PhD-level expert-written), BIG-Bench/BBH/BBEH, IFEval/IFBench, AlpacaEval, and frontier math benchmarks. Covers Item Response Theory (IRT) for efficient evaluation (tinyBenchmarks: 140× reduction), fluid benchmarking, and principles for building useful benchmarks that resist saturation and contamination.

---

## Applying Statistics to LLM Evaluations

**File:** `summaries/Applying Statistics to LLM Evaluations.md`  
**Type:** article  
**Topics:** evaluation, statistics, confidence-intervals, power-analysis, benchmarks

Cameron Wolfe statistical framework for rigorous LLM evaluation: standard errors, 95% CIs via CLT, clustered SEs for non-IID questions (can be 3× wider), variance reduction via resampling and token probabilities, paired vs unpaired model comparisons, and power analysis for sample size. Key finding: CLT fails for n < ~100 — use Bayesian methods instead.

---

## AI Agents from First Principles

**File:** `summaries/AI Agents from First Principles.md`  
**Type:** article  
**Topics:** agentic-patterns, ReAct, tool-use, reasoning-models, MCP, multi-agent

Cameron Wolfe's ground-up framework for AI agents. Introduces the Level 0–3 agent spectrum (standard LLM → tool use → problem decomposition → full autonomy), formalizes ReAct as a policy framework (context → action, with language thoughts as first-class actions), covers ReAct+CoT backoff strategies, and identifies "nines of reliability" as the key production bottleneck. Also covers MCP and prior agent work (Inner Monologue, WebGPT, Gato, RAP/MCTS).

---

## LLM Powered Autonomous Agents  Lil'Log

**File:** `summaries/LLM Powered Autonomous Agents  Lil'Log.md`  
**Type:** article  
**Topics:** agentic-patterns, planning, memory, tool-use, ReAct, Reflexion

Lilian Weng's foundational 2023 survey establishing the three-component agent model: Planning (CoT, ToT, ReAct, Reflexion), Memory (human memory taxonomy mapped to LLM components; ANN/MIPS algorithms: LSH, ANNOY, HNSW, FAISS, ScaNN), and Tool Use (MRKL, Toolformer, HuggingGPT). Case studies: ChemCrow (tools can't self-evaluate expert domains) and Generative Agents (25 virtual characters with memory stream, reflection, and retrieval).

---

## Building Multi-Agent Systems (Part 3) - by Shrivu Shankar

**File:** `summaries/Building Multi-Agent Systems (Part 3) - by Shrivu Shankar.md`  
**Type:** article  
**Topics:** multi-agent, agentic-patterns, context-engineering, sandboxes, tool-use

January 2026 practitioner update on how multi-agent architecture has converged: Planner + Execution Agent + ephemeral Task Agents, all in a VM sandbox. Introduces the "code-first" paradigm (agents solve non-coding problems by writing scripts), domain-agnostic harnesses, API/Mount tool design, context engineering (progressive disclosure, indirection, simplification), and three long-context management techniques (TODOs, reminders, automated compaction).

---

## A Practitioners Guide to Retrieval Augmented Generation (RAG)

**File:** `summaries/A Practitioners Guide to Retrieval Augmented Generation (RAG).md`  
**Type:** article  
**Topics:** RAG, retrieval, vector-search, hybrid-search, evaluation, hallucination

Cameron Wolfe practitioner-focused guide to RAG: pipeline stages (cleaning/chunking → indexing → hybrid retrieval → generation), the original RAG paper (Lewis et al. 2020, DPR + BART), RAG vs finetuning for knowledge injection (RAG wins), the lost-in-the-middle context layout problem, RAGAS evaluation framework (faithfulness, answer relevance, context relevance), and iterative improvement tactics.

---

## Using LLMs for Evaluation - by Cameron R. Wolfe, Ph.D.

**File:** `summaries/Using LLMs for Evaluation - by Cameron R. Wolfe, Ph.D..md`  
**Type:** article  
**Topics:** evaluation, llm-as-a-judge, benchmarks, bias, RLAIF, alignment

Cameron Wolfe deep-dive on LLM-as-a-Judge: using a powerful LLM to evaluate other models' outputs. Covers three prompt setups (pairwise, pointwise, reference-guided), key benchmarks (MT-Bench, Chatbot Arena, AlpacaEval/length-controlled), three core biases (position, verbosity, self-enhancement) and mitigation strategies, G-Eval (Auto-CoT + logprob weighting), specialized judge models (Prometheus), and RLAIF (LLM judge as training signal for RLHF).

---

## Mixture-of-Experts (MoE) LLMs - by Cameron R. Wolfe, Ph.D.

**File:** `summaries/Mixture-of-Experts (MoE) LLMs - by Cameron R. Wolfe, Ph.D..md`  
**Type:** article  
**Topics:** MoE, architecture, routing, sparsity, scaling, DeepSeek, Mixtral

Cameron Wolfe deep-dive on MoE-based LLMs: replaces FFN layers with N expert FFNs + a top-K router, decoupling parameter count from compute. Covers routing collapse and three auxiliary losses (importance, load balancing, router z-loss), expert capacity, shared experts (DeepSeek), fine-grained experts (DBRX), and five models: Mixtral 8×7B, Grok-1, DBRX, OpenMoE, DeepSeek-v2/v3. Key DeepSeek innovations: MLA (93% KV cache reduction), MTP training objective, FP8 training, auxiliary-loss-free load balancing.

---

## Experimenting with LLMs to Research, Reflect, and Plan

**File:** `summaries/Experimenting with LLMs to Research, Reflect, and Plan.md`  
**Type:** article  
**Topics:** RAG, retrieval, chunking, hybrid-search, embeddings, agentic-patterns

Eugene Yan's practitioner account (Apr 2023) of building LLM tools on LangChain/Discord, exposing four concrete retrieval failures: sub-optimal ANN tuning (risk: ~50% recall), poor embedding domain transfer (fix: triplet loss fine-tuning), fixed-size chunking producing muddy embeddings (fix: chunk by sections/paragraphs), and embedding-only retrieval phrasing sensitivity (fix: hybrid BM25+semantic + query expansion + reranking). Core framing: LLMs are reasoning engines, not fact databases.

---

## Andrej Karpathy — AGI is still a decade away

**File:** `summaries/Andrej Karpathy — AGI is still a decade away.md`  
**Type:** article  
**Topics:** AGI, continual-learning, model-collapse, RL, cognitive-core, multi-agent

Karpathy interview arguing for calibrated AGI optimism: decade timescale, not months. LLMs are cognitively incomplete (no hippocampus analog, model collapse, RL reward sparsity). Key ideas: cognitive core (~1B param model stripped of encyclopedic memory), LLM culture and self-play as unclaimed capability unlocks, AGI blending into existing 2% GDP growth curve rather than causing discontinuous explosion.
