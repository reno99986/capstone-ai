"""
Async PostgreSQL database connection and operations
"""
import asyncpg
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.config import settings
import logging
import pandas as pd
import uuid

logger = logging.getLogger(__name__)


class Database:
    """Async PostgreSQL database manager"""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Create database connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                settings.database_url,
                min_size=2,
                max_size=10,
                command_timeout=60
            )
            logger.info("Database connection pool created successfully")
        except Exception as e:
            logger.error(f"Failed to create database pool: {e}")
            raise
    
    async def disconnect(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")
    
    async def get_all_businesses(self) -> List[Dict[str, Any]]:
        """
        Fetch all businesses from usaha_llm view
        
        Returns:
            List of business records as dictionaries
        """
        if not self.pool:
            raise RuntimeError("Database pool not initialized")
        
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("SELECT * FROM usaha_llm")
                
                # Convert asyncpg.Record to dict
                businesses = [dict(row) for row in rows]
                logger.info(f"Retrieved {len(businesses)} businesses from database")
                return businesses
                
        except Exception as e:
            logger.error(f"Error fetching businesses: {e}")
            raise
    
    async def get_all_businesses_from_csv(self, csv_path: str) -> List[Dict[str, Any]]:
        """
        Load businesses from CSV for evaluation mode
        Transform CSV to usaha_llm format
        """
        try:
            logger.info(f"Loading from CSV: {csv_path}")
            df = pd.read_csv(csv_path, delimiter=';')
            
            businesses = []
            for _, row in df.iterrows():
                # Use correct column names from CSV
                nama = str(row.get('nama tempat', row.get('nama', '')))
                
                # Skip if nama is empty
                if not nama or nama == 'nan':
                    continue
                
                business = {
                    'source': 'csv_eval',
                    'usaha_id': str(uuid.uuid4()),
                    'user_id': None,
                    'nama_usaha': nama,
                    'nama_komersial_usaha': nama,
                    'alamat': str(row.get('alamat', '')),
                    'kdprov': str(row.get('kdprov', '64')),
                    'kdkab': str(row.get('kdkab', '71')),
                    'kdkec': str(row.get('kdkec', '')),
                    'kddesa': str(row.get('kddesa', '')),
                    'kdsls': str(row.get('kdsls', '')),
                    'nmprov': 'KALIMANTAN TIMUR',
                    'nmkab': 'BALIKPAPAN',
                    'nmkec': str(row.get('nmkec', '')),
                    'nmdesa': str(row.get('nmdesa', '')),
                    'nmsls': str(row.get('nmsls', '')),
                    'kategori': str(row.get('kategori', '')),
                    'produk_utama': str(row.get('produk_utama', '')),
                    'status': 'aktif',
                    'latitude': str(row.get('latitude', '')),
                    'longitude': str(row.get('longitude', '')),
                    'created_at': datetime.now(),
                    'updated_at': datetime.now(),
                    'kbli_section': None,
                    'kbli_code': None,
                    'kbli_title': None,
                    'section_code': None,
                    'kbli_section_name': None
                }
                businesses.append(business)
            
            logger.info(f"Loaded {len(businesses)} from CSV")
            return businesses
        except Exception as e:
            logger.error(f"CSV load error: {e}")
            return []
    
    async def search_businesses(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search businesses by name or product
        
        Args:
            query: Search query string
            limit: Maximum number of results
            
        Returns:
            List of matching business records
        """
        if not self.pool:
            raise RuntimeError("Database pool not initialized")
        
        try:
            async with self.pool.acquire() as conn:
                sql = """
                    SELECT * FROM usaha_llm
                    WHERE 
                        nama_usaha ILIKE $1 OR
                        nama_komersial_usaha ILIKE $1 OR
                        produk_utama ILIKE $1 OR
                        kategori ILIKE $1
                    LIMIT $2
                """
                search_pattern = f"%{query}%"
                rows = await conn.fetch(sql, search_pattern, limit)
                
                businesses = [dict(row) for row in rows]
                logger.info(f"Found {len(businesses)} businesses matching '{query}'")
                return businesses
                
        except Exception as e:
            logger.error(f"Error searching businesses: {e}")
            return []
    
    async def get_businesses_by_filter(
        self,
        filter_field: str,
        filter_value: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get businesses filtered by specific field
        
        Args:
            filter_field: Field to filter by (e.g., 'status', 'kategori')
            filter_value: Value to filter for
            limit: Maximum number of results
            
        Returns:
            List of filtered business records
        """
        if not self.pool:
            raise RuntimeError("Database not connected")
        
        try:
            # Build query with parameterized filter
            # Using ILIKE for case-insensitive matching
            query = f"""
                SELECT *
                FROM usaha_llm
                WHERE LOWER({filter_field}) = LOWER($1)
                LIMIT $2
            """
            
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(query, filter_value, limit)
                
            businesses = [dict(row) for row in rows]
            logger.info(f"Found {len(businesses)} businesses with {filter_field}='{filter_value}'")
            return businesses
            
        except Exception as e:
            logger.error(f"Error filtering businesses: {e}")
            return []
    
    async def get_latest_update_time(self) -> Optional[datetime]:
        """
        Get the most recent update timestamp from usaha_llm
        Used for timestamp-based auto-sync tracking
        
        Returns:
            Latest update timestamp or None if no data exists
        """
        if not self.pool:
            raise RuntimeError("Database not connected")
        
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchval(
                    "SELECT MAX(updated_at) FROM usaha_llm"
                )
                return result
                
        except Exception as e:
            logger.error(f"Error fetching latest update time: {e}")
            return None
    
    async def get_max_business_id(self) -> Optional[int]:
        """
        Get the maximum business ID from usaha_llm view
        Used for tracking new data additions
        
        Returns:
            Maximum ID or None if no data exists
        """
        if not self.pool:
            raise RuntimeError("Database pool not initialized")
        
        try:
            async with self.pool.acquire() as conn:
                # Note: usaha_llm view uses 'usaha_id', not 'id'
                # But usaha_id is UUID, not sequential integer
                # For auto-sync, we should use created_at or updated_at instead
                result = await conn.fetchval(
                    "SELECT COUNT(*) FROM usaha_llm"
                )
                return result if result else 0
                
        except Exception as e:
            logger.error(f"Error fetching max business ID: {e}")
            return None
    
    async def get_businesses_after_timestamp(
        self,
        last_sync_time: datetime,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Get businesses updated after a specific timestamp
        Used for timestamp-based auto-sync
        
        Args:
            last_sync_time: Last sync timestamp
            limit: Maximum number of records to fetch
            
        Returns:
            List of new/updated business records
        """
        if not self.pool:
            raise RuntimeError("Database not connected")
        
        try:
            query = """
                SELECT *
                FROM usaha_llm
                WHERE updated_at > $1
                ORDER BY updated_at
                LIMIT $2
            """
            
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(query, last_sync_time, limit)
                
            businesses = [dict(row) for row in rows]
            logger.info(f"Found {len(businesses)} businesses updated after {last_sync_time}")
            return businesses
            
        except Exception as e:
            logger.error(f"Error fetching businesses after timestamp: {e}")
            return []
    
    async def get_business_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about businesses in Balikpapan
        
        Returns:
            Dictionary containing various business statistics
        """
        if not self.pool:
            raise RuntimeError("Database pool not initialized")
        
        try:
            async with self.pool.acquire() as conn:
                # Total count
                total = await conn.fetchval("SELECT COUNT(*) FROM usaha_llm")
                
                # Count by category (top 10)
                by_category = await conn.fetch("""
                    SELECT kategori, COUNT(*) as count
                    FROM usaha_llm
                    WHERE kategori IS NOT NULL AND kategori != ''
                    GROUP BY kategori
                    ORDER BY count DESC
                    LIMIT 10
                """)
                
                # Count by district (kecamatan)
                by_district = await conn.fetch("""
                    SELECT nmkec as district, COUNT(*) as count
                    FROM usaha_llm
                    WHERE nmkec IS NOT NULL AND nmkec != ''
                    GROUP BY nmkec
                    ORDER BY count DESC
                """)
                
                # Count by subdistrict (kelurahan) - top 10
                by_subdistrict = await conn.fetch("""
                    SELECT nmdesa as subdistrict, COUNT(*) as count
                    FROM usaha_llm
                    WHERE nmdesa IS NOT NULL AND nmdesa != ''
                    GROUP BY nmdesa
                    ORDER BY count DESC
                    LIMIT 10
                """)
                
                # Count by status
                by_status = await conn.fetch("""
                    SELECT status, COUNT(*) as count
                    FROM usaha_llm
                    WHERE status IS NOT NULL AND status != ''
                    GROUP BY status
                """)
                
                # Count by source
                by_source = await conn.fetch("""
                    SELECT source, COUNT(*) as count
                    FROM usaha_llm
                    WHERE source IS NOT NULL AND source != ''
                    GROUP BY source
                """)
                
                # Format results
                statistics = {
                    "total": total,
                    "by_category": [
                        {"category": row["kategori"], "count": row["count"]}
                        for row in by_category
                    ],
                    "by_district": [
                        {"district": row["district"], "count": row["count"]}
                        for row in by_district
                    ],
                    "by_subdistrict": [
                        {"subdistrict": row["subdistrict"], "count": row["count"]}
                        for row in by_subdistrict
                    ],
                    "by_status": {
                        row["status"]: row["count"]
                        for row in by_status
                    },
                    "by_source": {
                        row["source"]: row["count"]
                        for row in by_source
                    }
                }
                
                logger.info(f"Generated statistics for {total} businesses")
                return statistics
                
        except Exception as e:
            logger.error(f"Error fetching business statistics: {e}")
            raise


# Global database instance
db = Database()
