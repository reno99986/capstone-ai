"""
Quick script to check database statistics
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def check_stats():
    # Connect to database
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    
    # Get total count
    total = await conn.fetchval('SELECT COUNT(*) FROM usaha_llm')
    print(f"Total usaha di database: {total}")
    
    # Get by status
    by_status = await conn.fetch("""
        SELECT status, COUNT(*) as count
        FROM usaha_llm
        GROUP BY status
    """)
    
    print("\nPer Status:")
    for row in by_status:
        print(f"  - {row['status']}: {row['count']}")
    
    # Get by source
    by_source = await conn.fetch("""
        SELECT source, COUNT(*) as count
        FROM usaha_llm
        GROUP BY source
    """)
    
    print("\nPer Source:")
    for row in by_source:
        print(f"  - {row['source']}: {row['count']}")
    
    # Check if there are NULL/empty kategori
    null_kategori = await conn.fetchval("""
        SELECT COUNT(*) FROM usaha_llm
        WHERE kategori IS NULL OR kategori = ''
    """)
    print(f"\nUsaha tanpa kategori: {null_kategori}")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(check_stats())
