import os
import json
import logging
from io import BytesIO
from typing import Dict, List, Optional
import requests
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

logger = logging.getLogger("sec_agent")

OPENROUTER_API_KEY = os.environ.get("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", "")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "gpt-4o-mini")
OPENROUTER_URL = "https://api.openrouter.ai/v1/chat/completions"


class KnowledgeStore:
    def __init__(self):
        self.trade_store: List[Dict] = []
        self.tweet_store: Dict[str, List[Dict]] = {}
        self.sentiment_store: Dict[str, Dict] = {}
        self.last_chart_path = "/chart"

    def initialize(self):
        self.trade_store = self._fetch_mock_sec_insider_trades()
        self.trade_store.sort(key=lambda item: item["trade_value"], reverse=True)
        self.trade_store = self.trade_store[:5]
        self.tweet_store = self._fetch_mock_tweets_for_top_trades(self.trade_store)
        self.sentiment_store = self._evaluate_sentiments(self.tweet_store)

    def _fetch_mock_sec_insider_trades(self) -> List[Dict]:
        return [
            {"ticker": "AAPL", "insider": "John Doe", "transaction": "Sale", "trade_value": 4_250_000, "date": "2026-04-14"},
            {"ticker": "MSFT", "insider": "Jane Smith", "transaction": "Purchase", "trade_value": 3_700_000, "date": "2026-04-14"},
            {"ticker": "NVDA", "insider": "Alan Chen", "transaction": "Sale", "trade_value": 3_100_000, "date": "2026-04-14"},
            {"ticker": "TSLA", "insider": "Priya Patel", "transaction": "Purchase", "trade_value": 2_940_000, "date": "2026-04-14"},
            {"ticker": "AMZN", "insider": "Carlos Rivera", "transaction": "Sale", "trade_value": 2_500_000, "date": "2026-04-14"},
        ]

    def _fetch_mock_tweets_for_top_trades(self, trades: List[Dict]) -> Dict[str, List[Dict]]:
        base_tweets = {
            "AAPL": [
                {"text": "Apple continues to dominate smartphone sales and investor sentiment is bullish.", "created_at": "2026-04-14T08:00:00Z"},
                {"text": "AAPL earnings whisper shows cautious optimism ahead of the next quarter.", "created_at": "2026-04-13T20:15:00Z"},
                {"text": "Some investors worry about Apple supply chain issues, but fundamentals remain strong.", "created_at": "2026-04-12T14:30:00Z"},
            ],
            "MSFT": [
                {"text": "Microsoft AI pipeline keeps momentum and the market is reacting positively.", "created_at": "2026-04-14T09:30:00Z"},
                {"text": "Some analysts are skeptical on Azure growth, but Windows revenue is steady.", "created_at": "2026-04-13T18:10:00Z"},
                {"text": "MSFT is likely to see more enterprise deal flow after the latest partner event.", "created_at": "2026-04-12T12:00:00Z"},
            ],
            "NVDA": [
                {"text": "Nvidia continues to lead the GPU market with very strong demand.", "created_at": "2026-04-14T10:00:00Z"},
                {"text": "Some considerations about chip supply but long-term sentiment remains positive.", "created_at": "2026-04-13T16:45:00Z"},
                {"text": "NVIDIA stock is extended, yet traders still expect strong growth next quarter.", "created_at": "2026-04-12T11:20:00Z"},
            ],
            "TSLA": [
                {"text": "Tesla deliveries are beating expectations and the EV narrative is strong.", "created_at": "2026-04-14T07:45:00Z"},
                {"text": "Some tweets question Tesla valuation, but product demand remains solid.", "created_at": "2026-04-13T19:55:00Z"},
                {"text": "Elon Musk announces a new energy product and the market is watching closely.", "created_at": "2026-04-12T13:10:00Z"},
            ],
            "AMZN": [
                {"text": "Amazon Prime Day rumors keep retail investors hopeful.", "created_at": "2026-04-14T09:00:00Z"},
                {"text": "Warehouse productivity improvements may help keep margins stable.", "created_at": "2026-04-13T17:25:00Z"},
                {"text": "There is still concern about AWS growth slowdown in some analyst threads.", "created_at": "2026-04-12T10:05:00Z"},
            ],
        }
        output = {}
        for trade in trades:
            ticker = trade["ticker"]
            output[ticker] = base_tweets.get(ticker, [])
        return output

    def _evaluate_sentiments(self, tweet_store: Dict[str, List[Dict]]) -> Dict[str, Dict]:
        result = {}
        for ticker, tweets in tweet_store.items():
            positive = 0
            neutral = 0
            negative = 0
            total_score = 0.0
            for tweet in tweets:
                sentiment, score = self._analyze_text_sentiment(tweet["text"])
                total_score += score
                if sentiment == "positive":
                    positive += 1
                elif sentiment == "negative":
                    negative += 1
                else:
                    neutral += 1
            average_score = total_score / max(len(tweets), 1)
            result[ticker] = {
                "positive": positive,
                "neutral": neutral,
                "negative": negative,
                "average_score": round(average_score, 3),
                "tweet_count": len(tweets),
            }
        return result

    def _analyze_text_sentiment(self, text: str) -> (str, float):
        if OPENROUTER_API_KEY:
            try:
                payload = {
                    "model": OPENROUTER_MODEL,
                    "messages": [
                        {"role": "system", "content": "Classify the following tweet text into sentiment categories: Positive, Neutral, or Negative. Return only JSON with keys sentiment and score."},
                        {"role": "user", "content": json.dumps({"text": text})},
                    ],
                    "temperature": 0,
                }
                headers = {
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                }
                response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=15)
                response.raise_for_status()
                data = response.json()
                text_out = data["choices"][0]["message"]["content"].strip()
                if text_out.startswith("{"):
                    parsed = json.loads(text_out)
                    sentiment = parsed.get("sentiment", "neutral").lower()
                    score = float(parsed.get("score", 0.5))
                    return sentiment, max(0.0, min(score, 1.0))
            except Exception as exc:
                logger.warning("OpenRouter sentiment call failed, using fallback. %s", exc)
        return self._fallback_sentiment(text)

    def _fallback_sentiment(self, text: str) -> (str, float):
        normalized = text.lower()
        positive_keywords = ["bullish", "strong", "positive", "momentum", "beat", "hopeful", "leading", "dominates"]
        negative_keywords = ["concern", "worry", "skeptical", "slowdown", "issue", "extended", "question"]
        score = 0.5
        for word in positive_keywords:
            if word in normalized:
                score += 0.15
        for word in negative_keywords:
            if word in normalized:
                score -= 0.15
        sentiment = "neutral"
        if score >= 0.6:
            sentiment = "positive"
        elif score <= 0.4:
            sentiment = "negative"
        return sentiment, round(max(0.0, min(score, 1.0)), 3)

    def answer_question(self, question: str) -> Optional[str]:
        normalized = question.lower()
        matches = []
        for trade in self.trade_store:
            ticker = trade["ticker"].lower()
            if ticker in normalized or ticker.lower() in normalized:
                matches.append(trade)
        if not matches:
            return None

        answers = []
        for trade in matches:
            ticker = trade["ticker"]
            sentiment = self.sentiment_store.get(ticker, {})
            lines = [
                f"Most recent insider trade: {trade['transaction']} {trade['ticker']} by {trade['insider']} for ${trade['trade_value']:,} on {trade['date']}.",
                f"Sentiment from recent tweets for {ticker}: {sentiment.get('positive', 0)} positive, {sentiment.get('neutral', 0)} neutral, {sentiment.get('negative', 0)} negative, average score {sentiment.get('average_score', 0.0)}.",
            ]
            answers.append(" ".join(lines))
        return " \n\n".join(answers)

    def generate_sentiment_chart_bytes(self) -> BytesIO:
        if not self.sentiment_store:
            raise ValueError("Sentiment data is not available.")
        tickers = list(self.sentiment_store.keys())
        positive = [self.sentiment_store[t]["positive"] for t in tickers]
        neutral = [self.sentiment_store[t]["neutral"] for t in tickers]
        negative = [self.sentiment_store[t]["negative"] for t in tickers]
        fig, ax = plt.subplots(figsize=(8, 5))
        x = range(len(tickers))
        ax.bar([i - 0.25 for i in x], positive, width=0.25, label="Positive", color="#4CAF50")
        ax.bar(x, neutral, width=0.25, label="Neutral", color="#FFC107")
        ax.bar([i + 0.25 for i in x], negative, width=0.25, label="Negative", color="#F44336")
        ax.set_xticks(x)
        ax.set_xticklabels(tickers)
        ax.set_title("Tweet Sentiment for Top 5 Insider Trading Tickers")
        ax.set_ylabel("Tweet count")
        ax.legend()
        fig.tight_layout()
        buffer = BytesIO()
        fig.savefig(buffer, format="png")
        plt.close(fig)
        buffer.seek(0)
        return buffer
