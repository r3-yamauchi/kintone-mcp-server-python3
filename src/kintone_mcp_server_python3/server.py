"""MCP server implementation for kintone."""

import json
import logging
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent, ServerCapabilities, ToolsCapability

from .auth import create_auth, KintoneAuth
from .client import KintoneClient, KintoneAPIError
from .models import CommentContent, UpdateRecordData
from .query_language import get_query_language_documentation


logger = logging.getLogger(__name__)


class KintoneMCPServer:
    """MCP Server for kintone API."""

    def __init__(self, auth_config: Dict[str, Any]) -> None:
        """Initialize the server with authentication configuration."""
        self.server: Server = Server("kintone-mcp-server-python3")
        self.auth: KintoneAuth = create_auth(auth_config)
        self.client: KintoneClient = KintoneClient(self.auth)

        # Register handlers
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Register MCP protocol handlers."""

        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="get_records",
                    description="Get records from a kintone app",
                    inputSchema={
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
                ),
                Tool(
                    name="get_all_records",
                    description="Get all records from a kintone app (handles pagination automatically)",
                    inputSchema={
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
                ),
                Tool(
                    name="get_apps",
                    description="Get kintone apps information by name or other filters",
                    inputSchema={
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
                ),
                Tool(
                    name="get_record",
                    description="Get a single record from a kintone app",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "app": {"type": "integer", "description": "The app ID"},
                            "id": {"type": "integer", "description": "The record ID"},
                        },
                        "required": ["app", "id"],
                    },
                ),
                Tool(
                    name="add_record",
                    description="Add a single record to a kintone app",
                    inputSchema={
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
                ),
                Tool(
                    name="add_records",
                    description="Add multiple records to a kintone app (max 100 records)",
                    inputSchema={
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
                ),
                Tool(
                    name="update_record",
                    description="Update a single record in a kintone app",
                    inputSchema={
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
                ),
                Tool(
                    name="update_records",
                    description="Update multiple records in a kintone app (max 100 records)",
                    inputSchema={
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
                ),
                Tool(
                    name="get_comments",
                    description="Get comments for a record",
                    inputSchema={
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
                ),
                Tool(
                    name="add_comment",
                    description="Add a comment to a record",
                    inputSchema={
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
                ),
                Tool(
                    name="update_status",
                    description="Update the status of a record",
                    inputSchema={
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
                ),
                Tool(
                    name="update_statuses",
                    description="Update the status of multiple records (max 100)",
                    inputSchema={
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
                ),
                Tool(
                    name="upload_file",
                    description="Upload a file to kintone",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file to upload",
                            }
                        },
                        "required": ["file_path"],
                    },
                ),
                Tool(
                    name="download_file",
                    description="Download a file from kintone",
                    inputSchema={
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
                ),
                Tool(
                    name="get_app",
                    description="Get app information",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer", "description": "The app ID"}
                        },
                        "required": ["id"],
                    },
                ),
                Tool(
                    name="get_form_fields",
                    description="Get form fields configuration",
                    inputSchema={
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
                ),
                Tool(
                    name="get_query_language_doc",
                    description="Get comprehensive documentation about kintone query language syntax",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
            ]

        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: Optional[Dict[str, Any]]
        ) -> List[TextContent]:
            """Handle tool calls."""
            try:
                if name == "get_records":
                    result = self._get_records(arguments or {})
                elif name == "get_all_records":
                    result = self._get_all_records(arguments or {})
                elif name == "get_apps":
                    result = self._get_apps(arguments or {})
                elif name == "get_record":
                    result = self._get_record(arguments or {})
                elif name == "add_record":
                    result = self._add_record(arguments or {})
                elif name == "add_records":
                    result = self._add_records(arguments or {})
                elif name == "update_record":
                    result = self._update_record(arguments or {})
                elif name == "update_records":
                    result = self._update_records(arguments or {})
                elif name == "get_comments":
                    result = self._get_comments(arguments or {})
                elif name == "add_comment":
                    result = self._add_comment(arguments or {})
                elif name == "update_status":
                    result = self._update_status(arguments or {})
                elif name == "update_statuses":
                    result = self._update_statuses(arguments or {})
                elif name == "upload_file":
                    result = self._upload_file(arguments or {})
                elif name == "download_file":
                    result = self._download_file(arguments or {})
                elif name == "get_app":
                    result = self._get_app(arguments or {})
                elif name == "get_form_fields":
                    result = self._get_form_fields(arguments or {})
                elif name == "get_query_language_doc":
                    result = self._get_query_language_doc(arguments or {})
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]

                return [
                    TextContent(
                        type="text",
                        text=json.dumps(result, ensure_ascii=False, indent=2),
                    )
                ]

            except KintoneAPIError as e:
                error_msg = f"kintone API error: {e}"
                if e.code:
                    error_msg += f" (code: {e.code})"
                if e.errors:
                    error_msg += (
                        f"\nDetails: {json.dumps(e.errors, ensure_ascii=False)}"
                    )

                return [TextContent(type="text", text=error_msg)]
            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}", exc_info=True)
                return [TextContent(type="text", text=f"Error: {str(e)}")]

    def _get_records(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get records from kintone."""
        app = arguments["app"]
        query = arguments.get("query")
        fields = arguments.get("fields")
        limit = arguments.get("limit", 100)
        offset = arguments.get("offset", 0)

        response = self.client.get_records(
            app=app, query=query, fields=fields, limit=limit, offset=offset
        )

        return {"records": response.records, "totalCount": response.totalCount}

    def _get_all_records(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get all records from kintone."""
        app = arguments["app"]
        query = arguments.get("query")
        fields = arguments.get("fields")

        records = self.client.get_all_records(app=app, query=query, fields=fields)

        return {"records": records, "totalCount": len(records)}

    def _get_apps(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get apps information from kintone."""
        name = arguments.get("name")
        ids = arguments.get("ids")
        codes = arguments.get("codes")
        space_ids = arguments.get("space_ids")
        limit = arguments.get("limit", 100)
        offset = arguments.get("offset", 0)

        response = self.client.get_apps(
            name=name,
            ids=ids,
            codes=codes,
            space_ids=space_ids,
            limit=limit,
            offset=offset,
        )

        # Convert Pydantic models to dict for JSON serialization
        apps_list = []
        for app in response.apps:
            app_dict = app.model_dump()
            apps_list.append(app_dict)

        return {"apps": apps_list, "count": len(apps_list)}

    def _get_record(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get a single record from kintone."""
        app = arguments["app"]
        id = arguments["id"]

        response = self.client.get_record(app=app, id=id)
        return {"record": response.record}

    def _add_record(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Add a single record to kintone."""
        app = arguments["app"]
        record = arguments["record"]

        response = self.client.add_record(app=app, record=record)
        return {"id": response.id, "revision": response.revision}

    def _add_records(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Add multiple records to kintone."""
        app = arguments["app"]
        records = arguments["records"]

        response = self.client.add_records(app=app, records=records)
        return {"ids": response.ids, "revisions": response.revisions}

    def _update_record(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Update a single record in kintone."""
        app = arguments["app"]
        record = arguments["record"]
        id = arguments.get("id")
        update_key = arguments.get("update_key")
        revision = arguments.get("revision")

        response = self.client.update_record(
            app=app, record=record, id=id, update_key=update_key, revision=revision
        )
        return {"revision": response.revision}

    def _update_records(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Update multiple records in kintone."""
        app = arguments["app"]
        records_data = arguments["records"]

        # Convert dict to UpdateRecordData objects
        records = []
        for rec in records_data:
            records.append(UpdateRecordData(**rec))

        response = self.client.update_records(app=app, records=records)
        return {"records": response.records}

    def _get_comments(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get comments for a record."""
        app = arguments["app"]
        record = arguments["record"]
        order = arguments.get("order", "desc")
        offset = arguments.get("offset", 0)
        limit = arguments.get("limit", 10)

        response = self.client.get_comments(
            app=app, record=record, order=order, offset=offset, limit=limit
        )

        # Convert Comment objects to dicts
        comments = []
        for comment in response.comments:
            comments.append(comment.model_dump())

        return {"comments": comments, "older": response.older, "newer": response.newer}

    def _add_comment(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Add a comment to a record."""
        app = arguments["app"]
        record = arguments["record"]
        text = arguments["text"]
        mentions = arguments.get("mentions")

        comment = CommentContent(text=text, mentions=mentions)
        response = self.client.add_comment(app=app, record=record, comment=comment)
        return {"id": response.id}

    def _update_status(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Update the status of a record."""
        app = arguments["app"]
        id = arguments["id"]
        action = arguments["action"]
        assignee = arguments.get("assignee")
        revision = arguments.get("revision")

        response = self.client.update_status(
            app=app, id=id, action=action, assignee=assignee, revision=revision
        )
        return {"revision": response.revision}

    def _update_statuses(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Update the status of multiple records."""
        app = arguments["app"]
        records = arguments["records"]

        response = self.client.update_statuses(app=app, records=records)
        return {"records": response.records}

    def _upload_file(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Upload a file to kintone."""
        file_path = arguments["file_path"]

        response = self.client.upload_file(file_path=file_path)
        return {"fileKey": response.fileKey}

    def _download_file(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Download a file from kintone."""
        file_key = arguments["file_key"]
        save_path = arguments["save_path"]

        file_data = self.client.download_file(file_key=file_key)

        # Save the file
        with open(save_path, "wb") as f:
            f.write(file_data)

        return {"saved_to": save_path, "size": len(file_data)}

    def _get_app(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get app information."""
        id = arguments["id"]

        response = self.client.get_app(id=id)
        return response.model_dump()

    def _get_form_fields(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get form fields configuration."""
        app = arguments["app"]
        lang = arguments.get("lang")

        response = self.client.get_form_fields(app=app, lang=lang)
        return {"properties": response.properties, "revision": response.revision}

    def _get_query_language_doc(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get query language documentation."""
        return {"documentation": get_query_language_documentation()}

    async def run(self) -> None:
        """Run the MCP server."""
        from mcp.server.stdio import stdio_server

        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="kintone-mcp-server-python3",
                    server_version="0.1.0",
                    capabilities=ServerCapabilities(tools=ToolsCapability()),
                ),
            )
