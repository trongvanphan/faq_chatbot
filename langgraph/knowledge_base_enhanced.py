"""
Enhanced Knowledge Base Management
Handles document upload, parsing, chunking, and vector storage with ChromaDB.
"""

import streamlit as st
import os
from dotenv import load_dotenv
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain_community.vectorstores import Chroma
import docx2txt
from PyPDF2 import PdfReader
from markitdown import MarkItDown
from typing import List, Dict, Any
import tempfile
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class KnowledgeBaseManager:
    """
    Enhanced knowledge base manager with document parsing and vector storage capabilities.
    """
    
    def __init__(self):
        self.vectordb = self._initialize_vectordb()
        self.markitdown = MarkItDown()
    
    def _initialize_vectordb(self) -> Chroma:
        """Initialize ChromaDB with Azure OpenAI embeddings."""
        try:
            embeddings = AzureOpenAIEmbeddings(
                azure_endpoint=os.getenv("AZURE_OPENAI_EMBEDDING_ENDPOINT"),
                api_key=os.getenv("AZURE_OPENAI_EMBEDDING_API_KEY"),
                model=os.getenv("AZURE_OPENAI_EMBEDDING_MODEL"),
                api_version="2024-07-01-preview"
            )
            vectordb = Chroma(
                persist_directory=os.getenv("CHROMA_DB_PATH", ".chromadb"), 
                embedding_function=embeddings
            )
            logger.info("Vector database initialized successfully")
            return vectordb
        except Exception as e:
            logger.error(f"Error initializing vector database: {e}")
            raise
    
    def parse_pdf(self, file) -> str:
        """Convert PDF file data to Markdown using MarkItDown with fallback."""
        try:
            # Primary: Use MarkItDown
            result = self.markitdown.convert_stream(file, file_extension=".pdf")
            logger.info(f"Successfully parsed PDF with MarkItDown: {len(result.text_content)} characters")
            return result.text_content
        except Exception as e:
            logger.warning(f"MarkItDown PDF parsing failed: {e}, falling back to PyPDF2")
            try:
                # Fallback: Use PyPDF2
                file.seek(0)
                reader = PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
                logger.info(f"Successfully parsed PDF with PyPDF2: {len(text)} characters")
                return text
            except Exception as e2:
                logger.error(f"Both PDF parsing methods failed: {e2}")
                return f"Error parsing PDF: {str(e2)}"
    
    def parse_txt(self, file) -> str:
        """Convert TXT file data to Markdown using MarkItDown with fallback."""
        try:
            # Primary: Use MarkItDown
            result = self.markitdown.convert_stream(file, file_extension=".txt")
            logger.info(f"Successfully parsed TXT with MarkItDown: {len(result.text_content)} characters")
            return result.text_content
        except Exception as e:
            logger.warning(f"MarkItDown TXT parsing failed: {e}, falling back to direct read")
            try:
                # Fallback: Direct read
                file.seek(0)
                text = file.read().decode("utf-8")
                logger.info(f"Successfully parsed TXT with direct read: {len(text)} characters")
                return text
            except Exception as e2:
                logger.error(f"Both TXT parsing methods failed: {e2}")
                return f"Error parsing TXT: {str(e2)}"
    
    def parse_docx(self, file) -> str:
        """Convert DOCX file data to Markdown using MarkItDown with fallback."""
        try:
            # Primary: Use MarkItDown
            result = self.markitdown.convert_stream(file, file_extension=".docx")
            logger.info(f"Successfully parsed DOCX with MarkItDown: {len(result.text_content)} characters")
            return result.text_content
        except Exception as e:
            logger.warning(f"MarkItDown DOCX parsing failed: {e}, falling back to docx2txt")
            try:
                # Fallback: Use docx2txt with temporary file
                file.seek(0)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_file:
                    temp_file.write(file.read())
                    temp_path = temp_file.name
                
                text = docx2txt.process(temp_path)
                os.unlink(temp_path)  # Clean up temp file
                logger.info(f"Successfully parsed DOCX with docx2txt: {len(text)} characters")
                return text
            except Exception as e2:
                logger.error(f"Both DOCX parsing methods failed: {e2}")
                return f"Error parsing DOCX: {str(e2)}"
    
    def parse_file(self, file) -> str:
        """Parse uploaded file based on its type."""
        if file.type == "application/pdf":
            return self.parse_pdf(file)
        elif file.type == "text/plain":
            return self.parse_txt(file)
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return self.parse_docx(file)
        else:
            logger.warning(f"Unsupported file type: {file.type} for file: {file.name}")
            return f"Unsupported file type: {file.type}"
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks."""
        if not text.strip():
            return []
        
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        
        logger.info(f"Text chunked into {len(chunks)} chunks")
        return chunks
    
    def add_documents(self, files, chunk_size: int = 500, overlap: int = 50) -> Dict[str, Any]:
        """
        Process uploaded files and add them to the vector database.
        
        Returns:
            Dict containing processing results and statistics
        """
        results = {
            "processed_files": [],
            "failed_files": [],
            "total_chunks": 0,
            "success": False,
            "error_message": None
        }
        
        try:
            all_chunks = []
            chunk_metadatas = []
            
            for file in files:
                try:
                    # Parse file content
                    text = self.parse_file(file)
                    
                    if text.startswith("Error parsing"):
                        results["failed_files"].append({
                            "name": file.name,
                            "error": text
                        })
                        continue
                    
                    # Chunk the text
                    chunks = self.chunk_text(text, chunk_size, overlap)
                    
                    if not chunks:
                        results["failed_files"].append({
                            "name": file.name,
                            "error": "No content extracted from file"
                        })
                        continue
                    
                    # Add chunks and metadata
                    all_chunks.extend(chunks)
                    chunk_metadatas.extend([{
                        "source": file.name,
                        "file_type": file.type,
                        "chunk_size": chunk_size,
                        "overlap": overlap
                    }] * len(chunks))
                    
                    results["processed_files"].append({
                        "name": file.name,
                        "chunks": len(chunks),
                        "characters": len(text)
                    })
                    
                except Exception as e:
                    logger.error(f"Error processing file {file.name}: {e}")
                    results["failed_files"].append({
                        "name": file.name,
                        "error": str(e)
                    })
            
            # Add to vector database if we have chunks
            if all_chunks:
                self.vectordb.add_texts(all_chunks, metadatas=chunk_metadatas)
                self.vectordb.persist()
                results["total_chunks"] = len(all_chunks)
                results["success"] = True
                logger.info(f"Successfully added {len(all_chunks)} chunks to vector database")
            else:
                results["error_message"] = "No valid content found in any files"
                
        except Exception as e:
            logger.error(f"Error adding documents to vector database: {e}")
            results["error_message"] = str(e)
        
        return results
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector database."""
        try:
            total_chunks = self.vectordb._collection.count()
            
            # Try to get unique sources
            try:
                # This might not work with all Chroma versions
                all_metadatas = self.vectordb._collection.get(include=["metadatas"])
                sources = set()
                if all_metadatas and 'metadatas' in all_metadatas:
                    for metadata in all_metadatas['metadatas']:
                        if metadata and 'source' in metadata:
                            sources.add(metadata['source'])
                unique_sources = len(sources)
            except:
                unique_sources = "Unknown"
            
            return {
                "total_chunks": total_chunks,
                "unique_sources": unique_sources,
                "database_path": self.vectordb._persist_directory
            }
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {
                "total_chunks": 0,
                "unique_sources": 0,
                "error": str(e)
            }
    
    def search_similar(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """Search for similar documents in the vector database."""
        try:
            results = self.vectordb.similarity_search_with_score(query, k=k)
            formatted_results = []
            
            for doc, score in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity_score": score
                })
            
            return formatted_results
        except Exception as e:
            logger.error(f"Error searching vector database: {e}")
            return []
    
    def get_vectordb(self):
        """Get the vector database instance."""
        return self.vectordb
    
    def clear_database(self) -> bool:
        """Clear all documents from the vector database."""
        try:
            # This is a simple approach - in production you might want more granular control
            self.vectordb._collection.delete()
            logger.info("Vector database cleared successfully")
            return True
        except Exception as e:
            logger.error(f"Error clearing database: {e}")
            return False

