import streamlit as st
import re
import os
from dotenv import load_dotenv
from chat_state import ChatState
from orchestration_agent import master_agent
from services import get_azure_llm, get_vectordb

load_dotenv()



def chat_tab():
    st.header("Chat with your documents")
    vectordb = get_vectordb()
    USER_BUBBLE = "background-color:#e6f7ff;padding:12px 16px;border-radius:12px 12px 12px 2px;margin-bottom:4px;display:inline-block;max-width:80%;"
    AI_BUBBLE = "background-color:#f6f6f6;padding:12px 16px;border-radius:12px 12px 2px 12px;margin-bottom:16px;display:inline-block;max-width:80%;"
    
    def format_ai_answer(ans: str) -> str:
        ans = re.sub(r"Step (\d+):", r"\n\1. ", ans)
        ans = re.sub(r"\.\s+", ".\n\n", ans)
        return ans.strip()
    
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
    
    # Display chat history
    for user_msg, ai_msg in st.session_state['chat_history']:
        st.markdown(f'<div style=\"{USER_BUBBLE}\"><b>You:</b> {user_msg}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style=\"{AI_BUBBLE}\"><b>AI:</b> </div>', unsafe_allow_html=True)
        st.markdown(format_ai_answer(ai_msg), unsafe_allow_html=False)
        st.markdown("<hr style='border:0;border-top:1px solid #eee;margin:8px 0;'>", unsafe_allow_html=True)
    
    # Generate answer using master orchestration agent
    if st.session_state['chat_history'] and st.session_state['chat_history'][-1][1] == "...":
        user_msg = st.session_state['chat_history'][-1][0]
    
        with st.spinner("Analyzing your request and finding the best agent..."):
            try:
                # Use master agent to process the query
                result = master_agent.process_query(
                    question=user_msg,
                    chat_history=st.session_state['chat_history'][:-1]
                )
                answer = result.get("answer", "I'm sorry, I couldn't generate a response.")
            except Exception as e:
                st.error(f"Error processing request: {str(e)}")
                answer = "I encountered an error while processing your request. Please try again."
        
        st.session_state['chat_history'][-1] = (user_msg, answer)
        st.rerun()
    
    # Chat input
    user_input = st.chat_input("Ask me anything - I can help with car recommendations, document search, or news!")
    if user_input:
        st.session_state['chat_history'].append((user_input, "..."))
        st.rerun()
    
    # Clear chat button
    if st.button("Clear Chat History"):
        st.session_state['chat_history'] = []
        st.rerun()
    
    # Agent status sidebar
    with st.sidebar:
        st.subheader("🤖 Available Agents")
        agents = master_agent.get_available_agents()
        for agent_name, agent_info in agents.items():
            st.write(f"**{agent_name.title()}:** {agent_info['description']}")
        st.subheader("🧠 Workflow Diagram")
        if st.button("Show LangGraph Workflow"):
            image_bytes = master_agent.get_workflow_image()
            if image_bytes:
                st.image(image_bytes, caption="Master Orchestration Graph", use_column_width=True)
            else:
                st.error("Failed to generate workflow image.")


# Example usage prompts for different agents:
# 
# For recommendation agent:
# "I need a car recommendation for my family of 4 with a budget of $35,000"
# "What car should I buy for daily commuting that's fuel efficient?"
# "Recommend a reliable car for business use under $50,000"
# "I need a car for weekend trips and outdoor adventures"
#
# For document search:
# "Tell me about maintenance schedules"
# "What information do you have about warranty coverage?"
# "Search for troubleshooting guides"
#
# For news search:
# "Show me latest automotive news"
# "What's new in electric vehicles?"
# "Recent updates in car technology"
