"""
Automotive Bot with LangChain and Chroma Vector Database
Handles conversational flows and retrieval integration for automotive queries
"""

import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Load environment variables
load_dotenv()

# Configuration from environment variables (same as faq_bot.py)
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
MODEL = os.getenv("MODEL_NAME", "GPT-4o-mini")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "200"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.5"))

# Retry configuration
RETRY_ATTEMPTS = int(os.getenv("RETRY_ATTEMPTS", "3"))
RETRY_WAIT_MIN = int(os.getenv("RETRY_WAIT_MIN", "1"))
RETRY_WAIT_MAX = int(os.getenv("RETRY_WAIT_MAX", "10"))

try:
    import chromadb
    from chromadb.config import Settings
    import openai
    
    # Initialize OpenAI client with same config as faq_bot.py
    openai_client = openai.OpenAI(
        base_url=OPENAI_BASE_URL,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Try to import LangChain components
    try:
        from langchain.embeddings import OpenAIEmbeddings
        from langchain.vectorstores import Chroma
        from langchain.chat_models import ChatOpenAI
        from langchain.chains import ConversationalRetrievalChain
        from langchain.memory import ConversationBufferWindowMemory
        from langchain.prompts import PromptTemplate
        from langchain.schema import Document
        LANGCHAIN_AVAILABLE = True
    except ImportError:
        print("⚠️ LangChain not available. Using simple fallback mode.")
        LANGCHAIN_AVAILABLE = False
        
except ImportError as e:
    print(f"⚠️ Some dependencies not available: {e}")
    LANGCHAIN_AVAILABLE = False
    openai_client = None

# Initialize ChromaDB client
try:
    chroma_client = chromadb.PersistentClient(path=os.getenv("CHROMA_DB_PATH", "./chroma_db"))
except:
    chroma_client = None

class AutomotiveBot:
    def __init__(self):
        self.embeddings = None
        self.vectorstore = None
        self.llm = None
        self.memory = None
        self.qa_chain = None
        self.conversation_history = []
        self.initialize_components()
    
    def initialize_components(self):
        """Initialize components - LangChain if available, otherwise fallback"""
        try:
            if LANGCHAIN_AVAILABLE and chroma_client and openai_client:
                self._initialize_langchain()
            else:
                self._initialize_fallback()
                
        except Exception as e:
            print(f"Error initializing AutomotiveBot: {str(e)}")
            self._initialize_fallback()
    
    def _initialize_langchain(self):
        """Initialize with full LangChain components"""
        # Load embedding model and embedding key from environment
        EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        EMBEDDING_KEY = os.getenv("EMBEDDING_KEY", os.getenv("OPENAI_API_KEY"))
        EMBEDDING_BASE_URL = os.getenv("EMBEDDING_BASE_URL", OPENAI_BASE_URL)
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=EMBEDDING_KEY,
            openai_api_base=EMBEDDING_BASE_URL,
            model=EMBEDDING_MODEL,
            openai_api_type="open_ai"
        )
        
        # Initialize vector store - connect to existing collection
        try:
            self.vectorstore = Chroma(
                client=chroma_client,
                collection_name="automotive_knowledge",
                embedding_function=self.embeddings,
                persist_directory=os.getenv("CHROMA_DB_PATH", "./chroma_db")
            )
            print(f"✅ Connected to existing ChromaDB collection: automotive_knowledge")
        except Exception as e:
            print(f"⚠️ Error connecting to existing collection: {e}")
            # Create new collection if it doesn't exist
            self.vectorstore = Chroma(
                client=chroma_client,
                collection_name="automotive_knowledge", 
                embedding_function=self.embeddings
            )
            print("✅ Created new ChromaDB collection: automotive_knowledge")
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model_name=MODEL,
            temperature=TEMPERATURE,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_api_base=OPENAI_BASE_URL
        )
        
        # Initialize memory
        self.memory = ConversationBufferWindowMemory(
            k=5,  # Remember last 5 exchanges
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        
        # Create custom prompt template
        prompt_template = """
        Bạn là một chuyên gia tư vấn ô tô chuyên nghiệp và thân thiện. Hãy trả lời câu hỏi dựa trên kiến thức sau:

        Context: {context}

        Chat History: {chat_history}

        Question: {question}

        Hướng dẫn trả lời:
        - Trả lời bằng tiếng Việt một cách tự nhiên và thân thiện
        - Sử dụng thông tin từ context để đưa ra câu trả lời chính xác
        - Nếu không có thông tin trong context, hãy nói rõ và đưa ra lời khuyên chung
        - Cung cấp thông tin chi tiết và hữu ích
        - Có thể đề xuất thêm câu hỏi liên quan

        Answer:"""
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "chat_history", "question"]
        )
        
        # Initialize conversational retrieval chain
        self.qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 4}
            ),
            memory=self.memory,
            combine_docs_chain_kwargs={"prompt": PROMPT},
            return_source_documents=True,
            verbose=True
        )
        
        print("✅ Automotive Bot initialized with LangChain")
    
    def _initialize_fallback(self):
        """Initialize fallback mode without LangChain"""
        self.qa_chain = None
        self.conversation_history = []
        print("⚠️ Automotive Bot running in fallback mode (no LangChain)")
    
    @retry(
        stop=stop_after_attempt(RETRY_ATTEMPTS),
        wait=wait_exponential(multiplier=1, min=RETRY_WAIT_MIN, max=RETRY_WAIT_MAX),
        retry=retry_if_exception_type((Exception,)),
        reraise=True
    )
    def _call_openai_direct(self, messages):
        """Direct OpenAI API call for fallback mode"""
        if not openai_client:
            raise Exception("OpenAI client not available")
            
        response = openai_client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE
        )
        return response.choices[0].message.content.strip()
    
    def get_response(self, question: str) -> Dict[str, Any]:
        """Get response from the automotive bot"""
        try:
            if self.qa_chain:
                # Use LangChain mode
                result = self.qa_chain({"question": question})
                
                # Format source documents
                sources = []
                if result.get("source_documents"):
                    for i, doc in enumerate(result["source_documents"][:3]):  # Top 3 sources
                        sources.append({
                            "content": doc.page_content[:200] + "...",
                            "metadata": doc.metadata
                        })
                
                return {
                    "answer": result["answer"],
                    "sources": sources,
                    "error": False,
                    "mode": "langchain"
                }
            else:
                # Use fallback mode with direct OpenAI API
                return self._get_fallback_response(question)
                
        except Exception as e:
            return {
                "answer": f"❌ Lỗi khi xử lý câu hỏi: {str(e)}",
                "sources": [],
                "error": True,
                "mode": "error"
            }
    
    def _get_fallback_response(self, question: str) -> Dict[str, Any]:
        """Fallback response using direct OpenAI API"""
        try:
            # Build conversation context
            messages = [
                {
                    "role": "system", 
                    "content": """Bạn là một chuyên gia tư vấn ô tô chuyên nghiệp và thân thiện. 
                    
Hãy trả lời các câu hỏi về:
- Thông tin xe hơi, công nghệ ô tô
- Tư vấn mua xe, so sánh xe
- Bảo dưỡng và sửa chữa xe
- Lái xe an toàn
- Xu hướng ngành ô tô

Trả lời bằng tiếng Việt một cách tự nhiên, chi tiết và hữu ích."""
                }
            ]
            
            # Add conversation history (last 4 exchanges)
            for msg in self.conversation_history[-8:]:  # 4 exchanges = 8 messages
                messages.append(msg)
            
            # Add current question
            messages.append({"role": "user", "content": question})
            
            # Get response
            answer = self._call_openai_direct(messages)
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": question})
            self.conversation_history.append({"role": "assistant", "content": answer})
            
            # Keep history manageable
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            return {
                "answer": answer,
                "sources": [],
                "error": False,
                "mode": "fallback"
            }
            
        except Exception as e:
            return {
                "answer": f"❌ Lỗi khi gọi OpenAI API: {str(e)}",
                "sources": [],
                "error": True,
                "mode": "fallback_error"
            }
    
    def reset_conversation(self):
        """Reset conversation memory"""
        if self.memory:
            self.memory.clear()
        if self.conversation_history:
            self.conversation_history.clear()
    
    def get_conversation_info(self) -> Dict[str, Any]:
        """Get current conversation information"""
        try:
            if self.memory:
                # LangChain mode
                history = self.memory.chat_memory.messages
                return {
                    "message_count": len(history),
                    "status": "LangChain Active" if len(history) > 0 else "LangChain Empty"
                }
            else:
                # Fallback mode
                return {
                    "message_count": len(self.conversation_history) // 2,  # Each exchange = 2 messages
                    "status": "Fallback Active" if len(self.conversation_history) > 0 else "Fallback Empty"
                }
        except Exception as e:
            return {"message_count": 0, "status": f"Error: {str(e)}"}

