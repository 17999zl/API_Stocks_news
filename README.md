# News Sentiment Microservice

A FastAPI-based microservice that fetches financial news headlines using NewsAPI, performs sentiment analysis using a transformer model, and returns structured sentiment insights with historical storage.

## Overview

This service provides:
- News fetching for a given company and ticker
- Sentiment analysis per article (positive, negative, neutral)
- Aggregated sentiment summary with confidence scoring
- In-memory history per ticker
- Structured error handling for external API failures and invalid inputs

## Architecture

The system follows a layered architecture:

FastAPI API Layer
→ NewsService (Data ingestion layer - NewsAPI)
→ SentimentService (ML inference layer - transformer model)
→ Aggregation layer (summary computation)
→ In-memory storage (history per ticker)

### Design Rationale

Each layer has a single responsibility:
- API layer handles request/response and validation
- Service layer handles external integrations
- Sentiment layer isolates ML inference logic
- Aggregation layer computes derived insights

This separation improves testability, maintainability, and modularity.

## Sentiment Approach

The system uses a pretrained transformer-based sentiment model (cardiffnlp/twitter-roberta-base-sentiment-latest, RoBERTa-based) accessed via the Hugging Face sentiment-analysis pipeline. This model is trained on a large corpus of tweets, making it well-suited for short, informal text such as comments and social posts.

Rationale:
- No custom training required
- Strong real-world performance on noisy, natural language text
- Better contextual understanding than rule-based or keyword approaches
- Provides calibrated confidence scores for aggregation
- Widely used and actively maintained, reducing model risk

## fetching data
News headlines are retrieved using the NewsAPI /v2/everything endpoint. The service searches using both the company name and stock ticker:
 "Apple" OR AAPL
This improves the likelihood of finding relevant financial news.

After fetching results, a lightweight relevance filter checks whether article titles contain the company name or ticker symbol. To avoid accidentally excluding valid articles, a fallback returns the original NewsAPI results if the filter removes all articles.

## Limitations

- NewsAPI is a noisy data source and may return irrelevant content
- Filtering is heuristic-based and not semantically robust
- Sentiment model is not fine-tuned specifically for financial domains
- No persistent storage (in-memory only)
- No caching or rate limiting implemented
- Limited handling of multilingual or non-English content

## Edge Case Handling

The system handles:

### Invalid or Unknown Tickers
Returns structured error responses when no data is found.

```json
{
  "detail": {
    "error": "NO_NEWS_FOUND",
    "message": "No articles found for xaaaaa"
  }
}
```

### External API Failure
Returns HTTP 503 with a structured error payload.

```json
{
  "detail": {
    "error": "NEWS_SERVICE_UNAVAILABLE",
    "message": "Failed to fetch data from NewsAPI"
  }
}
```

### Empty Results
Gracefully handles cases where no articles are returned.

```json
{
  "detail": {
    "error": "NO_NEWS_FOUND",
    "message": "No articles found for x"
  }
}
```

### Noisy Data
Filters short or irrelevant headlines before processing.

```json
{
  "detail": {
    "error": "NO_NEWS_FOUND",
    "message": "No articles found for x"
  }
}
```

## Installation

### 1. Clone repository

### 2. Create virtual environment
python -m venv venv

source venv/bin/activate   (Mac/Linux)

venv\Scripts\activate    (Windows)

### 3. Install dependencies
pip install -r requirements.txt

### 4. Add environment variables
Open `.env` file in the project root:

NEWS_API_KEY=your_api_key_here

Obtain a key from https://newsapi.org
Place it in .env file

### 5. Run the application
uvicorn app.main:app --reload

### 6. Access API documentation
http://127.0.0.1:8000/docs

## API Endpoints

### POST /news/fetch

Request:
```json
{
  "ticker": "AAPL",
  "company_name": "Apple"
}
```

Response:
```json
{
  "ticker": "AAPL",
  "company_name": "Apple",
  "articles": [
    {
      "headline": "Example headline",
      "sentiment": "positive",
      "confidence": 0.89
    }
  ],
  "summary": {
    "positive": 1,
    "negative": 0,
    "neutral": 0,
    "overall_sentiment": "positive",
    "confidence_score": 0.89
  }
}
```

### GET /news/history/{ticker}

Returns previously stored results for a ticker (in-memory storage).

## Design Decisions

- Layered architecture to separate concerns
- Heuristic filtering instead of heavy ML classification for efficiency
- Transformer-based sentiment model for accuracy
- Aggregated sentiment scoring for stability
- In-memory storage for simplicity and demonstration purposes

## Future Improvements

- Replace heuristic filtering with embedding-based relevance scoring
- Add Redis caching for performance optimization
- Persist data using PostgreSQL or MongoDB
- Add structured logging and observability (SIEM-style tracking)
- Introduce background jobs for prefetching and batching
