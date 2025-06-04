"""Authentication module for kintone API."""

import base64
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict


@dataclass
class AuthConfig:
    """Authentication configuration."""
    subdomain: str
    domain: str = "cybozu.com"


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
        return f"https://{self.config.subdomain}.{self.config.domain}"


class APITokenAuth(KintoneAuth):
    """API Token authentication."""
    
    def __init__(self, config: AuthConfig, api_token: str):
        super().__init__(config)
        self.api_token = api_token
    
    def get_headers(self) -> Dict[str, str]:
        """Get API Token authentication headers."""
        return {
            "X-Cybozu-API-Token": self.api_token,
            "Content-Type": "application/json"
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
        return {
            "X-Cybozu-Authorization": encoded,
            "Content-Type": "application/json"
        }


def create_auth(auth_config: dict) -> KintoneAuth:
    """Create authentication instance from configuration."""
    auth_type = auth_config.get("type", "api_token")
    subdomain = auth_config["subdomain"]
    domain = auth_config.get("domain", "cybozu.com")
    
    config = AuthConfig(subdomain=subdomain, domain=domain)
    
    if auth_type == "api_token":
        api_token = auth_config.get("api_token")
        if not api_token:
            raise ValueError("api_token is required for API Token authentication")
        return APITokenAuth(config, api_token)
    elif auth_type == "password":
        username = auth_config.get("username")
        password = auth_config.get("password")
        if not username or not password:
            raise ValueError("username and password are required for Password authentication")
        return PasswordAuth(config, username, password)
    else:
        raise ValueError(f"Unknown authentication type: {auth_type}")