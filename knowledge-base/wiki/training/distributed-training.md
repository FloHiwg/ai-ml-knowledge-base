# Distributed Training

**Related:** [[training/pretraining]] · [[training/optimization]]  
**Sources:** [[summaries/Language Model Training and Inference From Concept to Code]]

---

## Why Distribute?

1. **Speed:** Pretraining takes weeks/months on one GPU; thousands of GPUs shorten this to days
2. **Model size:** Modern LLMs (7B–700B+ parameters) don't fit in a single GPU's memory

---

## DDP — Distributed Data Parallel

Each GPU holds a **complete copy** of the model. Training data is split across GPUs:

```
GPU 0: model copy A → forward(batch_0) → gradient_0
GPU 1: model copy B → forward(batch_1) → gradient_1
...
All-reduce: average gradients across all GPUs
Each GPU applies the same averaged gradient update
```

**Requirement:** The full model must fit on a single GPU.  
**Used by:** NanoGPT, most training runs up to ~7B parameters.

```python
# NanoGPT DDP setup
ddp = int(os.environ.get('RANK', -1)) != -1
if ddp:
    ddp_rank = int(os.environ['RANK'])
    ddp_world_size = int(os.environ['WORLD_SIZE'])
    model = DDP(model, device_ids=[ddp_local_rank])
```

---

## FSDP — Fully Sharded Data Parallel

The model's parameters, gradients, and optimizer states are **sharded** across all GPUs — each GPU only holds a slice of the model.

During the forward/backward pass, GPUs communicate via all-gather to reconstruct needed parameters on-the-fly, then release them.

**Enables:** Training models too large for a single GPU  
**Used by:** Most large model training (Llama, etc.)  
**Trade-off:** More inter-GPU communication overhead than DDP

---

## Gradient Accumulation

Simulates a large batch size without needing the memory to hold it:

```
for micro_step in range(grad_accum_steps):
    loss = model(batch[micro_step])
    loss.backward()               # accumulate gradients (don't zero yet)

optimizer.step()                  # update weights with accumulated gradient
optimizer.zero_grad()
```

**Effective batch size** = micro-batch size × grad_accum_steps × num_GPUs

Useful when your desired batch size (e.g., 512 sequences) doesn't fit in memory at once.

---

## AMP — Automatic Mixed Precision

Runs most computation in `float16` / `bfloat16` (faster, less memory) while accumulating gradients in `float32` (more numerically stable):

```python
scaler = torch.cuda.amp.GradScaler()

with torch.autocast(device_type='cuda', dtype=torch.bfloat16):
    logits, loss = model(x, y)

scaler.scale(loss).backward()
scaler.unscale_(optimizer)
torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
scaler.step(optimizer)
scaler.update()
```

**Gradient scaling:** `float16` can underflow to zero for small gradients. The `GradScaler` multiplies the loss before backward (scaling up gradients), then divides before the optimizer step (scaling them back down). This keeps gradients in `float16`'s representable range.

**`bfloat16` vs `float16`:** `bfloat16` has the same range as `float32` (less underflow risk) but lower precision. Preferred for training on modern hardware (A100, H100).

---

## Gradient Clipping

Cap the global gradient norm to prevent explosive updates:

```python
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
```

Common in LLM training alongside AMP. Run **after** `scaler.unscale_()` so the gradient is in its true scale before clipping.

---

## Comparison

| Method | Model fits on 1 GPU? | Use case |
|---|---|---|
| Single GPU | Yes | Development, small models |
| DDP | Yes | Medium models (up to ~7B) |
| FSDP | No required | Large models (70B+) |
| Tensor / Pipeline Parallelism | No | Very large models, specialized setups |
