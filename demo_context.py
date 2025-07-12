#!/usr/bin/env python3
"""
Demo: Context Management and Multi-turn Conversations
This script demonstrates the difference between context-aware and context-unaware conversations
"""

from context_manager import get_contextual_response, reset_conversation, get_conversation_info
from faq_bot import get_faq_answer_with_functions

def demo_without_context():
    """Demonstrate conversation WITHOUT context management"""
    print("=" * 80)
    print("🚫 DEMO: WITHOUT Context Management (Current Implementation)")
    print("=" * 80)
    
    questions = [
        "Gợi ý xe SUV cho tôi",
        "Honda CR-V có ưu điểm gì?",  # Should understand this refers to previous response
        "Giá của nó như thế nào?",    # "nó" refers to Honda CR-V
        "So với Toyota RAV4 thì sao?" # Should remember RAV4 was also mentioned
    ]
    
    print("\n👤 Cuộc trò chuyện bắt đầu...\n")
    
    for i, question in enumerate(questions, 1):
        print(f"👤 User: {question}")
        response = get_faq_answer_with_functions(question)
        print(f"🤖 Bot: {response}")
        print(f"📝 Context: Mỗi câu hỏi được xử lý độc lập - bot không nhớ gì!")
        print("-" * 60)

def demo_with_context():
    """Demonstrate conversation WITH context management"""
    print("\n" + "=" * 80)
    print("✅ DEMO: WITH Context Management (New Implementation)")
    print("=" * 80)
    
    # Reset conversation for clean demo
    reset_conversation()
    
    questions = [
        "Gợi ý xe SUV cho tôi",
        "Honda CR-V có ưu điểm gì?",  # Should understand this refers to previous response
        "Giá của nó như thế nào?",    # "nó" refers to Honda CR-V
        "So với Toyota RAV4 thì sao?" # Should remember RAV4 was also mentioned
    ]
    
    print("\n👤 Cuộc trò chuyện bắt đầu...\n")
    
    for i, question in enumerate(questions, 1):
        print(f"👤 User: {question}")
        
        # Get response with context
        response = get_contextual_response(question)
        print(f"🤖 Bot: {response}")
        
        # Show context information
        context_info = get_conversation_info()
        print(f"📝 Context: {context_info['message_count']} tin nhắn, Topics: {context_info['last_topics']}")
        print(f"💭 Summary: {context_info['context_summary']}")
        print("-" * 60)

def demo_context_features():
    """Demonstrate specific context management features"""
    print("\n" + "=" * 80)
    print("🎯 DEMO: Context Management Features")
    print("=" * 80)
    
    reset_conversation()
    
    scenarios = [
        {
            "title": "1. Remembering Previous Recommendations",
            "conversation": [
                "Gợi ý xe sedan cho tôi",
                "Trong những xe này, xe nào tiết kiệm nhiên liệu nhất?"
            ]
        },
        {
            "title": "2. Understanding References",
            "conversation": [
                "Tôi quan tâm đến Honda Civic",
                "Nó có đắt không?",  # "Nó" = Honda Civic
                "Khi nào tôi nên bảo dưỡng nó?"  # Still talking about Honda Civic
            ]
        },
        {
            "title": "3. Maintaining Topic Flow",
            "conversation": [
                "Cho tôi mẹo tiết kiệm nhiên liệu",
                "Mẹo nào quan trọng nhất?",
                "Còn về áp suất lốp thì sao?"
            ]
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{scenario['title']}")
        print("-" * 40)
        reset_conversation()  # Start fresh for each scenario
        
        for question in scenario['conversation']:
            print(f"👤 {question}")
            response = get_contextual_response(question)
            print(f"🤖 {response[:150]}...")  # Truncate for demo
            print()

def explain_step_by_step():
    """Explain how context management works step by step"""
    print("\n" + "=" * 80)
    print("📚 HOW CONTEXT MANAGEMENT WORKS - STEP BY STEP")
    print("=" * 80)
    
    steps = [
        {
            "step": "1. Message Storage",
            "explanation": "Mỗi tin nhắn (user và bot) được lưu với timestamp",
            "code": """
conversation_history = [
    {"role": "user", "content": "Gợi ý xe SUV", "timestamp": "2025-06-28T10:00:00"},
    {"role": "assistant", "content": "Honda CR-V, Toyota RAV4...", "timestamp": "2025-06-28T10:00:05"}
]"""
        },
        {
            "step": "2. Context Building", 
            "explanation": "Khi có câu hỏi mới, toàn bộ lịch sử được gửi cho AI",
            "code": """
messages = [
    {"role": "system", "content": "Bạn là trợ lý ô tô, nhớ cuộc trò chuyện..."},
    {"role": "user", "content": "Gợi ý xe SUV"},
    {"role": "assistant", "content": "Honda CR-V, Toyota RAV4..."},
    {"role": "user", "content": "Honda CR-V có ưu điểm gì?"}  # Câu hỏi mới
]"""
        },
        {
            "step": "3. Reference Resolution",
            "explanation": "AI hiểu 'Honda CR-V' được đề cập trong câu trả lời trước",
            "code": """
# AI nhận được toàn bộ context nên biết:
# - Honda CR-V được đề cập trong response trước
# - User đang hỏi về xe đó cụ thể
# - Không cần tìm kiếm lại danh sách SUV"""
        },
        {
            "step": "4. Context Summary",
            "explanation": "Tóm tắt chủ đề để quản lý token limit",
            "code": """
context_summary = "Đã tư vấn xe SUV | Quan tâm Honda CR-V"
# Giúp AI nhớ những gì quan trọng ngay cả khi conversation dài"""
        }
    ]
    
    for step_info in steps:
        print(f"\n{step_info['step']}: {step_info['explanation']}")
        print(f"```{step_info['code']}```")
        print()

if __name__ == "__main__":
    print("🎭 CONTEXT MANAGEMENT & MULTI-TURN CONVERSATION DEMO")
    print("This demo shows the difference between context-aware and context-unaware chatbots")
    
    # Show explanations first
    explain_step_by_step()
    
    # Show demos
    demo_without_context()
    demo_with_context() 
    demo_context_features()
    
    print("\n" + "=" * 80)
    print("✨ SUMMARY")
    print("=" * 80)
    print("""
🚫 WITHOUT Context Management:
- Mỗi câu hỏi độc lập
- Không hiểu references ("nó", "xe đó")
- Không nhớ đã nói gì trước đó
- Trải nghiệm như chat với người lạ mỗi lần

✅ WITH Context Management:
- Nhớ toàn bộ cuộc trò chuyện
- Hiểu references và pronouns
- Duy trì flow tự nhiên
- Trải nghiệm như nói chuyện với một người
    """)
    print("=" * 80)
