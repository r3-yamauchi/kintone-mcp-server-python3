# kintone MCP Server (Python3) サンプル

kintone REST APIと連携するためのMCP (Model Context Protocol) サーバーのサンプル実装です。
このサーバーは、AI アシスタント（Claude等）がkintoneのデータを読み取り、操作できるようにするためのブリッジとして機能します。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/r3-yamauchi/kintone-mcp-server-python3)

## 主な特徴

- 🔐 **セキュアな認証**: APIトークン認証とパスワード認証の両方をサポート
- 📊 **完全なCRUD操作**: レコードの作成・読み取り・更新・削除が可能
- 📄 **自動ページネーション**: 大量のレコードを効率的に処理
- 🔍 **高度なクエリ機能**: kintoneのクエリ構文をフルサポート
- 📎 **ファイル管理**: ファイルのアップロード・ダウンロードに対応
- 💬 **コメント機能**: レコードへのコメント追加・取得
- 🔄 **ステータス管理**: プロセス管理のステータス更新
- 🚀 **非同期処理**: 高速なレスポンスと効率的なリソース使用
- 🛡️ **堅牢なエラー処理**: 詳細なエラーメッセージと適切な例外処理
- 🌐 **国際化対応**: 多言語フィールドのサポート

## 利用可能なツール

### レコード操作
| ツール名 | 説明 | 主な用途 |
|---------|-----|---------|
| `get_record` | 単一レコードの取得 | 特定のレコードの詳細情報を取得 |
| `get_records` | レコード一覧の取得（ページネーション付き） | 条件に合うレコードを検索・取得 |
| `get_all_records` | 全レコードの自動取得 | 大量レコードの一括取得（自動ページネーション） |
| `add_record` | 単一レコードの追加 | 新規レコードの作成 |
| `add_records` | 複数レコードの一括追加（最大100件） | バッチ処理による効率的なレコード作成 |
| `update_record` | 単一レコードの更新 | 既存レコードの情報更新 |
| `update_records` | 複数レコードの一括更新（最大100件） | バッチ処理による効率的なレコード更新 |

### コメント・ステータス操作
| ツール名 | 説明 | 主な用途 |
|---------|-----|---------|
| `get_comments` | レコードのコメント取得 | コミュニケーション履歴の確認 |
| `add_comment` | レコードへのコメント追加 | メンション付きコメントの投稿 |
| `update_status` | レコードのステータス更新 | ワークフローの進行 |
| `update_statuses` | 複数レコードのステータス一括更新 | 効率的なワークフロー処理 |

### ファイル・アプリ管理
| ツール名 | 説明 | 主な用途 |
|---------|-----|---------|
| `upload_file` | ファイルのアップロード | 添付ファイルの登録 |
| `download_file` | ファイルのダウンロード | 添付ファイルの取得 |
| `get_app` | アプリ情報の取得 | アプリ設定の確認 |
| `get_apps` | アプリ一覧の検索・取得 | 利用可能なアプリの探索 |
| `get_form_fields` | フォームフィールド設定の取得 | アプリ構造の理解 |

## 必要条件

- Python 3.12以上
- kintone環境へのアクセス権限
- APIトークンまたはユーザー認証情報

## MCPクライアント設定

### Claude Desktop設定

Claude Desktopでこのサーバーを使用するには、設定ファイルに以下を追加してください。

#### 設定ファイルの場所

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

#### uvxを使用（推奨）

GitHubから直接実行する設定：

