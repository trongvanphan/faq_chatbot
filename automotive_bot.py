"""
Automotive Bot with LangChain, ChromaDB for RAG, and Tavily for News Search
"""

import os
import re
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
    from langchain.callbacks.base import BaseCallbackHandler

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

class AgentCallbackHandler(BaseCallbackHandler):
    """Custom callback handler to capture agent thoughts and observations"""
    def __init__(self):
        super().__init__()
        self.thoughts = []
        self.observations = []
        self.actions = []
        self.current_step = 0
    
    def on_agent_action(self, action, color=None, **kwargs):
        """Called when agent takes an action"""
        print(f"🔧 Agent Action: {action.tool} with input: {action.tool_input}")
        self.current_step += 1
        self.actions.append({
            "step": self.current_step,
            "tool": action.tool,
            "tool_input": action.tool_input,
            "log": action.log
        })
    
    def on_tool_end(self, output, color=None, observation_prefix=None, llm_prefix=None, **kwargs):
        """Called when a tool finishes execution"""
        print(f"👀 Tool End: Output length: {len(str(output))}")
        print(f"🔍 Tool End Debug: Current step = {self.current_step}")
        print(f"📊 Tool End Debug: Output preview = {str(output)[:100]}...")
        
        # Make sure we have a current step from agent action
        if self.current_step > 0:
            obs_data = {
                "step": self.current_step,
                "output": str(output)[:500] + ("..." if len(str(output)) > 500 else "")
            }
            self.observations.append(obs_data)
            print(f"✅ Added observation for step {self.current_step}: {len(obs_data['output'])} chars")
        else:
            print("⚠️ Tool ended but no current step!")
    
    def on_tool_start(self, serialized, input_str, **kwargs):
        """Called when a tool starts execution"""
        print(f"🛠️ Tool Start: {serialized.get('name', 'Unknown')} with {input_str}")
    
    def on_text(self, text, color=None, end="\n", **kwargs):
        """Called when agent generates text (including observations)"""
        if "Observation:" in text:
            print(f"📝 Text with Observation: {text[:100]}...")
            # Try to capture observation from text
            if self.current_step > 0:
                obs_match = re.search(r'Observation:\s*(.*)', text, re.DOTALL)
                if obs_match:
                    obs_text = obs_match.group(1).strip()
                    self.observations.append({
                        "step": self.current_step,
                        "output": obs_text[:500] + ("..." if len(obs_text) > 500 else "")
                    })
    
    def on_llm_start(self, serialized, prompts, **kwargs):
        """Called when LLM starts"""
        print(f"🤖 LLM Start: {len(prompts)} prompts")
    
    def on_llm_end(self, response, **kwargs):
        """Called when LLM ends"""
        print(f"✅ LLM End: Generated response")
    
    def on_chain_start(self, serialized, inputs, **kwargs):
        """Called when a chain starts"""
        print(f"🔗 Chain Start: {serialized.get('name', 'Unknown')}")
    
    def on_chain_end(self, outputs, **kwargs):
        """Called when a chain ends"""
        print(f"🏁 Chain End: {type(outputs)}")
    
    def on_agent_finish(self, finish, color=None, **kwargs):
        """Called when agent finishes"""
        print(f"✅ Agent Finished with: {type(finish)}")
        pass
    
    def get_thinking_process(self):
        """Get the thinking process as formatted text"""
        print(f"🧠 Getting thinking process: {len(self.actions)} actions, {len(self.observations)} observations")
        
        if not self.actions:
            return ""
        
        process = "🧠 **Quá trình suy nghĩ của Bot:**\n\n"
        
        for i, action in enumerate(self.actions, 1):
            # Debug: Print the full log to see its structure
            print(f"🔍 Action {i} log: {action['log'][:200]}...")
            
            thought = ""
            # First, try to extract the thought using regex, which is the most reliable
            thought_match = re.search(r'Thought:\s*(.*?)(?:\nAction:|$)', action["log"], re.DOTALL)
            if thought_match:
                thought = thought_match.group(1).strip()
            
            # Fallback: If no explicit thought is found, generate a descriptive one.
            if not thought or thought.isspace():
                thought = f"Tôi cần sử dụng công cụ `{action['tool']}` để tìm kiếm thông tin về chủ đề: '{action['tool_input']}'."
            
            process += f"**💭 Bước {i} - Suy nghĩ:**\n{thought}\n\n"
            process += f"**🔧 Hành động:**\nSử dụng công cụ: `{action['tool']}`\n"
            process += f"**📝 Input cho công cụ:**\n`{action['tool_input']}`\n\n"
            
            # Find corresponding observation
            obs = next((o for o in self.observations if o["step"] == action["step"]), None)
            if obs:
                obs_content = obs['output'].strip()
                if len(obs_content) > 400:
                    obs_content = obs_content[:400] + "..."
                process += f"**👀 Quan sát:**\n{obs_content}\n\n"
            
            process += "---\n\n"
        
        print(f"📋 Generated process length: {len(process)}")
        return process
    
    def reset(self):
        """Reset the callback handler"""
        self.thoughts.clear()
        self.observations.clear()
        self.actions.clear()
        self.current_step = 0

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
        self.callback_handler = AgentCallbackHandler()
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
                max_iterations=3,
                callbacks=[self.callback_handler]
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
                self.callback_handler.reset()  # Reset before new agent run
                result = self.agent.run(question)
                
                # Get thinking process
                thinking_process = self.callback_handler.get_thinking_process()
                
                return {
                    "answer": result,
                    "sources": [],
                    "error": False,
                    "mode": "agent_news",
                    "thinking_process": thinking_process
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
                
                # Check if knowledge base has relevant information
                has_relevant_info = (
                    result.get("source_documents") and 
                    len(result["source_documents"]) > 0 and
                    any(doc.page_content.strip() for doc in result["source_documents"]) and
                    # Check if the answer contains meaningful content, not just "không có thông tin"
                    not any(phrase in result["answer"].lower() for phrase in [
                        "không có thông tin", "không tìm thấy", "không có dữ liệu",
                        "no information", "not found", "no data",
                        "xin lỗi, nhưng trong thông tin mà tôi có không có",
                        "trong thông tin mà tôi có không có chi tiết về",
                        "sorry, but i don't have information about",
                        "i don't have specific information about"
                    ])
                )
                
                # If no relevant info in knowledge base, try agent first, then fallback
                if not has_relevant_info:
                    if self.agent:
                        print("🔍 Knowledge base không có thông tin, đang dùng agent...")
                        try:
                            self.callback_handler.reset()  # Reset before new agent run
                            agent_result = self.agent.run(question)
                            
                            # Get thinking process
                            thinking_process = self.callback_handler.get_thinking_process()
                            
                            return {
                                "answer": agent_result,
                                "sources": [],
                                "error": False,
                                "mode": "agent_fallback",
                                "thinking_process": thinking_process
                            }
                        except Exception as e:
                            print(f"⚠️ Agent failed: {e}, falling back to direct chat...")
                            return self._get_fallback_response(question)
                    else:
                        # No agent available, use direct chat
                        print("📱 Không có agent, dùng direct chat...")
                        return self._get_fallback_response(question)
                
                return {
                    "answer": result["answer"],
                    "sources": sources,
                    "error": False,
                    "mode": "langchain",
                    "thinking_process": ""  # No thinking process for LangChain
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
                "mode": "fallback",
                "thinking_process": ""  # No thinking process for fallback
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
    # Check if user wants to search online
    if question.lower().startswith("search online"):
        search_query = question[13:].strip()  # Remove "search online" prefix
        if search_query and automotive_bot.agent:
            print("🌐 User requested online search...")
            try:
                automotive_bot.callback_handler.reset()  # Reset before new agent run
                result = automotive_bot.agent.run(search_query)
                
                # Get thinking process
                thinking_process = automotive_bot.callback_handler.get_thinking_process()
                
                response = f"🌐 **Kết quả tìm kiếm online:**\n\n{result}\n\n🤖 *🔍 Agent + Tavily Search*"
                
                # Add thinking process if available
                if thinking_process:
                    response = thinking_process + "\n" + response
                
                return response
            except Exception as e:
                return f"❌ Lỗi khi tìm kiếm online: {str(e)}"
        else:
            return "❌ Không thể tìm kiếm online. Vui lòng thử lại hoặc kiểm tra kết nối."
    
    result = automotive_bot.get_response(question)
    
    if result["error"]:
        return result["answer"]
    
    # Format response with sources
    response = result["answer"]
    
    # Add thinking process if available (for agent modes)
    thinking_process = result.get("thinking_process", "")
    if thinking_process:
        print(f"🧠 Adding thinking process to response ({len(thinking_process)} chars)")
        response = thinking_process + "\n\n" + response
    else:
        print(f"⚠️ No thinking process found for mode: {result.get('mode', 'unknown')}")
    
    # Add mode indicator
    mode_icons = {
        "langchain": "🧠 LangChain + ChromaDB",
        "agent_news": "🔍 Agent + Tavily News",
        "agent_fallback": "🤖 Smart Agent Fallback",
        "fallback": "⚡ Direct OpenAI",
        "error": "❌ Error",
        "suggest_online_search": "💡 Gợi ý tìm kiếm online"
    }
    mode = mode_icons.get(result.get("mode", "unknown"), "❓ Unknown")
    
    # Only show sources if there are actually sources with meaningful content
    # and the response is not just a greeting or simple interaction
    if (result.get("sources") and 
        len(result["sources"]) > 0 and 
        any(source.get("content", "").strip() for source in result["sources"]) and
        len(response.strip()) > 20 and  # Not just a short greeting
        result.get("mode") == "langchain"):  # Only for langchain mode with real retrieval
        response += f"\n\n📚 **Nguồn ({mode}):**\n"
        for i, source in enumerate(result["sources"], 1):
            if source.get("content", "").strip():  # Only show non-empty sources
                response += f"{i}. {source['content']}\n"
    else:
        # Only show mode for non-langchain or when no real sources were used
        if result.get("mode") != "langchain" or not result.get("sources"):
            if result.get("mode") != "suggest_online_search":  # Don't show mode for suggestion
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