# Global instance
automotive_bot = AutomotiveBot()

def get_automotive_response(question: str) -> str:
    """Get response from automotive bot"""
    result = automotive_bot.get_response(question)
    
    if result["error"]:
        return result["answer"]
    
    # Format response with sources and mode info
    response = result["answer"]
    
    # Add mode indicator
    mode_indicator = {
        "langchain": "🧠 LangChain + ChromaDB",
        "fallback": "⚡ Direct OpenAI API", 
        "error": "❌ Error Mode"
    }.get(result.get("mode", "unknown"), "❓ Unknown Mode")
    
    if result.get("sources"):
        response += f"\n\n📚 **Nguồn tham khảo ({mode_indicator}):**\n"
        for i, source in enumerate(result["sources"], 1):
            response += f"{i}. {source['content']}\n"
    else:
        response += f"\n\n🤖 *Powered by {mode_indicator}*"
    
    return response

def reset_automotive_conversation():
    """Reset automotive bot conversation"""
    automotive_bot.reset_conversation()

def get_automotive_info() -> Dict[str, Any]:
    """Get automotive bot conversation info"""
    return automotive_bot.get_conversation_info()

def sync_with_kb_manager():
    """Sync automotive bot with KB manager's vector store"""
    try:
        from kb_manager import kb_manager
        
        if kb_manager.vectorstore and automotive_bot.vectorstore:
            # Both are using the same ChromaDB client and collection name
            # They should automatically sync since they point to the same data
            print("✅ Automotive bot and KB manager are using shared ChromaDB")
            return True
        else:
            print("⚠️ One or both components are not using ChromaDB")
            return False
            
    except Exception as e:
        print(f"❌ Sync error: {e}")
        return False
