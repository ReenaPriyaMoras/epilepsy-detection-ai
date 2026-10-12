import os
from typing import List, Union, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "Epilepsy Detection API"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    APP_VERSION: str = "2.1.0"
    
    # Database URL: Supports SQLite locally and PostgreSQL on Railway/Render
    DATABASE_URL: Optional[str] = None
    
    # Request & Inference Settings
    INFERENCE_TIMEOUT_SECONDS: float = 60.0
    MAX_UPLOAD_FILE_SIZE_MB: int = 100
    ANALYSIS_WINDOW_SECONDS: float = 30.0
    ENABLE_XAI: bool = True
    
    # JWT Authentication settings
    JWT_SECRET: str = "epilepsy-detection-ai-clinical-secret-key-2026"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # CORS Origins
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return [str(item).strip() for item in v if str(item).strip()]
        return ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
