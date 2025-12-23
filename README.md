# PDF RAG System 🤖📄

A modern web application that allows users to upload PDF documents, automatically processes them into chunks, generates embeddings, stores them in a vector database (ChromaDB), and provides an AI-powered chat interface to ask questions about the document content.

![PDF RAG System](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![LangChain](https://img.shields.io/badge/LangChain-Latest-orange.svg)

## ✨ Features

- 📤 **PDF Upload**: Drag-and-drop or click to upload PDF documents
- 🔪 **Automatic Chunking**: Intelligently splits documents using RecursiveCharacterTextSplitter
- 🧠 **Embeddings**: Generates embeddings using OpenAI's text-embedding-3-small model
- 💾 **Vector Storage**: Stores embeddings in ChromaDB for efficient retrieval
- 💬 **AI Chat Interface**: Ask questions about your PDFs and get accurate answers
- 🎨 **Modern UI**: Beautiful dark mode interface with glassmorphism and smooth animations
- 📱 **Responsive Design**: Works seamlessly on desktop and mobile devices
- 🔄 **Real-time Updates**: Live processing status and chat updates

## 🏗️ Architecture

```
┌─────────────┐
│   Frontend  │  (HTML/CSS/JavaScript)
│   (Browser) │
└──────┬──────┘
       │ HTTP/REST API
       ▼
┌─────────────┐
│   FastAPI   │  (Python Backend)
│   Server    │
└──────┬──────┘
       │
       ├──────────────┐
       │              │
       ▼              ▼
┌─────────────┐  ┌──────────────┐
│ PDF         │  │ Chat Engine  │
│ Processor   │  │              │
└──────┬──────┘  └──────┬───────┘
       │                │
       │                │
       ▼                ▼
┌──────────────────────────┐
│      ChromaDB            │
│   (Vector Database)      │
└──────────────────────────┘
       │
       ▼
┌──────────────────────────┐
│   OpenAI API             │
│   - Embeddings           │
│   - GPT-4 (Chat)         │
└──────────────────────────┘
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- OpenAI API key

### Installation

   Navigate to the project directory:
   ```bash
   cd RAG-NAVGURUKUL
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   
   Create a `.env` file in the project root:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

   **OR** to use Google Gemini (Free Tier):
   
   1. Get a free API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
   2. Update your `.env` file:
   ```
   LLM_PROVIDER=gemini
   GOOGLE_API_KEY=your_google_api_key_here
   ```

### Running the Application

1. **Start the FastAPI server**:
   ```bash
   python app.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Open your browser** and navigate to:
   ```
   http://localhost:8000
   ```

3. **Upload a PDF** and start chatting!

## 📖 Usage

### Uploading a PDF

1. Click on the upload area or drag and drop a PDF file
2. Wait for the processing to complete (you'll see a progress indicator)
3. Once processed, you'll see statistics about the chunks created

### Chatting with Your PDF

1. Type your question in the chat input box
2. Press Enter or click the send button
3. The AI will retrieve relevant chunks and generate an answer
4. Source references will be shown below the answer

### Clearing Documents

Click the "Clear All" button in the header to remove all uploaded documents and reset the system.

## 🛠️ API Endpoints

### `POST /upload-pdf`
Upload and process a PDF file.

**Request**: Multipart form data with PDF file
**Response**:
```json
{
  "success": true,
  "message": "Successfully processed document.pdf",
  "filename": "document.pdf",
  "chunks_created": 42,
  "total_documents": 42
}
```

### `POST /chat`
Query the PDF content.

**Request**:
```json
{
  "question": "What is the main topic of this document?",
  "k": 5
}
```

**Response**:
```json
{
  "success": true,
  "answer": "The main topic is...",
  "sources": [...],
  "num_sources": 5
}
```

### `GET /status`
Get vector store status.

**Response**:
```json
{
  "initialized": true,
  "total_documents": 42,
  "persist_directory": "db/chroma_db",
  "message": "Vector store contains 42 document chunks"
}
```

### `DELETE /clear`
Clear all documents from the vector store.

**Response**:
```json
{
  "success": true,
  "message": "Vector store cleared successfully"
}
```

## 📁 Project Structure

```
project-root/
├── app.py                  # FastAPI application
├── pdf_processor.py        # PDF processing and vector storage
├── chat_engine.py          # Chat and retrieval logic
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create this)
├── .env.example           # Environment template
├── static/                # Frontend files
│   ├── index.html         # Main HTML page
│   ├── styles.css         # Styling
│   └── script.js          # Client-side logic
├── db/                    # Database directory (auto-created)
│   └── chroma_db/         # ChromaDB storage
└── uploads/               # Temporary upload directory (auto-created)
```

## 🎨 Features in Detail

### PDF Processing
- Extracts text from all pages of the PDF
- Handles encrypted PDFs with appropriate error messages
- Validates PDF integrity before processing

### Chunking Strategy
- Uses RecursiveCharacterTextSplitter for intelligent text splitting
- Default chunk size: 1000 characters
- Default overlap: 200 characters
- Preserves context across chunks

### Vector Storage
- Uses ChromaDB for efficient vector storage
- Cosine similarity for semantic search
- Persistent storage across sessions
- Metadata tracking for source attribution

### Chat Engine
- Retrieves top-k relevant chunks (default k=5)
- Uses GPT-4 for answer generation
- Provides source citations
- Handles edge cases gracefully

## 🔧 Configuration

You can customize various parameters in the code:

- **Chunk size**: Modify `chunk_size` in `pdf_processor.py`
- **Chunk overlap**: Modify `chunk_overlap` in `pdf_processor.py`
- **Number of retrieved chunks**: Modify `k` parameter in chat requests
- **LLM model**: Change `model` in `chat_engine.py`
- **Embedding model**: Change `model` in embedding initialization

## 🐛 Troubleshooting

### "No module named 'xyz'"
Install missing dependencies:
```bash
pip install -r requirements.txt
```

### "OpenAI API key not found"
Make sure you've created a `.env` file with your API key:
```
OPENAI_API_KEY=your_key_here
```

### "Error extracting text from PDF"
- Ensure the PDF is not corrupted
- Check if the PDF is encrypted
- Try a different PDF file

### Port already in use
Change the port in `app.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
```

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Powered by [LangChain](https://www.langchain.com/)
- Vector storage by [ChromaDB](https://www.trychroma.com/)
- AI by [OpenAI](https://openai.com/)

---


