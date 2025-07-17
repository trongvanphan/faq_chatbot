# AI Automotive Consultant - Copilot Instructions

## 🎯 System Architecture

This is a **multi-tier intelligent fallback system** with transparent AI reasoning:

**Query Flow**: `KB Search → Agent Mode → Direct Chat`
- `automotive_bot.py::get_automotive_response()` - main routing logic
- ChromaDB vector search first (fast path)
- LangChain agent activation for news/complex queries
- Direct OpenAI fallback for simple conversations

## 🔧 Core Components

### Primary Files
- `automotive_bot.py` - Main controller with 3-tier fallback system
- `kb_manager.py` - ChromaDB RAG operations (`automotive_knowledge` collection)
- `context_manager.py` - Multi-turn conversation memory
- `app.py` - Gradio UI with 5 specialized interfaces
- `faq_data.py` - Static data & OpenAI function definitions

### Key Classes
- `AutomotiveBot` - Main controller with intelligent routing
- `AgentCallbackHandler(BaseCallbackHandler)` - Captures reasoning process from LangChain agents
- `CustomChromaRetriever(BaseRetriever)` - LangChain-compatible ChromaDB interface
- `KnowledgeBaseManager` - Document processing and vector operations

## 🧠 Intelligent Reasoning System

**Reasoning Display Logic** (automotive_bot.py lines 120-160):
- Shows for: LangChain agent mode, web search, complex queries
- Hidden for: Direct KB hits, simple chat, function calling
- `AgentCallbackHandler.get_thinking_process()` formats for UI

**Query Classification** (automotive_bot.py lines 450-480):
```python
# News keywords trigger agent mode
news_keywords = ["tin tức", "news", "mới nhất", "latest", "đánh giá", "review"]
if any(keyword in user_input.lower() for keyword in news_keywords):
    return handle_agent_mode(user_input)  # Shows reasoning

# KB search first (no reasoning display)
kb_response = try_knowledge_base_search(user_input)
```

## 🔄 Development Patterns

### Error Handling Pattern
```python
try:
    # Main operation
    return primary_function()
except ImportError as e:
    print(f"⚠️ Dependencies not available: {e}")
    return fallback_mode()
except Exception as e:
    print(f"❌ Error: {e}")
    return graceful_fallback()
```

### Environment Setup
All modules use: `load_dotenv()` → `os.getenv("VAR", "default")`
Required: `OPENAI_API_KEY`
Optional: `TAVILY_API_KEY` (system works without web search)

### ChromaDB Integration
- Collection name: `"automotive_knowledge"`
- Persistent storage: `./chroma_db`
- Embedding model: `text-embedding-3-small`
- Chunk size: 1000 chars, overlap: 200

## 🎨 UI Architecture (app.py)

**5 Gradio Tabs**:
1. **AI Automotive Consultant** - Main interface with reasoning display
2. **Knowledge Base Manager** - Document upload and RAG management  
3. **Context-Aware Bot** - Multi-turn conversation memory
4. **Function Calling Bot** - OpenAI structured functions
5. **Simple FAQ Bot** - Basic responses without function calling

**Interface Pattern**:
```python
def interface_function(user_input, history):
    try:
        answer = get_response_function(user_input)
        # Standard debugging
        print(f"🎯 UI Request: {user_input}")
        print(f"✅ Response: {len(answer)} chars")
    except Exception as e:
        answer = f"❌ Lỗi: {str(e)}"
    
    history = history or []
    history.append({"role": "user", "content": user_input})
    history.append({"role": "assistant", "content": answer})
    return "", history
```

## 🛠️ Critical Commands

**Setup**: `./setup.sh` or manual `pip install -r requirements.txt`
**Run**: `python app.py` (starts Gradio on localhost:7860)
**Debug**: Check `print()` statements in terminal for detailed flow
**Reset KB**: Delete `./chroma_db` directory to start fresh

## 🔍 Key Implementation Details

### Agent Tools (automotive_bot.py lines 300-350)
- `tavily_search` - Web search for current automotive news
- `knowledge_base_search` - Local ChromaDB query tool
- Agent automatically selects tools based on query content

### Fallback Chain Logic
1. **KB Search**: `CustomChromaRetriever` → similarity search → direct response
2. **Agent Mode**: Tool selection → reasoning capture → formatted output  
3. **Direct Chat**: Simple OpenAI API call → basic response

### Memory Management
- `ConversationBufferWindowMemory(k=5)` - Last 5 exchanges
- Context-aware prompts include conversation history
- Reference resolution ("it", "that car") through context

