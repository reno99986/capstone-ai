"""
Test script untuk chatbot service
Jalankan ini untuk memverifikasi setup
"""
import asyncio
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings
from app.database import db
from app.rag_service import rag_service


async def test_setup():
    """Test database connection and RAG initialization"""
    print("=" * 60)
    print("Testing Geotags Chatbot Setup")
    print("=" * 60)
    print()
    
    # Test 1: Configuration
    print("✓ Configuration loaded")
    print(f"  - Database URL: {settings.database_url[:30]}...")
    print(f"  - Chatbot Model: {settings.chatbot_model}")
    print(f"  - Ollama URL: {settings.ollama_base_url}")
    print()
    
    # Test 2: Database connection
    print("Testing database connection...")
    try:
        await db.connect()
        print("✓ Database connected successfully")
        
        businesses = await db.get_all_businesses()
        print(f"✓ Retrieved {len(businesses)} businesses from database")
        
        if businesses:
            print(f"  Sample business: {businesses[0].get('nama_usaha', 'N/A')}")
        print()
        
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        print("  Please check your DATABASE_URL in .env file")
        return False
    
    # Test 3: RAG Service
    print("Testing RAG service...")
    try:
        await rag_service.initialize()
        print("✓ RAG service initialized")
        
        await rag_service.index_documents(businesses)
        print(f"✓ Indexed {len(businesses)} documents")
        print()
        
    except Exception as e:
        print(f"✗ RAG initialization failed: {e}")
        return False
    
    # Test 4: Search test
    print("Testing semantic search...")
    try:
        results = await rag_service.search("warung kopi", top_k=3)
        print(f"✓ Search completed, found {len(results)} results")
        
        if results:
            print("  Top result:")
            print(f"    - {results[0].get('nama_usaha', 'N/A')}")
            print(f"    - Score: {results[0].get('relevance_score', 0):.3f}")
        print()
        
    except Exception as e:
        print(f"✗ Search test failed: {e}")
        return False
    
    # Cleanup
    await db.disconnect()
    
    print("=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Make sure Ollama is running: ollama serve")
    print("2. Pull the model: ollama pull llama3.2")
    print("3. Start the server: run.bat")
    print()
    
    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(test_setup())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
