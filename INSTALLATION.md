# 🚀 Installation Guide

## Hướng dẫn cài đặt và chạy FAQ Chatbot

### 📋 Yêu cầu hệ thống
- Python 3.8+ 
- OpenAI API Key
- 4GB RAM (khuyến nghị)
- 2GB disk space cho ChromaDB

### 🔧 Cài đặt

#### Bước 1: Clone project (nếu chưa có)
```bash
git clone <repository-url>
cd faq_chatbot
```

#### Bước 2: Tự động cài đặt (Khuyến nghị)
```bash
# Chạy script cài đặt tự động
./setup.sh
```

#### Bước 3: Cấu hình API Key
```bash
# Edit file .env
nano .env

# Thêm OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here
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
# Chạy test setup
python test_setup.py
```

### 🌐 Chạy ứng dụng

```bash
python app.py
```

Mở trình duyệt và truy cập: http://127.0.0.1:7860

### 📱 Giao diện ứng dụng

Sau khi chạy thành công, bạn sẽ thấy 5 tab:

1. **🤖 Automotive Bot** - LangChain với ChromaDB
2. **📚 KB Management - RAG** - Upload và quản lý tài liệu  
3. **🧠 Context-Aware Bot** - Bot nhớ ngữ cảnh
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
