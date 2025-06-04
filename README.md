# kintone MCP Server (Python3)

kintone REST APIと連携するためのMCP (Model Context Protocol) サーバーです。

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/r3-yamauchi/kintone-mcp-server-python3)

## 機能

- kintoneアプリからのレコード取得
- kintoneアプリ情報の検索・取得
- APIトークン認証とパスワード認証の両方をサポート
- 自動ページネーション処理
- クエリによるフィルタリング機能
- すべてのAPIリクエストをPOST + X-HTTP-Method-Overrideで実行

## インストール

### uv/uvxを使用する場合

```bash
# uvxでインストール
uvx kintone-mcp-server-python3

# またはuvでインストール
uv tool install kintone-mcp-server-python3
```

### pipを使用する場合

```bash
pip install kintone-mcp-server-python3
```

## 設定

サーバーは環境変数で設定します。

### 環境変数

プロジェクトルートに`.env`ファイルを作成：

```bash
# 認証タイプ: "api_token" または "password"
KINTONE_AUTH_TYPE=api_token

# kintoneサブドメイン（必須）
KINTONE_SUBDOMAIN=your-subdomain

# kintoneドメイン（オプション、デフォルト: cybozu.com）
KINTONE_DOMAIN=cybozu.com

# APIトークン認証の場合
KINTONE_API_TOKEN=your-api-token

# パスワード認証の場合
KINTONE_USERNAME=your-username
KINTONE_PASSWORD=your-password
```

## 使用方法

### サーバーの起動

#### uvxを使用（推奨）

```bash
# uvxで実行
uvx kintone-mcp-server-python3
```

#### Pythonを直接使用

```bash
# pipインストール後
python3 -m kintone_mcp_server_python3

# ソースコードから（開発時）
cd /path/to/kintone-mcp-server-python3
pip install -e .
python3 -m kintone_mcp_server_python3

# またはメインモジュールを直接実行
python3 src/kintone_mcp_server_python3/__main__.py
```

### 利用可能なツール

#### get_records

ページネーション機能付きでkintoneアプリからレコードを取得します。

**パラメータ:**
- `app` (必須): アプリID
- `query` (オプション): レコードをフィルタリングするクエリ文字列
- `fields` (オプション): 取得するフィールドコードのリスト
- `limit` (オプション): 取得する最大レコード数（デフォルト: 100、最大: 500）
- `offset` (オプション): ページネーション用のオフセット（デフォルト: 0）

**使用例:**
```json
{
  "tool": "get_records",
  "arguments": {
    "app": 123,
    "query": "Status = \"Open\"",
    "fields": ["Title", "Status", "Created_datetime"],
    "limit": 100
  }
}
```

#### get_all_records

kintoneアプリから全レコードを取得します（ページネーションを自動処理）。

**パラメータ:**
- `app` (必須): アプリID
- `query` (オプション): レコードをフィルタリングするクエリ文字列
- `fields` (オプション): 取得するフィールドコードのリスト

**使用例:**
```json
{
  "tool": "get_all_records",
  "arguments": {
    "app": 123,
    "query": "Created_datetime > \"2024-01-01\"",
    "fields": ["Title", "Status"]
  }
}
```

#### get_apps

kintoneアプリの情報を検索・取得します。

**パラメータ:**
- `name` (オプション): アプリ名の部分一致検索（大文字小文字を区別しない）
- `ids` (オプション): 取得するアプリIDのリスト
- `codes` (オプション): 取得するアプリコードのリスト（完全一致、大文字小文字を区別）
- `space_ids` (オプション): スペースIDでフィルタリング
- `limit` (オプション): 取得する最大アプリ数（デフォルト: 100、最大: 100）
- `offset` (オプション): ページネーション用のオフセット（デフォルト: 0）

**使用例:**
```json
{
  "tool": "get_apps",
  "arguments": {
    "name": "顧客",
    "limit": 50
  }
}
```

