"""Authentication module for kintone API."""

import base64
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any

from .constants import (
    CONTENT_TYPE_JSON,
    HEADER_API_TOKEN,
    HEADER_AUTH,
    HEADER_CONTENT_TYPE,
)
from .exceptions import KintoneAuthError


@dataclass
class AuthConfig:
    """Authentication configuration."""

    domain: str


class KintoneAuth(ABC):
    """Base class for kintone authentication."""

    def __init__(self, config: AuthConfig):
        self.config = config

    @abstractmethod
    def get_headers(self) -> Dict[str, str]:
        """Get authentication headers."""
        pass

    def get_base_url(self) -> str:
        """Get the base URL for kintone API."""
        return f"https://{self.config.domain}"


class APITokenAuth(KintoneAuth):
    """API Token authentication."""

    def __init__(self, config: AuthConfig, api_token: str):
        super().__init__(config)
        self.api_token = api_token

    def get_headers(self) -> Dict[str, str]:
        """Get API Token authentication headers."""
        return {
            HEADER_API_TOKEN: self.api_token,
            HEADER_CONTENT_TYPE: CONTENT_TYPE_JSON,
        }


class PasswordAuth(KintoneAuth):
    """Username/Password authentication."""

    def __init__(self, config: AuthConfig, username: str, password: str):
        super().__init__(config)
        self.username = username
        self.password = password

    def get_headers(self) -> Dict[str, str]:
        """Get Password authentication headers."""
        auth_string = f"{self.username}:{self.password}"
        encoded = base64.b64encode(auth_string.encode()).decode()
        return {HEADER_AUTH: encoded, HEADER_CONTENT_TYPE: CONTENT_TYPE_JSON}


def create_auth(auth_config: Dict[str, Any]) -> KintoneAuth:
    """Create authentication instance from configuration."""
    auth_type = auth_config["type"]
    domain = auth_config["domain"]

    config = AuthConfig(domain=domain)

    if auth_type == "api_token":
        api_token = auth_config.get("api_token")
        if not api_token:
            raise KintoneAuthError("api_token is required for API Token authentication")
        return APITokenAuth(config, api_token)
    elif auth_type == "password":
        username = auth_config.get("username")
        password = auth_config.get("password")
        if not username or not password:
            raise KintoneAuthError(
                "username and password are required for Password authentication"
            )
        return PasswordAuth(config, username, password)
    else:
        raise KintoneAuthError(f"Unknown authentication type: {auth_type}")
