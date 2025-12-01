import os
import jwt
from functools import lru_cache

from fastapi import FastAPI, Depends, HTTPException, status, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any

from dotenv import load_dotenv
from starlette.concurrency import run_in_threadpool

from business_service import BusinessService
from chatbot_service import ChatbotService


# ============================================================
# Load env
# ============================================================
load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET:
    raise ValueError("JWT_SECRET_KEY tidak ditemukan di .env")

DATABASE_URL = os.getenv("DATABASE_URL")
CHATBOT_MODEL = os.getenv("CHATBOT_MODEL", "llama3.2")
INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY", "supersecretkey")


# ============================================================
# FastAPI init + CORS
# ============================================================
app = FastAPI(title="Geotagging + Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Service initialization
# ============================================================
business_service: Optional[BusinessService] = None
chatbot_service: Optional[ChatbotService] = None

if DATABASE_URL:
    try:
        business_service = BusinessService(db_uri=DATABASE_URL)
        chatbot_service = ChatbotService(
            business_service=business_service,
            model_name=CHATBOT_MODEL,
        )
        print("✓ Services initialized successfully")
    except Exception as e:
        print(f"✗ Service initialization failed: {e}")


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


def verify_internal_key(x_internal_key: str = Query(..., alias="X-Internal-Key")) -> bool:
    """Verify internal API key"""
    if x_internal_key != INTERNAL_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid internal API key",
        )
    return True


# ============================================================
# Pydantic Models
# ============================================================
class ChatbotChatRequest(BaseModel):
    message: str


# ============================================================
# Chatbot Endpoints
# ============================================================
@app.post("/chatbot/chat")
async def chatbot_chat(
    body: ChatbotChatRequest,
    user: Dict[str, Any] = Depends(get_current_user),
):
    """Main chatbot endpoint"""
    if not chatbot_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chatbot service tidak tersedia",
        )

    result = await run_in_threadpool(chatbot_service.chat, body.message)
    return result


@app.get("/chatbot/samples")
async def chatbot_samples(
    user: Dict[str, Any] = Depends(get_current_user),
):
    """Get sample questions"""
    if not chatbot_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chatbot service tidak tersedia",
        )

    samples = await run_in_threadpool(chatbot_service.get_sample_questions)
    return {
        "success": True,
        "samples": samples,
    }


# ============================================================
# Internal Endpoints (for debugging)
# ============================================================
@app.get("/internal/test")
async def internal_test(
    _: bool = Depends(verify_internal_key),
):
    """Test internal endpoint"""
    if not business_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Business service tidak tersedia",
        )

    count = business_service.count_all()

    return {
        "success": True,
        "total_businesses": count,
        "message": "Internal API working",
    }


# ============================================================
# Health check
# ============================================================
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "business_service": business_service is not None,
            "chatbot_service": chatbot_service is not None,
        },
    }


# ============================================================
# Run server
# ============================================================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=5000, reload=True)
