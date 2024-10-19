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

def load_custom_keywords(language: str, config_file: str = 'categories_config.json'):
    with open(config_file, 'r') as file:
        config = json.load(file)
    if language in config:
        return config[language]["custom_keywords"]
    else:
        raise ValueError(f"No configuration found for language: {language}")

def classify_text(text: str, language: str):
    lang: str = language.lower()

    nlp = load_spacy_model(lang)
    custom_keywords = load_custom_keywords(lang)
    doc = nlp(text)

    categories = defaultdict(list)

    for ent in doc.ents:
        categories[ent.label_].append(ent.text)


    for category, keywords in custom_keywords.items():
        for keyword in keywords:
            if keyword.lower() in text.lower():
                categories[category].append(keyword)

    return categories
