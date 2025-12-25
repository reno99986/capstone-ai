"""
Configuration management using Pydantic Settings
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # JWT Configuration
    jwt_secret_key: str = "CLASSIFIED"
    jwt_algorithm: str = "HS256"
    
    # Database Configuration
    database_url: str
    
    # Chatbot Configuration
    chatbot_model: str = "llama3.2"
    ollama_base_url: str = "http://localhost:11434"
    
    # RAG Configuration
    rag_sync_interval_seconds: int = 60  # Auto-sync check interval (1 minute)
    
    # Evaluation Mode (for testing)
    evaluation_mode: bool = False
    evaluation_csv_path: str = "output.csv"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # CORS Configuration
    cors_origins: str = "http://localhost:3000,http://localhost:8080"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.cors_origins.split(",")]


# Global settings instance
settings = Settings()
