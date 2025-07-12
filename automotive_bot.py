"""
Automotive Bot with LangChain, ChromaDB for RAG, and Tavily for News Search
"""

import os
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

# Configuration
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
MODEL = os.getenv("MODEL_NAME", "GPT-4o-mini")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.5"))
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

try:
    import chromadb
    import openai
    from langchain_community.chat_models import ChatOpenAI
    # TavilySearchResults import fallback
    try:
        from langchain_community.tools.tavily_search.tool import TavilySearchResults
    except ImportError:
        from langchain_community.tools.tavily_search import TavilySearchResults
    try:
        from langchain_community.vectorstores import FAISS
    except ImportError:
        from langchain.vectorstores import FAISS
    from langchain.chains import ConversationalRetrievalChain
    from langchain.memory import ConversationBufferWindowMemory
    from langchain.prompts import PromptTemplate
    from langchain.schema import Document, BaseRetriever
    from langchain.agents import initialize_agent, AgentType
    from langchain.tools import Tool

    # Initialize clients
    openai_client = openai.OpenAI(
        base_url=OPENAI_BASE_URL,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
except ImportError as e:
    print(f"⚠️ Dependencies not available: {e}")
    openai_client = None
    chroma_client = None

class CustomOpenAIEmbeddings:
    """Custom embedding class using OpenAI API directly"""
    def __init__(self, api_key, base_url, model="text-embedding-3-small"):
        import openai
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        
    def embed_documents(self, texts):
        embeddings = []
        for text in texts:
            response = self.client.embeddings.create(model=self.model, input=text)
            embeddings.append(response.data[0].embedding)
        return embeddings
        
    def embed_query(self, text):
        response = self.client.embeddings.create(model=self.model, input=text)
        return response.data[0].embedding

class CustomChromaRetriever(BaseRetriever):
    """Custom retriever for ChromaDB integration"""
    def __init__(self, collection, embeddings):
        super().__init__()
        self._collection = collection
        self._embeddings = embeddings
        
    def _get_relevant_documents(self, query, run_manager=None):
        query_embedding = self._embeddings.embed_query(query)
        results = self._collection.query(query_embeddings=[query_embedding], n_results=4)
        
        documents = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i] if results["metadatas"] and results["metadatas"][0] else {}
                documents.append(Document(page_content=doc, metadata=metadata))
        return documents

