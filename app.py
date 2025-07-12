import gradio as gr
import os
from context_manager import get_contextual_response, reset_conversation, get_conversation_info
from faq_bot import get_faq_answer_with_functions, get_faq_answer
from automotive_bot import get_automotive_response, reset_automotive_conversation, get_automotive_info
from kb_manager import upload_document_to_kb, get_kb_stats, search_kb, clear_kb

def context_aware_chatbot_interface(user_input, history):
    """Chatbot with full context management"""
    try:
        # Use context-aware response
        answer = get_contextual_response(user_input)
        
        # Get context information for display
        context_info = get_conversation_info()
        status_msg = f"✅ Context: {context_info['message_count']} messages, Topics: {context_info['last_topics']}"
        
    except Exception as e:
        answer = f"❌ Lỗi: {str(e)}"
        status_msg = "❌ Thất bại"
    
    history = history or []
    history.append({"role": "user", "content": user_input})
    history.append({"role": "assistant", "content": answer})
    return "", history

def chatbot_interface(user_input, history):
    """Original function calling without context management"""
    try:
        answer = get_faq_answer_with_functions(user_input)
        status_msg = "✅ Function calling (no context)"
    except Exception as e:
        answer = f"❌ Lỗi: {str(e)}"
        status_msg = "❌ Thất bại"
    
    history = history or []
    history.append({"role": "user", "content": user_input})
    history.append({"role": "assistant", "content": answer})
    return "", history

def simple_chatbot_interface(user_input, history):
    """Simple FAQ without function calling or context"""
    try:
        answer = get_faq_answer(user_input)
        status_msg = "✅ Simple FAQ"
    except Exception as e:
        answer = f"❌ Lỗi: {str(e)}"
        status_msg = "❌ Thất bại"
    
    history = history or []
    history.append({"role": "user", "content": user_input})
    history.append({"role": "assistant", "content": answer})
    return "", history

def reset_context():
    """Reset conversation context"""
    reset_conversation()
    return "🔄 Context đã được reset!"

def automotive_bot_interface(user_input, history):
    """AI Automotive Consultant with Advanced Reasoning - Powered by LangChain + ChromaDB + Tavily"""
    try:
        print(f"🎯 UI Request: {user_input}")
        answer = get_automotive_response(user_input)
        
        # Enhanced Debugging: Print the full response to be sent to the UI
        print("\n" + "="*30 + " UI RESPONSE START " + "="*30)
        print(answer)
        print("="*31 + " UI RESPONSE END " + "="*31 + "\n")
        
        # Get context information for display
        context_info = get_automotive_info()
        
        # Enhanced status with capabilities
        capabilities = []
        if "LangChain" in context_info['status']:
            capabilities.extend(["📚 Knowledge Base", "🔍 Live Search", "🧠 AI Reasoning"])
        if "Agent" in context_info['status']:
            capabilities.append("🤖 Smart Agent")
        
        status_msg = f"✅ {', '.join(capabilities)} | {context_info['message_count']} messages"
        
    except Exception as e:
        answer = f"❌ Lỗi: {str(e)}"
        status_msg = "❌ Thất bại"
        print(f"❌ UI Error: {e}")
    
    history = history or []
    history.append({"role": "user", "content": user_input})
    history.append({"role": "assistant", "content": answer})
    return "", history

def reset_automotive_context():
    """Reset automotive bot context"""
    reset_automotive_conversation()
    return "🔄 Automotive Bot context đã được reset!"

def upload_file_interface(file, description):
    """Upload file to knowledge base"""
    if file is None:
        return "❌ Vui lòng chọn file để upload"
    
    try:
        result = upload_document_to_kb(file.name, file.name.split('/')[-1], description or "")
        return result
    except Exception as e:
        return f"❌ Lỗi upload: {str(e)}"

def search_kb_interface(query):
    """Search knowledge base"""
    if not query.strip():
        return "❌ Vui lòng nhập từ khóa tìm kiếm"
    
    try:
        results = search_kb(query, k=3)
        if not results:
            return "🔍 Không tìm thấy kết quả phù hợp"
        
        response = f"🔍 **Tìm thấy {len(results)} kết quả:**\n\n"
        for i, result in enumerate(results, 1):
            response += f"**{i}. Similarity: {result['similarity_score']:.2f}**\n"
            response += f"📄 File: {result['metadata'].get('filename', 'Unknown')}\n"
            response += f"📝 Content: {result['content']}\n\n"
        
        return response
    except Exception as e:
        return f"❌ Lỗi tìm kiếm: {str(e)}"

def get_kb_stats_interface():
    """Get knowledge base statistics"""
    try:
        stats = get_kb_stats()
        return stats  # get_kb_stats() already returns formatted string
    except Exception as e:
        return f"❌ Lỗi: {str(e)}"

def clear_kb_interface():
    """Clear knowledge base"""
    try:
        result = clear_kb()
        return result
    except Exception as e:
        return f"❌ Lỗi: {str(e)}"

