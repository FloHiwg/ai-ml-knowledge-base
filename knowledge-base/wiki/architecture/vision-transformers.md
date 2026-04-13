# Vision Transformers

**Related:** [[architecture/transformer]] · [[architecture/attention]] · [[concepts/scaling-and-the-bitter-lesson]]  
**Sources:** [[summaries/Vision Transformers - by Cameron R. Wolfe, Ph.D.]]

---

## Core Idea

Apply the transformer encoder directly to images by splitting an image into fixed-size patches and treating each patch as a "token." The self-attention mechanism then captures relationships between any two patches regardless of spatial distance — unlike CNNs, which are inherently local.

---

## ViT — Vision Transformer (Dosovitskiy et al. 2020)

### Patch Embedding

An image of size `H × W` is split into `N = HW / P²` non-overlapping patches of size `P × P` (typically P = 16 or 32). Each patch is flattened and linearly projected to `d_model`:

```
image (H×W×C)  →  N patches (P×P×C)  →  linear projection  →  N token embeddings
```

A learnable `[CLS]` token is prepended — its final state is used for classification (analogous to BERT's CLS token).

**Positional embeddings** (learned, 1D) are added to patch embeddings to preserve spatial order.

### Training Requirements

ViT needs **large pretraining datasets** (JFT-300M, ImageNet-21K) to match CNN performance. With less data, the inductive biases of CNNs (locality, translation equivariance) give them an advantage. ViT relies on data to learn these biases from scratch.

### ViT vs CNN

| | CNN | ViT |
|---|---|---|
| **Inductive bias** | Locality, translation equivariance | Minimal (learned from data) |
| **Small data** | Better | Worse |
| **Large data** | Good | Better |
| **Receptive field** | Grows gradually through layers | Global from layer 1 |
| **Compute** | More efficient (sparse, local) | Less efficient (dense O(n²) attention) |

---

## DeiT — Data-efficient Image Transformers (Touvron et al. 2021)

Training ViT without massive proprietary datasets by introducing a **distillation token**. See [[concepts/distillation]] for how this differs from knowledge distillation and capability distillation.

### Distillation Token

A third learnable token (alongside CLS and patch tokens) whose final state is trained to match the output of a teacher CNN (e.g., RegNet). Two losses:
- CLS token loss: standard cross-entropy against labels
- Distillation token loss: matches teacher's soft predictions (hard label distillation can also be used)

**Result:** ViT-equivalent performance on ImageNet using only ImageNet (1.28M images) — no JFT needed. The distillation token specifically helps the model learn the CNN's spatial inductive biases.

---

## CLIP — Contrastive Language-Image Pretraining (Radford et al. 2021)

### Setup

Train two encoders jointly on 400M image-text pairs from the web:
- **Image encoder:** ViT (or ResNet)
- **Text encoder:** Decoder-only transformer (masked self-attention)

**Contrastive objective:** For each batch of N (image, text) pairs, maximize similarity for the N correct pairs and minimize it for the N² - N incorrect pairs.

Both encoders map to a shared embedding space — similar image-text pairs have high cosine similarity.

### Zero-Shot Classification

Given a new image and class names as text (e.g., "a photo of a cat"):
1. Embed the image with the image encoder
2. Embed each class description with the text encoder
3. Predict the class whose text embedding is most similar to the image embedding

No fine-tuning required for new tasks — just write a new text prompt.

### Why CLIP Matters

- Learns visual concepts from natural language supervision — extremely broad coverage
- Zero-shot transfer rivals supervised models on many benchmarks
- The joint embedding space enables cross-modal search, generation guidance (stable diffusion uses CLIP), and multimodal QA

---

## Key Takeaway

ViTs demonstrate the core [[concepts/scaling-and-the-bitter-lesson|Bitter Lesson]] insight in vision: removing CNN inductive biases and scaling data + compute produces superior results. CLIP extends this to multimodal learning via contrastive pretraining on internet-scale data.
