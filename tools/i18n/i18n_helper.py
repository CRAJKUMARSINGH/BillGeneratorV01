import json
from pathlib import Path

LANG_DIR = Path("locales")
_current = "en"

def set_lang(lang):
    global _current
    _current = lang if (LANG_DIR / f"{lang}.json").exists() else "en"

def t(key):
    fp = LANG_DIR / f"{_current}.json"
    try:
        data = json.loads(fp.read_text(encoding="utf-8"))
        return data.get(key, key)
    except Exception:
        return key