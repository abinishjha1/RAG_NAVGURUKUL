"""
LLM Configuration Module
Handles initialization of different LLM providers based on environment variables
"""
import os
from dotenv import load_dotenv

load_dotenv()


def get_llm_provider():
    """Get the configured LLM provider from environment"""
    return os.getenv("LLM_PROVIDER", "openai").lower()


def get_embeddings():
    """Initialize embeddings based on configured provider"""
    provider = get_llm_provider()
    
    if provider == "gemini" or provider == "google":
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        return GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=api_key
        )
    
    elif provider == "ollama":
        from langchain_ollama import OllamaEmbeddings
        model = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
        return OllamaEmbeddings(model=model)
    
    elif provider == "groq":
        # Groq doesn't provide embeddings, use HuggingFace (free, local)
        from langchain_huggingface import HuggingFaceEmbeddings
        model = os.getenv("HF_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        return HuggingFaceEmbeddings(model_name=model)
    
    elif provider == "huggingface" or provider == "hf":
        from langchain_huggingface import HuggingFaceEmbeddings
        model = os.getenv("HF_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        return HuggingFaceEmbeddings(model_name=model)
    
    else:  # default to openai
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(model="text-embedding-3-small")


def get_llm(temperature=0.7):
    """Initialize LLM based on configured provider"""
    provider = get_llm_provider()
    
    if provider == "gemini" or provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        return ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=api_key,
            temperature=temperature
        )
    
    elif provider == "ollama":
        from langchain_ollama import ChatOllama
        model = os.getenv("OLLAMA_MODEL", "llama2")
        return ChatOllama(model=model, temperature=temperature)
    
    elif provider == "groq":
        from langchain_groq import ChatGroq
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        model = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")
        return ChatGroq(
            groq_api_key=api_key,
            model_name=model,
            temperature=temperature
        )
    
    elif provider == "huggingface" or provider == "hf":
        from langchain_huggingface import HuggingFaceEndpoint
        api_key = os.getenv("HUGGINGFACE_API_KEY")
        if not api_key:
            raise ValueError("HUGGINGFACE_API_KEY not found in environment variables")
        model = os.getenv("HF_MODEL", "mistralai/Mistral-7B-Instruct-v0.2")
        return HuggingFaceEndpoint(
            repo_id=model,
            huggingfacehub_api_token=api_key,
            temperature=temperature
        )
    
    else:  # default to openai
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model="gpt-4o", temperature=temperature)


def get_provider_info():
    """Get information about the current provider"""
    provider = get_llm_provider()
    
    info = {
        "openai": {
            "name": "OpenAI",
            "models": {"llm": "gpt-4o", "embeddings": "text-embedding-3-small"},
            "cost": "Paid",
            "requires": ["OPENAI_API_KEY"]
        },
        "gemini": {
            "name": "Google Gemini",
            "models": {"llm": "gemini-pro", "embeddings": "embedding-001"},
            "cost": "Free tier available",
            "requires": ["GOOGLE_API_KEY"]
        },
        "google": {
            "name": "Google Gemini",
            "models": {"llm": "gemini-pro", "embeddings": "embedding-001"},
            "cost": "Free tier available",
            "requires": ["GOOGLE_API_KEY"]
        },
        "ollama": {
            "name": "Ollama (Local)",
            "models": {
                "llm": os.getenv("OLLAMA_MODEL", "llama2"),
                "embeddings": os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
            },
            "cost": "100% Free (Local)",
            "requires": ["Ollama installed locally"]
        },
        "groq": {
            "name": "Groq",
            "models": {
                "llm": os.getenv("GROQ_MODEL", "mixtral-8x7b-32768"),
                "embeddings": "N/A (use with HuggingFace embeddings)"
            },
            "cost": "Free tier available",
            "requires": ["GROQ_API_KEY"]
        },
        "huggingface": {
            "name": "Hugging Face",
            "models": {
                "llm": os.getenv("HF_MODEL", "mistralai/Mistral-7B-Instruct-v0.2"),
                "embeddings": os.getenv("HF_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
            },
            "cost": "Free tier available",
            "requires": ["HUGGINGFACE_API_KEY"]
        }
    }
    
    return info.get(provider, info["openai"])

