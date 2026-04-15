import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from app.services import KnowledgeStore
from app.models import ChatRequest, ChatResponse

logger = logging.getLogger("sec_agent")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

app = FastAPI(
    title="SEC Insider Trading Sentiment Chatbot",
    description="Minimal FastAPI chatbot using mock SEC insider trading data and sentiment for tickers.",
    version="0.1.0",
)

store = KnowledgeStore()

@app.on_event("startup")
async def startup_event():
    try:
        store.initialize()
        logger.info("Initialized knowledge store with %d tickers", len(store.trade_store))
    except Exception as exc:
        logger.exception("Startup failed: %s", exc)
        raise

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})

@app.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    try:
        logger.info("Chat request received: %s", payload.question)
        answer = store.answer_question(payload.question)
        if not answer:
            logger.info("No matching ticker found for question: %s", payload.question)
            raise HTTPException(status_code=404, detail="No matching insider trading data found for that question.")
        return ChatResponse(
            answer=answer,
            source="mock SEC insider trading data and tweet sentiment",
            chart_url="/chart",
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Error processing chat request: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to process chat request.")

@app.get("/chart")
async def chart():
    try:
        logger.info("Chart request received")
        chart_bytes = store.generate_sentiment_chart_bytes()
        return StreamingResponse(chart_bytes, media_type="image/png")
    except Exception as exc:
        logger.exception("Error generating chart: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to generate chart.")

@app.get("/health")
async def health():
    return {"status": "ok", "tickers_loaded": len(store.trade_store)}