## 🚨 Common Gotchas

- **Import Fallbacks**: All modules have try/except for optional dependencies
- **Agent Reasoning**: Only shows for LangChain agent mode, not KB hits
- **ChromaDB Collection**: Must exist before KB operations, auto-created if missing
- **Vietnamese Language**: All user-facing text in Vietnamese, prompts bilingual
- **API Key Priority**: EMBEDDING_KEY falls back to OPENAI_API_KEY if not set
from langchain_community.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType

# Local imports
from context_manager import get_contextual_response
from kb_manager import KnowledgeBaseManager
```

#### 2. **Environment Configuration**
```python
# Always load environment variables at module start
load_dotenv()

# Configuration constants at top of file
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
MODEL = os.getenv("MODEL_NAME", "gpt-4o-mini")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.5"))
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
```

#### 3. **Error Handling Pattern**
```python
def robust_function():
    """Function with proper error handling"""
    try:
        # Main logic here
        result = perform_operation()
        return result
    except ImportError as e:
        print(f"⚠️ Dependency not available: {e}")
        return None
    except Exception as e:
        print(f"❌ Error in {__name__}: {e}")
        return fallback_response()
```

#### 4. **Logging & Debugging**
```python
def debug_function(data):
    """Always include debugging information"""
    print(f"🔍 Debug: Processing {type(data)} with {len(data)} items")
    
    # Process data
    result = process(data)
    
    print(f"✅ Success: Generated {len(result)} results")
    return result
```

### 🏛️ Class Design Patterns

#### 1. **Callback Handler Pattern**
```python
class AgentCallbackHandler(BaseCallbackHandler):
    """Custom callback for capturing agent reasoning"""
    
    def __init__(self):
        super().__init__()
        self.actions = []
        self.observations = []
        self.current_step = 0
    
    def on_agent_action(self, action, **kwargs):
        """Capture agent actions"""
        self.current_step += 1
        self.actions.append({
            "step": self.current_step,
            "tool": action.tool,
            "tool_input": action.tool_input,
            "log": action.log
        })
    
    def get_thinking_process(self):
        """Format reasoning for display"""
        # Implementation details...
        pass
```

#### 2. **Custom Retriever Pattern**
```python
class CustomChromaRetriever(BaseRetriever):
    """LangChain-compatible ChromaDB retriever"""
    
    def __init__(self, collection, embeddings):
        super().__init__()
        self._collection = collection
        self._embeddings = embeddings
        
    def _get_relevant_documents(self, query, run_manager=None):
        """Implement required LangChain method"""
        query_embedding = self._embeddings.embed_query(query)
        results = self._collection.query(
            query_embeddings=[query_embedding], 
            n_results=4
        )
        # Convert to LangChain Documents
        return documents
```

#### 3. **Manager Class Pattern**
```python
class KnowledgeBaseManager:
    """Encapsulate KB operations"""
    
    def __init__(self):
        self.embeddings = None
        self.chroma_collection = None
        self.initialize_components()
    
    def initialize_components(self):
        """Setup with error handling"""
        try:
            if dependencies_available():
                self._setup_components()
            else:
                print("⚠️ Running in limited mode")
        except Exception as e:
            print(f"Error initializing: {e}")
```

## 🔧 Component Implementation Guidelines

### 🤖 Automotive Bot (`automotive_bot.py`)

**Key Responsibilities:**
- Query classification and routing
- LangChain agent orchestration
- Reasoning process capture
- Intelligent fallback handling

**Implementation Pattern:**
```python
def get_automotive_response(user_input: str) -> str:
    """Main entry point with intelligent routing"""
    
    # 1. Initialize components
    callback_handler = AgentCallbackHandler()
    
    # 2. Try knowledge base first (fast path)
    kb_response = try_knowledge_base_search(user_input)
    if has_sufficient_info(kb_response):
        return format_kb_response(kb_response)
    
    # 3. Use agent for complex queries
    if should_use_agent(user_input):
        return handle_agent_mode(user_input, callback_handler)
    
    # 4. Fallback to direct chat
    return handle_direct_chat_fallback(user_input)
