# Using LLMs for Evaluation - by Cameron R. Wolfe, Ph.D.

**Source:** [[raw/articles/Using LLMs for Evaluation - by Cameron R. Wolfe, Ph.D.]]
**Author:** Cameron R. Wolfe, Ph.D.
**Related:** [[summaries/The Anatomy of an LLM Benchmark]] · [[summaries/Applying Statistics to LLM Evaluations]] · [[summaries/Understanding and Using Supervised Fine-Tuning (SFT) for Language Models]]

---

## Core Idea

LLM-as-a-Judge is a scalable evaluation strategy that directly prompts a powerful LLM to assess the quality of another model's output. It fills the gap between expensive, slow human evaluation and unreliable legacy metrics (ROUGE, BLEU) that correlate poorly with human preferences for open-ended tasks. When implemented carefully — using strong judges, bias mitigation, and CoT prompting — LLM-as-a-Judge achieves ~80% agreement with human annotators, matching inter-annotator agreement among humans themselves.

---

## The LLM-as-a-Judge Technique

### What it is

A reference-free evaluation metric introduced after GPT-4's release. Rather than matching against a gold-standard output, a capable LLM (the "judge") is prompted to score one or more model responses, producing a structured evaluation.

### Three Prompt Setups

| Setup | Description | Trade-offs |
|---|---|---|
| **Pairwise comparison** | Judge picks the better of two responses | Most reliable; doesn't scale to many models |
| **Pointwise scoring** | Judge assigns a score (e.g., Likert 1–5) to a single response | Scalable; less stable (absolute scores fluctuate) |
| **Reference-guided** | Judge gets a reference solution alongside responses | Better for math/coding; requires ground truth |

### Combining with CoT

Appending a zero-shot CoT instruction ("explain your reasoning before scoring") improves accuracy. Critically, the rationale should come **before** the score — rationales generated *after* the score are not supported by the conclusion (from [16]).

### Does it work?

GPT-4 achieves **80% agreement with human preference scores** on MT-Bench, matching the 80% inter-annotator agreement rate among humans. AlpacaEval with length-controlled scoring achieves a **0.98 Spearman correlation** with Chatbot Arena (human-based leaderboard).

---

## Key Benchmarks and Platforms

### MT-Bench
- 80 high-quality questions across 8 genres (writing, roleplay, extraction, reasoning, math, coding, STEM, humanities)
- Focused on multi-turn conversation and instruction following
- Developed alongside the LLM-as-a-Judge paper [17]

### Chatbot Arena
- Crowdsourced battle platform: users interact with two unknown LLMs and pick a winner
- No predefined questions — diverse, real-world use cases
- Rankings via Elo scores; >1.5M pairwise preferences collected for >100 models
- One of the most widely-referenced LLM leaderboards

### AlpacaEval
- 805 instructions; LLM judge compares candidate model vs. a baseline (pairwise win-rate)
- Runs in <3 minutes, costs <$10
- **Length-controlled AlpacaEval** adds regression-based debiasing to neutralize verbosity bias, improving Spearman correlation from 0.94 → 0.98 with Chatbot Arena
- Used in the public leaderboard; cannot be significantly gamed by verbosity alone

---

## Sources of Bias

Three core biases documented in [17]:

1. **Position bias** — judge favors responses based on position in the prompt (GPT-4 prefers first; ChatGPT prefers second). Vicuna-13B win-rate over ChatGPT varied from 2.5% to 82.5% purely by switching position [16].
2. **Verbosity bias** — longer outputs receive higher scores independent of quality.
3. **Self-enhancement bias** — judge assigns higher scores to outputs from its own model family (GPT-4 preferred GPT-4-generated responses in 87.76% of cases vs. 47.61% for humans).

Additional weaknesses:
- Judges struggle with questions they cannot answer themselves (math, complex reasoning)
- Judges can be misled by incorrect information present in the responses being evaluated [18]

### Bias Mitigation Techniques

| Technique | Description |
|---|---|
| **Position switching trick** | Randomize output positions; average scores across orderings |
| **Few-shot calibration** | Provide examples to anchor the judge's internal scoring scale |
| **Reference answers** | Supply correct solutions for hard math/reasoning questions |
| **Multiple judges** | Use Claude, Gemini, GPT-4 together to dilute self-enhancement |
| **Grading rubric** | Explain what each score level means in the prompt |
| **Logprob weighting** | Compute weighted average across score probabilities (G-Eval approach) |
| **Low temperature** | Use ~0.1 for determinism; same temperature across all comparisons |

---

## Early Work and Adoption History

