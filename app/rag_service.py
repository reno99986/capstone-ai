"""
RAG (Retrieval Augmented Generation) Service
Uses sentence-transformers for embeddings and FAISS for vector search
"""
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import json

logger = logging.getLogger(__name__)


class RAGService:
    """RAG service for semantic search over business data"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize RAG service
        
        Args:
            model_name: Sentence transformer model name
                       (all-MiniLM-L6-v2 is lightweight and fast)
        """
        self.model_name = model_name
        self.model: Optional[SentenceTransformer] = None
        self.index: Optional[faiss.Index] = None
        self.documents: List[Dict[str, Any]] = []
        self.embeddings: Optional[np.ndarray] = None
        
        # Auto-sync tracking (TIMESTAMP-BASED)
        self.last_check_time: Optional[datetime] = None
        self.last_sync_time: Optional[datetime] = None  # Changed from last_known_max_id
        self.usaha_id_to_index: Dict[str, int] = {}  # Changed from id_to_index (UUID mapping)
        self.sync_interval_seconds: int = 60  # Will be set from config
        
        # Sync statistics
        self.sync_stats = {
            'total_checks': 0,
            'found_new_data': 0,
            'last_sync': None,
            'total_documents_added': 0
        }
        
    async def initialize(self):
        """Load the sentence transformer model"""
        try:
            logger.info(f"Loading sentence transformer model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("RAG service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {e}")
            raise
    
    def _create_document_text(self, business: Dict[str, Any]) -> str:
        """
        Create searchable text from business data
        
        Args:
            business: Business record dictionary
            
        Returns:
            Formatted text for embedding
        """
        parts = []
        
        # Business names
        if business.get("nama_usaha"):
            parts.append(f"Nama: {business['nama_usaha']}")
        if business.get("nama_komersial_usaha"):
            parts.append(f"Nama Komersial: {business['nama_komersial_usaha']}")
        
        # Location
        if business.get("alamat"):
            parts.append(f"Alamat: {business['alamat']}")
        if business.get("nmkec"):
            parts.append(f"Kecamatan: {business['nmkec']}")
        if business.get("nmkab"):
            parts.append(f"Kabupaten/Kota: {business['nmkab']}")
        if business.get("nmprov"):
            parts.append(f"Provinsi: {business['nmprov']}")
        
        # Business info
        if business.get("kategori"):
            parts.append(f"Kategori: {business['kategori']}")
        if business.get("produk_utama"):
            parts.append(f"Produk: {business['produk_utama']}")
        if business.get("kbli_title"):
            parts.append(f"KBLI: {business['kbli_title']}")
        
        # Status
        if business.get("status"):
            parts.append(f"Status: {business['status']}")
        
        return " | ".join(parts)
    
    async def index_documents(self, businesses: List[Dict[str, Any]]):
        """
        Index business documents for semantic search
        
        Args:
            businesses: List of business records from database
        """
        if not self.model:
            raise RuntimeError("RAG service not initialized")
        
        try:
            logger.info(f"Indexing {len(businesses)} business documents...")
            
            # Store documents
            self.documents = businesses
            
            # Create text representations
            texts = [self._create_document_text(biz) for biz in businesses]
            
            # Generate embeddings
            logger.info("Generating embeddings...")
            self.embeddings = self.model.encode(
                texts,
                show_progress_bar=True,
                convert_to_numpy=True
            )
            
            # Create FAISS index
            dimension = self.embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(self.embeddings)
            
            # Initialize tracking for auto-sync (TIMESTAMP-BASED with UUID)
            self.usaha_id_to_index = {}
            for idx, biz in enumerate(businesses):
                if 'usaha_id' in biz:
                    # Map UUID to index
                    self.usaha_id_to_index[str(biz['usaha_id'])] = idx
            
            # Set last sync time to now
            self.last_sync_time = datetime.now()
            
            logger.info(f"Successfully indexed {len(businesses)} documents")
            logger.info(f"Tracking initialized with {len(self.usaha_id_to_index)} UUIDs")
            logger.info(f"Last sync time: {self.last_sync_time}")
            
        except Exception as e:
            logger.error(f"Error indexing documents: {e}")
            raise
    
    async def search(
        self,
        query: str,
        top_k: int = 5,
        min_relevance: float = 0.2  # Lowered for better evaluation matching
    ) -> List[Dict[str, Any]]:
        """
        Semantic search for relevant businesses
        
        Args:
            query: User query string
            top_k: Number of top results to return
            min_relevance: Minimum relevance score (0-1) to include result
            
        Returns:
            List of most relevant business records with scores
        """
        if not self.model or not self.index:
            raise RuntimeError("RAG service not initialized or no documents indexed")
        
        try:
            # Encode query
            query_embedding = self.model.encode([query], convert_to_numpy=True)
            
            # Search with more candidates to filter
            search_k = min(top_k * 3, len(self.documents))  # Get 3x results for filtering
            distances, indices = self.index.search(query_embedding, search_k)
            
            # Prepare results with relevance filtering
            results = []
            for idx, distance in zip(indices[0], distances[0]):
                if idx < len(self.documents):
                    # Convert L2 distance to similarity score (0-1)
                    # Lower distance = higher similarity
                    relevance_score = float(1 / (1 + distance))
                    
                    # Only include if above threshold
                    if relevance_score >= min_relevance:
                        result = self.documents[idx].copy()
                        result["relevance_score"] = relevance_score
                        results.append(result)
                        
                        # Stop if we have enough relevant results
                        if len(results) >= top_k:
                            break
            
            if results:
                logger.info(f"Found {len(results)} relevant results for query: '{query}'")
                logger.info(f"Top relevance score: {results[0]['relevance_score']:.3f}")
            else:
                logger.warning(f"No results above relevance threshold {min_relevance} for query: '{query}'")
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise
    
    async def add_documents(self, new_businesses: List[Dict[str, Any]]):
        """
        Add new documents to the index incrementally
        This is much faster than re-indexing all documents
        
        Args:
            new_businesses: List of new business records to add
        """
        if not self.model or not self.index:
            raise RuntimeError("RAG service not initialized or no documents indexed")
        
        if not new_businesses:
            return
        
        try:
            logger.info(f"Adding {len(new_businesses)} new documents to index...")
            
            # Generate embeddings for new documents only
            texts = [self._create_document_text(biz) for biz in new_businesses]
            new_embeddings = self.model.encode(texts, convert_to_numpy=True)
            
            # Add to FAISS index
            self.index.add(new_embeddings)
            
            # Update tracking (UUID-BASED)
            start_idx = len(self.documents)
            for i, biz in enumerate(new_businesses):
                self.documents.append(biz)
                if 'usaha_id' in biz:
                    # Map UUID to index
                    self.usaha_id_to_index[str(biz['usaha_id'])] = start_idx + i
            
            # Concatenate embeddings
            if self.embeddings is not None:
                self.embeddings = np.vstack([self.embeddings, new_embeddings])
            else:
                self.embeddings = new_embeddings
            
            # Update stats
            self.sync_stats['total_documents_added'] += len(new_businesses)
            
            logger.info(f"Successfully added {len(new_businesses)} documents. Total: {len(self.documents)}")
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    async def sync_if_needed(self, db) -> bool:
        """
        Check database for new data and sync if needed (TIMESTAMP-BASED)
        Uses rate limiting to avoid excessive checks
        
        Args:
            db: Database instance for querying
            
        Returns:
            True if sync was performed
        """
        from app.config import settings
        
        now = datetime.now()
        check_interval = timedelta(seconds=settings.rag_sync_interval_seconds)
        
        # Rate limiting: skip if checked recently
        if self.last_check_time and (now - self.last_check_time) < check_interval:
            return False
        
        self.last_check_time = now
        
        try:
            self.sync_stats['total_checks'] += 1
            
            # Get latest update time from database
            latest_db_time = await db.get_latest_update_time()
            
            if not latest_db_time:
                logger.warning("Could not get latest update time from database")
                return False
            
            # Check if there are new updates
            if self.last_sync_time and latest_db_time <= self.last_sync_time:
                # No new updates
                return False
            
            # Get new/updated businesses
            new_businesses = await db.get_businesses_after_timestamp(
                self.last_sync_time or datetime.min,
                limit=1000
            )
            
            if not new_businesses:
                return False
            
            logger.info(f"Found {len(new_businesses)} new/updated businesses")
            
            # Add new documents to index
            await self.add_documents(new_businesses)
            
            # Update last sync time
            self.last_sync_time = latest_db_time
            
            self.sync_stats['found_new_data'] += 1
            self.sync_stats['last_sync'] = now
            
            logger.info(f"Auto-sync completed. Total documents: {len(self.documents)}")
            return True
            
        except Exception as e:
            logger.error(f"Error in auto-sync: {e}")
            return False # Don't raise - we don't want to block chat if sync fails
    
    def format_context(self, results: List[Dict[str, Any]]) -> str:
        """
        Format search results into context for LLM
        
        Args:
            results: List of business records from search
            
        Returns:
            Formatted context string
        """
        if not results:
            return "Tidak ada data usaha yang ditemukan."
        
        context_parts = ["Berikut adalah data usaha yang relevan:\n"]
        
        for i, biz in enumerate(results, 1):
            parts = [f"\n{i}. {biz.get('nama_usaha', 'N/A')}"]
            
            if biz.get("nama_komersial_usaha"):
                parts.append(f"   Nama Komersial: {biz['nama_komersial_usaha']}")
            
            if biz.get("alamat"):
                parts.append(f"   Alamat: {biz['alamat']}")
            
            if biz.get("kategori"):
                parts.append(f"   Kategori: {biz['kategori']}")
            
            if biz.get("produk_utama"):
                parts.append(f"   Produk Utama: {biz['produk_utama']}")
            
            if biz.get("status"):
                parts.append(f"   Status: {biz['status']}")
            
            if biz.get("latitude") and biz.get("longitude"):
                parts.append(f"   Koordinat: {biz['latitude']}, {biz['longitude']}")
            
            context_parts.append("\n".join(parts))
        
        return "\n".join(context_parts)


# Global RAG service instance
rag_service = RAGService()
