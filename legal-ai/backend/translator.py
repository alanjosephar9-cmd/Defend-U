from deep_translator import GoogleTranslator
from functools import lru_cache

@lru_cache(maxsize=1000)
def translate_text(text, target_lang='en'):
    """
    Translates text to the target language using Google Translate.
    Items to check:
    - If target is 'en' or empty, return original.
    - If text is too short or empty, return original.
    - Handles exceptions gracefully.
    """
    if not text or not target_lang or target_lang == 'en':
        return text

    try:
        # Split text if it's too long (Google Translate limit usually ~5000 chars)
        # For simplicity, we'll just truncate or limit usage in calling functions for now
        # deeper implementation would split by sentences.
        if len(text) > 4500:
            text = text[:4500]
            
        translator = GoogleTranslator(source='auto', target=target_lang)
        return translator.translate(text)
    except Exception as e:
        print(f"Translation Error: {e}")
        return text

def translate_list(items, target_lang='en'):
    """Helper to translate a list of strings"""
    if not items or not target_lang or target_lang == 'en':
        return items
    
    return [translate_text(item, target_lang) for item in items]
