# Multi-Agent Chatbot Architecture

This project has been restructured to use a master orchestration agent that coordinates multiple specialized agents.

## 📁 Project Structure

```
langgraph/
├── agents/                          # Specialized agents directory
│   ├── __init__.py                  # Agents package initialization
│   └── recommendation/              # Car recommendation agent
│       ├── __init__.py              # Package initialization
│       ├── car_database.py          # Comprehensive car database
│       └── recommendation_agent.py  # Smart recommendation logic
├── chat.py                          # Main Streamlit UI
├── orchestration_agent.py           # Master orchestration agent
├── chat_state.py                    # State management
├── services.py                      # Azure LLM and vector DB services
├── knowledge_base.py                # Knowledge base utilities
└── app.py                           # Application entry point
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

### 1. Recommendation Agent
**Triggers**: Car-related queries, buying advice, recommendations
**Examples**:
- "I need a car recommendation for my family of 4 with a budget of $35,000"
- "What car should I buy for daily commuting that's fuel efficient?"
- "Recommend a reliable car for business use under $50,000"

### 2. Document Retrieval Agent
**Triggers**: Knowledge base queries, document search
**Examples**:
- "Tell me about maintenance schedules"
- "What information do you have about warranty coverage?"
- "Search for troubleshooting guides"

### 3. News Search Agent
**Triggers**: Current events, news, updates
**Examples**:
- "Show me latest automotive news"
- "What's new in electric vehicles?"
- "Recent updates in car technology"

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
