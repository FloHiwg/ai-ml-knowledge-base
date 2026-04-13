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

## Andrej Karpathy — AGI is still a decade away

**File:** `summaries/Andrej Karpathy — AGI is still a decade away.md`  
**Type:** article  
**Topics:** AGI, continual-learning, model-collapse, RL, cognitive-core, multi-agent

Karpathy interview arguing for calibrated AGI optimism: decade timescale, not months. LLMs are cognitively incomplete (no hippocampus analog, model collapse, RL reward sparsity). Key ideas: cognitive core (~1B param model stripped of encyclopedic memory), LLM culture and self-play as unclaimed capability unlocks, AGI blending into existing 2% GDP growth curve rather than causing discontinuous explosion.
