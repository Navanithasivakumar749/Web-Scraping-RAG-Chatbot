# 🌐 Web Content Chatbot

A smart chatbot that can answer questions about the content of any website. Simply provide a URL, and the bot will analyze the page content to answer your questions.

## ✨ Features

- **Web Content Extraction**: Fetches and processes content from any public URL
- **AI-Powered Q&A**: Uses Ollama's language model to answer questions about the scraped content
- **Conversation History**: Saves your chat history for future reference
- **Responsive UI**: Clean, modern interface that works on both desktop and mobile
- **Persistent Storage**: Uses MongoDB to store scraped content and chat history
- **Vector Search**: Utilizes ChromaDB for efficient content retrieval

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- MongoDB (local or cloud instance)
- Node.js (for frontend development, optional)
- Ollama server running locally (default: http://localhost:11434)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd URL_based_chatbot
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # On Windows
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the project root with the following variables:
   ```
   MONGO_URL=mongodb://localhost:27017/
   OLLAMA_MODEL=qwen3:0.6b  # or your preferred model
   ```

### Running the Application

1. Start the FastAPI backend:
   ```bash
   uvicorn app:app --reload
   ```

2. Open `index.html` in your web browser or serve it using a local web server:
   ```bash
   python -m http.server 8000
   ```
   Then visit `http://localhost:8000` in your browser.

## 🛠️ Usage

1. Enter a URL in the input field and click "Scrape & Start Chat"
2. Once the content is loaded, ask questions about the webpage
3. The bot will provide answers based on the scraped content
4. Use the history button to view or delete previous conversations

## 🧠 How It Works

1. **Web Scraping**: The backend fetches the HTML content of the provided URL and extracts clean text using BeautifulSoup.
2. **Content Storage**: The extracted content is stored in both MongoDB and ChromaDB for vector search.
3. **Question Answering**: When you ask a question, the system:
   - Uses vector similarity to find the most relevant content
   - Sends the context and question to the Ollama model
   - Returns the generated answer

## 📂 Project Structure

```
URL_based_chatbot/
├── app.py              # FastAPI backend
├── index.html          # Frontend interface
├── requirements.txt    # Python dependencies
└── .env               # Environment variables
```

## 🤖 Models

By default, the application uses the `qwen3:0.6b` model from Ollama. You can change this by:
1. Pulling a different model: `ollama pull <model-name>`
2. Updating the `OLLAMA_MODEL` in your `.env` file

