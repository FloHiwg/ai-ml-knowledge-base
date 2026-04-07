# Foundation Models

**Related:** [[training/pretraining]] · [[training/fine-tuning]] · [[concepts/scaling-and-the-bitter-lesson]]  
**Sources:** [[summaries/Language Models GPT and GPT-2 - by Cameron R. Wolfe, Ph.D.]] · [[summaries/Understanding and Using Supervised Fine-Tuning (SFT) for Language Models]]

---

## The Core Insight

Instead of training a new narrow expert for every task (expensive, requires labeled data), pretrain one large model on abundant unlabeled text, then adapt it. The pretrained model is the "foundation" — it encodes broad knowledge and general capabilities.

> *"The pretrained model has learned representations that transfer broadly without ever seeing task labels."*

---

## The Pretrain-Then-Adapt Paradigm

```
1. Pretraining (one-time, expensive)
   Massive unlabeled text corpus → next token prediction
   Result: broad world knowledge, language understanding, reasoning

2. Adaptation (cheap, repeatable)
   Supervised fine-tuning, RLHF, DPO, or just prompting
   Result: model aligned to specific task, format, or preference
```

The split matters because:
- Pretraining amortizes compute across many downstream tasks
- Labels are scarce and expensive; unlabeled text is abundant
- General representations transfer further than task-specific ones

---

## Why Pretraining Works as a Universal Objective

Next token prediction is deceptively powerful. To predict the next token well, the model must develop:
- **Syntax:** grammatical structure
- **Semantics:** word meaning, entity relationships
- **Pragmatics:** discourse coherence, coreference
- **World knowledge:** facts, events, reasoning patterns
- **Task generalization:** recognize patterns of Q&A, instructions, code, math from training data

The model doesn't need labels — it learns by predicting what comes next in text produced by humans performing all of these tasks.

---

## The GPT Evolution as a Case Study

| | GPT | GPT-2 | GPT-3 |
|---|---|---|---|
| Human engineering required | Fine-tune per task | None (zero-shot) | None (few-shot) |
| Adaptation method | Gradient update on labeled data | Natural language prompt | In-context examples |
| Scaling takeaway | Pretraining transfers | Scale enables zero-shot | Scale enables few-shot |

Each step removed the need for more human-curated data and engineering. The pretrained model became increasingly self-sufficient.

---

## Transfer Learning vs Foundation Models

| | Traditional Transfer Learning | Foundation Models |
|---|---|---|
| Pretrained on | ImageNet (1.28M labeled images) | Billions of unlabeled tokens |
| Task coverage | Vision only (often) | Language, code, vision, reasoning |
| Adaptation | Often fine-tune entire network | Often prompting alone suffices |
| Generalization | Limited to similar visual domain | Broad cross-domain |

---

## Emergent Capabilities

Behaviors that appear suddenly at certain scale thresholds — not present at smaller sizes, present at larger:
- Chain-of-thought reasoning
- Multi-step arithmetic
- In-context learning from few examples

This is partly why GPT-2 (1.5B) showed consistent improvement across all tasks — the models were still in the "emergence ramp" and continued improving with scale.

---

## Alignment: Making Foundation Models Useful

A pretrained foundation model generates plausible text continuations — it's not inherently helpful or safe. Alignment stages bridge this:

1. **SFT:** Teach the model the format and style of helpful responses
2. **RLHF / DPO:** Align to human preferences — reinforce helpful, harmless, honest responses

See [[training/fine-tuning]] for details on each stage.
