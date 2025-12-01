"""
Business Data Service - Direct SQL queries to usaha_llm view
Simple, robust, no LangChain complexity
"""

from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool


class BusinessService:
    """Service untuk akses data usaha dari view usaha_llm"""

    def __init__(self, db_uri: str):
        """Initialize with connection pooling disabled for reliability"""
        self.engine = create_engine(
            db_uri,
            poolclass=NullPool,
            echo=False
        )
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # Test connection
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM usaha_llm"))
                count = result.scalar()
                print(f"✓ BusinessService connected - {count} businesses in database")
        except Exception as e:
            print(f"✗ BusinessService connection failed: {e}")
            raise

    # ============================================================
    # COUNT QUERIES
    # ============================================================
    
    def count_all(self) -> int:
        """Count total businesses"""
        session = self.SessionLocal()
        try:
            result = session.execute(text("SELECT COUNT(*) FROM usaha_llm"))
            return result.scalar() or 0
        finally:
            session.close()

    def count_by_location(
        self,
        kecamatan: Optional[str] = None,
        kabupaten: Optional[str] = None,
        status: Optional[str] = None
    ) -> int:
        """Count businesses by location and status"""
        session = self.SessionLocal()
        try:
            query = "SELECT COUNT(*) FROM usaha_llm WHERE 1=1"
            params = {}
            
            if kecamatan:
                query += " AND (LOWER(nmkec) LIKE LOWER(:kecamatan) OR LOWER(alamat) LIKE LOWER(:kecamatan))"
                params["kecamatan"] = f"%{kecamatan}%"
            elif kabupaten:
                query += " AND (LOWER(nmkab) LIKE LOWER(:kabupaten) OR LOWER(alamat) LIKE LOWER(:kabupaten))"
                params["kabupaten"] = f"%{kabupaten}%"
            
            if status:
                query += " AND LOWER(status) = LOWER(:status)"
                params["status"] = status
            
            result = session.execute(text(query), params)
            return result.scalar() or 0
            
        except Exception as e:
            print(f"✗ count_by_location error: {e}")
            import traceback
            traceback.print_exc()
            return 0
        finally:
            session.close()

    # ============================================================
    # SEARCH QUERIES
    # ============================================================
    
    def search_by_name(self, nama: str) -> Optional[Dict[str, Any]]:
        """
        Search business by name (fuzzy matching)
        Returns first match or None
        """
        session = self.SessionLocal()
        try:
            # ✅ FIX: Use correct column name 'nama_komersial_usaha'
            query = """
                SELECT 
                    nama_usaha, nama_komersial_usaha, alamat, kategori, status,
                    nmprov, nmkab, nmkec, nmdesa,
                    latitude, longitude
                FROM usaha_llm
                WHERE LOWER(nama_usaha) LIKE LOWER(:nama)
                   OR LOWER(nama_komersial_usaha) LIKE LOWER(:nama)
                LIMIT 1
            """
            params = {"nama": f"%{nama}%"}
            
            result = session.execute(text(query), params)
            row = result.fetchone()
            
            if not row:
                # Try word-by-word fuzzy search
                words = nama.split()
                if len(words) > 1:
                    # Search for longest word (usually most distinctive)
                    longest_word = max(words, key=len)
                    if len(longest_word) > 3:
                        query2 = """
                            SELECT 
                                nama_usaha, nama_komersial_usaha, alamat, kategori, status,
                                nmprov, nmkab, nmkec, nmdesa,
                                latitude, longitude
                            FROM usaha_llm
                            WHERE LOWER(nama_usaha) LIKE LOWER(:word)
                               OR LOWER(nama_komersial_usaha) LIKE LOWER(:word)
                            LIMIT 1
                        """
                        params2 = {"word": f"%{longest_word}%"}
                        result = session.execute(text(query2), params2)
                        row = result.fetchone()
            
            if not row:
                print(f"✗ Business not found: {nama}")
                return None
            
            print(f"✓ Found business: {row[0]}")
            
            return {
                "nama_usaha": row[0],
                "nama_komersial": row[1],  # nama_komersial_usaha
                "alamat": row[2],
                "kategori": row[3],
                "status": row[4],
                "provinsi": row[5],
                "kabupaten": row[6],
                "kecamatan": row[7],
                "kelurahan": row[8],
                "latitude": float(row[9]) if row[9] else None,
                "longitude": float(row[10]) if row[10] else None
            }
            
        except Exception as e:
            print(f"✗ search_by_name error: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            session.close()

    # ============================================================
    # LIST QUERIES
    # ============================================================
    
    def list_businesses(
        self,
        kecamatan: Optional[str] = None,
        kabupaten: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """List businesses with filters"""
        session = self.SessionLocal()
        try:
            query = """
                SELECT nama_usaha, alamat, kategori, status
                FROM usaha_llm
                WHERE 1=1
            """
            params = {}
            
            if kecamatan:
                query += " AND (LOWER(nmkec) LIKE LOWER(:kecamatan) OR LOWER(alamat) LIKE LOWER(:kecamatan))"
                params["kecamatan"] = f"%{kecamatan}%"
            elif kabupaten:
                query += " AND (LOWER(nmkab) LIKE LOWER(:kabupaten) OR LOWER(alamat) LIKE LOWER(:kabupaten))"
                params["kabupaten"] = f"%{kabupaten}%"
            
            if status:
                query += " AND LOWER(status) = LOWER(:status)"
                params["status"] = status
            
            query += " ORDER BY created_at DESC LIMIT :limit"
            params["limit"] = limit
            
            result = session.execute(text(query), params)
            
            businesses = []
            for row in result:
                businesses.append({
                    "nama_usaha": row[0],
                    "alamat": row[1],
                    "kategori": row[2],
                    "status": row[3]
                })
            
            return businesses
            
        except Exception as e:
            print(f"✗ list_businesses error: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            session.close()

    # ============================================================
    # UTILITY
    # ============================================================
    
    def close(self):
        """Close engine"""
        self.engine.dispose()