USE_SENTIMENT = True

try:

    import torch
    import torch.nn.functional as F

    from transformers import (
        AutoTokenizer,
        AutoModelForSequenceClassification
    )

    MODEL_NAME = "distilbert-base-uncased-finetuned-sst-2-english"

    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME
    )

    model.to(device)

    model.eval()

    print(f"Sentiment Model Loaded ({device})")

    SENTIMENT_AVAILABLE = True

except ImportError:

    print("PyTorch/Transformers not installed.")
    print("Sentiment Analysis Disabled.")

    SENTIMENT_AVAILABLE = False


def predict_sentiment(text):

    if not USE_SENTIMENT or not SENTIMENT_AVAILABLE:

        return {
            "sentiment": None,
            "confidence": 0.0
        }

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=512
    )

    inputs = {
        key: value.to(device)
        for key, value in inputs.items()
    }

    with torch.no_grad():

        outputs = model(**inputs)

    probabilities = F.softmax(
        outputs.logits,
        dim=1
    )

    prediction = torch.argmax(
        probabilities,
        dim=1
    ).item()

    confidence = probabilities[
        0
    ][prediction].item()

    sentiment = (
        "POSITIVE"
        if prediction == 1
        else "NEGATIVE"
    )

    return {
        "sentiment": sentiment,
        "confidence": round(confidence, 4)
    }