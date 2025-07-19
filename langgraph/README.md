# Multi-Agent Chatbot with Enhanced RAG

This project features a sophisticated multi-agent system with enhanced RAG (Retrieval-Augmented Generation) capabilities, powered by a master orchestration agent that coordinates multiple specialized agents.

## 🚀 **New RAG Features**

### **Enhanced Document Processing**
- **MarkItDown Integration**: Primary parsing with Microsoft's MarkItDown for superior document conversion
- **Fallback Mechanisms**: Robust fallback to PyPDF2, docx2txt when MarkItDown unavailable
- **Multi-format Support**: PDF, TXT, DOCX, JSON with intelligent parsing
- **Configurable Chunking**: Adjustable chunk size and overlap for optimal retrieval

### **Advanced Knowledge Base Management**
- **Smart File Processing**: Batch upload with detailed processing feedback
- **Enhanced Search**: Similarity search with scoring and metadata
- **Database Statistics**: Real-time stats on chunks, sources, and database health
- **Robust Error Handling**: Graceful degradation and detailed error reporting

## 📁 Project Structure

```
langgraph/
├── agents/                          # 🆕 Specialized agents directory
│   ├── __init__.py                  # Agents package initialization
│   └── recommendation/              # Car recommendation agent
│       ├── __init__.py              # Package initialization
│       ├── car_database.py          # Comprehensive car database
│       └── recommendation_agent.py  # Smart recommendation logic
├── chat.py                          # 🔄 Updated Streamlit UI with orchestration
├── orchestration_agent.py           # 🆕 Master orchestration agent
├── knowledge_base.py                # 🆕 Enhanced RAG with MarkItDown support
├── services.py                      # 🔄 Updated to use enhanced knowledge base
├── chat_state.py                    # State management
├── app.py                           # Application entry point
├── requirements.txt                 # 🆕 Complete dependency list
└── README.md                        # 🔄 Updated documentation
```

## 🤖 Agent Architecture

### Master Orchestration Agent (`orchestration_agent.py`)
- **Role**: Central coordinator that routes user queries to appropriate specialized agents
- **Features**:
  - Intelligent intent classification
  - Dynamic routing to specialized agents
  - Workflow orchestration using LangGraph
  - Error handling and fallback mechanisms
  - Extensible architecture for adding new agents

### Car Recommendation Agent (`agents/recommendation/`)
- **Role**: Specialized agent for car buying advice and recommendations
- **Features**:
  - Comprehensive car database with 9+ vehicle models
  - Intelligent criteria extraction from natural language
  - Multi-factor matching algorithm (budget, purpose, brand, etc.)
  - Detailed recommendation explanations
  - Scoring and ranking system

#### Car Database Features:
- **Complete Specifications**: Price, fuel economy, size, purposes, priorities
- **Brand Origins**: Japanese, Korean, German, American, Electric
- **Safety Ratings**: NHTSA and IIHS ratings
- **Technology Features**: Infotainment, safety systems, connectivity
- **Filtering Methods**: By budget, purpose, brand, body type

## 🚀 Key Improvements

### 1. **Modular Architecture**
- Each agent is self-contained and independently testable
- Clear separation of concerns
- Easy to add new specialized agents

### 2. **Intelligent Routing**
- Advanced intent classification using LLM
- Context-aware agent selection
- Fallback mechanisms for unknown intents

### 3. **Enhanced Car Recommendations**
- Sophisticated matching algorithm
- Natural language criteria extraction
- Comprehensive car database
- Detailed explanations and comparisons

### 4. **Scalable Design**
- Easy to add new agents via `master_agent.add_agent()`
- Standardized agent interface
- Centralized state management

## 🎯 Available Agents

### 1. **Enhanced Document Retrieval Agent** 🔍
**Triggers**: Knowledge base queries, document search, information lookup
**Features**:
- Advanced similarity search with scoring
- Intelligent document chunking and retrieval
- Metadata-rich search results
- Fallback mechanisms for reliability

**Examples**:
- *"Tell me about maintenance schedules"*
- *"What information do you have about warranty coverage?"*
- *"Search for troubleshooting guides"*

### 2. **Car Recommendation Agent** 🚗
**Triggers**: Car-related queries, buying advice, recommendations
**Features**:
- Comprehensive car database with 9+ models
- Multi-criteria matching (budget, purpose, brand, etc.)
- Intelligent scoring and ranking system
- Detailed explanations and comparisons

**Examples**:
- *"I need a family car under $35,000"*
- *"What's the best fuel-efficient car for daily commuting?"*
- *"Recommend a reliable business car"*

### 3. **News Search Agent** 📰
**Triggers**: Current events, news, automotive updates
**Examples**:
- *"Latest electric vehicle news"*
- *"What's new in automotive technology?"*
- *"Recent car industry updates"*

## 🛠️ **Enhanced RAG Capabilities**

### **Document Processing Pipeline**
1. **Upload**: Multi-file upload with size and type validation
2. **Parse**: MarkItDown primary + fallback parsing methods
3. **Chunk**: Configurable chunking with overlap control
4. **Embed**: Azure OpenAI embeddings with batch processing
5. **Store**: ChromaDB vector storage with metadata
6. **Search**: Advanced similarity search with scoring

### **Supported File Formats**
- **PDF**: MarkItDown → PyPDF2 fallback
- **TXT**: MarkItDown → Direct read fallback  
- **DOCX**: MarkItDown → docx2txt fallback
- **JSON**: Smart parsing with structured data conversion to readable text

### **Knowledge Base Features**
- **Real-time Statistics**: Track chunks, sources, database health
- **Advanced Search**: Similarity search with configurable results
- **Metadata Enrichment**: Source tracking, processing details
- **Database Management**: Clear, refresh, and maintain operations

## 🔧 Usage

### Running the Application
```bash
streamlit run app.py
```

### Adding New Agents
```python
from orchestration_agent import master_agent

def my_custom_agent(state: ChatState) -> ChatState:
    # Your agent logic here
    return {**state, "answer": "Custom response"}

master_agent.add_agent(
    name="custom_agent",
    function=my_custom_agent,
    description="Handles custom queries",
    keywords=["custom", "special", "unique"]
)
```

## 🏗️ Technical Architecture

### State Management
- Uses `ChatState` TypedDict for consistent state across agents
- Maintains conversation history and context
- Supports both document-based and direct responses

### LangGraph Integration
- Workflow orchestration using directed graphs
- Conditional routing based on intent classification
- Error handling and recovery paths

### Agent Communication
- Standardized input/output interface
- State-based data sharing
- Clean separation between routing and execution

## 🔮 Future Extensions

### Planned Agents
1. **Insurance Agent**: Car insurance recommendations and comparisons
2. **Financing Agent**: Loan and financing options
3. **Maintenance Agent**: Service schedules and maintenance advice
4. **Reviews Agent**: Customer reviews and ratings analysis

### Architecture Enhancements
- Agent performance monitoring
- Caching layer for common queries
- Multi-language support
- Integration with external APIs

## 📊 Benefits

1. **Better User Experience**: More accurate responses through specialized expertise
2. **Maintainability**: Modular code structure with clear responsibilities
3. **Scalability**: Easy to add new capabilities without affecting existing agents
4. **Testability**: Each agent can be tested independently
5. **Performance**: Efficient routing reduces unnecessary processing
6. **Extensibility**: Plugin-like architecture for new agents
