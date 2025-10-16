"""
Simple caching layer for BillGeneratorV01.

Use for repeated I/O operations that do not change often.
Caches Excel parsing, template loading, and static data lookup.
"""

import hashlib
import pickle
from pathlib import Path
from functools import wraps
import time

CACHE_DIR = Path(__file__).parent / ".cache"
CACHE_DIR.mkdir(exist_ok=True)

def _hash_args(*args, **kwargs):
    data = repr((args, kwargs)).encode()
    return hashlib.md5(data).hexdigest()

def cache_result(ttl: int = 86400):
    """
    Decorator to cache function results on disk for `ttl` seconds.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{func.__name__}_{_hash_args(*args, **kwargs)}"
            path = CACHE_DIR / f"{key}.pkl"
            if path.exists():
                age = time.time() - path.stat().st_mtime
                if age < ttl:
                    try:
                        with open(path, "rb") as fh:
                            return pickle.load(fh)
                    except Exception:
                        pass
            result = func(*args, **kwargs)
            try:
                with open(path, "wb") as fh:
                    pickle.dump(result, fh)
            except Exception:
                pass
            return result
        return wrapper
    return decorator