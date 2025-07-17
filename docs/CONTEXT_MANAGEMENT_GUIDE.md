# Context Management & Multi-turn Conversations - Complete Guide

## 🎯 What is Context Management?

**Context Management** is the ability of a chatbot to remember and use information from previous parts of the conversation. Instead of treating each question as isolated, the bot maintains awareness of what has been discussed.

## 🔄 What are Multi-turn Conversations?

**Multi-turn Conversations** are natural back-and-forth exchanges where each message builds upon previous ones, just like human conversations.

## 📊 Comparison: With vs Without Context

### ❌ WITHOUT Context Management (Original)

```python
# Each question is processed independently
def get_faq_answer(user_question):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_question}  # Only current question
    ]
    # No memory of previous exchanges
```

**Example conversation:**
```
👤 "Gợi ý xe SUV cho tôi"
🤖 "Honda CR-V, Toyota RAV4, Mazda CX-5..."

👤 "Honda CR-V có ưu điểm gì?"
🤖 "Tôi không biết Honda CR-V là gì..." ❌ (Forgot previous response)

👤 "Giá của nó như thế nào?"
🤖 "Bạn đang hỏi về cái gì?" ❌ (Doesn't understand "nó")
```

### ✅ WITH Context Management (New Implementation)

```python
# Conversation history is maintained and sent with each request
def get_contextual_response(user_question):
    conversation_manager.add_message("user", user_question)
    messages = conversation_manager.get_context_messages()  # Includes full history
    # AI can see and reference previous exchanges
```

**Same conversation with context:**
```
👤 "Gợi ý xe SUV cho tôi"
🤖 "Honda CR-V, Toyota RAV4, Mazda CX-5..."

👤 "Honda CR-V có ưu điểm gì?"
🤖 "Honda CR-V mà tôi vừa đề cập có ưu điểm..." ✅ (Remembers previous response)

👤 "Giá của nó như thế nào?"
🤖 "Giá Honda CR-V thường..." ✅ (Understands "nó" = Honda CR-V)
```

## 🏗️ How Context Management Works - Step by Step

### Step 1: Message Storage
Every message (user and bot) is stored with metadata:

```python
conversation_history = [
    {
        "role": "user", 
        "content": "Gợi ý xe SUV", 
        "timestamp": "2025-06-28T10:00:00"
    },
    {
        "role": "assistant", 
        "content": "Honda CR-V, Toyota RAV4, Mazda CX-5...", 
        "timestamp": "2025-06-28T10:00:05"
    },
    {
        "role": "user", 
        "content": "Honda CR-V có ưu điểm gì?", 
        "timestamp": "2025-06-28T10:01:00"
    }
]
```

### Step 2: Context Building
When a new question arrives, the entire conversation history is sent to the AI:

```python
messages = [
    {"role": "system", "content": "Bạn là trợ lý ô tô, nhớ cuộc trò chuyện..."},
    {"role": "user", "content": "Gợi ý xe SUV"},
    {"role": "assistant", "content": "Honda CR-V, Toyota RAV4..."},
    {"role": "user", "content": "Honda CR-V có ưu điểm gì?"}  # New question with full context
]
```

### Step 3: Reference Resolution
The AI can now understand:
- "Honda CR-V" was mentioned in its previous response
- The user is asking about that specific car
- No need to search for SUVs again

### Step 4: Context Summary
To manage token limits, important topics are summarized:

```python
context_summary = "Đã tư vấn xe SUV | Quan tâm Honda CR-V | Hỏi về ưu điểm"
```

### Step 5: Response Generation
The AI generates a response that:
- References previous conversation
- Understands pronouns and implicit references
- Maintains conversation flow

## 🔧 Implementation Components

### 1. ConversationManager Class

```python
class ConversationManager:
    def __init__(self, max_history: int = 10):
        self.conversation_history = []
        self.max_history = max_history
        self.context_summary = ""
    
    def add_message(self, role, content, function_call=None):
        # Store message with timestamp
        
    def get_context_messages(self):
        # Format messages for OpenAI API
        
    def update_context_summary(self, new_info):
        # Maintain topic summary
```

### 2. Context-Aware System Prompt

```python
def _build_context_aware_system_prompt(self):
    return """Bạn là một trợ lý thông minh về ô tô với khả năng nhớ và tham chiếu cuộc trò chuyện trước đó.

NGUYÊN TẮC QUAN TRỌNG:
- Nhớ và tham chiếu đến những gì đã thảo luận trước đó
- Hiểu các từ như "nó", "xe đó", "mẫu này" dựa trên ngữ cảnh
- Duy trì tính liên tục trong cuộc trò chuyện
"""
```

### 3. Context Integration with Function Calling

