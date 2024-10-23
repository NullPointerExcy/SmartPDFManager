import json
from collections import defaultdict

import spacy

def load_spacy_model(language):
    models = {
        "english": "en_core_web_sm",
        "german": "de_core_news_sm",
        "french": "fr_core_news_sm"
    }
    if language in models:
        return spacy.load(models[language])
    else:
        raise ValueError(f"No model found for language: {language}")
