def match_keywords(text, keywords):
    text = text.lower()
    return any(k in text for k in keywords)
