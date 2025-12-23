"""
Chat Engine Module
Handles querying the vector database and generating AI responses
"""
from typing import List, Dict, Any
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
from llm_config import get_embeddings, get_llm
import os

load_dotenv()


class ChatEngine:
    def __init__(self, persist_directory: str = "db/chroma_db"):
        """Initialize chat engine with vector store and LLM"""
        self.persist_directory = persist_directory
        self.embedding_model = get_embeddings()
        self.llm = get_llm(temperature=0.7)
        
        # Load vector store if it exists
        if os.path.exists(persist_directory):
            self.vectorstore = Chroma(
                persist_directory=persist_directory,
                embedding_function=self.embedding_model,
                collection_metadata={"hnsw:space": "cosine"}
            )
        else:
            self.vectorstore = None
    
    def query_vectordb(self, question: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks from vector database
        
        Args:
            question: User's question
            k: Number of relevant chunks to retrieve
            
        Returns:
            List of relevant document chunks with metadata
        """
        if self.vectorstore is None:
            return []
        
        try:
            # Create retriever
            retriever = self.vectorstore.as_retriever(
                search_kwargs={"k": k}
            )
            
            # Retrieve relevant documents
            relevant_docs = retriever.invoke(question)
            
            # Format results
            results = [
                {
                    "content": doc.page_content,
                    "source": doc.metadata.get("source", "Unknown"),
                    "chunk_index": doc.metadata.get("chunk_index", 0)
                }
                for doc in relevant_docs
            ]
            
            return results
        
        except Exception as e:
            print(f"Error querying vector database: {str(e)}")
            return []
    
    def generate_answer(self, question: str, context_docs: List[Dict[str, Any]]) -> str:
        """
        Generate answer using LLM based on retrieved context
        
        Args:
            question: User's question
            context_docs: List of relevant document chunks
            
        Returns:
            Generated answer as a string
        """
        if not context_docs:
            return "I don't have any information to answer that question. Please upload a PDF document first."
        
        # Format context from retrieved documents
        context = "\n\n".join([
            f"[Source: {doc['source']}, Chunk {doc['chunk_index']}]\n{doc['content']}"
            for doc in context_docs
        ])
        
        # Create prompt
        prompt = f"""Based on the following documents, please answer this question: {question}

Documents:
{context}

Please provide a clear, helpful answer using only the information from these documents. If you can't find the answer in the documents, say "I don't have enough information to answer that question based on the provided documents."

Include specific references to the source documents when relevant."""
        
        # Generate response
        try:
            messages = [
                SystemMessage(content="You are a helpful AI assistant that answers questions based on provided PDF documents. Always cite your sources and be accurate."),
                HumanMessage(content=prompt)
            ]
            
            result = self.llm.invoke(messages)
            return result.content
        
        except Exception as e:
            return f"Error generating answer: {str(e)}"
    
    def chat(self, question: str, k: int = 5) -> Dict[str, Any]:
        """
        Complete chat pipeline: retrieve context and generate answer
        
        Args:
            question: User's question
            k: Number of relevant chunks to retrieve
            
        Returns:
            Dictionary with answer and source information
        """
        if self.vectorstore is None:
            return {
                "success": False,
                "answer": "No documents have been uploaded yet. Please upload a PDF document first.",
                "sources": []
            }
        
        try:
            # Step 1: Retrieve relevant context
            context_docs = self.query_vectordb(question, k)
            
            if not context_docs:
                return {
                    "success": False,
                    "answer": "I couldn't find any relevant information to answer your question.",
                    "sources": []
                }
            
            # Step 2: Generate answer
            answer = self.generate_answer(question, context_docs)
            
            # Step 3: Format sources
            sources = [
                {
                    "source": doc["source"],
                    "chunk_index": doc["chunk_index"],
                    "preview": doc["content"][:200] + "..." if len(doc["content"]) > 200 else doc["content"]
                }
                for doc in context_docs
            ]
            
            return {
                "success": True,
                "answer": answer,
                "sources": sources,
                "num_sources": len(sources)
            }
        
        except Exception as e:
            return {
                "success": False,
                "answer": f"Error processing your question: {str(e)}",
                "sources": []
            }
