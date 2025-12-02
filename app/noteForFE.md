Use This service js for chatbopt

```javascript



import axios from "axios";
import authHeader from './auth-header';

// Hardcode Flask API URL
const FASTAPI_URL = import.meta.env.VITE_FLASK_API_URL || "http://localhost:8080";

// Create dedicated axios instance for Flask
const flaskHttp = axios.create({
  baseURL: FASTAPI_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add response interceptor
flaskHttp.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("Flask API Error:", error.response?.data || error.message);
    return Promise.reject(error);
  }
);

/**
 * Get sample questions for chatbot
 * Endpoint: GET /chatbot/samples
 * Response: { success: true, samples: ["Question 1", "Question 2", ...] }
 * @returns {Promise} List of sample questions
 */
export function getChatbotSamples() {
  return flaskHttp.get("/chatbot/samples", { 
    headers: authHeader() 
  });
}

/**
 * Send message to chatbot
 * Endpoint: POST /chatbot/chat
 * Request: { message: "user question" }
 * Response: { 
 *   success: true, 
 *   response: "AI answer", 
 *   message_type: "count"|"list"|"business_info"|"error"|"out_of_scope",
 *   count?: number,
 *   business_data?: object
 * }
 * Note: SQL query is NO LONGER returned (security)
 * @param {string} message - User's question
 * @returns {Promise} Chatbot response
 */
export function sendChatMessage(message) {
  return flaskHttp.post("/chatbot/chat", 
    { message }, 
    { headers: authHeader() }
  );
}

export default {
  getChatbotSamples,
  sendChatMessage,
};




```