```

### 📚 Knowledge Base Manager (`kb_manager.py`)

**Key Responsibilities:**
- Document processing and chunking
- ChromaDB operations
- Embedding generation
- Search and retrieval

**Implementation Pattern:**
```python
class KnowledgeBaseManager:
    def upload_document(self, file_path: str, description: str = ""):
        """Document upload with proper processing"""
        
        # 1. Extract text
        text_content = self._extract_text(file_path)
        
        # 2. Intelligent chunking
        chunks = self._chunk_text(text_content)
        
        # 3. Generate embeddings
        embeddings = self._generate_embeddings(chunks)
        
        # 4. Store in ChromaDB with metadata
        self._store_in_db(chunks, embeddings, metadata)
    
    def _chunk_text(self, text: str) -> List[str]:
        """Smart chunking preserving semantic coherence"""
        return self.text_splitter.split_text(text)
```

### 🧠 Context Manager (`context_manager.py`)

**Key Responsibilities:**
- Conversation history management
- Context-aware prompt building
- Memory optimization
- Reference resolution

**Implementation Pattern:**
```python
class ConversationManager:
    def __init__(self, max_history: int = 10):
        self.conversation_history = []
        self.max_history = max_history
        self.context_summary = ""
    
    def add_message(self, role: str, content: str):
        """Add message with automatic history management"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.conversation_history.append(message)
        self._manage_history_size()
    
    def get_context_messages(self) -> List[Dict]:
        """Build context-aware message list"""
        system_prompt = self._build_context_aware_system_prompt()
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add relevant conversation history
        for msg in self.conversation_history:
            if msg["role"] != "system":
                messages.append({
                    "role": msg["role"], 
                    "content": msg["content"]
                })
        
        return messages
```

## 🎨 UI Development (`app.py`)

### 🖼️ Gradio Interface Patterns

**Multi-Tab Structure:**
```python
def create_automotive_consultant_tab():
    """Main AI consultant with reasoning display"""
    with gr.Column():
        chatbot = gr.Chatbot(
            value=[],
            elem_id="automotive-chatbot",
            height=500,
            show_copy_button=True
        )
        
        with gr.Row():
            msg = gr.Textbox(
                placeholder="Hỏi về xe hơi...",
                lines=2,
                max_lines=5
            )
            send_btn = gr.Button("Gửi", variant="primary")
        
        clear_btn = gr.Button("🔄 Reset Conversation")
        
    # Event handlers
    send_btn.click(
        automotive_bot_interface,
        inputs=[msg, chatbot],
        outputs=[msg, chatbot]
    )
    
    return [chatbot, msg, send_btn, clear_btn]
```

**Interface Function Pattern:**
```python
def automotive_bot_interface(user_input, history):
    """Standard interface function for Gradio"""
    try:
        print(f"🎯 UI Request: {user_input}")
        
        # Get AI response
        answer = get_automotive_response(user_input)
        
        # Debug output
        print("\n" + "="*30 + " UI RESPONSE START " + "="*30)
        print(answer)
        print("="*31 + " UI RESPONSE END " + "="*31 + "\n")
        
        # Get status information
        context_info = get_automotive_info()
        status_msg = f"✅ {context_info['status']} | {context_info['message_count']} messages"
        
    except Exception as e:
        answer = f"❌ Lỗi: {str(e)}"
        print(f"❌ UI Error: {e}")
    
    # Update history
    history = history or []
    history.append({"role": "user", "content": user_input})
    history.append({"role": "assistant", "content": answer})
    
    return "", history
```

## 🚀 Advanced Features Implementation

### 🔍 Agent Tool Development

**Tool Creation Pattern:**
```python
from langchain.tools import Tool

def create_knowledge_base_tool():
    """Create KB search tool for agent"""
    def search_kb(query: str) -> str:
        """Search knowledge base"""
        try:
            results = kb_manager.search_kb(query, top_k=3)
            if results:
                return f"Found {len(results)} relevant documents: {results}"
            return "No relevant information found in knowledge base."
        except Exception as e:
            return f"Error searching KB: {e}"
    
    return Tool(
        name="knowledge_base_search",
        description="Search the local automotive knowledge base for specific information about cars, specifications, prices, and maintenance.",
        func=search_kb
    )

def create_web_search_tool():
    """Create Tavily web search tool"""
    if not TAVILY_API_KEY:
        return None
        
    return TavilySearchResults(
        api_key=TAVILY_API_KEY,
        max_results=5,
        search_depth="advanced"
    )
```

### 🧠 Reasoning Display Implementation

**Thought Process Extraction:**
```python
def get_thinking_process(self):
    """Extract and format agent reasoning"""
    if not self.actions:
        return ""
    
    process = "🧠 **Quá trình suy nghĩ của Bot:**\n\n"
    
    for i, action in enumerate(self.actions, 1):
        # Extract thought using regex
        thought_match = re.search(
            r'Thought:\s*(.*?)(?:\nAction:|$)', 
            action["log"], 
            re.DOTALL
        )
        
        thought = thought_match.group(1).strip() if thought_match else \
                 f"Cần sử dụng {action['tool']} để tìm thông tin"
        
        process += f"**💭 Bước {i} - Suy nghĩ:**\n{thought}\n\n"
        process += f"**🔧 Hành động:** `{action['tool']}`\n"
        process += f"**📝 Input:** `{action['tool_input']}`\n\n"
        
        # Add observation if available
        obs = next((o for o in self.observations if o["step"] == action["step"]), None)
        if obs:
            process += f"**👀 Quan sát:**\n{obs['output'][:400]}...\n\n---\n\n"
    
    return process
```

## 📊 Data Management

### 🗃️ Static Data Structure (`faq_data.py`)

```python
# Organize data in clear dictionaries
CAR_DATABASE = {
    "sedan": ["Honda Civic", "Toyota Camry", "BMW 3 Series"],
    "suv": ["Honda CR-V", "Toyota RAV4", "Mazda CX-5"],
    "electric": ["VinFast VF8", "Tesla Model 3", "BMW iX3"]
}

MAINTENANCE_SCHEDULE = {
    "oil_change": {
        "interval": "5000-10000 km", 
        "description": "Thay dầu động cơ và lọc dầu"
    },
    "brake_inspection": {
        "interval": "20000-30000 km", 
        "description": "Kiểm tra phanh"
    }
}

# Function definitions for OpenAI
FUNCTION_DEFINITIONS = [
    {
        "name": "search_faq",
        "description": "Tìm kiếm trong cơ sở dữ liệu FAQ",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Từ khóa tìm kiếm"
                }
            },
            "required": ["query"]
        }
    }
]
```

## 🔒 Security & Best Practices

### 🛡️ Environment Variable Management

```python
# Never hardcode API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

# Provide sensible defaults
MODEL = os.getenv("MODEL_NAME", "gpt-4o-mini")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.5"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1000"))
```

### 🚨 Error Handling Standards

```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(openai.RateLimitError)
)
def robust_api_call():
    """API call with retry mechanism"""
    try:
        response = openai_client.chat.completions.create(...)
        return response.choices[0].message.content
    except openai.RateLimitError:
        raise  # Will be retried
    except Exception as e:
        print(f"❌ API Error: {e}")
        return "Xin lỗi, tôi gặp lỗi kỹ thuật. Vui lòng thử lại."
```

### 💾 Resource Management

```python
def efficient_embedding_generation(texts: List[str]) -> List[List[float]]:
    """Batch process embeddings efficiently"""
    batch_size = 100
    all_embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        embeddings = embedding_model.embed_documents(batch)
        all_embeddings.extend(embeddings)
        
        # Rate limiting
        time.sleep(0.1)
    
    return all_embeddings
```

## 🧪 Testing & Quality Assurance

### 🔍 Testing Patterns

```python
def test_automotive_response():
    """Test main response function"""
    test_queries = [
        "Gợi ý xe SUV",  # Should use KB
        "Tin tức Tesla mới nhất",  # Should use agent
        "Chào bạn"  # Should use direct chat
    ]
    
    for query in test_queries:
        response = get_automotive_response(query)
        assert response is not None
        assert len(response) > 0
        print(f"✅ {query}: {len(response)} chars")

def test_knowledge_base():
    """Test KB operations"""
    kb_manager = KnowledgeBaseManager()
    results = kb_manager.search_kb("Honda Civic", top_k=3)
    assert isinstance(results, list)
    print(f"✅ KB Search: {len(results)} results")
```

### 📈 Performance Monitoring

```python
def monitor_response_time(func):
    """Decorator for monitoring performance"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        print(f"⏱️ {func.__name__}: {end_time - start_time:.2f}s")
        return result
    return wrapper

