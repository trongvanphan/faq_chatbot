from services import get_azure_llm, get_tavily_search
from langchain_core.messages import SystemMessage, HumanMessage
llm = get_azure_llm()

def evaluate(prompt):
    response = llm.invoke([
        SystemMessage(content="""Bạn là trợ lý chuyên gia về ô tô.

        Công việc của bạn là đánh giá xem một bài báo có liên quan trực tiếp đến câu hỏi của người dùng về xe hơi, ô tô, xu hướng ô tô, mẫu xe, an toàn, giá cả, tính năng, hoặc cập nhật ngành hay không.

        Xem xét tiêu đề tin tức, nội dung và câu hỏi của người dùng.

        Nếu tin tức trả lời rõ ràng hoặc cung cấp thông tin có giá trị liên quan đến câu hỏi của người dùng, hãy trả lời:
        YES

        Nếu tin tức không liên quan trực tiếp hoặc chỉ đề cập mơ hồ đến các chủ đề liên quan, hãy trả lời:
        NO

        Chỉ trả lời YES hoặc NO."""),
        HumanMessage(content=prompt)
    ])
    
    return response.content

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
            return {**state, "answer": "⚠️ Không tìm thấy tin tức liên quan đến câu hỏi của bạn về ô tô."}

        # Format in Vietnamese
        combined_news = "📰 **Tin tức ô tô mới nhất:**\n\n"
        combined_news += "\n\n".join(
            f"### � {art['title']}\n"
            f"{art['content'][:300]}...\n"
            f"[🔗 Đọc thêm]({art['url']})"
            for art in relevant_articles
        )

        return {**state, "answer": combined_news}

    except Exception as e:
        return {**state, "answer": f"⚠️ Không thể tìm kiếm tin tức: {str(e)}"}
