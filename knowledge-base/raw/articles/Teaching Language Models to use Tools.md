# Making LLMs more Capable

[

![](Teaching%20Language%20Models%20to%20use%20Tools/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252F7efe8c63-4487-4842-953f-d5a740a82b73_1826x1274.jpeg)

](https://substackcdn.com/image/fetch/$s_!f8yP!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F7efe8c63-4487-4842-953f-d5a740a82b73_1826x1274.png)

(from \[1\] and ChatGPT Plus)

As we learn more about them, large language models (LLMs) become increasingly interesting. These models can solve a variety of complex tasks accurately. At the same time, however, they struggle with certain functionality that we, as humans, consider basic! For example, LLMs commonly make arithmetic mistakes, lack access to current information, and even struggle to comprehend the progression of time. Given these limitations, we might wonder what can be done to make LLMs more capable. _Are LLMs doomed to suffer these limitations forever?_

Many advancements in the human race have been catalyzed by access to new and innovative tools (e.g., the [printing press](https://www.history.com/news/printing-press-renaissance) or [computer](https://www.youtube.com/watch?v=L40B08nWoMk)). _Might the same finding apply to LLMs?_ Within this overview, we will study a recent direction of research that aims to teach LLMs how to use external tools, which are made available via simple, text-to-text APIs. Using these tools, LLMs can delegate tasks like performing arithmetic or looking up current information to a specialized tool. Then, information returned by this tool can be used as context by the LLM when generating output, leading to more accurate and grounded responses.

## Making LLMs more Capable

Giving an LLM access to an external tool is a reliable way to solve some of the limitations that these models face. However, LLMs will not know how to use tools naturally, which raises the question: _How do we teach our model to leverage external tools?_ In this section, we will explore some of the options we have and enumerate various tools that are useful for building LLM applications.

### Different Types of Learning

[

![](Teaching%20Language%20Models%20to%20use%20Tools/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252F4c51db77-8d97-45a9-bd2c-d71e930ff0b8_2292x1234.jpeg)

](https://substackcdn.com/image/fetch/$s_!wEtP!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F4c51db77-8d97-45a9-bd2c-d71e930ff0b8_2292x1234.png)

Different forms of learning with LLMs

Teaching an LLM to leverage tools is no different than learning how to solve any other task with an LLM. Since these models learn in a couple of different ways, we will go over the main forms of learning with LLMs here. Beyond this post, there are also [detailed explanations](https://twitter.com/cwolferesearch/status/1635693551584522256?s=20) available online.

**pre-training.** The first and most basic form of learning for LLMs is pre-training. During pre-training, the model is trained over a large corpus of unlabeled textual data using a [language modeling objective](https://cameronrwolfe.substack.com/i/85568430/language-modeling). The pre-training process begins from a random initialization and is quite computationally expensive. Typically, pre-training is performed only once due to its [computational expense](https://www.mosaicml.com/blog/gpt-3-quality-for-500k)—we do not want to repeat the pre-training process very often! Notably, the computational expense of pre-training provides an explanation for the presence of a knowledge cutoff in LLMs like ChatGPT. These models learn [all of their knowledge](https://twitter.com/cwolferesearch/status/1660744247123890179?s=20) during pre-training, so the knowledge cutoff is just associated with data that is present during the most recent pre-training run.

[

![](Teaching%20Language%20Models%20to%20use%20Tools/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252F0a47baaf-62c9-4768-b333-22365389cb48_1762x914.jpeg)

](https://substackcdn.com/image/fetch/$s_!Ab2r!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F0a47baaf-62c9-4768-b333-22365389cb48_1762x914.png)

Fine-tuning methods for LLMs (from \[11\])

**fine-tuning.** After pre-training, LLMs can accurately perform next-token prediction, but this doesn’t always mean that they are actually useful. If we play with a demo of [GPT-2](https://cameronrwolfe.substack.com/i/85568430/language-models-are-unsupervised-multitask-learners-gpt) for 2 minutes, for example, we immediately see that predicting the next token accurately can result in some pretty boring and unhelpful outputs! As such, we typically fine-tune LLMs after pre-training, either via supervised fine-tuning (SFT) or reinforcement learning from human feedback (RLHF); see the image above and [here](https://cameronrwolfe.substack.com/i/93578656/refining-llm-behavior) for details. Although the details of these techniques are beyond the scope of this post, the basic idea is to:

1.  Curate more training data (e.g., in-domain data for the task we want to solve, examples of correct dialogue, human feedback on the LLM’s output, etc.).
    
2.  Train the model’s parameters over this new data using either [reinforcement learning](https://openai.com/research/openai-baselines-ppo) or gradient descent with a (self-)supervised objective.
    

By doing this, we can accomplish quite a bit! For example, [fine-tuning an LLM using RLHF](https://cameronrwolfe.substack.com/i/93578656/training-language-models-to-follow-instructions-with-human-feedback) \[11\] has been shown to make LLMs more interesting, factual, and helpful. Going further, the recent LIMA publication from Meta showed that performing SFT over just 1,000 high-quality dialogue examples can produce a model that rivals the quality of GPT-4 \[12\]. Put simply, fine-tuning takes us from a generic LLM to something that is truly special and useful.

[

![](Teaching%20Language%20Models%20to%20use%20Tools/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252F7abadc37-6ed1-482f-8ea2-fbf8bfa60615_1924x962.png)

](https://substackcdn.com/image/fetch/$s_!YtSB!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F7abadc37-6ed1-482f-8ea2-fbf8bfa60615_1924x962.png)

(from \[7\])

**in-context learning.** The final form of learning that we should be aware of is in-context learning; see above. In-context learning is different from pre-training and fine-tuning in that it _does not actually modify the underlying model’s parameters_. Rather, we teach the LLM to solve a problem more effectively by modifying its prompt! In particular, we can rephrase the prompt by using particular prompting techniques or even insert data into the prompt to perform [few-shot learning](https://cameronrwolfe.substack.com/i/117151147/few-shot-learning). The difference between fine-tuning and in-context learning is shown below.

[

![](Teaching%20Language%20Models%20to%20use%20Tools/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252F123f7cf3-40de-41ad-9a1c-157821bd0b7c_1528x1348.jpeg)

](https://substackcdn.com/image/fetch/$s_!JpvJ!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F123f7cf3-40de-41ad-9a1c-157821bd0b7c_1528x1348.png)

(from \[7\])

In-context learning is incredibly powerful as it allows us to solve a variety of different tasks using a single model. Instead of fine-tuning the model and modifying its underlying parameters, we can insert useful data into the LLM’s prompt. The LLM can learn from this data and more accurately solve a task without the model itself being modified! Additionally, we can perform in-context learning with both pre-trained and fine-tuned models. To learn about prompting techniques that can be used with LLMs, check out the overviews below:

-   Practical Prompting \[[link](https://cameronrwolfe.substack.com/p/practical-prompt-engineering-part)\]
    
-   Advanced Prompting \[[link](https://cameronrwolfe.substack.com/p/advanced-prompt-engineering)\]
    
-   Chain of Thought Prompting \[[link](https://cameronrwolfe.substack.com/p/chain-of-thought-prompting-for-llms)\]
    
-   Prompt Ensembles \[[link](https://cameronrwolfe.substack.com/p/prompt-ensembles-make-llms-more-reliable)\]
    

### What tools are useful for LLMs?

Although the idea of connecting LLMs to external tools seems enticing, we might wonder: _what kinds of tools would be the most useful?_ To answer this question, we should look to common limitations of LLMs, such as:

-   Lack of access to up-to-date information \[2\]
    
-   Tendency to hallucinate (i.e., output incorrect information)
    
-   Difficulties with [evaluating mathematical expressions](https://cameronrwolfe.substack.com/i/121554239/program-of-thoughts-pot-prompting)
    
-   Incomplete understanding of [low-resource languages](https://cameronrwolfe.substack.com/p/many-languages-one-deep-learning)
    
-   Inability to understand the progression of time \[8\]
    

If we wanted to solve these issues, we have a few options. We could focus on fine-tuning and refining the model via [SFT or RLHF](https://cameronrwolfe.substack.com/i/93578656/refining-llm-behavior)—just fine-tune the model extensively to avoid the behavior listed above. In fact, extensive resources have been invested into refining models like [GPT-4](https://openai.com/research/gpt-4) through targeted human feedback, which has produced pretty [impressive results](https://cameronrwolfe.substack.com/i/121554239/background-information). Instead of solving these problems within the model itself, however, we could focus on fine-tuning the model to take an approach that is indirect, but oftentimes more reliable. In particular, we could teach the model how to use external tools to help with answering questions!

**how do tools help?** When struggling to solve a problem, it is often useful for an LLM to query an external tool that can provide more context. Notable examples of useful tools include (but are not limited to):

-   Calendar apps that can return the current date
    
-   Calculators that can evaluate mathematical expressions
    
-   [Vector databases](https://cameronrwolfe.substack.com/i/118401596/knowledge-augmentation) that store (potentially) relevant information that is too large to store directly in the prompt
    
-   Translation modules for converting data into different languages
    

Overall, tools are incredibly useful whenever providing extra information or context can help an LLM with solving a problem. Going beyond these simple tools, we could even connect LLMs to external code interpreters, giving them the ability to write and execute arbitrary programs. When combined with code-enabled LLMs (e.g., [Codex](https://cameronrwolfe.substack.com/p/specialized-llms-chatgpt-lamda-galactica) \[10\]), such an approach can actually be quite powerful!

[Program-Aided LLMs](https://cameronrwolfe.substack.com/p/program-aided-language-models)

### Tools are super popular!

Although this overview will primarily focus upon recent research that studies the integration of tools with LLMs, augmenting models like GPT-4 with external tools has been a topic of recent interest. For example, OpenAI recently released a plugins extension for their models, allowing these powerful LLMs to leverage a massive number of external tools; see below.

[

![](Teaching%20Language%20Models%20to%20use%20Tools/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252F3211fdac-97bc-4bcf-9f1e-32ce3758ad44_2108x1052.jpeg)

](https://substackcdn.com/image/fetch/$s_!jZJa!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F3211fdac-97bc-4bcf-9f1e-32ce3758ad44_2108x1052.png)

Popular apps on the ChatGPT Plus plugin store

As of the time of writing, nearly 130 different plugins are available for GPT-4, thus demonstrating the massive amount of interest in integrating various kinds of tools with powerful LLMs. Going beyond 3rd party plugins, OpenAI has recently released code interpreter and internet search tools for GPT-4. The internet search tools is incredibly useful for mitigating hallucinations within LLMs, as answers provided by the model can be contextualized with relevant, up-to-date information taken from the internet. Beyond making LLMs more factual and grounded, the code interpreter tool is capable of [ingesting massive code and data files](https://news.ycombinator.com/item?id=36047187) and performing accurate analysis over this data to yield valuable insights.

**TL;DR:** The main takeaway here is that tools are becoming a common feature for LLMs. Beyond OpenAI’s offerings, we are even seeing models like Bard being enhanced with [similar features](https://blog.google/technology/ai/google-bard-updates-io-2023/), while open-source libraries like LangChain can be used to easily build a variety of tool-like features for available LLMs.

[

![](Teaching%20Language%20Models%20to%20use%20Tools/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252F2823ed58-0330-49a9-aaf3-060525eae629_2124x342.jpeg)

](https://substackcdn.com/image/fetch/$s_!bxmR!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F2823ed58-0330-49a9-aaf3-060525eae629_2124x342.png)

### Now from our partners!

-   [Rebuy Engine](https://www.rebuyengine.com/) is the Commerce AI company. They use cutting edge deep learning techniques to make any online shopping experience more personalized and enjoyable.
    
-   [KUNGFU.AI](https://urldefense.com/v3/__http://KUNGFU.AI__;!!BuQPrrmRaQ!i4L4Oc-1VDW1AHrfWwPg9wcLgB7A4UgD2LsIn9-L7LvnJJbz2Sh6c3ee4MnN_sn04GFwufC-Elb0tnEnztEylFoQBdkEJgf7$) partners with clients to help them compete and lead in the age of AI. Their team of AI-native experts deliver strategy, engineering, and operations services to achieve AI-centric transformation.
    
-   [MosaicML](https://www.mosaicml.com/) enables you to train and deploy large AI models on your data and in your secure environment. Try out their tools and platform [here](http://mosaicml.me/cameronrwolfe) or check out their [open-source, commercially-usable LLMs](https://www.mosaicml.com/blog/mpt-7b).
    

[

![](Teaching%20Language%20Models%20to%20use%20Tools/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252Fdb430281-e4d5-4b7e-b6ea-5b76ecba8992_758x1054.png)

](https://substackcdn.com/image/fetch/$s_!9drz!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fdb430281-e4d5-4b7e-b6ea-5b76ecba8992_758x1054.png)

(from \[1\])

In \[1\], authors explore an approach, called the Toolformer, that _i)_ teaches an LLM how to leverage external tools and _ii)_ maintains the generic nature of the LLM in the process. These tools are made available to the LLM via a set of simple text-to-text APIs (i.e., meaning that the model provides text as input and the API returns textual output). Interestingly, we see in \[1\] that the LLM can learn to leverage these tools in a completely end-to-end manner. The model decides what APIs to call, which arguments to pass to these APIs, and how to best use the information that is returned without any hard-coded control flows.

> _“Language models can learn to control a variety of tools, and to choose for themselves which tool to use when and how.”_ \- from \[1\]

To do this, we curate a dataset of training data that demonstrates the proper use of these tools. In \[1\], this dataset is created automatically using a self-supervised heuristic—meaning that no human intervention is required—that requires only a few examples of usage for each tool. Then, we fine-tune the LLM over this data, allowing it to learn the correct usage of each tool. The result is a high-performing LLM that can delegate simple, but difficult subtasks (e.g., language translation, arithmetic, accessing current information, etc.) to specialized, external tools that return relevant and accurate data for the LLM to use in generating an output.

[

![](Teaching%20Language%20Models%20to%20use%20Tools/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252Fb9396abd-34ec-4a58-bdca-4e2548476f03_2144x700.jpeg)

](https://substackcdn.com/image/fetch/$s_!m59y!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fb9396abd-34ec-4a58-bdca-4e2548476f03_2144x700.png)

(from \[1\])

**what tools are used?** In \[1\], the Toolformer uses the following, fixed set of tools:

-   _Question Answering Tool:_ Based on Atlas \[13\], an LLM that is fine-tuned for answering simple, fact-based questions.
    
-   _Calculator:_ A basic calculator for numerical operations.
    
-   _Wikipedia Search Tool:_ A search engine that returns short, textual snippets from Wikipedia given a search term.
    
-   _Translator:_ A language translation system that can translate text from any language into English (but not the other way around!).
    
-   _Calendar:_ A tool that just returns the current date when queried.
    

Each of these tools are made available via a simple API with a text-to-text structure; see above. To use the tools, the LLM must learn to _i)_ identify scenarios that require a tool, _ii)_ specify which tool to use, _iii)_ provide relevant textual input to the tool’s API, and _iv)_ use text returned from the API to craft a response. Notably, the simple text-to-text structure of these APIs allows us to easily insert examples of tool usage directly into a textual sequence; see below.

[

![](Teaching%20Language%20Models%20to%20use%20Tools/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252Fb823eb83-0440-4e84-9cab-42aa049bd722_1368x366.jpeg)

](https://substackcdn.com/image/fetch/$s_!TxnT!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fb823eb83-0440-4e84-9cab-42aa049bd722_1368x366.png)

Calls to external APIs are formatted as text and placed inline with an existing textual sequence

**improvements over prior work.** Giving LLMs access to external tools is not a new idea. As a simple example, many researchers have attempted to make LLMs better at arithmetic—especially with large numbers—by giving them access to an external calculator (see Appendix B in \[4\]). However, the main question is: _how should we teach the LLM to use such a tool?_ Prior approaches were heavily dependent upon human annotated datasets. For example, LaMDA \[3\] uses an external search tool to reduce hallucinations; see below.

[

![](Teaching%20Language%20Models%20to%20use%20Tools/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252Fe1dcf49f-3885-45ef-a422-cd91bd648f26_1276x1288.jpeg)

](https://substackcdn.com/image/fetch/$s_!Jk09!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fe1dcf49f-3885-45ef-a422-cd91bd648f26_1276x1288.png)

(from \[3\])

However, we see in \[3\] that teaching LaMDA to leverage external tools—in this case an external [information retrieval system](https://cameronrwolfe.substack.com/i/118401596/knowledge-augmentation)—requires a massive amount of human annotated data. More specifically, authors in \[3\] have a large number of crowd workers hand-write dialogues in which they leverage the same search tool as the LLM, thus providing examples of how the LLM should behave and respond. Related publications tend to rely upon a similar, human-centric approach \[2\]. Creating such a dataset is difficult, expensive, and time consuming, which leads authors in \[1\] to develop a more efficient solution.

**learning to use tools automatically.** In \[1\], we see that a dataset for teaching an LLM how to leverage external tools—we will call this a “tool-following dataset” for simplicity—can be automatically crafted via a prompting approach that leverages existing, pre-trained LLMs. We start with an initial (normal) dataset, such as the textual corpus used for pre-training. Then, we prompt a pre-trained LLM to augment this data with external API calls. Here, we rely upon the in-context learning abilities of generic pre-trained LLMs to curate a set of API calls that demonstrate how to correctly use available tools. An example prompt that generates requests to a question answering tool’s API is shown below.

[

![](Teaching%20Language%20Models%20to%20use%20Tools/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252Fe24f1112-591c-4cc5-845e-2b01391194b1_752x1076.png)

](https://substackcdn.com/image/fetch/$s_!Hd4y!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fe24f1112-591c-4cc5-845e-2b01391194b1_752x1076.png)

(from \[1\])

After we have augmented our dataset with example usages of each tool, we need to perform a filtering step. This step is necessary because we only want to use an external tool if it is actually helpful to the LLM! We shouldn’t just always rely upon external tools even when they aren’t needed—using a tool usually has a latency (or even monetary) cost. To capture this idea, we can just do the following:

1.  Measure the LLM’s performance (i.e., [cross entropy loss](https://pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html) over tokens that come after the API call) with the tool.
    
2.  Measure the LLM’s performance without the tool.
    
3.  Discard examples where using the tool does not improve the LLM’s performance beyond a certain threshold.
    

Here, we are assuming access to a dataset that demonstrates the correct output that an LLM should produce. By following this approach, we automatically construct a dataset that contains examples of when and how tools can be leveraged to tangibly improve the LLM’s output. In practice, the actual procedure is a bit more complex. Namely, to measure the LLM’s performance without the tool, we observe performance in two separate cases—one without the tool at all, and one that performs an API call but provides no response. Such an approach ensures that both the tool and its data are useful to the LLM.

> _“An API call is helpful to \[the language model\] if providing both the input and the output of this call makes it easier to predict future tokens”_ - from \[1\]

Additionally, instead of inserting the API call inline with the textual sequence, we append it as a prefix, which avoids spikes in the LLM’s loss. Remember, API calls like this are not present in the original pre-training corpus for the LLM, which means that inserting the API call directly into the textual sequence could skew results used for filtering. _The model is not expecting to see an API call like this within the data!_ Furthermore, when measuring performance, we assign a higher weight to tokens that are spatially close to the API call, ensuring that the API call is made near where it is needed and not at random times when generating output.

[

![](Teaching%20Language%20Models%20to%20use%20Tools/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252F37240b64-3d51-4e81-b581-c94d03d4132f_1232x414.png)

](https://substackcdn.com/image/fetch/$s_!IrLU!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F37240b64-3d51-4e81-b581-c94d03d4132f_1232x414.png)

(from \[1\])

The full process for constructing the tool-following dataset used in \[1\] is shown above. Unlike prior work, this process requires no human labor. Rather, we leverage the in-context learning abilities of LLMs and a few clever heuristics to construct the dataset automatically. Although this process is not perfect (i.e., some useless API calls may avoid filtering), it works quite well in practice!

**learning to use tools.** Once we have constructed a dataset, teaching an LLM how to leverage external tools is easy—we just fine-tune the model over this dataset using a [standard language modeling objective](https://cameronrwolfe.substack.com/i/85568430/language-modeling). In \[1\], the tool-following dataset is derived from a pre-training corpus. As such, the fine-tuned LLM is still a general-purpose model, despite having the ability to leverage external tools. Moreover, because the filtering process in \[1\] removes API calls that do not benefit performance, the LLM implicitly learns when and how each tool should be used to improve its own output. Pretty cool results for such a simple approach!

## Do tools make a difference?

The model analyzed in \[1\] is based upon [GPT-J](https://huggingface.co/EleutherAI/gpt-j-6b) \[5\], a 6 billion parameter language model, and [CCNet](https://github.com/facebookresearch/cc_net) is adopted as the training dataset. Toolformer is compared to several baselines, including a Toolformer model with API calls disabled, the original GPT-J model, a version of GPT-J that is fine-tuned on CCNet, as well as a few other LLMs like [OPT](https://cameronrwolfe.substack.com/p/understanding-the-open-pre-trained-transformers-opt-library-193a29c14a15) \[6\] and [GPT-3](https://cameronrwolfe.substack.com/i/88082618/language-models-are-few-shot-learners) \[7\]. Unlike prior work that studies few-shot learning, models are evaluated using a [zero-shot approach](https://cameronrwolfe.substack.com/i/117151147/zero-shot-learning), which simply describes the task to the model without providing any exemplars, and a [greedy decoding](https://twitter.com/cwolferesearch/status/1659608476455256078?s=20) strategy. With Toolformer, a tool is leveraged whenever `<API>` (i.e., the starting token for an API call) appears as one of the model’s `k` most likely tokens.

Toolformer is evaluated across several different domains. On fact-based datasets, we see that the question answering tool is heavily leveraged, leading to a large increase in accuracy over baseline models. Similarly, the calculator tool is found to be quite useful on mathematical reasoning datasets; see below.

[

![](Teaching%20Language%20Models%20to%20use%20Tools/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252F25d8534e-8d0c-469c-80c7-ceebbe066038_2020x676.jpeg)

](https://substackcdn.com/image/fetch/$s_!q39G!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F25d8534e-8d0c-469c-80c7-ceebbe066038_2020x676.png)

(from \[1\])

On (multilingual) question answering benchmarks, the model’s performance is not quite as impressive (i.e., Toolformer falls short of GPT-3 or GPT-J performance in some cases). However, certain tools, such as the calendar tool, are found to be incredibly useful for improving LLM performance on tasks like temporal reasoning. Interestingly, the authors also perform some analysis that modifies the probability of API calls within the LLM’s decoding strategy. From this analysis, we learn that _leveraging external tools more frequently is not always a good thing_—performance degrades if tools are used too frequently; see below.

[

![](Teaching%20Language%20Models%20to%20use%20Tools/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252F43dbbce7-98f6-41e0-b34c-835c0fa5e729_1384x896.jpeg)

](https://substackcdn.com/image/fetch/$s_!ZWPX!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F43dbbce7-98f6-41e0-b34c-835c0fa5e729_1384x896.png)

(from \[1\])

Such a finding highlights the importance of the filtering strategy used in \[1\]. Not only does tool usage come with a cost, but it may degrade performance. The LLM must learn to understand the scenarios in which calling a tool is most important. The approach taken in \[1\] explicitly biases the LLM towards only leveraging external tools when it provides a significant boost in the model’s performance.

[

![](Teaching%20Language%20Models%20to%20use%20Tools/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252Ff33b5c92-773a-4f9a-aaf7-05965d372eb2_1048x548.png)

](https://substackcdn.com/image/fetch/$s_!egWq!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Ff33b5c92-773a-4f9a-aaf7-05965d372eb2_1048x548.png)

(from \[1\])

**remaining generic.** Beyond the downstream evaluations described above, authors in \[1\] evaluate Toolformer on a hold-out portion of the pre-training dataset after fine-tuning on the tool-following dataset, finding that the model achieves comparable [perplexity](https://towardsdatascience.com/perplexity-intuition-and-derivation-105dd481c8f3) both before and after fine-tuning; see above. In other words, _Toolformer does not lose any of its capabilities as a generic language model when it learns to leverage external tools_, meaning that—unlike prior work that approaches tool-following in a task-specific manner \[8\]—this model is still a [foundation model](https://crfm.stanford.edu/) that can solve a variety of different tasks.

### Using Tools is Getting Easier

Although the approach proposed in \[1\] is groundbreaking and incredibly informative, it still requires an extensive fine-tuning process. Compared to most recent applications of LLMs, this is quite a hassle! _Is it possible that we could leverage a prompting-only approach to teach an LLM to leverage external tools?_ Recent developments surrounding GPT-4 suggest that this problem might be solved by improving the [instruction following capabilities](https://cameronrwolfe.substack.com/i/117151147/instruction-prompting) of LLMs.

[

![](Teaching%20Language%20Models%20to%20use%20Tools/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252F0cdade12-c78e-4203-bc6c-51dc10b7f4d9_1652x596.jpeg)

](https://substackcdn.com/image/fetch/$s_!S-WY!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F0cdade12-c78e-4203-bc6c-51dc10b7f4d9_1652x596.png)

A simple recipe for leveraging search tools with GPT-4

**GPT-4 plugin workflow.** As an example, GPT-4 has access to a variety of different tools via the [plugin store](https://openai.com/blog/chatgpt-plugins). However, the model is not explicitly fine-tuned to learn about each plugin within the store. Rather, it just uses in-context learning. In particular, OpenAI has invested heavily ubto improve GPT-4’s [steerability](https://twitter.com/cwolferesearch/status/1645535868021805056?s=20), which has made the model surprisingly capable of following very detailed instructions and prompts. As a result, teaching GPT-4 how to use a plugin only requires:

1.  A textual description describing the plugin’s purpose
    
2.  A schema describing the input/output format for the plugin’s API
    

Using this information, the model can determine when to use a plugin on its own, make properly-formatted API calls, and integrate the resulting information into its dialogue. All of this is done purely via textual descriptions without any explicit fine-tuning, _revealing that teaching LLMs to leverage external tools is likely to become easier over time_. To understand this process in more detail, we can look at [open-source plugin implementations](https://github.com/openai/chatgpt-retrieval-plugin) or [developer documentation](https://platform.openai.com/docs/plugins/introduction/plugin-flow) for OpenAI plugins.

## Closing Remarks

Similar to how humans become better with access to tools (e.g., hammers, computers, planes, etc.), LLMs become more capable when given access to a set of simple APIs that can provide useful information or perform simple tasks for them. _Why would we rely 100% on an LLM to solve everything, when we can delegate difficult tasks to a more accurate and specialized tool?_ We can use such an approach to mitigate problems that are constantly encountered with these models, such as incorrect information within the output or a lack of temporal reasoning skills. With Toolformer \[1\], we see than LLMs can be taught to leverage external tools via fine-tuning over a dataset of tool-following exemplars. But, recent trends suggest that teaching LLMs to use external tools might be possible via in-context learning alone. There is a lot to be uncovered in this area, and it will be interesting to watch these topics and related applications evolve over time!

### New to the newsletter?

Hello! I am [Cameron R. Wolfe](https://cameronrwolfe.me/), Director of AI at [Rebuy](https://www.rebuyengine.com/) and PhD student at Rice University. I study the empirical and theoretical foundations of deep learning. This is the Deep (Learning) Focus newsletter, where I help readers build a better understanding of deep learning research via understandable overviews that explain relevant topics from the ground up. If you like this newsletter, please subscribe, share it, or follow me on [twitter](https://twitter.com/cwolferesearch)!

### Bibliography

\[1\] Schick, Timo, et al. "Toolformer: Language models can teach themselves to use tools." _arXiv preprint arXiv:2302.04761_ (2023).

\[2\] Komeili, Mojtaba, Kurt Shuster, and Jason Weston. "Internet-augmented dialogue generation." _arXiv preprint arXiv:2107.07566_ (2021).

\[3\] Thoppilan, Romal, et al. "Lamda: Language models for dialog applications." _arXiv preprint arXiv:2201.08239_ (2022).

\[4\] Wei, Jason, et al. "Chain of thought prompting elicits reasoning in large language models." _arXiv preprint arXiv:2201.11903_ (2022).

\[5\] Wang, Ben, and Aran Komatsuzaki. "GPT-J-6B: A 6 billion parameter autoregressive language model." (2021).

\[6\] Zhang, Susan, et al. "Opt: Open pre-trained transformer language models." _arXiv preprint arXiv:2205.01068_ (2022).

\[7\] Brown, Tom, et al. "Language models are few-shot learners." _Advances in neural information processing systems_ 33 (2020): 1877-1901.

\[8\] Parisi, Aaron, Yao Zhao, and Noah Fiedel. "Talm: Tool augmented language models." _arXiv preprint arXiv:2205.12255_ (2022).

\[9\] Dhingra, Bhuwan, et al. "Time-aware language models as temporal knowledge bases." _Transactions of the Association for Computational Linguistics_ 10 (2022): 257-273.

\[10\] Chen, Mark, et al. "Evaluating large language models trained on code." _arXiv preprint arXiv:2107.03374_ (2021).

\[11\] Ouyang, Long, et al. "Training language models to follow instructions with human feedback." _Advances in Neural Information Processing Systems_ 35 (2022): 27730-27744.

\[12\] Zhou, Chunting, et al. "Lima: Less is more for alignment." _arXiv preprint arXiv:2305.11206_ (2023).

\[13\] Izacard, Gautier, et al. "Atlas: Few-shot learning with retrieval augmented language models." _arXiv preprint arXiv_ 2208 (2022).