# Pre-Transformer Architectures

**Related:** [[architecture/transformer]] · [[concepts/scaling-and-the-bitter-lesson]]  
**Sources:** [[manual/ML AI Engineering Cheat Sheet]]

---

## Historical Arc

```
Linear Regression / SVM (feature engineering by hand)
    → CNN / RNN (deep learning, learned features)
        → Transformer (parallelizable, global attention)
```

The 2012 ImageNet moment (AlexNet) was the inflection point where deep learning crushed hand-engineered approaches. Transformers then displaced CNNs and RNNs from 2017 onward for most tasks.

---

## CNN — Convolutional Neural Network

A sliding window over local patches — detects local patterns (edges, textures, short phrases).

**Key operations:**
- Convolution with learned filters
- Pooling (max/avg) to reduce spatial resolution
- Multiple layers stack to build increasingly abstract features

**Strengths:**
- Strong spatial inductive biases (locality, translation equivariance)
- Efficient on small data
- Fast inference

**Weaknesses:**
- Limited receptive field (grows slowly through layers)
- Struggles with long-range dependencies in sequences
- Sequence tasks require stacking many layers to capture global context

**Use cases:** Image classification, object detection, feature extraction. AlexNet (2012) breakthrough: moved ImageNet error from ~25% (SVM) to ~15%.

---

## RNN — Recurrent Neural Network

Processes sequences one token at a time, maintaining a hidden state across steps.

```
h_t = f(W_x · x_t + W_h · h_{t-1})
```

**Core limitation: Vanishing gradients.** Gradients shrink exponentially as they propagate back through time. By the end of a long sequence the model has "forgotten" the beginning.

---

## LSTM — Long Short-Term Memory (Hochreiter & Schmidhuber 1997)

Solved the vanishing gradient problem with a **cell state** (long-term memory highway) and three gating mechanisms:

| Gate | Function |
|---|---|
| **Forget gate** | How much of previous cell state to discard |
| **Input gate** | What new information to write to cell state |
| **Output gate** | What part of current state to expose as hidden state |

The cell state can carry information across many steps without modification — gradients flow back through it cleanly.

**Limitation:** Still sequential (slow to train), and still struggles with very long sequences.

---

## GRU — Gated Recurrent Unit (Cho et al. 2014)

Simplified LSTM — merges cell state and hidden state into one, uses two gates:

| Gate | Function |
|---|---|
| **Reset gate** | How much of past to ignore |
| **Update gate** | How much of past state to keep vs. new input |

Nearly identical performance to LSTM with fewer parameters and simpler implementation.

---

## CNN vs RNN vs Transformer (Sequence Modeling)

| | CNN | RNN/LSTM | Transformer |
|---|---|---|---|
| **Parallelizable** | Partial | No (sequential) | Yes |
| **Long-range deps** | Poor | Moderate | Excellent |
| **Training speed** | Fast | Slow | Fast (parallel) |
| **Data efficiency** | Good | Good | Needs more data |
| **Dominant since** | 2012 | ~2014 | 2017+ |

---

## GAN — Generative Adversarial Network (Goodfellow 2014)

Two networks in competition:
- **Generator** — creates fake samples trying to fool the Discriminator
- **Discriminator** — distinguishes real from fake

The adversarial loop forces the generator to produce increasingly realistic outputs.

**Relevance today:** Largely superseded by diffusion models for image generation, but the adversarial training concept influenced RLHF/reward model training indirectly.

---

## Regularization Techniques (Era-spanning)

### Dropout

During training, randomly zero out a fraction of activations (typically 20–50%) per forward pass. Forces neurons to learn independently; prevents co-adaptation and overfitting.

### Batch Normalization / Layer Normalization

- **BatchNorm:** Normalize across the batch dimension — effective for CNNs
- **LayerNorm:** Normalize across the feature dimension of a single sample — used in transformers (no dependence on batch size)
