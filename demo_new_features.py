#!/usr/bin/env python3
"""
Demo script for testing new Automotive Bot and KB Management features
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_automotive_bot():
    """Test Automotive Bot functionality"""
    print("\n🤖 Testing Automotive Bot...")
    
    try:
        from automotive_bot import get_automotive_response, get_automotive_info, reset_automotive_conversation
        
        # Test basic question
        print("\n🔸 Testing basic automotive question:")
        question = "Xe hybrid hoạt động như thế nào?"
        response = get_automotive_response(question)
        print(f"Q: {question}")
        print(f"A: {response[:200]}...")
        
        # Test conversation info
        info = get_automotive_info()
        print(f"\n📊 Conversation info: {info}")
        
        # Reset conversation
        reset_automotive_conversation()
        print("🔄 Conversation reset completed")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_kb_manager():
    """Test Knowledge Base Manager functionality"""
    print("\n📚 Testing KB Manager...")
    
    try:
        from kb_manager import get_kb_stats, search_kb
        
        # Test KB stats
        print("\n🔸 Testing KB statistics:")
        stats = get_kb_stats()
        print(f"Stats: {stats}")
        
        # Test search (even if empty)
        print("\n🔸 Testing KB search:")
        results = search_kb("xe điện", k=2)
        print(f"Search results: {len(results)} found")
        for i, result in enumerate(results[:2], 1):
            print(f"  {i}. Score: {result['similarity_score']:.2f}")
            print(f"     Content: {result['content'][:100]}...")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_app_integration():
    """Test app.py integration"""
    print("\n🎯 Testing App Integration...")
    
    try:
        # Test imports from app.py
        from automotive_bot import get_automotive_response
        from kb_manager import get_kb_stats
        from faq_bot import get_faq_answer
        
        print("✅ All imports successful")
        
        # Test basic functionality
        print("\n🔸 Testing integrated responses:")
        
        # Test automotive bot
        auto_response = get_automotive_response("Gợi ý xe SUV")
        print(f"Automotive Bot: {auto_response[:100]}...")
        
        # Test KB stats
        kb_stats = get_kb_stats()
        print(f"KB Stats: {kb_stats}")
        
        # Test original FAQ bot
        faq_response = get_faq_answer("Xe số sàn và số tự động khác gì?")
        print(f"FAQ Bot: {faq_response[:100]}...")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_environment():
    """Test environment configuration"""
    print("\n⚙️ Testing Environment...")
    
    # Check environment variables
    required_vars = ["OPENAI_API_KEY", "OPENAI_BASE_URL", "MODEL_NAME"]
    for var in required_vars:
        value = os.getenv(var)
        if value:
            display_value = value[:10] + "..." if len(value) > 10 else value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: Not set")
    
    # Check optional directories
    chroma_path = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    if os.path.exists(chroma_path):
        print(f"✅ ChromaDB path exists: {chroma_path}")
    else:
        print(f"⚠️ ChromaDB path will be created: {chroma_path}")

def main():
    """Main demo function"""
    print("🚀 FAQ Chatbot - New Features Demo")
    print("=" * 50)
    
    # Test environment first
    test_environment()
    
    # Test individual components
    automotive_ok = test_automotive_bot()
    kb_ok = test_kb_manager() 
    app_ok = test_app_integration()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Demo Summary:")
    print(f"  🤖 Automotive Bot: {'✅ OK' if automotive_ok else '❌ Failed'}")
    print(f"  📚 KB Manager: {'✅ OK' if kb_ok else '❌ Failed'}")
    print(f"  🎯 App Integration: {'✅ OK' if app_ok else '❌ Failed'}")
    
    if all([automotive_ok, kb_ok, app_ok]):
        print("\n🎉 All tests passed! Ready to run: python app.py")
    else:
        print("\n⚠️ Some tests failed. Check dependencies and configuration.")
        print("💡 Try: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