**レスポンス例:**
```json
{
  "apps": [
    {
      "appId": "123",
      "code": "CUSTOMER_APP",
      "name": "顧客管理",
      "description": "顧客情報を管理するアプリです",
      "spaceId": "10",
      "createdAt": "2024-01-01T00:00:00Z",
      "creator": {
        "code": "user1",
        "name": "山田太郎"
      },
      "modifiedAt": "2024-01-15T10:30:00Z",
      "modifier": {
        "code": "user2",
        "name": "佐藤花子"
      }
    }
  ],
  "count": 1
}
```

## MCPクライアント設定

MCPクライアントでこのサーバーを使用するには、以下の設定を追加してください：

### uvxを使用（推奨）

```json
{
  "mcpServers": {
    "kintone": {
      "command": "uvx",
      "args": ["kintone-mcp-server-python3"],
      "env": {
        "KINTONE_SUBDOMAIN": "your-subdomain",
        "KINTONE_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

### Pythonを直接使用（代替）

```json
{
  "mcpServers": {
    "kintone": {
      "command": "python3",
      "args": ["-m", "kintone_mcp_server_python3"],
      "env": {
        "KINTONE_SUBDOMAIN": "your-subdomain",
        "KINTONE_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

### 両方のオプションを含む完全な例

```json
{
  "mcpServers": {
    "kintone": {
      "command": "uvx",
      "args": ["kintone-mcp-server-python3"],
      "env": {
        "KINTONE_SUBDOMAIN": "your-subdomain",
        "KINTONE_API_TOKEN": "your-api-token"
      }
    },
    "kintone-python": {
      "command": "python3",
      "args": ["-m", "kintone_mcp_server_python3"],
      "env": {
        "KINTONE_SUBDOMAIN": "your-subdomain",
        "KINTONE_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

### パス指定について

#### 実行パスの動作

**uvxの場合**
- `"args": ["kintone-mcp-server-python3"]`と指定すると、PyPIからパッケージを自動的にダウンロード・実行
- カレントディレクトリに関係なく動作
- インストール不要で利用可能

**python3 -mの場合**
- `"args": ["-m", "kintone_mcp_server_python3"]`と指定
- `pip install`でインストール済みの場合、どこからでも実行可能
- Pythonのモジュール検索パスに依存

#### 相対パス指定

```json
{
  "mcpServers": {
    "kintone-dev": {
      "command": "python3",
      "args": ["./src/kintone_mcp_server_python3/__main__.py"],
      "env": {
        "KINTONE_SUBDOMAIN": "your-subdomain",
        "KINTONE_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

#### 絶対パス指定

```json
{
  "mcpServers": {
    "kintone-local": {
      "command": "python3",
      "args": ["/path/to/kintone-mcp-server-python3/src/kintone_mcp_server_python3/__main__.py"],
      "env": {
        "KINTONE_SUBDOMAIN": "your-subdomain",
        "KINTONE_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

#### 開発環境での実行（PYTHONPATH使用）

```json
{
  "mcpServers": {
    "kintone-dev": {
      "command": "python3",
      "args": ["-m", "kintone_mcp_server_python3"],
      "env": {
        "PYTHONPATH": "/path/to/kintone-mcp-server-python3/src",
        "KINTONE_SUBDOMAIN": "your-subdomain",
        "KINTONE_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

#### 推奨される使用方法

- **本番環境**: `pip install`または`uvx`を使用（パス指定不要）
- **開発環境**: 絶対パスまたはPYTHONPATH設定
- **テスト環境**: `pip install -e .`（編集可能インストール）後、モジュールとして実行

## 開発

### セットアップ

```bash
# リポジトリをクローン
git clone https://github.com/yourusername/kintone-mcp-server-python3.git
cd kintone-mcp-server-python3

# 依存関係をインストール
pip install -e ".[dev]"
```

### テストの実行

```bash
pytest
```

### コード品質

```bash
# コードフォーマット
black src tests

# リント
ruff check src tests

# 型チェック
mypy src
```

## ライセンス

MIT

## 貢献

プルリクエストは歓迎します！お気軽にご提出ください。