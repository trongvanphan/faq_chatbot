import os
from dotenv import load_dotenv
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain_community.vectorstores import Chroma

load_dotenv()

def get_vectordb():
    """
    Get vector database instance - now uses enhanced knowledge base.
    Maintained for backward compatibility.
    """
    try:
        from knowledge_base import knowledge_base
        return knowledge_base.get_vectordb()
    except ImportError:
        # Fallback to direct initialization
        embeddings = AzureOpenAIEmbeddings(
            azure_endpoint=os.getenv("AZURE_OPENAI_EMBEDDING_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_EMBEDDING_API_KEY"),
            model=os.getenv("AZURE_OPENAI_EMBEDDING_MODEL"),
            api_version="2024-07-01-preview"
        )
        return Chroma(persist_directory=".chromadb", embedding_function=embeddings)

def get_azure_llm():
    """Get Azure OpenAI LLM instance."""
    return AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_LLM_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_LLM_API_KEY"),
        model=os.getenv("AZURE_OPENAI_LLM_MODEL"),
        api_version="2024-07-01-preview"
    )
