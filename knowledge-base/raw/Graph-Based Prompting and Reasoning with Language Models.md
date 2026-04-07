## Background Information

[

![Deci AI Logo Vector Download - (.SVG + .PNG) - Logovectordl.Com](Graph-Based%20Prompting%20and%20Reasoning%20with%20Language%20Models/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252F6044b0b1-3002-4ce7-91d8-c752d896d340_900x500.png "Deci AI Logo Vector Download - (.SVG + .PNG) - Logovectordl.Com")

](https://substackcdn.com/image/fetch/$s_!7vgY!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F6044b0b1-3002-4ce7-91d8-c752d896d340_900x500.png)

This newsletter is presented by [Deci AI](https://deci.ai/). Deci does a ton of interesting AI research. Most recently, they released DeciCoder-1B, an open-source code generation model. Read about it [here](https://twitter.com/cwolferesearch/status/1691929174175264858?s=20) or [download it](https://huggingface.co/Deci/DeciCoder-1b) on HuggingFace.

If you like the newsletter, feel free to [get in touch with me](https://cameronrwolfe.me/) or follow me on [Medium](https://medium.com/@wolfecameron), [X](https://twitter.com/cwolferesearch), and [LinkedIn](https://www.linkedin.com/in/cameron-r-wolfe-ph-d-04744a238/). I try my best to produce useful/informative content.

[

![](Graph-Based%20Prompting%20and%20Reasoning%20with%20Language%20Models/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252F553be3b4-3c80-435d-88c5-c7079bff9cbb_1940x1090.jpeg)

](https://substackcdn.com/image/fetch/$s_!bEsV!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F553be3b4-3c80-435d-88c5-c7079bff9cbb_1940x1090.png)

(from \[1, 2\])

Advanced prompting techniques like [chain of thought](https://cameronrwolfe.substack.com/p/chain-of-thought-prompting-for-llms) \[8\] and [tree of thought](https://cameronrwolfe.substack.com/p/tree-of-thoughts-prompting) \[9\] prompting have drastically improved the ability of large language models (LLMs) to solve complex, reasoning-based tasks. At a high level, forcing the LLM to construct a step-by-step response to a problem drastically improves its problem-solving capabilities. However, all of such techniques assume that the reasoning process should follow a linear patterns that progresses from one thought to the next. Notably, the reasoning process followed by humans tends to be quite different, following multiple different chains of thought and even combining insights from different thoughts to arrive at a final solution. Within this overview, we will studying several prompting techniques that model the reasoning process as a graph structure—rather than a chain or tree—that better captures the various types of non-linear patterns that may occur when reasoning over a problem.

> _“Human thinking is often characterized by its ability to make sudden leaps and connections between seemingly unrelated ideas, which can lead to novel insights and solutions. This non-linear, jumping thought process is a hallmark of human creativity, reasoning, and problem-solving abilities.”_ - from \[1\]

## Background Information

Within this overview, we will explore several advanced prompting techniques for LLMs that can be used to solve difficult multi-step reasoning problems. Luckily, we have recently overviewed the basic ideas behind prompting, including:

-   Prompting basics (i.e., prompt engineering, context windows, structure of a prompt, etc.) \[[link](https://cameronrwolfe.substack.com/i/136223454/the-basics-of-prompting)\]
    
-   Simple prompting techniques (e.g., zero/few-shot learning and instruction prompting) \[[link](https://cameronrwolfe.substack.com/p/tree-of-thoughts-prompting#%C2%A7hierarchy-of-prompting-techniques)\]
    
-   Advanced prompting techniques (e.g., chain of thought, self-consistency, and least-to-most prompting) \[[link](https://cameronrwolfe.substack.com/i/136223454/advanced-prompting-techniques)\]
    

We have covered both [practical](https://cameronrwolfe.substack.com/p/practical-prompt-engineering-part) and [advanced](https://cameronrwolfe.substack.com/p/advanced-prompt-engineering) prompting techniques in the past. All of these concepts—especially [chain of thought (CoT) prompting](https://cameronrwolfe.substack.com/p/chain-of-thought-prompting-for-llms) \[8\], [self-consistency](https://cameronrwolfe.substack.com/i/116166267/variants-of-cot-prompting) \[10\], and [tree of thought (ToT) prompting](https://cameronrwolfe.substack.com/p/tree-of-thoughts-prompting) \[9\]—will be relevant for gaining an understanding of this overview. Beyond these ideas, we need to understand the transformer architecture and the graph convolutional network (GCN) \[13\], which is applicable to machine learning on graph-structured data.

#### The Transformer from Top to Bottom

The transformer architecture, proposed in \[11\], was originally applied to Seq2Seq[1](https://cameronrwolfe.substack.com/p/graph-based-prompting-and-reasoning?open=false#footnote-1-136366740) tasks (e.g., language translation). However, this model—and several of its variants—has since evolved to capture a variety of different use cases, such as:

-   Vision transformers \[4\] for object [detection](https://github.com/facebookresearch/detr) and [classification](https://cameronrwolfe.substack.com/p/vision-transformers-from-idea-to) in images
    
-   [Encoder-only transformers](https://cameronrwolfe.substack.com/i/76273144/berts-architecture) for [discriminative language tasks](https://cameronrwolfe.substack.com/p/language-understanding-with-bert)
    
-   [Decoder-only transformers](https://twitter.com/cwolferesearch/status/1640446111348555776?s=20) for [language modeling](https://cameronrwolfe.substack.com/i/85568430/language-modeling)
    

Many deep learning architectures are used in practice, but the transformer is unique in its scope—_it is a single architecture that can be applied to a massive variety of task_s. First, we will learn about the standard, encoder-decoder transformer architecture, then we will extend this discussion to other notable variants.

[

![](Graph-Based%20Prompting%20and%20Reasoning%20with%20Language%20Models/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252F4ff80936-f5fd-410f-8dc2-f09a16f29bfb_742x1166.png)

](https://substackcdn.com/image/fetch/$s_!_iMp!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F4ff80936-f5fd-410f-8dc2-f09a16f29bfb_742x1166.png)

**Encoder-decoder transformers.** The transformer has two components:

-   _Encoder_: each block contains [bidirectional, multi-headed self-attention](https://twitter.com/cwolferesearch/status/1641932082283700226?s=20) and a [feed-forward](https://cameronrwolfe.substack.com/i/94634004/feed-forward-neural-networks) transformation (usually a two-layer feed-forward network).
    
-   _Decoder_: each block contains [masked self-attention](https://twitter.com/cwolferesearch/status/1644773244786941952?s=20), [cross-attention](https://vaclavkosar.com/ml/cross-attention-in-transformer-architecture), and a feed-forward transformation.
    

In prior overviews, we have discussed how [raw text is processed](https://cameronrwolfe.substack.com/i/135273362/the-language-modeling-objective) before being ingested by a transformer. This processing converts text into a sequence of vectors—_with added positional information_—corresponding to each token in the input. This sequence of vectors is then ingested by the transformer’s encoder, which performs the operations described above. See below for a depiction.

[

![](Graph-Based%20Prompting%20and%20Reasoning%20with%20Language%20Models/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252F2cac73ca-fa2b-471c-b1bd-a023af6264e8_1754x1166.jpeg)

](https://substackcdn.com/image/fetch/$s_!V49-!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F2cac73ca-fa2b-471c-b1bd-a023af6264e8_1754x1166.png)

Depiction of a basic transformer encoder block

The output of this block is simply a sequence of token vectors that have been transformed via bidirectional self-attention and a feed-forward neural network. We can then take the resulting sequence that has been passed though all blocks of the encoder and use it as input for the decoder component. Put simply, _the encoder forms a representation of the entire input sequence using bidirectional self-attention_, meaning that every token within the input sequence considers all other tokens in the sequence when crafting the encoder’s output sequence.

The decoder then ingests the encoder’s output and uses this representation of the input sequence as context when generating output. The decoder portion of the transformer is similar to the encoder with two main differences:

1.  It uses [masked self-attention](https://twitter.com/cwolferesearch/status/1644773244786941952?s=20).
    
2.  It has an added cross-attention mechanism.
    

Masked self-attention restricts the multi-headed self-attention operation in the decoder from “looking forward” in the sequence. In other words, each token’s representation only depends on the tokens that come before it; see below.

[

![](Graph-Based%20Prompting%20and%20Reasoning%20with%20Language%20Models/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252F31acf19b-f698-4bf3-a992-821c3f000d58_1160x408.png)

](https://substackcdn.com/image/fetch/$s_!51QC!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F31acf19b-f698-4bf3-a992-821c3f000d58_1160x408.png)

Such a modification is necessary because the decoder is expected to generate a textual sequence as output. If the decoder used bidirectional self-attention, the model would be able to “cheat” during training by looking at the correct next token within the target sequence and copying it when predicting the next token. Masked self-attention avoids this issue and can be efficiently trained to generate coherent text via [next token prediction](https://cameronrwolfe.substack.com/i/135273362/the-language-modeling-objective). Cross attention is similar to any other attention operation, but it fuses two separate sequences—from the encoder and the decoder—with a single attention operation. See [here](https://sebastianraschka.com/blog/2023/self-attention-from-scratch.html) for more details.

**Example of the encoder-decoder architecture.** One notable and widely-used example of a standard, encoder-decoder transformer architecture is the text-to-text transformer (T5) model \[5\]. This model is heavily used for transfer learning tasks with natural language and is even used by one of the prompting techniques that we will learn about in this overview. Analysis of T5 shows us that encoder-decoder transformers are useful for Seq2Seq tasks and prefix language modeling tasks[2](https://cameronrwolfe.substack.com/p/graph-based-prompting-and-reasoning?open=false#footnote-2-136366740), which are both common practical problems. To learn more about the T5 architecture, feel free to check out the prior overview on this topic linked below.

-   T5 Architecture (Part One) \[[link](https://cameronrwolfe.substack.com/p/t5-text-to-text-transformers-part)\]
    
-   T5 Architecture (Part Two) \[[link](https://cameronrwolfe.substack.com/p/t5-text-to-text-transformers-part-354)\]
    

**Encoder-only and decoder-only variants.** Within the explanation of T5 linked above, we learn extensively about the [different variants](https://cameronrwolfe.substack.com/i/108182616/different-transformer-architectures) of the transformer architecture. The two most notable variants are _encoder-only_ and _decoder-only_ models, both of which are relatively self-explanatory. Encoder-only architectures use the encoder portion of the transformer and completely eliminate the decoder. Such an architecture was popularized by [BERT](https://cameronrwolfe.substack.com/p/language-understanding-with-bert) \[12\] and is incredibly effective when fine-tuned on a variety of different discriminative language tasks (e.g., sentence classification, named entity recognition, question answering, etc.).

[

![](Graph-Based%20Prompting%20and%20Reasoning%20with%20Language%20Models/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252Fe22dcc71-2a18-4d31-b811-9fae5d6c2889_1586x750.jpeg)

](https://substackcdn.com/image/fetch/$s_!BUno!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fe22dcc71-2a18-4d31-b811-9fae5d6c2889_1586x750.png)

The decoder-only transformer architecture (from \[11\])

Similarly, decoder-only architectures just eliminate the encoder portion of the transformer. However, this means that we also must get rid of any cross-attention modules due to the lack of an encoder; see above. As such, each block of a decoder-only transformer just performs masked self-attention and a feed-forward transformation. These architectures have exploded in popularity recently due to their heavy use in large, causal language models. Most of the generative LLMs that are widely studied today—[GPT variants](https://cameronrwolfe.substack.com/p/language-models-gpt-and-gpt-2), [PaLM](https://cameronrwolfe.substack.com/p/palm-efficiently-training-massive), [Falcon](https://cameronrwolfe.substack.com/p/falcon-the-pinnacle-of-open-source), [LLaMA-2](https://cameronrwolfe.substack.com/p/llama-2-from-the-ground-up), etc.—rely upon a decoder-only transformer architecture.

#### AI with Graph-Structured Data

[

![](Graph-Based%20Prompting%20and%20Reasoning%20with%20Language%20Models/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252Fe9692ad0-7227-4541-8b40-ddf2e59d94b2_1190x434.png)

](https://substackcdn.com/image/fetch/$s_!vYud!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fe9692ad0-7227-4541-8b40-ddf2e59d94b2_1190x434.png)

Basic examples of Euclidean and non-Euclidean data

Within this overview, we will learn about prompting techniques that leverage a graph data structure to model the reasoning processes. With this in mind, we need to learn about how graph-structured data is usually handled within machine learning applications. Namely, most model architectures (e.g., transformers or [convolutional neural networks](https://towardsdatascience.com/convolutional-neural-networks-explained-9cc5188c4939)) are meant for handling [Euclidean data](https://ai.stackexchange.com/questions/11226/what-is-non-euclidean-data) (e.g., images or text) that can easily be represented as a matrix. However, not all data is Euclidean. In fact, many sources of real world data are more appropriately modeled as a [graph](https://www.geeksforgeeks.org/graph-data-structure-and-algorithms/) (e.g., social networks, molecules, etc.). For such data, we use a special model architecture called a [graph convolutional network (GCN)](https://distill.pub/2021/gnn-intro/) \[13\].

[

![](Graph-Based%20Prompting%20and%20Reasoning%20with%20Language%20Models/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252Ff5ddfb0a-863e-4e3b-90d0-20d212bf0ef0_1236x882.png)

](https://substackcdn.com/image/fetch/$s_!1Vp_!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Ff5ddfb0a-863e-4e3b-90d0-20d212bf0ef0_1236x882.png)

Illustration of a layer in a graph convolutional network

**Understanding the GCN.** At their core, GCNs are not much different from your typical feed-forward neural network. Given a graph, we associate each node in this graph with an input embedding, which can come from a variety of sources (e.g., embedding of a document, features corresponding to a user, etc.). Then, in each layer of the GCN, we first apply a feed-forward transformation to each node embedding (and normalization). Then, we incorporate the structure of the underlying graph by aggregating neighboring features for each node, such as by taking an average of all neighboring node embeddings; see above. By adding multiple layers to the GCN, we can learn rich node representations that capture both the properties of each node and the structure of the graph; read more below.

[More on GCNs](https://distill.pub/2021/gnn-intro/)

**Other architectures.** The GCN architecture has gained a massive amount of popularity and is widely-used in a variety of impressive, large-scale applications (e.g., [Google Maps](https://arxiv.org/abs/2108.11482)). Given this popularity, several extensions to the GCN have been proposed, including new architectural variants.. One notable example, which we will see used in this overview, is the [Graph Attention Network (GAT)](https://petar-v.com/GAT/).

[

![](Graph-Based%20Prompting%20and%20Reasoning%20with%20Language%20Models/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252Fcd1bd461-74e7-43e4-8151-e24ea4262071_1348x884.jpeg)

](https://substackcdn.com/image/fetch/$s_!0j4b!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fcd1bd461-74e7-43e4-8151-e24ea4262071_1348x884.png)

(from \[14\])

The GAT \[14\] architecture is somewhat similar to the GCN, but it doesn’t just perform a simple average to aggregate features from neighboring nodes. Rather, a weighted average is taken over neighboring node features, where the weights are computed using an attention mechanism. The attention mechanism used in \[14\] is simple—it just takes two concatenated node embeddings as input and performs a feed-forward transformation to compute a score; see above. Such an approach allows more general aggregations of neighboring features to be learned.

#### Multi-Modal CoT Reasoning

[

![](Graph-Based%20Prompting%20and%20Reasoning%20with%20Language%20Models/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252Fa6aeb7fb-10a7-4d6f-bc41-efb7e556b6ef_664x476.jpeg)

](https://substackcdn.com/image/fetch/$s_!xrrD!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fa6aeb7fb-10a7-4d6f-bc41-efb7e556b6ef_664x476.png)

(from \[3\])

Finally, before moving on to graph-based prompting techniques, there is one final prompting technique of which we will want to be aware—[multi-modal chain of thought prompting](https://towardsdatascience.com/multimodal-chain-of-thoughts-solving-problems-in-a-multimodal-world-961a8ab9d0fa) \[3\]. This method, depicted above, proposes a two-stage approach for solving reasoning problems with both textual and visual inputs. In the first stage, the model takes both text and images as inputs and uses them to generate a problem-solving rationale similar to a chain of thought \[8\]. Then, this rationale is concatenated with the input and passed though the model—_along with the image_s—once again to produce a final answer. Notably, this approach uses a T5 architecture \[5\] and is fine-tuned on the tasks that it solves. As we will see, the approach used by graph of thought reasoning \[1\] is quite similar.

## Going Beyond Chain (or Tree) of Thought

[

![](Graph-Based%20Prompting%20and%20Reasoning%20with%20Language%20Models/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252Ff04dd32f-0938-47dc-a8c8-c6a4377a5b12_1604x858.jpeg)

](https://substackcdn.com/image/fetch/$s_!eW47!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Ff04dd32f-0938-47dc-a8c8-c6a4377a5b12_1604x858.png)

(from \[4\])

Although CoT prompting is incredibly impactful, we have seen that it has [important limitations](https://cameronrwolfe.substack.com/i/136223454/advanced-prompting-techniques). Most notably, it generates problem solving rationales in a left-to-right fashion using [next token prediction](https://cameronrwolfe.substack.com/i/135273362/the-language-modeling-objective), _which prevents the model from recovering from early mistakes in the reasoning process_. One solution to this problem is [Tree of Thoughts (ToT)](https://cameronrwolfe.substack.com/p/tree-of-thoughts-prompting) prompting (shown above), which enables backtracking and strategic lookahead over intermediate reasoning steps modeled as a tree. Despite its utility, ToT prompting still models reasoning and problem solving as a linear process that progresses over a single path of nodes within a tree, which fundamentally limits the capabilities of this prompting technique.

> _“By representing thought units as nodes and connections between them as edges, our approach captures the non-sequential nature of human thinking and allows for a more realistic modeling of thought processes.”_ \- from \[1\]

As we have discussed, humans do not reason linearly. Rather, we make leaps and connections between ideas that lead to novel insights. Inspired by this idea, researchers have recently extended chain and tree of thoughts prompting to graph-structured data. In other words, we model the reasoning process as a graph, rather than as a chain or tree. In this section, we will overview this work and how it can be used to improve the reasoning capabilities of LLMs.

#### Beyond Chain-of-Thought, Effective Graph-of-Thought Reasoning in Large Language Models \[1\]

[

![](Graph-Based%20Prompting%20and%20Reasoning%20with%20Language%20Models/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252F8ba9398f-32d5-4e02-bf8b-05561a51e6b6_1608x884.jpeg)

](https://substackcdn.com/image/fetch/$s_!6RYC!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F8ba9398f-32d5-4e02-bf8b-05561a51e6b6_1608x884.png)

(from \[1\])

In \[1\], authors propose a two-stage reasoning framework[3](https://cameronrwolfe.substack.com/p/graph-based-prompting-and-reasoning?open=false#footnote-3-136366740), called graph-of-thought reasoning (we’ll call it GOTR for short), for solving reasoning tasks with textual (and potentially visual) inputs. In the first stage, the language model is used to generate a problem-solving rationale. Then, the second stage uses this generated rationale to arrive at a final answer. This two-stage process is inspired by multi-modal CoT \[3\]. The GOTR framework relies upon three different kinds of inputs during the reasoning process:

-   _Text_: This is just the normal, textual input that we get for any prompt-based reasoning task.
    
-   _Image_: We can (optionally) ingest an image that is associated with the reasoning task.
    
-   _Thought Graph_: We generate a graph of all named entities within the textual input and their relationships to use as input.
    

As we will see, each of these inputs are given separate encoders within \[1\]. Then, the representations generated by each of these encoders is fused and passed to a decoder module that can generate output—_either a rationale or final answer_.

> _“By representing thought units as nodes and connections between thoughts as edges, the Graph-of-Thought captures the rich, non-sequential nature of human thinking and allows for a more realistic and logical modeling of reasoning processes.”_ - from \[1\]

**Two-stage framework.** As mentioned above, GOTR operates in a two-stage framework. In the first stage, the model is given the input text for the problem being solved and is expected to generate a problem-solving rationale—_similar to a chain of thought_. Then, the rationale that is generated during the first phase is just concatenated with the input text, and we generate output once again. The only difference between the first and second stages is that:

-   The second stage has a longer input (i.e., both input text and the rationale).
    
-   The second stage generates a final answer rather than a rationale.
    

However, the structure of both stages is identical other than the modified inputs and outputs. This two-stage process followed by GOTR is depicted below, where we see that two different kinds of outputs are generated in each stage.

[

![](Graph-Based%20Prompting%20and%20Reasoning%20with%20Language%20Models/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252F6c037be3-7b93-4815-a15c-7ea3165e8a4b_1548x952.jpeg)

](https://substackcdn.com/image/fetch/$s_!46tN!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F6c037be3-7b93-4815-a15c-7ea3165e8a4b_1548x952.png)

Two-stage framework for GOTR (from \[1\])

**Generating the thought graph.** As mentioned before, GOTR takes three sources of data as input: text, images, and a thought graph. The image data is completely optional—_GOTR works perfectly fine without it_. But, we might be wondering: _Where does the thought graph come from?_ Interestingly, we see in \[1\] that the thought graph is constructed based on the input text. A depiction of this is shown below.

[

![](Graph-Based%20Prompting%20and%20Reasoning%20with%20Language%20Models/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252Fe0896987-3aef-4fa8-bea7-2c85c4116967_1444x522.png)

](https://substackcdn.com/image/fetch/$s_!wPjI!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fe0896987-3aef-4fa8-bea7-2c85c4116967_1444x522.png)

(from \[1\])

More specifically, the thought graph in GOTR is used to represent the named entities within the input text and their relationships. To generate this graph, we just use off-the-shelf tools (i.e., from the [CoreNLP](https://stanfordnlp.github.io/CoreNLP/) framework) to extract subject-verb-object triplets from the text and perform coreference resolution[4](https://cameronrwolfe.substack.com/p/graph-based-prompting-and-reasoning?open=false#footnote-4-136366740) to unify duplicate entities, thus forming a graph representation of our input text.

**Encoding the inputs.** To ingest data from the different input modalities (i.e., text, image, and graph), we use separate encoders for each. For the image and text data, we can just use a transformer encoder! In \[1\], images are encoded using a [vision transformer](https://cameronrwolfe.substack.com/p/vision-transformers-from-idea-to) \[4\], while text is encoded using the encoder of the [T5 model](https://cameronrwolfe.substack.com/p/t5-text-to-text-transformers-part) \[5\].

Notably, we should realize here that the GOTR framework is using a different model architecture compared to most [causal LLMs](https://twitter.com/cwolferesearch/status/1640446111348555776?s=20)[5](https://cameronrwolfe.substack.com/p/graph-based-prompting-and-reasoning?open=false#footnote-5-136366740). Rather than the typical decoder-only architecture used by causal language models, GOTR uses a prefix-based language modeling approach that ingests input with multiple encoder models, then passes the output of these encoders to a decoder to generate output. This is similar to the encoder-decoder transformer architecture, but there are multiple different types of encoders that are used! To handle the multiple encoders, we have a few learnable layers prior to the decoder that fuse their outputs into a single sequence that is then passed to the decoder. The full encoder-decoder setup used by GOTR is fine-tuned on the desired task.

[

![](Graph-Based%20Prompting%20and%20Reasoning%20with%20Language%20Models/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252F7c69c15a-9512-4400-9a7a-b835750616cf_2108x820.jpeg)

](https://substackcdn.com/image/fetch/$s_!6MVB!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F7c69c15a-9512-4400-9a7a-b835750616cf_2108x820.png)

Formulation and depiction of the GAT-based encoder architecture used to encode the thought graph within GOTR (from \[1\])

**Using the GAT.** The encoder used for the thought graph is based upon a GAT architecture. As mentioned previously, the GAT is a style of GCN architecture. Instead of aggregating features of neighboring nodes via a simple sum or average operation, GATs use an attention mechanism to aggregate information between neighboring nodes. The exact GAT architecture used in \[1\] is depicted above.

[GAT Model](https://docs.dgl.ai/en/0.8.x/tutorials/models/1_gnn/9_gat.html)

**Fusing representations.** Once we have encoded the data from our text, image, and thought graph inputs, we need to fuse these features together prior to passing them to the decoder to generate an output. To do this, we can first use a simple [cross-attention mechanism](https://vaclavkosar.com/ml/cross-attention-in-transformer-architecture)! This initial feature fusion operation is shown below, where textual features are fused with both image and thought graph features using cross attention. Here, we should recall that image features are optional and can be completely excluded from the GOTR framework.

[

![](Graph-Based%20Prompting%20and%20Reasoning%20with%20Language%20Models/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252Ffefca346-bc7e-4082-9407-012ad612371d_1272x150.png)

](https://substackcdn.com/image/fetch/$s_!0Uqg!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Ffefca346-bc7e-4082-9407-012ad612371d_1272x150.png)

(from \[1\])

After cross-attention, we still have image features, text features, and (potentially) image features. We still need to combine these features together into a single feature representation that can be passed to the decoder. This is done via a gated fusion layer. Although this might sound complicated, all it means is that we _i)_ take our input features, _ii)_ multiply them by some learnable weight matrices, and _iii)_ produce “masks” (i.e., matrices with values between zero and one at each entry) that tell use which portions of each feature to keep or get rid of as we combine all image, text, and graph features together; see below.

[

![](Graph-Based%20Prompting%20and%20Reasoning%20with%20Language%20Models/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252F86d993f1-7c49-4a86-b159-8f491748a7f1_1636x362.jpeg)

](https://substackcdn.com/image/fetch/$s_!1i_m!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F86d993f1-7c49-4a86-b159-8f491748a7f1_1636x362.png)

Learnable fusion layer for GOTR (from \[1\])

**Experimental results.** The GOTR framework is evaluated on two tasks: text-only [GSM8K](https://huggingface.co/datasets/gsm8k) (i.e., grade-school math problems) and multi-modal [ScienceQA](https://scienceqa.github.io/) (i.e., multiple choice science questions). GOTR uses a pre-trained T5 model \[5\] as its backbone and [DETR](https://github.com/facebookresearch/detr) \[6\] as its image encoder. Notably, GOTR is fine-tuned on each of the experimental benchmarks. As such, all baselines that are used for comparison—_including few-shot learning and CoT prompting with multiple LLMs, as well as a few task-specific methods_—undergo similar fine-tuning prior to evaluation.

[

![](Graph-Based%20Prompting%20and%20Reasoning%20with%20Language%20Models/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252F3ad21d3d-6ff8-458c-8674-7e0a390a2572_1612x584.jpeg)

](https://substackcdn.com/image/fetch/$s_!uuED!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F3ad21d3d-6ff8-458c-8674-7e0a390a2572_1612x584.png)

(from \[1\])

When we solely look at the quality of problem-solving rationales generated by GOTR in comparison to other frameworks, we immediately learn that GOTR generates higher-quality rationales in terms of [ROUGE](https://eugeneyan.com/writing/llm-patterns/#more-about-evals) score; see above. Most notably, we see a slight increase in quality compared to multi-modal CoT and [UnifiedQA](https://arxiv.org/abs/2005.00700) approaches, which seem to indicate that incorporating a thought graph into the problem-solving process can be helpful.

[

![](Graph-Based%20Prompting%20and%20Reasoning%20with%20Language%20Models/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252F8c16f38a-f6f0-42fa-baa7-d274dad8b502_1372x516.png)

](https://substackcdn.com/image/fetch/$s_!6nRF!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F8c16f38a-f6f0-42fa-baa7-d274dad8b502_1372x516.png)

(from \[1\])

When we examine the accuracy of GOTR’s final solutions, we see that the framework in \[1\] outperforms a variety of other alternatives on the GSM8K dataset; see above. Notably, [GPT-4](https://openai.com/research/gpt-4) far outperforms all other techniques. However, we should keep in mind that such a comparison is likely unfair given that GPT-4 is [rumored](https://www.semianalysis.com/p/gpt-4-architecture-infrastructure) to be an ensemble (or [mixture](https://arxiv.org/abs/1701.06538)) of several large models. Plus, GOTR makes significant progress towards closing the gap in performance with GPT-4 and outperforms strong baselines like [GPT-3](https://cameronrwolfe.substack.com/i/88082618/language-models-are-few-shot-learners) \[7\] and [GPT-3.5](https://platform.openai.com/docs/models/gpt-3-5).

[

![](Graph-Based%20Prompting%20and%20Reasoning%20with%20Language%20Models/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252F2864d797-1fa9-4a3e-942b-6228cb60c280_1626x1064.jpeg)

](https://substackcdn.com/image/fetch/$s_!dYMN!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F2864d797-1fa9-4a3e-942b-6228cb60c280_1626x1064.png)

(from \[1\])

On the ScienceQA dataset, GOTR achieves state-of-the-art performance among all techniques, even outperforming GPT-4 with CoT prompting in several cases. Such results indicate that GOTR is a useful framework for integrating multiple modalities of data into the problem-solving process. Although we see a slight improvement in performance on the GSM8K dataset, GOTR’s value is most evident when used for ScienceQA given its ability to leverage all input data modalities—_text, image, and graph_—when solving a reasoning task.

#### **Graph of Thoughts: Solving Elaborate Problems with Large Language Models \[2\]**

> _“This work brings the LLM reasoning closer to human thinking or brain mechanisms such as recurrence, both of which form complex networks.”_ - from \[2\]

Although GOTR is an interesting framework, one may argue that it is not truly a prompting technique, as it must be fine-tuned or trained to solve any reasoning problem. In \[2\], authors again explore a graph-inspired framework for reasoning with LLMs. However, a pure prompting approach—similar to [CoT](https://cameronrwolfe.substack.com/p/chain-of-thought-prompting-for-llms) \[8\] or [ToT prompting](https://cameronrwolfe.substack.com/p/tree-of-thoughts-prompting) \[9\]—is taken that _i)_ uses a casual pre-trained LLM and _ii)_ does not require any fine-tuning. The method, called Graph of Thought (GoT) prompting, models each thought generated by an LLM as a node within a graph, then uses vertices that connect these nodes to represent dependencies; see below.

[

![](Graph-Based%20Prompting%20and%20Reasoning%20with%20Language%20Models/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252F93a6e06d-3c31-40b4-b96d-d7957898cfaa_822x666.png)

](https://substackcdn.com/image/fetch/$s_!x1-P!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F93a6e06d-3c31-40b4-b96d-d7957898cfaa_822x666.png)

(from \[2\])

As previously mentioned, humans may not follow a strict chain of thought when solving a problem. Instead, they are likely to:

1.  Try multiple chains of thought.
    
2.  Combine insights from multiple chains of thought together.
    

The first case outlined above can be handled by ToT prompting, but combining different chains of thought is not amenable to a tree-structured thought pattern. For this, _we need a graph structure in which multiple paths of reasoning can be merged together_. Furthermore, such a structure enables patterns like recurrence to be captured, which may be valuable for solving a variety of different problems.

The GoT approach in \[1\] enables us to model individual thoughts from an LLM and arbitrarily combine these thoughts—_e.g., by distilling an entire network of thoughts, enhancing thoughts with feedback loops, and more_—to form an accurate output. Plus, the framework is extensible to other models and thought patterns, making plug-and-play with different LLMs and prompting techniques easy.

[

![](Graph-Based%20Prompting%20and%20Reasoning%20with%20Language%20Models/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252Fc113cb01-ac85-4e0e-a418-a21c5dd9a4e0_1728x718.jpeg)

](https://substackcdn.com/image/fetch/$s_!-9Bs!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fc113cb01-ac85-4e0e-a418-a21c5dd9a4e0_1728x718.png)

(from \[2\])

**GoT framework.** The approach employed by GoT is shown in the figure above. The LLM’s reasoning process is represented as a (directed) graph. Each node in this graph corresponds to an individual thought generated by an LLM, and edges represent relationships between thoughts. Namely, an edge from thought `a` to `b`—or directed edge (`a`, `b`) in the graph—simply tells us that thought `b` was generated using thought `a` as input. Similarly to ToT prompting, the exact definition of a thought depends on the problem being solved. Going further, each node represents a (potentially intermediate) solution to a problem, but we can have different types of nodes within the graph that represent different aspects of the reasoning process (e.g., planning versus execution).

[

![](Graph-Based%20Prompting%20and%20Reasoning%20with%20Language%20Models/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252Fe9619ac8-6a8d-4394-b9bd-d9a530667aa5_824x656.png)

](https://substackcdn.com/image/fetch/$s_!7jso!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fe9619ac8-6a8d-4394-b9bd-d9a530667aa5_824x656.png)

(from \[2\])

**Thought transformations.** Given that we use a graph to represent the reasoning process executed by the LLM, any modification to this graph represents a modification to the underlying reasoning process. Authors in \[2\] refer to these modifications as _thought transformations_, which are concretely defined as adding new vertices or edges to the graph. As shown in the figure above, various kinds of thought transformations exist (e.g., merging or splitting numbers of an array, summarizing a set of articles, generating multiple summaries of a single article, and so on). We consider three primary types of thought transformations in \[2\]:

-   _Aggregation_: aggregate arbitrary thoughts into a new thought.
    
-   _Refinement_: refining the content in a thought via a self-connection.
    
-   _Generation_: generate multiple new thoughts based on a single thought.
    

Each of these transformations can modify and advance an LLM’s reasoning process arbitrarily. For example, aggregation can merge the results of multiple different chains of thought together, while refinement can recursively update a thought until arriving at a final answer. Such functionality strictly extends CoT and ToT prompting—_it can do everything these techniques can do and more_!

> _“When working on a novel idea, a human would not only follow a chain of thoughts (as in CoT) or try different separate ones (as in ToT), but would actually form a more complex network of thoughts.”_ - from \[2\]

**Scoring and ranking.** Finally, GoT prompting uses evaluator functions to assign scores to certain thoughts, as well as a ranking function to select the most relevant thoughts. Notably, both ranking and scoring consider the entire graph. This is necessary because, for scoring, the quality of a thought might depend on other thoughts. Ranking typically just returns thoughts with the highest scores.

[

![](Graph-Based%20Prompting%20and%20Reasoning%20with%20Language%20Models/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252Fb5134c71-394b-4157-a9d4-4ad992a6a8ff_1102x1448.png)

](https://substackcdn.com/image/fetch/$s_!Zghz!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fb5134c71-394b-4157-a9d4-4ad992a6a8ff_1102x1448.png)

(from \[2\])

**Actual implementation.** So far, the discussion of GoT prompting has been relatively high-level, but _how do we actually implement this?_ In \[2\], authors do this via a series of different LLM-powered modules. The modules, which are detailed in depth in the figure above, are as follows:

-   _Prompter_: prepares messages or prompts for the LLM. The prompt is expected to contain an encoding of the graph structure.
    
-   _Parser_: extracts relevant information from LLM outputs, thus forming the state stored within each thought.
    
-   _Scorer_: verifies that thought states satisfy correctness conditions and assigns them a score (derived either from an LLM or a human annotator).
    
-   _Controller_: coordinates the reasoning process and decides how to progress.
    

Notably, the controller selects the thought transformations that should be applied to the underlying graph, communicates this information to the prompter, and decides whether the reasoning process has finished or should continue forward based on the output of the scorer on generated thought states. Throughout this process, the controller maintains two pieces of information:

-   _Graph of Operations_: a user-defined, static structure that is created prior to the reasoning process and captures the execution plan for thought operations.
    
-   _Graph Reasoning State_: a dynamic structure that tracks the state of the LLM reasoning process, including all thoughts and their states.
    

[

![](Graph-Based%20Prompting%20and%20Reasoning%20with%20Language%20Models/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252Fa95ca135-cf15-4e66-a1df-15fa49e865c8_532x1374.png)

](https://substackcdn.com/image/fetch/$s_!0WRn!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fa95ca135-cf15-4e66-a1df-15fa49e865c8_532x1374.png)

(from \[2\])

**Use cases.** Several applications of GoT prompting are explored in \[2\]. The first use case is sorting a list of digits (with duplicates) using a merge-based approach[6](https://cameronrwolfe.substack.com/p/graph-based-prompting-and-reasoning?open=false#footnote-6-136366740). Here, a thought is defined as a sequence of sorted numbers and thoughts are scored based on the number of errors in the sorting. The full GoT framework for sorting is depicted above. Beyond sorting, authors consider computing the intersection of two sets using GoT prompting, which is also implemented using a merge-based approach. The score of each thought is computed as the number of missing elements from the set intersection. Finally, a few practical use cases, such as keyword counting and document merging (i.e., generating a new output document based on several similar input examples), are considered.

[

![](Graph-Based%20Prompting%20and%20Reasoning%20with%20Language%20Models/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252F0b1c5787-c840-45b5-b842-e607d16632df_982x420.png)

](https://substackcdn.com/image/fetch/$s_!Ast5!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F0b1c5787-c840-45b5-b842-e607d16632df_982x420.png)

(from \[2\])

**Is GoT effective?** To begin their evaluations, authors theoretically analyze two properties of all prompting approaches considered in \[2\]:

-   _Latency_: How many thoughts does it take to reach a solution?
    
-   _Volume_: How many preceding thoughts can impact the current thought?
    

Interestingly, simple analysis can be used to show that GoT prompting has _i)_ less latency and _ii)_ greater volume compared to prior techniques; see above. When evaluated on sorting tasks, we see that GoT prompting consistently produces fewer errors compared to techniques like [CoT](https://cameronrwolfe.substack.com/p/chain-of-thought-prompting-for-llms) \[8\], [CoT with self-consistency](https://cameronrwolfe.substack.com/i/116166267/variants-of-cot-prompting) \[10\], or [ToT prompting](https://cameronrwolfe.substack.com/p/tree-of-thoughts-prompting) \[9\]. These results are outlined in the figure below.

[

![](Graph-Based%20Prompting%20and%20Reasoning%20with%20Language%20Models/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252Fbce3db99-ae73-46d5-9e78-5a4aa5c84bb3_2044x852.png)

](https://substackcdn.com/image/fetch/$s_!pIe1!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fbce3db99-ae73-46d5-9e78-5a4aa5c84bb3_2044x852.png)

(from \[2\])

One downside of GoT prompting that we see above is that the total cost of deriving a solution is higher than more straightforward approaches like basic [few-shot prompting](https://cameronrwolfe.substack.com/i/117151147/few-shot-learning) (IO) or CoT. On other tasks, findings are similar; see below.

[

![](Graph-Based%20Prompting%20and%20Reasoning%20with%20Language%20Models/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252Fcf6bfcd2-78a6-4d51-9a1c-3f87db8f3cf9_1514x1372.jpeg)

](https://substackcdn.com/image/fetch/$s_!ODWe!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fcf6bfcd2-78a6-4d51-9a1c-3f87db8f3cf9_1514x1372.png)

(from \[2\])

However, one key takeaway to notice here is that the difference in performance between GoT and other [advanced prompting techniques](https://cameronrwolfe.substack.com/p/advanced-prompt-engineering) seems to be less pronounced on real-world tasks. For example, GoT prompting provides a less noticeable improvement on the document merging task. Similarly, GoT provides a benefit in terms of performance on the keyword counting task, but baseline techniques—_especially ToT prompting_—are quite competitive.

**When does GoT work well?** Within \[2\], we see that GoT works quite well for certain tasks, but provides less of a benefit on others. When considering whether to use GoT in practice, there are a few questions we should ask:

-   Can the problem we are trying to solve be easily broken in to smaller, solvable sub-problems and merged for a final solution? For these kinds of (merge-based) problems, GoT prompting works incredibly well.
    
-   Is the increased cost of GoT prompting going to be a problem? Can we get a reasonable solution with a cheaper technique (e.g., CoT prompting)?
    

The answers to these questions will determine whether it makes sense to use GoT prompting. We see in \[2\] that this method works well, but it also _i)_ is more costly and _ii)_ only has a noticeable impact on performance for certain types of problems.

## Takeaways

> _“Graph-enabled transformations bring a promise of more powerful prompting when applied to LLM thoughts, but they are not naturally expressible with chain of thought or tree of thought prompting.”_ - from \[2\]

The techniques we have learned about in this overview are inspired by a simple idea—_allowing language models to structure their reasoning process as a graph_. Although this idea might seem natural, prior techniques have achieved massive success without it. Despite this success, we see in this overview that moving away from a linear reasoning process towards a more flexible graph-based structure is beneficial on certain tasks. Interestingly, multiple different approaches for “graph of thought” prompting have been explored, including both GOTR—_a two-stage reasoning framework that uses an encoder-decoder structure with fine-tuning_—and GoT \[2\]—_a more traditional prompting approach that leverages a system of language foundation models with prompts_. For both of these techniques, we see that a graph structure can benefit the reasoning process. However, the resulting reasoning process can be more complex and costly, revealing that a GoT-style approach may only be necessary for problems that cannot be solved via standard CoT.

#### New to the newsletter?

Hi! I’m [Cameron R. Wolfe](https://cameronrwolfe.me/), deep learning Ph.D. and Director of AI at [Rebuy](https://www.rebuyengine.com/). This is the Deep (Learning) Focus newsletter, where I help readers understand AI research via overviews of relevant topics from the ground up. If you like the newsletter, please subscribe, share it, or follow me on [Medium](https://medium.com/@wolfecameron), [X](https://twitter.com/cwolferesearch), and [LinkedIn](https://www.linkedin.com/in/cameron-r-wolfe-ph-d-04744a238/)!

#### Bibliography

\[1\] Yao, Yao, Zuchao Li, and Hai Zhao. "Beyond Chain-of-Thought, Effective Graph-of-Thought Reasoning in Large Language Models." _arXiv preprint arXiv:2305.16582_ (2023).

\[2\] Besta, Maciej, et al. "Graph of Thoughts: Solving Elaborate Problems with Large Language Models." _arXiv preprint arXiv:2308.09687_ (2023).

\[3\] Zhang, Zhuosheng, et al. "Multimodal chain-of-thought reasoning in language models." _arXiv preprint arXiv:2302.00923_ (2023).

\[4\] Dosovitskiy, Alexey, et al. "An image is worth 16x16 words: Transformers for image recognition at scale." _arXiv preprint arXiv:2010.11929_ (2020).

\[5\] Raffel, Colin, et al. "Exploring the limits of transfer learning with a unified text-to-text transformer." _The Journal of Machine Learning Research_ 21.1 (2020): 5485-5551.

\[6\] Carion, Nicolas, et al. "End-to-end object detection with transformers." _European conference on computer vision_. Cham: Springer International Publishing, 2020.

\[7\] Brown, Tom, et al. "Language models are few-shot learners." _Advances in neural information processing systems_ 33 (2020): 1877-1901.

\[8\] Wei, Jason, et al. "Chain-of-thought prompting elicits reasoning in large language models." _Advances in Neural Information Processing Systems_ 35 (2022): 24824-24837.

\[9\] Yao, Shunyu, et al. "Tree of thoughts: Deliberate problem solving with large language models." _arXiv preprint arXiv:2305.10601_ (2023).

\[10\] Wang, Xuezhi, et al. "Self-consistency improves chain of thought reasoning in language models." _arXiv preprint arXiv:2203.11171_ (2022).

\[11\] Vaswani, Ashish, et al. "Attention is all you need." _Advances in neural information processing systems_ 30 (2017).

\[12\] Devlin, Jacob, et al. "Bert: Pre-training of deep bidirectional transformers for language understanding." _arXiv preprint arXiv:1810.04805_ (2018).

\[13\] Kipf, Thomas N., and Max Welling. "Semi-supervised classification with graph convolutional networks." _arXiv preprint arXiv:1609.02907_ (2016).

\[14\] Veličković, Petar, et al. "Graph attention networks." _arXiv preprint arXiv:1710.10903_ (2017).

[1](https://cameronrwolfe.substack.com/p/graph-based-prompting-and-reasoning?open=false#footnote-anchor-1-136366740)

This stands for sequence-to-sequence and refers to tasks that take a sequence as input and produce another sequence as output. For example, language translation tasks take a sequence of tokens in one language and produce the corresponding/translated sequence of tokens in another language as output.

[2](https://cameronrwolfe.substack.com/p/graph-based-prompting-and-reasoning?open=false#footnote-anchor-2-136366740)

These tasks take a textual prefix as input, then generate a completion. Encoder-decoder models work well for these tasks because the bidirectional self-attention used in the encoder allows a more comprehensive representation of the prefix to be formed before generating output, compared to causal language models that use solely masked self-attention to ingest the prefix.

[3](https://cameronrwolfe.substack.com/p/graph-based-prompting-and-reasoning?open=false#footnote-anchor-3-136366740)

Notable, the two-stage framework adopted in \[1\] is inspired by the technique used by multi-modal CoT prompting \[3\].

[4](https://cameronrwolfe.substack.com/p/graph-based-prompting-and-reasoning?open=false#footnote-anchor-4-136366740)

Put simply, coreference resolution refers to the problem of finding all noun phrases that refer to the same real-world entity. In \[1\], we need this to ensure that all nodes in our thought graph are unique! Read more about this idea [here](https://www.cs.cmu.edu/~yimengz/papers/Coreference_survey.pdf).

[5](https://cameronrwolfe.substack.com/p/graph-based-prompting-and-reasoning?open=false#footnote-anchor-5-136366740)

Here, we use the term “causal LLM” to refer to large language models that use a decoder-only transformer architecture and are trained using a next token prediction (or language modeling) objective.

[6](https://cameronrwolfe.substack.com/p/graph-based-prompting-and-reasoning?open=false#footnote-anchor-6-136366740)

This means that our approach will divide an array of digits into sub-arrays, sort these sub-arrays, then combine them back together.