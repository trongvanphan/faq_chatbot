import os
from dotenv import load_dotenv
load_dotenv()
import streamlit as st
from knowledge_base import knowledge_base_tab
from chat import chat_tab

st.set_page_config(page_title="RAG Q&A App", layout="wide")
st.title("📚 Automotive ChatBot")

tab1, tab2 = st.tabs(["Chat", "Knowledge Base"])

with tab1:
    chat_tab()
    
with tab2:
    knowledge_base_tab()