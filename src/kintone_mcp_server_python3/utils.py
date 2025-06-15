"""Utility functions for kintone MCP server."""

from pathlib import Path
from typing import Any, Dict, Optional

from .exceptions import KintoneValidationError


def validate_file_path(path: str, must_exist: bool = False) -> Path:
    """Validate and sanitize file path.

    Args:
        path: File path to validate
        must_exist: Whether the file must exist

    Returns:
        Validated Path object

    Raises:
        KintoneValidationError: If path is invalid
    """
    try:
        p = Path(path)

        # Check for path traversal attempts
        if ".." in p.parts:
            raise KintoneValidationError("Path traversal not allowed")

        # Ensure absolute path
        if not p.is_absolute():
            raise KintoneValidationError("Must use absolute paths")

        # Check existence if required
        if must_exist and not p.exists():
            raise KintoneValidationError(f"File not found: {path}")

        return p
    except Exception as e:
        if isinstance(e, KintoneValidationError):
            raise
        raise KintoneValidationError(f"Invalid file path: {str(e)}")


def validate_app_id(app_id: Any) -> int:
    """Validate app ID.

    Args:
        app_id: App ID to validate

    Returns:
        Validated app ID as integer

    Raises:
        KintoneValidationError: If app ID is invalid
    """
    try:
        app_id = int(app_id)
        if app_id <= 0:
            raise ValueError("App ID must be positive")
        return app_id
    except (TypeError, ValueError) as e:
        raise KintoneValidationError(f"Invalid app ID: {str(e)}")


def validate_record_id(record_id: Any) -> int:
    """Validate record ID.

    Args:
        record_id: Record ID to validate

    Returns:
        Validated record ID as integer

    Raises:
        KintoneValidationError: If record ID is invalid
    """
    try:
        record_id = int(record_id)
        if record_id <= 0:
            raise ValueError("Record ID must be positive")
        return record_id
    except (TypeError, ValueError) as e:
        raise KintoneValidationError(f"Invalid record ID: {str(e)}")


def validate_limit(limit: Any, max_limit: int) -> int:
    """Validate limit parameter.

    Args:
        limit: Limit value to validate
        max_limit: Maximum allowed limit

    Returns:
        Validated limit as integer

    Raises:
        KintoneValidationError: If limit is invalid
    """
    try:
        limit = int(limit)
        if limit <= 0:
            raise ValueError("Limit must be positive")
        if limit > max_limit:
            raise ValueError(f"Limit exceeds maximum of {max_limit}")
        return limit
    except (TypeError, ValueError) as e:
        raise KintoneValidationError(f"Invalid limit: {str(e)}")


def sanitize_query(query: Optional[str]) -> Optional[str]:
    """Sanitize query string to prevent injection.

    Args:
        query: Query string to sanitize

    Returns:
        Sanitized query string
    """
    if not query:
        return None

    # Basic sanitization - remove dangerous characters
    # This is a simple implementation; consider using a proper query parser
    dangerous_chars = [";", "--", "/*", "*/", "xp_", "sp_"]
    sanitized = query

    for char in dangerous_chars:
        if char in sanitized:
            sanitized = sanitized.replace(char, "")

    return sanitized.strip()


def parse_kintone_query(
    query: Optional[str], 
    default_limit: Optional[int] = None,
    default_offset: Optional[int] = None
) -> Dict[str, Any]:
    """Parse kintone query to extract order by, limit, and offset clauses.
    
    Args:
        query: The kintone query string
        default_limit: Default limit to use if not specified in query
        default_offset: Default offset to use if not specified in query
        
    Returns:
        Dict containing:
            - base_query: Query without order by, limit, offset clauses
            - order_by: Order by clause if present
            - limit: Limit value (from query or default)
            - offset: Offset value (from query or default)
    """
    import re
    
    if not query:
        return {
            "base_query": "",
            "order_by": None,
            "limit": default_limit,
            "offset": default_offset
        }
    
    # Pattern to match order by clause (case insensitive)
    order_pattern = r'\s+order\s+by\s+([^\s]+(?:\s+(?:asc|desc))?(?:\s*,\s*[^\s]+(?:\s+(?:asc|desc))?)*)'
    
    # Pattern to match limit clause (case insensitive)
    limit_pattern = r'\s+limit\s+(\d+)'
    
    # Pattern to match offset clause (case insensitive)
    offset_pattern = r'\s+offset\s+(\d+)'
    
    # Extract order by clause
    order_match = re.search(order_pattern, query, re.IGNORECASE)
    order_by = order_match.group(0).strip() if order_match else None
    
    # Extract limit
    limit_match = re.search(limit_pattern, query, re.IGNORECASE)
    query_limit = int(limit_match.group(1)) if limit_match else None
    
    # Extract offset
    offset_match = re.search(offset_pattern, query, re.IGNORECASE)
    query_offset = int(offset_match.group(1)) if offset_match else None
    
    # Remove order by, limit, and offset from query
    base_query = query
    if order_match:
        base_query = base_query[:order_match.start()] + base_query[order_match.end():]
    
    # Remove limit and offset in reverse order to maintain indices
    for pattern in [offset_pattern, limit_pattern]:
        match = re.search(pattern, base_query, re.IGNORECASE)
        if match:
            base_query = base_query[:match.start()] + base_query[match.end():]
    
    base_query = base_query.strip()
    
    # Determine final limit (use smaller value if both are specified)
    final_limit = default_limit
    if query_limit is not None and default_limit is not None:
        final_limit = min(query_limit, default_limit)
    elif query_limit is not None:
        final_limit = query_limit
    
    # Determine final offset (use query offset if specified)
    final_offset = query_offset if query_offset is not None else default_offset
    
    return {
        "base_query": base_query,
        "order_by": order_by,
        "limit": final_limit,
        "offset": final_offset
    }


def format_error_response(error: Exception) -> Dict[str, Any]:
    """Format error for response.

    Args:
        error: Exception to format

    Returns:
        Formatted error dict
    """
    from .exceptions import KintoneAPIError, KintoneError

    if isinstance(error, KintoneAPIError):
        response = {
            "error": str(error),
            "code": error.code,
            "details": error.errors,
        }
        if error.status_code:
            response["status_code"] = error.status_code
        return response
    elif isinstance(error, KintoneError):
        return {
            "error": str(error),
            "details": error.details,
        }
    else:
        return {
            "error": str(error),
            "type": type(error).__name__,
        }