```python
def get_contextual_response(user_question):
    # Add user message to history
    conversation_manager.add_message("user", user_question)
    
    # Get full context
    messages = conversation_manager.get_context_messages()
    
    # API call with context + function calling
    response = call_openai_with_retry(
        messages=messages,
        functions=FUNCTION_DEFINITIONS,
        function_call="auto"
    )
    
    # Add response to history
    conversation_manager.add_message("assistant", final_answer)
```

## 🎯 Key Benefits

### 1. Natural Conversation Flow
- **Pronouns**: "nó", "xe đó", "mẫu này"
- **References**: "Honda CR-V mà bạn vừa đề cập"
- **Follow-ups**: "Còn về bảo dưỡng thì sao?"

### 2. Contextual Function Calls
- If user asks "Giá của nó?" after discussing Honda CR-V
- AI knows to get pricing for Honda CR-V specifically
- No need to ask "xe nào?" again

### 3. Topic Continuity
- Maintains topic threads across multiple exchanges
- Can return to previous topics naturally
- Builds comprehensive discussions

### 4. Memory Management
- Automatic token limit management
- Context summarization for long conversations
- Cleanup of old messages while preserving important context

## 🧪 Testing Context Management

### Basic Test
```python
from context_manager import get_contextual_response, reset_conversation

# Start fresh
reset_conversation()

# First question
response1 = get_contextual_response("Gợi ý xe SUV cho tôi")
print("Response 1:", response1)

# Follow-up with reference
response2 = get_contextual_response("Honda CR-V có ưu điểm gì?")
print("Response 2:", response2)  # Should understand CR-V from previous response

# Follow-up with pronoun
response3 = get_contextual_response("Giá của nó như thế nào?")
print("Response 3:", response3)  # Should understand "nó" = Honda CR-V
```

### Advanced Test Scenarios

1. **Reference Resolution**:
   ```
   "Gợi ý xe sedan" → "Toyota Camry có tốt không?" → "So với BMW 3 Series thì sao?"
   ```

2. **Topic Switching and Return**:
   ```
   "Xe SUV nào tốt?" → "Còn về bảo dưỡng?" → "Quay lại Honda CR-V đi"
   ```

3. **Complex References**:
   ```
   "Mẹo tiết kiệm nhiên liệu" → "Mẹo thứ 2 là gì?" → "Làm sao áp dụng nó?"
   ```

## 📈 Performance Considerations

### Token Management
- Maximum history limit (default: 10 exchanges)
- Context summarization for long conversations
- Automatic cleanup of old messages

### Memory Efficiency
- Store only essential information
- Clean timestamps and metadata for API calls
- Compress context summaries

### Response Quality
- Fuller context leads to better responses
- More relevant function calls
- Natural conversation flow

## 🔮 Use Cases

### 1. Car Shopping Assistant
```
👤 "Tôi cần xe gia đình 7 chỗ"
🤖 "Gợi ý: Honda CR-V, Toyota Fortuner..."

👤 "Honda CR-V có 7 chỗ không?"
🤖 "Honda CR-V mà tôi vừa đề cập chỉ có 5 chỗ. Với nhu cầu 7 chỗ của bạn, tôi khuyên..."

👤 "Vậy Toyota Fortuner thì sao?"
🤖 "Toyota Fortuner trong danh sách có 7 chỗ đầy đủ..."
```

### 2. Maintenance Consultation
```
👤 "Xe tôi 50,000km rồi"
🤖 "Ở mức 50,000km nên: thay dầu, kiểm tra phanh..."

👤 "Thay dầu bao lâu một lần?"
🤖 "Với xe đã 50,000km như xe bạn, nên thay dầu mỗi 5,000-10,000km..."

👤 "Còn phanh thì sao?"
🤖 "Về phanh mà tôi vừa đề cập, ở 50,000km nên kiểm tra..."
```

### 3. Technical Comparison
```
👤 "So sánh Honda Civic vs Toyota Corolla"
🤖 "Honda Civic: [specs], Toyota Corolla: [specs]"

👤 "Cái nào tiết kiệm nhiên liệu hơn?"
🤖 "Giữa Honda Civic và Toyota Corolla mà tôi vừa so sánh..."

👤 "Giá thế nào?"
🤖 "Về giá cả của 2 mẫu xe này..."
```

## 🚀 Running the System

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Context Demo
```bash
python demo_context.py
```

### Run Full Application
```bash
python app.py
```

### Test Context Features
- Try the "Context-Aware Bot" tab
- Start with a general question
- Follow up with specific references
- Use pronouns like "nó", "xe đó"
- Notice how the bot maintains context

## 🎭 Context vs No Context Demo

The `demo_context.py` script shows side-by-side comparison:

1. **Without Context**: Each question processed independently
2. **With Context**: Full conversation awareness
3. **Specific Features**: Reference resolution, pronoun understanding, topic continuity

This demonstrates why context management is crucial for natural, human-like conversations!
