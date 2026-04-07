# Vision Transformers

**Source:** [[raw/articles/Vision Transformers - by Cameron R. Wolfe, Ph.D.]]  
**Author:** Cameron R. Wolfe  
**Related:** [[raw/articles/Language Models GPT and GPT-2 - by Cameron R. Wolfe, Ph.D.]] · [[raw/articles/Language Model Training and Inference From Concept to Code]]

---

## What it is

Vision Transformers (ViTs) apply the standard transformer encoder architecture — originally designed for NLP — to image classification by converting images into sequences of flattened patches. Despite lacking CNN-specific inductive biases, they match or exceed CNN performance when trained at sufficient scale.

---

## Background: The Transformer Architecture

A transformer processes a sequence of token embeddings through stacked layers, each containing:
- **Multi-headed self-attention** — for each token, computes a weighted average over all other tokens in the sequence, where weights reflect pairwise relevance. Running multiple attention heads in parallel and concatenating their outputs captures diverse relationships.
- **Feed-forward network** — a two-layer MLP applied independently to each token.
- **Layer norm + residual connections** around each module.

**Positional embeddings** are added to the input tokens because self-attention is permutation-invariant — it has no inherent notion of order or position.

**Encoder vs. decoder:**
- *Encoder* — bidirectional attention; each token attends to all others. Used for understanding/classification tasks.
- *Decoder* — masked (causal) attention; each token only attends to preceding tokens. Used for generation. ViTs are encoder-only.

Self-supervised pretraining (e.g. masked token prediction, as in BERT) dramatically boosted NLP transformers but has been less successful for ViTs.

---

## ViT: An Image is Worth 16×16 Words [Dosovitskiy et al., 2020]

**Key idea:** Treat an image as a sequence of fixed-size patches, the same way NLP treats text as a sequence of tokens.

**Pipeline:**
1. Divide image into `N` non-overlapping patches (e.g. 16×16 pixels each).
2. Flatten and linearly project each patch to dimension `d`.
3. Prepend a learnable `[CLS]` token.
4. Add positional embeddings to each patch token.
5. Pass the full sequence through a standard BERT-style encoder.
6. Attach a classification head to the `[CLS]` token output.

**Key finding — data hunger:** Without large-scale pretraining, ViTs underperform CNNs. CNNs have built-in inductive biases (translation invariance, locality) that ViTs must learn from data. With enough pretraining data (JFT-300M → ImageNet-21K → ImageNet-1K), ViTs surpass CNN baselines at lower compute cost.

---

## DeiT: Data-Efficient Image Transformers [Touvron et al., 2021]

**Problem solved:** ViT required pretraining on massive external datasets (e.g. JFT-300M, 300M images). DeiT achieves competitive performance training only on ImageNet-1K in ~3 days on a single machine.

**How:** Knowledge distillation from a CNN teacher using a **distillation token**:
- Add a distillation token to the input sequence alongside the `[CLS]` token.
- After the final layer, train the distillation token to match the argmax output of the CNN teacher (hard distillation).
- At inference, fuse the `[CLS]` and distillation token outputs for the final prediction.

**Result:** Accuracy competitive with ViTs pretrained on external data; throughput comparable to EfficientNet. ViTs are now practical without massive pretraining infrastructure.

---

## CLIP: Learning Transferable Visual Models from Natural Language Supervision [Radford et al., 2021]

**Key idea:** Pretrain on 400M noisy image-caption pairs from the internet using a contrastive objective — instead of predicting captions word-by-word, match each image to the correct caption among a batch of candidates.

**Architecture:**
- **Image encoder** — ViT or ResNet.
- **Text encoder** — decoder-only transformer (masked self-attention).
- Both encoders map their inputs to a shared embedding space.

**Training objective:** Normalized temperature-scaled cross-entropy (NT-Xent) — maximize cosine similarity between matched image-caption pairs, minimize it for all other pairs in the batch.

**Zero-shot classification:** Encode each class name with the text encoder; pick the class whose embedding is most similar to the image embedding. Improved zero-shot ImageNet accuracy from 11.5% → **76.2%**.

CLIP's representations are foundational to multimodal models (DALL-E 2, etc.).

---

## ViTs vs. CNNs

| | CNNs | Vision Transformers |
|---|---|---|
| Inductive biases | Translation invariance, locality | None — must be learned from data |
| Data efficiency | High | Lower (needs more data to match CNNs) |
| Scalability | Good | Better — performance keeps improving with more data/compute |
| Self-supervised pretraining | Limited | Active research area (less mature than NLP) |
| Practical efficiency | EfficientNet is highly optimized | DeiT shows comparable throughput |

---

## Key Takeaways

- ViTs reuse the NLP transformer architecture almost unchanged — the only adaptation is the patch embedding step.
- The lack of inductive bias is both a weakness (needs more data) and a strength (scales better with data/compute), echoing [[summaries/The Bitter Lesson]].
- DeiT showed ViTs are practical without massive external pretraining budgets.
- CLIP extended the idea to multimodal representation learning, enabling zero-shot transfer at scale.
- **Tooling:** `huggingface/transformers` supports pretrained ViT weights and fine-tuning via the standard trainer API.
