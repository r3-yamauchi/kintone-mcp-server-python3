# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## よく使用されるコマンド

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
│   ├── __main__.py       # エントリーポイント
│   ├── auth.py           # 認証システム（APIトークン/パスワード）
│   ├── client.py         # kintone APIクライアント
│   ├── config.py         # 設定管理（Pydanticベース）
│   ├── constants.py      # 定数定義（API制限、ヘッダー名等）
│   ├── exceptions.py     # カスタム例外クラス
│   ├── models.py         # Pydanticデータモデル
│   ├── server.py         # MCPサーバー実装
│   ├── tools.py          # MCPツール定義レジストリ
│   └── utils.py          # ユーティリティ関数（バリデーション等）
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
- KintoneConfigを使用した設定読み込み
- ロギングレベルの動的設定
- サーバーインスタンスの作成と起動

#### 6. 設定管理 (`config.py`)
- **KintoneConfig**: Pydantic BaseSettingsを使用した設定クラス
- 環境変数の自動読み込みと検証
- `.env`ファイルのサポート
- 認証タイプに応じた必須パラメータの検証

#### 7. エラーハンドリング (`exceptions.py`)
- **KintoneError**: 基底例外クラス
- **KintoneAPIError**: API関連エラー（ステータスコード、エラーコード含む）
- **KintoneAuthError**: 認証エラー
- **KintoneConfigError**: 設定エラー
- **KintoneValidationError**: 入力検証エラー
- **KintoneRateLimitError**: レート制限エラー
- **KintoneNetworkError**: ネットワークエラー

#### 8. 定数管理 (`constants.py`)
- API制限値（MAX_RECORDS_PER_REQUEST = 500等）
- HTTPヘッダー名
- 認証タイプ定数
- エラーコード

#### 9. ツール定義 (`tools.py`)
- **TOOLS**: すべてのMCPツールの定義を辞書形式で管理
- 各ツールのスキーマ、説明、ハンドラー名を定義
- 新しいツールの追加が容易

#### 10. ユーティリティ (`utils.py`)
- **validate_file_path()**: ファイルパスの検証（パストラバーサル防止）
- **validate_app_id()**, **validate_record_id()**: ID検証
- **validate_limit()**: ページネーション制限値の検証
- **sanitize_query()**: クエリ文字列のサニタイズ
- **format_error_response()**: エラーレスポンスの統一フォーマット

### 設定管理
設定は`KintoneConfig`クラス（Pydantic BaseSettings）で管理：
1. 環境変数（`KINTONE_SUBDOMAIN`、`KINTONE_API_TOKEN`等）
2. `.env`ファイル（自動読み込み）
3. バリデーション付き（認証タイプに応じた必須フィールドチェック）

### 認証フロー
1. `KintoneConfig()`で設定を読み込み・検証
2. `config.to_auth_config()`で認証設定を生成
3. `create_auth()`で認証タイプに応じた認証インスタンスを生成
4. 各APIリクエストで認証ヘッダーを自動付与

### エラー処理
専用の例外クラス階層（`exceptions.py`）：
- **KintoneError**: 基底クラス（詳細情報を保持）
- **KintoneAPIError**: API固有エラー（ステータスコード、エラーコード、詳細を含む）
- **KintoneAuthError**: 認証関連エラー
- **KintoneValidationError**: 入力検証エラー
- **KintoneNetworkError**: ネットワーク関連エラー
- MCPプロトコルレベルでの統一されたエラーフォーマット

### 非同期処理
- MCPサーバーは非同期（asyncio）で動作
- kintone APIクライアントは同期的（requests）
- 将来的に非同期APIクライアントへの移行が可能な設計

### 拡張可能なポイント
- 新しいツールの追加は`tools.py`の`TOOLS`辞書に定義を追加
- 対応するハンドラーメソッドを`server.py`に実装
- 新しい認証方式（OAuth等）は`auth.py`に新クラスを追加
- フィールドタイプの追加は`models.py`で対応
- 定数の追加は`constants.py`に集約

### 開発のベストプラクティス
- 型ヒントを必ず使用（MyPyでチェック）
- エラーメッセージは日本語/英語の両方を考慮
- kintone APIのレート制限（100回/分）を考慮した実装
- 定数は`constants.py`に定義（マジックナンバーを避ける）
- バリデーションは`utils.py`の関数を使用
- 新しい例外は`exceptions.py`の階層に追加

### APIリクエストの実装方針
- すべてのkintone REST APIリクエストはPOSTメソッドを使用
- 本来のHTTPメソッド（GET、PUT、DELETE等）はX-HTTP-Method-Overrideヘッダーで指定
- URLパラメータはJSONボディとして送信
- エラーハンドリングは専用の例外クラスを使用

### 新しいkintone APIを追加する場合
1. `models.py`に必要なリクエスト/レスポンスモデルを追加
2. `client.py`に新しいAPIメソッドを実装
3. `tools.py`の`TOOLS`辞書に新しいツール定義を追加
4. `server.py`に対応するハンドラーメソッドを実装
5. 必要に応じて`constants.py`に定数を追加

### 利用可能なツール（2024年12月時点）
- **レコード操作**: get_record, get_records, get_all_records, add_record, add_records, update_record, update_records
- **コメント操作**: get_comments, add_comment
- **ステータス操作**: update_status, update_statuses
- **ファイル操作**: upload_file, download_file
- **アプリ情報**: get_app, get_apps, get_form_fields