from pydantic_settings import BaseSettings
from typing import Optional


class OAuthSettings(BaseSettings):
    # Google OAuth settings
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""  # This should be set in your .env file
    GOOGLE_REDIRECT_URI: str = ""  # Update this as needed (will be configured based on environment)
    GOOGLE_SCOPES: str = "openid email profile"

    class Config:
        env_file = ".env"


oauth_settings = OAuthSettings()