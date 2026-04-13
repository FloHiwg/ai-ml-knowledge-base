# PEFT and LoRA

**Related:** [[training/fine-tuning]] · [[training/continual-learning]] · [[concepts/agi-and-intelligence]]  
**Sources:** [[summaries/Understanding and Using Supervised Fine-Tuning (SFT) for Language Models]] · [[summaries/Continual Learning with RL for LLMs]]

---

## The Problem PEFT Solves

Full fine-tuning updates every parameter in the model. For a 7B+ parameter model this is:
- **Expensive** — requires storing gradients and optimizer states for all parameters
- **Destructive** — overwrites representations broadly, causing catastrophic forgetting
- **Inflexible** — produces a separate model checkpoint per task

**Parameter-Efficient Fine-Tuning (PEFT)** keeps most weights frozen and only updates a small, targeted subset. The result is cheaper training, less forgetting, and reusable base weights.

---

## LoRA — Low-Rank Adaptation (Hu et al. 2021)

The dominant PEFT technique for LLMs.

### Core Idea

For any weight matrix `W` (shape `d × k`), rather than updating `W` directly, learn a low-rank decomposition of the update:

```
W' = W + ΔW = W + B · A
```

Where:
- `A` has shape `r × k` (randomly initialized)
- `B` has shape `d × r` (initialized to zero, so ΔW = 0 at the start)
- `r` is the **rank** — a small integer (typically 4–64)

During training, `W` is frozen; only `A` and `B` are updated. At inference, `W + BA` can be merged back into `W` — zero added latency.

### Why Low Rank Works

The hypothesis: weight updates during fine-tuning lie in a low-dimensional subspace. Full fine-tuning "wastes" most of its parameter budget on directions that don't matter for the task. LoRA directly parameterizes only the important subspace.

### Parameter Count

```
Full fine-tuning:  d × k  parameters per layer
LoRA:              r × (d + k) parameters per layer
```

For a typical attention projection (`d = k = 4096`, `r = 8`): **LoRA uses ~0.4% of the parameters**.

---

## What to Adapt

LoRA is most commonly applied to the **attention projection matrices** in each transformer layer:

| Matrix | What it does |
|---|---|
| `W_Q` (Query) | Projects input to query space |
| `W_K` (Key) | Projects input to key space |
| `W_V` (Value) | Projects input to value space |
| `W_O` (Output) | Projects concatenated heads back to model dim |

Some implementations also adapt the FFN weight matrices. Empirically, adapting Q and V is often sufficient for instruction-following tasks.

---

## Rank Hyperparameter

`r` controls the expressivity of the adaptation:

| Rank | Use case |
|---|---|
| `r = 4–8` | Simple domain adaptation, style tuning |
| `r = 16–32` | Moderate task specialization |
| `r = 64+` | Complex tasks; approaches full fine-tuning expressivity |

Higher rank → more parameters → more risk of forgetting. For continual learning, keeping `r` small reduces distributional shift.

---

## PEFT and Catastrophic Forgetting

LoRA's frozen base weights are the key mechanism for preserving prior capabilities:

- Gradient updates only flow through the small `A`, `B` matrices
- Base model representations are completely unaffected
- A per-task LoRA adapter can be loaded/unloaded at inference time — effectively a modular multi-task system with shared weights

This makes LoRA a practical alternative to full RL for continual learning when compute is constrained. See [[training/continual-learning]] for empirical comparison with RL-based approaches and EAFT.

---

## Practical Use

HuggingFace `peft` library provides `LoraConfig` and `get_peft_model`:

```python
from peft import LoraConfig, get_peft_model

config = LoraConfig(
    r=16,
    lora_alpha=32,       # scaling factor: ΔW is scaled by lora_alpha / r
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.1,
    bias="none",
)
model = get_peft_model(model, config)
model.print_trainable_parameters()
# trainable params: 4,194,304 || all params: 6,742,609,920 || trainable%: 0.06%
```

`trl.SFTTrainer` accepts a `peft_config` argument directly — no manual wrapping needed.

---

## Other PEFT Approaches

| Method | How it works | Notes |
|---|---|---|
| **LoRA** | Low-rank weight update matrices | Most widely used |
| **Prefix tuning** | Learned "virtual tokens" prepended to each layer's K/V | No weight changes at all |
| **Prompt tuning** | Learned tokens prepended to input only | Minimal params; weaker for large tasks |
| **Adapter layers** | Small bottleneck FFN modules inserted between transformer layers | Original PEFT approach; more latency than LoRA |
| **QLoRA** | LoRA on a 4-bit quantized base model | Enables 65B+ fine-tuning on a single GPU |
