# Models

## Linear Regression

Model to come up with a polynomial formula to

## SVM (90s - 10s)

Finding a hyperplane, which is a boundary between different categories. Feature engineering was mostly done manually.

## Deep Learning and Neural Networks

With increase in computing power the reliance on humans engineering the features got lower and it was possible to let the model discover the features by it self.

Sputnik moment was 2012 with ImageNet Challenge. SVMs plateaued at a error rate of 25%. AlexNet based on CNNs moved this to 15%.

Mostly possible because of the data set size that Fei Fei Li at Stanford build up. Furthermore they realized that GPUs are perfectly suited for training the model.

ReLU and Dropout got added as further tricks that simplified and improved the performance.

### CNN

While famous for image recognition, CNNs were used in NLP to find local patterns. Think of a CNN as a sliding window looking at 3–5 words at a time to identify key phrases. They were fast but struggled with long-distance relationships between words at the beginning and end of a paragraph.

### RNN

RNNs were designed specifically for sequences. They process words one by one, maintaining a "hidden state" (a memory) of what they’ve seen before.

- **The Flaw:** They suffer from **vanishing gradients**. By the time an RNN reaches the end of a long sentence, it often "forgets" the beginning.

**LSTM - Long Short-Term Memory (1997)**

Introduced in 1997, the LSTM was the first real solution to the "vanishing gradient" problem (where AI would "forget" the beginning of a long sentence).

The "Cell State": Think of this as a long-term memory highway that runs through the entire sequence.

The Three Gates:

- Forget Gate: Decides what information from the past is no longer relevant and should be deleted.
- Input Gate: Decides which new information is worth adding to the long-term memory.
- Output Gate: Decides what part of the current memory should be used as the output for this specific step.

**GRU - Gated Recurrent Unit (2014)**

Introduced in 2014, the GRU is a "lite" version of the LSTM. It achieves almost identical results but with a simpler, faster design.

Simplified Memory: It combines the long-term and short-term memory into a single "hidden state."

**The Two Gates:**

