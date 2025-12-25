"""
FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database import db
from app.rag_service import rag_service
from app.routes import chatbot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    # Startup
    logger.info("Starting Geotags Chatbot Service...")
    
    try:
        # Connect to database
        await db.connect()
        
        # Initialize RAG service
        await rag_service.initialize()
        
        # Load businesses based on mode
        if settings.evaluation_mode:
            # EVALUATION MODE: Load from CSV
            logger.info("🧪 EVALUATION MODE: Loading from CSV")
            csv_path = settings.evaluation_csv_path
            businesses = await db.get_all_businesses_from_csv(csv_path)
            logger.info(f"Loaded {len(businesses)} businesses from CSV: {csv_path}")
        else:
            # PRODUCTION MODE: Load from database
            logger.info("🚀 PRODUCTION MODE: Loading from database")
            businesses = await db.get_all_businesses()
            logger.info(f"Loaded {len(businesses)} businesses from database")
        
        # Index documents (same for both modes)
        await rag_service.index_documents(businesses)
        
        logger.info("Service started successfully!")
        
    except Exception as e:
        logger.error(f"Failed to start service: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Geotags Chatbot Service...")
    await db.disconnect()
    logger.info("Service stopped")


# Create FastAPI app
app = FastAPI(
    title="Geotags Chatbot API",
    description="RAG-based chatbot for querying business information",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(chatbot.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Geotags Chatbot API",
        "version": "1.0.0",
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
