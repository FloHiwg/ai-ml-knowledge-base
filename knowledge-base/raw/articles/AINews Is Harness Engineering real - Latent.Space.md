A common debate in my finance days was about [the value of the human vs the value of the seat](https://scalingdevtools.com/podcast/episodes/scaling-devtools-episode-swyx-final-2-mp4): if a trader made $3m in profits, how much of it was because of her skills, and how much was because of the position/institution/brand she is in, and any generally competent human could have made the same results?

The same debate is currently raging in “Harness Engineering”, the systems subset of [Agent Engineering](https://www.latent.space/p/agent), and the [main job of Agent Labs](https://www.latent.space/p/agent-labs). The central tension is between **Big Model** and **Big Harness**. \[An AI framework founder you all know\] once confided in me at an OpenAI event: “I’m not even sure these guys want me to exist.”

> _Aside: let’s [define Harness](https://x.com/djfarrelly/status/2028556984396452250) — “In every engineering discipline, a harness is the same thing: the layer that connects, protects, and orchestrates components — without doing the work itself.“_

And, talking with the **Big Model** guys, you really see it:

# **AI Twitter Recap**

-   Every podcast with [Boris Cherny and Cat Wu](https://www.latent.space/p/claude-code) emphasizes how minimal the harness of Claude Code is, meaning their job is mostly letting the model express its full power in the way that only the model maker knows best:
    
    -   [Boris](https://open.substack.com/pub/swyx/p/claude-code?r=1h4isl&selection=5895f787-9fb7-4c30-82f0-98c9af305872&utm_campaign=post-share-selection&utm_medium=web&aspectRatio=instagram&textColor=%23ffffff&bgImage=true): “I would say like there’s nothing that secret in the source. And obviously it’s all JavaScript, so you can just decompile it. Compilation’s out there. It’s very interesting. Yeah. And generally our approach is, you know, all the secret sauce, it’s all in the model. And this is the thinnest possible wrapper over the model. We literally could not build anything more minimal. This is the most minimal thing.
        
    -   Cat \[01:09:21\]: It is very much the simplest thing I think by design.
        
    -   Boris \[01:09:25\]: So it’s got simpler. It got simpler. It doesn’t go more complex. We’ve rewritten it from scratch probably every three weeks, four weeks or something. And it just like all the, it’s like a ship of Theseus, right? Like every piece keeps getting swapped out and just cause quad is so good at writing its own code.”
        
-   OpenAI’s [own piece on Harness Engineering](https://openai.com/index/harness-engineering/) (with upcoming guest Ryan Lopopolo on the Codex team) emphasizes how simple it is to start. Of course, with [the “execuhire” of OpenClaw](https://www.latent.space/p/ainews-moltbook-the-first-social), OpenAI are now big investors of the world’s most successful open source harness.
    
-   [Noam Brown](https://open.substack.com/pub/swyx/p/self-improving?r=1h4isl&selection=cf386440-623f-4e12-9475-16418f0b6414&utm_campaign=post-share-selection&utm_medium=web&aspectRatio=instagram&textColor=%23ffffff&bgImage=true): “_before the reasoning models emerged, there was like all of this work that went into engineering agentic systems that like made a lot of calls to GPT-4o or like these non-reasoning models to get reasoning behavior. And then it turns out we just created reasoning models and they, you don’t need this complex behavior. In fact, in many ways, it makes it worse. Like you just give the reasoning model the same question without any sort of scaffolding and it just does it. And so people are building scaffolding on top of the reasoning models right now. But I think in many ways, **those scaffolds will also just be replaced by the reasoning models and models in general becoming more capable**. And similarly, I think things like model routers, we’ve said pretty openly that we want to move to a world where there is a single unified model. And in that world, you shouldn’t need a router on top of the model._”
    
-   [METR saying Claude Code and Codex](https://x.com/nikolaj2030/status/2022398669337825737) don’t beat a basic scaffold:
    
    [
    
    ![](AINews%20Is%20Harness%20Engineering%20real%20-%20Latent.Space/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252F518dc06e-45ab-4c1d-81e5-76f385eae461_1174x1146.jpeg)
    
    ](https://substackcdn.com/image/fetch/$s_!Ve3G!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F518dc06e-45ab-4c1d-81e5-76f385eae461_1174x1146.png)
    
-   [Scale AI’s SWE-Atlas](https://x.com/scale_AI/status/2029244660905095359) is finds that Opus 4.6 does 2.5 points better in Claude Code than in the generic SWE-Agent, but the reverse for GPT 5.2, making the harness you choose essentially noise within the margin of error:
    
    [
    
    ![Image](AINews%20Is%20Harness%20Engineering%20real%20-%20Latent.Space/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252Fd50421a3-d45c-4044-b491-8cc3348121eb_1214x1432.png)
    
    ](https://substackcdn.com/image/fetch/$s_!a0ia!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fd50421a3-d45c-4044-b491-8cc3348121eb_1214x1432.webp)
    

And yet. The **Big Harness** guys disagree:

-   **[The Harness is the Product](https://x.com/Hxlfed14/status/2028116431876116660)**:
    
    -   Every production agent converges on this core loop:
        
        > while (model returns tool calls):  
        > execute tool → capture result → append to context → call model again
        
        That is it. The entire architecture of Claude Code, Cursor’s agent, and Manus fits inside that loop.
        
-   [Jerry Liu](https://x.com/jerryjliu0/status/2026840829441225127?s=20): “The Model Harness is Everything — the biggest barrier to getting value from AI is your own ability to context and workflow engineer the models. This is \*especially\* true the more horizontal the tool that you’re using.”
    
    [
    
    ![](AINews%20Is%20Harness%20Engineering%20real%20-%20Latent.Space/https%253A%252F%252Fsubstack-post-media.s3.amazonaws.com%252Fpublic%252Fimages%252Fe98e0f7e-eee7-4ced-afd9-ccc4d5e2eead_1216x1040.jpeg)
    
    ](https://substackcdn.com/image/fetch/$s_!nEpJ!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fe98e0f7e-eee7-4ced-afd9-ccc4d5e2eead_1216x1040.png)
    
-   [Improving 15 LLMs at Coding in One Afternoon. Only the Harness Changed](http://blog.can.ac/2026/02/12/the-harness-problem/) shows dramatic improvements in every model when you optimize the harness (Pi)
    

Obviously Big Harness guys are trying to sell you their Harness, Big Model guys are trying to sell you their Model. The ML/AI industry has always had some form of milquetoast “[compound AI](http://bair.berkeley.edu/blog/2024/02/18/compound-ai-systems/)” debate that tells you both are valuable. But perhaps the times are changing.

On Latent Space we’ve been very, very respectful of the Bitter Lesson, but increasingly as the Agent Labs thesis has played out (with [Cursor now valued at $50B](https://www.latent.space/p/ainews-truth-in-the-time-of-artifice)), we are acknowledging that “Harness Engineering” has real value. [AIE Europe](https://www.ai.engineer/europe) now has **the world’s first Harness Engineering track**, and if you are keen on this debate, you should join.

> _AI News for 3/3/2026-3/4/2026. We checked 12 subreddits, [544 Twitters](https://twitter.com/i/lists/1585430245762441216) and 24 Discords (**264** channels, and **14242** messages) for you. Estimated reading time saved (at 200wpm): **1397** minutes. [AINews’ website](https://news.smol.ai/) lets you search all past issues. As a reminder, [AINews is now a section of Latent Space](https://www.latent.space/p/2026). You can [opt in/out](https://support.substack.com/hc/en-us/articles/8914938285204-How-do-I-subscribe-to-or-unsubscribe-from-a-section-on-Substack) of email frequencies!_

## **AI Twitter Recap**

**Frontier model shipping: Gemini 3.1 Flash-Lite, GPT-5.4 rumors, and “agent-first” product positioning**

-   **Gemini 3.1 Flash-Lite positioning (speed/$)**: Demis Hassabis teased **Gemini 3.1 Flash-Lite** as “incredibly fast and cost-efficient” for its performance—clearly framing the model line around latency and cost per capability rather than raw frontier scores ([tweet](https://x.com/demishassabis/status/2029047252275060895)). Related product chatter highlights **NotebookLM** as a “favorite AI tool” ([tweet](https://x.com/demishassabis/status/2029355691933085731)) and a major new **NotebookLM Studio** feature: **Cinematic Video Overviews** that generate bespoke, immersive videos from user sources for Ultra users ([tweet](https://x.com/NotebookLM/status/2029240601334436080)).
    
-   **GPT-5.4 leak narrative (The Information)**: Multiple tweets amplify a report that **GPT-5.4** is coming with a **~1M token context window** and a new **“extreme reasoning mode”** that can “think for hours,” targeting long-horizon agentic workflows and lower complex-task error rates ([tweet](https://x.com/kimmonismus/status/2029213568155992425), [tweet](https://x.com/steph_palazzolo/status/2029212039760023941), [tweet](https://x.com/scaling01/status/2029215437922169254)). There’s also speculation that OpenAI is shifting to **more frequent (monthly) model updates** ([tweet](https://x.com/kimmonismus/status/2029223828677599244)). Separately, one arena watcher claims “GPT-5.4 landed in the arena,” implying an imminent release window ([tweet](https://x.com/kimmonismus/status/2029325405212070200)). Treat all of this as **unconfirmed** unless corroborated by OpenAI.
    
-   **Claude as “agent behavior” leader, not just coding**: Nat Lambert argues the discussion should shift from Anthropic “going all-in on code” to their lead on **general agent behavior**, implying coding capability will commoditize but agent robustness will not ([tweet](https://x.com/natolambert/status/2029212769648836806)). MathArena evaluation adds a datapoint: **Claude Opus 4.6** is strong overall but weak on **visual mathematics**, and costly to evaluate (claimed ~$8k) ([tweet](https://x.com/j_dekoninck/status/2029160582687985727)).
    

Hi **florian.hiwg@gmail.com**

## Keep reading with a 7-day free trial

Subscribe to Latent.Space to keep reading this post and get 7 days of free access to the full post archives.