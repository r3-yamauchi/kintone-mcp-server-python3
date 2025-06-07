"""Tool definitions for kintone MCP server."""

from typing import Dict, Any

# Tool definitions registry
TOOLS = {
    "get_records": {
        "description": "Get records from a kintone app",
        "handler": "_get_records",
        "schema": {
            "type": "object",
            "properties": {
                "app": {"type": "integer", "description": "The app ID"},
                "query": {
                    "type": "string",
                    "description": "Query string to filter records (optional)",
                },
                "fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of field codes to retrieve (optional)",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of records to retrieve (default: 100, max: 500)",
                },
                "offset": {
                    "type": "integer",
                    "description": "Offset for pagination (default: 0)",
                },
            },
            "required": ["app"],
        },
    },
    "get_all_records": {
        "description": "Get all records from a kintone app (handles pagination automatically)",
        "handler": "_get_all_records",
        "schema": {
            "type": "object",
            "properties": {
                "app": {"type": "integer", "description": "The app ID"},
                "query": {
                    "type": "string",
                    "description": "Query string to filter records (optional)",
                },
                "fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of field codes to retrieve (optional)",
                },
            },
            "required": ["app"],
        },
    },
    "get_apps": {
        "description": "Get kintone apps information by name or other filters",
        "handler": "_get_apps",
        "schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Partial match for app name (case-insensitive)",
                },
                "ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "List of app IDs to retrieve",
                },
                "codes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of app codes to retrieve (exact match, case-sensitive)",
                },
                "space_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "List of space IDs to filter apps",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of apps to retrieve (default: 100, max: 100)",
                },
                "offset": {
                    "type": "integer",
                    "description": "Offset for pagination (default: 0)",
                },
            },
        },
    },
    "get_record": {
        "description": "Get a single record from a kintone app",
        "handler": "_get_record",
        "schema": {
            "type": "object",
            "properties": {
                "app": {"type": "integer", "description": "The app ID"},
                "id": {"type": "integer", "description": "The record ID"},
            },
            "required": ["app", "id"],
        },
    },
    "add_record": {
        "description": "Add a single record to a kintone app",
        "handler": "_add_record",
        "schema": {
            "type": "object",
            "properties": {
                "app": {"type": "integer", "description": "The app ID"},
                "record": {
                    "type": "object",
                    "description": "Record data with field codes as keys and objects with 'value' property",
                },
            },
            "required": ["app", "record"],
        },
    },
    "add_records": {
        "description": "Add multiple records to a kintone app (max 100 records)",
        "handler": "_add_records",
        "schema": {
            "type": "object",
            "properties": {
                "app": {"type": "integer", "description": "The app ID"},
                "records": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Array of record data (max 100)",
                },
            },
            "required": ["app", "records"],
        },
    },
    "update_record": {
        "description": "Update a single record in a kintone app",
        "handler": "_update_record",
        "schema": {
            "type": "object",
            "properties": {
                "app": {"type": "integer", "description": "The app ID"},
                "id": {
                    "type": "integer",
                    "description": "The record ID (either id or update_key required)",
                },
                "update_key": {
                    "type": "object",
                    "description": "Update key field and value (either id or update_key required)",
                },
                "record": {
                    "type": "object",
                    "description": "Record data with field codes to update",
                },
                "revision": {
                    "type": "integer",
                    "description": "Expected revision number (optional, for optimistic locking)",
                },
            },
            "required": ["app", "record"],
        },
    },
    "update_records": {
        "description": "Update multiple records in a kintone app (max 100 records)",
        "handler": "_update_records",
        "schema": {
            "type": "object",
            "properties": {
                "app": {"type": "integer", "description": "The app ID"},
                "records": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "updateKey": {"type": "object"},
                            "revision": {"type": "integer"},
                            "record": {"type": "object"},
                        },
                    },
                    "description": "Array of update data (max 100)",
                },
            },
            "required": ["app", "records"],
        },
    },
    "get_comments": {
        "description": "Get comments for a record",
        "handler": "_get_comments",
        "schema": {
            "type": "object",
            "properties": {
                "app": {"type": "integer", "description": "The app ID"},
                "record": {
                    "type": "integer",
                    "description": "The record ID",
                },
                "order": {
                    "type": "string",
                    "enum": ["asc", "desc"],
                    "description": "Sort order (default: desc)",
                },
                "offset": {
                    "type": "integer",
                    "description": "Offset for pagination",
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of comments to retrieve (max 10)",
                },
            },
            "required": ["app", "record"],
        },
    },
    "add_comment": {
        "description": "Add a comment to a record",
        "handler": "_add_comment",
        "schema": {
            "type": "object",
            "properties": {
                "app": {"type": "integer", "description": "The app ID"},
                "record": {
                    "type": "integer",
                    "description": "The record ID",
                },
                "text": {"type": "string", "description": "Comment text"},
                "mentions": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Array of mention objects (optional)",
                },
            },
            "required": ["app", "record", "text"],
        },
    },
    "update_status": {
        "description": "Update the status of a record",
        "handler": "_update_status",
        "schema": {
            "type": "object",
            "properties": {
                "app": {"type": "integer", "description": "The app ID"},
                "id": {"type": "integer", "description": "The record ID"},
                "action": {
                    "type": "string",
                    "description": "The action name",
                },
                "assignee": {
                    "type": "string",
                    "description": "The login name of the assignee (optional)",
                },
                "revision": {
                    "type": "integer",
                    "description": "Expected revision number (optional)",
                },
            },
            "required": ["app", "id", "action"],
        },
    },
    "update_statuses": {
        "description": "Update the status of multiple records (max 100)",
        "handler": "_update_statuses",
        "schema": {
            "type": "object",
            "properties": {
                "app": {"type": "integer", "description": "The app ID"},
                "records": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "action": {"type": "string"},
                            "assignee": {"type": "string"},
                            "revision": {"type": "integer"},
                        },
                    },
                    "description": "Array of status update data",
                },
            },
            "required": ["app", "records"],
        },
    },
    "upload_file": {
        "description": "Upload a file to kintone",
        "handler": "_upload_file",
        "schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to upload",
                }
            },
            "required": ["file_path"],
        },
    },
    "download_file": {
        "description": "Download a file from kintone",
        "handler": "_download_file",
        "schema": {
            "type": "object",
            "properties": {
                "file_key": {
                    "type": "string",
                    "description": "The file key",
                },
                "save_path": {
                    "type": "string",
                    "description": "Path where to save the file",
                },
            },
            "required": ["file_key", "save_path"],
        },
    },
    "get_app": {
        "description": "Get app information",
        "handler": "_get_app",
        "schema": {
            "type": "object",
            "properties": {"id": {"type": "integer", "description": "The app ID"}},
            "required": ["id"],
        },
    },
    "get_form_fields": {
        "description": "Get form fields configuration",
        "handler": "_get_form_fields",
        "schema": {
            "type": "object",
            "properties": {
                "app": {"type": "integer", "description": "The app ID"},
                "lang": {
                    "type": "string",
                    "description": "Language code (e.g., 'en', 'ja')",
                },
            },
            "required": ["app"],
        },
    },
}


def get_tool_definitions() -> Dict[str, Any]:
    """Get all tool definitions."""
    return TOOLS