### Sparks of AGI (GPT-4 paper, [1])
- First paper to use GPT-4 as an evaluator (one page of analysis, less than 10 days after GPT-4 release)
- Found GPT-4 preferred GPT-4-generated responses 87.76% of the time vs. 47.61% for humans — early evidence of self-enhancement bias
- Concluded that more calibration research was needed

### Vicuna [2]
- First mainstream use of GPT-4 as an evaluator for a finetuned model
- Setup: 80 questions across 8 categories; GPT-4 assigns 1–10 scores to two responses simultaneously; preference inferred from score differential
- Found Vicuna preferred over other open-source models 90% of time; positional bias confirmed by later work [8]
- Prompts explicitly asked GPT-4 to avoid positional bias; separate prompts for coding/math

### LIMA [3]
- Used both human and GPT-4 pairwise evaluation
- Found 1,000 curated SFT examples sufficient for strong alignment — **Superficial Alignment Hypothesis**: pretraining provides the knowledge; alignment teaches output format
- LIMA matched or exceeded GPT-4 on 34–43% of prompts

### Guanaco / QLoRA [4]
- Used both pairwise scoring (like Vicuna) and direct pairwise comparison (3-class: A better / B better / tie)
- GPT-4 demonstrated clear first-position bias, corrected via position switching trick
- "GPT-4 evaluations are a cheap and reasonable alternative to human evaluation… current chatbot benchmarks are not trustworthy"

### False Promise of Imitating LLMs [5]
- Imitation models (fine-tuned on GPT-4/ChatGPT outputs) mimic style but not factuality
- Both human and GPT-4 evaluations consistently showed that increasing base model size outperforms collecting more imitation data

---

## Key Analysis Papers

### Can LLMs Be an Alternative to Human Evaluation? [11]
- First rigorous study comparing human and LLM evaluation on story generation
- Same instructions and rubric given to both human annotators (English teachers) and LLMs
- Results: sufficiently powerful LLMs detect aggregate quality differences consistently with humans; per-instance correlation weaker
- Recommendation: use LLM evaluation for fast iteration during development; use human evaluation before deployment

### G-Eval [13]
- Two improvements over prior work:
  1. **Auto-CoT**: LLM first generates a set of evaluation steps from task description, then uses those steps as context when scoring
  2. **Weighted scoring via logprobs**: final score = weighted average of scores, weighted by token probabilities
- Achieves Spearman correlation of 0.514 with human ratings on summarization — a major leap
- Limitations: prompt-sensitive; self-enhancement bias present; integer score clustering

### Large Language Models Are Not Fair Evaluators [16]
- Deep quantitative study of position bias with ChatGPT and GPT-4
- GPT-4 biased toward first response; ChatGPT biased toward second
- Proposed two mitigation strategies:
  1. **Multiple-Evidence Calibration**: generate CoT evidence before scoring
  2. **Balanced Position Calibration**: generate evidence+score multiple times with switched positions

---

## Advanced Topics

### Specialized Judge Models
- **Prometheus** [19, 20]: open-source LLM finetuned specifically for fine-grained evaluation
- Other specialized judges: JudgeLM [21], PandaLM [22], Generative Judge [23]
- LLaMA-3 release made open-source judges competitive with proprietary ones

### RLAIF (Reinforcement Learning from AI Feedback)
- Use LLM-as-a-Judge to generate synthetic preference pairs for RLHF training
- Explored by Lee et al. [24] and Constitutional AI [25]
- Rumored to be heavily used in top industry labs
- See also: [[summaries/Demystifying Reasoning Models - by Cameron R. Wolfe, Ph.D.]]

---

## Practical Implementation Guidance

- **Pointwise scoring**: add a grading rubric and/or few-shot examples; use logprob-weighted scoring
- **Pairwise comparison**: use position switching; average over both orderings
- **Temperature**: 0.1 for deterministic scoring; slightly higher when sampling multiple scores for calibration
- **CoT**: always ask for rationale *before* score; zero-shot CoT is sufficient
- **Hard tasks**: supply reference answers for math/reasoning in the prompt
- **Multi-judge**: use 2–3 different judge models to reduce self-enhancement bias

---

## Key Takeaways

- LLM-as-a-Judge is the dominant fast-iteration evaluation strategy for modern LLMs — alongside human evaluation
- GPT-4-class judges achieve human-level inter-annotator agreement (~80%) on preference tasks
- Three main biases to always address: position, verbosity, self-enhancement
- Position switching trick (randomize + average) is the most important single mitigation
- Never use LLM-as-a-Judge in isolation — pair it with targeted human evaluation for deployment decisions
- AlpacaEval (length-controlled) is the benchmark with highest correlation to human preferences (Spearman 0.98)
- RLAIF turns LLM-as-a-Judge into a training signal: synthetic preference data for RLHF
