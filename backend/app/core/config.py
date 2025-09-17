from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    app_name: str = "Base44"
    version: str = "1.0.0"
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Database
    database_url: str = "postgresql://base44:base44@postgres:5432/base44"
    database_test_url: str = "postgresql://base44:base44@postgres:5432/base44_test"
    
    # Redis
    redis_url: str = "redis://redis:6379"
    
    # Neo4j
    neo4j_uri: str = "bolt://neo4j:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"
    
    # OpenAI
    openai_api_key: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings()


