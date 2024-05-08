# translator.py
from easynmt import EasyNMT
from googletrans import Translator as GoogleTranslator
from langdetect import detect
from .cache import Cache

class TranslationService:
    def __init__(self, cache_dir=None, offline_model='opus-mt', cache_ttl=3600):
        self.translator_offline = EasyNMT(offline_model)
        self.translator_online = GoogleTranslator()
        self.cache = Cache(directory=cache_dir)
        self.cache_ttl = cache_ttl

    def detect_language(self, text):
        return detect(text)

    def translate_offline(self, text, target_lang='en'):
        source_lang = self.detect_language(text)
        cache_key = f"{source_lang}:{target_lang}:{text}"
        cached_translation = self.cache.get(cache_key)

        if cached_translation:
            return cached_translation

        translation = self.translator_offline.translate(text, source_lang=source_lang, target_lang=target_lang)
        self.cache.set(cache_key, translation, ttl=self.cache_ttl)
        return translation

    def translate_online(self, text, target_lang='en'):
        source_lang = self.detect_language(text)
        cache_key = f"{source_lang}:{target_lang}:{text}"
        cached_translation = self.cache.get(cache_key)

        if cached_translation:
            return cached_translation

        translation = self.translator_online.translate(text, src=source_lang, dest=target_lang).text
        self.cache.set(cache_key, translation, ttl=self.cache_ttl)
        return translation

    def translate(self, text, target_lang='en', online=True):
        if online:
            try:
                return self.translate_online(text, target_lang)
            except Exception:
                return self.translate_offline(text, target_lang)
        else:
            return self.translate_offline(text, target_lang)
