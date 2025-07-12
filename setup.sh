#!/bin/bash
# Setup script for FAQ Chatbot with LangChain and ChromaDB

echo "🚀 Setting up FAQ Chatbot with LangChain and ChromaDB..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing requirements..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file from template..."
    cp .env.example .env
    echo "📝 Please edit .env file and add your OpenAI API key!"
fi

# Create chroma_db directory
if [ ! -d "chroma_db" ]; then
    echo "🗄️ Creating ChromaDB directory..."
    mkdir chroma_db
fi

echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file and add your OpenAI API key"
echo "2. Activate virtual environment: source venv/bin/activate"
echo "3. Run the application: python app.py"
echo ""
echo "🔗 The app will be available at http://127.0.0.1:7860"
