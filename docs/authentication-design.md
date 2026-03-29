# 認証認可設計書

## 1. 目的

このアプリケーションに、将来的な AWS Cognito 利用を前提とした認証認可基盤を導入する。

ただしローカル開発では Cognito に直接依存せず、開発用の JWT 発行機構を用いて開発を進める。重要なのは、ローカル実装と本番実装でトークン検証の中核ロジックを変えないことである。

そのため、ローカル開発でも以下を満たす構成を採用する。

- JWT は秘密鍵で署名する
- JWT ヘッダーに `kid` を含める
- 公開鍵は `/.well-known/jwks.json` で公開する
- FastAPI 側は JWKS エンドポイントから公開鍵を取得して検証する

この構成により、将来 Cognito へ移行する際は、JWT の発行元と JWKS URL を切り替えるだけで済む状態を目指す。

## 2. 前提

### 2.1 技術スタック

- フロントエンド: React + Vite
- バックエンド: FastAPI
- JWT ライブラリ: `python-jose`

### 2.2 認証と認可の責務分離

- 認証: 「このトークンは正しいか」「誰のトークンか」を判定する
- 認可: 「そのユーザーがこの操作をしてよいか」を判定する

認証は JWT 検証と claim 解釈で行い、認可はアプリケーション側のロール/権限判定で行う。

将来 Cognito の Group claim を使う可能性はあるが、認可ロジックそのものは Cognito 依存にしない。

## 3. 目標アーキテクチャ

## 3.1 全体像

ローカル開発時の構成は以下を想定する。

1. 開発用ログイン API が認証成功時に JWT を発行する
2. JWT は RS256 で署名する
3. 公開鍵はバックエンドの `/.well-known/jwks.json` から取得できる
4. 保護 API は Bearer token を受け取り、JWKS を使って署名検証する
5. 検証済み claim を `current_user` に正規化して認可へ渡す

## 3.2 将来の Cognito 移行時

将来 Cognito に切り替える場合に変更するのは主に以下だけとする。

- JWT の発行元をローカル issuer から Cognito に変更する
- JWKS URL をローカルの `/.well-known/jwks.json` から Cognito の JWKS エンドポイントに変更する
- 必要に応じて claim のマッピングを微調整する

一方で、以下は極力変えない。

- FastAPI 側の validator の基本フロー
- `Authorization: Bearer <token>` の受け渡し
- `get_current_user` の利用パターン
- アプリ側の認可 dependency

## 4. JWT 設計

## 4.1 署名方式

ローカル開発でも HS256 は使わず、Cognito と同様に公開鍵暗号方式を使う。

- アルゴリズム: `RS256`
- 発行ライブラリ: `python-jose`
- JWT ヘッダー: `alg`, `typ`, `kid` を含める

`kid` を最初から使うことで、鍵ローテーションや複数鍵運用を見据えた validator を組める。

## 4.2 想定 claims

最低限、以下の claim を利用対象とする。

### 標準 claim

- `sub`: ユーザー識別子
- `iss`: issuer
- `aud`: audience
- `iat`: 発行時刻
- `exp`: 有効期限

### アプリケーション claim

- `email`: ユーザーのメールアドレス
- `roles`: アプリケーションが扱うロール一覧

必要に応じて、将来的には以下も検討できる。

- `scope`
- `tenant_id`
- `preferred_username`

## 4.3 claim の扱い

JWT の claim はそのまま業務ロジックに流し込まず、FastAPI 側で `current_user` へ正規化する。

例えば以下のような内部表現を想定する。

```python
{
    "subject": "...",
    "email": "...",
    "roles": ["admin", "viewer"],
    "issuer": "...",
}
```

これにより、ローカル JWT と Cognito JWT の差異を dependency 層で吸収しやすくなる。

## 5. JWKS ベース検証

## 5.1 採用理由

Cognito は JWT を秘密鍵で署名し、公開鍵を `/.well-known/jwks.json` で公開する。

ローカル開発でも同じ検証フローを採用しない場合、本番移行時に validator の本体を書き換える必要が出る。そのため、ローカル段階から JWKS ベース検証を採用する。

## 5.2 FastAPI 側 validator の基本フロー

validator は以下の順序で検証する。

1. `Authorization` ヘッダーを取得する
2. `Bearer` トークン形式を検証する
3. JWT ヘッダーを decode して `kid` を取得する
4. 設定された JWKS URL から鍵セットを取得する
5. `kid` に一致する JWK を選択する
6. JWK から公開鍵を解決する
7. `iss`, `aud`, `exp`, 署名を検証する
8. claim を `current_user` 用の内部表現へ正規化する

この流れは、ローカルでも Cognito でも共通とする。

## 5.3 JWKS エンドポイント

ローカル開発用のバックエンドに `/.well-known/jwks.json` を用意する。

レスポンス形式は標準的な JWKS 形式に従う。

```json
{
  "keys": [
    {
      "kty": "RSA",
      "kid": "local-dev-key-1",
      "use": "sig",
      "alg": "RS256",
      "n": "...",
      "e": "AQAB"
    }
  ]
}
```

