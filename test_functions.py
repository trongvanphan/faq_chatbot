#!/usr/bin/env python3
"""
Test script for FAQ Chatbot with Function Calling
"""

from faq_bot import get_faq_answer_with_functions, get_faq_answer

def test_function_calling():
    """Test the function calling capabilities"""
    
    print("=== FAQ Chatbot với Function Calling ===\n")
    
    # Test cases
    test_questions = [
        "Gợi ý cho tôi một số xe SUV",
        "Khi nào tôi nên thay dầu xe?",
        "Cho tôi mẹo tiết kiệm nhiên liệu",
        "Tìm thông tin về xe điện",
        "Tôi muốn biết về xe sedan",
        "Làm sao để bảo dưỡng xe?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"🔹 Test {i}: {question}")
        print("📤 Function Calling Response:")
        try:
            response = get_faq_answer_with_functions(question)
            print(f"📥 {response}")
        except Exception as e:
            print(f"❌ Lỗi: {e}")
        print("-" * 80)

def test_comparison():
    """Compare function calling vs traditional approach"""
    
    print("\n=== So sánh Function Calling vs Traditional ===\n")
    
    question = "Gợi ý cho tôi xe SUV"
    
    print(f"❓ Câu hỏi: {question}\n")
    
    print("🔧 Function Calling Response:")
    try:
        fc_response = get_faq_answer_with_functions(question)
        print(f"📥 {fc_response}")
    except Exception as e:
        print(f"❌ Lỗi: {e}")
    
    print("\n📖 Traditional FAQ Response:")
    try:
        trad_response = get_faq_answer(question)
        print(f"📥 {trad_response}")
    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    test_function_calling()
    test_comparison()
