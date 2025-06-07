"""Configuration management for kintone MCP server."""

from typing import Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings

from .constants import AUTH_TYPE_API_TOKEN, AUTH_TYPE_PASSWORD, DEFAULT_DOMAIN
from .exceptions import KintoneConfigError


class KintoneConfig(BaseSettings):
    """Configuration for kintone MCP server."""

    # Auth configuration
    auth_type: str = Field(
        default=AUTH_TYPE_API_TOKEN,
        description="Authentication type: api_token or password",
    )
    subdomain: str = Field(..., description="kintone subdomain")
    domain: str = Field(default=DEFAULT_DOMAIN, description="kintone domain")

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

    @validator("auth_type")
    def validate_auth_type(cls, v: str) -> str:
        """Validate authentication type."""
        if v not in [AUTH_TYPE_API_TOKEN, AUTH_TYPE_PASSWORD]:
            raise ValueError(
                f"Invalid auth_type: {v}. Must be '{AUTH_TYPE_API_TOKEN}' or '{AUTH_TYPE_PASSWORD}'"
            )
        return v

    @validator("api_token")
    def validate_api_token(cls, v: Optional[str], values: dict) -> Optional[str]:
        """Validate API token is provided when using api_token auth."""
        if values.get("auth_type") == AUTH_TYPE_API_TOKEN and not v:
            raise ValueError("api_token is required for api_token authentication")
        return v

    @validator("password")
    def validate_password_auth(cls, v: Optional[str], values: dict) -> Optional[str]:
        """Validate username and password are provided for password auth."""
        if values.get("auth_type") == AUTH_TYPE_PASSWORD:
            if not v or not values.get("username"):
                raise ValueError(
                    "Both username and password are required for password authentication"
                )
        return v

    @validator("subdomain")
    def validate_subdomain(cls, v: str) -> str:
        """Validate subdomain format."""
        if not v or not v.strip():
            raise ValueError("subdomain cannot be empty")
        # Remove any protocol or domain parts if accidentally included
        v = v.strip()
        if "://" in v:
            v = v.split("://")[-1]
        if "." in v:
            v = v.split(".")[0]
        return v

    def to_auth_config(self) -> dict:
        """Convert to auth configuration dict."""
        config = {
            "type": self.auth_type,
            "subdomain": self.subdomain,
            "domain": self.domain,
        }

        if self.auth_type == AUTH_TYPE_API_TOKEN:
            config["api_token"] = self.api_token
        else:
            config["username"] = self.username
            config["password"] = self.password

        return config


def load_config() -> KintoneConfig:
    """Load configuration from environment variables and .env file."""
    try:
        return KintoneConfig()
    except Exception as e:
        raise KintoneConfigError(f"Failed to load configuration: {str(e)}")
