# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 一般的に使用されるコマンド

### インストールとセットアップ
```bash
# 開発環境のセットアップ（編集可能インストール）
pip install -e ".[dev]"

# 通常のインストール
pip install .
```

### ビルドとパッケージング
```bash
# パッケージのビルド（hatchlingを使用）
python -m build

# PyPIへの公開準備
python -m twine upload dist/*
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
black src tests && ruff check src tests && mypy src
```

### テスト実行
```bash
# すべてのテストを実行
pytest

# 特定のテストファイルを実行
pytest tests/test_auth.py

# 特定のテストを実行
pytest tests/test_auth.py::test_api_token_auth

# カバレッジ付きでテスト実行
pytest --cov=kintone_mcp_server_python3 --cov-report=html
```

### サーバーの起動
```bash
# 環境変数を使用して起動
export KINTONE_SUBDOMAIN=your-subdomain
export KINTONE_API_TOKEN=your-api-token
python3 -m kintone_mcp_server_python3

# 開発環境から直接起動
python3 src/kintone_mcp_server_python3/__main__.py

# uvxを使用（インストール後）
uvx kintone-mcp-server-python3
```

## 高レベルのコードアーキテクチャと構造

### プロジェクト構造
```
kintone-mcp-server-python3/
├── src/kintone_mcp_server_python3/
│   ├── __init__.py       # パッケージ初期化、バージョン管理
│   ├── __main__.py       # エントリーポイント、設定読み込み
│   ├── auth.py           # 認証システム（APIトークン/パスワード）
│   ├── client.py         # kintone APIクライアント
│   ├── models.py         # Pydanticデータモデル
│   └── server.py         # MCPサーバー実装
└── tests/                # テストスイート
```

### 主要コンポーネント

#### 1. 認証システム (`auth.py`)
- **KintoneAuth**: 認証の基底抽象クラス
- **APITokenAuth**: APIトークン認証の実装（推奨）
- **PasswordAuth**: ユーザー名/パスワード認証の実装
- **create_auth()**: 設定から適切な認証インスタンスを生成

認証ヘッダーの生成とベースURLの管理を担当。

#### 2. APIクライアント (`client.py`)
- **KintoneClient**: kintone REST API v1との通信を管理
- `get_records()`: ページネーション付きレコード取得
- `get_all_records()`: 全レコード自動取得（ページネーション自動処理）
- `get_apps()`: アプリ情報の検索・取得（名前による部分一致検索対応）
- エラーハンドリング（KintoneAPIError）
- すべてのAPIリクエストをPOST + X-HTTP-Method-Overrideで実行

#### 3. MCPサーバー (`server.py`)
- **KintoneMCPServer**: MCP (Model Context Protocol) サーバーの実装
- ツールの登録と公開（`get_records`、`get_all_records`、`get_apps`）
- JSON-RPC通信の処理
- 非同期処理（asyncio）によるI/O効率化

#### 4. データモデル (`models.py`)
- Pydanticを使用した型安全なデータモデル
- kintoneのレコード構造を表現
- リクエスト/レスポンスのバリデーション
- アプリ情報用のモデル（AppInfo、UserInfo、GetAppsRequest/Response）

#### 5. エントリーポイント (`__main__.py`)
- 環境変数からの設定読み込み
- ロギングの設定
- サーバーインスタンスの作成と起動

### 設定管理
設定は以下の優先順位で読み込まれます：
1. 環境変数（`KINTONE_SUBDOMAIN`、`KINTONE_API_TOKEN`等）
2. `.env`ファイル（python-dotenvによる自動読み込み）

### 認証フロー
1. `load_config()`で設定を読み込み
2. `create_auth()`で認証タイプに応じた認証インスタンスを生成
3. 各APIリクエストで認証ヘッダーを自動付与

### エラー処理
- **KintoneAPIError**: kintone API固有のエラー（エラーコード、詳細情報を含む）
- 認証エラー、ネットワークエラーの適切な処理
- MCPプロトコルレベルでのエラーメッセージ返却

### 非同期処理
- MCPサーバーは非同期（asyncio）で動作
- kintone APIクライアントは同期的（requests）
- 将来的に非同期APIクライアントへの移行が可能な設計

### 拡張可能なポイント
- 新しいツール（レコード作成、更新、削除等）の追加は`server.py`の`_register_handlers()`で実装
- 新しい認証方式（OAuth等）は`auth.py`に新クラスを追加
- フィールドタイプの追加は`models.py`で対応

### 開発のベストプラクティス
- 型ヒントを必ず使用（MyPyでチェック）
- エラーメッセージは日本語/英語の両方を考慮
- kintone APIのレート制限（100回/分）を考慮した実装
- ページネーションの最大値は500レコード/リクエスト（アプリ一覧は100アプリ/リクエスト）

### APIリクエストの実装方針
- すべてのkintone REST APIリクエストはPOSTメソッドを使用
- 本来のHTTPメソッド（GET、PUT、DELETE等）はX-HTTP-Method-Overrideヘッダーで指定
- URLパラメータはJSONボディとして送信