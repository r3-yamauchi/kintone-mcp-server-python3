"""Entry point for kintone MCP server."""

import asyncio
import logging
import sys

from .config import KintoneConfig, KintoneConfigError
from .server import KintoneMCPServer


# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def setup_logging(config: KintoneConfig) -> None:
    """Setup logging based on configuration."""
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def main() -> None:
    """Main entry point."""
    try:
        # Load configuration
        config = KintoneConfig()

        # Setup logging
        setup_logging(config)

        # Create and run server
        server = KintoneMCPServer(config.to_auth_config())

        # Run the async server
        asyncio.run(server.run())

    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except KintoneConfigError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