@monitor_response_time
def get_automotive_response(user_input: str) -> str:
    # Implementation...
    pass
```

## 🚀 Deployment & Production

### 📦 Dependencies Management

```python
# requirements.txt structure
"""
# Core dependencies
openai>=1.0.0
gradio>=4.0.0
python-dotenv>=1.0.0

# AI/ML stack
langchain>=0.1.0
langchain-community>=0.0.20
chromadb>=0.4.0
faiss-cpu>=1.7.4

# Utilities
tenacity>=8.0.0
tiktoken>=0.5.0
PyPDF2>=3.0.0
"""
```

### 🏃‍♂️ Startup Script

```bash
#!/bin/bash
# setup.sh
set -e

echo "🚀 Setting up AI Automotive Consultant..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Create environment file
if [ ! -f .env ]; then
    cp .env.example .env
    echo "📝 Please edit .env file with your API keys"
fi

# Create data directories
mkdir -p chroma_db
mkdir -p uploads

echo "✅ Setup complete! Run: python app.py"
```

## 🎯 Extension Guidelines

### 🔌 Adding New Interfaces

```python
def create_new_interface_tab():
    """Template for new interface"""
    with gr.Column():
        # UI components
        interface_chatbot = gr.Chatbot()
        interface_input = gr.Textbox()
        
        # Event handling
        interface_input.submit(
            new_interface_function,
            inputs=[interface_input, interface_chatbot],
            outputs=[interface_input, interface_chatbot]
        )
    
    return [interface_chatbot, interface_input]

