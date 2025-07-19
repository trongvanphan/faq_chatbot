---
context-pack: true
type: app
name: "automotive-chatbot"
version: "1.0"
creationDate: "2025-07-19"
lastUpdated: "2025-07-19"
repository: "faq_chatbot/langgraph"
owner: "trongpv6"
tags:
- category: ai-assistant
- domain: automotive
- framework: langchain
- deployment: streamlit
relatedSystems:
- chromadb
- azure-openai
- langraph
---

# Automotive Chatbot Context Pack

## Purpose
An intelligent multi-agent conversational AI system specialized for automotive knowledge and car recommendations. The application uses a master orchestration agent to coordinate between specialized agents (recommendation, document retrieval, news search) and provides enhanced RAG capabilities with ChromaDB vector storage for automotive document processing and retrieval.

## Architecture Overview
- **Languages**: Python 3.11+
- **Frameworks**: 
  - Streamlit (Web UI)
  - LangChain (AI orchestration)
  - LangGraph (Workflow management)
- **Databases**: ChromaDB (Vector database for document embeddings)
- **AI Services**: Azure OpenAI (GPT models and embeddings)
- **Infrastructure**: Local deployment with Streamlit server
- **Key Dependencies**: 
  - `streamlit>=1.28.0` (Web interface)
  - `langchain>=0.1.0` (AI framework)
  - `langgraph>=0.0.26` (Graph-based workflows)
  - `chromadb>=0.4.0` (Vector database)
  - `markitdown>=0.0.1a2` (Enhanced document parsing)

## Core Modules

| Module/File | Purpose | Description |
|-------------|---------|-------------|
| `app.py` | Application entry point | Main Streamlit application with dual-tab interface (Chat/Knowledge Base) |
| `orchestration_agent.py` | Master orchestration | Central agent that classifies intent and routes queries to specialized agents using LangGraph workflows |
| `chat.py` | Chat interface | Streamlit chat UI that integrates with the master orchestration agent for conversational interactions |
| `knowledge_base.py` | Enhanced RAG system | Document processing, chunking, and vector storage with MarkItDown parsing and ChromaDB integration |
| `services.py` | Core services | Azure OpenAI LLM and embedding services, vector database initialization |
| `chat_state.py` | State management | TypedDict definitions for consistent state management across agents |
| `agents/recommendation/` | Car recommendation agent | Specialized agent for automotive recommendations with comprehensive car database |
| `agents/news_research_agent/` | News search agent | External news research capabilities for automotive updates |

## Specialized Agents

### Master Orchestration Agent (`orchestration_agent.py`)
- **Purpose**: Central coordinator and router
- **Key Features**:
  - Intent classification using LLM
  - Dynamic routing to specialized agents
  - LangGraph workflow orchestration
  - Extensible agent registration system
- **Routing Logic**: Classifies queries into recommendation/retrieve_docs/search_news based on keywords and context

### Car Recommendation Agent (`agents/recommendation/`)
- **Purpose**: Automotive buying advice and recommendations
- **Database**: 50+ car models with specifications (price, fuel economy, safety ratings, technology features)
- **Matching Algorithm**: Multi-criteria scoring based on budget, purpose, brand preference, priorities
- **Output**: Top 3 ranked recommendations with detailed explanations

### Document Retrieval Agent (via `knowledge_base.py`)
- **Purpose**: Knowledge base search and document retrieval
- **Features**: Enhanced similarity search with metadata, configurable result count
- **Parsing**: MarkItDown primary + fallback mechanisms (PyPDF2, docx2txt)
- **Supported Formats**: PDF, TXT, DOCX, JSON

## RAG Implementation Details

### Document Processing Pipeline
1. **Upload**: Multi-file upload via Streamlit interface
2. **Parse**: MarkItDown conversion with fallback parsing methods
3. **Chunk**: Configurable chunking (default 500 words, 50 word overlap)
4. **Embed**: Azure OpenAI text-embedding-ada-002 model
5. **Store**: ChromaDB vector storage with metadata preservation
6. **Retrieve**: Similarity search with scoring and relevance ranking

### Vector Database Schema
- **Embeddings**: Azure OpenAI embeddings (1536 dimensions)
- **Metadata Fields**: source, file_type, chunk_size, overlap
- **Storage**: Local ChromaDB instance with persistence
- **Search**: Cosine similarity with configurable k parameter

## User Experience Flow

### Chat Interface
1. User enters automotive query in Streamlit chat
2. Master orchestration agent classifies intent
3. Query routed to appropriate specialized agent
4. Agent processes request and returns structured response
5. Final answer generated and displayed with sources

### Knowledge Base Management
1. Document upload through Streamlit interface
2. Batch processing with progress feedback
3. Real-time statistics (chunks, sources, database health)
4. Search functionality with similarity scoring
5. Database management (clear, refresh operations)

## Configuration and Environment

