"""
Car Recommendation Agent
Specialized agent for providing intelligent car recommendations based on user criteria.
Uses ChromaDB to query car information that was already ingested via the UI.
"""

from typing import Dict, List, Any, Optional
from chat_state import ChatState
from services import get_azure_llm, get_vectordb
from .car_database import VALID_PURPOSES, VALID_PRIORITIES, VALID_BRAND_ORIGINS
import json
import re


class CarRecommendationAgent:
    """
    Intelligent car recommendation agent that analyzes user needs and provides 
    personalized vehicle recommendations using ChromaDB for car data retrieval.
    """
    
    def __init__(self):
        self.vectordb = get_vectordb()
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
    
    def query_cars_from_chromadb(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Query car information from ChromaDB based on user criteria.
        """
        try:
            # Build query string based on criteria
            query_parts = []
            
            # Add budget-related queries
            if criteria.get("budget_max"):
                budget = criteria["budget_max"]
                if budget < 25000:
                    query_parts.append("affordable budget-friendly economical cheap inexpensive")
                elif budget < 40000:
                    query_parts.append("mid-range moderate price value")
                else:
                    query_parts.append("luxury premium high-end expensive")
            
            # Add purpose-related queries
            if criteria.get("purposes"):
                purposes_text = " ".join(criteria["purposes"])
                query_parts.append(purposes_text)
            
            # Add priority-related queries
            if criteria.get("priorities"):
                priorities_text = " ".join(criteria["priorities"])
                query_parts.append(priorities_text)
            
            # Add brand preference
            if criteria.get("brand_preference"):
                query_parts.append(criteria["brand_preference"])
            
            # Add size preference
            if criteria.get("size_preference"):
                query_parts.append(criteria["size_preference"])
            
            # Add style preference
            if criteria.get("style_preference"):
                query_parts.append(criteria["style_preference"])
            
            # Create comprehensive query
            query = " ".join(query_parts) if query_parts else "car vehicle automobile"
            
            # Search ChromaDB for relevant car information
            results = self.vectordb.similarity_search_with_score(query, k=10)
            
            # Extract car information from results
            car_info_list = []
            for doc, score in results:
                car_info_list.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity_score": score
                })
            
            return car_info_list
            
        except Exception as e:
            print(f"Error querying ChromaDB: {e}")
            return []
    
    def analyze_car_data_with_llm(self, car_data: List[Dict[str, Any]], criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Use LLM to analyze retrieved car data and extract structured information.
        """
        if not car_data:
            return []
        
        # Combine all car information from ChromaDB results
        car_content = "\n\n".join([item["content"] for item in car_data])
        
        analysis_prompt = f"""
        You are a car expert analyzing car data to provide recommendations. 
        
        User criteria: {json.dumps(criteria, indent=2)}
        
        Car data from database:
        {car_content}
        
        Based on this data, extract and return information about the most suitable cars as a JSON array. 
        Each car should include:
        {{
            "name": "Car Make Model",
            "make": "Brand",
            "model": "Model",
            "year": year,
            "price": price_info,
            "purposes": [list of suitable purposes],
            "priorities": [list of matching priorities],
            "brand_origin": "origin",
            "safety_rating": "rating",
            "technology": "tech features",
            "style": "style description",
            "fuel_economy": "economy info",
            "size": "size description",
            "match_score": score_out_of_100,
            "why_recommended": "explanation of why this car matches user needs"
        }}
        
        Return only the JSON array, no other text. Focus on cars that best match the user's criteria.
        """
        
        try:
            response = self.llm.invoke(analysis_prompt)
            # Try to extract JSON from the response
            content = response.content.strip()
            
            # Handle potential markdown code blocks
            if content.startswith("```json"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                content = content[3:-3].strip()
            
            cars = json.loads(content)
            return cars if isinstance(cars, list) else [cars]
            
        except Exception as e:
            print(f"Error analyzing car data with LLM: {e}")
            return []
    def rank_recommendations(self, cars: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rank cars by match score and return top recommendations.
        """
        if not cars:
            return []
            
        # Sort by match_score (descending)
        ranked_cars = sorted(cars, key=lambda x: x.get("match_score", 0), reverse=True)
        return ranked_cars[:3]  # Top 3 recommendations
    
    def generate_recommendation_response(self, question: str, top_cars: List[Dict[str, Any]]) -> str:
        """
        Generate detailed recommendation response using LLM.
        """
        if not top_cars:
            return self._get_fallback_response()
        
        cars_info = []
        for i, car in enumerate(top_cars, 1):
            car_info = f"""
            {i}. **{car.get('name', 'Unknown Car')}**
               - Price: {car.get('price', 'Price not specified')}
               - Year: {car.get('year', 'N/A')}
               - Fuel Economy: {car.get('fuel_economy', 'Not specified')}
               - Size: {car.get('size', 'Not specified')}
               - Purposes: {', '.join(car.get('purposes', []))}
               - Priorities: {', '.join(car.get('priorities', []))}
               - Brand Origin: {car.get('brand_origin', 'Not specified')}
               - Safety Rating: {car.get('safety_rating', 'Not specified')}
               - Technology: {car.get('technology', 'Not specified')}
               - Style: {car.get('style', 'Not specified')}
               - Match Score: {car.get('match_score', 0)}/100
               - Why Recommended: {car.get('why_recommended', 'Good match for your needs')}
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
    
    def _format_basic_response(self, question: str, top_cars: List[Dict[str, Any]]) -> str:
        """
        Generate a basic formatted response without LLM.
        """
        response = "🚗 **Car Recommendations Based on Your Needs**\n\n"
        
        for i, car in enumerate(top_cars, 1):
            response += f"**{i}. {car.get('name', 'Unknown Car')}** ({car.get('price', 'Price not specified')})\n"
            response += f"   • **Why it fits:** {car.get('why_recommended', 'Good match for your needs')}\n"
            response += f"   • **Year:** {car.get('year', 'N/A')}\n"
            response += f"   • **Fuel Economy:** {car.get('fuel_economy', 'Not specified')}\n"
            response += f"   • **Size:** {car.get('size', 'Not specified')}\n"
            response += f"   • **Key Features:** {car.get('technology', 'Not specified')}\n"
            response += f"   • **Style:** {car.get('style', 'Not specified')}\n"
            response += f"   • **Match Score:** {car.get('match_score', 0)}/100\n\n"
        
        response += "**My Recommendation:** "
        if top_cars:
            top_choice = top_cars[0].get('name', 'Unknown Car')
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
        Main method to process car recommendation requests using ChromaDB.
        """
        question = state["question"]
        
        try:
            # Step 1: Extract user criteria
            criteria = self.extract_user_criteria(question)
            
            # Step 2: Query car data from ChromaDB
            car_data = self.query_cars_from_chromadb(criteria)
            
            # Step 3: Use LLM to analyze and structure car data
            analyzed_cars = self.analyze_car_data_with_llm(car_data, criteria)
            
            # Step 4: Rank recommendations
            top_cars = self.rank_recommendations(analyzed_cars)
            
            # Step 5: Generate response
            response = self.generate_recommendation_response(question, top_cars)
            
            return {**state, "answer": response}
            
        except Exception as e:
            print(f"Error in recommendation processing: {e}")
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
