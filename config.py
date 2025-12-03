"""
Configuration settings for the Mental Health Bot.
Uses pydantic-settings for environment variable management.
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # Bot Configuration
    bot_token: str
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./mental_health_bot.db"
    
    # Admin Configuration (stored as comma-separated string, parsed to list)
    admin_ids_str: str = ""
    
    # AI API Configuration
    ai_api_url: str = "https://api.example.com/predict"
    ai_api_key: str = ""
    
    # Scheduler Configuration
    reminder_day: str = "sunday"
    reminder_hour: int = 10
    reminder_minute: int = 0
    
    # Rate Limiting
    rate_limit_messages: int = 30
    rate_limit_period: int = 60
    
    # Session Timeout (seconds)
    session_timeout: int = 3600
    
    # Timezone
    timezone: str = "UTC"
    
    @property
    def admin_ids(self) -> List[int]:
        """Parse admin IDs from comma-separated string."""
        if not self.admin_ids_str.strip():
            return []
        return [int(x.strip()) for x in self.admin_ids_str.split(',') if x.strip()]


# Global settings instance
settings = Settings()