class AutomotiveBot:
    def __init__(self):
        self.qa_chain = None
        self.agent = None
        self.conversation_history = []
        self.initialize_components()
    
    def initialize_components(self):
        """Initialize bot components"""
        try:
            if chroma_client and openai_client:
                self._setup_langchain()
                self._setup_agent()
            else:
                self._setup_fallback()
        except Exception as e:
            print(f"Error initializing AutomotiveBot: {e}")
            self._setup_fallback()
    
    def _setup_langchain(self):
        """Setup LangChain with ChromaDB"""
        # Initialize embeddings
        self.embeddings = CustomOpenAIEmbeddings(
            api_key=os.getenv("EMBEDDING_KEY", os.getenv("OPENAI_API_KEY")),
            base_url=os.getenv("EMBEDDING_BASE_URL", OPENAI_BASE_URL),
            model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        )
        
        # Connect to ChromaDB collection
        try:
            self.chroma_collection = chroma_client.get_collection("automotive_knowledge")
            print(f"✅ Connected to ChromaDB collection (documents: {self.chroma_collection.count()})")
        except:
            self.chroma_collection = chroma_client.create_collection("automotive_knowledge")
            print("✅ Created new ChromaDB collection")
        
        # Initialize LLM and memory
        self.llm = ChatOpenAI(
            model_name=MODEL,
            temperature=TEMPERATURE,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_api_base=OPENAI_BASE_URL
        )
        
        self.memory = ConversationBufferWindowMemory(
            k=5,
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        
        # Setup retrieval chain
        prompt_template = """Bạn là chuyên gia tư vấn ô tô. Trả lời dựa trên thông tin sau:

Context: {context}
Chat History: {chat_history}
Question: {question}

Trả lời bằng tiếng Việt, chi tiết và hữu ích. Nếu không có thông tin trong context, hãy nói rõ.

Answer:"""
        
        try:
            retriever = CustomChromaRetriever(self.chroma_collection, self.embeddings)
            self.qa_chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=retriever,
                memory=self.memory,
                combine_docs_chain_kwargs={"prompt": PromptTemplate(
                    template=prompt_template,
                    input_variables=["context", "chat_history", "question"]
                )},
                return_source_documents=True
            )
            print("✅ LangChain setup successful")
        except Exception as e:
            print(f"⚠️ LangChain setup failed: {e}")
            self.qa_chain = None
    
    def _setup_agent(self):
        """Setup agent with Tavily search tool"""
        try:
            if not TAVILY_API_KEY:
                print("⚠️ Tavily API key not found - agent will not be available")
                return
            
            # Create Tavily search tool
            tavily_search = TavilySearchResults(
                api_key=TAVILY_API_KEY,
                max_results=5,
                search_depth="advanced"
            )
            
            # Create knowledge base search tool
            def search_knowledge_base(query: str) -> str:
                """Search the local knowledge base for automotive information"""
                try:
                    if not self.chroma_collection:
                        return "Knowledge base not available"
                    
                    query_embedding = self.embeddings.embed_query(query)
                    results = self.chroma_collection.query(
                        query_embeddings=[query_embedding], 
                        n_results=3
                    )
                    
                    if not results["documents"] or not results["documents"][0]:
                        return "No relevant information found in knowledge base"
                    
                    response = "Knowledge base results:\n"
                    for i, doc in enumerate(results["documents"][0], 1):
                        response += f"{i}. {doc[:300]}...\n\n"
                    
                    return response
                except Exception as e:
                    return f"Error searching knowledge base: {str(e)}"
            
            # Define tools
            tools = [
                Tool(
                    name="tavily_search",
                    func=tavily_search.run,
                    description="Search for latest automotive news, reviews, and information. Use this for current events, new car releases, market trends, and recent automotive developments."
                ),
                Tool(
                    name="knowledge_base_search",
                    func=search_knowledge_base,
                    description="Search the local knowledge base for stored automotive information like prices, specifications, and historical data."
                )
            ]
            
            # Initialize agent
            self.agent = initialize_agent(
                tools,
                self.llm,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=3
            )
            
            print("✅ Agent setup successful with Tavily integration")
            
        except Exception as e:
            print(f"⚠️ Agent setup failed: {e}")
            self.agent = None
    
    def _setup_fallback(self):
        """Setup fallback mode"""
        self.qa_chain = None
        self.agent = None
        print("⚠️ Running in fallback mode")
    
    def get_response(self, question: str) -> Dict[str, Any]:
        """Get response from the automotive bot"""
        try:
            # Check if question requires news search
            news_keywords = [
                "tin tức", "news", "mới nhất", "latest", "cập nhật", "update",
                "ra mắt", "launch", "giới thiệu", "introduce", "thị trường", "market",
                "xu hướng", "trend", "đánh giá", "review", "so sánh", "compare"
            ]
            
            question_lower = question.lower()
            requires_news = any(keyword in question_lower for keyword in news_keywords)
            
            if requires_news and self.agent:
                # Use agent for news search
                print("🔍 Using agent for news search...")
                result = self.agent.run(question)
                
                return {
                    "answer": result,
                    "sources": [],
                    "error": False,
                    "mode": "agent_news"
                }
            
            elif self.qa_chain:
                # Use LangChain mode for knowledge base queries
                print("📚 Using LangChain for knowledge base search...")
                result = self.qa_chain({"question": question})
                
                sources = []
                if result.get("source_documents"):
                    for doc in result["source_documents"][:3]:
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
                # Use fallback mode
                return self._get_fallback_response(question)
                
        except Exception as e:
            return {
                "answer": f"❌ Lỗi: {str(e)}",
                "sources": [],
                "error": True,
                "mode": "error"
            }
    
    def _get_fallback_response(self, question: str) -> Dict[str, Any]:
        """Fallback response using direct OpenAI API"""
        try:
            messages = [
                {"role": "system", "content": "Bạn là chuyên gia tư vấn ô tô. Trả lời bằng tiếng Việt."},
                {"role": "user", "content": question}
            ]
            
            response = openai_client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=TEMPERATURE
            )
            
            return {
                "answer": response.choices[0].message.content.strip(),
                "sources": [],
                "error": False,
                "mode": "fallback"
            }
            
        except Exception as e:
            return {
                "answer": f"❌ Lỗi API: {str(e)}",
                "sources": [],
                "error": True,
                "mode": "fallback_error"
            }
    
    def reset_conversation(self):
        """Reset conversation memory"""
        if hasattr(self, 'memory') and self.memory:
            self.memory.clear()
        self.conversation_history.clear()

# Global instance
automotive_bot = AutomotiveBot()

def get_automotive_response(question: str) -> str:
    """Get response from automotive bot"""
    result = automotive_bot.get_response(question)
    
    if result["error"]:
        return result["answer"]
    
    # Format response with sources
    response = result["answer"]
    
    # Add mode indicator
    mode_icons = {
        "langchain": "🧠 LangChain + ChromaDB",
        "agent_news": "🔍 Agent + Tavily News",
        "fallback": "⚡ Direct OpenAI",
        "error": "❌ Error"
    }
    mode = mode_icons.get(result.get("mode", "unknown"), "❓ Unknown")
    
    if result.get("sources"):
        response += f"\n\n📚 **Nguồn ({mode}):**\n"
        for i, source in enumerate(result["sources"], 1):
            response += f"{i}. {source['content']}\n"
    else:
        response += f"\n\n🤖 *{mode}*"
    
    return response

def reset_automotive_conversation():
    """Reset automotive bot conversation"""
    automotive_bot.reset_conversation()

def get_automotive_info() -> Dict[str, Any]:
    """Get automotive bot info"""
    if hasattr(automotive_bot, 'memory') and automotive_bot.memory:
        history = automotive_bot.memory.chat_memory.messages
        return {"message_count": len(history), "status": "LangChain + Agent"}
    else:
        return {"message_count": len(automotive_bot.conversation_history) // 2, "status": "Fallback"}
