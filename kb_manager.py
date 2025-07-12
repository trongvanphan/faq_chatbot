"""
Knowledge Base Management with RAG (Retrieval-Augmented Generation)
Handles document upload, processing, and indexing into ChromaDB with FAISS
"""

import os
import tempfile
import shutil
from typing import List, Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables (same as faq_bot.py)
load_dotenv()

# Configuration from environment variables
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://aiportalapi.stu-platform.live/jpe")
MODEL = os.getenv("MODEL_NAME", "GPT-4o-mini")

try:
    import chromadb
    from chromadb.config import Settings
    import pandas as pd
    import openai
    
    # Initialize OpenAI client with same config as faq_bot.py
    openai_client = openai.OpenAI(
        base_url=OPENAI_BASE_URL,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Try to import document processing dependencies
    try:
        import PyPDF2
        PDF_AVAILABLE = True
    except ImportError:
        print("⚠️ PyPDF2 not available. PDF processing disabled.")
        PDF_AVAILABLE = False
    
    # Try to import LangChain dependencies
    try:
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain.embeddings import OpenAIEmbeddings
        from langchain.vectorstores import Chroma
        from langchain.schema import Document
        LANGCHAIN_AVAILABLE = True
    except ImportError:
        print("⚠️ LangChain not available. Using simple text processing.")
        LANGCHAIN_AVAILABLE = False
        
    # Try to import additional dependencies
    try:
        import faiss
        import numpy as np
        FAISS_AVAILABLE = True
    except ImportError:
        print("⚠️ FAISS not available. Using ChromaDB default similarity search.")
        FAISS_AVAILABLE = False
        
except ImportError as e:
    print(f"⚠️ Some dependencies not available: {e}")
    LANGCHAIN_AVAILABLE = False
    PDF_AVAILABLE = False
    FAISS_AVAILABLE = False
    openai_client = None

# Initialize ChromaDB client
try:
    chroma_client = chromadb.PersistentClient(path=os.getenv("CHROMA_DB_PATH", "./chroma_db"))
except:
    chroma_client = None

class KnowledgeBaseManager:
    def __init__(self):
        self.embeddings = None
        self.vectorstore = None
        self.text_splitter = None
        self.collection_name = "automotive_knowledge"
        self.simple_storage = {}  # Fallback storage
        self.initialize_components()
    
    def initialize_components(self):
        """Initialize components for KB management"""
        try:
            if LANGCHAIN_AVAILABLE and chroma_client and openai_client:
                self._initialize_langchain()
            else:
                self._initialize_fallback()
                
        except Exception as e:
            print(f"Error initializing KnowledgeBaseManager: {str(e)}")
            self._initialize_fallback()
    
    def _initialize_langchain(self):
        """Initialize with full LangChain components"""
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_api_base=OPENAI_BASE_URL
        )
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Initialize vector store
        self.vectorstore = Chroma(
            client=chroma_client,
            collection_name=self.collection_name,
            embedding_function=self.embeddings
        )
        
        print("✅ KB Manager initialized with LangChain + ChromaDB")
    
    def _initialize_fallback(self):
        """Initialize fallback mode without LangChain"""
        self.vectorstore = None
        self.embeddings = None
        self.text_splitter = None
        self.simple_storage = {}
        print("⚠️ KB Manager running in fallback mode (simple storage)")
    
    def simple_text_split(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Simple text splitting without LangChain"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            
            # Try to find a good break point
            if end < len(text):
                # Look for sentence endings
                for i in range(end, max(start + chunk_size - 200, start), -1):
                    if text[i:i+1] in '.!?\n':
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = max(start + chunk_size - overlap, end)
        
        return chunks
    
    def process_pdf(self, file_path: str) -> List[str]:
        """Extract text from PDF file"""
        if not PDF_AVAILABLE:
            return []
            
        try:
            texts = []
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if text.strip():
                        texts.append(text)
            return texts
        except Exception as e:
            print(f"Error processing PDF: {str(e)}")
            return []
    
    def process_text_file(self, file_path: str) -> List[str]:
        """Extract text from text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                return [content] if content.strip() else []
        except Exception as e:
            print(f"Error processing text file: {str(e)}")
            return []
    
    def process_document(self, file_path: str, file_name: str) -> Dict[str, Any]:
        """Process uploaded document and extract text"""
        try:
            file_extension = Path(file_name).suffix.lower()
            
            if file_extension == '.pdf':
                if not PDF_AVAILABLE:
                    return {
                        "success": False,
                        "message": "PDF processing không có sẵn. Vui lòng cài đặt PyPDF2.",
                        "chunks": 0
                    }
                texts = self.process_pdf(file_path)
            elif file_extension in ['.txt', '.md']:
                texts = self.process_text_file(file_path)
            else:
                return {
                    "success": False,
                    "message": f"Định dạng file không được hỗ trợ: {file_extension}",
                    "chunks": 0
                }
            
            if not texts:
                return {
                    "success": False,
                    "message": "Không thể trích xuất nội dung từ file",
                    "chunks": 0
                }
            
            # Combine all texts
            full_text = "\n\n".join(texts)
            
            # Split into chunks
            if self.text_splitter:
                chunks = self.text_splitter.split_text(full_text)
            else:
                chunks = self.simple_text_split(full_text)
            
            return {
                "success": True,
                "message": f"Đã xử lý thành công file {file_name}",
                "chunks": len(chunks),
                "content": chunks
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Lỗi khi xử lý file: {str(e)}",
                "chunks": 0
            }
    
    def add_to_vectorstore(self, chunks: List[str], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Add processed chunks to vector store"""
        try:
            if self.vectorstore:
                # LangChain mode
                documents = []
                for i, chunk in enumerate(chunks):
                    doc_metadata = {
                        **metadata,
                        "chunk_id": i,
                        "chunk_size": len(chunk)
                    }
                    documents.append(Document(
                        page_content=chunk,
                        metadata=doc_metadata
                    ))
                
                # Add to vector store
                self.vectorstore.add_documents(documents)
                
                return {
                    "success": True,
                    "message": f"Đã thêm {len(chunks)} chunks vào ChromaDB",
                    "added_chunks": len(chunks)
                }
            else:
                # Fallback mode - simple storage
                doc_id = metadata.get("filename", "unknown")
                self.simple_storage[doc_id] = {
                    "chunks": chunks,
                    "metadata": metadata
                }
                
                return {
                    "success": True,
                    "message": f"Đã lưu {len(chunks)} chunks vào simple storage",
                    "added_chunks": len(chunks)
                }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Lỗi khi thêm vào storage: {str(e)}"
            }
    
    def upload_document(self, file_path: str, file_name: str, description: str = "") -> Dict[str, Any]:
        """Complete pipeline: process document and add to vector store"""
        try:
            # Process document
            process_result = self.process_document(file_path, file_name)
            
            if not process_result["success"]:
                return process_result
            
            # Prepare metadata
            metadata = {
                "filename": file_name,
                "description": description,
                "upload_date": str(pd.Timestamp.now()) if 'pd' in globals() else "unknown",
                "total_chunks": process_result["chunks"]
            }
            
            # Add to vector store
            add_result = self.add_to_vectorstore(process_result["content"], metadata)
            
            if add_result["success"]:
                storage_type = "ChromaDB" if self.vectorstore else "Simple Storage"
                return {
                    "success": True,
                    "message": f"✅ Upload thành công!\n📄 File: {file_name}\n📊 Chunks: {process_result['chunks']}\n💾 Lưu vào {storage_type}",
                    "filename": file_name,
                    "chunks": process_result["chunks"]
                }
            else:
                return add_result
                
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Lỗi trong quá trình upload: {str(e)}"
            }
    
    def get_knowledge_base_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        try:
            if self.vectorstore and chroma_client:
                # ChromaDB mode
                collection = chroma_client.get_collection(self.collection_name)
                count = collection.count()
                
                return {
                    "total_chunks": count,
                    "status": "ChromaDB Active",
                    "collection_name": self.collection_name,
                    "mode": "vector_db"
                }
            else:
                # Fallback mode
                total_chunks = sum(len(doc["chunks"]) for doc in self.simple_storage.values())
                return {
                    "total_chunks": total_chunks,
                    "total_documents": len(self.simple_storage),
                    "status": "Simple Storage Active",
                    "collection_name": "simple_storage",
                    "mode": "fallback"
                }
            
        except Exception as e:
            return {
                "total_chunks": 0,
                "status": f"Error: {str(e)}",
                "collection_name": self.collection_name,
                "mode": "error"
            }
    
    def search_knowledge_base(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search in the knowledge base"""
        try:
            if self.vectorstore:
                # ChromaDB mode
                results = self.vectorstore.similarity_search_with_score(query, k=k)
                
                search_results = []
                for doc, score in results:
                    search_results.append({
                        "content": doc.page_content[:300] + "...",
                        "metadata": doc.metadata,
                        "similarity_score": 1 - score  # Convert distance to similarity
                    })
                
                return search_results
            else:
                # Fallback mode - simple text search
                search_results = []
                query_lower = query.lower()
                
                for doc_id, doc_data in self.simple_storage.items():
                    for i, chunk in enumerate(doc_data["chunks"]):
                        if query_lower in chunk.lower():
                            # Simple relevance scoring based on keyword frequency
                            score = chunk.lower().count(query_lower) / len(chunk.split())
                            search_results.append({
                                "content": chunk[:300] + "...",
                                "metadata": {
                                    **doc_data["metadata"],
                                    "chunk_id": i
                                },
                                "similarity_score": min(score * 10, 1.0)  # Normalize to 0-1
                            })
                
                # Sort by relevance and return top k
                search_results.sort(key=lambda x: x["similarity_score"], reverse=True)
                return search_results[:k]
            
        except Exception as e:
            print(f"Error searching knowledge base: {str(e)}")
            return []
    
    def clear_knowledge_base(self) -> Dict[str, Any]:
        """Clear all data from knowledge base"""
        try:
            if self.vectorstore and chroma_client:
                # ChromaDB mode
                chroma_client.delete_collection(self.collection_name)
                
                # Reinitialize vector store
                self.vectorstore = Chroma(
                    client=chroma_client,
                    collection_name=self.collection_name,
                    embedding_function=self.embeddings
                )
                
                return {
                    "success": True,
                    "message": "🗑️ Đã xóa toàn bộ ChromaDB knowledge base"
                }
            else:
                # Fallback mode
                self.simple_storage.clear()
                
                return {
                    "success": True,
                    "message": "🗑️ Đã xóa toàn bộ simple storage"
                }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Lỗi khi xóa knowledge base: {str(e)}"
            }

# Global instance
kb_manager = KnowledgeBaseManager()

def upload_document_to_kb(file_path: str, file_name: str, description: str = "") -> str:
    """Upload document to knowledge base"""
    result = kb_manager.upload_document(file_path, file_name, description)
    return result["message"]

def get_kb_stats() -> Dict[str, Any]:
    """Get knowledge base statistics"""
    return kb_manager.get_knowledge_base_stats()

def search_kb(query: str, k: int = 5) -> List[Dict[str, Any]]:
    """Search knowledge base"""
    return kb_manager.search_knowledge_base(query, k)

def clear_kb() -> str:
    """Clear knowledge base"""
    result = kb_manager.clear_knowledge_base()
    return result["message"]
