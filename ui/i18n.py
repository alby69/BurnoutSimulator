import json
import os

_current_lang = "it"
_translations = {}

def load_translations(lang="it"):
    global _current_lang, _translations
    _current_lang = lang
    path = os.path.join("locales", lang, "ui.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            _translations = json.load(f)
    else:
        _translations = {}

def t(key):
    return _translations.get(key, key)

# Initial load
load_translations("it")
