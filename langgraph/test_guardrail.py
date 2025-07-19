"""
Test Guardrail và Vietnamese Response
Kiểm tra khả năng chatbot từ chối trả lời câu hỏi không liên quan và trả lời bằng tiếng Việt
"""

from chat_state import ChatState
from orchestration_agent import master_agent
import time

# Test cases để kiểm tra guardrail
guardrail_test_cases = [
    # Câu hỏi KHÔNG liên quan đến ô tô - phải bị từ chối
    "Hướng dẫn nấu phở bò ngon",
    "Dự báo thời tiết ngày mai ở Hà Nội", 
    "Cách học tiếng Anh hiệu quả",
    "Recipe for chocolate cake",
    "What is quantum physics?",
    "Giá vàng hôm nay thế nào?",
    "Cách chăm sóc cây xanh",
    
    # Câu hỏi liên quan đến ô tô - phải được trả lời
    "Xe nào tốt nhất dưới 1 tỷ đồng?",
    "Honda Civic có tốt không?",
    "Tin tức về xe điện mới nhất",
    "Cách bảo dưỡng xe ô tô",
    "So sánh Toyota và Honda",
    
    # Câu hỏi biên giới - cần xem xét
    "Giá xăng hôm nay", # liên quan gián tiếp đến ô tô
    "Luật giao thông mới nhất", # liên quan đến ô tô
    "Xe máy nào tốt?" # không phải ô tô nhưng là vehicle
]

def test_guardrail_question(question, expected_blocked=False):
    """Test một câu hỏi và kiểm tra guardrail"""
    print(f"\n🔍 Test: {question}")
    print(f"Expected blocked: {expected_blocked}")
    
    start_time = time.time()
    
    try:
        # Gửi câu hỏi qua master agent
        result = master_agent.process_query(question)
        response = result.get("answer", "")
        
        elapsed = time.time() - start_time
        
        # Kiểm tra xem có bị block không
        is_blocked = "🚫 Xin lỗi" in response and "chỉ có thể trả lời" in response
        
        print(f"⏱️  Time: {elapsed:.2f}s")
        print(f"🤖 Response preview: {response[:100]}...")
        print(f"🛡️  Blocked: {is_blocked}")
        
        # Kiểm tra tính đúng đắn của guardrail
        if expected_blocked and is_blocked:
            print("✅ PASS: Correctly blocked invalid question")
        elif not expected_blocked and not is_blocked:
            print("✅ PASS: Correctly allowed valid question")  
        elif expected_blocked and not is_blocked:
            print("❌ FAIL: Should have blocked but didn't")
        else:
            print("❌ FAIL: Blocked valid automotive question")
            
        return {
            "question": question,
            "expected_blocked": expected_blocked,
            "actually_blocked": is_blocked,
            "response": response,
            "time": elapsed,
            "correct": (expected_blocked == is_blocked)
        }
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return {
            "question": question,
            "expected_blocked": expected_blocked,
            "actually_blocked": False,
            "response": f"Error: {str(e)}",
            "time": time.time() - start_time,
            "correct": False
        }

def run_guardrail_tests():
    """Chạy tất cả test cases"""
    print("🛡️ GUARDRAIL & VIETNAMESE RESPONSE TEST")
    print("=" * 60)
    
    results = []
    
    print("\n🚫 TESTING INVALID QUESTIONS (Should be blocked)")
    print("-" * 50)
    
    invalid_questions = [
        "Hướng dẫn nấu phở bò ngon",
        "Dự báo thời tiết ngày mai ở Hà Nội", 
        "Cách học tiếng Anh hiệu quả",
        "Recipe for chocolate cake",
        "What is quantum physics?",
        "Giá vàng hôm nay thế nào?",
        "Cách chăm sóc cây xanh"
    ]
    
    for question in invalid_questions:
        result = test_guardrail_question(question, expected_blocked=True)
        results.append(result)
    
    print("\n✅ TESTING VALID AUTOMOTIVE QUESTIONS (Should be answered)")
    print("-" * 50)
    
    valid_questions = [
        "Xe nào tốt nhất dưới 1 tỷ đồng?",
        "Honda Civic có tốt không?", 
        "Tin tức về xe điện mới nhất",
        "Cách bảo dưỡng xe ô tô",
        "So sánh Toyota và Honda"
    ]
    
    for question in valid_questions:
        result = test_guardrail_question(question, expected_blocked=False)
        results.append(result)
    
    print("\n🤔 TESTING BORDER CASES")
    print("-" * 50)
    
    border_questions = [
        ("Giá xăng hôm nay", False), # Should allow - related to cars
        ("Luật giao thông mới nhất", False), # Should allow - traffic laws
        ("Xe máy nào tốt?", True) # Should block - not cars
    ]
    
    for question, should_block in border_questions:
        result = test_guardrail_question(question, expected_blocked=should_block)
        results.append(result)
    
    # Tổng kết
    print(f"\n📊 TEST SUMMARY")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r["correct"])
    failed_tests = total_tests - passed_tests
    
    print(f"Total tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"🎯 Success rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests > 0:
        print(f"\n🔍 FAILED TESTS:")
        for result in results:
            if not result["correct"]:
                print(f"❌ {result['question'][:50]}... (Expected blocked: {result['expected_blocked']}, Actually blocked: {result['actually_blocked']})")
    
    # Test Vietnamese responses
    print(f"\n🇻🇳 VIETNAMESE RESPONSE TEST")
    print("-" * 40)
    
    vietnamese_test = test_guardrail_question("Xe nào phù hợp cho gia đình?", expected_blocked=False)
    response = vietnamese_test["response"]
    
    # Check for Vietnamese characters and phrases
    vietnamese_indicators = [
        "xe", "ô tô", "phù hợp", "gợi ý", "tôi", "bạn", 
        "triệu", "tỷ", "tính năng", "an toàn"
    ]
    
    vietnamese_score = sum(1 for indicator in vietnamese_indicators if indicator.lower() in response.lower())
    
    print(f"Vietnamese indicators found: {vietnamese_score}/{len(vietnamese_indicators)}")
    print(f"Response contains Vietnamese: {'✅ YES' if vietnamese_score >= 3 else '❌ NO'}")
    
    return {
        "total_tests": total_tests,
        "passed": passed_tests,
        "failed": failed_tests,
        "success_rate": (passed_tests/total_tests)*100,
        "results": results,
        "vietnamese_score": vietnamese_score
    }

if __name__ == "__main__":
    test_results = run_guardrail_tests()
    
    # Save results
    import json
    with open("guardrail_test_results.json", "w", encoding="utf-8") as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to guardrail_test_results.json")
    
    # Recommendations
    success_rate = test_results["success_rate"]
    
    print(f"\n💡 RECOMMENDATIONS")
    print("-" * 30)
    
    if success_rate >= 90:
        print("🌟 Excellent! Guardrail working as expected.")
    elif success_rate >= 75:
        print("👍 Good performance. Minor tweaks might be needed.")
        print("Consider refining the intent classification prompt.")
    else:
        print("⚠️  Guardrail needs improvement:")
        print("1. Review intent classification keywords")
        print("2. Add more specific automotive context")
        print("3. Consider using a two-step validation")
    
    vietnamese_score = test_results["vietnamese_score"]
    if vietnamese_score >= 5:
        print("🇻🇳 Vietnamese responses working well!")
    else:
        print("🔄 Consider improving Vietnamese language prompts")
