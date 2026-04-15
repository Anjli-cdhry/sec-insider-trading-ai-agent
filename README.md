# SEC Insider Trading Sentiment AI Agent

## Project Overview
This project is a FastAPI-based backend system that analyzes sentiment around SEC insider trading activity.

It simulates:
- Insider trading data (top trades by value)
- Tweet sentiment for related tickers
- AI-powered responses via a chat interface

---

## Features
- Chat endpoint to query sentiment (`/chat`)
- Sentiment visualization chart (`/chart`)
- Health check endpoint (`/health`)
- OpenRouter LLM integration (optional)
- Modular and scalable architecture

---

## Tech Stack
- Python
- FastAPI
- OpenRouter (LLM)
- Matplotlib
- Apify (planned integration)

---

## Project Structure
app/
├── main.py # FastAPI app & routes
├── models.py # Request/Response models
├── services.py # Data + sentiment logic


---

## How to Run

### 1. Create virtual environment
python -m venv .venv
.venv\Scripts\activate


### 2. Install dependencies
pip install -r requirements.txt


### 3. Add environment variable

Create `.env` file:
OPENROUTER_API_KEY=your_key_here


### 4. Run the app
uvicorn app.main:app --reload

### 5. Open API docs
http://127.0.0.1:8000/docs


---

## API Endpoints

### POST /chat
Ask questions about sentiment

**Example Request**
```json
{
  "question": "What is sentiment for TSLA?"
}

GET /chart

Returns sentiment chart for top tickers

GET /health

Check system status

{
  "answer": "Most recent insider trade: Purchase TSLA...",
  "source": "mock SEC insider trading data and tweet sentiment",
  "chart_url": "/chart"
}

Notes
Mock data is used due to time constraints
Designed for easy integration with:
SEC APIs
Apify Twitter scraping
Scalable for real-world deployment

Future Improvements
Integrate real SEC EDGAR data
Use Apify for live tweet scraping
Add vector database for RAG
Implement Hermes multi-agent workflow