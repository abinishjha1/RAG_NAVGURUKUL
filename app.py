"""
FastAPI Application for PDF RAG System
Provides endpoints for PDF upload, processing, and chat functionality
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import shutil
from typing import Optional
from pdf_processor import PDFProcessor
from chat_engine import ChatEngine

# Initialize FastAPI app
app = FastAPI(
    title="PDF RAG System",
    description="Upload PDFs and chat with your documents using AI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize processors
pdf_processor = PDFProcessor()
chat_engine = ChatEngine()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# Pydantic models for request/response
class ChatRequest(BaseModel):
    question: str
    k: Optional[int] = 5


class ChatResponse(BaseModel):
    success: bool
    answer: str
    sources: list
    num_sources: Optional[int] = 0


@app.get("/")
async def root():
    """Redirect to static index.html"""
    from fastapi.responses import FileResponse
    return FileResponse("static/index.html")


@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload and process a PDF file
    
    - Accepts PDF file upload
    - Extracts text from PDF
    - Chunks the text
    - Generates embeddings and stores in ChromaDB
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Save uploaded file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
    
    # Process PDF
    try:
        # Reinitialize processors to ensure clean state
        global pdf_processor, chat_engine
        pdf_processor = PDFProcessor()
        
        result = pdf_processor.process_pdf(file_path, file.filename)
        
        # Reinitialize chat engine to load new documents
        chat_engine = ChatEngine()
        
        if result["success"]:
            return JSONResponse(content={
                "success": True,
                "message": result["message"],
                "filename": result["filename"],
                "chunks_created": result["chunks_created"],
                "total_documents": result["total_documents"]
            })
        else:
            raise HTTPException(status_code=500, detail=result["message"])
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")
    
    finally:
        # Clean up uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Query the PDF content using natural language
    
    - Accepts a question
    - Retrieves relevant chunks from vector database
    - Generates AI-powered answer
    """
    try:
        result = chat_engine.chat(request.question, request.k)
        return ChatResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")


@app.get("/status")
async def get_status():
    """
    Get current status of the vector store
    
    Returns information about stored documents
    """
    try:
        status = pdf_processor.get_vectorstore_status()
        return JSONResponse(content=status)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")


@app.delete("/clear")
async def clear_vectorstore():
    """
    Clear all documents from the vector store
    
    WARNING: This will delete all uploaded PDFs and their embeddings
    """
    global pdf_processor, chat_engine
    
    try:
        result = pdf_processor.clear_vectorstore()
        
        # Reinitialize processors
        pdf_processor = PDFProcessor()
        chat_engine = ChatEngine()
        
        if result["success"]:
            return JSONResponse(content={
                "success": True,
                "message": result["message"]
            })
        else:
            raise HTTPException(status_code=500, detail=result["message"])
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing vector store: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "PDF RAG System is running"}


@app.get("/provider-info")
async def get_provider_info():
    """Get information about the current LLM provider"""
    try:
        from llm_config import get_provider_info
        info = get_provider_info()
        return JSONResponse(content=info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting provider info: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)


