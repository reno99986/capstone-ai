"""
Chatbot API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from app.auth import get_current_user
from app.chatbot_service import chatbot_service
from app.database import db
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chatbot"])


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str = Field(..., min_length=1, max_length=1000, description="User message")
    conversation_history: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description="Previous conversation messages"
    )
    top_k: int = Field(default=5, ge=1, le=20, description="Number of relevant documents to retrieve")


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    sources: List[Dict[str, Any]]
    context_used: bool
    user_id: str


class BusinessStatistics(BaseModel):
    """Business statistics model"""
    total: int
    by_category: List[Dict[str, Any]]
    by_district: List[Dict[str, Any]]
    by_subdistrict: List[Dict[str, Any]]
    by_status: Dict[str, int]
    by_source: Dict[str, int]


class BusinessResponse(BaseModel):
    """Business list response model"""
    businesses: List[Dict[str, Any]]
    total: int
    statistics: BusinessStatistics



@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Send a message to the chatbot
    
    Requires JWT authentication via Bearer token.
    
    Args:
        request: Chat request with message and optional history
        current_user: Authenticated user from JWT token
        
    Returns:
        Chatbot response with relevant business information
    """
    try:
        logger.info(f"Chat request from user {current_user['user_id']}: '{request.message}'")
        
        # Auto-sync: check for new data and update index if needed
        from app.rag_service import rag_service
        await rag_service.sync_if_needed(db)
        
        # Process query with RAG + LLM (pass db for counting queries)
        result = await chatbot_service.process_query(
            message=request.message,
            top_k=request.top_k,
            conversation_history=request.conversation_history,
            db=db  # Pass database instance for hybrid queries
        )
        
        return ChatResponse(
            response=result["response"],
            sources=result["sources"],
            context_used=result["context_used"],
            user_id=current_user["user_id"]
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Terjadi kesalahan saat memproses permintaan"
        )


@router.get("/businesses", response_model=BusinessResponse)
async def get_businesses(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get all businesses from database with comprehensive statistics
    
    Requires JWT authentication via Bearer token.
    Useful for debugging and admin purposes.
    
    Args:
        current_user: Authenticated user from JWT token
        
    Returns:
        List of all businesses with statistics including:
        - Total count
        - Count by category (top 10)
        - Count by district (kecamatan)
        - Count by subdistrict (kelurahan, top 10)
        - Count by status (aktif/tidak aktif)
        - Count by source (geotags/prelist)
    """
    try:
        logger.info(f"Get businesses request from user {current_user['user_id']}")
        
        # Fetch businesses and statistics
        businesses = await db.get_all_businesses()
        stats = await db.get_business_statistics()
        
        return BusinessResponse(
            businesses=businesses,
            total=len(businesses),
            statistics=BusinessStatistics(**stats)
        )
        
    except Exception as e:
        logger.error(f"Error in get_businesses endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Terjadi kesalahan saat mengambil data usaha"
        )


@router.get("/health")
async def health_check():
    """
    Health check endpoint (no authentication required)
    
    Returns:
        Service status
    """
    return {
        "status": "healthy",
        "service": "geotags-chatbot",
        "version": "1.0.0"
    }


@router.get("/admin/sync-stats")
async def get_sync_stats(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get RAG auto-sync statistics
    
    Requires JWT authentication via Bearer token.
    Useful for monitoring and tuning sync interval.
    
    Args:
        current_user: Authenticated user from JWT token
        
    Returns:
        Sync statistics and recommendations
    """
    try:
        from app.rag_service import rag_service
        from app.config import settings
        
        stats = rag_service.sync_stats.copy()
        
        # Calculate hit rate
        hit_rate = (
            (stats['found_new_data'] / stats['total_checks'] * 100)
            if stats['total_checks'] > 0 else 0
        )
        
        # Generate recommendation
        if hit_rate < 5:
            recommendation = "Consider increasing interval (data rarely changes)"
        elif hit_rate > 50:
            recommendation = "Consider decreasing interval (data changes frequently)"
        else:
            recommendation = "Interval is optimal"
        
        return {
            "total_checks": rag_service.sync_stats.get('total_checks', 0),
            "found_new_data": rag_service.sync_stats.get('found_new_data', 0),
            "last_sync": rag_service.sync_stats.get('last_sync'),
            "total_documents_added": rag_service.sync_stats.get('total_documents_added', 0),
            "current_document_count": len(rag_service.documents),
            "last_sync_time": rag_service.last_sync_time.isoformat() if rag_service.last_sync_time else None,
            "last_check_time": rag_service.last_check_time.isoformat() if rag_service.last_check_time else None,
            "sync_interval_seconds": settings.rag_sync_interval_seconds,
            "tracking_method": "timestamp-based (UUID)",
            "tracked_businesses": len(rag_service.usaha_id_to_index)
        }
        
    except Exception as e:
        logger.error(f"Error getting sync stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve sync statistics"
        )
