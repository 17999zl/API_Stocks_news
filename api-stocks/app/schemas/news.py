from pydantic import BaseModel


class FetchNewsRequest(BaseModel):
    ticker: str
    company_name: str


class ArticleSentiment(BaseModel):
    headline: str
    sentiment: str
    confidence: float


class SentimentSummary(BaseModel):
    positive: int
    negative: int
    neutral: int
    overall_sentiment: str
    confidence_score: float


class FetchNewsResponse(BaseModel):
    ticker: str
    company_name: str
    articles: list[ArticleSentiment]
    summary: SentimentSummary