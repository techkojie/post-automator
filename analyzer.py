# app/analyzer_spacy.py
import spacy
from app.logger import logger

nlp = spacy.load("en_core_web_sm", disable=["parser"])

def extract_topics(text: str, top_k: int = 8):
    try:
        doc = nlp(text)
        keywords = [chunk.text.lower().strip() for chunk in doc.noun_chunks if len(chunk.text.split()) <= 3]
        entities = [ent.text.lower().strip() for ent in doc.ents]
        combined = keywords + entities
        freqs = {}
        for w in combined:
            freqs[w] = freqs.get(w, 0) + 1
        sorted_keywords = sorted(freqs.items(), key=lambda x: x[1], reverse=True)
        return [w for w,_ in sorted_keywords[:top_k]]
    except Exception:
        logger.exception("extract_topics failed")
        return []