# Global instance
knowledge_base = KnowledgeBaseManager()

def get_vectordb():
    """Get the vector database instance (for backward compatibility)."""
    return knowledge_base.get_vectordb()

def knowledge_base_tab():
    """Streamlit UI for knowledge base management."""
    st.header("📚 Knowledge Base Management")
    
    # File upload section
    st.subheader("Upload Documents")
    uploaded_files = st.file_uploader(
        "Upload documents (PDF, TXT, DOCX)",
        type=["pdf", "txt", "docx"],
        accept_multiple_files=True,
        help="Upload multiple documents to build your knowledge base"
    )
    
    # Chunking configuration
    col1, col2 = st.columns(2)
    with col1:
        chunk_size = st.slider("Chunk Size (words)", 200, 1000, 500, step=50)
    with col2:
        overlap = st.slider("Overlap (words)", 0, 200, 50, step=10)
    
    if uploaded_files:
        st.write(f"📁 **{len(uploaded_files)} file(s) selected:**")
        for file in uploaded_files:
            file_size_mb = len(file.getvalue()) / (1024 * 1024)
            st.write(f"- {file.name} ({file_size_mb:.2f} MB, {file.type})")
        
        if st.button("🔄 Process and Embed Documents", type="primary"):
            with st.spinner("Processing documents..."):
                results = knowledge_base.add_documents(uploaded_files, chunk_size, overlap)
            
            if results["success"]:
                st.success(f"✅ Successfully processed {len(results['processed_files'])} files!")
                st.write(f"📊 **Total chunks added:** {results['total_chunks']}")
                
                if results["processed_files"]:
                    st.subheader("✅ Successfully Processed")
                    for file_info in results["processed_files"]:
                        st.write(f"- {file_info['name']}: {file_info['chunks']} chunks ({file_info['characters']} characters)")
                
                # Update session state for file tracking
                if 'file_list' not in st.session_state:
                    st.session_state['file_list'] = []
                st.session_state['file_list'].extend([f["name"] for f in results["processed_files"]])
                
            if results["failed_files"]:
                st.subheader("❌ Failed to Process")
                for file_info in results["failed_files"]:
                    st.error(f"- {file_info['name']}: {file_info['error']}")
            
            if not results["success"] and results["error_message"]:
                st.error(f"❌ Processing failed: {results['error_message']}")
    
    # Database statistics
    st.subheader("📊 Database Statistics")
    stats = knowledge_base.get_database_stats()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Chunks", stats.get("total_chunks", 0))
    with col2:
        st.metric("Unique Sources", stats.get("unique_sources", 0))
    with col3:
        if st.button("🔄 Refresh Stats"):
            st.rerun()
    
    # File list
    st.subheader("📋 Embedded Files")
    if st.session_state.get('file_list'):
        for fname in sorted(set(st.session_state['file_list'])):
            st.write(f"📄 {fname}")
    else:
        st.info("No files embedded yet.")
    
    # Search functionality
    st.subheader("🔍 Search Knowledge Base")
    search_query = st.text_input("Enter search query:")
    search_k = st.slider("Number of results", 1, 10, 4)
    
    if search_query and st.button("🔍 Search"):
        with st.spinner("Searching..."):
            results = knowledge_base.search_similar(search_query, k=search_k)
        
        if results:
            st.write(f"Found {len(results)} similar documents:")
            for i, result in enumerate(results, 1):
                with st.expander(f"Result {i} - {result['metadata'].get('source', 'Unknown')} (Score: {result['similarity_score']:.3f})"):
                    st.write(result['content'][:500] + "..." if len(result['content']) > 500 else result['content'])
                    st.json(result['metadata'])
        else:
            st.info("No similar documents found.")
    
    # Database management
    st.subheader("🗄️ Database Management")
    if st.button("🗑️ Clear Database", type="secondary"):
        if st.confirm("Are you sure you want to clear all documents from the database?"):
            if knowledge_base.clear_database():
                st.success("Database cleared successfully!")
                st.session_state['file_list'] = []
                st.rerun()
            else:
                st.error("Failed to clear database.")
    
    # Display database path
    st.info(f"📁 Database location: {stats.get('database_path', 'Unknown')}")

if __name__ == "__main__":
    # For testing
    st.set_page_config(page_title="Knowledge Base Manager", layout="wide")
    knowledge_base_tab()
