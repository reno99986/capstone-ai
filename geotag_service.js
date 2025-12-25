import axios from "axios";
import authHeader from './auth-header';

// FastAPI URL from environment
const FASTAPI_URL = import.meta.env.VITE_FASTAPI_URL

// Create dedicated axios instance for FastAPI
const fastApiHttp = axios.create({
  baseURL: FASTAPI_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add response interceptor
fastApiHttp.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("FastAPI Error:", error.response?.data || error.message);
    return Promise.reject(error);
  }
);

/**
 * Send message to chatbot
 * Endpoint: POST /api/chat
 * Request: { message: "user question" }
 * Response: { 
 *   response: "AI answer text",
 *   sources: [
 *     {
 *       source: "geotags"|"prelist",
 *       usaha_id: "uuid",
 *       user_id: "uuid"|null,
 *       nama_usaha: "string",
 *       nama_komersial_usaha: "string",
 *       alamat: "string",
 *       kdprov: "string",
 *       kdkab: "string",
 *       kdkec: "string",
 *       kddesa: "string",
 *       kdsls: "string",
 *       nmprov: "string"|null,
 *       nmkab: "string"|null,
 *       nmkec: "string"|null,
 *       nmdesa: "string"|null,
 *       nmsls: "string"|null,
 *       kbli_section: "string"|null,
 *       kbli_code: "string"|null,
 *       kbli_title: "string"|null,
 *       section_code: "string"|null,
 *       kbli_section_name: "string"|null,
 *       kategori: "string",
 *       produk_utama: "string",
 *       status: "aktif"|"tidak aktif",
 *       latitude: "string",
 *       longitude: "string",
 *       created_at: "ISO timestamp",
 *       updated_at: "ISO timestamp"
 *     }
 *   ],
 *   context_used: boolean,
 *   user_id: "uuid"
 * }
 * @param {string} message - User's question
 * @returns {Promise} Chatbot response with sources
 */
export function sendChatMessage(message) {
  return fastApiHttp.post("/api/chat", 
    { message }, 
    { headers: authHeader() }
  );
}

export default {
  sendChatMessage,
};


