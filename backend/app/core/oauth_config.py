from pydantic_settings import BaseSettings
from typing import Optional


class OAuthSettings(BaseSettings):
    # Google OAuth settings
    GOOGLE_CLIENT_ID: str = "91312196263-bqdjcd1dahd76cfv4jsf9t3h7bf2fi5b.apps.googleusercontent.com"
    GOOGLE_CLIENT_SECRET: str = ""  # This should be set in your .env file
    GOOGLE_REDIRECT_URI: str = "http://localhost:8002/api/v1/auth/google/callback"  # Update this as needed
    GOOGLE_SCOPES: str = "openid email profile"

    class Config:
        env_file = ".env"


oauth_settings = OAuthSettings()