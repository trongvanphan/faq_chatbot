from services import get_azure_llm, get_tavily_search
llm = get_azure_llm()

def evaluate(prompt):
    response = llm.chat.completions.create(
        model="GPT-4.1",
        messages=[
            {"role": "system", "content": """You are an expert car assistant.

Your job is to evaluate whether a news article is directly relevant to a user's question about cars, vehicles, automotive trends, car models, safety, pricing, features, or industry updates.

Consider the news title, content, and the user's question.

If the news clearly answers or provides valuable information related to the user's question, reply with:
YES

If the news is not directly related or only vaguely mentions related topics, reply with:
NO

Reply strictly with YES or NO."""},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0,
        max_tokens=10
    )
    return response.choices[0].message.content.strip()

def external_news_agent(state):
    question = state.get("question", "").strip()
    if not question:
        return {**state, "external_context": "⚠️ No question provided for news search."}

    try:
        focused_query = f"Latest automotive news about: {question}"
        response = get_tavily_search().invoke(focused_query)
        articles = []
        for res in response.get("results", []):
            title = res.get("title", "").strip()
            url = res.get("url", "").strip()
            content = res.get("content", "").strip()

            # Keep articles with either content or meaningful title + url
            if title and url:
                articles.append({
                    "title": title,
                    "url": url,
                    "content": content or "No detailed content available."
                })

        if not articles:
            return {**state, "external_context": "⚠️ No usable news articles found."}

        relevant_articles = []
        print(f"🔍 Found {articles} articles, checking relevance...")
        for article in articles:
            check_prompt = f"""
You are a helpful assistant checking news relevance.

User question:
"{question}"

News title:
"{article['title']}"

News content:
"{article['content']}"

Is this news relevant to the user's question? Reply with YES or NO.
"""
            try:
                llm_response = evaluate(check_prompt).upper()
                print(f"🔍 LLM Relevance Check: {llm_response} for article '{article['title']}'")
                if llm_response == "YES":
                    relevant_articles.append(article)
            except Exception as e:
                print(f"⚠️ LLM relevance check failed for article '{article['title']}': {str(e)}")
                continue  # Continue with next article

        if not relevant_articles:
            return {**state, "answer": "⚠️ No news articles were found"}

        combined_news = "\n\n".join(
            f"### 📰 {art['title']}\n"
            f"{art['content']}\n"
            f"[🔗 Read more]({art['url']})"
            for art in relevant_articles
        )

        return {**state, "answer": combined_news}

    except Exception as e:
        return {**state, "answer": f"⚠️ External news retrieval failed: {str(e)}"}
