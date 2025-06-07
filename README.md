# kintone MCP Server (Python3)

kintone REST APIと連携するためのMCP (Model Context Protocol) サーバーです。

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/r3-yamauchi/kintone-mcp-server-python3)

## 機能

### レコード操作
- 単一/複数レコードの取得（`get_record`, `get_records`, `get_all_records`）
- レコードの作成（`add_record`, `add_records`）
- レコードの更新（`update_record`, `update_records`）
- レコードへのコメント追加/取得（`add_comment`, `get_comments`）
- ステータス更新（`update_status`, `update_statuses`）

### ファイル操作
- ファイルのアップロード（`upload_file`）
- ファイルのダウンロード（`download_file`）

### アプリ管理
- アプリ情報の取得（`get_app`, `get_apps`）
- フォームフィールド設定の取得（`get_form_fields`）

### その他の機能
- APIトークン認証とパスワード認証の両方をサポート
- 自動ページネーション処理
- クエリによるフィルタリング機能
- すべてのAPIリクエストをPOST + X-HTTP-Method-Overrideで実行
- エラーハンドリングと詳細なエラーメッセージ

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

#### get_record

単一のレコードを取得します。

**パラメータ:**
- `app` (必須): アプリID
- `id` (必須): レコードID

**使用例:**
```json
{
  "tool": "get_record",
  "arguments": {
    "app": 123,
    "id": 456
  }
}
```

#### add_record

kintoneアプリに単一のレコードを追加します。

**パラメータ:**
- `app` (必須): アプリID
- `record` (必須): フィールドコードと値のオブジェクト

**使用例:**
```json
{
  "tool": "add_record",
  "arguments": {
    "app": 123,
    "record": {
      "Title": {"value": "新しいタスク"},
      "Status": {"value": "未着手"},
      "Assignee": {"value": [{"code": "user1"}]}
    }
  }
}
```

#### add_records

複数のレコードを一括で追加します（最大100件）。

**パラメータ:**
- `app` (必須): アプリID
- `records` (必須): レコードデータの配列

**使用例:**
```json
{
  "tool": "add_records",
  "arguments": {
    "app": 123,
    "records": [
      {
        "Title": {"value": "タスク1"},
        "Status": {"value": "未着手"}
      },
      {
        "Title": {"value": "タスク2"},
        "Status": {"value": "進行中"}
      }
    ]
  }
}
```

#### update_record

単一のレコードを更新します。

**パラメータ:**
- `app` (必須): アプリID
- `id` (オプション): レコードID（idまたはupdate_keyのいずれか必須）
- `update_key` (オプション): 更新キーとなるフィールドと値
- `record` (必須): 更新するフィールドと値
- `revision` (オプション): リビジョン番号（楽観的ロック用）

**使用例:**
```json
{
  "tool": "update_record",
  "arguments": {
    "app": 123,
    "id": 456,
    "record": {
      "Status": {"value": "完了"},
      "CompletedDate": {"value": "2024-12-07"}
    }
  }
}
```

#### update_records

複数のレコードを一括更新します（最大100件）。

**パラメータ:**
- `app` (必須): アプリID
- `records` (必須): 更新データの配列

**使用例:**
```json
{
  "tool": "update_records",
  "arguments": {
    "app": 123,
    "records": [
      {
        "id": 456,
        "record": {"Status": {"value": "完了"}}
      },
      {
        "id": 789,
        "record": {"Status": {"value": "保留"}}
      }
    ]
  }
}
```

#### get_comments

レコードのコメントを取得します。

**パラメータ:**
- `app` (必須): アプリID
- `record` (必須): レコードID
- `order` (オプション): ソート順（"asc" または "desc"、デフォルト: "desc"）
- `offset` (オプション): オフセット（デフォルト: 0）
- `limit` (オプション): 取得件数（最大10、デフォルト: 10）

**使用例:**
```json
{
  "tool": "get_comments",
  "arguments": {
    "app": 123,
    "record": 456,
    "order": "desc",
    "limit": 5
  }
}
```

#### add_comment

レコードにコメントを追加します。

**パラメータ:**
- `app` (必須): アプリID
- `record` (必須): レコードID
- `text` (必須): コメント本文
- `mentions` (オプション): メンション情報の配列

**使用例:**
```json
{
  "tool": "add_comment",
  "arguments": {
    "app": 123,
    "record": 456,
    "text": "作業が完了しました。",
    "mentions": [
      {"code": "user1", "type": "USER"}
    ]
  }
}
```

#### update_status

レコードのステータスを更新します。

**パラメータ:**
- `app` (必須): アプリID
- `id` (必須): レコードID
- `action` (必須): アクション名
- `assignee` (オプション): 担当者のログイン名
- `revision` (オプション): リビジョン番号

**使用例:**
```json
{
  "tool": "update_status",
  "arguments": {
    "app": 123,
    "id": 456,
    "action": "承認する",
    "assignee": "user2"
  }
}
```

#### update_statuses

複数レコードのステータスを一括更新します（最大100件）。

**パラメータ:**
- `app` (必須): アプリID
- `records` (必須): ステータス更新データの配列

**使用例:**
```json
{
  "tool": "update_statuses",
  "arguments": {
    "app": 123,
    "records": [
      {
        "id": 456,
        "action": "承認する"
      },
      {
        "id": 789,
        "action": "却下する"
      }
    ]
  }
}
```

#### upload_file

ファイルをkintoneにアップロードします。

**パラメータ:**
- `file_path` (必須): アップロードするファイルのパス

**使用例:**
```json
{
  "tool": "upload_file",
  "arguments": {
    "file_path": "/path/to/document.pdf"
  }
}
```

**レスポンス例:**
```json
{
  "fileKey": "20241207103000-1234567890ABCDEF"
}
```

#### download_file

kintoneからファイルをダウンロードします。

**パラメータ:**
- `file_key` (必須): ファイルキー
- `save_path` (必須): 保存先のファイルパス

**使用例:**
```json
{
  "tool": "download_file",
  "arguments": {
    "file_key": "20241207103000-1234567890ABCDEF",
    "save_path": "/path/to/save/document.pdf"
  }
}
```

#### get_app

アプリの詳細情報を取得します。

**パラメータ:**
- `id` (必須): アプリID

**使用例:**
```json
{
  "tool": "get_app",
  "arguments": {
    "id": 123
  }
}
```

#### get_form_fields

アプリのフォームフィールド設定を取得します。

**パラメータ:**
- `app` (必須): アプリID
- `lang` (オプション): 言語コード（例: "ja", "en"）

**使用例:**
```json
{
  "tool": "get_form_fields",
  "arguments": {
    "app": 123,
    "lang": "ja"
  }
}
```

**レスポンス例:**
```json
{
  "properties": {
    "Title": {
      "type": "SINGLE_LINE_TEXT",
      "code": "Title",
      "label": "タイトル",
      "required": true
    },
    "Status": {
      "type": "DROP_DOWN",
      "code": "Status",
      "label": "ステータス",
      "options": {
        "未着手": {"label": "未着手", "index": "0"},
        "進行中": {"label": "進行中", "index": "1"},
        "完了": {"label": "完了", "index": "2"}
      }
    }
  },
  "revision": "5"
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