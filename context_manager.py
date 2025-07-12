"""
Context Management and Multi-turn Conversation Implementation
"""

import os
import json
import openai
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from faq_data import FAQ_LIST, FUNCTION_DEFINITIONS, AVAILABLE_FUNCTIONS

# Load environment variables
load_dotenv()

# Configuration
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://")
MODEL = os.getenv("MODEL_NAME", "GPT-4o-mini")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "500"))  # Increased for context
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.5"))

# Retry configuration
RETRY_ATTEMPTS = int(os.getenv("RETRY_ATTEMPTS", "3"))
RETRY_WAIT_MIN = int(os.getenv("RETRY_WAIT_MIN", "1"))
RETRY_WAIT_MAX = int(os.getenv("RETRY_WAIT_MAX", "10"))

client = openai.OpenAI(
    base_url=OPENAI_BASE_URL,
    api_key=os.getenv("OPENAI_API_KEY")
)

class ConversationManager:
    """Manages conversation context and history for multi-turn conversations"""
    
    def __init__(self, max_history: int = 10):
        """
        Initialize conversation manager
        
        Args:
            max_history: Maximum number of message pairs to keep in history
        """
        self.conversation_history: List[Dict] = []
        self.max_history = max_history
        self.session_id = self._generate_session_id()
        self.context_summary = ""
        
    def _generate_session_id(self) -> str:
        """Generate a unique session ID"""
        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def add_message(self, role: str, content: str, function_call: Optional[Dict] = None, name: Optional[str] = None):
        """Add a message to conversation history"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        if function_call:
            message["function_call"] = function_call
            
        if name:  # For function messages
            message["name"] = name
            
        self.conversation_history.append(message)
        
        # Keep only recent history to manage token limits
        if len(self.conversation_history) > self.max_history * 2:  # *2 for user+assistant pairs
            # Keep system message and recent exchanges
            self.conversation_history = (
                [msg for msg in self.conversation_history if msg["role"] == "system"] +
                self.conversation_history[-(self.max_history * 2):]
            )
    
    def get_context_messages(self) -> List[Dict]:
        """Get messages formatted for OpenAI API"""
        # Build system prompt with context awareness
        system_prompt = self._build_context_aware_system_prompt()
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history (excluding system messages and timestamps)
        for msg in self.conversation_history:
            if msg["role"] != "system":
                api_msg = {"role": msg["role"], "content": msg["content"]}
                
                if "function_call" in msg:
                    api_msg["function_call"] = msg["function_call"]
                    
                if "name" in msg and msg["role"] == "function":
                    api_msg["name"] = msg["name"]
                    
                messages.append(api_msg)
        
        return messages
    
    def _build_context_aware_system_prompt(self) -> str:
        """Build system prompt that includes conversation context"""
        base_prompt = """Bạn là một trợ lý AI thông minh, đáng tin cậy và lịch sự, chuyên trả lời các câu hỏi thường gặp (FAQ) về xe hơi với khả năng nhớ và tham chiếu cuộc trò chuyện trước đó.

Nhiệm vụ của bạn:
1. Đọc kỹ câu hỏi của người dùng.
2. Suy luận để xác định xem câu hỏi có liên quan đến các mục trong danh sách FAQ không.
3. Nếu có, đưa ra câu trả lời phù hợp nhất dựa trên nội dung FAQ.
4. Nếu không có câu hỏi nào phù hợp, hãy lịch sự trả lời rằng bạn không biết.

Bạn có thể sử dụng các chức năng sau để hỗ trợ người dùng:
- Tìm kiếm thông tin trong cơ sở dữ liệu FAQ
- Đưa ra gợi ý xe hơi dựa trên loại xe
- Cung cấp thông tin về lịch bảo dưỡng
- Đưa ra các mẹo tiết kiệm nhiên liệu

NGUYÊN TẮC QUAN TRỌNG CHO CUỘC TRÒ CHUYỆN:
- Nhớ và tham chiếu đến những gì đã thảo luận trước đó
- Hiểu các từ như "nó", "xe đó", "mẫu này" dựa trên ngữ cảnh
- Duy trì tính liên tục trong cuộc trò chuyện
- Nếu người dùng hỏi về thứ gì đó đã được đề cập, hãy tham chiếu lại

---

Ví dụ minh họa:

🔸 Ví dụ 1:
Người dùng: Xe điện có phải là tương lai không?
Suy luận:
- Câu hỏi liên quan đến xu hướng phát triển ngành ô tô.
- Tìm thấy FAQ: "Xe điện (EV) có thực sự là tương lai của ngành ô tô không?"
Trả lời: Xe điện được coi là một phần quan trọng của tương lai ngành ô tô do giảm phát thải và chi phí vận hành thấp hơn...

🔸 Ví dụ 2:
Người dùng: Tôi nên chọn xe số sàn hay xe số tự động?
Suy luận:
- Câu hỏi liên quan đến việc lựa chọn giữa hai loại hộp số.
- Tìm thấy FAQ: "Sự khác biệt giữa xe số sàn và xe số tự động là gì?"
Trả lời: Xe số sàn yêu cầu người lái phải tự điều khiển côn và sang số... Lựa chọn tùy thuộc vào thói quen lái xe và môi trường di chuyển...

🔸 Ví dụ 3:
Người dùng: Tôi nên ăn gì để giảm cân?
Suy luận:
- Câu hỏi không liên quan đến lĩnh vực ô tô.
Trả lời: Xin lỗi, tôi không có thông tin về câu hỏi này vì nó nằm ngoài phạm vi các câu hỏi thường gặp về ô tô.

