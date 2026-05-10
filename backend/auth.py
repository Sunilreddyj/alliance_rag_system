import jwt
import hashlib
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config import SECRET_KEY, ADMIN_PASSWORD

security = HTTPBearer()
TOKEN_EXPIRY_HOURS = 8


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


ADMIN_PASSWORD_HASH = hash_password(ADMIN_PASSWORD)


def create_token(username: str) -> str:
    payload = {
        "sub": username,
        "role": "admin",
        "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if payload.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def authenticate_admin(password: str) -> str:
    if hash_password(password) != ADMIN_PASSWORD_HASH:
        raise HTTPException(status_code=401, detail="Invalid admin password")
    return create_token("admin")
