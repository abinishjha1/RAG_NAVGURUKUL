"""
PDF Processing Module
Handles PDF text extraction, chunking, and vector store operations
"""
import os
from typing import List, Dict, Any
try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader
from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from dotenv import load_dotenv
from llm_config import get_embeddings

load_dotenv()


class PDFProcessor:
    def __init__(self, persist_directory: str = "db/chroma_db"):
        """Initialize PDF processor with vector store configuration"""
        self.persist_directory = persist_directory
        self.embedding_model = get_embeddings()
        self.vectorstore = None  # Don't load existing store, create fresh when needed
    
    def _get_or_create_vectorstore(self):
        """Get existing vectorstore or create new one"""
        if self.vectorstore is None:
            if os.path.exists(self.persist_directory):
                try:
                    self.vectorstore = Chroma(
                        persist_directory=self.persist_directory,
                        embedding_function=self.embedding_model,
                        collection_metadata={"hnsw:space": "cosine"}
                    )
                except Exception as e:
                    # If loading fails, remove the directory and create fresh
                    import shutil
                    if os.path.exists(self.persist_directory):
                        shutil.rmtree(self.persist_directory)
                    self.vectorstore = None
        return self.vectorstore
    
    def extract_text_from_pdf(self, pdf_file_path: str) -> str:
        """
        Extract text content from a PDF file
        
        Args:
            pdf_file_path: Path to the PDF file
            
        Returns:
            Extracted text as a string
            
        Raises:
            Exception: If PDF cannot be read or is corrupted
        """
        try:
            text = ""
            with open(pdf_file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                
                # Check if PDF is encrypted
                if pdf_reader.is_encrypted:
                    raise Exception("PDF is encrypted and cannot be processed")
                
                # Extract text from all pages
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n--- Page {page_num + 1} ---\n{page_text}"
                
                if not text.strip():
                    raise Exception("No text could be extracted from the PDF")
                
                return text
        
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def chunk_text(self, text: str, pdf_filename: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Document]:
        """
        Split text into chunks with metadata
        
        Args:
            text: Text to be chunked
            pdf_filename: Name of the source PDF file
            chunk_size: Maximum size of each chunk
            chunk_overlap: Number of characters to overlap between chunks
            
        Returns:
            List of Document objects with chunked text and metadata
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Split text into chunks
        chunks = text_splitter.split_text(text)
        
        # Create Document objects with metadata
        documents = [
            Document(
                page_content=chunk,
                metadata={
                    "source": pdf_filename,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
            )
            for i, chunk in enumerate(chunks)
        ]
        
        return documents
    
    def store_chunks_in_vectordb(self, chunks: List[Document]) -> Dict[str, Any]:
        """
        Embed chunks and store in ChromaDB
        
        Args:
            chunks: List of Document objects to store
            
        Returns:
            Dictionary with storage status information
        """
        try:
            vectorstore = self._get_or_create_vectorstore()
            
            if vectorstore is None:
                # Create new vector store
                self.vectorstore = Chroma.from_documents(
                    documents=chunks,
                    embedding=self.embedding_model,
                    persist_directory=self.persist_directory,
                    collection_metadata={"hnsw:space": "cosine"}
                )
            else:
                # Add to existing vector store
                self.vectorstore.add_documents(chunks)
            
            # Get total count
            total_docs = self.vectorstore._collection.count()
            
            return {
                "success": True,
                "chunks_added": len(chunks),
                "total_documents": total_docs,
                "message": f"Successfully stored {len(chunks)} chunks in vector database"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Error storing chunks in vector database: {str(e)}"
            }
    
    def process_pdf(self, pdf_file_path: str, pdf_filename: str) -> Dict[str, Any]:
        """
        Complete pipeline: extract, chunk, and store PDF
        
        Args:
            pdf_file_path: Path to the PDF file
            pdf_filename: Name of the PDF file
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Step 1: Extract text
            text = self.extract_text_from_pdf(pdf_file_path)
            
            # Step 2: Chunk text
            chunks = self.chunk_text(text, pdf_filename)
            
            # Step 3: Store in vector database
            result = self.store_chunks_in_vectordb(chunks)
            
            if result["success"]:
                return {
                    "success": True,
                    "filename": pdf_filename,
                    "text_length": len(text),
                    "chunks_created": len(chunks),
                    "chunks_stored": result["chunks_added"],
                    "total_documents": result["total_documents"],
                    "message": f"Successfully processed {pdf_filename}"
                }
            else:
                return result
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Error processing PDF: {str(e)}"
            }
    
    def get_vectorstore_status(self) -> Dict[str, Any]:
        """Get current status of the vector store"""
        try:
            vectorstore = self._get_or_create_vectorstore()
            if vectorstore is None:
                return {
                    "initialized": False,
                    "total_documents": 0,
                    "message": "Vector store not initialized"
                }
            
            total_docs = vectorstore._collection.count()
            return {
                "initialized": True,
                "total_documents": total_docs,
                "persist_directory": self.persist_directory,
                "message": f"Vector store contains {total_docs} document chunks"
            }
        except Exception as e:
            return {
                "initialized": False,
                "error": str(e),
                "message": f"Error getting vector store status: {str(e)}"
            }
    
    def clear_vectorstore(self) -> Dict[str, Any]:
        """Clear all documents from the vector store"""
        try:
            # Close and delete the vectorstore properly
            if self.vectorstore is not None:
                try:
                    # Try to delete the collection first
                    self.vectorstore.delete_collection()
                except:
                    pass  # Ignore errors if collection doesn't exist
                
                # Clear the reference
                self.vectorstore = None
            
            # Force garbage collection to release file handles
            import gc
            gc.collect()
            
            # Wait a moment for file handles to be released
            import time
            time.sleep(0.5)
            
            # Remove persist directory completely
            if os.path.exists(self.persist_directory):
                import shutil
                try:
                    # Try multiple times with increasing delays
                    for attempt in range(3):
                        try:
                            shutil.rmtree(self.persist_directory)
                            break
                        except Exception as e:
                            if attempt < 2:
                                time.sleep(0.5)
                                gc.collect()
                            else:
                                # Last resort: remove files individually
                                import glob
                                for file_path in glob.glob(os.path.join(self.persist_directory, "**/*"), recursive=True):
                                    try:
                                        if os.path.isfile(file_path):
                                            os.chmod(file_path, 0o777)
                                            os.remove(file_path)
                                    except:
                                        pass
                                # Try to remove directory one last time
                                try:
                                    shutil.rmtree(self.persist_directory)
                                except:
                                    pass
                except:
                    pass
            
            # Reset ChromaDB client cache (important!)
            try:
                import chromadb
                # Clear any cached clients
                if hasattr(chromadb, '_client_cache'):
                    chromadb._client_cache.clear()
            except:
                pass
            
            return {
                "success": True,
                "message": "Vector store cleared successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Error clearing vector store: {str(e)}"
            }
