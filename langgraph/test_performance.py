"""
Performance Test Script
So sánh tốc độ giữa agent gốc và agent được tối ưu
"""

import time
from chat_state import ChatState
from agents.recommendation.recommendation_agent import car_recommendation_agent
from agents.recommendation.recommendation_agent_optimized import optimized_car_agent

# Test cases tiếng Việt
test_cases = [
    "Tôi muốn mua xe với ngân sách 800 triệu cho gia đình 4 người",
    "Xe nào tốt nhất dưới 1 tỷ đồng để đi làm hàng ngày?",
    "Gợi ý xe luxury trong tầm 2 tỷ cho doanh nhân",
    "Xe hybrid nào đáng mua nhất ở Việt Nam?",
    "Tôi cần xe 7 chỗ cho gia đình đông người"
]

def test_agent_performance(agent, agent_name, test_question):
    """Test performance của một agent"""
    print(f"\n🚀 Testing {agent_name}...")
    print(f"Question: {test_question}")
    
    start_time = time.time()
    
    try:
        # Tạo state
        state = ChatState(question=test_question, answer="")
        
        # Process request
        if hasattr(agent, 'process_recommendation_request'):
            result = agent.process_recommendation_request(state)
        else:
            result = agent.process_recommendation_fast(state)
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        print(f"⏱️  Time taken: {elapsed:.2f} seconds")
        print(f"📝 Response length: {len(result['answer'])} characters")
        print(f"✅ Success: {bool(result['answer'])}")
        
        return elapsed, len(result['answer'])
        
    except Exception as e:
        end_time = time.time()
        elapsed = end_time - start_time
        print(f"❌ Error: {str(e)}")
        print(f"⏱️  Time before error: {elapsed:.2f} seconds")
        return elapsed, 0

def run_performance_comparison():
    """Chạy so sánh hiệu suất"""
    print("🔥 CAR RECOMMENDATION AGENT PERFORMANCE TEST")
    print("=" * 60)
    
    original_times = []
    optimized_times = []
    
    for i, question in enumerate(test_cases, 1):
        print(f"\n📋 TEST CASE {i}/{len(test_cases)}")
        print("-" * 40)
        
        # Test original agent
        orig_time, orig_length = test_agent_performance(
            car_recommendation_agent, 
            "Original Agent", 
            question
        )
        
        # Test optimized agent  
        opt_time, opt_length = test_agent_performance(
            optimized_car_agent,
            "Optimized Agent",
            question
        )
        
        # Calculate improvement
        if orig_time > 0:
            improvement = ((orig_time - opt_time) / orig_time) * 100
            print(f"🚀 Speed improvement: {improvement:.1f}% faster")
        
        original_times.append(orig_time)
        optimized_times.append(opt_time)
        
        print("-" * 40)
    
    # Overall statistics
    print(f"\n📊 OVERALL RESULTS")
    print("=" * 60)
    
    avg_original = sum(original_times) / len(original_times)
    avg_optimized = sum(optimized_times) / len(optimized_times)
    overall_improvement = ((avg_original - avg_optimized) / avg_original) * 100
    
    print(f"⏱️  Average Original Time: {avg_original:.2f} seconds")
    print(f"⏱️  Average Optimized Time: {avg_optimized:.2f} seconds")
    print(f"🚀 Overall Speed Improvement: {overall_improvement:.1f}% faster")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS")
    print("-" * 30)
    if avg_optimized < 3:
        print("✅ Optimized agent meets performance target (<3s)")
    else:
        print("⚠️  Still slower than target. Consider further optimizations:")
        print("   • Reduce ChromaDB query size")
        print("   • Implement more aggressive caching")
        print("   • Pre-process common queries")
    
    return {
        "avg_original": avg_original,
        "avg_optimized": avg_optimized,
        "improvement_percent": overall_improvement,
        "individual_times": {
            "original": original_times,
            "optimized": optimized_times
        }
    }

if __name__ == "__main__":
    results = run_performance_comparison()
    
    # Save results to file for analysis
    import json
    with open("performance_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to performance_test_results.json")
