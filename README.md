# 🚗 FAQ Chatbot: Advanced Multi-Modal AI Assistant

An advanced chatbot system featuring **5 different AI approaches** for automotive FAQ, from simple Q&A to sophisticated RAG (Retrieval-Augmented Generation) with LangChain and ChromaDB.

## 🌟 Features

### **🤖 Tab 1: Automotive Bot (NEW!)**
- **LangChain ConversationalRetrievalChain** với memory
- **ChromaDB local vector database** cho fast similarity search
- **RAG (Retrieval-Augmented Generation)** pipeline
- **Conversational context** nhớ toàn bộ cuộc trò chuyện

### **📚 Tab 2: KB Management - RAG (NEW!)**
- **Document upload** (PDF, TXT, MD)
- **Automatic text chunking** và preprocessing
- **ChromaDB + FAISS** vector storage
- **Knowledge base statistics** và monitoring
- **Search functionality** trong vector database

### **🧠 Tab 3: Context-Aware Bot**
- **Full conversation context management**
- **Reference understanding** ("nó", "xe đó")
- **Function calling** với context
- **Smart token management**

### **🔧 Tab 4: Function Calling Bot**
- **OpenAI Function Calling** capabilities
- **Retry mechanism** với exponential backoff
- Independent message processing

### **📖 Tab 5: Simple FAQ Bot**
- Basic FAQ responses
- Static knowledge base
- Simple Q&A matching

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Gradio UI     │────│  LangChain Core  │────│   ChromaDB      │
│   (5 Tabs)      │    │                  │    │  (Vector Store) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Context Manager │    │   OpenAI API     │    │   FAISS Index   │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Option 1: Automatic Setup (Recommended)
```bash
./setup.sh
```

### Option 2: Manual Setup
```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env and add your OpenAI API key

# 4. Run application
python app.py
```

## 📁 Project Structure
## 📁 Project Structure

```
faq_chatbot/
├── app.py                      # 🎯 Main Gradio application (5 tabs)
├── automotive_bot.py           # 🤖 NEW: LangChain + ChromaDB bot
├── kb_manager.py              # 📚 NEW: RAG knowledge base manager
├── context_manager.py         # 🧠 Context-aware conversation manager
├── faq_bot.py                 # 🔧 Function calling & simple FAQ
├── faq_data.py               # 📖 Static FAQ dataset
├── requirements.txt          # 📦 Python dependencies
├── .env.example             # ⚙️ Environment configuration template
├── setup.sh                # 🚀 Automatic setup script
├── chroma_db/              # 🗄️ ChromaDB vector database
└── README.md               # 📋 This file
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional
RETRY_ATTEMPTS=3
RETRY_WAIT_MIN=1
RETRY_WAIT_MAX=10
CHROMA_DB_PATH=./chroma_db
```

## 💡 Usage Guide

### 1. **🤖 Automotive Bot Tab**
- Ask any automotive questions
- Bot searches ChromaDB knowledge base
- Conversational memory maintains context
- Example: "What are hybrid engines?" → "How do they compare to electric?"

### 2. **📚 KB Management Tab**
- Upload PDF/TXT documents about automotive topics
- System automatically processes and indexes
- Search existing knowledge base
- Monitor statistics and clear data if needed

### 3. **🧠 Context-Aware Bot Tab**
- Multi-turn conversations with full context
- Understands references from previous messages
- Function calling with conversational context
- Example: "Suggest SUVs" → "What about the Honda CR-V?" → "What's its price?"

### 4. **🔧 Function Calling Bot Tab**
- OpenAI function calling without context
- Each message processed independently
- Good for specific queries

### 5. **📖 Simple FAQ Bot Tab**
- Basic static FAQ responses
- No AI processing, simple matching
- Fastest response time

## 🛠️ Technical Details

### **LangChain Components**
- `ConversationalRetrievalChain`: Main conversation chain
- `OpenAIEmbeddings`: Text embedding for similarity search
- `ConversationBufferWindowMemory`: Conversation memory management
- `RecursiveCharacterTextSplitter`: Document chunking

### **ChromaDB Features**
- Persistent local vector database
- FAISS similarity search
- Automatic embedding storage
- Collection management

### **RAG Pipeline**
1. **Document Upload** → Text extraction (PDF/TXT)
2. **Text Splitting** → Chunking with overlap
3. **Embedding** → OpenAI embeddings
4. **Storage** → ChromaDB vector store
5. **Retrieval** → Similarity search
6. **Generation** → LLM response with context

## 🚀 Development

### Adding New Features
```python
# Add new bot type
from your_new_bot import YourNewBot

def your_bot_interface(user_input, history):
    # Your implementation
    pass

# Add to app.py tabs
with gr.Tab("🆕 Your New Bot"):
    # Your UI components
    pass
```

### Extending Knowledge Base
```python
# Add new document types in kb_manager.py
def process_new_format(self, file_path: str):
    # Your processing logic
    pass
```

## 📊 Monitoring

- **ChromaDB stats**: Number of documents, chunks, collection status
- **Conversation tracking**: Message count, topics, context size
- **Error handling**: Comprehensive error messages and fallbacks
- **Performance**: Retry mechanisms with exponential backoff

## 🔍 Troubleshooting

### Common Issues
1. **OpenAI API Key**: Make sure it's set in `.env`
2. **Dependencies**: Run `pip install -r requirements.txt`
3. **ChromaDB**: Delete `chroma_db/` folder to reset
4. **Memory**: Restart app if conversations get too long

### Debug Mode
```bash
# Run with verbose logging
LANGCHAIN_VERBOSE=true python app.py
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **OpenAI** for GPT models and embeddings
- **LangChain** for RAG framework
- **ChromaDB** for vector database
- **Gradio** for web interface
- **FAISS** for similarity search
   - Clone this repository to your local machine.
2. **Install dependencies**
   - Run `pip install -r requirements.txt` to install required packages.
3. **Review and update FAQ data**
   - Open `faq_data.py` to view or edit the list of FAQs and answers.
4. **Understand the chatbot logic**
   - Check `faq_bot.py` to see how user questions are matched to FAQ answers.
5. **Run the application**
   - Start the chatbot by running `python app.py`.
   - Open the provided local URL in your browser to interact with the chatbot.
6. **Customize as needed**
   - Add new questions/answers in `faq_data.py`.
   - Adjust logic in `faq_bot.py` for improved matching or features.

### Installation
1. Clone this repository:
   ```bash
   git clone <repo-url>
   cd faq_chatbot
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Chatbot
Start the Gradio app:
```bash
python app.py
```
This will launch a local web server. Open the provided URL in your browser to interact with the chatbot.

## Customization
- Add or modify FAQs in `faq_data.py` to update the chatbot's knowledge base.

## Requirements
- Python 3.7+
- gradio

## License
This project is for educational purposes.
