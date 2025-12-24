# PDF RAG System 🤖📄

A simple web app to chat with your PDF documents using AI.

**🔗 GitHub:** https://github.com/abinishjha1/RAG_NAVGURUKUL

---

## ⚡ Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up API Key

Create a `.env` file:
```bash
cp .env.example .env
```

Choose one of these **FREE** options:

**Option A - Groq (Recommended):**
```
LLM_PROVIDER=groq
GROQ_API_KEY=your_key_from_console.groq.com
GROQ_MODEL=llama-3.3-70b-versatile
```

**Option B - Google Gemini:**
```
LLM_PROVIDER=gemini
GOOGLE_API_KEY=your_key_from_aistudio.google.com
```

**Option C - OpenAI (Paid):**
```
OPENAI_API_KEY=your_openai_api_key
```

### 3. Run the App
```bash
./start.sh
```

Or manually:
```bash
python app.py
```

### 4. Open Browser
Go to: **http://localhost:8000**

---

## 📖 How to Use

1. **Upload PDF** - Drag & drop or click to upload
2. **Wait** - The system processes and stores your PDF
3. **Ask Questions** - Type your question and get AI-powered answers

---

## 🏗️ Project Structure

```
├── app.py              # Main FastAPI server
├── pdf_processor.py    # PDF processing & vector storage
├── chat_engine.py      # AI chat logic
├── llm_config.py       # LLM provider configuration
├── start.sh            # Startup script
├── static/             # Frontend (HTML/CSS/JS)
├── db/                 # Vector database storage
└── uploads/            # Temporary PDF uploads
```

---

## 🛠️ API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/upload-pdf` | POST | Upload a PDF |
| `/chat` | POST | Ask a question |
| `/status` | GET | Check system status |
| `/clear` | DELETE | Clear all documents |

---

## 🔧 Supported LLM Providers

| Provider | Free Tier | API Key Source |
|----------|-----------|----------------|
| **Groq** | ✅ Yes | [console.groq.com](https://console.groq.com/keys) |
| **Gemini** | ✅ Yes | [aistudio.google.com](https://aistudio.google.com/app/apikey) |
| **Ollama** | ✅ Local | [ollama.com](https://ollama.com) |
| **OpenAI** | ❌ Paid | [platform.openai.com](https://platform.openai.com) |

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Module not found | `pip install -r requirements.txt` |
| API key error | Check your `.env` file |
| Port in use | Change port in `app.py` |
| PDF won't upload | Make sure PDF isn't encrypted |

---

## 📝 License

MIT License - Free to use and modify.

---


