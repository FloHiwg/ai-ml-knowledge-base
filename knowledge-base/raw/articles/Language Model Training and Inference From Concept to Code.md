## Relevant Background Concepts

[

![](Language%20Model%20Training%20and%20Inference%20From%20Concept%20to%20Code/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252F85dbb7d4-7acd-459f-8d02-8ffdd042ecbf_1938x1092.jpeg)

](https://substackcdn.com/image/fetch/$s_!5gOZ!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F85dbb7d4-7acd-459f-8d02-8ffdd042ecbf_1938x1092.png)

Despite all that has been accomplished with large language models (LLMs), the underlying concept that powers all of these models is simple—_we just need to accurately predict the next token_! Though some may (reasonably) argue that recent research on LLMs goes beyond this basic idea, next token prediction still underlies the pre-training, fine-tuning (depending on the variant), and inference process of all causal language models, making it a fundamental and important concept for any LLM practitioner to understand.

> _“It is perhaps surprising that underlying all this progress is still the original autoregressive mechanism for generating text, which makes token-level decisions one by one and in a left-to-right fashion.”_ - from \[10\]

Within this overview, we will take a deep and practical dive into the concept of next token prediction to understand how it is used by language models both during training and inference. First, we will learn these ideas at a conceptual level. Then, we will walk through an actual implementation (in PyTorch) of the language model pretraining and inference processes to make the idea of next token prediction more concrete.

## Relevant Background Concepts

Prior to diving into the topic of this overview, there are a few fundamental ideas that we need to understand. Within this section, we will quickly overview these important concepts and provide links to further reading for each.

**The transformer architecture.** First, we need to have a working understanding of the transformer architecture \[5\], especially the [decoder-only variant](https://twitter.com/cwolferesearch/status/1640446111348555776?s=20). Luckily, we have covered these ideas extensively in the past:

-   The Transformer Architecture \[[link](https://cameronrwolfe.substack.com/i/136366740/the-transformer-from-top-to-bottom)\]
    
-   Decoder-Only Transformers \[[link](https://cameronrwolfe.substack.com/i/85568430/decoder-only-transformers)\]
    

More fundamentally, we also need to understand the idea of [self-attention](https://twitter.com/cwolferesearch/status/1641932082283700226?s=20) and the role that it plays in the transformer architecture. More specifically, large causal language models—_the kind that we will study in this overview_—use a particular variant of self-attention called [multi-headed causal self-attention](https://twitter.com/cwolferesearch/status/1644773244786941952?s=20).

**Training neural nets with PyTorch.** The code we will look at in this overview is written in [PyTorch](https://pytorch.org/) and heavily relies upon distributed training techniques, such as distributed data parallel (DDP) training. To understand the basics of PyTorch and distributed training, check out the following articles:

-   Neural Nets in PyTorch \[[link](https://pytorch.org/tutorials/beginner/blitz/neural_networks_tutorial.html)\]
    
-   PyTorch Distributed Overview \[[link](https://pytorch.org/tutorials/beginner/dist_overview.html)\]
    
-   Distributed Data Parallel in PyTorch \[[link](https://pytorch.org/tutorials/intermediate/ddp_tutorial.html)\]
    

Beyond basic (and distributed) neural network training in PyTorch, we will also see [automatic mixed precision (AMP)](https://developer.nvidia.com/automatic-mixed-precision) training being used, which selectively adjusts the precision—between full precision (`float32`) and half precision (`float16` or [bfloat16](https://cloud.google.com/tpu/docs/bfloat16))—within the neural net during training to improve efficiency. Put simply, we perform a lot of matrix multiplications within the neural net, and _training is a lot faster if we can run some of these multiplications in lower precision_. See [here](https://pytorch.org/tutorials/recipes/recipes/amp_recipe.html) for a more extensive (and practical) overview of AMP.

**Deep learning basics.** This overview also requires a baseline understanding of neural networks, including how they are trained and used. To gain this knowledge, I highly recommend the _[Practical Deep Learning for Coders](https://course.fast.ai/)_ course from [fast.ai](https://www.fast.ai/), which is updated frequently and remains (in my opinion) the best practical introduction to deep learning that anyone can get[1](https://cameronrwolfe.substack.com/p/language-model-training-and-inference?open=false#footnote-1-136638774).

## Understanding Next Token Prediction

We will now learn about next token prediction (also known as the standard language modeling objective)—_the workhorse behind all causal language models_. Within this section, we will first cover a few fundamental concepts related to tokenization, then we will overview the pretraining and inference processes for language models, as well as their relation to the concept of next token prediction.

#### Tokens and Vocabularies

In trying to understand next token prediction, the first question we might have is: _What is a token?_ Put simply, a token is just a word or sub-word within a sequence of text. Given a sequence of raw text as input, the first step we take in using a language model is to tokenize this raw text, or break it into a sequence of discrete tokens; see below for an example.

[

![](Language%20Model%20Training%20and%20Inference%20From%20Concept%20to%20Code/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252F56dd3364-44d1-4587-a0b8-3909f1f02f31_1132x282.png)

](https://substackcdn.com/image/fetch/$s_!m6ce!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F56dd3364-44d1-4587-a0b8-3909f1f02f31_1132x282.png)

Tokenizing a sequence of raw text

To perform this tokenization, we rely upon a [tokenizer](https://huggingface.co/docs/transformers/main_classes/tokenizer). The tokenizer is trained over an unlabeled textual corpus to learn a fixed-size, unique set of tokens that exist. This fixed-size set of tokens is referred to as our vocabulary, and the vocabulary contains all tokens that are known by the language model. Usually, we should try to make sure that the data used to train the tokenizer accurately reflects the kind of data our model will see during training and inference. Given that the vocabulary has a fixed size, this ensures that the tokens we see in the wild are present within the language model’s vocabulary more often than not.

**Tokenization techniques.** Numerous different tokenization techniques exist; see [here](https://huggingface.co/docs/transformers/tokenizer_summary) for an overview. For details on training and using popular tokenizers for LLMs, see [this article](https://huggingface.co/learn/nlp-course/chapter6/5?fw=pt) that details the byte pair encoding (BPE) tokenizer—_the most commonly-used tokenizer for LLMs_. Another tokenization technique that has become recently popular is [byte-level BPE (BBPE)](https://medium.com/@pierre_guillou/byte-level-bpe-an-universal-tokenizer-but-aff932332ffe), which relies upon bytes (instead of textual characters) as the basic unit of tokenization.

**Token embeddings.** Once we have tokenized our text, we look up the embedding for each token within an embedding layer that is stored as part of the language model’s parameters[2](https://cameronrwolfe.substack.com/p/language-model-training-and-inference?open=false#footnote-2-136638774). After this, the sequence of textual tokens constructed from our input becomes a sequence of token embedding vectors; see below.

[

![](Language%20Model%20Training%20and%20Inference%20From%20Concept%20to%20Code/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252F1fd4ac84-3925-428c-8f6a-64dfed5268ad_1714x848.jpeg)

](https://substackcdn.com/image/fetch/$s_!Ugld!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F1fd4ac84-3925-428c-8f6a-64dfed5268ad_1714x848.png)

Generating token embeddings from raw text

There is one final step required to construct the input that is actually passed to our decoder-only transformer architecture—_we need to add positional embeddings_. Positional embeddings are the same size as token embeddings and treated similarly (i.e., they are stored as part of the language model and trained along with other model parameters). Instead of associating an embedding with each unique token, however, we associate an embedding with each unique position that can exist within a tokenized input; see below for a depiction.

[

![](Language%20Model%20Training%20and%20Inference%20From%20Concept%20to%20Code/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252F3510038d-21bf-4a65-b4a2-20c5676b0fb1_1468x1392.jpeg)

](https://substackcdn.com/image/fetch/$s_!_g8L!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F3510038d-21bf-4a65-b4a2-20c5676b0fb1_1468x1392.png)

Positional embeddings within a language model

We add these embeddings to the token embeddings at the corresponding position. Such additive positional embeddings are necessary because the self-attention operation does not have any way of representing the position of each token. By adding positional embeddings, we allow the self-attention layers within the transformer to use the position of each token as a relevant feature during the learning process. Recent research has explored novel techniques for injecting positional information into self-attention, resulting in techniques like [RoPE](https://blog.eleuther.ai/rotary-embeddings/) \[6\].

[

![](Language%20Model%20Training%20and%20Inference%20From%20Concept%20to%20Code/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252F6e3f8a12-a893-4508-95d7-312d37a77ea2_1792x1112.jpeg)

](https://substackcdn.com/image/fetch/$s_!ROno!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F6e3f8a12-a893-4508-95d7-312d37a77ea2_1792x1112.png)

Context window for language models

**Context window.** Language models are pretrained with token sequences of a particular size, which is referred to as the size of the context window or the context length. This size—_typically somewhere in the range of 1K to 8K tokens_ (though [some models](https://www.anthropic.com/index/100k-context-windows) are much larger!)—is (usually) selected based hardware and memory constraints[3](https://cameronrwolfe.substack.com/p/language-model-training-and-inference?open=false#footnote-3-136638774). Given that we only learn positional embeddings for input of this length, the context window limits the amount of input data that an LLM can process. However, recent techniques like [ALiBi](https://paperswithcode.com/method/alibi) \[7\] have been developed to enable extrapolation to inputs longer than those seen during training.

#### Language Model Pretraining

[

![](Language%20Model%20Training%20and%20Inference%20From%20Concept%20to%20Code/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252Fa6ac34b2-b4c4-4ae8-87eb-dd46417adba4_1932x374.jpeg)

](https://substackcdn.com/image/fetch/$s_!Mawr!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fa6ac34b2-b4c4-4ae8-87eb-dd46417adba4_1932x374.png)

(from \[8, 9\])

Language models are trained in several steps, as shown above. The first (and most computationally expensive) step is pretraining, which we will focus on within this overview. During pretraining, we get a large corpus of unlabeled text and train the model by _i)_ sampling some text from the dataset and _ii)_ training the model to predict the next word. This is a [self-supervised](https://cameronrwolfe.substack.com/p/language-understanding-with-bert#%C2%A7self-supervised-learning) objective due to the fact that no labels are required. Rather, the ground truth next token is already present within the corpus itself—_the source of supervision is implici_t. Such a training objective is referred to as next token prediction, or the standard language modeling objective.

**Predicting the next token.** After we have our token embeddings (with position embeddings), we pass these vectors into a decoder-only transformer, which produces a corresponding output vector for each token embedding; see below.

[

![](Language%20Model%20Training%20and%20Inference%20From%20Concept%20to%20Code/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252F7721d1fa-c9ef-47e0-96cf-483bbde4967f_1008x792.png)

](https://substackcdn.com/image/fetch/$s_!l5Db!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F7721d1fa-c9ef-47e0-96cf-483bbde4967f_1008x792.png)

Input and output of a decoder-only transformer

Given an output vector for each token, we can perform next token prediction by _i)_ taking the output vector for a token and _ii)_ using this to predict the token that comes next in the sequence. See below for an illustration.

[

![](Language%20Model%20Training%20and%20Inference%20From%20Concept%20to%20Code/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252Fd162da5e-a14f-42ba-bf51-9425b199fd35_1242x1188.png)

](https://substackcdn.com/image/fetch/$s_!bwZh!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fd162da5e-a14f-42ba-bf51-9425b199fd35_1242x1188.png)

Visualizing next token prediction on a single token

As we can see above, the next token is predicted by passing a token’s output vector as input to a linear layer, which outputs a vector with the same size as our vocabulary. After a softmax transformation is applied, a probability distribution over the token vocabulary is formed, and we can either _i)_ sample the next token from this distribution during inference or _ii)_ train the model to maximize the probability of the correct next token during pretraining.

**Predicting tokens across a sequence.** During pretraining, we don’t predict only a single next token. Rather, we perform next token prediction for every token in a sequence and aggregate the loss over them all. Due to the use of causal self-attention, each output token vector only considers the current token and those that come before it in the sequence. As such, next token prediction can be performed across an entire sequence using a single forward pass of the decoder-only transformer, as each token has no knowledge of tokens that come after it.

#### Autoregressive Inference Process

[

![](Language%20Model%20Training%20and%20Inference%20From%20Concept%20to%20Code/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252F08729f45-ace9-419d-80dd-4520c878cfac_2300x1164.jpeg)

](https://substackcdn.com/image/fetch/$s_!vR2B!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F08729f45-ace9-419d-80dd-4520c878cfac_2300x1164.png)

Generating text with a language model

Now, we understand how to pretrain a language model, but next token prediction is also used when we are performing inference! _Next token prediction underlies all aspects of training and using LLMs._ Starting with an initial (possibly empty) input sequence or prefix, language models generate text by following an autoregressive next token prediction process (see above) with the following steps:

1.  Predict the next token
    
2.  Add the predicted token to the current input sequence
    
3.  Repeat
    

**Choosing next token.** In the prior section, we’ve seen how a probability distribution over tokens is created. But, _how do we actually choose the next token from this distribution?_ Typically, we just sample the next token from this distribution. However, numerous sampling strategies exist that add slight variations to this approach by modifying the probability distribution over tokens. The exact decoding approach varies depending upon the application, but the main concepts and strategies that we need to be familiar with are outlined below:

-   Temperature \[[link](https://twitter.com/cwolferesearch/status/1671628210180698112?s=20)\]
    
-   Greedy Decoding \[[link](https://twitter.com/cwolferesearch/status/1659608476455256078?s=20)\]
    
-   Nucleus Sampling \[[link](https://twitter.com/cwolferesearch/status/1692617211205022064?s=20)\]
    
-   Top-K Sampling \[[link](https://docs.cohere.com/docs/controlling-generation-with-top-k-top-p)\]
    

## Creating a Minimal Implementation

Now that we understand the concept of next token prediction, we need to take the ideas we have learned and make them a bit more concrete. Within this section, we will examine an implementation—written in PyTorch—of pretraining and inference (using next token prediction) with an LLM. This implementation is derived from [NanoGPT](https://github.com/karpathy/nanoGPT) by [Andrej Karpathy](https://twitter.com/karpathy), which matches the specs of [GPT-2](https://cameronrwolfe.substack.com/i/85568430/language-models-are-unsupervised-multitask-learners-gpt) \[1\]. In addition to the implementation of NanoGPT provided on GitHub (linked above), there’s an awesome tutorial video to go with it; see below.

[NanoGPT Tutorial](https://www.youtube.com/watch?v=kCc8FmEb1nY&list=PLAqhIrjkxbuWI23v9cThsA9GvCAUhRvKZ&index=7)

Although this model is small compared to most modern LLMs[4](https://cameronrwolfe.substack.com/p/language-model-training-and-inference?open=false#footnote-4-136638774), it serves as a great example of what language models look like in code. Here, we will study the implementation of NanoGPT and connect it to our discussion of next token prediction from previous sections.

#### The Decoder-Only Transformer

First, we will detail the implementation of our language model architecture, which is based upon a decoder-only transformer. First, we will overview the components of this architecture, moving from a single block of the model to the full, multi-layer architecture. Then, we will study how this model architecture can be used during pretraining and inference with next token prediction.

[

![](Language%20Model%20Training%20and%20Inference%20From%20Concept%20to%20Code/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252Fe9b00af0-840d-4079-93e6-4a976c648b68_1666x708.png)

](https://substackcdn.com/image/fetch/$s_!O55q!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fe9b00af0-840d-4079-93e6-4a976c648b68_1666x708.png)

**Model configuration.** The first thing we need to look at is the configuration of our model architecture; see above. As we can see, the configuration is just a [data class](https://www.dataquest.io/blog/how-to-use-python-data-classes/) in Python that specifies the various hyperparameters of our architecture. The settings shown above correspond to those of the smallest model architecture explored within the GPT-2 paper \[1\], as shown in the table below.

[

![](Language%20Model%20Training%20and%20Inference%20From%20Concept%20to%20Code/https%253A%252F%252Fbucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com%252Fpublic%252Fimages%252F80a786e0-35eb-4216-be14-7e32b88f5ff8_1186x460.png)

](https://substackcdn.com/image/fetch/$s_!QilT!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fbucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com%2Fpublic%2Fimages%2F80a786e0-35eb-4216-be14-7e32b88f5ff8_1186x460.png)

(from \[1\])

This model contains only 117M parameters and is actually identical to the base transformer architecture used within the original [GPT publication](https://cameronrwolfe.substack.com/i/85568430/improving-language-understanding-by-generative-pre-training-gpt) \[2\].

[

![](Language%20Model%20Training%20and%20Inference%20From%20Concept%20to%20Code/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252F4e74de2d-90f4-4749-ba1b-7c2426a89ea9_1402x1080.png)

](https://substackcdn.com/image/fetch/$s_!Q-iC!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F4e74de2d-90f4-4749-ba1b-7c2426a89ea9_1402x1080.png)

**A single block.** Next, we can look at the implementation of a single block within the decoder-only transformer architecture; see above. Here, we see that a decoder-only transformer block has two components:

1.  Multi-headed Causal Self-Attention \[[link](https://twitter.com/cwolferesearch/status/1644773244786941952?s=20)\]
    
2.  Feed-forward Neural Network \[[link](https://cameronrwolfe.substack.com/i/94634004/feed-forward-neural-networks)\]
    

For most language models (including NanoGPT), the feed-forward network is a two-layer model, where the hidden layer is slightly wider[5](https://cameronrwolfe.substack.com/p/language-model-training-and-inference?open=false#footnote-5-136638774) than the input layer. The block’s input is normalized prior to each of the two layers, and a residual connection is added between the layers. See below for an illustration.

[

![](Language%20Model%20Training%20and%20Inference%20From%20Concept%20to%20Code/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252F3c924527-cc5b-463a-96a3-c2969e600883_334x582.png)

](https://substackcdn.com/image/fetch/$s_!w1LX!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F3c924527-cc5b-463a-96a3-c2969e600883_334x582.png)

Schematic of a decoder-only transformer block

**Model definition.** Now that we understand the structure of a decoder-only transformer block, we can look at NanoGPT’s full model definition. This definition is provided below, where we see the [constructor](https://www.geeksforgeeks.org/constructors-in-python/) for the model class.

[

![](Language%20Model%20Training%20and%20Inference%20From%20Concept%20to%20Code/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252F4a908daa-d345-4e9e-b4f4-d4af5de0f1e0_2114x1526.png)

](https://substackcdn.com/image/fetch/$s_!sbXc!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F4a908daa-d345-4e9e-b4f4-d4af5de0f1e0_2114x1526.png)

As shown above, the LLM contains two different embedding layers—one to store token embeddings and one to store positional embeddings. There are 1024 positional embeddings, corresponding to the context length used to train NanoGPT (i.e., `block_size` setting in the configuration). The language model has 12 transformer blocks in total. The weights of the model are initialized [normally](https://github.com/karpathy/nanoGPT/blob/master/model.py#L162), aside from a few special techniques adopted from GPT-2 \[1\].

Beyond the basic transformer architecture, there are extra [dropout](https://pytorch.org/docs/stable/generated/torch.nn.Dropout.html) and [LayerNorm](https://pytorch.org/docs/stable/generated/torch.nn.LayerNorm.html) modules that are used during the forward pass at the first/final layer of the LLM. Plus, we have a linear classification head that is used for next token prediction and shares weights with the token embedding layer. This weight sharing method, called [weight tying](https://paperswithcode.com/method/weight-tying) \[3\], can improve performance while drastically decreasing the total number of parameters in the model[6](https://cameronrwolfe.substack.com/p/language-model-training-and-inference?open=false#footnote-6-136638774).

#### Implementing Next Token Prediction

[

![](Language%20Model%20Training%20and%20Inference%20From%20Concept%20to%20Code/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252Fa0695ab4-3547-436a-a00b-f88245869f28_1820x1024.jpeg)

](https://substackcdn.com/image/fetch/$s_!AfDI!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fa0695ab4-3547-436a-a00b-f88245869f28_1820x1024.png)

Pretraining a language model with next token prediction

Now that we understand the implementation of an LLM’s model architecture, we will take a look at a pretraining and inference implementation with the same architecture. Both pretraining (shown above) and inference rely upon a next token prediction strategy, and we will overview the implementation of next token prediction for each of these processes within this section.

**Forward pass.** To understand how to train NanoGPT, we need to understand the model’s forward pass. There are two different types of forward passes that we can consider—_one for training and one for inference_. The code for NanoGPT’s forward pass (i.e., this method is part of the GPT model class provided previously) is shown below. First, we will consider how this forward pass is used during pretraining, then will return to the inference process later.

[

![](Language%20Model%20Training%20and%20Inference%20From%20Concept%20to%20Code/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252F83f92e86-d0c9-4c10-a1e9-70a9f69283c9_2168x1564.jpeg)

](https://substackcdn.com/image/fetch/$s_!YcNG!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F83f92e86-d0c9-4c10-a1e9-70a9f69283c9_2168x1564.png)

The forward pass operates as we might expect. We take two tensors as input:

-   _Input tensor_ (`idx`): a matrix where each row contains a sequence of token ids, representing a textual sequence to use for pretraining (or inference).
    
-   _Target tensor_ (`targets`): similar to the input tensor, but each entry contains the ground truth next token id for each token in the input tensor.
    

Each of these tensors store an entire [mini-batch](https://machinelearningmastery.com/gentle-introduction-mini-batch-gradient-descent-configure-batch-size/) that contains multiple sequences of text over which a training iteration is parallelized. Here, we will assume the target tensor is not `None`. This is always true during pretraining, while during inference we have no target and are just freely generating next tokens.

[

![](Language%20Model%20Training%20and%20Inference%20From%20Concept%20to%20Code/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252F2ea151b2-0d4d-4a50-b701-22a232342a79_724x366.jpeg)

](https://substackcdn.com/image/fetch/$s_!KkOY!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F2ea151b2-0d4d-4a50-b701-22a232342a79_724x366.png)

The first step in the forward pass it to construct a matrix corresponding to our positional and token embeddings; see above. The `idx` tensor contains token ids that can be directly used for lookup within the token embedding matrix. We have to manually construct index values to look up positional embeddings. Positional and token embeddings are added together, passed through a dropout layer, and passed through all transformer blocks. Then, a final LayerNorm operation is performed before computing the loss with the next token prediction objective.

[

![](Language%20Model%20Training%20and%20Inference%20From%20Concept%20to%20Code/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252Ffc60ee97-77ad-40b9-af54-830b71dc1882_1156x214.jpeg)

](https://substackcdn.com/image/fetch/$s_!kNow!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Ffc60ee97-77ad-40b9-af54-830b71dc1882_1156x214.png)

The next token prediction process outputs a distribution over potential next tokens—using the linear `lm_head` module, where the transformer’s output vector for each token is used as input—for every token within the input sequence. Then, we apply a [CrossEntropy](https://pytorch.org/docs/stable/generated/torch.nn.functional.cross_entropy.html) loss to this result, thus training the model to correctly predict the next token at every position within the entire input sequence.

[

![](Language%20Model%20Training%20and%20Inference%20From%20Concept%20to%20Code/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252F2d8f6830-66bf-48f5-888b-4ceaac2a11c0_2082x1414.png)

](https://substackcdn.com/image/fetch/$s_!89P6!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F2d8f6830-66bf-48f5-888b-4ceaac2a11c0_2082x1414.png)

**Performing inference.** Beyond pretraining, we can can generate text with next token prediction. As explained previously, generating text with a language model is an autoregressive process that iteratively predicts each next token. To predict a token, NanoGPT follows the steps outlined below:

1.  Perform a forward pass with the current input sequence
    
2.  Scale the outputted [logits](https://wandb.ai/amanarora/Written-Reports/reports/Understanding-Logits-Sigmoid-Softmax-and-Cross-Entropy-Loss-in-Deep-Learning--Vmlldzo0NDMzNTU3) according to the specified [temperature](https://twitter.com/cwolferesearch/status/1671628210180698112?s=20)
    
3.  \[Optional\] Remove all but the `k` most likely tokens (i.e., [Top-K sampling](https://docs.cohere.com/docs/controlling-generation-with-top-k-top-p))
    
4.  Apply the [softmax](https://en.wikipedia.org/wiki/Softmax_function) function
    
5.  Sample the next token from the resulting distribution
    

Notably, the forward pass within the code above uses the same exact forward pass we defined previously, but no target tensor is specified within the input!

#### NanoGPT Training

Although distributed training is a complex topic that we will not be able to cover thoroughly in this overview, we will cover the practical highlights of NanoGPT’s pretraining process for the purpose of completeness. We typically distribute LLM training across multiple compute devices (e.g., GPUs or [TPU](https://en.wikipedia.org/wiki/Tensor_Processing_Unit)s). At a high level, there are a few reasons that distributed training is desirable and/or necessary:

-   Pretraining is computationally expensive and we want to speed it up.
    
-   The size of the model might be too big to store on a single device.
    

The second case outlined above is especially applicable to the current generation of language models, which are quite large and typically cannot be stored on a single device. A variety of distributed training techniques exist that can handle these cases and speed up the training process; see [here](https://twitter.com/rasbt/status/1625494398778892292?s=20) for a summary.

**Distributed training setup.** The full pretraining implementation is provided within the [train.py file](https://github.com/karpathy/nanoGPT/blob/master/train.py) within NanoGPT’s repository. The model is trained using either using a single GPU or with a [distributed data parallel (DDP)](https://pytorch.org/tutorials/intermediate/ddp_tutorial.html) approach. The setup of this training framework is shown below.

[

![](Language%20Model%20Training%20and%20Inference%20From%20Concept%20to%20Code/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252F8cf5757b-34ae-4f5f-b0bc-2b9bcba54b67_2168x1600.jpeg)

](https://substackcdn.com/image/fetch/$s_!QFWJ!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F8cf5757b-34ae-4f5f-b0bc-2b9bcba54b67_2168x1600.png)

As we can see, training with DDP requires that we simultaneously run multiple training processes[7](https://cameronrwolfe.substack.com/p/language-model-training-and-inference?open=false#footnote-7-136638774) that will communicate together. The number of processes is equal to the total number of GPUs that we have available (either on the same machine or across multiple nodes) for training. Using DDP, we can parallelize the training process across these GPUs. To coordinate the multiple processes that are running, we must specify a rank for each process. For example, if there are four total processes running training across four GPUs, these processes will each have a unique rank within the range \[0, 3\][8](https://cameronrwolfe.substack.com/p/language-model-training-and-inference?open=false#footnote-8-136638774). In the code above, all rank information is stored within an [environment variable](https://towardsdatascience.com/environment-variables-python-aecb9bf01b85) that can be accessed by the process.

**Gradient accumulation.** Within the NanoGPT implementation, you might see the term gradient accumulation mentioned a few times. Typically, we train a neural network by:

-   Computing the loss over a mini-batch of data
    
-   Backpropagating this loss to derive a gradient
    
-   Updating the model’s weights based on this gradient
    

Gradient accumulation removes the last step shown above. Instead, the gradient is _accumulated_ (i.e., by just taking an average) across multiple “micro-batches” of data that simulate a single, larger mini-batch. Once we have accumulated gradients across a sufficient amount of data, we update the weights. Such a process is useful when our desired batch size is too large for the hardware being used. We can simply compute the gradient over several smaller batches and use gradient accumulation to simulate the larger batch. See [here](https://kozodoi.me/blog/20210219/gradient-accumulation) for more details.

**What if we have a larger model?** With DDP, a copy of the model is sent to each device, and we train these copies of the model in parallel by _i)_ computing gradients over data that is randomly sampled on each device and _ii)_ getting an aggregated model update by synchronizing the gradients on each device after a mini-batch. For many modern LLMs, we might not be able to store the full model within the memory of a single device, so we need a different training approach. One of the most popular distributed training algorithms that is compatible with such large models is [fully sharded data parallel (FSDP)](https://pytorch.org/tutorials/intermediate/FSDP_tutorial.html) training \[4\]. This approach, as opposed to DDP, is more commonly used for training modern LLMs.

[

![](Language%20Model%20Training%20and%20Inference%20From%20Concept%20to%20Code/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252F6a2d7353-385e-4266-a667-5bdc345cf20e_2168x894.png)

](https://substackcdn.com/image/fetch/$s_!CzFF!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F6a2d7353-385e-4266-a667-5bdc345cf20e_2168x894.png)

**Loading the data.** There are many ways in which we can create a [data loader](https://pytorch.org/tutorials/beginner/basics/data_tutorial.html) for training a language model. One (simplified) example is shown within the code above. Here, the data is stored within a single file, and we have separate files for training and validation data. This data is loaded during training by simply taking random chunks with the size of the context window. We can optionally put this data onto the GPU, but the overall process is simple enough!

[

![](Language%20Model%20Training%20and%20Inference%20From%20Concept%20to%20Code/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252F7b057707-9c67-4a13-89ac-c7d1b2c8f342_2168x930.jpeg)

](https://substackcdn.com/image/fetch/$s_!lbAd!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F7b057707-9c67-4a13-89ac-c7d1b2c8f342_2168x930.png)

**The learning rate.** One of the main hyperparameters that we need to think about while pretraining a language model is the learning rate. Typically, we will adopt a [schedule](https://cameronrwolfe.substack.com/p/the-best-learning-rate-schedules) for the learning rate during pretraining. An example implementation of a typical learning rate schedule for language model pretraining is shown above. Here, the schedule has a short (linear) warm-up period followed by a (cosine) decay period that lasts for a specified number of iterations; see below.

[

![](Language%20Model%20Training%20and%20Inference%20From%20Concept%20to%20Code/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252Fa0c86d2c-9d19-4026-afbc-60b9d0d1c9d3_640x480.png)

](https://substackcdn.com/image/fetch/$s_!Q8nv!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fa0c86d2c-9d19-4026-afbc-60b9d0d1c9d3_640x480.png)

Cosine decay learning rate schedule used for language model pretraining

**The training loop.** Now that we have done all of the necessary setup, we can finally implement the actual (pre)training loop for our language model; see below.

[

![](Language%20Model%20Training%20and%20Inference%20From%20Concept%20to%20Code/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252F86475da5-84a5-42c9-929f-3ca87927dbfd_2082x1936.png)

](https://substackcdn.com/image/fetch/$s_!yYxz!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F86475da5-84a5-42c9-929f-3ca87927dbfd_2082x1936.png)

There may be a few unfamiliar components in the implementation above (e.g., gradient clipping and loss scaling). Most of these changes are related to [automatic mixed precision (AMP)](https://pytorch.org/docs/stable/notes/amp_examples.html) training, which is a supported (but not mandatory) component of NanoGPT. Aside from these added details, the above code matches our prior discussion of the pretraining process and uses standard PyTorch syntax.

## Closing Thoughts

Reading papers about LLMs is fun and informative, but we can only go so far by just reading. Eventually, we have to implement these ideas if we want to build anything tangible. In this overview, we first learned about the idea of next token prediction and its application to causal language models. Then, we explored a concrete implementation of next token prediction for pretraining and inference with an LLM in PyTorch. Although this implementation is simple compared to some of the massive language models that are explored by current research, it lays a practical foundation that gives us a more concrete understanding of LLMs.

#### New to the newsletter?

Hi! I’m [Cameron R. Wolfe](https://cameronrwolfe.me/), deep learning Ph.D. and Director of AI at [Rebuy](https://www.rebuyengine.com/). This is the Deep (Learning) Focus newsletter, where I help readers understand AI research via overviews of relevant topics from the ground up. If you like the newsletter, please subscribe, share it, or follow me on [Medium](https://medium.com/@wolfecameron), [X](https://twitter.com/cwolferesearch), and [LinkedIn](https://www.linkedin.com/in/cameron-r-wolfe-ph-d-04744a238/)!

#### Bibliography

\[1\] Radford, Alec, et al. "Language Models are Unsupervised Multitask Learners."

\[2\] Radford, Alec, et al. "Improving language understanding by generative pre-training." (2018). 

\[3\] Press, Ofir, and Lior Wolf. "Using the output embedding to improve language models." _arXiv preprint arXiv:1608.05859_ (2016).

\[4\] Ott, Myle, et al. "Fully sharded data parallel: faster ai training with fewer gpus." (2021).

\[5\] Vaswani, Ashish, et al. "Attention is all you need." _Advances in neural information processing systems_ 30 (2017).

\[6\] Su, Jianlin, et al. "Roformer: Enhanced transformer with rotary position embedding." _arXiv preprint arXiv:2104.09864_ (2021).

\[7\] Press, Ofir, Noah A. Smith, and Mike Lewis. "Train short, test long: Attention with linear biases enables input length extrapolation." _arXiv preprint arXiv:2108.12409_ (2021).

\[8\] Ouyang, Long, et al. "Training language models to follow instructions with human feedback." _Advances in Neural Information Processing Systems_ 35 (2022): 27730-27744.

\[9\] Glaese, Amelia, et al. "Improving alignment of dialogue agents via targeted human judgements." _arXiv preprint arXiv:2209.14375_ (2022).

\[10\] Yao, Shunyu, et al. "Tree of thoughts: Deliberate problem solving with large language models." _arXiv preprint arXiv:2305.10601_ (2023).

[1](https://cameronrwolfe.substack.com/p/language-model-training-and-inference?open=false#footnote-anchor-1-136638774)

In fact, I watched the first version of this course during my undergrad, when I was first learning about neural networks. It advanced my understanding significantly and made me capable of implementing a lot of the ideas that I would see in books or papers.

[2](https://cameronrwolfe.substack.com/p/language-model-training-and-inference?open=false#footnote-anchor-2-136638774)

As we will see later, the token embeddings are part of the language model and are trained normally along with the rest of the model’s parameters.

[3](https://cameronrwolfe.substack.com/p/language-model-training-and-inference?open=false#footnote-anchor-3-136638774)

This isn’t always the case. For example, we might be able to support a longer context length but choose to use a shorter context length because a longer context is not necessary for a certain application.

[4](https://cameronrwolfe.substack.com/p/language-model-training-and-inference?open=false#footnote-anchor-4-136638774)

The GPT-2 publication studies multiple sizes of models, the largest of which contains roughly 1.5 billion parameters.

[5](https://cameronrwolfe.substack.com/p/language-model-training-and-inference?open=false#footnote-anchor-5-136638774)

See [here](https://github.com/karpathy/nanoGPT/blob/master/model.py#L78) for the exact feed-forward network implementation by NanoGPT. The input to the feed-forward model is of size 768 (i.e., size of a single token embedding), while the hidden layer is `4X` wider than this.

[6](https://cameronrwolfe.substack.com/p/language-model-training-and-inference?open=false#footnote-anchor-6-136638774)

Notably, the token embedding layer is huge! If we have a vocabulary of `V` tokens and use `d` dimensional vectors for each token, this layer has `V x d` parameters that are learned throughout pretraining. The next token prediction layer has the same exact number of parameters, so tying their weights together is highly beneficial.

[7](https://cameronrwolfe.substack.com/p/language-model-training-and-inference?open=false#footnote-anchor-7-136638774)

We can just think of this as running the training script from multiple terminals at the same time

[8](https://cameronrwolfe.substack.com/p/language-model-training-and-inference?open=false#footnote-anchor-8-136638774)

We specify both rank and local rank. Rank corresponds to a process’ rank among all other processes. Notably, however, we might be running training across several compute nodes (e.g., across several servers, each of which have eight GPUs). Local rank corresponds to the rank of a process on its individual node.