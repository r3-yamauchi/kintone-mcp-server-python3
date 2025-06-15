"""Tests for query language documentation."""

import pytest
from kintone_mcp_server_python3.query_language import get_query_language_documentation


def test_get_query_language_documentation():
    """Test that query language documentation is returned."""
    doc = get_query_language_documentation()
    
    # Check that documentation is returned
    assert isinstance(doc, str)
    assert len(doc) > 0
    
    # Check for key sections
    assert "# kintoneクエリ言語仕様" in doc
    assert "## 基本構文" in doc
    assert "## 演算子一覧" in doc
    assert "## 特殊な関数" in doc
    assert "## クエリオプション" in doc
    assert "## クエリ例" in doc
    assert "## 注意事項" in doc
    
    # Check for key operators
    assert "### 比較演算子" in doc
    assert "### 文字列演算子" in doc
    assert "## 論理演算子" in doc
    
    # Check for special functions
    assert "LOGINUSER()" in doc
    assert "TODAY()" in doc
    assert "FROM_TODAY(" in doc
    
    # Check for query options
    assert "order by" in doc
    assert "limit" in doc
    assert "offset" in doc
    
    # Check for examples
    assert "ステータス = \"完了\"" in doc
    assert "and" in doc
    assert "or" in doc
    assert "in" in doc
    assert "like" in doc


def test_documentation_structure():
    """Test that documentation has proper markdown structure."""
    doc = get_query_language_documentation()
    lines = doc.split('\n')
    
    # Check headers
    h1_count = sum(1 for line in lines if line.startswith('# '))
    h2_count = sum(1 for line in lines if line.startswith('## '))
    h3_count = sum(1 for line in lines if line.startswith('### '))
    
    assert h1_count >= 1  # At least one main header
    assert h2_count >= 5  # Multiple sections
    assert h3_count >= 3  # Sub-sections
    
    # Check code blocks
    assert '```' in doc  # Contains code examples
    
    # Check lists
    assert '- ' in doc  # Contains bullet points