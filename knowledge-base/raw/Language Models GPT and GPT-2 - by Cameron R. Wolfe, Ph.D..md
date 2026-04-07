# Prerequisites for GPT

[

![](Language%20Models%20GPT%20and%20GPT-2%20-%20by%20Cameron%20R.%20Wolfe,%20Ph.D./https%253A%252F%252Fbucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com%252Fpublic%252Fimages%252F9fdd1f96-1f6f-4a00-9a80-8fd5ea9487b0_2014x870.png)

](https://substackcdn.com/image/fetch/$s_!bWaL!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fbucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com%2Fpublic%2Fimages%2F9fdd1f96-1f6f-4a00-9a80-8fd5ea9487b0_2014x870.png)

Pre-trained language models can be used to solve a variety of downstream tasks

Language models like GPT-3 \[7\] have revolutionized modern deep learning applications for NLP, leading to widespread publicity and recognition. Interestingly, however, most of the technical novelty of GPT-3 was inherited from its predecessors GPT and GPT-2 \[1, 2\]. As such, a working understanding of GPT and GPT-2 is useful for gaining a better grasp of current approaches for NLP.

The basic methodology explored by the GPT and GPT-2 models is simple. In fact, it can be boiled down to only a few steps:

1.  Pre-train a language model using a lot of raw textual data
    
2.  Adapt this pre-trained model to solve a downstream tasks
    

However, the description is a bit vague. _How does pre-training work for language models? How do we “adapt” the language model to solve different tasks?_

In this overview, we will build a fundamental understanding of language modeling, its use within GPT and GPT-2, and how it can be used to solve problems beyond just generating coherent text. Though GPT and GPT-2 are somewhat outdated due to the recent proposal of larger, more capable models, the fundamental concepts upon which they are built are still highly relevant to modern deep learning applications. Let’s take a closer look.

## Prerequisites for GPT

The basic intuition behind GPT and GPT-2 is to use generic, [pre-trained](https://cameronrwolfe.substack.com/i/73746314/training-pre-training-and-fine-tuning) language models to solve a variety of language modeling tasks with high accuracy. To fully understand this approach, we have to first cover some fundamental concepts about how language models work and how they are leveraged within GPT and GPT-2.

### language modeling

[

![](Language%20Models%20GPT%20and%20GPT-2%20-%20by%20Cameron%20R.%20Wolfe,%20Ph.D./https%253A%252F%252Fbucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com%252Fpublic%252Fimages%252F89687ad1-ab5d-4c72-840c-343d7fa26ab2_1854x1030.png)

](https://substackcdn.com/image/fetch/$s_!aSsR!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fbucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com%2Fpublic%2Fimages%2F89687ad1-ab5d-4c72-840c-343d7fa26ab2_1854x1030.png)

Language model pre-training

GPT models are pre-trained over a corpus/dataset of unlabeled textual data using a language modeling objective. Put simply, this means that we train the model by _(i)_ sampling some text from the dataset and _(ii)_ training the model to predict the next word; see the illustration above. This pre-training procedure is a form of [self-supervised learning](https://cameronrwolfe.substack.com/i/76273144/self-supervised-learning), as the correct “next” word can be determined by simply looking at the next word in the dataset.

**language modeling in math.** To understand language modeling, we only need to grasp the basic idea outlined above. To make this a bit more rigorous, however, we can notice that our corpus is just a set of tokens. We can think of tokens as individual words within the dataset, but this is not quite correct. In reality, tokens may be sub-words or even characters; see below for more details. 

[Learn about Tokenization](https://towardsdatascience.com/how-to-build-a-wordpiece-tokenizer-for-bert-f505d97dddbb)

Let us denote this set of tokens (of size `N`) that comprise our pre-training dataset as follows.

[

![](Language%20Models%20GPT%20and%20GPT-2%20-%20by%20Cameron%20R.%20Wolfe,%20Ph.D./https%253A%252F%252Fbucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com%252Fpublic%252Fimages%252F45501723-a132-40e7-8cb8-5050b2b265fb_1328x378.png)

](https://substackcdn.com/image/fetch/$s_!sZJS!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fbucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com%2Fpublic%2Fimages%2F45501723-a132-40e7-8cb8-5050b2b265fb_1328x378.png)

Our unlabeled text corpus is just an ordered set of tokens!

Given a deep learning model with parameters `θ`, a language modeling objective tries to maximize the likelihood shown below.

[

![](Language%20Models%20GPT%20and%20GPT-2%20-%20by%20Cameron%20R.%20Wolfe,%20Ph.D./https%253A%252F%252Fbucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com%252Fpublic%252Fimages%252F3430b67c-2d19-4840-9207-09e68a25d03a_1318x444.png)

](https://substackcdn.com/image/fetch/$s_!3eqH!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fbucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com%2Fpublic%2Fimages%2F3430b67c-2d19-4840-9207-09e68a25d03a_1318x444.png)

Language modeling loss over a text corpus

Put simply, this expression characterizes the model’s probability of predicting the correct next token given `k` preceding tokens as context. For anyone who might be struggling to understand this formulation, feel free to check out the helper links below.

-   Why do we use log probabilities? \[[blog](https://chrispiech.github.io/probabilityForComputerScientists/en/part1/log_probabilities/)\]
    
-   Understanding conditional probabilities \[[blog](https://www.hackerearth.com/practice/machine-learning/prerequisites-of-machine-learning/bayes-rules-conditional-probability-chain-rule/tutorial/)\]
    

Using the language modeling loss (which just characterizes our model’s ability to accurately predict the next token in a sequence!), we can follow the procedure below to pre-train our model’s parameters `θ` such that the loss is minimized:

1.  Sample text from the pre-training corpus
    
2.  Predict the next token with our model
    
3.  Use stochastic gradient descent (SGD), or any [other optimizer](https://ruder.io/optimizing-gradient-descent/), to increase the probability of the correct next token
    

By repeating this (self-supervised) training procedure many times, our model will eventually become really good at language modeling (i.e., predicting the next token in a sequence).

**what is a language model?** Models pre-trained using such a self-supervised language modeling objective are commonly referred to as language models (LMs). LMs become more effective as they are scaled up (i.e., more layers, parameters, etc.). Thus, we will often see larger versions of these models (e.g., GPT-3 \[7\]), which are referred to as large language models (LLMs). 

**why are LMs useful?** LMs can generate coherent text by iteratively predicting the most likely next token, which enables a range of applications from text auto-completion to chatbots. Beyond their generative capabilities, however, prior work in NLP has shown that LM pre-training is incredibly beneficial for a variety tasks; e.g., pre-trained word embeddings are useful in downstream tasks \[3, 4\] and LM pre-training improves the performance of [LSTMs](https://colah.github.io/posts/2015-08-Understanding-LSTMs/) \[5\].

Moving beyond such approaches, GPT models explore language model pre-training with transformers \[6\]. Compared to sequential models (e.g., LSTM), transformers are _(i)_ incredibly expressive (i.e., high representational capacity, many parameters, etc.) and _(ii)_ better suited to the ability of modern GPUs to parallelize computation, allowing LM pre-training to be performed with larger models and more data. Such scalability enables the exploration of LLMs, which have revolutionized NLP applications.

### decoder-only transformers

Both GPT and GPT-2 use a decoder-only transformer architecture. I have [previously summarized](https://cameronrwolfe.substack.com/p/understanding-the-open-pre-trained-transformers-opt-library-193a29c14a15#%C2%A7understanding-opt) this architecture, but I will provide a quick overview here for completeness. To learn more about the transformer architecture, I would recommend briefly reading the explanation linked below.

[Learn about Transformers](https://cameronrwolfe.substack.com/i/74325854/background)

The transformer architecture has two major components: the encoder and the decoder.

[

![](Language%20Models%20GPT%20and%20GPT-2%20-%20by%20Cameron%20R.%20Wolfe,%20Ph.D./https%253A%252F%252Fbucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com%252Fpublic%252Fimages%252F0235fd2f-26f4-47ff-b95e-eddf6a4593b0_782x1152.png)

](https://substackcdn.com/image/fetch/$s_!zs8j!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fbucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com%2Fpublic%2Fimages%2F0235fd2f-26f4-47ff-b95e-eddf6a4593b0_782x1152.png)

(from \[6\])

A decoder-only architecture removes the following components from the transformer:

-   The entire encoder module
    
-   All encoder-decoder self-attention modules in the decoder
    

After these components have been removed, each layer of the decoder simply consists of a masked self-attention layer followed by a feed forward neural network. Stacking several of such layers on top of each other forms a deep, decoder-only transformer architecture, such as those used for GPT or GPT-2; see below.

[

![](Language%20Models%20GPT%20and%20GPT-2%20-%20by%20Cameron%20R.%20Wolfe,%20Ph.D./https%253A%252F%252Fbucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com%252Fpublic%252Fimages%252F91a045da-57be-437d-962c-529ee5bc93fb_1234x828.png)

](https://substackcdn.com/image/fetch/$s_!yHjt!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fbucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com%2Fpublic%2Fimages%2F91a045da-57be-437d-962c-529ee5bc93fb_1234x828.png)

Decoder-only transformer architecture

**why the decoder?** The choice of using the decoder architecture (as opposed to the encoder) for LMs is not arbitrary. The masked self-attention layers within the decoder ensure that the model cannot look forward in a sequence when crafting a token’s representation. In contrast, bidirectional self-attention (as used in the encoder) allows each token’s representation to be adapted based on all other tokens within a sequence.

[Learn about Self-Attention](https://cameronrwolfe.substack.com/i/76273144/self-attention)

Masked self-attention is required for language modeling because we should not be able to look forward in the sentence while predicting the next token. Using masked self-attention yields an autoregressive architecture (i.e., meaning that the model’s output at time `t` is used as input at time `t+1`) that can continually predict the next token in a sequence; see below.

[

![](Language%20Models%20GPT%20and%20GPT-2%20-%20by%20Cameron%20R.%20Wolfe,%20Ph.D./https%253A%252F%252Fbucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com%252Fpublic%252Fimages%252F83ac8a81-a3b8-42e8-bc53-6ab3a505effc_1880x1010.png)

](https://substackcdn.com/image/fetch/$s_!-IMK!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fbucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com%2Fpublic%2Fimages%2F83ac8a81-a3b8-42e8-bc53-6ab3a505effc_1880x1010.png)

Autoregressive output from a decoder-only transformer architecture

For tasks that do not require masked self-attention (e.g., sentence classification, tagging, etc.), however, we should remember that using bidirectional self-attention is really beneficial; see the link below for more details.

[Learn about BERT](https://cameronrwolfe.substack.com/p/language-understanding-with-bert)

### creating foundation models

Now that we have a basic understanding of language modeling and relevant architectures, we can understand the inspiration behind the GPT LMs, which begins with the following observations: 

-   Unlabeled text corpora are largely abundant
    
-   Labeled data is scarce 
    

For most deep learning systems, a lot of labeled data is needed to perform discriminative language understanding tasks. _Current deep learning systems are narrow experts_. The model is simply trained over a large, supervised dataset such that it learns to accurately perform a specific task; see below.

Though commonly used, this approach suffers a few major limitations:

1.  Some domains do not have much labeled data
    
2.  We have to train a new model for every task that we want to solve (and training deep learning models is expensive!)
    

**foundation models.** GPT and GPT-2 move away from the paradigm of narrow experts within deep learning. Rather than train a new model for every application, we can pre-train a single LM, then somehow adapt this model to solve numerous tasks. Generic models that are used to solve many tasks are referred to as foundation models.

[More on Foundation Models](https://crfm.stanford.edu/)

This approach mitigates problems with data scarcity by pre-training over a large, diverse dataset. Additionally, these models can be reused or adapted to solve other tasks, allowing us to avoid constantly training new models. One approach for adapting a foundation model to a downstream task is to perform fine-tuning (i.e., more training) over a supervised dataset. More recently, however, the go-to approach is via zero or few-shot inference.

**zero/few-shot inference via prompting.** The GPT models receive text as input and produce text as output. We can exploit this generic input-output structure by providing inputs like the following:

-   “Translate this sentence to English: `<sentence> =>`”
    
-   “Summarize the following document: `<document> =>`”.
    

These task-solving “prompts” enable zero-shot (i.e., without seeing examples of correct output) inference with LMs, as the most appropriate output from the LM is to solve the specified task (e.g., translating to English or summarizing a document)! To perform few-shot inference, we can construct a similar prompt with examples of correct output provided at the start; see below.

[

![](Language%20Models%20GPT%20and%20GPT-2%20-%20by%20Cameron%20R.%20Wolfe,%20Ph.D./https%253A%252F%252Fbucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com%252Fpublic%252Fimages%252F20c74320-2996-47ed-9507-08e1967a36d9_736x1262.png)

](https://substackcdn.com/image/fetch/$s_!yjl0!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fbucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com%2Fpublic%2Fimages%2F20c74320-2996-47ed-9507-08e1967a36d9_736x1262.png)

Zero, one, and few-shot inference with LMs (from \[7\])me

## Publications

We will now overview the details of GPT and GPT-2. Published by researchers at [OpenAI](https://openai.com/), these models pioneered the use of generic LMs for solving downstream tasks. They laid the foundation for breakthrough advancements like GPT-3. The main differentiator between these models is simply the size of the underlying LM.

### **[Improving Language Understanding by Generative Pre-Training](https://www.cs.ubc.ca/~amuham01/LING530/papers/radford2018improving.pdf) (GPT) \[1\]**

GPT is a general purpose language understanding model that is trained in two phases: pre-training and fine-tuning.

[

![](Language%20Models%20GPT%20and%20GPT-2%20-%20by%20Cameron%20R.%20Wolfe,%20Ph.D./https%253A%252F%252Fbucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com%252Fpublic%252Fimages%252F47d302b2-a7e6-4ee9-bf10-7c161a9e4057_342x648.png)

](https://substackcdn.com/image/fetch/$s_!ZhhZ!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fbucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com%2Fpublic%2Fimages%2F47d302b2-a7e6-4ee9-bf10-7c161a9e4057_342x648.png)

GPT architecture (from \[1\])

GPT uses a 12-layer, decoder-only transformer architecture that matches the original transformer decoder \[6\] (aside from using learnable positional embeddings); see the figure above. GPT first performs language model pre-training over the [BooksCorpus](https://yknzhu.wixsite.com/mbweb) dataset, then is separately fine-tuned (in a supervised manner) on a variety of discriminative language understanding tasks.

[

![](Language%20Models%20GPT%20and%20GPT-2%20-%20by%20Cameron%20R.%20Wolfe,%20Ph.D./https%253A%252F%252Fbucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com%252Fpublic%252Fimages%252F60d46502-4340-48d7-8db6-057993f82060_1622x816.png)

](https://substackcdn.com/image/fetch/$s_!cTz2!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fbucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com%2Fpublic%2Fimages%2F60d46502-4340-48d7-8db6-057993f82060_1622x816.png)

(from \[1\])

Instead of modifying GPT’s architecture to solve different tasks, we provide input to GPT in a task-specific structure, then pass the output of GPT to a separate classification layer. For example, on entailments tasks, we concatenate the input sentences, separate them with a special delimiter, provide this input to GPT, then pass GPT’s output to a separate classification layer. Fine-tuning GPT with different supervised tasks is explained further in Section 3.3 of \[1\] and illustrated above. 

[

![](Language%20Models%20GPT%20and%20GPT-2%20-%20by%20Cameron%20R.%20Wolfe,%20Ph.D./https%253A%252F%252Fbucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com%252Fpublic%252Fimages%252F636f5316-9d99-4b79-8c91-e4b3c76da2ef_1600x332.png)

](https://substackcdn.com/image/fetch/$s_!KSiE!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fbucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com%2Fpublic%2Fimages%2F636f5316-9d99-4b79-8c91-e4b3c76da2ef_1600x332.png)

(from \[1\])

GPT is evaluated on a wide variety of tasks from question answering to classification; see above. The authors find that pre-training GPT on a corpus with long spans of contiguous text (as opposed to individual, shuffled sentences) is essential; this was also verified by later work \[9\]. Across experimental settings, we see that GPT sets a new state-of-the-art on 9 of 12 tasks and even consistently outperforms model ensembles; see below.

[

![](Language%20Models%20GPT%20and%20GPT-2%20-%20by%20Cameron%20R.%20Wolfe,%20Ph.D./https%253A%252F%252Fbucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com%252Fpublic%252Fimages%252Fb925c519-b72b-40a7-8d32-2f5c8b3804dc_1968x1078.png)

](https://substackcdn.com/image/fetch/$s_!nONN!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fbucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com%2Fpublic%2Fimages%2Fb925c519-b72b-40a7-8d32-2f5c8b3804dc_1968x1078.png)

(from \[1\])

From these experiments, we learn that GPT can accurately learn difficult patterns such as long-term dependencies and linguistic ambiguity. Put simply, GPT demonstrates that general purpose models for textual understanding are incredibly effective. Without using any task-specific architectures or modifications, we can outperform numerous baselines by a large margin, even including those that are specialized for solving individual tasks.

### **[Language Models are Unsupervised Multitask Learners](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf) (GPT-2) \[2\]**

The proposal of GPT-2 \[2\] follows a similar pattern as its predecessor. The model is pre-trained using a language modeling objective, but it performs no fine-tuning, choosing to solve downstream tasks in a zero-shot manner instead. Put simply, GPT-2 performs multi-task learning by:

1.  Pre-training a generic LM over raw textual data
    
2.  Using textual “prompts” to perform zero-shot inference on a variety of tasks
    

Pre-training is performed over a custom WebText dataset that is constructed by scraping popular links from Reddit, and four different sizes of LMs are tested. The smallest model matches the size of GPT \[1\] and the largest model is GPT-2; see below.

[

![](Language%20Models%20GPT%20and%20GPT-2%20-%20by%20Cameron%20R.%20Wolfe,%20Ph.D./https%253A%252F%252Fbucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com%252Fpublic%252Fimages%252F80a786e0-35eb-4216-be14-7e32b88f5ff8_1186x460.png)

](https://substackcdn.com/image/fetch/$s_!QilT!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fbucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com%2Fpublic%2Fimages%2F80a786e0-35eb-4216-be14-7e32b88f5ff8_1186x460.png)

(from \[2\])

The model architecture is identical to GPT, barring a few minor differences (e.g., different weight initialization, larger vocabulary, longer input sequence, etc.). Despite the size of these LMs, they are found to underfit the WebText dataset during pre-training, indicating that larger LMs would perform even better.

GPT-2 is evaluated on several tasks (i.e., language modeling, question answering, translation, etc.), where it achieves promising (but not always state-of-the-art) results. For example, we see that GPT-2 reaches near state-of-the-art performance on language modeling and reading comprehension tasks, but it falls far short of baseline performance for summarization and question answering; see below.

[

![](Language%20Models%20GPT%20and%20GPT-2%20-%20by%20Cameron%20R.%20Wolfe,%20Ph.D./https%253A%252F%252Fbucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com%252Fpublic%252Fimages%252F206e161b-36a7-40a1-8dd7-06d73725deb9_1982x586.png)

](https://substackcdn.com/image/fetch/$s_!7wr7!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fbucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com%2Fpublic%2Fimages%2F206e161b-36a7-40a1-8dd7-06d73725deb9_1982x586.png)

(from \[2\])

But, we need to remember that _GPT-2 performs no fine-tuning to solve any of these tasks_. All of these results are achieved via zero-shot inference, which makes GPT’s competitive performance on certain tasks pretty impressive.

Interestingly, zero-shot performance consistently improves with the size of the underlying LM, indicating that increasing an LM’s size/capacity improves its ability to learn relevant features during pre-training; see below.

[

![](Language%20Models%20GPT%20and%20GPT-2%20-%20by%20Cameron%20R.%20Wolfe,%20Ph.D./https%253A%252F%252Fbucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com%252Fpublic%252Fimages%252F2a242e94-54ba-44e1-9f99-663a8330a67d_1966x800.png)

](https://substackcdn.com/image/fetch/$s_!Qu_u!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fbucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com%2Fpublic%2Fimages%2F2a242e94-54ba-44e1-9f99-663a8330a67d_1966x800.png)

(from \[2\])

Although pre-training and fine-tuning is an effective transfer learning paradigm, GPT-2 shows us that easier, more general methods of transfer are achievable. Given that they are pre-trained over a sufficiently-large corpus, LMs can solve downstream tasks without any architectural or parameter modifications.

As we saw, however, the performance of GPT-2 lags behind baselines on several tasks, indicating that foundation models like GPT-2 are not a drop-in replacement for the narrow expert models that were currently in use. The authors of \[2\] indicate that larger LMs are needed to eliminate this gap in performance.

> “… a language model with sufficient capacity will begin to learn to infer and perform the tasks demonstrated in natural language sequences in order to better predict them, regardless of their method of procurement.” -from \[2\]

## Takeaways

GPT and GPT-2 taught us a lot about deep learning. Though their effectiveness on downstream tasks was not incredibly impressive from an accuracy perspective, they provided a glimpse into the incredible potential of LMs as foundation models and laid the methodological foundation for the emergence of LLMs like GPT-3. The impact of these models is far-reaching, but I’ve tried to summarize some of the most useful takeaways and ideas from research on GPT and GPT-2 below.

**language model pre-training is awesome.** Transformers, due to their efficient utilization of compute, enable language model pre-training to be performed at a massive scale. The representations learned during this pre-training process allow pre-trained LMs to generalize well to solving other tasks. Put simply, _LMs aren’t just good at language modeling_ – they can solve other tasks too!

**size matters.** As we see in the transition from GPT to GPT-2, increasing the size of the pre-trained LM increases the quality of the learned representations; e.g., GPT-2 far outperforms GPT in terms of zero/few-shot inference. This trend became more pronounced after the release of the (larger) GPT-3 model \[7\].

**we should leverage foundation models.** Most deep learning models are trained to accomplish a single, narrow task. In many cases, however, we can benefit from _(i)_ pre-training a larger model via self-supervised learning on unlabeled data and _(ii)_ adapting this model to solve many tasks. Such repurposing of large, foundation models is computationally efficient (i.e., computation is shared across many tasks) and not specific to LMs. We can train foundation models for domains like computer vision too \[8\]!

### code and resources

For those interested in trying out applications with GPT-2, the code is [publicly available](https://github.com/openai/gpt-2)! However, pre-training such a model is quite computationally expensive. A better approach would be to [download a pre-trained language model](https://huggingface.co/models?sort=downloads) and either [fine-tune](https://huggingface.co/docs/transformers/v4.14.1/en/training) it or perform zero/few-shot inference (e.g., by using the demo below).

[GPT-2 LM Demo](https://transformer.huggingface.co/doc/gpt2-large)

## New to the newsletter?

Hello! I am [Cameron R. Wolfe](https://cameronrwolfe.me/), a research scientist at [Alegion](https://www.alegion.com/) and PhD student at Rice University. I study the empirical and theoretical foundations of deep learning. This is the Deep (Learning) Focus newsletter, where I pick a single, bi-weekly topic in deep learning research, provide an understanding of relevant background information, then overview a handful of popular papers on the topic. If you like this newsletter, please subscribe, share it with your friends, or follow me on [twitter](https://twitter.com/cwolferesearch)!

### Bibliography

\[1\] Radford, Alec, et al. "Improving language understanding by generative pre-training." (2018). 

\[2\] Radford, Alec, et al. "Language Models are Unsupervised Multitask Learners."

\[3\] Pennington, Jeffrey, Richard Socher, and Christopher D. Manning. "Glove: Global vectors for word representation." Proceedings of the 2014 conference on empirical methods in natural language processing (EMNLP). 2014.

\[4\] Conneau, Alexis, et al. "Supervised learning of universal sentence representations from natural language inference data." arXiv preprint arXiv:1705.02364 (2017).

\[5\] Howard, Jeremy, and Sebastian Ruder. "Universal language model fine-tuning for text classification." arXiv preprint arXiv:1801.06146 (2018).

\[6\] Vaswani, Ashish, et al. "Attention is all you need." Advances in neural information processing systems 30 (2017).

\[7\] Brown, Tom, et al. "Language models are few-shot learners." Advances in neural information processing systems 33 (2020): 1877-1901.

\[8\] Yuan, Lu, et al. "Florence: A new foundation model for computer vision." arXiv preprint arXiv:2111.11432 (2021).

\[9\] Krishna, Kundan, et al. "Downstream Datasets Make Surprisingly Good Pretraining Corpora." _arXiv preprint arXiv:2209.14389_ (2022).