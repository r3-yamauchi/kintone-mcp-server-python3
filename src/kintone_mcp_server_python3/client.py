"""kintone API client."""

import json
from typing import Any, Dict, List, Optional
import requests
from requests.exceptions import RequestException

from .auth import KintoneAuth
from .models import GetRecordsRequest, GetRecordsResponse, GetAppsResponse


class KintoneAPIError(Exception):
    """kintone API error."""
    def __init__(self, message: str, code: Optional[str] = None, errors: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.code = code
        self.errors = errors


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
        headers["X-HTTP-Method-Override"] = method
        
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
                method="POST",
                url=url,
                headers=headers,
                **kwargs
            )
            
            # Check for HTTP errors
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    raise KintoneAPIError(
                        message=error_data.get("message", f"HTTP {response.status_code}"),
                        code=error_data.get("code"),
                        errors=error_data.get("errors")
                    )
                except (json.JSONDecodeError, KeyError):
                    raise KintoneAPIError(f"HTTP {response.status_code}: {response.text}")
            
            return response.json()
            
        except RequestException as e:
            raise KintoneAPIError(f"Request failed: {str(e)}")
    
    def get_records(
        self,
        app: int,
        query: Optional[str] = None,
        fields: Optional[List[str]] = None,
        total_count: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
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
            "size": min(limit, 500)  # kintone max is 500
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
            method="GET",
            endpoint="/records.json",
            params=params
        )
        
        return GetRecordsResponse(**response_data)
    
    def get_all_records(
        self,
        app: int,
        query: Optional[str] = None,
        fields: Optional[List[str]] = None,
        batch_size: int = 500
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
                app=app,
                query=query,
                fields=fields,
                limit=batch_size,
                offset=offset
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
        offset: int = 0
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
        
        params["limit"] = min(limit, 100)  # kintone max is 100
        params["offset"] = offset
        
        # Make request
        response_data = self._make_request(
            method="GET",
            endpoint="/apps.json",
            params=params
        )
        
        return GetAppsResponse(**response_data)