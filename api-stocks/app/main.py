from fastapi import FastAPI

from app.api.news import router

app = FastAPI(
    title="News Sentiment API",
    version="1.0.0"
)

app.include_router(router)