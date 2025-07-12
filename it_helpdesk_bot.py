"""
IT Helpdesk Bot inspired by sample.py
Simple RAG + Function Calling implementation
"""

import os
import json
from typing import List, Tuple, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Configuration
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
MODEL = os.getenv("MODEL_NAME", "GPT-4o-mini")

# Azure OpenAI Configuration for IT Helpdesk Bot
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY") 
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-07-01-preview")
AZURE_DEPLOYMENT_CHAT = os.getenv("AZURE_DEPLOYMENT_CHAT", "gpt-4o-mini")
AZURE_DEPLOYMENT_EMBEDDING = os.getenv("AZURE_DEPLOYMENT_EMBEDDING", "text-embedding-3-small")
AZURE_EMBEDDING_KEY = os.getenv("EMBEDDING_KEY") 

try:
    import openai
    from langchain_community.vectorstores import FAISS
    from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
    from langchain.chains import ConversationalRetrievalChain
    from langchain.text_splitter import RecursiveCharacterTextSplitter

    # Initialize Azure OpenAI client
    openai_client = openai.AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION
    )

    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Dependencies not available: {e}")
    DEPENDENCIES_AVAILABLE = False
    openai_client = None

class ITHelpdeskBot:
    def __init__(self):
        self.vectorstore = None
        self.retrieval_chain = None
        self.chat_history = []
        self.functions = self._define_functions()
        self.initialize_components()
    
    def initialize_components(self):
        """Initialize helpdesk bot components"""
        try:
            if DEPENDENCIES_AVAILABLE and openai_client and AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY:
                self._setup_rag_system()
            else:
                print("⚠️ IT Helpdesk Bot running in limited mode")
                print("   Missing Azure OpenAI configuration. Please set:")
                print("   - AZURE_OPENAI_ENDPOINT")
                print("   - AZURE_OPENAI_API_KEY") 
                print("   - AZURE_DEPLOYMENT_CHAT")
                print("   - AZURE_DEPLOYMENT_EMBEDDING")
        except Exception as e:
            print(f"Error initializing IT Helpdesk Bot: {e}")
            print("Falling back to limited mode")
    
    def _setup_rag_system(self):
        """Setup RAG system with mock IT documents using Azure OpenAI"""
        # Mock IT helpdesk documents
        mock_docs = [
            "How to reset password: Visit company portal, click 'Forgot Password', enter email, check inbox for reset link.",
            "Computer running slow: First restart computer, close unnecessary applications, run antivirus scan, check disk space.",
            "VPN connection issues: Download VPN client from IT portal, install, enter credentials, contact IT if still failing.",
            "Printer not working: Check power cable, ensure printer is online, check ink/toner levels, restart print spooler service.",
            "Email not syncing: Check internet connection, verify email settings, restart email client, contact IT for Exchange issues.",
            "Software installation: Use Software Center for approved apps, request new software through IT ticket system.",
            "WiFi connectivity problems: Forget and reconnect to network, restart network adapter, check with IT for network issues.",
            "Blue screen errors: Note error code, restart in safe mode, run memory diagnostic, contact IT with error details."
        ]
        
        # Initialize Azure OpenAI embeddings (force correct model and api_version)
        embeddings = AzureOpenAIEmbeddings(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            azure_deployment=AZURE_DEPLOYMENT_EMBEDDING,
            api_key=AZURE_EMBEDDING_KEY,
            api_version=AZURE_OPENAI_API_VERSION,
            model="text-embedding-3-small"
        )
        
        # Create FAISS vectorstore
        self.vectorstore = FAISS.from_texts(mock_docs, embedding=embeddings)
        
        # Initialize Azure Chat OpenAI
        llm = AzureChatOpenAI(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            azure_deployment=AZURE_DEPLOYMENT_CHAT,
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION,
            temperature=0.3
        )
        
        # Setup retrieval chain
        self.retrieval_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 3}),
            return_source_documents=True
        )
        
        print("✅ IT Helpdesk Bot initialized with Azure OpenAI RAG + Function Calling")
    
    def _define_functions(self):
        """Define available functions for function calling"""
        return [
            {
                "name": "check_system_status",
                "description": "Check status of IT systems and devices by device ID",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "device_id": {
                            "type": "string",
                            "description": "Device unique identifier (e.g., printer01, router23, server07)"
                        }
                    },
                    "required": ["device_id"]
                }
            },
            {
                "name": "create_it_ticket",
                "description": "Create an IT support ticket for complex issues",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "issue_type": {
                            "type": "string",
                            "description": "Type of issue (hardware, software, network, security)"
                        },
                        "priority": {
                            "type": "string",
                            "description": "Priority level (low, medium, high, critical)"
                        },
                        "description": {
                            "type": "string",
                            "description": "Detailed description of the issue"
                        }
                    },
                    "required": ["issue_type", "priority", "description"]
                }
            }
        ]
    
    def check_system_status(self, device_id: str) -> str:
        """Mock function to check system status"""
        status_map = {
            "printer01": "🟢 Online and functioning normally",
            "printer02": "🟡 Online but low on toner",
            "router23": "🔴 Offline - requires restart", 
            "router24": "🟢 Online with good signal strength",
            "server07": "🟡 Online but high CPU usage (85%)",
            "server08": "🟢 Online with normal performance",
            "workstation15": "🔴 Offline - last seen 2 hours ago",
            "workstation16": "🟢 Online and updated"
        }
        return status_map.get(device_id, f"❓ Device '{device_id}' not found in monitoring system")
    
    def create_it_ticket(self, issue_type: str, priority: str, description: str) -> str:
        """Mock function to create IT ticket"""
        import random
        ticket_id = f"IT-{random.randint(1000, 9999)}"
        
        priority_emoji = {
            "low": "🟢",
            "medium": "🟡", 
            "high": "🟠",
            "critical": "🔴"
        }
        
        return f"""🎫 IT Ticket Created Successfully!

**Ticket ID:** {ticket_id}
**Type:** {issue_type.title()}
**Priority:** {priority_emoji.get(priority, '⚪')} {priority.upper()}
**Description:** {description}
**Status:** Open
**Assigned:** IT Support Team

You will receive email updates on ticket progress."""
    
    def _execute_function(self, function_name: str, arguments: dict) -> str:
        """Execute the requested function"""
        if function_name == "check_system_status":
            return self.check_system_status(arguments.get("device_id", ""))
        elif function_name == "create_it_ticket":
            return self.create_it_ticket(
                arguments.get("issue_type", ""),
                arguments.get("priority", "medium"),
                arguments.get("description", "")
            )
        else:
            return f"❌ Unknown function: {function_name}"
    
    def get_response(self, user_input: str) -> str:
        """Get response using RAG + Function Calling"""
        try:
            # First, try RAG retrieval
            rag_response = ""
            if self.retrieval_chain:
                try:
                    # Convert chat_history to the format expected by LangChain
                    formatted_history = []
                    for q, a in self.chat_history[-5:]:  # Last 5 exchanges
                        formatted_history.extend([
                            {"role": "user", "content": q},
                            {"role": "assistant", "content": a}
                        ])
                    
                    rag_result = self.retrieval_chain({"question": user_input, "chat_history": formatted_history})
                    rag_response = rag_result.get('answer', '')
                    
                    # Check if we have good sources
                    sources = rag_result.get('source_documents', [])
                    if sources:
                        rag_response += f"\n\n📚 **Knowledge Base Sources:** {len(sources)} relevant documents found"
                        
                except Exception as e:
                    print(f"RAG retrieval error: {e}")
            
            # Try function calling for specific system queries
            function_response = ""
            try:
                messages = [
                    {"role": "system", "content": "You are an IT helpdesk assistant. Use functions when users ask about system status or need to create tickets."},
                    {"role": "user", "content": user_input}
                ]
                
                response = openai_client.chat.completions.create(
                    model=AZURE_DEPLOYMENT_CHAT,
                    messages=messages,
                    functions=self.functions,
                    function_call="auto"
                )
                
                choice = response.choices[0]
                message = choice.message
                
                if hasattr(message, 'function_call') and message.function_call:
                    func_name = message.function_call.name
                    try:
                        args = json.loads(message.function_call.arguments)
                        function_response = self._execute_function(func_name, args)
                    except json.JSONDecodeError:
                        function_response = "❌ Error parsing function arguments"
                        
            except Exception as e:
                print(f"Function calling error: {e}")
            
            # Combine responses
            final_response = ""
            
            if function_response:
                final_response = f"🔧 **System Check:**\n{function_response}"
                if rag_response:
                    final_response += f"\n\n💡 **Additional Help:**\n{rag_response}"
            elif rag_response:
                final_response = f"💡 **IT Support:**\n{rag_response}"
            else:
                # Fallback response
                final_response = """🤖 **IT Helpdesk Assistant**

I can help you with:
• Password resets and account issues
• Computer performance problems  
• Network and VPN connectivity
• Printer and hardware support
• Software installation requests
• System status checks (try: "check status of printer01")
• Creating IT tickets (try: "create a ticket for broken laptop")

What IT issue can I help you resolve today?"""
            
            # Update chat history
            self.chat_history.append((user_input, final_response))
            
            # Keep history manageable
            if len(self.chat_history) > 10:
                self.chat_history = self.chat_history[-10:]
            
            return final_response
            
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def reset_conversation(self):
        """Reset chat history"""
        self.chat_history.clear()
    
    def get_available_devices(self) -> str:
        """Get list of devices available for status check"""
        devices = [
            "🖨️ **Printers:** printer01, printer02", 
            "🌐 **Routers:** router23, router24",
            "🖥️ **Servers:** server07, server08", 
            "💻 **Workstations:** workstation15, workstation16"
        ]
        return "**Available Devices for Status Check:**\n" + "\n".join(devices)

# Global instance
it_helpdesk_bot = ITHelpdeskBot()

def get_it_helpdesk_response(question: str) -> str:
    """Get response from IT helpdesk bot"""
    return it_helpdesk_bot.get_response(question)

def reset_it_helpdesk_conversation():
    """Reset IT helpdesk conversation"""
    it_helpdesk_bot.reset_conversation()

def get_it_device_list() -> str:
    """Get list of available devices"""
    return it_helpdesk_bot.get_available_devices()
