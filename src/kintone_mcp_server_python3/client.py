"""kintone API client."""

import json
from typing import Any, Dict, List, Optional
import requests
from requests.exceptions import RequestException

from .auth import KintoneAuth
from .constants import (
    HEADER_METHOD_OVERRIDE,
    MAX_APPS_PER_REQUEST,
    MAX_BATCH_RECORDS,
    MAX_COMMENTS_PER_REQUEST,
    MAX_RECORDS_PER_REQUEST,
)
from .exceptions import KintoneAPIError, KintoneNetworkError, KintoneValidationError
from .models import (
    GetRecordsResponse,
    GetAppsResponse,
    GetRecordResponse,
    AddRecordResponse,
    AddRecordsResponse,
    UpdateRecordResponse,
    UpdateRecordsResponse,
    UpdateRecordData,
    GetCommentsResponse,
    AddCommentResponse,
    CommentContent,
    UpdateStatusResponse,
    UpdateStatusesResponse,
    FileUploadResponse,
    GetAppResponse,
    GetFormFieldsResponse,
)


class KintoneClient:
    """Client for kintone REST API."""

    def __init__(self, auth: KintoneAuth):
        self.auth = auth
        self.base_url = auth.get_base_url()
        self.headers = auth.get_headers()

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to kintone API."""
        url = f"{self.base_url}/k/v1{endpoint}"

        # Merge headers
        headers = self.headers.copy()
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))

        # Use POST method with X-HTTP-Method-Override header
        headers[HEADER_METHOD_OVERRIDE] = method

        # Convert params to JSON body for POST request
        # All requests to kintone API should use POST method
        if "params" in kwargs:
            # Move URL parameters to JSON body
            if "json" not in kwargs:
                kwargs["json"] = kwargs.pop("params")
            else:
                # Merge params into existing json
                kwargs["json"].update(kwargs.pop("params"))

        try:
            response = requests.request(
                method="POST", url=url, headers=headers, **kwargs
            )

            # Check for HTTP errors
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    raise KintoneAPIError(
                        message=error_data.get(
                            "message", f"HTTP {response.status_code}"
                        ),
                        code=error_data.get("code"),
                        errors=error_data.get("errors"),
                        status_code=response.status_code,
                    )
                except (json.JSONDecodeError, KeyError):
                    raise KintoneAPIError(
                        f"HTTP {response.status_code}: {response.text}"
                    )

            result: Dict[str, Any] = response.json()
            return result

        except RequestException as e:
            raise KintoneNetworkError(f"Request failed: {str(e)}")

    def get_records(
        self,
        app: int,
        query: Optional[str] = None,
        fields: Optional[List[str]] = None,
        total_count: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> GetRecordsResponse:
        """Get records from a kintone app.

        Args:
            app: The app ID
            query: Query string to filter records
            fields: List of field codes to retrieve
            total_count: Whether to get total count
            limit: Number of records to retrieve (max 500)
            offset: Offset for pagination

        Returns:
            GetRecordsResponse containing records and optional total count
        """
        # Build request parameters
        params: Dict[str, Any] = {
            "app": app,
            "size": min(limit, MAX_RECORDS_PER_REQUEST),
        }

        if query:
            params["query"] = f"{query} limit {params['size']} offset {offset}"
        else:
            params["query"] = f"limit {params['size']} offset {offset}"

        if fields:
            params["fields"] = fields

        if total_count is not None:
            params["totalCount"] = total_count

        # Make request
        response_data = self._make_request(
            method="GET", endpoint="/records.json", params=params
        )

        return GetRecordsResponse(**response_data)

    def get_all_records(
        self,
        app: int,
        query: Optional[str] = None,
        fields: Optional[List[str]] = None,
        batch_size: int = 500,
    ) -> List[Dict[str, Any]]:
        """Get all records from a kintone app (handles pagination automatically).

        Args:
            app: The app ID
            query: Query string to filter records
            fields: List of field codes to retrieve
            batch_size: Number of records per request (max 500)

        Returns:
            List of all records matching the query
        """
        all_records = []
        offset = 0

        while True:
            response = self.get_records(
                app=app, query=query, fields=fields, limit=batch_size, offset=offset
            )

            records = response.records
            if not records:
                break

            all_records.extend(records)

            # Check if we've retrieved all records
            if len(records) < batch_size:
                break

            offset += batch_size

        return all_records

    def get_apps(
        self,
        name: Optional[str] = None,
        ids: Optional[List[int]] = None,
        codes: Optional[List[str]] = None,
        space_ids: Optional[List[int]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> GetAppsResponse:
        """Get apps information from kintone.

        Args:
            name: Partial match for app name (case-insensitive)
            ids: List of app IDs to retrieve
            codes: List of app codes to retrieve (exact match, case-sensitive)
            space_ids: List of space IDs to filter apps
            limit: Number of apps to retrieve (max 100)
            offset: Offset for pagination

        Returns:
            GetAppsResponse containing list of apps
        """
        # Build request parameters
        params: Dict[str, Any] = {}

        if name:
            params["name"] = name

        if ids:
            params["ids"] = ids

        if codes:
            params["codes"] = codes

        if space_ids:
            params["spaceIds"] = space_ids

        params["limit"] = min(limit, MAX_APPS_PER_REQUEST)
        params["offset"] = offset

        # Make request
        response_data = self._make_request(
            method="GET", endpoint="/apps.json", params=params
        )

        return GetAppsResponse(**response_data)

    def get_record(self, app: int, id: int) -> GetRecordResponse:
        """Get a single record from a kintone app.

        Args:
            app: The app ID
            id: The record ID

        Returns:
            GetRecordResponse containing the record
        """
        params = {"app": app, "id": id}

        response_data = self._make_request(
            method="GET", endpoint="/record.json", params=params
        )

        return GetRecordResponse(**response_data)

    def add_record(
        self, app: int, record: Dict[str, Dict[str, Any]]
    ) -> AddRecordResponse:
        """Add a single record to a kintone app.

        Args:
            app: The app ID
            record: Record data with field codes and values

        Returns:
            AddRecordResponse containing the new record ID and revision
        """
        request_data = {"app": app, "record": record}

        response_data = self._make_request(
            method="POST", endpoint="/record.json", json=request_data
        )

        return AddRecordResponse(**response_data)

    def add_records(
        self, app: int, records: List[Dict[str, Dict[str, Any]]]
    ) -> AddRecordsResponse:
        """Add multiple records to a kintone app.

        Args:
            app: The app ID
            records: List of record data (max 100 records)

        Returns:
            AddRecordsResponse containing the new record IDs and revisions
        """
        if len(records) > MAX_BATCH_RECORDS:
            raise KintoneValidationError(
                f"Cannot add more than {MAX_BATCH_RECORDS} records at once"
            )

        request_data = {"app": app, "records": records}

        response_data = self._make_request(
            method="POST", endpoint="/records.json", json=request_data
        )

        return AddRecordsResponse(**response_data)

    def update_record(
        self,
        app: int,
        record: Dict[str, Dict[str, Any]],
        id: Optional[int] = None,
        update_key: Optional[Dict[str, Any]] = None,
        revision: Optional[int] = None,
    ) -> UpdateRecordResponse:
        """Update a single record in a kintone app.

        Args:
            app: The app ID
            record: Record data with field codes and values to update
            id: The record ID (either id or update_key must be specified)
            update_key: Update key field and value (either id or update_key must be specified)
            revision: Expected revision number (for optimistic locking)

        Returns:
            UpdateRecordResponse containing the new revision
        """
        if id is None and update_key is None:
            raise KintoneValidationError("Either id or update_key must be specified")

        request_data = {"app": app, "record": record}

        if id is not None:
            request_data["id"] = id

        if update_key is not None:
            request_data["updateKey"] = update_key

        if revision is not None:
            request_data["revision"] = revision

        response_data = self._make_request(
            method="PUT", endpoint="/record.json", json=request_data
        )

        return UpdateRecordResponse(**response_data)

    def update_records(
        self, app: int, records: List[UpdateRecordData]
    ) -> UpdateRecordsResponse:
        """Update multiple records in a kintone app.

        Args:
            app: The app ID
            records: List of update data (max 100 records)

        Returns:
            UpdateRecordsResponse containing the updated record IDs and revisions
        """
        if len(records) > MAX_BATCH_RECORDS:
            raise KintoneValidationError(
                f"Cannot update more than {MAX_BATCH_RECORDS} records at once"
            )

        # Convert UpdateRecordData objects to dicts
        records_data = []
        for record in records:
            record_dict: Dict[str, Any] = {}
            if record.id is not None:
                record_dict["id"] = record.id
            if record.updateKey is not None:
                record_dict["updateKey"] = record.updateKey
            if record.revision is not None:
                record_dict["revision"] = record.revision
            record_dict["record"] = record.record
            records_data.append(record_dict)

        request_data = {"app": app, "records": records_data}

        response_data = self._make_request(
            method="PUT", endpoint="/records.json", json=request_data
        )

        return UpdateRecordsResponse(**response_data)

    def get_comments(
        self,
        app: int,
        record: int,
        order: str = "desc",
        offset: int = 0,
        limit: int = 10,
    ) -> GetCommentsResponse:
        """Get comments for a record.

        Args:
            app: The app ID
            record: The record ID
            order: Sort order ("asc" or "desc", default: "desc")
            offset: Offset for pagination
            limit: Number of comments to retrieve (max 10)

        Returns:
            GetCommentsResponse containing the comments
        """
        params = {
            "app": app,
            "record": record,
            "order": order,
            "offset": offset,
            "limit": min(limit, MAX_COMMENTS_PER_REQUEST),
        }

        response_data = self._make_request(
            method="GET", endpoint="/record/comments.json", params=params
        )

        return GetCommentsResponse(**response_data)

    def add_comment(
        self, app: int, record: int, comment: CommentContent
    ) -> AddCommentResponse:
        """Add a comment to a record.

        Args:
            app: The app ID
            record: The record ID
            comment: Comment content

        Returns:
            AddCommentResponse containing the new comment ID
        """
        request_data = {
            "app": app,
            "record": record,
            "comment": comment.model_dump(exclude_none=True),
        }

        response_data = self._make_request(
            method="POST", endpoint="/record/comment.json", json=request_data
        )

        return AddCommentResponse(**response_data)

    def update_status(
        self,
        app: int,
        id: int,
        action: str,
        assignee: Optional[str] = None,
        revision: Optional[int] = None,
    ) -> UpdateStatusResponse:
        """Update the status of a record.

        Args:
            app: The app ID
            id: The record ID
            action: The action name
            assignee: The login name of the assignee
            revision: Expected revision number (for optimistic locking)

        Returns:
            UpdateStatusResponse containing the new revision
        """
        request_data = {"app": app, "id": id, "action": action}

        if assignee is not None:
            request_data["assignee"] = assignee

        if revision is not None:
            request_data["revision"] = revision

        response_data = self._make_request(
            method="PUT", endpoint="/record/status.json", json=request_data
        )

        return UpdateStatusResponse(**response_data)

    def update_statuses(
        self, app: int, records: List[Dict[str, Any]]
    ) -> UpdateStatusesResponse:
        """Update the status of multiple records.

        Args:
            app: The app ID
            records: List of status update data (max 100 records)

        Returns:
            UpdateStatusesResponse containing the updated record IDs and revisions
        """
        if len(records) > MAX_BATCH_RECORDS:
            raise KintoneValidationError(
                f"Cannot update more than {MAX_BATCH_RECORDS} record statuses at once"
            )

        request_data = {"app": app, "records": records}

        response_data = self._make_request(
            method="PUT", endpoint="/records/status.json", json=request_data
        )

        return UpdateStatusesResponse(**response_data)

    def upload_file(self, file_path: str) -> FileUploadResponse:
        """Upload a file to kintone.

        Args:
            file_path: Path to the file to upload

        Returns:
            FileUploadResponse containing the file key
        """
        with open(file_path, "rb") as f:
            files = {"file": f}

            # Don't use json parameter for file uploads
            response_data = self._make_request(
                method="POST", endpoint="/file.json", files=files
            )

        return FileUploadResponse(**response_data)

    def upload_file_from_bytes(
        self, file_name: str, file_data: bytes
    ) -> FileUploadResponse:
        """Upload a file from bytes to kintone.

        Args:
            file_name: Name of the file
            file_data: File content as bytes

        Returns:
            FileUploadResponse containing the file key
        """
        files = {"file": (file_name, file_data)}

        response_data = self._make_request(
            method="POST", endpoint="/file.json", files=files
        )

        return FileUploadResponse(**response_data)

    def download_file(self, file_key: str) -> bytes:
        """Download a file from kintone.

        Args:
            file_key: The file key

        Returns:
            File content as bytes
        """
        params = {"fileKey": file_key}

        url = f"{self.base_url}/k/v1/file.json"
        headers = self.headers.copy()
        headers[HEADER_METHOD_OVERRIDE] = "GET"

        try:
            response = requests.post(url=url, headers=headers, json=params)

            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    raise KintoneAPIError(
                        message=error_data.get(
                            "message", f"HTTP {response.status_code}"
                        ),
                        code=error_data.get("code"),
                        errors=error_data.get("errors"),
                        status_code=response.status_code,
                    )
                except (json.JSONDecodeError, KeyError):
                    raise KintoneAPIError(
                        f"HTTP {response.status_code}: {response.text}"
                    )

            return response.content

        except RequestException as e:
            raise KintoneNetworkError(f"Request failed: {str(e)}")

    def get_app(self, id: int) -> GetAppResponse:
        """Get app information.

        Args:
            id: The app ID

        Returns:
            GetAppResponse containing app information
        """
        params = {"id": id}

        response_data = self._make_request(
            method="GET", endpoint="/app.json", params=params
        )

        return GetAppResponse(**response_data)

    def get_form_fields(
        self, app: int, lang: Optional[str] = None
    ) -> GetFormFieldsResponse:
        """Get form fields configuration.

        Args:
            app: The app ID
            lang: Language code (e.g., "en", "ja")

        Returns:
            GetFormFieldsResponse containing field properties and revision
        """
        params = {"app": app}

        if lang is not None:
            params["lang"] = lang

        response_data = self._make_request(
            method="GET", endpoint="/app/form/fields.json", params=params
        )

        return GetFormFieldsResponse(**response_data)
