#!/usr/bin/env python3
"""
Test runner for FAQ Chatbot components
"""

import os

def test_imports():
    """Test if all imports work correctly"""
    try:
        print("🧪 Testing basic imports...")
        import os
        print("✅ os - OK")
        
        # Test optional imports
        try:
            import gradio as gr
            print("✅ gradio - OK")
        except ImportError:
            print("❌ gradio - Not installed (run: pip install gradio)")
        
        try:
            import openai
            print("✅ openai - OK")
        except ImportError:
            print("❌ openai - Not installed (run: pip install openai)")
            
        try:
            import chromadb
            print("✅ chromadb - OK")
        except ImportError:
            print("❌ chromadb - Not installed (run: pip install chromadb)")
            
        try:
            import langchain
            print("✅ langchain - OK")
        except ImportError:
            print("❌ langchain - Not installed (run: pip install langchain)")
            
        print("\n🔧 To install all dependencies:")
        print("pip install -r requirements.txt")
        
    except Exception as e:
        print(f"❌ Error testing imports: {e}")

def test_env_config():
    """Test environment configuration"""
    print("\n🔍 Testing environment configuration...")
    
    if os.path.exists(".env"):
        print("✅ .env file exists")
        
        # Check for OpenAI API key
        from dotenv import load_dotenv
        load_dotenv()
        
        if os.getenv("OPENAI_API_KEY"):
            print("✅ OPENAI_API_KEY is set")
        else:
            print("❌ OPENAI_API_KEY not found in .env")
    else:
        print("❌ .env file not found")
        print("💡 Copy .env.example to .env and add your OpenAI API key")

def test_directory_structure():
    """Test if required directories exist"""
    print("\n📁 Testing directory structure...")
    
    required_files = [
        "app.py",
        "automotive_bot.py", 
        "kb_manager.py",
        "context_manager.py",
        "faq_bot.py",
        "faq_data.py",
        "requirements.txt"
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - Missing")
    
    # Check for chroma_db directory
    if os.path.exists("chroma_db"):
        print("✅ chroma_db/ directory exists")
    else:
        print("❌ chroma_db/ directory not found")
        print("💡 Will be created automatically on first run")

if __name__ == "__main__":
    print("🚀 FAQ Chatbot - System Test\n")
    
    test_imports()
    test_env_config()
    test_directory_structure()
    
    print("\n✨ Test complete!")
    print("\n📋 Next steps:")
    print("1. Install missing dependencies: pip install -r requirements.txt")
    print("2. Configure .env file with your OpenAI API key")
    print("3. Run the app: python app.py")
