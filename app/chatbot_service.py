"""
Chatbot Service with Ollama LLM integration
"""
import ollama
from typing import List, Dict, Any, Optional
import logging
from app.config import settings
from app.rag_service import rag_service

logger = logging.getLogger(__name__)


class ChatbotService:
    """Chatbot service using Ollama for LLM responses"""
    
    def __init__(self):
        self.model = settings.chatbot_model
        self.client = ollama.Client(host=settings.ollama_base_url)
        self.system_prompt = """Anda adalah asisten chatbot untuk aplikasi Geotags yang membantu pengguna mencari informasi tentang usaha/bisnis.

Tugas Anda:
1. Menjawab pertanyaan tentang usaha berdasarkan data yang diberikan
2. Memberikan informasi yang akurat dan relevan
3. Jika data tidak tersedia, katakan dengan jelas
4. Gunakan bahasa Indonesia yang sopan dan profesional
5. Fokus pada informasi yang paling relevan dengan pertanyaan
6. Untuk pertanyaan statistik/jumlah, gunakan data statistik yang diberikan

ATURAN PENTING UNTUK ANGKA/STATISTIK:
- Jika ada kotak (╔═══╗) dengan angka TOTAL, GUNAKAN ANGKA ITU!
- JANGAN gunakan angka dari kategori sebagai total keseluruhan
- JANGAN menambah, mengurangi, atau mengubah angka dari data
- Jika ditanya "berapa total usaha", lihat bagian "TOTAL USAHA DI BALIKPAPAN"
- Angka kategori (misal: Rumah Makan: 349) adalah SUBSET dari total, BUKAN total keseluruhan

ATURAN UNTUK DATA TIDAK DITEMUKAN:
- Jika konteks kosong atau tidak ada data yang relevan, katakan: "Tidak ditemukan informasi tentang [nama usaha] dalam database."
- JANGAN memberikan informasi tentang usaha lain yang tidak ditanyakan
- JANGAN mencoba menebak atau memberikan alternatif jika tidak diminta
- Cukup jawab bahwa data tidak ditemukan, lalu berhenti

ATURAN UNTUK PERTANYAAN TIDAK JELAS:
- Jika pertanyaan terlalu umum atau ambigu (misal: "tes", "coba", "halo"), minta klarifikasi
- JANGAN listing semua data yang ada
- JANGAN mencoba menebak maksud user
- Berikan contoh pertanyaan yang jelas

GAYA PENULISAN:
- Langsung ke poin utama, TANPA salam pembuka yang berlebihan
- JANGAN gunakan frasa marketing seperti "Terima kasih telah memilih...", "Saya senang membantu...", dll
- JANGAN gunakan frasa bertele-tele seperti "Berikut adalah informasi yang relevan tentang..."
- Cukup langsung jawab pertanyaan dengan format: "[Nama Usaha] adalah [deskripsi singkat]"
- Sertakan detail penting: alamat, kategori, status (jika relevan)
- Jangan menambahkan informasi yang tidak ada dalam data
- Jangan Berhalusinasi
- Jangan Memberikan data kalau tidak jelas pertanyaannya
- GUNAKAN ANGKA PERSIS DARI STATISTIK DATABASE
- jangan memberikan koordinat apabila tidak ditanyakan
- Jangan memberikan koordinat apabila tidak ditanyakan dimana koordinatnya

CONTOH JAWABAN YANG BAIK:
User: "Jelaskan tentang Soto Banjar Azizah"
 BURUK: "Terima kasih telah memilih aplikasi Geotags! Berikut adalah informasi yang relevan tentang Soto Banjar Azizah Bilqis..."
 BAIK: "Soto Banjar Azizah Bilqis adalah rumah makan yang berlokasi di Jl. Serindit No.123, Gunung Bahagia, Balikpapan Selatan. Status: Aktif."

User: "Jelaskan tentang McDonald's" (tidak ada di database)
 BURUK: "McDonald's tidak terdapat dalam daftar. Namun, Velia Tekno adalah toko yang terletak di..."
 BAIK: "Tidak ditemukan informasi tentang McDonald's dalam database."

User: "Berapa jumlah usaha di Balikpapan?"
 BURUK: "Terima kasih atas pertanyaannya! Saya dengan senang hati menjelaskan bahwa berdasarkan data terkini..."
 BAIK: "Terdapat 614 usaha di Balikpapan, dengan 612 usaha aktif dan 2 tidak aktif."
"""
    
    def is_valid_query(self, message: str) -> tuple[bool, str]:
        """
        Validate if query is clear enough to process
        
        Returns:
            (is_valid, error_message)
        """
        message = message.strip()
        
        # Too short
        if len(message) < 3:
            return False, "Pertanyaan terlalu pendek. Silakan berikan pertanyaan yang lebih jelas."
        
        # Generic test words
        generic_words = ['tes', 'test', 'coba', 'halo', 'hai', 'hello', 'hi']
        if message.lower() in generic_words:
            return False, "Silakan ajukan pertanyaan spesifik tentang usaha di Balikpapan, misalnya:\n- 'Cari rumah makan di Balikpapan Selatan'\n- 'Berapa jumlah usaha aktif?'\n- 'Jelaskan tentang Soto Banjar Azizah'"
        
        return True, ""
    
    def is_counting_query(self, message: str) -> bool:
        """
        Detect if query is asking for counts/statistics
        
        Args:
            message: User's message
            
        Returns:
            True if query is about counting/statistics
        """
        message_lower = message.lower()
        counting_keywords = [
            "berapa", "jumlah", "total", "banyak", "ada berapa",
            "hitung", "count", "statistik", "data"
        ]
        return any(keyword in message_lower for keyword in counting_keywords)
    
    def is_filtering_query(self, message: str) -> tuple[bool, str, str]:
        """
        Detect if query is asking for filtered list (by status, category, location)
        
        Args:
            message: User's message
            
        Returns:
            (is_filtering, filter_type, filter_value)
        """
        message_lower = message.lower()
        
        # Status filtering
        if any(word in message_lower for word in ['tidak aktif', 'nonaktif', 'tutup', 'inactive']):
            return True, 'status', 'tidak aktif'
        if any(word in message_lower for word in ['aktif', 'buka', 'active', 'beroperasi']):
            # Only if explicitly asking for active ones
            if any(word in message_lower for word in ['yang aktif', 'usaha aktif', 'bisnis aktif']):
                return True, 'status', 'aktif'
        
        # Category filtering (can be extended)
        # if 'rumah makan' in message_lower:
        #     return True, 'category', 'rumah makan'
        
        return False, '', ''
    
    async def generate_response(
        self,
        message: str,
        context: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generate chatbot response using Ollama
        
        Args:
            message: User's message/question
            context: RAG context from relevant documents
            conversation_history: Previous conversation messages
            
        Returns:
            Chatbot response string
        """
        try:
            # Build messages for Ollama
            messages = [
                {
                    "role": "system",
                    "content": self.system_prompt
                }
            ]
            
            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history[-6:])  # Last 3 exchanges
            
            # Add current query with context
            user_message = f"""Konteks data usaha:
{context}

Pertanyaan pengguna: {message}

Berikan jawaban yang informatif berdasarkan data di atas."""
            
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # Generate response
            logger.info(f"Generating response for: '{message}'")
            response = self.client.chat(
                model=self.model,
                messages=messages
            )
            
            answer = response['message']['content']
            logger.info("Response generated successfully")
            return answer
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
    
    async def process_query(
        self,
        message: str,
        top_k: int = 5,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        db = None
    ) -> Dict[str, Any]:
        """
        Process user query end-to-end: RAG retrieval + LLM generation
        Uses hybrid approach for counting queries (database stats + RAG examples)
        
        Args:
            message: User's message
            top_k: Number of documents to retrieve
            conversation_history: Previous conversation
            db: Database instance for statistics queries
            
        Returns:
            Dictionary with response and metadata
        """
        try:
            # Import rag_service at the top to avoid scope issues
            from app.rag_service import rag_service
            
            # Validate query first
            is_valid, error_msg = self.is_valid_query(message)
            if not is_valid:
                return {
                    "response": error_msg,
                    "sources": [],
                    "context_used": False,
                    "query_type": "invalid"
                }
            
            # Check if this is a filtering query (status, category, etc.)
            is_filtering, filter_type, filter_value = self.is_filtering_query(message)
            
            if is_filtering and db:
                # For filtering queries: use database filtering
                logger.info(f"Detected filtering query: {filter_type}='{filter_value}'")
                
                # Get filtered businesses from database
                filtered_businesses = await db.get_businesses_by_filter(
                    filter_field=filter_type,
                    filter_value=filter_value,
                    limit=50
                )
                
                if not filtered_businesses:
                    return {
                        "response": f"Tidak ditemukan usaha dengan {filter_type} '{filter_value}' dalam database.",
                        "sources": [],
                        "context_used": False,
                        "query_type": "filtering"
                    }
                
                # Format context from filtered results
                context = rag_service.format_context(filtered_businesses)
                
                # Generate response with filtered data
                response = await self.generate_response(
                    message=message,
                    context=context,
                    conversation_history=conversation_history
                )
                
                return {
                    "response": response,
                    "sources": filtered_businesses,
                    "context_used": True,
                    "query_type": "filtering"
                }
            
            # Check if this is a counting/statistics query
            is_counting = self.is_counting_query(message)
            
            if is_counting and db:
                # For counting queries: use pre-calculated statistics
                logger.info("Detected counting query, using database statistics")
                
                # Get pre-calculated statistics (much faster than fetching all data)
                stats = await db.get_business_statistics()
                
                # DEBUG: Log the actual total
                logger.info(f"Database total: {stats['total']} usaha")
                logger.info(f"Active: {stats['by_status'].get('aktif', 0)}, Inactive: {stats['by_status'].get('Tidak Aktif', 0)}")
                
                # Check if query is about specific category/district
                message_lower = message.lower()
                
                # Get relevant examples via RAG
                results = await rag_service.search(message, top_k=min(top_k, 5))
                example_context = rag_service.format_context(results)
                
                # Build comprehensive statistics context with CLEAR emphasis on total
                stats_context = f"""STATISTIK DATABASE - DATA RESMI:

╔════════════════════════════════════════╗
║  TOTAL USAHA DI BALIKPAPAN: {stats['total']} USAHA  ║
╚════════════════════════════════════════╝

DETAIL STATUS:
- Usaha AKTIF: {stats['by_status'].get('aktif', 0)} usaha
- Usaha TIDAK AKTIF: {stats['by_status'].get('Tidak Aktif', 0)} usaha

SUMBER DATA:
- Data dari Geotags (input user): {stats['by_source'].get('geotags', 0)} usaha
- Data dari Prelist (import bulk): {stats['by_source'].get('prelist', 0)} usaha

TOP 5 KATEGORI TERBANYAK:
"""
                # Add top 5 categories
                for i, cat in enumerate(stats['by_category'][:5], 1):
                    stats_context += f"{i}. {cat['category']}: {cat['count']} usaha\n"
                
                stats_context += f"""
DISTRIBUSI PER KECAMATAN:
"""
                # Add districts
                for dist in stats['by_district']:
                    stats_context += f"- {dist['district']}: {dist['count']} usaha\n"
                
                stats_context += f"""
TOP 5 KELURAHAN TERBANYAK:
"""
                # Add top 5 subdistricts
                for i, subdist in enumerate(stats['by_subdistrict'][:5], 1):
                    stats_context += f"{i}. {subdist['subdistrict']}: {subdist['count']} usaha\n"
                
                stats_context += f"""
CONTOH USAHA YANG RELEVAN:
{example_context}

╔═══════════════════════════════════════════════════════════╗
║ PENTING - BACA INI:                                       ║
║ - TOTAL USAHA DI BALIKPAPAN = {stats['total']} USAHA              ║
║ - Angka di atas adalah TOTAL KESELURUHAN                  ║
║ - Jangan gunakan angka kategori sebagai total!            ║
║ - Jika ditanya "berapa usaha", jawab: {stats['total']} usaha      ║
╚═══════════════════════════════════════════════════════════╝
"""
                
                context = stats_context
                
            else:
                # Regular query: use RAG only
                results = await rag_service.search(message, top_k=top_k)
                context = rag_service.format_context(results)
            
            # Generate response
            response = await self.generate_response(
                message=message,
                context=context,
                conversation_history=conversation_history
            )
            
            return {
                "response": response,
                "sources": results,
                "context_used": True,
                "query_type": "counting" if is_counting else "search"
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            # Fallback response
            return {
                "response": "Maaf, terjadi kesalahan saat memproses pertanyaan Anda. Silakan coba lagi.",
                "sources": [],
                "context_used": False,
                "error": str(e)
            }


# Global chatbot service instance
chatbot_service = ChatbotService()
