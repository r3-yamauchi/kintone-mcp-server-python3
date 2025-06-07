"""Data models for kintone MCP server."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class KintoneField(BaseModel):
    """Represents a field in a kintone record."""

    type: str
    value: Any


class KintoneRecord(BaseModel):
    """Represents a kintone record."""

    id: Optional[str] = Field(None, alias="$id")
    revision: Optional[str] = Field(None, alias="$revision")
    fields: Dict[str, KintoneField] = Field(default_factory=dict)

    model_config = ConfigDict(populate_by_name=True)


class GetRecordsRequest(BaseModel):
    """Request parameters for getting records."""

    app: int
    query: Optional[str] = None
    fields: Optional[List[str]] = None
    totalCount: Optional[bool] = None

    model_config = ConfigDict(populate_by_name=True)


class GetRecordsResponse(BaseModel):
    """Response from get records API."""

    records: List[Dict[str, Any]]
    totalCount: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


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

    model_config = ConfigDict(populate_by_name=True)


class GetAppsRequest(BaseModel):
    """Request parameters for getting apps."""

    name: Optional[str] = None
    ids: Optional[List[int]] = None
    codes: Optional[List[str]] = None
    spaceIds: Optional[List[int]] = None
    limit: int = 100
    offset: int = 0

    model_config = ConfigDict(populate_by_name=True)


class GetAppsResponse(BaseModel):
    """Response from get apps API."""

    apps: List[AppInfo]

    model_config = ConfigDict(populate_by_name=True)


# Single record models
class GetRecordRequest(BaseModel):
    """Request for getting a single record."""

    app: int
    id: int


class GetRecordResponse(BaseModel):
    """Response from get record API."""

    record: Dict[str, Any]


# Record creation models
class AddRecordRequest(BaseModel):
    """Request for adding a single record."""

    app: int
    record: Dict[str, Dict[str, Any]]


class AddRecordResponse(BaseModel):
    """Response from add record API."""

    id: str
    revision: str


class AddRecordsRequest(BaseModel):
    """Request for adding multiple records."""

    app: int
    records: List[Dict[str, Dict[str, Any]]]


class AddRecordsResponse(BaseModel):
    """Response from add records API."""

    ids: List[str]
    revisions: List[str]


# Record update models
class UpdateRecordRequest(BaseModel):
    """Request for updating a single record."""

    app: int
    id: Optional[int] = None
    updateKey: Optional[Dict[str, Any]] = None
    revision: Optional[int] = None
    record: Dict[str, Dict[str, Any]]


class UpdateRecordResponse(BaseModel):
    """Response from update record API."""

    revision: str


class UpdateRecordData(BaseModel):
    """Data for updating a record in batch."""

    id: Optional[int] = None
    updateKey: Optional[Dict[str, Any]] = None
    revision: Optional[int] = None
    record: Dict[str, Dict[str, Any]]


class UpdateRecordsRequest(BaseModel):
    """Request for updating multiple records."""

    app: int
    records: List[UpdateRecordData]


class UpdateRecordsResponse(BaseModel):
    """Response from update records API."""

    records: List[Dict[str, str]]  # List of {id, revision}


# Record comment models
class Comment(BaseModel):
    """Represents a comment."""

    id: str
    text: str
    createdAt: str
    creator: UserInfo
    mentions: List[Dict[str, Any]] = Field(default_factory=list)


class GetCommentsRequest(BaseModel):
    """Request for getting comments."""

    app: int
    record: int
    order: Optional[str] = "desc"
    offset: Optional[int] = 0
    limit: Optional[int] = 10


class GetCommentsResponse(BaseModel):
    """Response from get comments API."""

    comments: List[Comment]
    older: bool
    newer: bool


class CommentContent(BaseModel):
    """Content for adding a comment."""

    text: str
    mentions: Optional[List[Dict[str, Any]]] = None


class AddCommentRequest(BaseModel):
    """Request for adding a comment."""

    app: int
    record: int
    comment: CommentContent


class AddCommentResponse(BaseModel):
    """Response from add comment API."""

    id: str


# Record status models
class UpdateStatusRequest(BaseModel):
    """Request for updating record status."""

    app: int
    id: int
    action: str
    assignee: Optional[str] = None
    revision: Optional[int] = None


class UpdateStatusResponse(BaseModel):
    """Response from update status API."""

    revision: str


class UpdateStatusesRequest(BaseModel):
    """Request for updating multiple record statuses."""

    app: int
    records: List[Dict[str, Any]]


class UpdateStatusesResponse(BaseModel):
    """Response from update statuses API."""

    records: List[Dict[str, str]]  # List of {id, revision}


# File models
class FileUploadResponse(BaseModel):
    """Response from file upload API."""

    fileKey: str


class FileDownloadRequest(BaseModel):
    """Request for downloading a file."""

    fileKey: str


# App settings models
class GetAppRequest(BaseModel):
    """Request for getting app info."""

    id: int


class GetAppResponse(BaseModel):
    """Response from get app API."""

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


class GetFormFieldsRequest(BaseModel):
    """Request for getting form fields."""

    app: int
    lang: Optional[str] = None


class GetFormFieldsResponse(BaseModel):
    """Response from get form fields API."""

    properties: Dict[str, Any]
    revision: str
