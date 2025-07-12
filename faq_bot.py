import os
import json
import openai
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from faq_data import FAQ_LIST, FUNCTION_DEFINITIONS, AVAILABLE_FUNCTIONS

# Load environment variables from .env file
load_dotenv()

# Configuration from environment variables
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://aiportalapi.stu-platform.live/jpe")
MODEL = os.getenv("MODEL_NAME", "GPT-4o-mini")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "200"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.5"))

# Retry configuration
RETRY_ATTEMPTS = int(os.getenv("RETRY_ATTEMPTS", "3"))
RETRY_WAIT_MIN = int(os.getenv("RETRY_WAIT_MIN", "1"))
RETRY_WAIT_MAX = int(os.getenv("RETRY_WAIT_MAX", "10"))

client = openai.OpenAI(
    base_url=OPENAI_BASE_URL,
    api_key=os.getenv("OPENAI_API_KEY")
)

# Build the system prompt for function calling
def build_system_prompt():
    prompt = """Bạn là một trợ lý AI thông minh, đáng tin cậy và lịch sự, chuyên trả lời các câu hỏi thường gặp (FAQ) về xe hơi.

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

Hãy sử dụng các chức năng có sẵn để trả lời câu hỏi của người dùng một cách chính xác và hữu ích."""
    return prompt

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

def get_faq_answer_with_functions(user_question):
    """Get FAQ answer using function calling capabilities with retry mechanism"""
    system_prompt = build_system_prompt()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_question}
    ]
    
    try:
        # First API call with function definitions
        print("🔄 Calling OpenAI API...")
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
            
            # Add the function call and result to the conversation
            messages.append({
                "role": "assistant",
                "content": None,
                "function_call": {
                    "name": function_name,
                    "arguments": message.function_call.arguments
                }
            })
            messages.append({
                "role": "function",
                "name": function_name,
                "content": function_result
            })
            
            # Second API call to get the final response
            print("🔄 Getting final response...")
            final_response = call_openai_with_retry(messages=messages)
            
            return final_response.choices[0].message.content.strip()
        else:
            # No function call needed, return the direct response
            return message.content.strip()
            
    except Exception as e:
        error_msg = f"❌ Đã xảy ra lỗi sau {RETRY_ATTEMPTS} lần thử: {str(e)}"
        print(error_msg)
        return f"Xin lỗi, tôi đang gặp sự cố kỹ thuật. Vui lòng thử lại sau. ({str(e)})"

# Keep the original function for backward compatibility
def get_faq_answer(user_question):
    """Original FAQ function without function calling (for backward compatibility) with retry"""
    system_prompt = """Bạn là một trợ lý AI thông minh, đáng tin cậy và lịch sự, chuyên trả lời các câu hỏi thường gặp (FAQ) về xe hơi.

Nhiệm vụ của bạn:
1. Đọc kỹ câu hỏi của người dùng.
2. Suy luận để xác định xem câu hỏi có liên quan đến các mục trong danh sách FAQ không.
3. Nếu có, đưa ra câu trả lời phù hợp nhất dựa trên nội dung FAQ.
4. Nếu không có câu hỏi nào phù hợp, hãy lịch sự trả lời rằng bạn không biết.

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

---

FAQs:\n"""
    
    for faq in FAQ_LIST:
        system_prompt += f"Q: {faq['question']}\nA: {faq['answer']}\n"
    system_prompt += "\nHãy trả lời câu hỏi của người dùng một cách chính xác và hữu ích dựa trên các FAQ trên."
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_question}
    ]
    
    try:
        print("🔄 Calling OpenAI API (traditional mode)...")
        response = call_openai_with_retry(messages=messages)
        return response.choices[0].message.content.strip()
    except Exception as e:
        error_msg = f"❌ Đã xảy ra lỗi sau {RETRY_ATTEMPTS} lần thử: {str(e)}"
        print(error_msg)
        return f"Xin lỗi, tôi đang gặp sự cố kỹ thuật. Vui lòng thử lại sau. ({str(e)})"
