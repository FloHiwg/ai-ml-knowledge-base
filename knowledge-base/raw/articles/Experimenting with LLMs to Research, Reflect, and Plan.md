Over the past few weekends, I’ve been playing with large language models (LLMs) and combining them with tools and interfaces to build a [simple assistant](https://eugeneyan.com/writing/llm-experiments/#tools-to-summarize-query-and-advise). Along the way, I noticed [some issues with retrieval](https://eugeneyan.com/writing/llm-experiments/#shortcomings-in-retrieval-and-how-to-solve-them) and thought of a few ideas on how to solve them.

It was a lot of fun, and I came away from this experience optimistic that LLMs have great potential to augment how we work, especially how we [research, reflect, and plan](https://eugeneyan.com/writing/llm-experiments/#llm-augmented-research-reflection-and-planning).

> Here’s the [code](https://github.com/eugeneyan/discord-llm) to speed run this. It’s messy and relies largely on LangChain abstractions. Could be useful as a reference, but not as learning material.

## Tools to summarize, query, and advise[](https://eugeneyan.com/writing/llm-experiments/#tools-to-summarize-query-and-advise)

My first project was inspired by Simon’s [post](https://simonwillison.net/2023/Mar/10/chatgpt-internet-access/) on how ChatGPT is unable to read content from URLs. Thus, I tried to help it do just that with `/summarize` and `/eli5`. The former can `/summarize` content from URLs into bullet points while the latter reads the content and explains like I’m five (eli5). They help me skim content before deciding if I want to read the details in full ([tweet thread](https://twitter.com/eugeneyan/status/1637562031233708032)).

![Using /summarize on 'ChatGPT Is a Blurry JPEG of the Web'](Experimenting%20with%20LLMs%20to%20Research,%20Reflect,%20and%20Plan/summarize.webp "Using /summarize on 'ChatGPT Is a Blurry JPEG of the Web'")

Bullet point summary of "[ChatGPT Is a Blurry JPEG of the Web](https://www.newyorker.com/tech/annals-of-technology/chatgpt-is-a-blurry-jpeg-of-the-web)"

![Using /eli5 on 'ChatGPT Is a Blurry JPEG of the Web'](Experimenting%20with%20LLMs%20to%20Research,%20Reflect,%20and%20Plan/eli5.webp "Using /eli5 on 'ChatGPT Is a Blurry JPEG of the Web'")

Explaining to a five-year old "[ChatGPT Is a Blurry JPEG of the Web](https://www.newyorker.com/tech/annals-of-technology/chatgpt-is-a-blurry-jpeg-of-the-web)"

Next, I explored building agents with access to tools like SQL and search. `/sql` takes natural language questions, writes and runs SQL queries, and returns the result. `/sql-agent` does the same but as a zero-shot agent. Though `/sql-agent` didn’t work as reliably as I hoped (see [Appendix](https://eugeneyan.com/writing/llm-experiments/#appendix)), watching it struggle and eventually get it right was endearing and motivating ([tweet thread](https://twitter.com/eugeneyan/status/1640160729537073152)).

![Querying a small database via /sql](Experimenting%20with%20LLMs%20to%20Research,%20Reflect,%20and%20Plan/sql.webp "Querying a small database via /sql")

Querying a small database via `/sql`

![Querying a small database via /sql-agent](Experimenting%20with%20LLMs%20to%20Research,%20Reflect,%20and%20Plan/sql-agent-1.webp "Querying a small database via /sql-agent") ![Querying a small database via /sql-agent](Experimenting%20with%20LLMs%20to%20Research,%20Reflect,%20and%20Plan/sql-agent-2.webp "Querying a small database via /sql-agent") ![Querying a small database via /sql-agent](Experimenting%20with%20LLMs%20to%20Research,%20Reflect,%20and%20Plan/sql-agent-3.webp "Querying a small database via /sql-agent")

Querying a small database via `/sql-agent` (it's fun to watch it think, observe, and act)

I also built `/search`, an agent that can use tools to query search provider APIs (e.g., Google Search). This way, the LLM can find recent data that it hasn’t been trained on and return an accurate and up-to-date response. (This was before ChatGPT plugins that now have this functionality out of the box. Even so, it was fun building it from scratch.)

![Using /search to find recent information for the LLM](Experimenting%20with%20LLMs%20to%20Research,%20Reflect,%20and%20Plan/search.webp "Using /search to find recent information for the LLM") ![Using /search to find recent information for the LLM](Experimenting%20with%20LLMs%20to%20Research,%20Reflect,%20and%20Plan/search-2.webp "Using /search to find recent information for the LLM")

Using `/search` to find recent information for the LLM

Most recently, I built a `/board` of advisors. It’s based on content from informal mentors—and prolific writers—like Paul Graham, Marc Andreessen, Will Larson, Charity Majors, and Naval Ravikant. `/board` provides advice on topics including technology, leadership, and startups. Its response includes source URLs for further reading, which can be chained with `/summarize` and `/eli5` ([tweet thread](https://twitter.com/eugeneyan/status/1642775988215107584)).

![Seeking advice from the /board](Experimenting%20with%20LLMs%20to%20Research,%20Reflect,%20and%20Plan/board-2.webp "Seeking advice on technical leadership from the /board") ![Seeking advice from the /board](Experimenting%20with%20LLMs%20to%20Research,%20Reflect,%20and%20Plan/board.webp "Seeking advice on personal success from the /board")

Seeking advice on technical leadership and personal success from the `/board`

I also built `/ask-ey` which is similar to `/board` but based on my own writing. Because I’m more familiar with my work, it’s easier to spot issues such as not using an expected source (i.e., recall issue) or using irrelevant sources (i.e., ranking issue).

![Synthesizing across posts on my site via /ask-ey](Experimenting%20with%20LLMs%20to%20Research,%20Reflect,%20and%20Plan/ask-ey.webp "Synthesizing across recsys posts on my site via /ask-ey") ![Synthesizing across posts on my site via /ask-ey](Experimenting%20with%20LLMs%20to%20Research,%20Reflect,%20and%20Plan/ask-ey-2.webp "Synthesizing across mechanism posts on my site via /ask-ey")

Synthesizing across recsys and mechanism posts on my site via `/ask-ey`

## Combining LLMs, databases, search APIs, and Discord[](https://eugeneyan.com/writing/llm-experiments/#combining-llms-databases-search-apis-and-discord)

To extract content from URLs, I used good ol’ [`requests`](https://pypi.org/project/requests/) and [`BeautifulSoup`](https://pypi.org/project/beautifulsoup4/). For LLMs, I worked with OpenAI’s [`gpt-3.5-turbo`](https://platform.openai.com/docs/models/gpt-3-5) and [`gpt-4`](https://platform.openai.com/docs/models/gpt-4), primarily the former due to its cost-effectiveness. [LangChain](https://github.com/hwchase17/langchain) made it easy to apply the LLM chains, agents, and tools. For search, I used Google’s custom search through the [`google-api-python-client`](https://pypi.org/project/google-api-python-client/2.84.0/) wrapper. To embed documents and queries, I used OpenAI’s [`text-embedding-ada-002`](https://platform.openai.com/docs/models/embeddings).

The application server was hosted on [Railway](https://railway.app/). To host, serve, and find nearest neighbours on embeddings, I used [Pinecone](https://www.pinecone.io/). Lastly, I integrated everything with Discord via the [`interactions`](https://github.com/interactions-py/interactions.py) wrapper.

## Shortcomings in retrieval and how to solve them[](https://eugeneyan.com/writing/llm-experiments/#shortcomings-in-retrieval-and-how-to-solve-them)

While experimenting with `/board` and `/ask-ey`, I noticed that it wasn’t retrieving and using the expected sources some of the time.

For example, when I asked the `/board` “How do I decide between being a manager or an IC”, it fails to use (as a source) any of Charity’s writing on the [manager](https://charity.wtf/2017/05/11/the-engineer-manager-pendulum/)\-[engineer](https://charity.wtf/2019/01/04/engineering-management-the-pendulum-or-the-ladder/) [pendulum](https://charity.wtf/2022/03/24/twin-anxieties-of-the-engineer-manager-pendulum/) or [management](https://charity.wtf/2019/09/08/reasons-not-to-be-a-manager/). However, tweaking the question to “How do I decide between being a manager or an _engineer_” resolved this.

![Failing to retrieve the relevant engineering-IC resources the first time](Experimenting%20with%20LLMs%20to%20Research,%20Reflect,%20and%20Plan/manager-ic.webp "Failing to retrieve the relevant engineering-IC resources the first time")

Asking the first question doesn't lead to the expected manager-eng sources being used; the second does

Similarly, when I `/ask-ey` “What bandits are used in recommendation systems”, it didn’t retrieve my main writing on [bandits](https://eugeneyan.com/writing/bandits/). But updating the question to “_How_ are bandits used in recommendation systems” fixed this issue.

![Failing to retrieve the relevant bandit resources the first time](Experimenting%20with%20LLMs%20to%20Research,%20Reflect,%20and%20Plan/bandit.webp "Failing to retrieve the relevant bandit resources the first time")

Asking the first question doesn't lead to the expected bandit sources being used; the second does

But when I checked the retrieved sources, it was disappointing to see that only the top hit came from the [expected URL](https://eugeneyan.com/writing/bandits/), and even that was an irrelevant chunk of the content. (Text from each URL is split into chunks of 1,500 tokens.) I had expected embedding-based retrival to fetch more chunks from the bandit URL. This suggests there’s room to improve on how I processed the data before embedding and highlights the importance of data prep.

![Only the top hit has the right resource but it doesn't contain useful content](Experimenting%20with%20LLMs%20to%20Research,%20Reflect,%20and%20Plan/bandit-sources.webp "Only the top hit has the right resource but it doesn't contain useful content")

Only the top hit has the right resource but it doesn't contain useful content

This issue is partially due to poor recall. Here are a few hypotheses on why this happens:

-   [ANN indices might be tuned sub-optimally](https://eugeneyan.com/writing/llm-experiments/#ann-indices-might-be-tuned-sub-optimally)
-   [Off-the-shelf embeddings may transfer poorly across domains](https://eugeneyan.com/writing/llm-experiments/#off-the-shelf-embeddings-may-transfer-poorly-across-domains)
-   [Documents may be inadequately chunked](https://eugeneyan.com/writing/llm-experiments/#documents-may-be-inadequately-chunked)
-   [Embedding-based retrieval alone might be insufficient](https://eugeneyan.com/writing/llm-experiments/#embedding-based-retrieval-alone-might-be-insufficient)

### ANN indices might be tuned sub-optimally[](https://eugeneyan.com/writing/llm-experiments/#ann-indices-might-be-tuned-sub-optimally)

Most (if not all) embedding-based retrieval use _approximate_ nearest neighbours (ANN). If we use _exact_ nearest neighbours, we would get perfect recall of 1.0 but with higher latency (think seconds). In contrast, ANN offers good-enough recall (~0.95) with millisecond latency. I’ve [previously compared several open-source ANNs](https://eugeneyan.com/writing/real-time-recommendations/#how-to-design-and-implement-an-mvp) and most achieved ~0.95 recall at throughput of hundreds to thousands of queries per second.

![Benchmarking ANNs on recall vs latency](Experimenting%20with%20LLMs%20to%20Research,%20Reflect,%20and%20Plan/ann-benchmarks.webp "Benchmarking ANNs on recall vs latency")

Benchmarking ANNs on recall vs latency across index parameters; top-right is better.

If the issue lies in a sub-optimally tuned ANN index, we can tune the index parameters to achieve the recall/latency trade-off we need. However, this requires more effort compared to a plug-and-play index as a service. I’m also not sure if cloud vector databases offer the option to tune the ANN. As a result, we could end up with [as low as 50% recall](https://twitter.com/jobergum/status/1643187540222959616).

### Off-the-shelf embeddings may transfer poorly across domains[](https://eugeneyan.com/writing/llm-experiments/#off-the-shelf-embeddings-may-transfer-poorly-across-domains)

Off-the-shelf embeddings may be too generic and don’t transfer well to other domains. From the examples in [this OpenAI forum](https://community.openai.com/t/some-questions-about-text-embedding-ada-002-s-embedding/35299), we see unexpectedly high cosine similarity between seemingly different text. (While the failure examples above seem generic, the point is that we should pay attention when applying embeddings to our domain.)

A possible solution: If we have both positive and negative examples, we can fine-tune an embedding model via triplet loss. This way, we can ensure that the distance between the anchor and positive example is closer than the distance between the anchor and negative example (by a margin). This is especially helpful when embedding private data that contains language that foundational models may not have seen.

Preparing these `(anchor, positive, negative)` triplets is the bulk of the work. One way is to collect explicit feedback by returning sources in responses and asking people to thumbs up/down on them. Alternatively, implicit feedback is available in settings such as e-commerce, where we can consider results that users ignore as negatives, or search, where we provide sources in results (à la Bing Chat) and observe if users click on them.

### Documents may be inadequately chunked[](https://eugeneyan.com/writing/llm-experiments/#documents-may-be-inadequately-chunked)

Third, if we’re using LangChain, we’re probably taking the default approach of using its [text splitter](https://python.langchain.com/en/latest/reference/modules/text_splitter.html) and chunking content into documents of 1,000 - 2,000 tokens each. While we can have such large documents because recent embedding models can scale to long input text, problems may arise when the input is overloaded with multiple concepts.

Imagine embedding a [3,000-word document](https://eugeneyan.com/writing/content-moderation/) that has five high-level concepts and a dozen lower-level concepts. Embedding the entire document may force the model to place it in the latent space of all concepts, making retrieval based on any single concept difficult. Even if we split it into multiple chunks of 1,500 tokens each, each chunk’s embedding could be a muddy blend of multiple concepts.

A more effective approach could be to chunk documents by sections or paragraphs. After all, this is how most content is organized, where each section/chapter discusses a high-level concept while paragraphs contain lower-level concepts. This should enhance the quality of embeddings and improve embedding-based retrieval. Thankfully, most writing is organized by sections or chapters, with paragraphs separated by `/n/n`.

I suspect there are large gains to be made here though it’s more art than science. It also requires more manual work—scraping and preparing data for my document store took as much, if not more, effort as building the tools. Also see this [OpenAI example](https://github.com/eugeneyan/openai-cookbook/blob/main/examples/Embedding_Wikipedia_articles_for_search.ipynb) of how they cleaned, chunked, and embedded wikipedia articles.

### Embedding-based retrieval alone might be insufficient[](https://eugeneyan.com/writing/llm-experiments/#embedding-based-retrieval-alone-might-be-insufficient)

Lastly, relying solely on document and query embeddings for retrieval may be insufficient. While embedding-based retrieval is great for semantic retrieval, it can struggle when term matching is crucial. Because embeddings represent documents as dense vectors, they may fail to capture the importance of individual words in the documents, leading to poor recall. And if the search query is precise and short, embedding-based retrieval may not add that much value, or perform worse. Also, simply embedding the entire query might be too crude and could make the results sensitive to how the question is phrased.

One solution is to ensemble semantic search with keyword search. [BM25](https://en.wikipedia.org/wiki/Okapi_BM25) is a solid baseline when we expect at least one keyword to match. Nonetheless, it doesn’t do as well on shorter queries where there’s no keyword overlap with the relevant documents—in this case, averaged keyword embeddings may perform better. By combining the best of keyword search and semantic search, we can improve recall for various types of queries.

Query parsing can also help by identifying and expanding (e.g., synonyms) keywords in the query, ensuring that questions are interpreted consistently regardless of minor differences in phrasing. Spelling correction and autocomplete can also guide users toward better results. (A simple hack is to have the LLM parse the query before proceeding with retrieval.)

We can also rank retrieved documents before including them in the LLM’s context. In the bandit query example above, the top hit doesn’t offer any useful information. One solution is to rank documents via query-dependent and query-independent signals. The former is done via BM25 and semantic search while the latter includes user feedback, popularity, recency, PageRank, and so on. Heuristics such as document length may also help.

> Update: The [next iteration](https://eugeneyan.com/writing/obsidian-copilot/) uses a hybrid of OpenSearch and E5 embeddings.

## LLM-augmented research, reflection, and planning[](https://eugeneyan.com/writing/llm-experiments/#llm-augmented-research-reflection-and-planning)

While the tools above were hacked together over a few weekends, they hint at the potential in LLM-augmented workflows. Here are some ideas in the adjacent possible.

### Enterprise/Personal Search and Q&A[](https://eugeneyan.com/writing/llm-experiments/#enterprisepersonal-search-and-qa)

Picture yourself as part of an organization where internal documents, meeting transcripts, code, and other resources were stored as retrievable documents. For confidentiality and security reasons, you would only be able to access documents that you have permissions for. To navigate this vast knowledge base, you could ask simple queries such as:

-   What were the common causes of high-severity tickets last month?
-   What were our biggest wins and most valuable lessons from last quarter?
-   What are some recent “Think Big” ideas or [PRFAQs](https://commoncog.com/putting-amazons-pr-faq-to-practice/) the team has written?

Then, instead of returning links to documents that we would have to read, why not have an LLM `/summarize` or `/eli5` the information? It could also synthesize via `/board` and find common patterns, uncovering root causes for seemingly unrelated incidents or finding synergies (or duplication) in upcoming projects. To augment the results, it could `/sql` or `/sql-agent` databases or `/search` for recent data on the internet.

Let’s consider another scenario which uses a personal knowledge base. Over the years, I’ve built up a library of books, papers, and disorganized notes. Unfortunately, my [memory degrades over time](https://en.wikipedia.org/wiki/Forgetting_curve) and I forget most of the details within a week. To address this, I can apply similar techniques to my personal knowledge base and `/ask-ey`:

-   What papers discuss the use of [bandits in recommendation systems](https://eugeneyan.com/writing/bandits/)?
-   What guidance would I give someone [joining](https://eugeneyan.com/writing/onboarding/) [a](https://eugeneyan.com/writing/influencing-without-authority/) [new](https://eugeneyan.com/writing/15-5/) [team](https://eugeneyan.com/writing/red-flags/)?
-   What were the main themes in my life in the [last](https://eugeneyan.com/writing/retrospective-2020/) [few](https://eugeneyan.com/writing/2021-year-in-review/) [years](https://eugeneyan.com/writing/2022-in-review/)?

For each of those questions, I’ve invested effort into research, distilling, and publishing the answers as [permanent notes](https://eugeneyan.com/writing/note-taking-zettelkasten/#permanent-note). And the process was invaluable for clarifying my thoughts and learning while writing. That said, I think the tools above can get us ~50% there with far less effort. Products like [Glean](https://www.glean.com/) (enterprise) and [Rewind](https://www.rewind.ai/) (personal) seem to do this.

### Research, Planning, and Writing[](https://eugeneyan.com/writing/llm-experiments/#research-planning-and-writing)

Back to the scenario of internal docs and meeting transcripts. Let’s say you’re a leader in your org and need to write an important doc. It could be a six-week plan to tackle tech debt or a more ambitious three-year roadmap. How can we make writing this doc easier?

To write the tech debt document, we’ll first need to understand what are the most pressing issues. We can start by asking `/board` to gather details about the problems we’re already aware of. `/board` can help us retrieve and synthesize the relevant trouble tickets, war room meeting transcripts, and more via `/sql` and internal `/search`. Then, we can expand to broader queries to find problems we’re unaware of, before diving deeper as needed.

With the top three issues, we can start writing an introduction that outlines the purpose of the document (aka the [Why](https://eugeneyan.com/writing/writing-docs-why-what-how/#writing-framework-why-what-how-who) aka the prompt). Then, as we created section headers for each issue, a document retrieval + LLM copilot helps with filling them out, providing data points (`/sql`), links to relevant sources (`/search`), and even suggesting solutions (`/board`). Bing Chat has this in some form. Also, I believe this is the vision for Office 365 Copilot.

As the main author, we’ll still need to apply our judgment to check the relevance of the sources and prioritize the issues. We’ll also need to assess suggested solutions and decide if tweaking one solution could address multiple issues, thereby reducing effort and duplication. Nonetheless, while we’re still responsible for writing the document, our copilot can help gather and prepare the data, significantly reducing our workload.

## LLMs: Not a knowledge base but a reasoning engine[](https://eugeneyan.com/writing/llm-experiments/#llms-not-a-knowledge-base-but-a-reasoning-engine)

> “The right way to think of the models that we create is a reasoning engine, not a fact database. They can also act as a fact database, but that’s not really what’s special about them. What we want them to do is something closer to the ability to reason, not to memorize.” — [Sam Altman](https://abcnews.go.com/Technology/openai-ceo-sam-altman-ai-reshape-society-acknowledges/story?id=97897122)

We’ve seen that LLMs are adept at using tools, summarizing information, and synthesizing patterns. Being trained on the entire internet somehow gave them reasoning abilities. (Perhaps this is due to learning on Github and StackOverflow data, since code is logic?) Nonetheless, while they can reason, they’re often constrained by the lack of in-depth or private knowledge, like the kind found in enterprise or personal knowledge bases.

I think the key challenge, and solution, is getting them the right information at the right time. Having a well-organized document store can help. And by using a hybrid of keyword and semantic search, we can accurately retrieve the context that LLMs need—this explains why traditional search indices are integrating [vector](https://www.elastic.co/guide/en/elasticsearch/reference/master/knn-search.html) [search](https://opensearch.org/docs/latest/search-plugins/knn/index/), why vector databases are adding [keyword](https://www.pinecone.io/learn/hybrid-search/) [search](https://weaviate.io/blog/hybrid-search-explained), and why some apps adopt a hybrid approach ([Vespa.ai](https://vespa.ai/features), [FB search](https://arxiv.org/abs/2006.11632)).

• • •

It’s hard to foresee how effective or widespread LLMs will become. I’ve previously [asked](https://www.linkedin.com/posts/eugeneyan_activity-7041585027503046657-CeIo) whether LLMs might have the same impact as computers, mobile phones, or the internet. But as I continue experimenting with them, I’m starting to think that their potential could be even greater than all those technologies combined.

And even if I end up being wrong, at least I can still have fun getting LLMs to explain headlines in the style of Dr. Seuss or make up quirky quotes on my Raspberry Pi Pico.

___

## Appendix[](https://eugeneyan.com/writing/llm-experiments/#appendix)

Here’s an example of how `/sql-agent` struggled and eventually figured out that it should check the database schema. While it finally executed the right query and got the results, it also ran out of iterations before it could respond 🥲 (Back to [top](https://eugeneyan.com/writing/llm-experiments/#llm-tools-to-summarize-query-and-advise))

![Querying a small database via /sql-agent](Experimenting%20with%20LLMs%20to%20Research,%20Reflect,%20and%20Plan/sql-agent-fail-1.webp "Querying a small database via /sql-agent") ![Querying a small database via /sql-agent](Experimenting%20with%20LLMs%20to%20Research,%20Reflect,%20and%20Plan/sql-agent-fail-2.webp "Querying a small database via /sql-agent") ![Querying a small database via /sql-agent](Experimenting%20with%20LLMs%20to%20Research,%20Reflect,%20and%20Plan/sql-agent-fail-3.webp "Querying a small database via /sql-agent") ![Querying a small database via /sql-agent](Experimenting%20with%20LLMs%20to%20Research,%20Reflect,%20and%20Plan/sql-agent-fail-4.webp "Querying a small database via /sql-agent")

`/sql-agent` struggling with getting the query right

If you found this useful, please cite this write-up as:

> Yan, Ziyou. (Apr 2023). Experimenting with LLMs to Research, Reflect, and Plan. eugeneyan.com. https://eugeneyan.com/writing/llm-experiments/.

or

```typescript
@article{yan2023llmapps,
  title   = {Experimenting with LLMs to Research, Reflect, and Plan},
  author  = {Yan, Ziyou},
  journal = {eugeneyan.com},
  year    = {2023},
  month   = {Apr},
  url     = {https://eugeneyan.com/writing/llm-experiments/}
}
```

Share on:

Join **11,800+** readers getting updates on machine learning, RecSys, LLMs, and engineering.