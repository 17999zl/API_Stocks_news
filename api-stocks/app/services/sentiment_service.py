from transformers import pipeline


class SentimentService:

    def __init__(self):
        self.classifier = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment-latest"
        )

        # map model outputs → clean labels
        self.label_map = {
            "LABEL_0": "negative",
            "LABEL_1": "neutral",
            "LABEL_2": "positive",
        }

    def analyze(self, text: str):

        result = self.classifier(text)[0]

        label = result["label"]
        score = result["score"]

        sentiment = self.label_map.get(label, label.lower())

        return {
            "sentiment": sentiment,
            "confidence": round(score, 3)
        }