将来の鍵ローテーションを考慮し、単一鍵でも `keys` 配列で返す。

## 5.4 キャッシュ方針

JWKS は毎回取得せず、validator 側にキャッシュを持たせる。

設計上は以下を想定する。

- 一定時間メモリキャッシュする
- `kid` 不一致時は再取得を試みる
- 取得失敗時は明示的に認証エラーとする

これにより、外部依存を減らしつつ、鍵更新にも追従しやすくする。

## 6. FastAPI 側の責務

## 6.1 設定

認証まわりの設定は `Settings` に集約する。

想定する設定値:

- `auth_issuer`
- `auth_audience`
- `auth_jwks_url`
- `auth_algorithm`
- `auth_access_token_ttl_minutes`
- `auth_local_private_key_path`
- `auth_local_public_key_path`
- `auth_local_key_id`

ローカル環境ではこれらを `.env` で持ち、本番では Cognito の値に切り替える。

## 6.2 認証 dependency

FastAPI では `get_current_user` のような dependency を用意する。

責務は以下の通り。

- Authorization ヘッダーを読む
- validator を呼ぶ
- claim を内部表現へ正規化する
- ルートハンドラーへ安全な user context を渡す

さらに認可用に、例えば以下のような dependency を追加できるようにする。

- `require_authenticated_user`
- `require_roles([...])`

## 6.3 エラーハンドリング

認証失敗は曖昧にせず、理由ごとに制御する。

例:

- Authorization ヘッダーがない
- Bearer 形式でない
- `kid` がない
- `kid` に対応する鍵が JWKS にない
- `iss` が一致しない
- `aud` が一致しない
- 署名検証に失敗
- 有効期限切れ

ユーザーへの返却は `401 Unauthorized` または `403 Forbidden` を適切に使い分ける。

## 7. 認可設計

認可は JWT 発行元の製品仕様ではなく、アプリケーションのルールとして定義する。

最低限、以下の考え方を採用する。

- ロールはアプリケーションが理解できる名前で保持する
- ルートごとに必要ロールを定義する
- Cognito Group は将来的にロールの入力元になりうるが、認可判定そのものではない

例:

- `admin`
- `operator`
- `viewer`

FastAPI 側では、`roles` claim を正規化したうえで dependency で判定する。

## 8. フロントエンド設計

フロントエンドでは、認証状態と API 呼び出し時の token 付与を統一する。

最低限必要な要素は以下。

- auth state の保持
- ログイン画面の表示
- ログイン API 呼び出し
- token の保存
- API リクエスト時の `Authorization` ヘッダー付与
- 未認証時の画面制御

## 8.1 token 保持

初期案としてはローカル開発のシンプルさを優先し、クライアント側で token を保持する。

ただし、本番設計では保存先の見直しを行う余地を残す。

## 8.2 ログイン画面

フロントエンドには専用のログイン画面を作成する。

この画面の責務は以下とする。

- メールアドレスとパスワードの入力を受け付ける
- ログイン API を呼び出す
- 成功時に access token を保存して認証状態を更新する
- 失敗時にエラーメッセージを表示する
- 認証後に保護された画面へ遷移させる

ログイン画面は、将来 Cognito Hosted UI や外部 IdP 連携へ切り替える場合でも、認証開始地点として置き換えやすい構造にしておく。

## 8.3 API クライアント

各画面で `fetch` を直接ばらばらに書くのではなく、Bearer token を付与する共通処理へ寄せる。

これにより、トークン更新やエラー処理をまとめやすくする。

## 9. 監査ログとの連携

既存の監査ログでは、将来的にユーザー情報を残せる形が望ましい。

そのため、認証成功後に得られた subject や user identifier を request context へ格納し、監査ログミドルウェアが参照できる構成を想定する。

最低限、以下のような情報を連携対象とする。

- `sub`
- 必要に応じて `email`

ただし、監査ログには過剰な個人情報を入れすぎない。

## 10. 実装方針

実装は以下の順で進める。

1. 認証設定を追加する
2. ローカル開発用の RSA 鍵運用方針を定める
3. `python-jose` を使った JWT issuer を追加する
4. `/.well-known/jwks.json` を追加する
5. JWKS ベース validator を追加する
6. `get_current_user` と認可 dependency を追加する
7. 既存 API の保護を始める
8. フロントエンドのログイン画面を追加する
9. フロントエンドの auth state とヘッダー付与を追加する
10. 監査ログとの連携を入れる

## 11. 移行時に守るべき原則

AWS Cognito へ移行するときも、以下は維持する。

- トークン検証は JWKS ベース
- API は Bearer token を受け取る
- 認可はアプリケーション dependency で行う
- claim は内部 user context に正規化してから使う

これにより、認証基盤の差し替えは設定変更と claim mapping の調整に閉じ込めやすくなる。

## 12. 非目標

この設計書では、現時点では以下を対象外とする。

- 完全なユーザー管理 UI
- パスワードリセットや多要素認証の詳細仕様
- 本番向けセキュリティハードニングの最終形
- Cognito Hosted UI の詳細導線
- Refresh Token の詳細な回転戦略

これらは今後の要件確定後に別途詳細化する。
