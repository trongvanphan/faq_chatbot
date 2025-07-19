---
context-pack: true
type: app
name: "faq-chatbot"
version: "1.0"
creationDate: "2025-07-18"
lastUpdated: "2025-07-18"
repository: "https://github.com/trongvanphan/faq_chatbot"
owner: "trongvanphan"
# Optional metadata
tags:
- language: python
- framework: gradio
- ai: langchain
- vectordb: chromadb
- ui: gradio
relatedSystems:
- openai-api
- tavily-api
---

# FAQ Chatbot Context Pack

## Purpose
An intelligent automotive AI consultant application that combines local knowledge base search, real-time web search, and multi-tier fallback systems to provide comprehensive automotive advice with transparent reasoning processes. The system uses ChromaDB for vector storage, LangChain for agent orchestration, and Gradio for the web interface.

## Architecture Overview
- **Languages**: Python 3.11+
- **Frameworks**: Gradio (UI), LangChain (AI agents), ChromaDB (vector database)
- **Databases**: ChromaDB (persistent vector storage), FAISS (fallback vector operations)
- **Infrastructure**: Local file system storage, environment-based configuration
- **Key Dependencies**: OpenAI API, Tavily API (optional), tenacity (retry logic)

## Core Modules

| Module/File | Purpose | Description |
|-------------|---------|-------------|
| app.py | Main UI application | Gradio interface with multiple chat tabs and knowledge base management |
| automotive_bot.py | AI agent controller | Main intelligence system with LangChain agents, reasoning display, and fallback logic |
| kb_manager.py | Knowledge base operations | ChromaDB document upload, processing, and vector search capabilities |
| context_manager.py | Conversation memory | Multi-turn conversation management with context summarization |
| faq_bot.py | Function calling bot | OpenAI function calling implementation for structured queries |
| faq_data.py | Static data store | FAQ content, car database, and OpenAI function definitions |
| setup.sh | Environment setup | Automated virtual environment and dependency installation |

## Performance and Reliability Notes
- **SLAs**: No formal SLAs defined, designed for development/demo use
- **Scaling Mechanisms**: Single-instance application, ChromaDB supports concurrent queries
- **Known Bottlenecks**: OpenAI API rate limits, embedding generation for large documents
- **Resource Constraints**: Local storage for ChromaDB, memory usage scales with conversation history

## Testing Strategy
- **Testing Frameworks**: No formal testing framework implemented
- **Test Types**: Manual testing through Gradio interface
- **Coverage Requirements**: No formal coverage requirements
- **Test Environments**: Local development environment only

## Security Considerations
- **Authentication**: No authentication system implemented
- **Authorization**: No authorization controls
- **Sensitive Data**: API keys stored in environment variables, conversation history in memory only
- **Security Risks**: No input sanitization, direct API key exposure in logs possible, no rate limiting on UI

## Past Incidents/Gotchas
- **Import Fallbacks**: Multiple try/except blocks handle missing dependencies gracefully (e.g., TavilySearchResults import variations)
- **ChromaDB Collection Management**: Collections must exist before operations; auto-created if missing but can cause initial setup issues
- **Agent Reasoning Display**: Only shows for LangChain agent mode, not for direct knowledge base hits or simple chat fallbacks
- **Environment Variable Dependencies**: Application degrades gracefully without TAVILY_API_KEY but requires OPENAI_API_KEY to function

## Copilot/LLM Usage Notes
- **Naming Conventions**: 
  - Functions use snake_case (e.g., `get_automotive_response`, `upload_document_to_kb`)
  - Classes use PascalCase (e.g., `AgentCallbackHandler`, `ConversationManager`)
  - Constants use UPPER_CASE (e.g., `MODEL`, `TEMPERATURE`, `FAQ_LIST`)
- **Style Guide**: 
  - Comprehensive docstrings for all public functions
  - Type hints used consistently throughout codebase
  - Error handling with try/except blocks and graceful degradation
- **Safe Generation Areas**: 
  - Adding new FAQ entries to `faq_data.py`
  - Creating new Gradio interface components in `app.py`
  - Extending function definitions in `FUNCTION_DEFINITIONS`
- **Review-Required Areas**: 
  - LangChain agent configuration and tool definitions
  - ChromaDB collection operations and embedding logic
  - OpenAI API integration and error handling

## Technical Architecture Details

### Query Processing Flow
```
User Input → automotive_bot.py::get_automotive_response() → 
  1. Knowledge Base Search (ChromaDB)
  2. LangChain Agent Mode (with Tavily web search)
  3. Direct OpenAI Fallback
```

### Key Integration Points
- **ChromaDB**: Persistent storage at `./chroma_db` with `automotive_knowledge` collection
- **OpenAI API**: Used for embeddings (`text-embedding-3-small`) and chat completions
- **Tavily API**: Optional web search capability for real-time automotive news
- **Gradio Interface**: Multi-tab UI with chat history and file upload capabilities

### Configuration Management
- Environment variables in `.env` file with fallback defaults
- Retry configuration for API calls using tenacity library
- Model selection via `MODEL_NAME` environment variable (default: "GPT-4o-mini")

### Memory and Context Management
- Conversation history maintained in `ConversationManager` class
- Context summarization for token management
- Window-based memory with configurable history length (default: 10 exchanges)

### Error Handling Patterns
- Graceful degradation when dependencies unavailable
- Comprehensive try/catch blocks with user-friendly error messages
- Fallback modes when external APIs fail
- Debug logging throughout request lifecycle

## Development Workflow
- **Setup**: Run `./setup.sh` to create virtual environment and install dependencies
- **Configuration**: Copy `.env.example` to `.env` and add required API keys
- **Run**: Execute `python app.py` to start Gradio interface on localhost:7860
- **Debug**: Monitor terminal output for detailed request/response logging

## Knowledge Base Management
- **Document Upload**: Supports PDF, TXT, and Markdown files
- **Text Processing**: Recursive character text splitter with 1000 char chunks, 200 char overlap
- **Vector Storage**: ChromaDB with OpenAI embeddings for semantic search
- **Search Capabilities**: Similarity search with configurable result count and score thresholds
