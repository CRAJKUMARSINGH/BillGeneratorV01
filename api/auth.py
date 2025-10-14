# api/auth.py
"""
Simple auth stub for SaaS gateway.
Replace with JWT/OAuth implementation for production.
"""

from fastapi import HTTPException, Header

def verify_token(x_api_key: str | None = Header(default=None)):
    # Placeholder: allow local dev if key missing
    if x_api_key is None or x_api_key == "dev-key":
        return {"tenant": "local", "role": "dev"}
    # In production validate JWT / DB lookup
    if x_api_key.startswith("svc-"):
        return {"tenant": "svc", "role": "service"}
    raise HTTPException(status_code=401, detail="Invalid API key")