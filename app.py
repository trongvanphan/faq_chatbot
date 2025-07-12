import gradio as gr
import os
from context_manager import get_contextual_response, reset_conversation, get_conversation_info
from faq_bot import get_faq_answer_with_functions, get_faq_answer
from automotive_bot import get_automotive_response, reset_automotive_conversation, get_automotive_info
from kb_manager import upload_document_to_kb, get_kb_stats, search_kb, clear_kb
from it_helpdesk_bot import get_it_helpdesk_response, reset_it_helpdesk_conversation, get_it_device_list

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
    """LangChain Automotive Bot with ChromaDB"""
    try:
        answer = get_automotive_response(user_input)
        
        # Get context information for display
        context_info = get_automotive_info()
        status_msg = f"✅ LangChain Bot: {context_info['message_count']} messages, Status: {context_info['status']}"
        
    except Exception as e:
        answer = f"❌ Lỗi: {str(e)}"
        status_msg = "❌ Thất bại"
    
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

# IT Helpdesk Bot Interface Functions
def it_helpdesk_interface(user_input, history):
    """IT Helpdesk bot interface"""
    try:
        if not user_input.strip():
            return history, ""
        
        response = get_it_helpdesk_response(user_input)
        
        # Ensure history is a list of dicts for Gradio Chatbot
        history = history or []
        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": response})
        
        return history, ""
    except Exception as e:
        error_msg = f"❌ Lỗi IT Helpdesk: {str(e)}"
        history = history or []
        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": error_msg})
        return history, ""

def reset_it_helpdesk_interface():
    """Reset IT helpdesk conversation"""
    reset_it_helpdesk_conversation()
    return [], ""  # Clear chatbot and devices display

def get_device_list_interface():
    """Get available devices for status check"""
    return get_it_device_list()

# Get retry configuration for display
retry_attempts = os.getenv("RETRY_ATTEMPTS", "3")
retry_wait_min = os.getenv("RETRY_WAIT_MIN", "1")
retry_wait_max = os.getenv("RETRY_WAIT_MAX", "10")

