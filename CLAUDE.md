# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## よく使用されるコマンド

### インストールとセットアップ
```bash
# 開発環境のセットアップ（編集可能インストール）
pip install -e ".[dev]"

# GitHubからインストール
pip install git+https://github.com/r3-yamauchi/kintone-mcp-server-python3.git

# uvxを使用した実行（インストール不要、推奨）
uvx --from git+https://github.com/r3-yamauchi/kintone-mcp-server-python3.git kintone-mcp-server-python3

# 環境変数の設定ファイルを作成
cp .env.example .env
# .envファイルを編集して認証情報を設定
```

### ビルドとパッケージング
```bash
# パッケージのビルド（hatchlingを使用）
python -m build

# ビルド成果物の確認
ls -la dist/

# GitHubへのプッシュ
git add .
git commit -m "Release vX.Y.Z"
git tag vX.Y.Z
git push origin main --tags
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

# pre-commitフックの設定（推奨）
pre-commit install
pre-commit run --all-files
```

### テスト実行
```bash
# すべてのテストを実行
pytest

# 詳細な出力付きでテスト実行
pytest -v

# 特定のテストファイルを実行
pytest tests/test_auth.py

# 特定のテストを実行
pytest tests/test_auth.py::test_api_token_auth

# カバレッジ付きでテスト実行
pytest --cov=kintone_mcp_server_python3 --cov-report=html

# 並列実行で高速化
pytest -n auto

# 失敗したテストのみ再実行
pytest --lf
```

### サーバーの起動
```bash
# 環境変数を使用して起動（パスワード認証）
export KINTONE_DOMAIN=your-subdomain.cybozu.com
export KINTONE_USERNAME=your-username@example.com
export KINTONE_PASSWORD=your-password
export KINTONE_LOG_LEVEL=INFO
python3 -m kintone_mcp_server_python3

# 環境変数を使用して起動（APIトークン認証）
export KINTONE_DOMAIN=your-subdomain.cybozu.com
export KINTONE_API_TOKEN=your-api-token
export KINTONE_LOG_LEVEL=INFO
python3 -m kintone_mcp_server_python3

# .envファイルを使用して起動
python3 -m kintone_mcp_server_python3

# 開発環境から直接起動
python3 src/kintone_mcp_server_python3/__main__.py

# uvxを使用（推奨）
uvx --from git+https://github.com/r3-yamauchi/kintone-mcp-server-python3.git kintone-mcp-server-python3

# デバッグモードで起動
KINTONE_LOG_LEVEL=DEBUG uvx --from git+https://github.com/r3-yamauchi/kintone-mcp-server-python3.git kintone-mcp-server-python3
```

### 開発用コマンド
```bash
# 依存関係の更新
pip install --upgrade -e ".[dev]"

# 環境のクリーンアップ
rm -rf build/ dist/ *.egg-info/
find . -type d -name "__pycache__" -exec rm -rf {} +

# ログの確認（デバッグ時）
tail -f /path/to/log/file

# MCPクライアントの設定確認
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json | jq .

# プロセスの確認（デバッグ用）
ps aux | grep kintone-mcp-server

# 仮想環境の作成（推奨）
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows
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
├── tests/                # テストスイート
├── .env.example          # 環境変数の設定例
├── pyproject.toml        # プロジェクト設定、依存関係
├── LICENSE               # MITライセンス
└── README.md             # プロジェクトドキュメント
```

### 主要コンポーネント

#### 1. 認証システム (`auth.py`)
- **KintoneAuth**: 認証の基底抽象クラス
- **APITokenAuth**: APIトークン認証の実装
- **PasswordAuth**: ユーザー名/パスワード認証の実装
- **create_auth()**: 設定から適切な認証インスタンスを生成

認証ヘッダーの生成とベースURLの管理を担当。

**認証の優先順位**:
1. ユーザー名とパスワードの両方が指定されている場合 → パスワード認証
2. APIトークンのみが指定されている場合 → APIトークン認証
3. いずれも指定されていない場合 → エラー

