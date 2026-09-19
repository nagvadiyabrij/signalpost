from pydantic_settings import BaseSettings
from typing import Optional
import secrets


class Settings(BaseSettings):
    database_url: str = "sqlite:///./data/signalpost.db"
    openai_api_key: Optional[str] = None
    search_api_key: Optional[str] = None
    search_provider: Optional[str] = None
    
    secret_key: str = secrets.token_urlsafe(32)
    
    max_requests: int = 1800
    max_concurrency: int = 5
    request_timeout: int = 15
    max_retries: int = 2
    
    backend_port: int = 8000
    frontend_port: int = 3000
    
    environment: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
