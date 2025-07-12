"""
Knowledge Base Management with RAG and ChromaDB
"""

import os
import tempfile
from typing import List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Configuration
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
MODEL = os.getenv("MODEL_NAME", "GPT-4o-mini")

try:
    import chromadb
    import openai
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.schema import Document
    
    # PDF processing
    try:
        import PyPDF2
        PDF_AVAILABLE = True
    except ImportError:
        PDF_AVAILABLE = False
    
    # Initialize clients
    openai_client = openai.OpenAI(
        base_url=OPENAI_BASE_URL,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    
except ImportError as e:
    print(f"⚠️ Dependencies not available: {e}")
    openai_client = None
    chroma_client = None
    PDF_AVAILABLE = False

class CustomOpenAIEmbeddings:
    """Custom embedding class using OpenAI API directly"""
    def __init__(self, api_key, base_url, model="text-embedding-3-small"):
        import openai
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        
    def embed_documents(self, texts):
        embeddings = []
        for text in texts:
            response = self.client.embeddings.create(model=self.model, input=text)
            embeddings.append(response.data[0].embedding)
        return embeddings
        
    def embed_query(self, text):
        response = self.client.embeddings.create(model=self.model, input=text)
        return response.data[0].embedding

class KnowledgeBaseManager:
    def __init__(self):
        self.embeddings = None
        self.chroma_collection = None
        self.text_splitter = None
        self.initialize_components()
    
    def initialize_components(self):
        """Initialize KB manager components"""
        try:
            if chroma_client and openai_client:
                self._setup_components()
            else:
                print("⚠️ KB Manager running in limited mode")
        except Exception as e:
            print(f"Error initializing KB Manager: {e}")
    
    def _setup_components(self):
        """Setup embeddings and ChromaDB"""
        # Initialize embeddings
        self.embeddings = CustomOpenAIEmbeddings(
            api_key=os.getenv("EMBEDDING_KEY", os.getenv("OPENAI_API_KEY")),
            base_url=os.getenv("EMBEDDING_BASE_URL", OPENAI_BASE_URL),
            model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        )
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Connect to ChromaDB collection
        try:
            self.chroma_collection = chroma_client.get_collection("automotive_knowledge")
            print(f"✅ Connected to existing ChromaDB collection: automotive_knowledge (persist: ./chroma_db)")
            print(f"📊 Collection document count: {self.chroma_collection.count()}")
        except:
            self.chroma_collection = chroma_client.create_collection("automotive_knowledge")
            print("✅ Created new ChromaDB collection: automotive_knowledge")
        
        print("✅ KB Manager initialized with LangChain + ChromaDB")
            self.chroma_collection = chroma_client.get_collection(self.collection_name)
            print(f"✅ Connected to existing ChromaDB collection: {self.collection_name} (persist: {persist_directory})")
            print(f"📊 Collection document count: {self.chroma_collection.count()}")
        except Exception as e:
            print(f"⚠️ Error connecting to existing collection: {e}")
            # Create new collection if it doesn't exist
            self.chroma_collection = chroma_client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            print(f"✅ Created new ChromaDB collection: {self.collection_name} (persist: {persist_directory})")
        
        # For compatibility, keep vectorstore as None since we use chroma_collection directly
        self.vectorstore = None

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
            if hasattr(self, 'chroma_collection') and self.chroma_collection:
                # Direct ChromaDB mode for better reliability
                documents = []
                embeddings = []
                metadatas = []
                ids = []
                
                for i, chunk in enumerate(chunks):
                    doc_metadata = {
                        **metadata,
                        "chunk_id": i,
                        "chunk_size": len(chunk)
                    }
                    
                    # Generate embedding
                    embedding = self.embeddings.embed_query(chunk)
                    
                    # Create unique ID
                    doc_id = f"{metadata.get('filename', 'unknown')}_{i}_{hash(chunk) % 10000}"
                    
                    documents.append(chunk)
                    embeddings.append(embedding)
                    metadatas.append(doc_metadata)
                    ids.append(doc_id)
                
                # Add to ChromaDB collection directly
                self.chroma_collection.add(
                    documents=documents,
                    embeddings=embeddings,
                    metadatas=metadatas,
                    ids=ids
                )
                
                print(f"✅ Added {len(chunks)} chunks to ChromaDB. Total docs: {self.chroma_collection.count()}")
                
                return {
                    "success": True,
                    "message": f"Đã thêm {len(chunks)} chunks vào ChromaDB",
                    "added_chunks": len(chunks),
                    "total_documents": self.chroma_collection.count()
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
            if hasattr(self, 'chroma_collection') and self.chroma_collection:
                # Direct ChromaDB mode
                count = self.chroma_collection.count()
                
                return {
                    "total_chunks": count,
                    "status": "ChromaDB Active (Direct)",
                    "collection_name": self.collection_name,
                    "mode": "vector_db_direct"
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
            if hasattr(self, 'chroma_collection') and self.chroma_collection:
                # Direct ChromaDB mode
                query_embedding = self.embeddings.embed_query(query)
                
                results = self.chroma_collection.query(
                    query_embeddings=[query_embedding],
                    n_results=k
                )
                
                search_results = []
                if results["documents"] and results["documents"][0]:
                    for i, doc in enumerate(results["documents"][0]):
                        metadata = results["metadatas"][0][i] if results["metadatas"] and results["metadatas"][0] else {}
                        distance = results["distances"][0][i] if results["distances"] and results["distances"][0] else 0
                        
                        search_results.append({
                            "content": doc[:300] + "..." if len(doc) > 300 else doc,
                            "metadata": metadata,
                            "similarity_score": 1 - distance  # Convert distance to similarity
                        })
                
                return search_results
                
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
                try:
                    chroma_client.delete_collection(self.collection_name)
                    print(f"🗑️ Deleted collection: {self.collection_name}")
                except:
                    print(f"⚠️ Collection {self.collection_name} may not exist")
                
                # Reinitialize vector store with persist_directory
                self.vectorstore = Chroma(
                    client=chroma_client,
                    collection_name=self.collection_name,
                    embedding_function=self.embeddings,
                    persist_directory=os.getenv("CHROMA_DB_PATH", "./chroma_db")
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
