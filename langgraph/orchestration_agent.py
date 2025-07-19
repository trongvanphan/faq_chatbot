"""
Master Orchestration Agent
Coordinates between different specialized agents and handles routing decisions.
"""

from typing import Dict, Any, List
from chat_state import ChatState
from services import get_azure_llm
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_core.output_parsers import StrOutputParser
from agents.recommendation import recommend_car
from langgraph.graph import StateGraph, END
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MasterOrchestrationAgent:
    """
    Master agent that orchestrates between different specialized agents.
    Handles intent classification and routing to appropriate agents.
    """
    
    def __init__(self):
        self.llm = get_azure_llm()
        self.available_agents = {
            "recommendation": {
                "function": recommend_car,
                "description": "Car recommendation and buying advice",
                "keywords": ["car", "recommend", "buy", "purchase", "vehicle", "budget", "family car", "commute"]
            },
            "retrieve_docs": {
                "function": self.retrieve_docs,
                "description": "Document retrieval and knowledge base search",
                "keywords": ["document", "search", "find", "information", "knowledge"]
            },
            "search_news": {
                "function": self.search_news,
                "description": "News search and current events",
                "keywords": ["news", "latest", "update", "current", "recent", "breaking"]
            }
        }
        self.setup_intent_classifier()
        self.setup_workflow()
    
    def setup_intent_classifier(self):
        """Set up the intent classification system."""
        agent_descriptions = "\n".join([
            f"- {name}: {info['description']}"
            for name, info in self.available_agents.items()
        ])
        
        self.intent_prompt = PromptTemplate.from_template(
            f"""You are an intelligent intent classifier for a multi-agent system.
            
            Available agents:
            {agent_descriptions}
            
            Classify the user's question into one of these agent types:
            - recommendation (for car buying, vehicle advice, recommendations)
            - retrieve_docs (for document search, knowledge base queries)
            - search_news (for news, current events, updates)
            
            User question: {{question}}
            
            Respond with only the agent name (recommendation/retrieve_docs/search_news)."""
        )
        
        self.intent_classifier: RunnableSequence = (
            self.intent_prompt 
            | self.llm 
            | StrOutputParser()
        )
    
    def classify_intent(self, question: str) -> str:
        """
        Classify user intent and determine which agent to route to.
        """
        try:
            intent = self.intent_classifier.invoke({"question": question}).strip().lower()
            
            # Validate intent
            if intent not in self.available_agents:
                logger.warning(f"Unknown intent '{intent}', defaulting to retrieve_docs")
                intent = "retrieve_docs"
            
            logger.info(f"Classified intent: {intent} for question: {question[:50]}...")
            return intent
            
        except Exception as e:
            logger.error(f"Error in intent classification: {e}")
            return "retrieve_docs"  # Default fallback
    
    def route_user_input(self, state: ChatState) -> ChatState:
        """
        Route user input to appropriate agent based on intent classification.
        """
        question = state["question"]
        intent = self.classify_intent(question)
        
        logger.info(f"Routing to agent: {intent}")
        return {**state, "next_step": intent}
    
    def retrieve_docs(self, state: ChatState) -> ChatState:
        """
        Handle document retrieval requests using enhanced knowledge base.
        """
        try:
            from knowledge_base import knowledge_base
            
            # Use the enhanced knowledge base search
            results = knowledge_base.search_similar(state["question"], k=4)
            
            if results:
                # Convert search results to document format for compatibility
                docs = []
                for result in results:
                    # Create a mock document object
                    class MockDoc:
                        def __init__(self, content, metadata):
                            self.page_content = content
                            self.metadata = metadata
                    
                    docs.append(MockDoc(result["content"], result["metadata"]))
                
                return {**state, "context_docs": docs}
            else:
                return {**state, "context_docs": [], "answer": "I couldn't find relevant information in the knowledge base."}
                
        except Exception as e:
            logger.error(f"Error in enhanced document retrieval: {e}")
            # Fallback to basic retrieval if enhanced version fails
            try:
                from services import get_vectordb
                retriever = get_vectordb().as_retriever(search_kwargs={"k": 4}) 
                docs = retriever.get_relevant_documents(state["question"])
                return {**state, "context_docs": docs}
            except Exception as e2:
                logger.error(f"Fallback document retrieval also failed: {e2}")
                return {**state, "context_docs": [], "answer": "I'm having trouble accessing the document database right now."}
    
    def search_news(self, state: ChatState) -> ChatState:
        """
        Handle news search requests.
        """
        topic = state["question"].lower()
        
        # Mock news articles - in production, this would connect to a real news API
        mock_articles = [
            "🚘 Breaking: Electric vehicle sales surge 25% in Q2 2025.",
            "🔧 Update: Toyota announces new hybrid models for 2026.",
            "🛠️ Analysis: How EV maintenance compares with gas-powered cars.",
            "⚡ News: Major automakers commit to faster EV charging networks.",
            "🌱 Report: Government extends EV tax incentives through 2026."
        ]
        
        response = f"Here are some recent news headlines related to **{topic}**:\n\n"
        response += "\n".join(f"- {article}" for article in mock_articles)
        response += "\n\n*Note: This is a demo with mock headlines. In production, this would pull real-time news.*"
        
        return {**state, "answer": response}
    
    def generate_answer(self, state: ChatState) -> ChatState:
        """
        Generate final answer, handling both document-based and direct agent responses.
        """
        question = state["question"]
        chat_history = state["chat_history"]
        docs = state.get("context_docs", [])
        
        # If context_docs are available, use them for answer generation
        if docs:
            try:
                context = "\n".join([doc.page_content for doc in docs])
                enhanced_prompt = f"""
                Based on the following context documents, please answer the user's question comprehensively.
                
                Context: {context}
                
                Question: {question}
                
                Please provide a detailed, helpful answer based on the context provided.
                If the context doesn't contain relevant information, please say so clearly.
                """
                response = self.llm.invoke(enhanced_prompt)
                return {**state, "answer": response.content}
            except Exception as e:
                logger.error(f"Error in answer generation: {e}")
                return {**state, "answer": "I encountered an error while processing the documents."}
        
        # If answer is already set by an agent (recommendation/news), return it
        elif "answer" in state and state["answer"]:
            return state
        
        # Fallback response
        else:
            return {**state, "answer": "I'm not sure how to help with that right now. Could you please rephrase your question?"}
    
    def setup_workflow(self):
        """
        Set up the LangGraph workflow for the orchestration agent.
        """
        self.graph = StateGraph(ChatState)
        
        # Add all nodes
        self.graph.add_node("router", self.route_user_input)
        self.graph.add_node("retrieve_docs", self.retrieve_docs)
        self.graph.add_node("recommendation", recommend_car)
        self.graph.add_node("search_news", self.search_news)
        self.graph.add_node("generate_answer", self.generate_answer)
        
        # Set entry point
        self.graph.set_entry_point("router")
        
        # Add conditional routing from router
        self.graph.add_conditional_edges("router", lambda state: state["next_step"], {
            "retrieve_docs": "retrieve_docs",
            "recommendation": "recommendation", 
            "search_news": "search_news"
        })
        
        # Connect all paths to answer generation
        self.graph.add_edge("retrieve_docs", "generate_answer")
        self.graph.add_edge("recommendation", "generate_answer") 
        self.graph.add_edge("search_news", "generate_answer")
        self.graph.add_edge("generate_answer", END)
        
        # Compile the workflow
        self.workflow = self.graph.compile()
        logger.info("Master orchestration workflow compiled successfully")
    
    def process_query(self, question: str, chat_history: List = None) -> Dict[str, Any]:
        """
        Process a user query through the orchestration system.
        """
        if chat_history is None:
            chat_history = []
        
        try:
            result = self.workflow.invoke({
                "question": question,
                "chat_history": chat_history,
                "context_docs": [],
                "answer": "",
                "next_step": ""
            })
            return result
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "question": question,
                "answer": "I encountered an error while processing your request. Please try again.",
                "chat_history": chat_history
            }
    
    def add_agent(self, name: str, function, description: str, keywords: List[str]):
        """
        Add a new specialized agent to the orchestration system.
        """
        self.available_agents[name] = {
            "function": function,
            "description": description,
            "keywords": keywords
        }
        
        # Rebuild intent classifier with new agent
        self.setup_intent_classifier()
        logger.info(f"Added new agent: {name}")
    
    def get_available_agents(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all available agents.
        """
        return self.available_agents.copy()

    def get_workflow_image(self) -> bytes:
        """
        Returns a PNG image (as bytes) of the LangGraph workflow.
        """
        try:
            return self.workflow.get_graph().draw_mermaid_png()
        except Exception as e:
            logger.error(f"Error generating workflow image: {e}")
            return None
# Create global master orchestration agent instance
master_agent = MasterOrchestrationAgent()
