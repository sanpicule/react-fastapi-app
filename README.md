## プロジェクト概要

FastAPI + SQLAlchemy を用いたモノリシックなバックエンド API サーバーです。  
ローカルの PostgreSQL データベースに接続し、Alembic によるマイグレーションでスキーマ管理を行います。

---

## 前提条件

- macOS（他 OS でも構成は同様ですが、コマンドは適宜読み替えてください）
- Python は `uv` が自動で管理します
- `uv` がインストール済み
- Homebrew がインストール済み（PostgreSQL 用）

### uv のインストール（未インストールの場合）

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

インストール後、シェルを再起動するか、`eval "$(uv generate-shell-completion zsh)"` などで補完を有効化します（任意）。

---

## セットアップの流れ（ざっくり）

1. `.env` の作成（DB 接続設定など）
2. PostgreSQL のインストール & 起動
3. DB ユーザー / データベース作成
4. 依存パッケージのインストール（`uv sync`）
5. マイグレーション実行（`alembic upgrade head`）
6. バックエンドサーバー起動（`uvicorn`）
7. Swagger UI で動作確認
8. `psql` で DB の中身を簡易確認

以下で順に説明します。

---

## 1. `.env` の作成

プロジェクトルート（`/Users/hiwadasanshirou/Documents/my_monolith`）に `.env` ファイルを作成し、少なくとも以下を設定します。

```env
# SQLAlchemy から利用する DB 接続 URL
# ドライバは pyproject.toml の依存に合わせて psycopg を利用します
DATABASE_URL=postgresql+psycopg://monolith:monolith@localhost:5432/my_monolith
```

環境変数は `app/core/config.py` の `Settings` クラスから読み込まれます。

必要であれば、今後追加される設定も `.env` に追記してください。

---

## 2. PostgreSQL のインストール & 起動（macOS / Homebrew）

### 2-1. インストール（初回のみ）

```bash
brew install postgresql@16
```

### 2-2. サービス起動

```bash
brew services start postgresql@16
```

起動状態は次のコマンドで確認できます。

```bash
brew services list | grep postgresql
```

---

## 3. DB ユーザー / データベース作成（初回のみ）

PostgreSQL が起動している状態で、以下を実行します。

```bash
psql postgres <<'SQL'
CREATE ROLE monolith WITH LOGIN PASSWORD 'monolith';
ALTER ROLE monolith CREATEDB;
CREATE DATABASE my_monolith OWNER monolith;
SQL
```

- ユーザー名: `monolith`
- パスワード: `monolith`
- データベース名: `my_monolith`

`.env` の `DATABASE_URL` と整合していることを確認してください。

---

## 4. 依存パッケージのインストール

プロジェクトルートで以下を実行します。

```bash
cd /Users/hiwadasanshirou/Documents/my_monolith
uv sync
```

- `pyproject.toml` / `uv.lock` を元に、仮想環境の作成と依存インストールが行われます。

---

## 5. DB マイグレーションの実行

DB のテーブル定義を最新にするため、Alembic のマイグレーションを適用します。

```bash
cd /Users/hiwadasanshirou/Documents/my_monolith
uv run alembic upgrade head
```

- `alembic/env.py` から `settings.database_url`（`.env` の `DATABASE_URL`）が利用されます。
- `.env` が未設定、もしくは PostgreSQL が起動していないとエラーになります。

---

## 6. バックエンドサーバーの起動

仮想環境や Python のバージョンは `uv` がよしなに扱うので、そのまま以下を実行します。

```bash
cd /Users/hiwadasanshirou/Documents/my_monolith
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- `--reload` によりソースコード変更時に自動リロードされます（開発用）。
- 起動ログに `Application startup complete.` と表示されれば成功です。

サーバー停止はターミナルで `Ctrl + C` です。

---

## 7. Swagger UI（OpenAPI ドキュメント）の確認

サーバー起動後、ブラウザで次の URL にアクセスします。

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

Swagger UI 上からは以下ができます。

- 各エンドポイントの仕様確認
- リクエストパラメータ / レスポンススキーマの確認
- 「Try it out」を使った実際の API 呼び出しテスト

---

## 8. DB を簡易的に確認する方法

### 8-1. `psql` でテーブル一覧・レコード確認

```bash
psql -h localhost -U monolith -d my_monolith
```

パスワードは `monolith`（3章で作成したユーザーのパスワード）です。

対話シェルに入ったら、例えば次のコマンドでテーブルやデータを確認できます。

```sql
-- テーブル一覧
\dt

-- 特定テーブルのカラム情報
\d users

-- データ確認
SELECT * FROM users LIMIT 10;
```

### 8-2. SQL を一発で投げる（非対話）

```bash
psql -h localhost -U monolith -d my_monolith -c "SELECT * FROM users LIMIT 5;"
```

---

## ディレクトリ構成（概要）

```text
app/
  api/          # FastAPI のルーター定義
  core/         # 設定などのコア部分（.env 読み込みなど）
  db/           # DB セッションや Base モデル
  dependencies/ # FastAPI の Depends 用依存定義
  models/       # SQLAlchemy モデル
  repositories/ # DB アクセスロジック
  schemas/      # Pydantic スキーマ
  service/      # ドメインロジック層
  main.py       # FastAPI アプリエントリポイント
alembic/        # マイグレーションスクリプト
```

---

## トラブルシューティング

- **DB に接続できない**
  - `.env` の `DATABASE_URL` が正しいか（ユーザー名 / パスワード / DB 名）
  - PostgreSQL サービスが起動しているか  
    `brew services list | grep postgresql` で確認
  - ファイアウォールやポート競合がないか（通常ローカル開発では問題になりにくい）

- **マイグレーションに失敗する**
  - `uv run alembic upgrade head` のエラーメッセージを確認
  - 既存の DB スキーマと競合している場合は、一旦 DB を削除して作り直すか、手動で調整してください。

- **FastAPI 起動時に例外が発生する**
  - `.env` がない / `DATABASE_URL` が未設定だと起動時にエラーになります。
  - 依存関係が不足していそうな場合は、`uv sync` を再実行してください。

---

## 開発時のよく使うコマンドまとめ

```bash
# 依存関係インストール
uv sync

# DB マイグレーションを最新に
uv run alembic upgrade head

# バックエンド起動（ホットリロード有り）
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# PostgreSQL 起動（macOS/Homebrew）
brew services start postgresql@16
```

この README の内容に従えば、ゼロから環境構築して API を叩ける状態まで持っていける想定です。不足や不整合があれば、実際のエラー内容とあわせて調整していってください。