```python
# 使用例
auth = create_auth(auth_config)
headers = auth.get_auth_headers()
base_url = auth.get_base_url()
```

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
- 認証方法の自動判定（`get_auth_type()`メソッド）
- 環境変数プレフィックス: `KINTONE_`

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
1. 環境変数（`KINTONE_DOMAIN`、`KINTONE_API_TOKEN`等）
2. `.env`ファイル（自動読み込み）
3. バリデーション付き（認証情報の検証）
4. 認証方法は自動判定（KINTONE_AUTH_TYPE廃止）

### 認証フロー
1. `KintoneConfig()`で設定を読み込み・検証
2. `config.get_auth_type()`で認証方法を自動判定
3. `config.to_auth_config()`で認証設定を生成
4. `create_auth()`で認証タイプに応じた認証インスタンスを生成
5. 各APIリクエストで認証ヘッダーを自動付与

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

### テスト戦略
- **単体テスト**: 各コンポーネントの独立したテスト
- **統合テスト**: APIクライアントとサーバーの連携テスト
- **モックの使用**: 外部API呼び出しはモック化
- **テストカバレッジ**: 80%以上を目標
- **エッジケース**: 境界値、エラーケースを重点的にテスト

### パフォーマンス最適化
- **バッチ処理**: 大量データは`add_records`、`update_records`を使用
- **ページネーション**: 大量レコード取得時は適切なlimit設定
- **キャッシュ**: 頻繁にアクセスするアプリ情報はキャッシュ検討
- **非同期処理**: MCPサーバーレベルでの非同期処理を活用
- **接続プーリング**: requests.Sessionを使用した接続再利用

### セキュリティ考慮事項
- **認証情報**: 環境変数または.envファイルで管理
- **入力検証**: すべての入力をサニタイズ（utils.py）
- **パストラバーサル防止**: ファイルパスの検証を徹底
- **エラー情報**: 内部構造を露出しないエラーメッセージ
- **ログ**: センシティブ情報をログに出力しない

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
- ドキュメント文字列（docstring）を必ず記述
- コミットメッセージは明確で簡潔に

### APIリクエストの実装方針
- すべてのkintone REST APIリクエストはPOSTメソッドを使用
- 本来のHTTPメソッド（GET、PUT、DELETE等）はX-HTTP-Method-Overrideヘッダーで指定
- URLパラメータはJSONボディとして送信
- エラーハンドリングは専用の例外クラスを使用
- レスポンスの型変換はPydanticモデルで実施

### 新しいkintone APIを追加する場合
1. `models.py`に必要なリクエスト/レスポンスモデルを追加
   ```python
   # 例: 新しいAPIのモデル
   class NewFeatureRequest(BaseModel):
       app: int
       field: str
   ```

2. `client.py`に新しいAPIメソッドを実装（docstring必須）
   ```python
   def new_feature(self, app: int, field: str) -> dict:
       """新機能の実装."""
       # 実装
   ```

3. `tools.py`の`TOOLS`辞書に新しいツール定義を追加
   ```python
   "new_feature": {
       "description": "新機能の説明",
       "handler": "_new_feature",
       "schema": {...}
   }
   ```

4. `server.py`に対応するハンドラーメソッドを実装
5. 必要に応じて`constants.py`に定数を追加
6. `tests/`に対応するテストケースを追加
7. README.mdの使用例セクションを更新

### トラブルシューティングガイド

#### 接続エラー
```bash
# ドメインの確認
echo $KINTONE_DOMAIN
# ネットワーク接続の確認
curl -I https://$KINTONE_DOMAIN
```

#### 認証エラー
- APIトークンの権限を確認（レコード閲覧、追加、編集等）
- APIトークンが有効になっているか確認
- パスワード認証の場合、2要素認証の設定を確認

#### レート制限エラー
```python
# バッチ処理の例
records = [...]  # 大量のレコード
for i in range(0, len(records), 100):
    batch = records[i:i+100]
    client.add_records(app_id, batch)
    time.sleep(1)  # 1秒待機
```

