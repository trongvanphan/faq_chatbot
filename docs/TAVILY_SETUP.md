# 🚗 Tavily API Setup for Automotive Bot

## Overview
The automotive bot now includes Tavily API integration for real-time news search and current information lookup. This allows users to get the latest automotive news, reviews, and market trends.

## 🔑 Getting Tavily API Key

1. **Visit Tavily**: Go to [https://tavily.com/](https://tavily.com/)
2. **Sign Up**: Create a free account
3. **Get API Key**: Copy your API key from the dashboard
4. **Free Tier**: 1000 searches per month (sufficient for testing)

## ⚙️ Environment Setup

Add your Tavily API key to your `.env` file:

```bash
# Existing variables
OPENAI_API_KEY=your_openai_key
OPENAI_BASE_URL=your_openai_base_url

# Add Tavily API key
TAVILY_API_KEY=your_tavily_api_key
```

## 📦 Install Dependencies

```bash
pip install tavily-python langchain-community langchain-core
```

Or update your requirements:

```bash
pip install -r requirements.txt
```

## 🧪 Test the Integration

Run the test script:

```bash
python test_automotive_agent.py
```

## 🔄 How It Works

### Smart Query Routing
The bot automatically detects query type and routes to appropriate handler:

**News/Current Events** → **Agent + Tavily**
- Keywords: "tin tức", "news", "mới nhất", "đánh giá", "review", etc.
- Searches real-time web for latest information

**Knowledge Base Queries** → **LangChain + ChromaDB**
- Keywords: "giá", "thông số", "specifications", etc.
- Searches uploaded documents and stored data

### Agent Tools
1. **Tavily Search**: Real-time web search for automotive news
2. **Knowledge Base Search**: Local document search

### Example Queries

**News Queries (uses Agent + Tavily):**
- "Tin tức mới nhất về xe điện Tesla"
- "Đánh giá xe Honda CR-V 2024"
- "Xu hướng thị trường ô tô Việt Nam 2024"
- "So sánh Toyota Camry và Honda Accord"

**Knowledge Base Queries (uses LangChain + ChromaDB):**
- "Giá xe Honda CR-V 2024 là bao nhiêu?"
- "Thông số kỹ thuật của Honda City"
- "Giá xe Audi A4"

## 🎯 Benefits

1. **Real-time Information**: Get latest news and reviews
2. **Hybrid Approach**: Combine local knowledge with web search
3. **Smart Routing**: Automatic query type detection
4. **Fallback Support**: Works even without Tavily API key
5. **Conversational Memory**: Maintains context across queries

## 🔧 Configuration Options

### Agent Settings
```python
# In automotive_bot.py
tavily_search = TavilySearchResults(
    api_key=TAVILY_API_KEY,
    max_results=5,        # Number of search results
    search_depth="advanced"  # "basic" or "advanced"
)
```

### Query Detection Keywords
```python
news_keywords = [
    "tin tức", "news", "mới nhất", "latest", "cập nhật", "update",
    "ra mắt", "launch", "giới thiệu", "introduce", "thị trường", "market",
    "xu hướng", "trend", "đánh giá", "review", "so sánh", "compare"
]
```

## 🚀 Usage in Gradio App

The integration works seamlessly with the existing Gradio interface:

1. **Upload documents** in Tab 2 (KB Management)
2. **Ask questions** in Tab 1 (Automotive Bot)
3. **Automatic routing** based on query type
4. **Real-time responses** with source attribution

## 🐛 Troubleshooting

### Common Issues

1. **"Tavily API key not found"**
   - Check `.env` file has `TAVILY_API_KEY`
   - Restart the application

2. **"Agent setup failed"**
   - Verify Tavily API key is valid
   - Check internet connection
   - Install required dependencies

3. **"No news results"**
   - Try different keywords
   - Check Tavily API quota
   - Verify query contains news-related keywords

### Debug Mode
Enable verbose logging in the agent:
```python
self.agent = initialize_agent(
    tools,
    self.llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,  # Shows agent reasoning
    handle_parsing_errors=True,
    max_iterations=3
)
```

## 📊 Performance Tips

1. **Query Optimization**: Use specific keywords for better results
2. **Caching**: Agent results are not cached (real-time)
3. **Rate Limiting**: Respect Tavily API limits
4. **Fallback**: System works without Tavily (basic mode)

## 🔮 Future Enhancements

- [ ] Add more specialized tools (price comparison, specs lookup)
- [ ] Implement result caching for common queries
- [ ] Add sentiment analysis for reviews
- [ ] Integrate with automotive APIs (CarQuery, NHTSA)
- [ ] Add image search capabilities 