# Get retry configuration for display
retry_attempts = os.getenv("RETRY_ATTEMPTS", "3")
retry_wait_min = os.getenv("RETRY_WAIT_MIN", "1")
retry_wait_max = os.getenv("RETRY_WAIT_MAX", "10")

with gr.Blocks() as demo:
    # gr.Markdown(f"""
    # # 🚗 FAQ Chatbot: Context Management & Multi-turn Conversations
    # **Demo năm cấp độ chatbot khác nhau:**
    # **🔁 Retry Configuration:** Max attempts: {retry_attempts}, Wait: {retry_wait_min}-{retry_wait_max}s
    # """)
    
    with gr.Tab("🚗 AI Automotive Consultant"):
        gr.Markdown("""
        ## 🚗 Advanced AI Automotive Consultant
        
        **🎯 Chuyên gia tư vấn ô tô thông minh với khả năng suy luận**
        
        ### 🌟 Tính năng đặc biệt:
        - 🧠 **AI Reasoning Process**: Hiển thị quá trình suy nghĩ của AI
        - � **Local Knowledge Base**: Dữ liệu Audi & Honda chuyên sâu  
        - 🔍 **Live Web Search**: Tìm kiếm tin tức và thông tin mới nhất với Tavily
        - 🤖 **Smart Fallback**: Tự động chuyển đổi giữa các nguồn thông tin
        - 💬 **Context Memory**: Nhớ cuộc hội thoại để tư vấn chính xác hơn
        
        ### � Cách hoạt động:
        1. **Knowledge Base First**: Tìm trong database Audi/Honda
        2. **Smart Agent**: Nếu không có info → Tự động search online  
        3. **Direct Chat**: Fallback cuối cùng với AI model        
        
        """)
        
        automotive_chatbot = gr.Chatbot(
            type="messages", 
            height=500,
            show_copy_button=True,
            placeholder="🤖 Xin chào! Tôi là AI Automotive Consultant. Tôi có thể tư vấn về xe hơi với khả năng suy luận thông minh và tìm kiếm thông tin realtime. Hãy hỏi tôi bất cứ điều gì về ô tô!"
        )
        with gr.Row():
            automotive_txt = gr.Textbox(
                show_label=False, 
                placeholder="💬 Hỏi về xe hơi, công nghệ, tin tức, so sánh, tư vấn mua xe...",
                scale=4
            )
            automotive_reset_btn = gr.Button("🔄 Reset", scale=1, variant="secondary")
        
        gr.Examples(
            examples=[
                "So sánh Audi A4 và Honda Civic về tính năng an toàn",
                "Tin tức mới nhất về xe điện Tesla",
                "Bảo dưỡng định kỳ cho Honda Accord cần làm gì?",
                "Toyota Camry 2024 có những nâng cấp gì?",
                "Xu hướng thị trường ô tô điện năm 2025"
            ],
            inputs=automotive_txt
        )
        
        automotive_txt.submit(automotive_bot_interface, [automotive_txt, automotive_chatbot], [automotive_txt, automotive_chatbot])
        automotive_reset_btn.click(reset_automotive_context, outputs=gr.Textbox(visible=False))
    
    with gr.Tab("📚 Knowledge Base Manager"):
        gr.Markdown("""
        ## 📚 Vector Database & RAG Management System
        
        **🎯 Quản lý cơ sở tri thức thông minh cho AI Automotive Consultant**
        
        ### 🌟 Tính năng:
        - 📤 **Smart Document Upload**: Hỗ trợ PDF, TXT, Markdown
        - 🔧 **Auto Text Processing**: Tự động phân chunk và preprocessing
        - 🗄️ **ChromaDB Vector Storage**: Lưu trữ embedding hiệu quả
        - 🔍 **Semantic Search**: Tìm kiếm theo nghĩa, không chỉ từ khóa
        - 📊 **Real-time Statistics**: Monitor database performance
        
        ### 🚀 Workflow:
        1. **Upload**: Tải tài liệu automotive lên hệ thống
        2. **Processing**: AI tự động phân tích và tạo embeddings
        3. **Storage**: Lưu vào ChromaDB với metadata
        4. **Integration**: Sử dụng ngay trong AI Consultant
        
        **💡 Gợi ý tài liệu tốt:**
        - Manual xe Audi/Honda
        - Review chuyên sâu từ Car & Driver, Motor Trend
        - Thông số kỹ thuật chính thức từ nhà sản xuất
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 📤 Upload Documents")
                upload_file = gr.File(
                    label="📄 Choose File (PDF, TXT, MD)",
                    file_types=[".pdf", ".txt", ".md"]
                )
                upload_description = gr.Textbox(
                    label="📝 Description (optional)",
                    placeholder="Ví dụ: Manual Audi A4 2024, Review Honda Civic..."
                )
                upload_btn = gr.Button("📤 Upload to Knowledge Base", variant="primary")
                upload_result = gr.Textbox(label="📊 Upload Status", lines=3)
                
            with gr.Column(scale=1):
                gr.Markdown("### 🔍 Semantic Search")
                search_query = gr.Textbox(
                    label="🔎 Search Query",
                    placeholder="Ví dụ: động cơ turbo Audi, hệ thống an toàn Honda..."
                )
                search_btn = gr.Button("🔍 Semantic Search", variant="secondary")
                search_results = gr.Textbox(label="🎯 Search Results", lines=8)
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 📊 Database Statistics")
                stats_btn = gr.Button("📊 View Statistics", variant="secondary")
                stats_display = gr.Textbox(label="📈 Knowledge Base Stats", lines=4)
                
            with gr.Column(scale=1):
                gr.Markdown("### 🗑️ Reset Database")
                gr.Markdown("⚠️ **Warning**: This will permanently delete all data!")
                clear_btn = gr.Button("🗑️ Clear All Data", variant="stop")
                clear_result = gr.Textbox(label="⚠️ Clear Status", lines=2)
        
        # Event handlers for KB Management
        upload_btn.click(upload_file_interface, [upload_file, upload_description], upload_result)
        search_btn.click(search_kb_interface, search_query, search_results)
        search_query.submit(search_kb_interface, search_query, search_results)
        stats_btn.click(get_kb_stats_interface, outputs=stats_display)
        clear_btn.click(clear_kb_interface, outputs=clear_result)
    
    # with gr.Tab("🧠 Context-Aware Bot (28June)"):
    #     gr.Markdown("""
    #     ### Bot với Context Management + Function Calling
        #
    #     **✨ Đặc điểm:**
    #     - 🧠 **Nhớ toàn bộ cuộc trò chuyện**
    #     - 🔗 **Hiểu references** ("nó", "xe đó", "mẹo này")
    #     - 📚 **Context summary** để quản lý token
    #     - 🔧 **Function calling** với context
        
    #     **💡 Thử nghiệm:**
    #     1. "Gợi ý xe SUV cho tôi"
    #     2. "Honda CR-V có ưu điểm gì?" ← Hiểu CR-V từ response trước
    #     3. "Giá của nó như thế nào?" ← "nó" = Honda CR-V
    #     """)
    #
    #     context_chatbot = gr.Chatbot(type="messages", height=400)
    #     with gr.Row():
    #         context_txt = gr.Textbox(
    #             show_label=False, 
    #             placeholder="Hỏi về xe, rồi tiếp tục hỏi chi tiết về xe đó...",
    #             scale=4
    #         )
    #         reset_btn = gr.Button("🔄 Reset Context", scale=1)
    #
    #     context_txt.submit(context_aware_chatbot_interface, [context_txt, context_chatbot], [context_txt, context_chatbot])
    #     reset_btn.click(reset_context, outputs=gr.Textbox(visible=False))
    
    # with gr.Tab("🔧 Function Calling Bot (28June)"):
    #     gr.Markdown("""
    #     ### Bot với Function Calling (No Context)
    #
    #     **✨ Đặc điểm:**
    #     - 🔧 **Function calling** capabilities
    #     - 🔁 **Retry mechanism**
    #     - ❌ **Không nhớ** cuộc trò chuyện trước
        
    #     **💡 Hạn chế:**
    #     - Mỗi câu hỏi được xử lý độc lập
    #     - Không hiểu references
    #     """)
        
    #     function_chatbot = gr.Chatbot(type="messages", height=400)
    #     with gr.Row():
    #         function_txt = gr.Textbox(
    #             show_label=False, 
    #             placeholder="Hỏi về xe hơi, bảo dưỡng, gợi ý xe...",
    #             scale=4
    #         )
        
    #     function_txt.submit(chatbot_interface, [function_txt, function_chatbot], [function_txt, function_chatbot])
    
    # with gr.Tab("📖 Simple FAQ Bot (21June)"):
    #     gr.Markdown("""
    #     ### Bot thông thường (FAQ only)
        
    #     **✨ Đặc điểm:**
    #     - 📖 **Chỉ dữ liệu FAQ** tĩnh
    #     - 🔁 **Retry mechanism**
    #     - ❌ **Không có function calling**
    #     - ❌ **Không có context**
    #     """)
        
    #     simple_chatbot = gr.Chatbot(type="messages", height=400)
    #     with gr.Row():
    #         simple_txt = gr.Textbox(
    #             show_label=False, 
    #             placeholder="Hỏi câu hỏi về ô tô (FAQ cơ bản)...",
    #             scale=4
    #         )
        
    #     simple_txt.submit(simple_chatbot_interface, [simple_txt, simple_chatbot], [simple_txt, simple_chatbot])

if __name__ == "__main__":
    demo.launch()
    # demo.launch(
    #     server_name="http://127.0.0.1/",
    #     server_port=7860,
    #     share=True,
    #     show_api=False,
    #     favicon_path=None
    # )
