# SEC Insider Trading Sentiment AI Agent
An AI-powered backend system that analyzes insider trading activity and market sentiment using FastAPI and LLM integration.

---

## Key Highlights
- Built scalable FastAPI backend
- Integrated sentiment analysis pipeline
- Designed modular architecture for extensibility
- Supports LLM-based intelligent responses

---

## Project Overview
This project is a FastAPI-based backend system that analyzes sentiment around SEC insider trading activity.

The system simulates:
- Insider trading data (top trades by value)
- Social media sentiment for related stock tickers
- AI-powered responses via a chat interface

---

## Features
- Chat endpoint to query sentiment (`/chat`)
- Sentiment visualization chart (`/chart`)
- Health check endpoint (`/health`)
- Optional OpenRouter LLM integration
- Modular and scalable backend architecture

---

## Tech Stack
- Python
- FastAPI
- OpenRouter (LLM - optional)
- Matplotlib
- Apify (planned integration)

---

## Architecture
- FastAPI handles API routing and request management
- services.py:
  - Processes insider trading data
  - Performs sentiment analysis on social data
- models.py:
  - Defines request and response schemas using Pydantic
- Chart endpoint:
  - Generates sentiment visualization using Matplotlib
- LLM Integration (optional):
  - Enhances responses using OpenRouter API

---


## Project Structure
```
app/
├── main.py # FastAPI app & routes
├── models.py # Request/Response models
├── services.py # Data + sentiment logic
```

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
## Use Case
This system can help:
- Investors can analyze insider trading trends
- Detect bullish or bearish sentiment signals
- Combine trading data with social sentiment insights
- Build intelligent financial analysis tools

---

## Limitations
- Uses mock data instead of real SEC filings
- Social sentiment is simulated
- Not suitable for real financial decisions without real data integration

---

## API Endpoints
### POST /chat

Ask questions about sentiment

Example:
{
  "question": "What is sentiment for TSLA?"
}

---

### GET /chart
Returns sentiment chart for top tickers

---

### GET /health
Check system status

---

### Sample Output
```json
{
  "answer": "Most recent insider trade: Purchase TSLA...",
  "source": "mock SEC insider trading data and social sentiment",
  "chart_url": "/chart"
}
```

---

## Notes

- This project uses mock data due to time constraints  
- Designed for easy integration with external data sources:
  - SEC APIs  
  - Apify Twitter scraping  
- Scalable for real-world deployment  

---

## Future Improvements

- Integrate real SEC EDGAR data  
- Use Apify for live tweet scraping  
- Add vector database for RAG  
- Implement multi-agent workflow  
