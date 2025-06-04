"""Data models for kintone MCP server."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class KintoneField(BaseModel):
    """Represents a field in a kintone record."""
    type: str
    value: Any


class KintoneRecord(BaseModel):
    """Represents a kintone record."""
    id: Optional[str] = Field(None, alias="$id")
    revision: Optional[str] = Field(None, alias="$revision")
    fields: Dict[str, KintoneField] = Field(default_factory=dict)
    
    class Config:
        populate_by_name = True


class GetRecordsRequest(BaseModel):
    """Request parameters for getting records."""
    app: int
    query: Optional[str] = None
    fields: Optional[List[str]] = None
    totalCount: Optional[bool] = None
    
    class Config:
        populate_by_name = True


class GetRecordsResponse(BaseModel):
    """Response from get records API."""
    records: List[Dict[str, Any]]
    totalCount: Optional[str] = None
    
    class Config:
        populate_by_name = True


class UserInfo(BaseModel):
    """Represents user information."""
    code: str
    name: str


class AppInfo(BaseModel):
    """Represents a kintone app information."""
    appId: str
    code: str
    name: str
    description: str
    spaceId: Optional[str] = None
    threadId: Optional[str] = None
    createdAt: str
    creator: UserInfo
    modifiedAt: str
    modifier: UserInfo
    
    class Config:
        populate_by_name = True


class GetAppsRequest(BaseModel):
    """Request parameters for getting apps."""
    name: Optional[str] = None
    ids: Optional[List[int]] = None
    codes: Optional[List[str]] = None
    spaceIds: Optional[List[int]] = None
    limit: int = 100
    offset: int = 0
    
    class Config:
        populate_by_name = True


class GetAppsResponse(BaseModel):
    """Response from get apps API."""
    apps: List[AppInfo]
    
    class Config:
        populate_by_name = True