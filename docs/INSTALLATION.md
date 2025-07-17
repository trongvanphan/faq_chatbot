# 🚀 Installation Guide

## Hướng dẫn cài đặt và chạy FAQ Chatbot

### 📋 Yêu cầu hệ thống
- Python 3.8+ (Python 3.11+ recommended)
- OpenAI API Key (required)
- Tavily API Key (optional - for web search features)
- 4GB RAM (recommended for optimal performance)
- 2GB disk space cho ChromaDB vector database

### 🔧 Cài đặt

#### Bước 1: Clone project
```bash
git clone https://github.com/trongvanphan/faq_chatbot.git
cd faq_chatbot
```

#### Bước 2: Tự động cài đặt (Khuyến nghị)
```bash
# Chạy script cài đặt tự động (tạo virtual environment + cài dependencies)
chmod +x setup.sh
./setup.sh
```

#### Bước 3: Cấu hình API Keys
```bash
# Copy template và edit file .env
cp .env.example .env
nano .env

# Thêm các API keys cần thiết:
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here  # Optional for web search
```

#### Bước 4: Chạy ứng dụng
```bash
# Kích hoạt virtual environment
source venv/bin/activate

# Chạy app
python app.py
```

### 🔧 Cài đặt thủ công (nếu script tự động không hoạt động)

#### 1. Tạo Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# hoặc
venv\Scripts\activate     # Windows
```

#### 2. Upgrade pip
```bash
pip install --upgrade pip
```

#### 3. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

#### 4. Tạo file cấu hình
```bash
cp .env.example .env
```

#### 5. Cấu hình OpenAI API Key
Mở file `.env` và thêm:
```
OPENAI_API_KEY=your_openai_api_key_here
```

#### 6. Tạo thư mục ChromaDB
```bash
mkdir chroma_db
```

### 🧪 Kiểm tra cài đặt

```bash
# Chạy test setup (nếu có)
python -c "
import openai, gradio, chromadb, langchain
print('✅ All dependencies installed successfully')
"

# Test OpenAI connection
python -c "
import openai
import os
from dotenv import load_dotenv
load_dotenv()
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
print('✅ OpenAI connection successful')
"
```

### 🛠️ Troubleshooting

#### 🔧 Lỗi thường gặp

**1. ModuleNotFoundError: No module named 'xxx'**
```bash
# Đảm bảo virtual environment được kích hoạt
source venv/bin/activate
pip install -r requirements.txt
```

**2. OpenAI API Error**
```bash
# Kiểm tra API key trong .env
cat .env | grep OPENAI_API_KEY
# Đảm bảo API key hợp lệ và có credit
```

**3. ChromaDB Error**
```bash
# Tạo thư mục ChromaDB
mkdir -p chroma_db
# Kiểm tra quyền ghi
touch chroma_db/test.txt && rm chroma_db/test.txt
```

**4. Gradio không khởi động**
```bash
# Kiểm tra port 7860 có bị chiếm không
lsof -i :7860
# Hoặc thử port khác
python app.py --server-port 7861
```

**5. Tavily API Error (Optional)**
```bash
# Tavily là tùy chọn, ứng dụng vẫn chạy được mà không có
# Chỉ ảnh hưởng đến tính năng web search
echo "TAVILY_API_KEY=optional" >> .env
```

### 🌐 Chạy ứng dụng

```bash
python app.py
```

Mở trình duyệt và truy cập: http://127.0.0.1:7860

### 📱 Giao diện ứng dụng

Sau khi chạy thành công, bạn sẽ thấy các tab chính:

1. **🚗 AI Automotive Consultant** - LangChain agent với ChromaDB và web search
2. **📚 Knowledge Base Manager** - Upload và quản lý tài liệu RAG
3. **🧠 Context-Aware Bot** - Bot nhớ ngữ cảnh đa lượt hội thoại
4. **🔧 Function Calling Bot** - OpenAI function calling cho câu hỏi có cấu trúc
5. **💬 Simple FAQ Bot** - FAQ cơ bản không có function calling

### 🎯 Tính năng chính

- **Intelligent Fallback**: Tự động chuyển đổi giữa Knowledge Base → Agent → Direct Chat
- **Transparent Reasoning**: Hiển thị quá trình suy nghĩ của AI agent
- **Real-time Web Search**: Tìm kiếm tin tức ô tô mới nhất qua Tavily API
- **Conversation Memory**: Nhớ ngữ cảnh qua nhiều lượt hội thoại
- **Document Upload**: Upload PDF, TXT, MD để mở rộng knowledge base
4. **🔧 Function Calling Bot** - Bot với function calling
5. **📖 Simple FAQ Bot** - Bot FAQ đơn giản

### 🚨 Xử lý lỗi thường gặp

#### Lỗi: `Import "gradio" could not be resolved`
```bash
pip install gradio
```

#### Lỗi: `Import "chromadb" could not be resolved` 
```bash
pip install chromadb
```

#### Lỗi: `Import "langchain" could not be resolved`
```bash
pip install langchain langchain-openai
```

#### Lỗi: `OpenAI API Key not found`
- Kiểm tra file `.env` có tồn tại
- Đảm bảo `OPENAI_API_KEY` được cấu hình đúng
- Restart ứng dụng sau khi thay đổi

#### Lỗi: ChromaDB database lock
```bash
# Xóa và tạo lại database
rm -rf chroma_db
mkdir chroma_db
```

#### Lỗi: Memory issues
- Giảm `chunk_size` trong `kb_manager.py`
- Tăng RAM hoặc sử dụng swap file
- Clear ChromaDB nếu quá lớn

### 🔄 Cập nhật

```bash
# Pull code mới
git pull origin main

# Update dependencies  
pip install -r requirements.txt --upgrade

# Restart app
python app.py
```

### 🗑️ Gỡ cài đặt

```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment
rm -rf venv

# Remove ChromaDB
rm -rf chroma_db

# Remove config file
rm .env
```

### 💡 Tips

1. **Performance**: Upload nhỏ từng file thay vì upload nhiều file lớn cùng lúc
2. **Memory**: Restart app định kỳ nếu sử dụng lâu dài  
3. **Backup**: Backup `chroma_db/` folder để lưu knowledge base
4. **Development**: Sử dụng `LANGCHAIN_VERBOSE=true` để debug

### 📞 Hỗ trợ

Nếu gặp vấn đề:
1. Chạy `python test_setup.py` để kiểm tra
2. Xem logs trong terminal
3. Restart app và thử lại
4. Check GitHub Issues
