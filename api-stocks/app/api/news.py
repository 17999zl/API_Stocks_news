from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.schemas.news import (
    FetchNewsRequest,
    FetchNewsResponse,
)

from app.storage.memory import news_history
from app.services.news_service import NewsService
from app.services.sentiment_service import SentimentService


router = APIRouter(
    prefix="/news",
    tags=["News"]
)

news_service = NewsService()
sentiment_service = SentimentService()

# ERROR SCHEMA 
class ErrorResponse(BaseModel):
    error: str
    message: str


# SUMMARY BUILDER
def build_summary(articles):
    if not articles:
        return {
            "positive": 0,
            "negative": 0,
            "neutral": 0,
            "overall_sentiment": "neutral",
            "confidence_score": 0.0
        }

    positive = sum(1 for a in articles if a["sentiment"] == "positive")
    negative = sum(1 for a in articles if a["sentiment"] == "negative")
    neutral = sum(1 for a in articles if a["sentiment"] == "neutral")

    counts = {
        "positive": positive,
        "negative": negative,
        "neutral": neutral,
    }

    overall = max(counts, key=counts.get)

    confidence = round(
        sum(a["confidence"] for a in articles) / len(articles),
        3
    )

    return {
        "positive": positive,
        "negative": negative,
        "neutral": neutral,
        "overall_sentiment": overall,
        "confidence_score": confidence
    }

# FETCH NEWS ENDPOINT
@router.post("/fetch", response_model=FetchNewsResponse)
async def fetch_news(request: FetchNewsRequest):

    try:
        headlines = await news_service.fetch_headlines(
            request.ticker,
            request.company_name
        )
        if not headlines:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "NO_NEWS_FOUND",
                    "message": f"No relevant news found for {request.ticker}"
                }
            )

    except Exception as e:
        print(f"News API Error: {e}")

        raise HTTPException(
            status_code=503,
            detail={
                "error": "NEWS_SERVICE_UNAVAILABLE",
                "message": "Failed to fetch data from NewsAPI"
            }
        )

    if not headlines:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "NO_NEWS_FOUND",
                "message": f"No articles found for {request.ticker}"
            }
        )

    articles = []

    for headline in headlines:

        if not headline or len(headline) < 3:
            continue

        sentiment = sentiment_service.analyze(headline)

        articles.append({
            "headline": headline,
            **sentiment
        })

    summary = build_summary(articles)

    result = {
        "ticker": request.ticker,
        "company_name": request.company_name,
        "articles": articles,
        "summary": summary
    }

    # in-memory storage
    news_history[request.ticker.upper().strip()] = result

    return result

# HISTORY ENDPOINT
@router.get("/history/{ticker}")
async def get_history(ticker: str):

    ticker = ticker.upper().strip()

    print("Stored tickers:", list(news_history.keys()))

    if ticker not in news_history:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "TICKER_NOT_FOUND",
                "message": f"No history found for ticker '{ticker}'"
            }
        )

    return news_history[ticker]