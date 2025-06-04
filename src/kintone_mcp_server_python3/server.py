"""MCP server implementation for kintone."""

import json
import logging
from typing import Any, Dict, List, Optional

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent, ServerCapabilities
from pydantic import AnyUrl

from .auth import create_auth
from .client import KintoneClient, KintoneAPIError


logger = logging.getLogger(__name__)


class KintoneMCPServer:
    """MCP Server for kintone API."""
    
    def __init__(self, auth_config: dict):
        """Initialize the server with authentication configuration."""
        self.server = Server("kintone-mcp-server-python3")
        self.auth = create_auth(auth_config)
        self.client = KintoneClient(self.auth)
        
        # Register handlers
        self._register_handlers()
    
    def _register_handlers(self):
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
                            "app": {
                                "type": "integer",
                                "description": "The app ID"
                            },
                            "query": {
                                "type": "string",
                                "description": "Query string to filter records (optional)"
                            },
                            "fields": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of field codes to retrieve (optional)"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of records to retrieve (default: 100, max: 500)"
                            },
                            "offset": {
                                "type": "integer",
                                "description": "Offset for pagination (default: 0)"
                            }
                        },
                        "required": ["app"]
                    }
                ),
                Tool(
                    name="get_all_records",
                    description="Get all records from a kintone app (handles pagination automatically)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "app": {
                                "type": "integer",
                                "description": "The app ID"
                            },
                            "query": {
                                "type": "string",
                                "description": "Query string to filter records (optional)"
                            },
                            "fields": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of field codes to retrieve (optional)"
                            }
                        },
                        "required": ["app"]
                    }
                ),
                Tool(
                    name="get_apps",
                    description="Get kintone apps information by name or other filters",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Partial match for app name (case-insensitive)"
                            },
                            "ids": {
                                "type": "array",
                                "items": {"type": "integer"},
                                "description": "List of app IDs to retrieve"
                            },
                            "codes": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of app codes to retrieve (exact match, case-sensitive)"
                            },
                            "space_ids": {
                                "type": "array",
                                "items": {"type": "integer"},
                                "description": "List of space IDs to filter apps"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of apps to retrieve (default: 100, max: 100)"
                            },
                            "offset": {
                                "type": "integer",
                                "description": "Offset for pagination (default: 0)"
                            }
                        }
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Optional[Dict[str, Any]]) -> List[TextContent]:
            """Handle tool calls."""
            try:
                if name == "get_records":
                    result = self._get_records(arguments or {})
                elif name == "get_all_records":
                    result = self._get_all_records(arguments or {})
                elif name == "get_apps":
                    result = self._get_apps(arguments or {})
                else:
                    return [TextContent(
                        type="text",
                        text=f"Unknown tool: {name}"
                    )]
                
                return [TextContent(
                    type="text",
                    text=json.dumps(result, ensure_ascii=False, indent=2)
                )]
                
            except KintoneAPIError as e:
                error_msg = f"kintone API error: {e}"
                if e.code:
                    error_msg += f" (code: {e.code})"
                if e.errors:
                    error_msg += f"\nDetails: {json.dumps(e.errors, ensure_ascii=False)}"
                
                return [TextContent(
                    type="text",
                    text=error_msg
                )]
            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}", exc_info=True)
                return [TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]
    
    def _get_records(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get records from kintone."""
        app = arguments["app"]
        query = arguments.get("query")
        fields = arguments.get("fields")
        limit = arguments.get("limit", 100)
        offset = arguments.get("offset", 0)
        
        response = self.client.get_records(
            app=app,
            query=query,
            fields=fields,
            limit=limit,
            offset=offset
        )
        
        return {
            "records": response.records,
            "totalCount": response.totalCount
        }
    
    def _get_all_records(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get all records from kintone."""
        app = arguments["app"]
        query = arguments.get("query")
        fields = arguments.get("fields")
        
        records = self.client.get_all_records(
            app=app,
            query=query,
            fields=fields
        )
        
        return {
            "records": records,
            "totalCount": len(records)
        }
    
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
            offset=offset
        )
        
        # Convert Pydantic models to dict for JSON serialization
        apps_list = []
        for app in response.apps:
            app_dict = app.model_dump()
            apps_list.append(app_dict)
        
        return {
            "apps": apps_list,
            "count": len(apps_list)
        }
    
    async def run(self):
        """Run the MCP server."""
        from mcp.server.stdio import stdio_server
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="kintone-mcp-server-python3",
                    server_version="0.1.0",
                    capabilities=ServerCapabilities(
                        tools={}
                    )
                )
            )