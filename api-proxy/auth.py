from fastapi import Header, HTTPException
import jwt
from .config import AI_PROXY_API_KEY, JWT_SECRET, JWT_ALGORITHM

def require_api_key(x_api_key: str = Header(None)):
    if not x_api_key or x_api_key != AI_PROXY_API_KEY:
        raise HTTPException(status_code=401, detail="Missing or invalid API key.")
    return True

def verify_jwt_token(authorization: str = Header(None)):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    parts = authorization.split()

    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid Authorization format")

    token = parts[1]

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid JWT token")