```json
{
  "mcpServers": {
    "kintone": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/r3-yamauchi/kintone-mcp-server-python3.git",
        "kintone-mcp-server-python3"
      ],
      "env": {
        "KINTONE_SUBDOMAIN": "your-subdomain",
        "KINTONE_API_TOKEN": "your-api-token",
        "KINTONE_AUTH_TYPE": "api_token",
        "KINTONE_DOMAIN": "cybozu.com",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**重要**: 
- `KINTONE_SUBDOMAIN`と`KINTONE_API_TOKEN`は必ず実際の値に置き換えてください
- 環境変数は`claude_desktop_config.json`内に直接記載されます
- 設定変更後はClaude Desktopを再起動してください

#### Pythonを直接使用（代替）

```json
{
  "mcpServers": {
    "kintone": {
      "command": "python3",
      "args": ["-m", "kintone_mcp_server_python3"],
      "env": {
        "KINTONE_SUBDOMAIN": "your-subdomain",
        "KINTONE_API_TOKEN": "your-api-token",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### VS Code設定

VS CodeのMCP拡張機能を使用する場合：

```json
{
  "mcp.servers": {
    "kintone": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/r3-yamauchi/kintone-mcp-server-python3.git",
        "kintone-mcp-server-python3"
      ],
      "env": {
        "KINTONE_SUBDOMAIN": "your-subdomain",
        "KINTONE_API_TOKEN": "your-api-token",
        "KINTONE_AUTH_TYPE": "api_token",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### 複数環境の設定例

本番環境と開発環境を分けて管理する場合：

```json
{
  "mcpServers": {
    "kintone-prod": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/r3-yamauchi/kintone-mcp-server-python3.git",
        "kintone-mcp-server-python3"
      ],
      "env": {
        "KINTONE_SUBDOMAIN": "production",
        "KINTONE_API_TOKEN": "prod-api-token",
        "KINTONE_AUTH_TYPE": "api_token",
        "KINTONE_DOMAIN": "cybozu.com",
        "LOG_LEVEL": "WARNING"
      }
    },
    "kintone-dev": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/r3-yamauchi/kintone-mcp-server-python3.git",
        "kintone-mcp-server-python3"
      ],
      "env": {
        "KINTONE_SUBDOMAIN": "development",
        "KINTONE_API_TOKEN": "dev-api-token",
        "KINTONE_AUTH_TYPE": "api_token",
        "KINTONE_DOMAIN": "cybozu.com",
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

### パスワード認証を使用する場合の設定例

APIトークンの代わりにユーザー名/パスワード認証を使用する場合：

```json
{
  "mcpServers": {
    "kintone-password": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/r3-yamauchi/kintone-mcp-server-python3.git",
        "kintone-mcp-server-python3"
      ],
      "env": {
        "KINTONE_SUBDOMAIN": "your-subdomain",
        "KINTONE_AUTH_TYPE": "password",
        "KINTONE_USERNAME": "your-username",
        "KINTONE_PASSWORD": "your-password",
        "KINTONE_DOMAIN": "cybozu.com",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### 設定のポイント

1. **環境変数の直接記載**
   - すべての環境変数は`env`セクション内に直接記載します
   - `.env`ファイルは不要です

2. **uvxの利点**
   - 事前のインストールが不要
   - 常に最新版を実行
   - 依存関係の競合を回避

3. **セキュリティの注意点**
   - `claude_desktop_config.json`にはAPIトークンなどの機密情報が含まれます
   - このファイルを他人と共有しないでください
   - Gitリポジトリにコミットしないよう注意してください

## トラブルシューティング

### よくある問題と解決方法

#### 接続エラー

```
Error: Failed to connect to kintone
```

**解決方法**:
1. `KINTONE_SUBDOMAIN`が正しいか確認
2. ネットワーク接続を確認
3. ファイアウォール設定を確認

#### 認証エラー

```
Error: Authentication failed (401)
```

**解決方法**:
1. APIトークンが正しいか確認
2. APIトークンに必要な権限があるか確認
3. アプリの設定でAPIトークンが有効になっているか確認

#### 権限エラー

```
Error: Permission denied (403)
```

**解決方法**:
1. ユーザーにアプリへのアクセス権限があるか確認
2. APIトークンに必要な権限が付与されているか確認
3. レコードのアクセス権限を確認

#### レート制限エラー

```
Error: Rate limit exceeded (429)
```

**解決方法**:
1. リクエスト頻度を下げる
2. バッチ処理を使用する（`add_records`、`update_records`）
3. 処理を分散させる

### デバッグモード

詳細なログを出力するには：

```bash
export LOG_LEVEL=DEBUG
uvx --from git+https://github.com/r3-yamauchi/kintone-mcp-server-python3.git kintone-mcp-server-python3
```

## ソースコードをローカルインストールする場合

```bash
# リポジトリをクローン
git clone https://github.com/r3-yamauchi/kintone-mcp-server-python3.git
cd kintone-mcp-server-python3

# 依存関係をインストール
pip install -e .

# 実行
python -m kintone_mcp_server_python3
```

## 設定

### 環境変数の設定

サーバーは環境変数で設定します。プロジェクトルートに`.env`ファイルを作成するか、環境変数を直接設定してください。

#### 基本設定

```bash
# kintoneサブドメイン（必須）
# 例: https://example.cybozu.com の場合は "example"
KINTONE_SUBDOMAIN=your-subdomain

# kintoneドメイン（オプション）
# デフォルト: cybozu.com
# cybozu.cn（中国）やcustom.comなどの場合に指定
KINTONE_DOMAIN=cybozu.com

# ログレベル（オプション）
# DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO
```

#### 認証設定

##### APIトークン認証（推奨）

```bash
# 認証タイプ
KINTONE_AUTH_TYPE=api_token

# APIトークン
# kintoneアプリの設定画面から生成
KINTONE_API_TOKEN=your-api-token
```

##### パスワード認証

```bash
# 認証タイプ
KINTONE_AUTH_TYPE=password

# ユーザー認証情報
KINTONE_USERNAME=your-username
KINTONE_PASSWORD=your-password
```

### APIトークンの生成方法

1. kintoneアプリの設定画面を開く
2. 「設定」タブ → 「APIトークン」をクリック
3. 必要な権限にチェックを入れる：
   - レコード閲覧
   - レコード追加
   - レコード編集
   - レコード削除（必要に応じて）
   - アプリ管理（アプリ情報取得に必要）
4. 「生成」をクリックしてトークンをコピー
5. 「保存」をクリックして設定を反映

## クイックスタート

### 1. 環境変数の設定

```bash
# 設定ファイルのサンプルをコピー
cp .env.example .env

# .envファイルを編集して認証情報を設定
# KINTONE_SUBDOMAIN=your-subdomain
# KINTONE_API_TOKEN=your-api-token
```

### 2. サーバーの起動

```bash
# uvxを使用（推奨）
uvx --from git+https://github.com/r3-yamauchi/kintone-mcp-server-python3.git kintone-mcp-server-python3

# またはローカルインストール後
python3 -m kintone_mcp_server_python3
```

### 3. MCPクライアントでの使用

Claude Desktop、VS Code、または他のMCP対応クライアントで設定してください（設定例は後述）。

## 使用例

### 基本的な使い方

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

## 開発

### 開発環境のセットアップ

```bash
# リポジトリをクローン
git clone https://github.com/r3-yamauchi/kintone-mcp-server-python3.git
cd kintone-mcp-server-python3

# 仮想環境の作成（推奨）
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# 開発用依存関係をインストール
pip install -e ".[dev]"

# 環境変数の設定
cp .env.example .env
# .envファイルを編集して必要な設定を追加

# pre-commitフックの設定（推奨）
pre-commit install
```

### テスト

```bash
# すべてのテストを実行
pytest

# カバレッジレポート付きでテスト実行
pytest --cov=kintone_mcp_server_python3 --cov-report=html

# 特定のテストファイルを実行
pytest tests/test_auth.py

# 特定のテストを実行
pytest tests/test_auth.py::test_api_token_auth -v
```

### コード品質管理

```bash
# コードフォーマット（Black）
black src tests

# リンティング（Ruff）
ruff check src tests
ruff check src tests --fix  # 自動修正

# 型チェック（MyPy）
mypy src

# すべてのチェックを実行
make lint  # Makefileがある場合
# または
black src tests && ruff check src tests && mypy src
```

### リリース手順

1. バージョン番号を更新（`pyproject.toml`）
2. 変更履歴を更新（CHANGELOG.md）
3. テストを実行して成功を確認
4. コード品質チェック：
   ```bash
   black src tests
   ruff check src tests
   mypy src
   ```
5. GitHubにプッシュ：
   ```bash
   git add .
   git commit -m "Release v0.1.0"
   git tag v0.1.0
   git push origin main --tags
   ```
6. GitHubでリリースノートを作成（オプション）

## FAQ

### Q: 複数のkintone環境を同時に使用できますか？

A: はい、MCPクライアントの設定で複数のサーバーインスタンスを定義できます。環境ごとに異なる名前（例：`kintone-prod`、`kintone-dev`）を付けてください。

### Q: 日本語以外の言語でフィールド情報を取得できますか？

A: はい、`get_form_fields`ツールで`lang`パラメータを使用することで、英語（en）、中国語（zh）、スペイン語（es）などでフィールド情報を取得できます。

## 著者

r3-yamauchi

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルを参照してください。
