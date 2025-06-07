"""Configuration management for kintone MCP server."""

from typing import Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings

from .constants import AUTH_TYPE_API_TOKEN, AUTH_TYPE_PASSWORD
from .exceptions import KintoneConfigError


class KintoneConfig(BaseSettings):
    """Configuration for kintone MCP server."""

    # Auth configuration
    domain: str = Field(..., description="kintone domain (e.g., dev-demo.cybozu.com)")

    # API Token auth
    api_token: Optional[str] = Field(None, description="API token for authentication")

    # Password auth
    username: Optional[str] = Field(
        None, description="Username for password authentication"
    )
    password: Optional[str] = Field(
        None, description="Password for password authentication"
    )

    # Server configuration
    log_level: str = Field(default="INFO", description="Logging level")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum number of retries")

    class Config:
        env_prefix = "KINTONE_"
        env_file = ".env"
        env_file_encoding = "utf-8"

    @validator("domain")
    def validate_domain(cls, v: str) -> str:
        """Validate domain format."""
        if not v or not v.strip():
            raise ValueError("domain cannot be empty")
        # Remove any protocol if accidentally included
        v = v.strip()
        if "://" in v:
            v = v.split("://")[-1]
        # Remove trailing slash if present
        if v.endswith("/"):
            v = v.rstrip("/")
        return v

    @validator("api_token")
    def validate_api_token(cls, v: Optional[str], values: dict) -> Optional[str]:
        """Validate API token format."""
        # API token can contain up to 9 comma-separated tokens
        if v and v.strip():
            # Just ensure it's not empty after stripping
            return v.strip()
        return v

    @validator("password")
    def validate_auth_credentials(cls, v: Optional[str], values: dict) -> Optional[str]:
        """Validate authentication credentials."""
        username = values.get("username")
        api_token = values.get("api_token")
        
        # If both username and password are provided, use password auth
        # If neither username/password nor api_token is provided, raise error
        if not username and not v and not api_token:
            raise ValueError(
                "Either username and password, or api_token must be provided"
            )
        
        # If username is provided but password is missing
        if username and not v:
            raise ValueError(
                "Password is required when username is provided"
            )
        
        return v

    def get_auth_type(self) -> str:
        """Determine authentication type based on provided credentials."""
        # If both username and password are provided, use password auth
        if self.username and self.password:
            return AUTH_TYPE_PASSWORD
        # Otherwise, use API token auth if api_token is provided
        elif self.api_token:
            return AUTH_TYPE_API_TOKEN
        else:
            raise KintoneConfigError(
                "No valid authentication credentials provided. "
                "Please provide either username and password, or api_token."
            )

    def to_auth_config(self) -> dict:
        """Convert to auth configuration dict."""
        auth_type = self.get_auth_type()
        config = {
            "type": auth_type,
            "domain": self.domain,
        }

        if auth_type == AUTH_TYPE_API_TOKEN:
            if self.api_token:
                config["api_token"] = self.api_token
        else:
            if self.username:
                config["username"] = self.username
            if self.password:
                config["password"] = self.password

        return config


def load_config() -> KintoneConfig:
    """Load configuration from environment variables and .env file."""
    try:
        return KintoneConfig()
    except Exception as e:
        raise KintoneConfigError(f"Failed to load configuration: {str(e)}")
