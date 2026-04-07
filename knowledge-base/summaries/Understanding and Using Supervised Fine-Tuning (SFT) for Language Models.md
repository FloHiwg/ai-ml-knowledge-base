# Understanding and Using Supervised Fine-Tuning (SFT) for Language Models

**Source:** [[raw/articles/Understanding and Using Supervised Fine-Tuning (SFT) for Language Models]]  
**Author:** Cameron R. Wolfe  
**Related:** [[summaries/Direct Preference Optimization (DPO)]] · [[raw/articles/Language Model Training and Inference From Concept to Code]] · [[raw/articles/Language Models GPT and GPT-2 - by Cameron R. Wolfe, Ph.D.]]

---

## What it is

SFT is the first alignment step after pretraining. It fine-tunes a pretrained LLM on a curated dataset of high-quality (prompt, response) examples, teaching the model to emulate the correct style and behavior.

The training objective is identical to pretraining — **next token prediction** — but applied to a small, supervised dataset rather than raw internet text. The loss is typically computed only on the response tokens, not the prompt.

> *"The supervised aspect of fine-tuning comes from the fact that we are collecting a dataset of examples that the model should emulate."*

---

## Where SFT fits in the training pipeline

```
Pretraining  →  SFT  →  RLHF / DPO
(internet-scale     (alignment    (preference
 text, expensive)    step 1)       step 2)
```

This three-step framework was introduced by **InstructGPT** [Ouyang et al., 2022] and is now the standard for most LLMs (ChatGPT, LLaMA-2, etc.). Pretraining is orders of magnitude more expensive; SFT costs roughly 100× less compute.

SFT produces the **reference policy (π_ref)** used by downstream preference-tuning algorithms like DPO and PPO-based RLHF. See [[summaries/Direct Preference Optimization (DPO)]].

---

## Pros

- **Simple** — same objective as pretraining, minimal implementation overhead.
- **Cheap** — ~100× less compute than pretraining; a few hundred dollars vs. hundreds of thousands.
- **Effective** — measurably improves instruction following, coherence, and correctness even without any RLHF.
- **Generic** — unlike task-specific fine-tuning, SFT preserves the model's broad capabilities (it teaches style/behavior, not a narrow skill).

## Cons

- **Dataset quality is the bottleneck** — results depend heavily on the curation of training examples. Bad data → bad alignment.
- **Hard to guarantee coverage** — no systematic way to verify that all desired behaviors are represented without expensive manual inspection.
- **Not sufficient alone** — RLHF on top of SFT consistently yields further gains, especially for helpfulness and safety (demonstrated clearly by LLaMA-2).
- **Dataset generation has limits** — automated generation (e.g. Self-Instruct) helps scale data but doesn't guarantee quality.

---

## Dataset: Quality and Diversity over Size

**LIMA** [Zhou et al., 2023] demonstrated that a carefully curated dataset of only **1,000 examples** produces a model competitive with top LLMs trained on far more data. Key finding: **quality and diversity matter more than raw dataset size**.

LLaMA-2 corroborates this: a moderately-sized, high-quality SFT dataset outperforms a larger but noisier one. After SFT, the model can generate dialogue sessions comparable in quality to human-written ones, meaning collecting more SFT data has diminishing returns — it's better to invest in RLHF preference data instead.

---

## Practical Use Cases

**Imitation learning** — fine-tune an open-source base model on outputs from a proprietary model (ChatGPT, GPT-4):
- Early examples: Alpaca, Koala, Vicuna (cheap, surprisingly good, but later shown to underperform on deeper evaluation)
- Better approach: larger/richer imitation sets — e.g. **Orca** [Mukherjee et al., 2023]

**Open-source alignment** — most early aligned open models (MPT-Instruct, Falcon-Instruct, LLaMA-Instruct) relied on SFT alone, without RLHF.

---

## Implementation

**Tooling:** HuggingFace `trl.SFTTrainer` — wraps the transformers library, handles dataset formatting, response-only loss masking, and PEFT integration.

```python
from trl import SFTTrainer

trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=512,
)
trainer.train()
```

**Advanced options supported by SFTTrainer:**
- Response-only supervision (ignore prompt tokens in loss)
- Shared prompt templates applied across examples
- **LoRA / PEFT** [Hu et al., 2021] — parameter-efficient fine-tuning that updates only a small set of adapter weights, drastically reducing memory and compute requirements

---

## Key Takeaways

- SFT = next token prediction on a supervised dataset of desirable (prompt, response) pairs.
- It is cheap, simple, and effective — but only a starting point for alignment.
- Dataset **quality and diversity** are the key variables; size matters less.
- SFT sets up the reference policy for RLHF/DPO. The better the SFT model, the stronger the starting point for preference tuning.
- After SFT, further investment in **preference data + RLHF/DPO** (not more SFT data) is the optimal path to higher-quality alignment.
