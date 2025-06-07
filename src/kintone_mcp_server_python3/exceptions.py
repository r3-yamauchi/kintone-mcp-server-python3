"""Exception classes for kintone MCP server."""

from typing import Any, Dict, Optional


class KintoneError(Exception):
    """Base exception for all kintone-related errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.details = details or {}


class KintoneAPIError(KintoneError):
    """kintone API error with error code and details."""

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        errors: Optional[Dict[str, Any]] = None,
        status_code: Optional[int] = None,
    ) -> None:
        super().__init__(
            message, {"code": code, "errors": errors, "status_code": status_code}
        )
        self.code = code
        self.errors = errors
        self.status_code = status_code


class KintoneAuthError(KintoneError):
    """Authentication-related errors."""

    pass


class KintoneConfigError(KintoneError):
    """Configuration-related errors."""

    pass


class KintoneValidationError(KintoneError):
    """Input validation errors."""

    pass


class KintoneRateLimitError(KintoneAPIError):
    """Rate limit exceeded error."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
    ) -> None:
        super().__init__(message, code="RATE_LIMIT_EXCEEDED")
        self.retry_after = retry_after


class KintoneNetworkError(KintoneError):
    """Network-related errors."""

    pass
