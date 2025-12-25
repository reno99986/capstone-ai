"""
JWT Authentication middleware compatible with existing backend
"""
import jwt
from fastapi import Request, HTTPException, status
from typing import Dict, Any
from app.config import settings

# JWT Secret constant
JWT_SECRET = settings.jwt_secret_key


# ============================================================
# Dependencies
# ============================================================
def get_current_user(request: Request) -> Dict[str, Any]:
    """JWT authentication"""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak ditemukan",
        )

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Format token tidak valid",
        )

    token = parts[1]

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return {
            "user_id": payload.get("sub") or payload.get("user_id"),
            "role": payload.get("role"),
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token sudah kadaluarsa",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak valid",
        )