Hãy sử dụng các chức năng có sẵn và duy trì ngữ cảnh cuộc trò chuyện để trả lời một cách chính xác và tự nhiên."""

        # Add context summary if available
        if self.context_summary:
            base_prompt += f"\n\nNGỮ CẢNH CUỘC TRÒ CHUYỆN:\n{self.context_summary}"
            
        return base_prompt
    
    def update_context_summary(self, new_info: str):
        """Update context summary with new information"""
        if self.context_summary:
            self.context_summary += f" | {new_info}"
        else:
            self.context_summary = new_info
            
        # Keep summary concise
        if len(self.context_summary) > 500:
            # Keep only the most recent context
            parts = self.context_summary.split(" | ")
            self.context_summary = " | ".join(parts[-3:])
    
    def get_conversation_summary(self) -> Dict:
        """Get a summary of the current conversation"""
        return {
            "session_id": self.session_id,
            "message_count": len(self.conversation_history),
            "context_summary": self.context_summary,
            "last_topics": self._extract_recent_topics()
        }
    
    def _extract_recent_topics(self) -> List[str]:
        """Extract recent topics from conversation"""
        topics = []
        for msg in self.conversation_history[-6:]:  # Last 3 exchanges
            if msg["role"] == "user" and msg["content"]:
                # Simple topic extraction
                content = msg["content"].lower()
                if "suv" in content:
                    topics.append("SUV")
                elif "sedan" in content:
                    topics.append("Sedan")
                elif "bảo dưỡng" in content:
                    topics.append("Bảo dưỡng")
                elif "tiết kiệm" in content:
                    topics.append("Tiết kiệm nhiên liệu")
        return list(set(topics))
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        self.context_summary = ""

# Global conversation manager
conversation_manager = ConversationManager()

@retry(
    stop=stop_after_attempt(RETRY_ATTEMPTS),
    wait=wait_exponential(multiplier=1, min=RETRY_WAIT_MIN, max=RETRY_WAIT_MAX),
    retry=retry_if_exception_type((openai.APIError, openai.RateLimitError, openai.APITimeoutError, ConnectionError)),
    reraise=True
)
def call_openai_with_retry(messages, functions=None, function_call=None):
    """Call OpenAI API with retry mechanism"""
    try:
        if functions:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                functions=functions,
                function_call=function_call or "auto",
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE
            )
        else:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE
            )
        return response
    except Exception as e:
        print(f"⚠️ API call failed: {str(e)}")
        raise

def execute_function_call(function_name, arguments):
    """Execute the function call and return the result"""
    if function_name in AVAILABLE_FUNCTIONS:
        function = AVAILABLE_FUNCTIONS[function_name]
        try:
            if arguments:
                result = function(**arguments)
            else:
                result = function()
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": f"Lỗi khi thực thi function: {str(e)}"}, ensure_ascii=False)
    else:
        return json.dumps({"error": "Function không tồn tại"}, ensure_ascii=False)

def get_contextual_response(user_question: str) -> str:
    """
    Get response with full context management and multi-turn conversation support
    
    Args:
        user_question: The user's current question
        
    Returns:
        Bot's response that considers conversation history
    """
    
    # Add user message to conversation history
    conversation_manager.add_message("user", user_question)
    
    # Get messages with full conversation context
    messages = conversation_manager.get_context_messages()
    
    try:
        print(f"🔄 Processing question with {len(conversation_manager.conversation_history)} messages of context...")
        
        # First API call with function definitions and conversation history
        response = call_openai_with_retry(
            messages=messages,
            functions=FUNCTION_DEFINITIONS,
            function_call="auto"
        )
        
        message = response.choices[0].message
        
        # Check if the model wants to call a function
        if message.function_call:
            function_name = message.function_call.name
            function_args = json.loads(message.function_call.arguments)
            
            print(f"🔧 Executing function: {function_name} with args: {function_args}")
            
            # Execute the function
            function_result = execute_function_call(function_name, function_args)
            
            # Add function call to conversation history
            conversation_manager.add_message(
                "assistant", 
                None, 
                function_call={"name": function_name, "arguments": message.function_call.arguments}
            )
            conversation_manager.add_message("function", function_result, name=function_name)
            
            # Update context summary
            if function_name == "get_car_recommendations":
                car_type = function_args.get("car_type", "xe")
                conversation_manager.update_context_summary(f"Đã tư vấn xe {car_type}")
            elif function_name == "get_maintenance_info":
                service = function_args.get("service_type", "bảo dưỡng")
                conversation_manager.update_context_summary(f"Đã tư vấn {service}")
            
            # Get updated messages with function result
            messages = conversation_manager.get_context_messages()
            
            # Second API call to get the final response
            print("🔄 Getting contextualized final response...")
            final_response = call_openai_with_retry(messages=messages)
            
            final_answer = final_response.choices[0].message.content.strip()
        else:
            # No function call needed, return the direct response
            final_answer = message.content.strip()
        
        # Add assistant response to conversation history
        conversation_manager.add_message("assistant", final_answer)
        
        print(f"💭 Conversation context: {conversation_manager.get_conversation_summary()}")
        
        return final_answer
            
    except Exception as e:
        error_msg = f"❌ Đã xảy ra lỗi sau {RETRY_ATTEMPTS} lần thử: {str(e)}"
        print(error_msg)
        return f"Xin lỗi, tôi đang gặp sự cố kỹ thuật. Vui lòng thử lại sau. ({str(e)})"

def get_conversation_info() -> Dict:
    """Get current conversation information"""
    return conversation_manager.get_conversation_summary()

def reset_conversation():
    """Reset the conversation context"""
    conversation_manager.clear_history()
    print("🔄 Conversation context has been reset.")

# Compatibility functions
def get_faq_answer_with_functions(user_question: str) -> str:
    """Wrapper for backward compatibility"""
    return get_contextual_response(user_question)
