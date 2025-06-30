from transformers import pipeline

def get_nlp_insights(text):
    nlp = pipeline("text-classification", model="distilbert-base-uncased")
    return nlp(text)
