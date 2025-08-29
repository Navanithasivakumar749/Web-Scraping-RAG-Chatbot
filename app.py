import os
import requests
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import json
import chromadb
from chromadb.utils import embedding_functions
from pymongo import MongoClient
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
import urllib.request

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB setup
mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
mongo_client = MongoClient(mongo_url)
db = mongo_client["web_scraper_bot"]
scrapes_collection = db["scrapes"]
queries_collection = db["queries"]

# ChromaDB
last_scraped_content = ""
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(
    name="scraped_data",
    embedding_function=embedding_functions.DefaultEmbeddingFunction()
)

def clean_html(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")
    for script in soup(["script", "style"]):
        script.decompose()
    return soup.get_text(separator=" ", strip=True)

@app.post("/scrape")
async def scrape(request: Request):
    global last_scraped_content
    try:
        data = await request.json()
        url = data.get("url")

        if not url:
            return {"error": "Missing URL"}

        logger.debug(f"Fetching content from URL: {url}")

        # Fetch and parse HTML
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        content = clean_html(response.text)

        if content:
            last_scraped_content = content
            collection.add(documents=[content], ids=[url])
            scrapes_collection.insert_one({
                "url": url,
                "content": content,
                "timestamp": datetime.utcnow()
            })
            return {"success": True, "data": content[:500]}  # return snippet
        else:
            return {"error": "Content could not be extracted"}

    except Exception as e:
        logger.error(f"Scrape error: {e}", exc_info=True)
        return {"error": "Failed to fetch data", "details": str(e)}

@app.post("/query")
async def query_bot(request: Request):
    global last_scraped_content
    try:
        data = await request.json()
        query = data.get("query", "").strip()

        if not query:
            return {"error": "Missing query"}

        if not last_scraped_content and collection.count() == 0:
            return {"response": "No content available. Please scrape a URL first."}

        # Try fetching similar text using ChromaDB
        relevant_content = last_scraped_content
        if collection.count() > 0:
            results = collection.query(query_texts=[query], n_results=1)
            if results.get('documents') and results['documents'][0]:
                relevant_content = results['documents'][0][0]

        # Truncate if too long
        if len(relevant_content) > 3000:
            relevant_content = relevant_content[:3000]

        prompt = (
            "Answer the following question based only on the context provided. "
            "Be clear and concise.\n\n"
            f"Context:\n{relevant_content}\n\n"
            f"Question:\n{query}\n\nAnswer:"
        )

        logger.debug(f"Sending prompt to Ollama:\n{prompt}")

        model_name = os.getenv("OLLAMA_MODEL", "qwen3:0.6b")

        ollama_response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": False
            },
            timeout=300
        )

        try:
            parsed = ollama_response.json()
            answer = parsed.get("response", "").strip()
        except json.JSONDecodeError:
            return {"error": "Invalid response from Ollama", "details": ollama_response.text}

        queries_collection.insert_one({
            "query": query,
            "response": answer,
            "timestamp": datetime.utcnow()
        })

        return {"response": answer or "No answer generated."}

    except Exception as e:
        logger.error(f"Ollama query error: {e}", exc_info=True)
        return {"error": "Failed to process query", "details": str(e)}
   