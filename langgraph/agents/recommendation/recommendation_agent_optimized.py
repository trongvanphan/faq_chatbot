"""
Optimized Car Recommendation Agent
Fast version with reduced LLM calls and better caching.
"""

from typing import Dict, List, Any, Optional
from chat_state import ChatState
from services import get_azure_llm, get_vectordb
from .car_database import VALID_PURPOSES, VALID_PRIORITIES, VALID_BRAND_ORIGINS
import json
import re
import time
from functools import lru_cache


class OptimizedCarRecommendationAgent:
    """
    Optimized car recommendation agent with reduced latency.
    """
    
    def __init__(self):
        self.vectordb = get_vectordb()
        self.llm = get_azure_llm()
        # Cache for common queries
        self._query_cache = {}
        
    @lru_cache(maxsize=100)
    def _cached_criteria_extraction(self, question_hash: str, question: str) -> str:
        """Cache LLM responses for common criteria extraction."""
        extraction_prompt = f"""
        Trích xuất thông tin mua xe từ câu hỏi: "{question}"
        
        Chỉ trả về JSON với các trường sau (dùng null nếu không có):
        {{"budget_max": <số tiền hoặc null>, "purposes": [<từ: {VALID_PURPOSES}>], "priorities": [<từ: {VALID_PRIORITIES}>], "brand_preference": "<từ: {VALID_BRAND_ORIGINS} hoặc null>", "passengers": <số người hoặc null>}}
        """
        
        response = self.llm.invoke(extraction_prompt)
        return response.content.strip()
    
    def extract_user_criteria_fast(self, question: str) -> Dict[str, Any]:
        """Fast criteria extraction with caching and fallback."""
        question_lower = question.lower()
        
        # Quick keyword-based extraction first
        criteria = self._quick_keyword_extraction(question_lower)
        
        # Only use LLM if we need complex analysis
        if not any([criteria["budget_max"], criteria["purposes"], criteria["brand_preference"]]):
            try:
                question_hash = str(hash(question))
                llm_response = self._cached_criteria_extraction(question_hash, question)
                
                # Simple JSON extraction
                if "{" in llm_response and "}" in llm_response:
                    json_str = llm_response[llm_response.find("{"):llm_response.rfind("}")+1]
                    llm_criteria = json.loads(json_str)
                    criteria.update({k: v for k, v in llm_criteria.items() if v})
            except:
                pass  # Use keyword extraction fallback
                
        return criteria
    
    def _quick_keyword_extraction(self, question_lower: str) -> Dict[str, Any]:
        """Ultra-fast keyword-based extraction."""
        criteria = {
            "budget_max": None,
            "purposes": [],
            "priorities": [],
            "brand_preference": None,
            "passengers": None
        }
        
        # Budget extraction (Vietnamese patterns)
        budget_patterns = [
            r'(\d+)\s*tỷ',  # 1 tỷ, 1.5 tỷ
            r'(\d+)\s*triệu',  # 800 triệu
            r'dưới\s*(\d+)\s*tỷ',  # dưới 1 tỷ
            r'trong\s*tầm\s*(\d+)\s*tỷ',  # trong tầm 1 tỷ
        ]
        
        for pattern in budget_patterns:
            match = re.search(pattern, question_lower)
            if match:
                amount = int(match.group(1))
                if 'triệu' in pattern:
                    criteria["budget_max"] = amount * 1000000
                elif 'tỷ' in pattern:
                    criteria["budget_max"] = amount * 1000000000
                break
        
        # Purpose extraction (Vietnamese)
        purpose_map = {
            "gia đình": "family",
            "family": "family", 
            "đi làm": "daily_commute",
            "commute": "daily_commute",
            "kinh doanh": "business",
            "business": "business",
            "du lịch": "leisure",
            "weekend": "leisure"
        }
        
        for vn_term, purpose in purpose_map.items():
            if vn_term in question_lower:
                criteria["purposes"].append(purpose)
        
        # Brand extraction (Vietnamese)
        brand_map = {
            "nhật": "Japanese",
            "japanese": "Japanese",
            "hàn": "Korean", 
            "korean": "Korean",
            "đức": "German",
            "german": "German",
            "mỹ": "American",
            "american": "American"
        }
        
        for brand_term, brand in brand_map.items():
            if brand_term in question_lower:
                criteria["brand_preference"] = brand
                break
                
        return criteria
    
    def query_cars_optimized(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Optimized ChromaDB query with better search terms."""
        cache_key = str(sorted(criteria.items()))
        if cache_key in self._query_cache:
            return self._query_cache[cache_key]
        
        # Build targeted query
        query_terms = []
        
        # Budget terms
        budget = criteria.get("budget_max", 0)
        if budget:
            if budget < 500000000:  # < 500M VND
                query_terms.append("affordable economical budget")
            elif budget < 1500000000:  # < 1.5B VND  
                query_terms.append("mid-range value practical")
            else:
                query_terms.append("luxury premium high-end")
        
        # Purpose terms
        purposes = criteria.get("purposes", [])
        if "family" in purposes:
            query_terms.append("family sedan SUV spacious safe")
        if "daily_commute" in purposes:
            query_terms.append("fuel efficient compact reliable")
        if "business" in purposes:
            query_terms.append("professional luxury sedan")
            
        # Brand terms
        brand = criteria.get("brand_preference")
        if brand:
            query_terms.append(brand.lower())
            
        query = " ".join(query_terms) if query_terms else "car automobile vehicle"
        
        # Reduced k for faster processing
        try:
            results = self.vectordb.similarity_search_with_score(query, k=6)
            car_data = [{
                "content": doc.page_content[:1000],  # Truncate for speed
                "metadata": doc.metadata,
                "score": score
            } for doc, score in results]
            
            # Cache result
            self._query_cache[cache_key] = car_data
            return car_data
            
        except Exception as e:
            print(f"ChromaDB query error: {e}")
            return []
    
    def generate_fast_recommendation(self, question: str, car_data: List[Dict], criteria: Dict) -> str:
        """Single LLM call for fast recommendation generation."""
        if not car_data:
            return self._get_quick_fallback()
            
        # Combine top car data efficiently
        top_cars_text = "\n\n".join([
            f"Car {i+1}: {item['content'][:500]}"  # Limit text per car
            for i, item in enumerate(car_data[:3])  # Only top 3
        ])
        
        # Streamlined prompt for faster processing
        prompt = f"""
        Nhu cầu của người dùng: {question}
        Ngân sách: {criteria.get('budget_max', 'không xác định')}
        Mục đích sử dụng: {criteria.get('purposes', [])}
        
        Các xe có sẵn:
        {top_cars_text}
        
        Hãy gợi ý 3 xe phù hợp theo định dạng sau:
        
        🚗 **Top 3 Gợi Ý Xe Cho Bạn:**
        
        **1. [Tên xe]** - [Giá bán]
        ✅ Tại sao phù hợp: [lý do ngắn gọn]
        📊 Thông số chính: [tính năng nổi bật]
        
        **2. [Tên xe]** - [Giá bán] 
        ✅ Tại sao phù hợp: [lý do ngắn gọn]
        📊 Thông số chính: [tính năng nổi bật]
        
        **3. [Tên xe]** - [Giá bán]
        ✅ Tại sao phù hợp: [lý do ngắn gọn] 
        📊 Thông số chính: [tính năng nổi bật]
        
        **💡 Lựa chọn hàng đầu của tôi:** [#1 với lý do ngắn]
        
        Trả lời hoàn toàn bằng tiếng Việt.
        """
        
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            return self._format_emergency_response(car_data)
    
    def _get_quick_fallback(self) -> str:
        """Quick fallback when no data available."""
        return """
        🚗 **Cần thêm thông tin để gợi ý xe phù hợp:**
        
        📋 Vui lòng cho biết:
        • **Ngân sách**: Trong tầm bao nhiêu? (VD: 800 triệu, 1.2 tỷ)
        • **Mục đích**: Gia đình, đi làm, kinh doanh?
        • **Số người**: Cần xe mấy chỗ ngồi?
        
        Tôi sẽ gợi ý xe phù hợp ngay! 🚀
        """
    
    def _format_emergency_response(self, car_data: List[Dict]) -> str:
        """Emergency formatting without LLM."""
        if not car_data:
            return self._get_quick_fallback()
            
        response = "🚗 **Gợi ý xe phù hợp:**\n\n"
        for i, car in enumerate(car_data[:3], 1):
            content = car["content"][:200]  # Brief excerpt
            response += f"**{i}. Xe được đề xuất**\n"
            response += f"📋 {content}...\n"
            response += f"⭐ Điểm phù hợp: {1 - car['score']:.2f}\n\n"
            
        return response + "\n💬 Bạn muốn biết thêm chi tiết xe nào?"
    
    def process_recommendation_fast(self, state: ChatState) -> ChatState:
        """Main optimized processing method."""
        start_time = time.time()
        question = state["question"]
        
        try:
            # Step 1: Fast criteria extraction
            criteria = self.extract_user_criteria_fast(question)
            
            # Step 2: Optimized database query
            car_data = self.query_cars_optimized(criteria)
            
            # Step 3: Single LLM call for recommendation
            response = self.generate_fast_recommendation(question, car_data, criteria)
            
            # Add performance info in debug mode
            elapsed = time.time() - start_time
            if elapsed > 3:  # Log slow queries
                print(f"Recommendation took {elapsed:.2f}s - consider further optimization")
                
            return {**state, "answer": response}
            
        except Exception as e:
            print(f"Fast recommendation error: {e}")
            fallback_response = self._get_quick_fallback()
            return {**state, "answer": fallback_response}


# Create optimized instance
optimized_car_agent = OptimizedCarRecommendationAgent()


def recommend_car_fast(state: ChatState) -> ChatState:
    """Fast entry point for optimized car recommendations."""
    return optimized_car_agent.process_recommendation_fast(state)