def new_interface_function(user_input, history):
    """Handler for new interface"""
    # Implement specific logic
    response = process_with_new_method(user_input)
    
    # Standard response format
    history = history or []
    history.append({"role": "user", "content": user_input})
    history.append({"role": "assistant", "content": response})
    return "", history
```

### 🛠️ Adding New Tools

```python
def create_custom_tool():
    """Template for custom agent tool"""
    def tool_function(input_data: str) -> str:
        """Implement tool logic"""
        try:
            # Process input
            result = process_data(input_data)
            return f"Tool result: {result}"
        except Exception as e:
            return f"Tool error: {e}"
    
    return Tool(
        name="custom_tool",
        description="Description for agent to understand when to use this tool",
        func=tool_function
    )
```

## 📚 Documentation Standards

### 📝 Function Documentation

```python
def complex_function(param1: str, param2: List[str], param3: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Brief description of what the function does.
    
    Args:
        param1: Description of first parameter
        param2: Description of second parameter  
        param3: Optional parameter description
    
    Returns:
        Dictionary containing result data with keys:
        - 'status': Success/error status
        - 'data': Processed results
        - 'metadata': Additional information
    
    Raises:
        ValueError: When param1 is empty
        ConnectionError: When API is unavailable
    
    Example:
        >>> result = complex_function("query", ["item1", "item2"])
        >>> print(result['status'])
        'success'
    """
    # Implementation...
    pass
```

### 📖 Module Documentation

```python
"""
automotive_bot.py - AI Automotive Consultant Core Module

This module implements the main AI consultation system with:
- LangChain agent orchestration
- Transparent reasoning display
- Intelligent query routing
- Multi-tier fallback system

Key Classes:
    AgentCallbackHandler: Captures agent reasoning process
    CustomChromaRetriever: LangChain-compatible ChromaDB interface
    AutomotiveBot: Main controller class

Main Functions:
    get_automotive_response(): Entry point for AI consultation
    handle_agent_mode(): LangChain agent processing
    handle_direct_chat_fallback(): Direct LLM fallback

Dependencies:
    - openai: LLM and embedding APIs
    - langchain: Agent framework
    - chromadb: Vector database
    - tavily: Web search API
"""
```

## 🎉 Final Notes

### ✅ Code Quality Checklist

- [ ] **Error Handling**: All functions have try/catch blocks
- [ ] **Logging**: Debug prints for troubleshooting
- [ ] **Type Hints**: Function parameters and returns typed
- [ ] **Documentation**: Docstrings for all public functions
- [ ] **Environment**: No hardcoded secrets or URLs
- [ ] **Fallbacks**: Graceful degradation when APIs fail
- [ ] **Testing**: Core functions have test cases
- [ ] **Performance**: Efficient resource usage

### 🚀 Development Workflow

1. **Setup**: Use `setup.sh` for consistent environment
2. **Development**: Follow modular patterns and error handling
3. **Testing**: Test each component individually
4. **Integration**: Verify end-to-end functionality
5. **Documentation**: Update docs for any changes
6. **Deployment**: Use production-ready configurations

### 🎯 Success Metrics

- **Reliability**: System handles errors gracefully
- **Performance**: Fast response times for all interfaces
- **Transparency**: Users can understand AI reasoning
- **Extensibility**: Easy to add new features
- **Maintainability**: Code is clean and well-documented

---

**Happy Coding! 🚗✨**

*Build intelligent, transparent, and reliable AI systems*