### Required Environment Variables
```bash
AZURE_OPENAI_LLM_ENDPOINT=your_llm_endpoint
AZURE_OPENAI_LLM_API_KEY=your_llm_api_key
AZURE_OPENAI_LLM_MODEL=your_model_name
AZURE_OPENAI_EMBEDDING_ENDPOINT=your_embedding_endpoint
AZURE_OPENAI_EMBEDDING_API_KEY=your_embedding_api_key
AZURE_OPENAI_EMBEDDING_MODEL=text-embedding-ada-002
CHROMA_DB_PATH=.chromadb
```

### Deployment
- **Development**: `streamlit run app.py`
- **Port**: Default Streamlit port 8501
- **Dependencies**: Install via `pip install -r requirements.txt`

## Performance and Reliability Notes
- **SLAs**: No formal SLAs defined (development application)
- **Scaling Mechanisms**: Single-instance Streamlit deployment, ChromaDB local storage
- **Known Bottlenecks**: 
  - Large document processing can be memory-intensive
  - Azure OpenAI API rate limits may affect concurrent users
  - ChromaDB performance degrades with very large document collections
- **Resource Constraints**: Memory usage scales with document corpus size

## Testing Strategy
- **Testing Frameworks**: No formal testing framework implemented
- **Test Types**: Manual testing through Streamlit interface
- **Coverage Requirements**: None defined
- **Test Environments**: Local development environment only
- **Validation**: End-to-end testing via chat interface and knowledge base upload

## Security Considerations
- **Authentication**: No user authentication implemented
- **Authorization**: Open access to all functionality
- **Sensitive Data**: Azure OpenAI API keys stored in environment variables
- **Security Risks**: 
  - API keys exposed if environment not properly secured
  - No input validation on uploaded documents
  - No rate limiting on API calls
  - ChromaDB data stored locally without encryption

## Past Incidents/Gotchas

### Major Issue: ChromaDB Integration Challenges
- **Problem**: Initial integration with ChromaDB faced compatibility issues with different versions
- **Symptoms**: Import errors, collection access failures, persistence issues
- **Resolution**: 
  - Standardized on ChromaDB >= 0.4.0
  - Added proper error handling and fallback mechanisms
  - Implemented connection verification in services.py
- **Prevention**: Added comprehensive error handling and version pinning in requirements.txt

### Known Edge Cases
- **Empty Document Upload**: Application handles gracefully with user feedback
- **Unsupported File Types**: Clear error messages and type validation
- **API Rate Limiting**: May cause delays, no automatic retry implemented
- **Large File Processing**: Memory constraints with files > 10MB

### Debugging Tips
- Check ChromaDB initialization logs for connection issues
- Verify Azure OpenAI endpoint configuration if embeddings fail
- Monitor Streamlit console for detailed error messages
- Use `st.write()` for debugging state variables in development

## Copilot/LLM Usage Notes

### Naming Conventions
- **Agents**: `{purpose}_agent.py` pattern (e.g., `recommendation_agent.py`)
- **Functions**: Snake_case with descriptive names (`classify_intent`, `route_user_input`)
- **Classes**: PascalCase with descriptive suffixes (`MasterOrchestrationAgent`, `KnowledgeBaseManager`)
- **Constants**: UPPER_CASE for configuration values (`VALID_PURPOSES`, `MARKITDOWN_AVAILABLE`)

### Style Guide
- **Documentation**: Comprehensive docstrings for all classes and methods
- **Error Handling**: Try-catch blocks with logging for all external API calls
- **State Management**: Use TypedDict for consistent state across agents
- **UI Components**: Streamlit components with descriptive labels and help text

### Safe Generation Areas
- **New Agent Creation**: Follow existing pattern in `agents/` directory
- **UI Enhancements**: Streamlit components can be safely modified/extended
- **Utility Functions**: Helper functions in existing modules
- **Configuration**: Environment variable additions and configuration updates

### Review-Required Areas
- **Agent Routing Logic**: Changes to intent classification require careful testing
- **ChromaDB Integration**: Vector database operations need validation
- **Azure OpenAI Calls**: API integration changes need cost and rate limit consideration
- **State Management**: Changes to `ChatState` structure affect all agents

## Extension Points

### Adding New Agents
1. Create new agent module in `agents/` directory
2. Implement agent function with `ChatState` input/output
3. Register agent using `master_agent.add_agent()` method
4. Update intent classification keywords and descriptions

### Supported Agent Types
- **Recommendation Agents**: Product/service recommendations
- **Retrieval Agents**: Document search and knowledge base queries
- **Research Agents**: External API integration for current information
- **Analysis Agents**: Data processing and insight generation

### Integration Patterns
- **State-based Communication**: All agents use standardized `ChatState`
- **LangGraph Workflows**: New workflows can be defined for complex multi-step processes
- **External APIs**: Integration via agent functions with proper error handling
- **Database Extensions**: Additional vector stores can be integrated alongside ChromaDB