#### デバッグ方法
```bash
# 詳細ログを有効化
KINTONE_LOG_LEVEL=DEBUG python -m kintone_mcp_server_python3

# リクエスト/レスポンスの確認
# client.pyに以下を追加
import logging
logging.basicConfig(level=logging.DEBUG)
```

### リリースプロセス
1. すべてのテストが成功することを確認
2. CHANGELOGを更新
3. バージョン番号を更新（pyproject.toml）
4. タグを作成してGitHubにプッシュ
5. リリースノートを作成（必要に応じて）

### 重要な設定変更（2025年1月更新）

#### 認証方法の自動判定
- `KINTONE_AUTH_TYPE` 環境変数は廃止されました
- 認証方法は以下の優先順位で自動的に決定されます：
  1. `KINTONE_USERNAME` と `KINTONE_PASSWORD` の両方が指定 → パスワード認証
  2. `KINTONE_API_TOKEN` のみが指定 → APIトークン認証
  3. いずれも指定なし → エラー

#### ドメイン設定の統一
- `KINTONE_SUBDOMAIN` 環境変数は廃止されました
- `KINTONE_DOMAIN` にサブドメインを含む完全なドメイン名を指定します
  - 例: `dev-demo.cybozu.com`, `example.kintone.com`, `your-subdomain.cybozu.cn`

#### APIトークンの仕様
- APIトークンは最大9個までカンマ区切りで指定可能
- 例: `KINTONE_API_TOKEN=token1,token2,token3`

### 利用可能なツール（2025年1月時点）

#### レコード操作

- **get_record**: 単一レコードの取得
  - 必須: `app` (アプリID), `id` (レコードID)
- **get_records**: レコード一覧の取得（ページネーション付き）
  - 必須: `app` (アプリID)
  - オプション: `query`, `fields`, `limit` (最大500), `offset`
- **get_all_records**: 全レコードの自動取得（ページネーション自動処理）
  - 必須: `app` (アプリID)
  - オプション: `query`, `fields`
- **add_record**: 単一レコードの追加
  - 必須: `app` (アプリID), `record` (フィールドデータ)
- **add_records**: 複数レコードの一括追加（最大100件）
  - 必須: `app` (アプリID), `records` (レコード配列)
- **update_record**: 単一レコードの更新
  - 必須: `app` (アプリID), `record` (更新データ)
  - いずれか必須: `id` または `update_key`
- **update_records**: 複数レコードの一括更新（最大100件）
  - 必須: `app` (アプリID), `records` (更新データ配列)

#### コメント・ステータス操作

- **get_comments**: レコードのコメント取得
  - 必須: `app` (アプリID), `record` (レコードID)
  - オプション: `order`, `offset`, `limit` (最大10)
- **add_comment**: レコードへのコメント追加（メンション対応）
  - 必須: `app` (アプリID), `record` (レコードID), `text`
  - オプション: `mentions` (メンション情報配列)
- **update_status**: レコードのステータス更新（プロセス管理）
  - 必須: `app` (アプリID), `id` (レコードID), `action`
  - オプション: `assignee`, `revision`
- **update_statuses**: 複数レコードのステータス一括更新（最大100件）
  - 必須: `app` (アプリID), `records` (ステータス更新配列)

#### ファイル操作

- **upload_file**: ファイルのアップロード（最大10MB）
  - 必須: `file_path` (アップロードするファイルパス)
- **download_file**: ファイルのダウンロード
  - 必須: `file_key`, `save_path` (保存先パス)

#### アプリ管理

- **get_app**: アプリ情報の取得
  - 必須: `id` (アプリID)
- **get_apps**: アプリ一覧の検索・取得（名前検索対応）
  - オプション: `name` (部分一致), `ids`, `codes`, `space_ids`, `limit`, `offset`
- **get_form_fields**: フォームフィールド設定の取得（多言語対応）
  - 必須: `app` (アプリID)
  - オプション: `lang` (言語コード: ja, en, zh, es)