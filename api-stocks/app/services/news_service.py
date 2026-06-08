import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()


class NewsService:

    def __init__(self):
        self.api_key = os.getenv("NEWS_API_KEY")

    def is_relevant(self, title: str, company: str, ticker: str) -> bool:
        text = title.lower()

        keywords = [
            company.lower(),
            ticker.lower(),
        ]

        if company.lower() == "apple":
            keywords.extend([
                "iphone",
                "ios",
                "mac",
                "ipad",
                "wwdc",
                "siri",
            ])

        return any(keyword in text for keyword in keywords)

    async def fetch_headlines(
        self,
        ticker: str,
        company_name: str,
    ):

        url = "https://newsapi.org/v2/everything"

        params = {
            "q": f'"{company_name}" OR {ticker}',
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 10,
            "apiKey": self.api_key,
        }

        response = requests.get(
            url,
            params=params,
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        filtered_headlines = []

        for article in data.get("articles", []):
            title = article.get("title")

            if not title:
                continue

            if self.is_relevant(title, company_name, ticker):
                filtered_headlines.append(title)

        # fallback if filter was too strict
        if filtered_headlines:
            return filtered_headlines

        return [
            article.get("title")
            for article in data.get("articles", [])
            if article.get("title")
        ]