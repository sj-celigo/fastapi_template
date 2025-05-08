from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        case_sensitive=True,
        extra="ignore"  # Ignore extra fields from env variables
    )

    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "FastAPI Template"
    SECRET_KEY: str
    
    # CORS settings
    # Default to allowing all local origins
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # SQLite database for local development only
    SQLITE_FILE: str = "app.db"
    SQLALCHEMY_DATABASE_URI: str = f"sqlite:///./{SQLITE_FILE}"


settings = Settings() 