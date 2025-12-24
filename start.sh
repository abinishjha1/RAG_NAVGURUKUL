#!/bin/bash

# PDF RAG System - Startup Script

echo "🚀 Starting PDF RAG System..."
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found!"
    echo "📝 Please create a .env file with your OpenAI API key:"
    echo ""
    echo "   OPENAI_API_KEY=your_openai_api_key_here"
    echo ""
    echo "You can copy .env.example to .env and edit it:"
    echo "   cp .env.example .env"
    echo ""
    exit 1
fi

# Check API Keys
source .env

if [ "$LLM_PROVIDER" = "gemini" ]; then
    if [ -z "$GOOGLE_API_KEY" ]; then
        echo "⚠️  GOOGLE_API_KEY is not set in .env file!"
        echo "📝 Please add your Google API key to the .env file"
        exit 1
    fi
elif [ "$LLM_PROVIDER" = "groq" ]; then
    if [ -z "$GROQ_API_KEY" ]; then
        echo "⚠️  GROQ_API_KEY is not set in .env file!"
        echo "📝 Please add your Groq API key to the .env file"
        exit 1
    fi
elif [ "$LLM_PROVIDER" = "ollama" ]; then
    echo "📦 Using Ollama (local) - no API key required"
elif [ "$LLM_PROVIDER" = "huggingface" ]; then
    if [ -z "$HUGGINGFACE_API_KEY" ]; then
        echo "⚠️  HUGGINGFACE_API_KEY is not set in .env file!"
        echo "📝 Please add your Hugging Face API key to the .env file"
        exit 1
    fi
else
    if [ -z "$OPENAI_API_KEY" ]; then
        echo "⚠️  OPENAI_API_KEY is not set in .env file! (Default provider)"
        echo "📝 Please add your OpenAI API key to the .env file"
        exit 1
    fi
fi

echo "✅ Environment configured"
echo "🌐 Starting server on http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the FastAPI server
python3 app.py

