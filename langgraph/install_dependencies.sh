#!/bin/bash
# Installation script for enhanced RAG dependencies

echo "🚀 Installing enhanced RAG dependencies..."

# Core dependencies
echo "📦 Installing core dependencies..."
pip install streamlit python-dotenv

# LangChain ecosystem
echo "🔗 Installing LangChain ecosystem..."
pip install langchain langchain-openai langchain-community langchain-core langgraph

# Vector database
echo "🗄️ Installing ChromaDB..."
pip install chromadb

# Document processing
echo "📄 Installing document processing libraries..."
pip install PyPDF2 python-docx docx2txt

# Enhanced parsing (optional)
echo "✨ Installing enhanced parsing (MarkItDown)..."
pip install markitdown || echo "⚠️ MarkItDown installation failed - fallback parsing will be used"

# Azure OpenAI
echo "☁️ Installing OpenAI client..."
pip install openai

# Additional utilities
echo "🛠️ Installing additional utilities..."
pip install typing-extensions pydantic

echo "✅ Installation complete!"
echo "💡 Note: If MarkItDown failed to install, the system will use fallback parsing methods."
echo "🚀 You can now run: streamlit run app.py"
