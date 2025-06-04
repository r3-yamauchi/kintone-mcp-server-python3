"""Entry point for kintone MCP server."""

import asyncio
import logging
import os
import sys
from typing import Dict, Any

from dotenv import load_dotenv

from .server import KintoneMCPServer


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config() -> Dict[str, Any]:
    """Load configuration from environment variables."""
    # Load .env file if exists
    load_dotenv()
    
    # Load from environment variables
    auth_type = os.environ.get("KINTONE_AUTH_TYPE", "api_token")
    subdomain = os.environ.get("KINTONE_SUBDOMAIN")
    
    if not subdomain:
        raise ValueError("KINTONE_SUBDOMAIN environment variable is required")
    
    config = {
        "auth": {
            "type": auth_type,
            "subdomain": subdomain,
            "domain": os.environ.get("KINTONE_DOMAIN", "cybozu.com")
        }
    }
    
    if auth_type == "api_token":
        api_token = os.environ.get("KINTONE_API_TOKEN")
        if not api_token:
            raise ValueError("KINTONE_API_TOKEN environment variable is required for API token authentication")
        config["auth"]["api_token"] = api_token
    
    elif auth_type == "password":
        username = os.environ.get("KINTONE_USERNAME")
        password = os.environ.get("KINTONE_PASSWORD")
        if not username or not password:
            raise ValueError("KINTONE_USERNAME and KINTONE_PASSWORD environment variables are required for password authentication")
        config["auth"]["username"] = username
        config["auth"]["password"] = password
    
    else:
        raise ValueError(f"Unknown authentication type: {auth_type}")
    
    return config


def main():
    """Main entry point."""
    try:
        # Load configuration
        config = load_config()
        
        # Create and run server
        server = KintoneMCPServer(config["auth"])
        
        # Run the async server
        asyncio.run(server.run())
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()