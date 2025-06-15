"""Test query parsing utilities."""

import pytest
from kintone_mcp_server_python3.utils import parse_kintone_query


class TestParseKintoneQuery:
    """Test parse_kintone_query function."""

    def test_empty_query(self):
        """Test parsing empty query."""
        result = parse_kintone_query(None, 100, 0)
        assert result["base_query"] == ""
        assert result["order_by"] is None
        assert result["limit"] == 100
        assert result["offset"] == 0

    def test_simple_query(self):
        """Test parsing query without order by, limit, offset."""
        query = 'field1 = "value1" and field2 > 10'
        result = parse_kintone_query(query, 100, 0)
        assert result["base_query"] == query
        assert result["order_by"] is None
        assert result["limit"] == 100
        assert result["offset"] == 0

    def test_query_with_order_by(self):
        """Test parsing query with order by clause."""
        query = 'field1 = "value1" order by field2 desc'
        result = parse_kintone_query(query, 100, 0)
        assert result["base_query"] == 'field1 = "value1"'
        assert result["order_by"] == "order by field2 desc"
        assert result["limit"] == 100
        assert result["offset"] == 0

    def test_query_with_multiple_order_by(self):
        """Test parsing query with multiple order by fields."""
        query = 'field1 = "value1" order by field2 desc, field3 asc'
        result = parse_kintone_query(query, 100, 0)
        assert result["base_query"] == 'field1 = "value1"'
        assert result["order_by"] == "order by field2 desc, field3 asc"
        assert result["limit"] == 100
        assert result["offset"] == 0

    def test_query_with_limit(self):
        """Test parsing query with limit clause."""
        query = 'field1 = "value1" limit 50'
        result = parse_kintone_query(query, 100, 0)
        assert result["base_query"] == 'field1 = "value1"'
        assert result["order_by"] is None
        assert result["limit"] == 50  # Query limit is smaller
        assert result["offset"] == 0

    def test_query_with_larger_limit(self):
        """Test parsing query with limit larger than default."""
        query = 'field1 = "value1" limit 200'
        result = parse_kintone_query(query, 100, 0)
        assert result["base_query"] == 'field1 = "value1"'
        assert result["order_by"] is None
        assert result["limit"] == 100  # Default limit is smaller
        assert result["offset"] == 0

    def test_query_with_offset(self):
        """Test parsing query with offset clause."""
        query = 'field1 = "value1" offset 50'
        result = parse_kintone_query(query, 100, 0)
        assert result["base_query"] == 'field1 = "value1"'
        assert result["order_by"] is None
        assert result["limit"] == 100
        assert result["offset"] == 50  # Query offset overrides default

    def test_query_with_all_clauses(self):
        """Test parsing query with order by, limit, and offset."""
        query = 'field1 = "value1" order by field2 desc limit 75 offset 25'
        result = parse_kintone_query(query, 100, 0)
        assert result["base_query"] == 'field1 = "value1"'
        assert result["order_by"] == "order by field2 desc"
        assert result["limit"] == 75  # Query limit is smaller
        assert result["offset"] == 25  # Query offset overrides default

    def test_case_insensitive_clauses(self):
        """Test parsing with case variations."""
        query = 'field1 = "value1" ORDER BY field2 DESC LIMIT 50 OFFSET 10'
        result = parse_kintone_query(query, 100, 0)
        assert result["base_query"] == 'field1 = "value1"'
        assert result["order_by"] == "ORDER BY field2 DESC"
        assert result["limit"] == 50
        assert result["offset"] == 10

    def test_no_default_limit(self):
        """Test parsing when no default limit is provided."""
        query = 'field1 = "value1" limit 50'
        result = parse_kintone_query(query, None, 0)
        assert result["base_query"] == 'field1 = "value1"'
        assert result["order_by"] is None
        assert result["limit"] == 50
        assert result["offset"] == 0

    def test_complex_query_preservation(self):
        """Test that complex query conditions are preserved."""
        query = 'field1 = "value1" and (field2 > 10 or field3 in ("a", "b")) order by field4'
        result = parse_kintone_query(query, 100, 0)
        assert result["base_query"] == 'field1 = "value1" and (field2 > 10 or field3 in ("a", "b"))'
        assert result["order_by"] == "order by field4"
        assert result["limit"] == 100
        assert result["offset"] == 0