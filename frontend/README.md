# モノリス フロントエンド

モノリスアプリケーションのフロントエンドです。React と Vite で構築されており、バックエンド API と連携するためのモダンなダッシュボードスタイルの UI を備えています。

## ✨ 主な特徴

- **モダンなUI**: [ShadCN/UI](https://ui.shadcn.com/) と [Tailwind CSS](https://tailwindcss.com/) で構築されています。
- **効率的なデータフェッチ**: [TanStack Query](https://tanstack.com/query) を使用して、バックエンドからデータを取得し、キャッシュします。
- **高速な開発体験**: [Vite](https://vitejs.dev/) により、高速で無駄のない開発体験を提供します。
- **アイコン**: [lucide-react](https://lucide.dev/guide/packages/lucide-react) アイコンライブラリを使用しています。

## 🛠️ 使用技術

- **フレームワーク**: [React](https://react.dev/)
- **ビルドツール**: [Vite](https://vitejs.dev/)
- **スタイリング**: [Tailwind CSS](https://tailwindcss.com/)
- **コンポーネントライブラリ**: [ShadCN/UI](https://ui.shadcn.com/)
- **データフェッチ**: [TanStack Query](https://tanstack.com/query)
- **アイコン**: [lucide-react](https://lucide.dev/guide/packages/lucide-react)

## 🚀 セットアップ方法

### 前提条件

- [Node.js](https://nodejs.org/) (`package.json` の `engines` フィールドで推奨されているバージョン)
- [npm](https://www.npmjs.com/)

### インストール

1.  `frontend` ディレクトリに移動します:
    ```bash
    cd frontend
    ```
2.  依存関係をインストールします:
    ```bash
    npm install
    ```

### 開発サーバーの起動

1.  バックエンドサーバーが起動していることを確認してください。
2.  `frontend` ディレクトリで、以下のコマンドを実行します:
    ```bash
    npm run dev
    ```
3.  ブラウザを開き、`http://localhost:5173` （またはコンソールに表示されるポート）にアクセスします。

## ⚙️ 設定

- **APIプロキシ**: Vite 開発サーバーは、`/users` へのリクエストを `http://localhost:8000` で実行されているバックエンドサーバーにプロキシするように設定されています。この設定は `vite.config.js` で行われています。
- **CORS**: バックエンドは、フロントエンドのオリジン (`http://localhost:5173`) からのリクエストを受け入れるように設定する必要があります。これはバックエンドの `main.py` にある `CORSMiddleware` で処理されます。
