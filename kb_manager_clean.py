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
    
    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        if not PDF_AVAILABLE:
            return "PDF processing not available"
        
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            return f"Error reading PDF: {str(e)}"
    
    def _process_file(self, file_path: str, filename: str) -> Dict[str, Any]:
        """Process uploaded file and extract text"""
        try:
            file_extension = Path(filename).suffix.lower()
            
            if file_extension == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            elif file_extension == '.pdf':
                content = self._extract_text_from_pdf(file_path)
            else:
                return {"success": False, "message": f"Unsupported file type: {file_extension}"}
            
            if not content.strip():
                return {"success": False, "message": "No text content found"}
            
            # Split text into chunks
            if self.text_splitter:
                chunks = self.text_splitter.split_text(content)
            else:
                # Simple fallback splitting
                chunks = [content[i:i+1000] for i in range(0, len(content), 800)]
            
            # Prepare metadata
            metadata = {
                "filename": filename,
                "file_type": file_extension,
                "upload_date": "now",
                "chunk_count": len(chunks)
            }
            
            return {
                "success": True,
                "content": content,
                "chunks": chunks,
                "metadata": metadata
            }
            
        except Exception as e:
            return {"success": False, "message": f"Error processing file: {str(e)}"}
    
    def add_to_vectorstore(self, chunks: List[str], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Add text chunks to ChromaDB vectorstore"""
        try:
            if not self.chroma_collection or not self.embeddings:
                return {"success": False, "message": "ChromaDB not available"}
            
            # Generate embeddings for chunks
            embeddings = self.embeddings.embed_documents(chunks)
            
            # Prepare documents for ChromaDB
            ids = [f"{metadata['filename']}_{i}" for i in range(len(chunks))]
            metadatas = [metadata.copy() for _ in chunks]
            
            # Add to ChromaDB
            self.chroma_collection.add(
                documents=chunks,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            return {
                "success": True,
                "message": f"Added {len(chunks)} chunks to knowledge base",
                "chunks_added": len(chunks)
            }
            
        except Exception as e:
            return {"success": False, "message": f"Error adding to vectorstore: {str(e)}"}
    
    def search_knowledge_base(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """Search the knowledge base for relevant information"""
        try:
            if not self.chroma_collection or not self.embeddings:
                return {"success": False, "message": "Knowledge base not available"}
            
            # Generate query embedding
            query_embedding = self.embeddings.embed_query(query)
            
            # Search ChromaDB
            results = self.chroma_collection.query(
                query_embeddings=[query_embedding],
                n_results=max_results
            )
            
            # Format results
            search_results = []
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    metadata = results["metadatas"][0][i] if results["metadatas"] and results["metadatas"][0] else {}
                    distance = results["distances"][0][i] if results["distances"] and results["distances"][0] else 0
                    
                    search_results.append({
                        "content": doc,
                        "metadata": metadata,
                        "similarity_score": 1 - distance  # Convert distance to similarity
                    })
            
            return {
                "success": True,
                "results": search_results,
                "query": query,
                "total_results": len(search_results)
            }
            
        except Exception as e:
            return {"success": False, "message": f"Error searching knowledge base: {str(e)}"}
    
    def get_knowledge_base_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        try:
            if not self.chroma_collection:
                return {"success": False, "message": "Knowledge base not available"}
            
            count = self.chroma_collection.count()
            
            # Get sample of metadata to analyze
            if count > 0:
                sample = self.chroma_collection.get(limit=min(count, 100))
                file_types = {}
                filenames = set()
                
                if sample["metadatas"]:
                    for metadata in sample["metadatas"]:
                        if metadata:
                            file_type = metadata.get("file_type", "unknown")
                            filename = metadata.get("filename", "unknown")
                            
                            file_types[file_type] = file_types.get(file_type, 0) + 1
                            filenames.add(filename)
                
                return {
                    "success": True,
                    "total_chunks": count,
                    "unique_files": len(filenames),
                    "file_types": file_types,
                    "collection_name": "automotive_knowledge"
                }
            else:
                return {
                    "success": True,
                    "total_chunks": 0,
                    "unique_files": 0,
                    "file_types": {},
                    "collection_name": "automotive_knowledge"
                }
                
        except Exception as e:
            return {"success": False, "message": f"Error getting stats: {str(e)}"}
    
    def upload_file(self, file_path: str, filename: str) -> str:
        """Upload and process a file to the knowledge base"""
        try:
            # Process the file
            result = self._process_file(file_path, filename)
            
            if not result["success"]:
                return f"❌ {result['message']}"
            
            # Add to vectorstore
            add_result = self.add_to_vectorstore(result["chunks"], result["metadata"])
            
            if add_result["success"]:
                return f"✅ Successfully uploaded '{filename}' - {add_result['chunks_added']} chunks added"
            else:
                return f"❌ Failed to add to vectorstore: {add_result['message']}"
                
        except Exception as e:
            return f"❌ Error uploading file: {str(e)}"

# Global instance
kb_manager = KnowledgeBaseManager()

def upload_file_to_kb(file) -> str:
    """Upload file to knowledge base"""
    if file is None:
        return "❌ No file selected"
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.name).suffix) as tmp_file:
            tmp_file.write(file.read())
            tmp_path = tmp_file.name
        
        # Process the file
        result = kb_manager.upload_file(tmp_path, file.name)
        
        # Clean up
        os.unlink(tmp_path)
        
        return result
        
    except Exception as e:
        return f"❌ Error: {str(e)}"

def search_kb(query: str) -> str:
    """Search knowledge base"""
    if not query.strip():
        return "❌ Please enter a search query"
    
    result = kb_manager.search_knowledge_base(query)
    
    if not result["success"]:
        return f"❌ {result['message']}"
    
    if not result["results"]:
        return "🔍 No relevant information found"
    
    # Format results
    response = f"🔍 **Search Results for:** {query}\n\n"
    
    for i, item in enumerate(result["results"][:3], 1):
        content = item["content"][:300] + "..." if len(item["content"]) > 300 else item["content"]
        filename = item["metadata"].get("filename", "Unknown file")
        score = item["similarity_score"]
        
        response += f"**{i}. {filename}** (Score: {score:.2f})\n"
        response += f"{content}\n\n"
    
    return response

def get_kb_stats() -> str:
    """Get knowledge base statistics"""
    result = kb_manager.get_knowledge_base_stats()
    
    if not result["success"]:
        return f"❌ {result['message']}"
    
    stats = f"""📊 **Knowledge Base Statistics**

🗃️ **Total Chunks:** {result['total_chunks']}
📁 **Unique Files:** {result['unique_files']}
🗂️ **Collection:** {result['collection_name']}

📋 **File Types:**"""
    
    for file_type, count in result['file_types'].items():
        stats += f"\n• {file_type}: {count} chunks"
    
    return stats