with gr.Blocks() as demo:
    gr.Markdown(f"""
    # 🚗 FAQ Chatbot: Context Management & Multi-turn Conversations
    
    **Demo năm cấp độ chatbot khác nhau:**
    
    **🔁 Retry Configuration:** Max attempts: {retry_attempts}, Wait: {retry_wait_min}-{retry_wait_max}s
    """)
    
    with gr.Tab("🤖 Automotive Bot"):
        gr.Markdown("""
        ### LangChain Automotive Bot với ChromaDB Vector Store
        
        **✨ Đặc điểm:**
        - 🧠 **LangChain ConversationalRetrievalChain**
        - 🗄️ **ChromaDB local vector database**
        - 🔍 **Similarity search** cho câu trả lời chính xác
        - 💬 **Conversational memory** nhớ ngữ cảnh
        - 📚 **RAG (Retrieval-Augmented Generation)**
        
        **💡 Cách sử dụng:**
        1. Hỏi bất kỳ câu hỏi nào về ô tô
        2. Bot sẽ tìm kiếm trong knowledge base
        3. Trả lời dựa trên thông tin đã được index
        """)
        
        automotive_chatbot = gr.Chatbot(type="messages", height=400)
        with gr.Row():
            automotive_txt = gr.Textbox(
                show_label=False, 
                placeholder="Hỏi về xe hơi, công nghệ ô tô, bảo dưỡng...",
                scale=4
            )
            automotive_reset_btn = gr.Button("🔄 Reset Chat", scale=1)
        
        automotive_txt.submit(automotive_bot_interface, [automotive_txt, automotive_chatbot], [automotive_txt, automotive_chatbot])
        automotive_reset_btn.click(reset_automotive_context, outputs=gr.Textbox(visible=False))
    
    with gr.Tab("📚 KB Management - RAG"):
        gr.Markdown("""
        ### Knowledge Base Management với RAG
        
        **✨ Tính năng:**
        - 📤 **Upload documents** (PDF, TXT, MD)
        - 🔧 **Text chunking** và preprocessing
        - 🗄️ **ChromaDB vector storage** với FAISS
        - 🔍 **Similarity search** trong knowledge base
        - 📊 **Statistics** và monitoring
        
        **📋 Quy trình:**
        1. Upload tài liệu automotive
        2. Hệ thống tự động chunking và embedding
        3. Lưu vào ChromaDB local database
        4. Sử dụng trong Automotive Bot ở tab trước
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 📤 Upload Document")
                upload_file = gr.File(
                    label="Choose File (PDF, TXT, MD)",
                    file_types=[".pdf", ".txt", ".md"]
                )
                upload_description = gr.Textbox(
                    label="Description (optional)",
                    placeholder="Mô tả ngắn về tài liệu..."
                )
                upload_btn = gr.Button("📤 Upload to KB", variant="primary")
                upload_result = gr.Textbox(label="Upload Status", lines=3)
                
            with gr.Column(scale=1):
                gr.Markdown("### 🔍 Search Knowledge Base")
                search_query = gr.Textbox(
                    label="Search Query",
                    placeholder="Nhập từ khóa tìm kiếm..."
                )
                search_btn = gr.Button("🔍 Search")
                search_results = gr.Textbox(label="Search Results", lines=8)
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 📊 KB Statistics")
                stats_btn = gr.Button("📊 Get Stats")
                stats_display = gr.Textbox(label="Statistics", lines=4)
                
            with gr.Column(scale=1):
                gr.Markdown("### 🗑️ Clear KB")
                gr.Markdown("⚠️ **Cảnh báo:** Thao tác này sẽ xóa toàn bộ dữ liệu!")
                clear_btn = gr.Button("🗑️ Clear All Data", variant="stop")
                clear_result = gr.Textbox(label="Clear Status", lines=2)
        
        # Event handlers for KB Management
        upload_btn.click(upload_file_interface, [upload_file, upload_description], upload_result)
        search_btn.click(search_kb_interface, search_query, search_results)
        search_query.submit(search_kb_interface, search_query, search_results)
        stats_btn.click(get_kb_stats_interface, outputs=stats_display)
        clear_btn.click(clear_kb_interface, outputs=clear_result)
    
    with gr.Tab("🧠 Context-Aware Bot (28June)"):
        gr.Markdown("""
        ### Bot với Context Management + Function Calling
        
        **✨ Đặc điểm:**
        - 🧠 **Nhớ toàn bộ cuộc trò chuyện**
        - 🔗 **Hiểu references** ("nó", "xe đó", "mẹo này")
        - 📚 **Context summary** để quản lý token
        - 🔧 **Function calling** với context
        
        **💡 Thử nghiệm:**
        1. "Gợi ý xe SUV cho tôi"
        2. "Honda CR-V có ưu điểm gì?" ← Hiểu CR-V từ response trước
        3. "Giá của nó như thế nào?" ← "nó" = Honda CR-V
        """)
        
        context_chatbot = gr.Chatbot(type="messages", height=400)
        with gr.Row():
            context_txt = gr.Textbox(
                show_label=False, 
                placeholder="Hỏi về xe, rồi tiếp tục hỏi chi tiết về xe đó...",
                scale=4
            )
            reset_btn = gr.Button("🔄 Reset Context", scale=1)
        
        context_txt.submit(context_aware_chatbot_interface, [context_txt, context_chatbot], [context_txt, context_chatbot])
        reset_btn.click(reset_context, outputs=gr.Textbox(visible=False))
    
    with gr.Tab("🔧 Function Calling Bot (28June)"):
        gr.Markdown("""
        ### Bot với Function Calling (No Context)
        
        **✨ Đặc điểm:**
        - 🔧 **Function calling** capabilities
        - 🔁 **Retry mechanism**
        - ❌ **Không nhớ** cuộc trò chuyện trước
        
        **💡 Hạn chế:**
        - Mỗi câu hỏi được xử lý độc lập
        - Không hiểu references
        """)
        
        function_chatbot = gr.Chatbot(type="messages", height=400)
        with gr.Row():
            function_txt = gr.Textbox(
                show_label=False, 
                placeholder="Hỏi về xe hơi, bảo dưỡng, gợi ý xe...",
                scale=4
            )
        
        function_txt.submit(chatbot_interface, [function_txt, function_chatbot], [function_txt, function_chatbot])
    
    with gr.Tab("📖 Simple FAQ Bot (21June)"):
        gr.Markdown("""
        ### Bot thông thường (FAQ only)
        
        **✨ Đặc điểm:**
        - 📖 **Chỉ dữ liệu FAQ** tĩnh
        - 🔁 **Retry mechanism**
        - ❌ **Không có function calling**
        - ❌ **Không có context**
        """)
        
        simple_chatbot = gr.Chatbot(type="messages", height=400)
        with gr.Row():
            simple_txt = gr.Textbox(
                show_label=False, 
                placeholder="Hỏi câu hỏi về ô tô (FAQ cơ bản)...",
                scale=4
            )
        
        simple_txt.submit(simple_chatbot_interface, [simple_txt, simple_chatbot], [simple_txt, simple_chatbot])
    
    with gr.Tab("💻 IT Helpdesk Bot"):
        gr.Markdown("""
        ### 🔧 IT Helpdesk Bot (Based on sample.py)
        
        **✨ Features:**
        - 💬 **RAG-powered IT Support** (FAISS + LangChain)
        - 🔧 **Function Calling** (System status, Ticket creation)  
        - � **Knowledge Base** (Password reset, VPN, Printers, etc.)
        - 🎫 **IT Ticket System** (Create tickets for complex issues)
        
        **💡 Try these:**
        - "How to reset my password?"
        - "Check status of printer01"
        - "Create a ticket for broken laptop"
        - "My computer is running slow"
        """)
        
        it_helpdesk_chatbot = gr.Chatbot(type="messages", height=400)
        
        with gr.Row():
            it_helpdesk_txt = gr.Textbox(
                show_label=False, 
                placeholder="Describe your IT issue or ask for system status...",
                scale=3
            )
            it_helpdesk_reset_btn = gr.Button("🔄 Reset", scale=1)
        
        with gr.Row():
            devices_btn = gr.Button("📋 Available Devices", scale=1)
            devices_display = gr.Textbox(
                label="System Devices",
                placeholder="Click 'Available Devices' to see monitored systems...",
                lines=3,
                scale=2,
                interactive=False
            )
        
        # Event handlers
        it_helpdesk_txt.submit(
            it_helpdesk_interface, 
            [it_helpdesk_txt, it_helpdesk_chatbot], 
            [it_helpdesk_chatbot, it_helpdesk_txt]
        )
        it_helpdesk_reset_btn.click(
            reset_it_helpdesk_interface, 
            outputs=[it_helpdesk_chatbot, devices_display]
        )
        devices_btn.click(
            get_device_list_interface, 
            outputs=devices_display
        )

demo.launch()
