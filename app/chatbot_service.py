"""
Simple Intent-Based Chatbot Service
- Count queries (berapa usaha...)
- Business description (apa itu/jelaskan [nama usaha])
- NO SQL generation complexity
- REST API mode only
"""

from typing import Dict, Any, Optional
from langchain_community.llms import Ollama
import re


class ChatbotService:
    """
    Simple chatbot with 2 main features:
    1. Count queries (statistics)
    2. Business description
    """

    def __init__(self, business_service, model_name: str = "llama3.2"):
        """
        Args:
            business_service: Instance of BusinessService
            model_name: Ollama model name
        """
        self.business_service = business_service
        self.llm = Ollama(model=model_name, temperature=0.3)
        
        print(f"✓ ChatbotService initialized with model: {model_name}")

    # ============================================================
    # MAIN ENTRY POINT
    # ============================================================
    
    def chat(self, message: str) -> Dict[str, Any]:
        """
        Main chat handler
        
        Returns:
            {
                "success": bool,
                "response": str,
                "message_type": "count"|"business_info"|"out_of_scope"|"error",
                "count": int (optional),
                "business_data": dict (optional)
            }
        """
        message = (message or "").strip()
        
        if not message:
            return {
                "success": False,
                "response": "Pesan tidak boleh kosong.",
                "message_type": "error"
            }
        
        try:
            # Classify intent
            intent = self._classify_intent(message)
            
            print(f"[DEBUG] Message: '{message}' → Intent: '{intent}'")  # Debug
            
            if intent == "count":
                return self._handle_count(message)
            elif intent == "business_info":
                return self._handle_business_info(message)
            else:
                return {
                    "success": True,
                    "response": (
                        "Maaf, saya hanya dapat menjawab pertanyaan tentang:\n"
                        "• Jumlah usaha (contoh: 'berapa usaha di Balikpapan?')\n"
                        "• Informasi usaha (contoh: 'apa itu Sembako Mukhlas?')"
                    ),
                    "message_type": "out_of_scope"
                }
        
        except Exception as e:
            print(f"✗ Chat error: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "success": False,
                "response": "Terjadi kesalahan internal. Silakan coba lagi.",
                "message_type": "error"
            }

    # ============================================================
    # INTENT CLASSIFICATION (FIXED v2)
    # ============================================================
    
    def _classify_intent(self, message: str) -> str:
        """
        Classify user intent with STRICT rules
        Priority: count > business_info > unknown
        
        Returns: "count", "business_info", or "unknown"
        """
        text = message.lower().strip()
        
        # 🔴 RULE 1: Count keywords have ABSOLUTE PRIORITY
        count_keywords = [
            "berapa", "jumlah", "total", "ada berapa",
            "hitung", "count", "banyak", "berapa banyak"
        ]
        
        # If ANY count keyword exists, it's a count query
        if any(kw in text for kw in count_keywords):
            print(f"[DEBUG] Detected count keyword in: {text}")
            return "count"
        
        # 🔴 RULE 2: Business info patterns (only if NO count keywords)
        # Use STRICT patterns to avoid false positives
        
        # Pattern 1: "apa itu [nama]"
        if re.search(r'\bapa\s+itu\b', text):
            print(f"[DEBUG] Detected 'apa itu' pattern")
            return "business_info"
        
        # Pattern 2: "jelaskan [tentang] [nama]"
        if re.search(r'\bjelaskan\b', text):
            print(f"[DEBUG] Detected 'jelaskan' pattern")
            return "business_info"
        
        # Pattern 3: "deskripsikan [nama]"
        if re.search(r'\bdeskripsikan\b', text):
            print(f"[DEBUG] Detected 'deskripsikan' pattern")
            return "business_info"
        
        # Pattern 4: "info tentang [nama]"
        if re.search(r'\binfo\s+tentang\b', text):
            print(f"[DEBUG] Detected 'info tentang' pattern")
            return "business_info"
        
        # Pattern 5: "ceritakan [tentang] [nama]"
        if re.search(r'\bceritakan\b', text):
            print(f"[DEBUG] Detected 'ceritakan' pattern")
            return "business_info"
        
        # Pattern 6: "cari info [nama]"
        if re.search(r'\bcari\s+info\b', text):
            print(f"[DEBUG] Detected 'cari info' pattern")
            return "business_info"
        
        # If none matched
        print(f"[DEBUG] No pattern matched, returning unknown")
        return "unknown"

    # ============================================================
    # COUNT HANDLER
    # ============================================================
    
    def _handle_count(self, message: str) -> Dict[str, Any]:
        """Handle count queries"""
        text = message.lower()
        
        # Extract location
        kecamatan = self._extract_kecamatan(text)
        kabupaten = self._extract_kabupaten(text)
        status = self._extract_status(text)
        
        print(f"[DEBUG] Count filters - kec:{kecamatan}, kab:{kabupaten}, status:{status}")
        
        # Get count from database
        if kecamatan or kabupaten or status:
            count = self.business_service.count_by_location(
                kecamatan=kecamatan,
                kabupaten=kabupaten,
                status=status
            )
        else:
            count = self.business_service.count_all()
        
        print(f"[DEBUG] Count result: {count}")
        
        # Build response with LLM
        response = self._format_count_response(
            count=count,
            kecamatan=kecamatan,
            kabupaten=kabupaten,
            status=status
        )
        
        return {
            "success": True,
            "response": response,
            "message_type": "count",
            "count": count
        }

    def _extract_kecamatan(self, text: str) -> Optional[str]:
        """Extract district name from text"""
        districts = [
            "balikpapan timur",
            "balikpapan selatan",
            "balikpapan utara",
            "balikpapan barat",
            "balikpapan tengah",
            "balikpapan kota"
        ]
        
        for district in districts:
            if district in text:
                return district.title()
        
        return None

    def _extract_kabupaten(self, text: str) -> Optional[str]:
        """Extract city name from text"""
        # Only if no specific district mentioned
        if "balikpapan" in text and not self._extract_kecamatan(text):
            return "Balikpapan"
        return None

    def _extract_status(self, text: str) -> Optional[str]:
        """Extract status filter"""
        if "aktif" in text and "tidak" not in text and "non" not in text:
            return "aktif"
        elif "nonaktif" in text or "tidak aktif" in text:
            return "nonaktif"
        return None

    def _format_count_response(
        self,
        count: int,
        kecamatan: Optional[str],
        kabupaten: Optional[str],
        status: Optional[str]
    ) -> str:
        """Format count response naturally"""
        # Build location string
        if kecamatan:
            location = f"di Kecamatan {kecamatan}"
        elif kabupaten:
            location = f"di {kabupaten}"
        else:
            location = "di database"
        
        # Build status string
        if status:
            status_str = f" dengan status {status}"
        else:
            status_str = ""
        
        # Simple template
        response = f"Terdapat {count} usaha{status_str} {location}."
        
        return response

    # ============================================================
    # BUSINESS INFO HANDLER
    # ============================================================
    
    def _handle_business_info(self, message: str) -> Dict[str, Any]:
        """Handle business information queries"""
        # Extract business name
        business_name = self._extract_business_name(message)
        
        print(f"[DEBUG] Extracted business name: '{business_name}'")
        
        if not business_name:
            return {
                "success": False,
                "response": "Nama usaha tidak ditemukan. Contoh: 'apa itu Sembako Mukhlas?'",
                "message_type": "error"
            }
        
        # Search in database
        business = self.business_service.search_by_name(business_name)
        
        if not business:
            return {
                "success": True,
                "response": f"Saya tidak menemukan usaha dengan nama '{business_name}' di database.",
                "message_type": "not_found"
            }
        
        # Generate description with LLM
        description = self._generate_description(business)
        
        return {
            "success": True,
            "response": description,
            "message_type": "business_info",
            "business_data": business
        }

    def _extract_business_name(self, message: str) -> Optional[str]:
        """Extract business name from message (STRICT patterns)"""
        text = message.strip().rstrip('?!.')
        
        # Patterns to extract name (in order of specificity)
        patterns = [
            r"apa\s+itu\s+(.+)",           # "apa itu [nama]"
            r"jelaskan\s+tentang\s+(.+)",  # "jelaskan tentang [nama]"
            r"jelaskan\s+(.+)",            # "jelaskan [nama]"
            r"deskripsikan\s+(.+)",        # "deskripsikan [nama]"
            r"info\s+tentang\s+(.+)",      # "info tentang [nama]"
            r"ceritakan\s+tentang\s+(.+)", # "ceritakan tentang [nama]"
            r"ceritakan\s+(.+)",           # "ceritakan [nama]"
            r"cari\s+info\s+(.+)",         # "cari info [nama]"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                
                # Clean up common noise words
                name = re.sub(r'^(usaha|toko|warung|tentang)\s+', '', name, flags=re.IGNORECASE)
                
                if len(name) > 2:
                    return name
        
        return None

    def _generate_description(self, business: Dict[str, Any]) -> str:
        """
        Generate business description using LLM
        STRICTLY based on database data only
        """
        nama = business["nama_usaha"]
        kategori = business["kategori"]
        alamat = business["alamat"]
        status = business["status"]
        
        # Build location context
        location_parts = []
        if business.get("kecamatan"):
            location_parts.append(f"Kecamatan {business['kecamatan']}")
        if business.get("kabupaten"):
            location_parts.append(business["kabupaten"])
        
        location_str = ", ".join(location_parts) if location_parts else "alamat terlampir"
        
        # Prompt for LLM (strict rules)
        prompt = (
            f"Buat deskripsi singkat (maksimal 2 kalimat) tentang usaha berikut.\n\n"
            f"ATURAN WAJIB:\n"
            f"1. Kalimat pertama HARUS diawali dengan '{nama} adalah...'\n"
            f"2. Gunakan HANYA data yang diberikan di bawah\n"
            f"3. Jangan menambahkan asumsi atau opini\n"
            f"4. Maksimal 2 kalimat\n\n"
            f"DATA USAHA:\n"
            f"- Nama: {nama}\n"
            f"- Kategori: {kategori}\n"
            f"- Alamat: {alamat}\n"
            f"- Lokasi: {location_str}\n"
            f"- Status: {status}\n\n"
            f"Deskripsi:"
        )
        
        try:
            description = self.llm.invoke(prompt).strip()
            return description
        except Exception as e:
            print(f"✗ LLM generation error: {e}")
            # Fallback deterministic description
            return (
                f"{nama} adalah usaha {kategori.lower()} yang berlokasi di {alamat}. "
                f"Status usaha ini adalah {status}."
            )

    # ============================================================
    # UTILITY
    # ============================================================
    
    def get_sample_questions(self) -> list:
        """Get sample questions for UI"""
        return [
            "Berapa total usaha di database?",
            "Berapa usaha di Balikpapan?",
            "Ada berapa usaha aktif di Balikpapan Timur?",
            "Berapa jumlah usaha nonaktif di Balikpapan Selatan?",
            "Apa itu Sembako Mukhlas?",
            "Jelaskan Warung HELL MIE",
            "Info tentang PT MAHAMERU ENERGI SEMESTA",
        ]
