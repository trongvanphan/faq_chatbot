"""
Car Recommendation Agent
Specialized agent for providing intelligent car recommendations based on user criteria.
"""

from typing import Dict, List, Any, Optional
from chat_state import ChatState
from services import get_azure_llm
from .car_database import CarDatabase, VALID_PURPOSES, VALID_PRIORITIES, VALID_BRAND_ORIGINS
import json
import re


class CarRecommendationAgent:
    """
    Intelligent car recommendation agent that analyzes user needs and provides 
    personalized vehicle recommendations.
    """
    
    def __init__(self):
        self.car_db = CarDatabase()
        self.llm = get_azure_llm()
    
    def extract_user_criteria(self, question: str) -> Dict[str, Any]:
        """
        Extract user criteria from natural language question using LLM.
        """
        extraction_prompt = f"""
        You are an expert at analyzing car buying needs. Extract the following information from the user's question:
        
        User question: "{question}"
        
        Extract and return a JSON object with these fields (use null if not mentioned):
        {{
            "budget_max": <integer or null>,
            "budget_range": "<string range like '20000-30000' or null>",
            "purposes": [<list of purposes from: {VALID_PURPOSES}>],
            "priorities": [<list of priorities from: {VALID_PRIORITIES}>],
            "brand_preference": "<brand origin from: {VALID_BRAND_ORIGINS} or null>",
            "size_preference": "<compact/mid-size/full-size/suv/pickup or null>",
            "fuel_type": "<gasoline/hybrid/electric or null>",
            "passengers": <integer or null>,
            "style_preference": "<sporty/luxury/practical/rugged or null>"
        }}
        
        Only return the JSON object, no other text.
        """
        
        try:
            response = self.llm.invoke(extraction_prompt)
            criteria = json.loads(response.content.strip())
            return criteria
        except (json.JSONDecodeError, Exception) as e:
            # Fallback to basic keyword extraction
            return self._basic_criteria_extraction(question)
    
    def _basic_criteria_extraction(self, question: str) -> Dict[str, Any]:
        """
        Fallback method for basic criteria extraction using keywords.
        """
        question_lower = question.lower()
        criteria = {
            "budget_max": None,
            "budget_range": None,
            "purposes": [],
            "priorities": [],
            "brand_preference": None,
            "size_preference": None,
            "fuel_type": None,
            "passengers": None,
            "style_preference": None
        }
        
        # Extract budget
        budget_patterns = [
            r'\$?(\d{1,3},?\d{3})',  # $30,000 or 30000
            r'under \$?(\d{1,3},?\d{3})',
            r'below \$?(\d{1,3},?\d{3})',
            r'budget.*?\$?(\d{1,3},?\d{3})'
        ]
        
        for pattern in budget_patterns:
            match = re.search(pattern, question_lower)
            if match:
                budget_str = match.group(1).replace(',', '')
                criteria["budget_max"] = int(budget_str)
                break
        
        # Extract purposes
        purpose_keywords = {
            "family": ["family", "kids", "children", "school"],
            "daily_commute": ["commute", "commuting", "work", "daily"],
            "business": ["business", "professional", "client"],
            "leisure": ["leisure", "weekend", "vacation", "trip"],
            "towing": ["tow", "haul", "truck", "cargo"],
            "luxury": ["luxury", "premium", "high-end"]
        }
        
        for purpose, keywords in purpose_keywords.items():
            if any(keyword in question_lower for keyword in keywords):
                criteria["purposes"].append(purpose)
        
        # Extract brand preferences
        brand_keywords = {
            "Japanese": ["toyota", "honda", "mazda", "nissan", "subaru", "japanese", "reliable"],
            "German": ["bmw", "mercedes", "audi", "volkswagen", "german", "luxury"],
            "Korean": ["hyundai", "kia", "korean"],
            "American": ["ford", "chevrolet", "gmc", "american"]
        }
        
        for brand, keywords in brand_keywords.items():
            if any(keyword in question_lower for keyword in keywords):
                criteria["brand_preference"] = brand
                break
        
        return criteria
    
    def filter_cars_by_criteria(self, criteria: Dict[str, Any]) -> Dict[str, Dict]:
        """
        Filter cars based on extracted criteria.
        """
        cars = self.car_db.get_all_cars()
        filtered_cars = {}
        
        for car_name, specs in cars.items():
            score = 0
            match = True
            
            # Budget filter
            if criteria.get("budget_max"):
                price_range = specs["price_range"]
                max_price = int(price_range.split('-')[1].replace('$', '').replace(',', ''))
                if max_price > criteria["budget_max"]:
                    match = False
                    continue
                else:
                    score += 10  # Budget match bonus
            
            # Purpose filter
            if criteria.get("purposes"):
                car_purposes = specs["purposes"]
                purpose_matches = sum(1 for p in criteria["purposes"] if p in car_purposes)
                if purpose_matches == 0:
                    match = False
                    continue
                else:
                    score += purpose_matches * 15
            
            # Brand preference
            if criteria.get("brand_preference"):
                if criteria["brand_preference"].lower() in specs["brand_origin"].lower():
                    score += 20
                else:
                    score -= 5
            
            # Priority matching
            if criteria.get("priorities"):
                car_priorities = specs["priorities"]
                priority_matches = sum(1 for p in criteria["priorities"] if p in car_priorities)
                score += priority_matches * 10
            
            if match:
                filtered_cars[car_name] = {**specs, "match_score": score}
        
        return filtered_cars
    
    def rank_recommendations(self, filtered_cars: Dict[str, Dict]) -> List[tuple]:
        """
        Rank cars by match score and return top recommendations.
        """
        ranked = [(name, specs) for name, specs in filtered_cars.items()]
        ranked.sort(key=lambda x: x[1].get("match_score", 0), reverse=True)
        return ranked[:3]  # Top 3 recommendations
    
    def generate_recommendation_response(self, question: str, top_cars: List[tuple]) -> str:
        """
        Generate detailed recommendation response using LLM.
        """
        if not top_cars:
            return self._get_fallback_response()
        
        cars_info = []
        for i, (car_name, specs) in enumerate(top_cars, 1):
            car_info = f"""
            {i}. **{car_name}**
               - Price: {specs['price_range']}
               - Fuel Economy: {specs['fuel_economy']}
               - Size: {specs['size']}
               - Purposes: {', '.join(specs['purposes'])}
               - Priorities: {', '.join(specs['priorities'])}
               - Brand: {specs['brand_origin']}
               - Safety: {specs['safety_rating']}
               - Technology: {specs['technology']}
               - Style: {specs['style']}
            """
            cars_info.append(car_info)
        
        recommendation_prompt = f"""
        You are an expert car recommendation agent. Based on the user's question: "{question}"
        
        I have analyzed their needs and selected these top 3 car recommendations:
        {"".join(cars_info)}
        
        Please provide a comprehensive recommendation response that includes:
        1. A brief analysis of their stated needs
        2. Detailed explanation for each of the 3 cars and why they match
        3. Key advantages and considerations for each option
        4. A final recommendation with reasoning
        
        Format the response in a clear, engaging way with proper sections and bullet points.
        Make it personal and helpful, as if you're a knowledgeable car advisor.
        """
        
        try:
            response = self.llm.invoke(recommendation_prompt)
            return response.content
        except Exception as e:
            return self._format_basic_response(question, top_cars)
    
    def _format_basic_response(self, question: str, top_cars: List[tuple]) -> str:
        """
        Generate a basic formatted response without LLM.
        """
        response = "🚗 **Car Recommendations Based on Your Needs**\n\n"
        
        for i, (car_name, specs) in enumerate(top_cars, 1):
            response += f"**{i}. {car_name}** ({specs['price_range']})\n"
            response += f"   • **Why it fits:** Perfect for {', '.join(specs['purposes'])}\n"
            response += f"   • **Fuel Economy:** {specs['fuel_economy']}\n"
            response += f"   • **Size:** {specs['size']}\n"
            response += f"   • **Key Features:** {specs['technology']}\n"
            response += f"   • **Style:** {specs['style']}\n\n"
        
        response += "**My Recommendation:** "
        if top_cars:
            top_choice = top_cars[0][0]
            response += f"The **{top_choice}** would be my top choice based on your requirements. "
            response += "It offers the best balance of your priorities and budget.\n\n"
        
        response += "Would you like more details about any of these vehicles or have specific questions about features?"
        
        return response
    
    def _get_fallback_response(self) -> str:
        """
        Fallback response when no cars match criteria or for general inquiries.
        """
        return """
        🚗 **Car Recommendation Service**
        
        I'd be happy to help you find the perfect car! To provide the best recommendation, please tell me about:
        
        **1. Budget** 💰
        - What's your price range?
        
        **2. Main Purpose** 🎯
        - Daily city commuting?
        - Family trips and school runs?
        - Business/service use?
        - Long-distance travel?
        - Weekend leisure trips?
        
        **3. Size Requirements** 👥
        - How many passengers do you need to seat?
        - Do you need cargo space for luggage/equipment?
        
        **4. Priorities** ⭐ (in order of importance)
        - Fuel economy
        - Driving feel (sporty, responsive)
        - Smooth, quiet ride
        - Technology features
        - Safety features
        - Design and style
        
        **5. Brand/Style Preferences** 🎨
        - Any preferred brands (Japanese, Korean, German, etc.)?
        - Style preference (sporty, luxury, practical, rugged)?
        
        Please share these details and I'll recommend the perfect cars for you!
        """
    
    def process_recommendation_request(self, state: ChatState) -> ChatState:
        """
        Main method to process car recommendation requests.
        """
        question = state["question"]
        
        try:
            # Step 1: Extract user criteria
            criteria = self.extract_user_criteria(question)
            
            # Step 2: Filter cars based on criteria
            filtered_cars = self.filter_cars_by_criteria(criteria)
            
            # Step 3: Rank recommendations
            top_cars = self.rank_recommendations(filtered_cars)
            
            # Step 4: Generate response
            response = self.generate_recommendation_response(question, top_cars)
            
            return {**state, "answer": response}
            
        except Exception as e:
            # Fallback response
            response = self._get_fallback_response()
            return {**state, "answer": response}


# Create global instance
car_recommendation_agent = CarRecommendationAgent()


def recommend_car(state: ChatState) -> ChatState:
    """
    Entry point function for the car recommendation agent.
    """
    return car_recommendation_agent.process_recommendation_request(state)