- Reset Gate: Decides how much of the past information to forget (similar to the LSTM's forget gate).
- Update Gate: Decides how much of the previous state to keep and how much new information to mix in.

### GANs - Generative Adversarial Networks

Introduced by Ian Goodfellow in 2014, a GAN isn't just one model; it’s two neural networks locked in a game of cat-and-mouse.

The magic is in the adversarial loop.

- The Generator tries to fool the Detective.
- The Detective gets better at spotting the flaws.
- Because the Detective got better, the Generator is forced to get even better to keep fooling it.
- Eventually, the Generator becomes so good that the "fakes" are indistinguishable from reality.

## Transformers

With the paper “Attention Is All You Need” the world has changed and in favor of the one word at a time sequential systems and models a parallelizable system got introduced.

Secret sauce is self attention

The "Query, Key, Value" (QKV) Framework

To do this, the Transformer uses a mathematical trick similar to a retrieval system:

- Query ($Q$): What am I looking for? (e.g., "I am the word 'it', what do I refer to?")
- Key ($K$): What do I offer? (e.g., "I am 'animal', I am a noun that can be tired.")
- Value ($V$): What is my actual content?

There are three reasons why Transformers killed off almost every other architecture:

- Parallelization: Because they don't process words sequentially, we can train them on thousands of GPUs simultaneously. This allowed us to train on the entire internet instead of just small datasets.
- No Recurrence: They don't have "memory" that fades over time. A Transformer can see the first word and the millionth word of a document with equal clarity.
- Positional Encodings: Since the model sees the whole sentence at once, it doesn't naturally know the order of words. Researchers solved this by "tagging" each word with a mathematical signal (a wave function) that tells the model exactly where that word sits in the sequence.

### BERT - Bidirectional Encoder Representations

Reading from left to right and right to left and filling in blanks.

Architecture: Encoder-Only

BERT is designed to understand language. It reads a sentence in both directions simultaneously (left-to-right and right-to-left). This allows it to understand the deep context of a word based on everything that comes before and after it.

How it "Studies":
- It uses Masked Language Modeling (MLM). It hides random words in a sentence (like a fill-in-the-blank test) and tries to guess them.
- Best For: Search engines (Google uses BERT), sentiment analysis, and "understanding" if a word like "bank" refers to a river or a building.
- Vibe: The high-speed researcher who reads a whole page at once to find the one fact you need.

Usage:
- Still used at Google to understand the meaning of a query for their DeepRank algorithm
- Also used in RAG use cases to find the right content in a data realm

### GPT - Generative Pre-trained Transformer

Architecture: Decoder-Only

GPT is designed to generate language. Unlike BERT, it reads strictly from left-to-right. This "one-way" constraint is actually its superpower because it mimics how humans write: one word at a time.

- How it "Studies": It uses Causal Language Modeling (CLM). It looks at a string of words and tries to predict the single most likely next word.
- Best For: Chatbots (ChatGPT), writing essays, coding, and creative brainstorming.
- Vibe: The eloquent novelist who can start with a single sentence and spin an entire universe out of it.

### Why GPT and not BERT for generation? 

The task that was used to train BERT was not as much as GPT related to generating new text and new content.

## Bitter lesson (Rich Sutton)

**Core Thesis:** In the long run, the only thing that matters in AI is leveraging **computation**. Human-designed "tricks," rules, and specialized knowledge (heuristics) consistently lose to general-purpose methods that scale with Moore's Law.

**Key Takeaways:**

- **The Failure of Human Intuition:** Researchers often try to "help" AI by hard-coding how humans think (e.g., grammar rules or edge detection). This provides a short-term boost but creates a long-term performance ceiling.
- **The Power of General Methods:** Two types of methods consistently win as compute increases:
    - 1. **Search** (e.g., Deep Blue in Chess).
    - 2. **Learning** (e.g., Deep Learning and Transformers).
- **Historical Evidence:**
    - _Computer Vision:_ Hand-coded features were crushed by Deep Learning (ImageNet 2012).
    - _NLP:_ Rule-based translation and RNNs were crushed by Transformers and Scaling.
- **The "Bitter" Reality:** Progress in AI is rarely driven by a "smarter" human design, but by the relentless application of more data and more compute to simple, scalable algorithms.

## Regularization Function

### Dropout

Dropout is a regularization method. Preventing the model from memorizing the test answers (overfitting).

The Logic: During training, Dropout randomly "kills" a certain percentage of neurons (usually 20% to 50%) in each layer for a single pass.

The Benefit: Since a neuron can't rely on its "neighbors" to be there, it is forced to learn useful features on its own. It prevents a few "star" neurons from doing all the work, making the whole network more robust and better at handling new, unseen data.

## Activation Function

### ReLU

ReLU (Rectified Linear Unit) is the mathematical gatekeeper of a neuron. Before ReLU, we used functions like Sigmoid or Tanh, which were "curvy" and caused gradients to disappear (the vanishing gradient problem).

The Math: $f(x) = \max(0, x)$

How it works: If the input is negative, the output is 0 (the neuron stays dark). If the input is positive, the output is the exact same value as the input.

Why we love it: It is computationally "cheap" (fast) and allows the model to learn complex, non-linear relationships without getting "stuck" during training.

### Tanh

### Sigmoid

# Agentic Patterns

## Prompt Chaining

- Breaking down complex tasks into smaller chunks
- Frameworks can help to enable this multistep sequence

## Routing

- Implementation of routers
    - LLM based
    - Embedding based
    - Rule based
    - ML model based

## Parallelization

- starting multiple agents off and collecting them like threads
- Improved performance and reduced waiting

## Reflection

- execution → critique → reflection → iteration
- separation of concerns can fundamentally improve the output

## Tool use

- Process
    1. Tool definitions gets to the model
    2. LLM decides to call the tool
    3. Generates the function call
    4. Tool gets executed from a third party service
    5. Output is returned to the agent
    6. The LLM uses this to generate a final response
- When?
    - Whenever the LLM needs to break out of the internal knowledge

## Planning

- When the request is too complex to be handled by a single action or tool
- Plan multiple steps and use things like a todo list or similar
- Prompting to plan first can help as well to trigger a internal processing part

## Multi Agent Collaboration

- Pattern of interaction
    - Sequential hand off
    - Parallel processing
    - Debate and consensus → different sources and view points and come up with one reply
    - Hierarchical structures → one supervisor
    - Expert team → Collaboration of different specialists
    - Critic reviewer → one group produces and second critics it
- Communication structures
    - Single agent
    - Network → Everyone can talk to everyone
    - Supervisor → One coordinates and delegates like a star
    - Supervisor as tool → Providing resources guidance
    - Hierarchical → Multi layer hierarchy that has multiple supervisors
    - Custom → Tailored for the given situation

## Memory

Short term → within the context window

Long term → across multiple sessions (memory bank)

## Learning and Adapting

- Link to section

## Model Context Protocol

- Especially relevant when there a lot of third party MCP providers and tools or tools are handled and provided by different teams
- Concepts
    - Tools - Methods that can be used
    - Resources - A shared state across client and server these can be referenced in the prompt
    - Prompt templates
    - Catalog - List of tools and descriptions with meta information about parameters etc.

## A2A - Agent to Agent Protocol

- Core actors
    - User - Initiates request
    - A2A Client
    - A2A Server
- Agent card
    - JSON description of the agent with metadata information like
        - authentication
        - capabilities
        - skills
- Agent discovery
    - Registries with the agents listed
    - Well known endpoints to access the agent card
    - Or direct configuration for closed and private systems
- Communication and Tasks
    - Organized around asynchronous tasks
    - Using JSON-RPC 2.0 and sending artifacts as soon as they become available
- Interaction mechanism
    - Requests Response (Polling)
    - SSEs
- Security
    - TLS Transport Layer Security by design to secure the communication between two agents

## Goal setting and monitoring

- Let the LLM agent review its own code against metrics and goal it gets
- It needs clear and defined objectives SMART goals
    - specific, measurable, achievable, relevant, time bound

## Exception Handling & Recovery

- Detecting errors, handling them gracefully and recover into a uncorrupted state
- Monitoring of errors and logging them and doing retries but also having feedback to recover is important

## Human in the loop

- Either at fixed break points or based on the models call a human is involved for reviewing results or intermediate states or to simply execute some more actions that cannot be done by the LLM it self

## RAG

→ Link

## Skills

Skills are like building functions and meaningful to not clutter the context of the model by let the model decide when to load the full skill and the instructions based on the description and the task at hand.

## Resource Aware Optimization

# Post training

# RAG

Retrieve Augmented Generation is a technique to preselect a knowledge or content from a corpus of content and inject it into the context during inference. This can help to introduce proprietary content and information to the model or to give information more importance and higher the chances that the model prioritizes this content over the content in pre-training to reduce noice, incorporation of unnecessary content or hallucination because it cannot recall the right information from its pre-training.

## Information representation

### Vector Database

### RAG Graph

Instead of saving the data in a flat structure it retains some more relational information how the different information are related and interconnected.

## Retrieval techniques

### Cosine Similarity / Distance

This is basically KNN (K nearest neighbors) and calculates the distance between the different vectors and comes up with the K elements in the database that are closest to the search vector.

### BM25 (Best Match)

TF-IDF is the foundation of the BM25 algorithm. This can also be replaced by a different way to generate keywords for documents.

**F-IDF** is the classic way to rank documents. It combines two simple ideas:

- **TF (Term Frequency):** The more a word appears in a document, the more relevant that document probably is.
- **IDF (Inverse Document Frequency):** Common words (like "the" or "is") are less important than rare words (like "quantum" or "espresso"). Rare words get a higher weight.

BM25 is extending this by taking the document length into account so the frequency of a word is put into relation of the document length.

### Reranking

Additional step to curate the results coming from the database and filter not relevant results before injecting it to the context. 

#### Bi Encoder

Uses two towers (Usually BERT models) to process both query and document independently and compares the similarity based on the output vectors and uses just simple Cosine similarity.

Problem:
- Information loss when the document gets moved into the vector

#### Cross encoder 

Instead of feeding query and document into an encoder separately the Cross Encoder feeds both into a Cross Encoder together. 
- It looks for deep interactions between every word in the query and every word in the document
- Cons: Slow and not feasible to filter 1 mio documents but can be used to rerank the top 50 

Examples: BGE Reranker, BERT based cross encoders

#### Late Interaction (CoIBERT)

Contextualized Late Interaction over BERT which is faster than Cross encoding (processing each document with a lot of effort) and more accurate then Bi Encoders.

Colbert is storing query and document as multi vectors to retain the information of each word and the interaction of the query and document vectors happening in the last second based on MaxSim (max similarity). 

This is looking for the best matching vector in the document for the input query vectors and simply sums them up. 

Index like PLAID is used to narrow down the vectors that are relevant for this comparison. 

#### LLM as a ranker (Brutforce method)

For this the system is using e.g. an agent as a gatekeeper to analysis and reason about the sources that should be included and changes the ranking in terms of relevance or sorts out some all together.

With the speed of modern LLMs this is not a bottle neck anymore. It doesn't need any training or optimization on your own besides optimizing the prompt. 
But expensive at scale and the context window limits the potential candidates that are taken into account.

#### Commercial ReRanking APIs
Jina Reranker, Cohere Rerank, Voyage AI
# Learning of LLMs 

## Pre Training

## Alignment 

### SFT - Supervised Fine Tuning

- Contains of a data set of high quality LLM prompts and outputs to train against a standard language modeling objective
- Decoder only transfomers 
	- Originally encoder processes input and decoder generates outputs 
	- -> Used by nearly any LLM nowadays
- Downstream tasks like fine truning or zero 

### Reinforcement Learning 

Usually this is done based on Human Feedback (RLHF) 
- Model produces some text and gets feedback as a score or reward from a human co-notator

## Post Training 

## Supervised Learning

The data set used is labeled. 
Process: 
- Sampling from the data set, predicting labels, computing loss (prediction vs ground truth), Back propagating the changes through the weights and update the weights accordingly
## Self Supervised Learning 

- The dataset is just text and the model is predicting the next token or missing tokens from the dataset
