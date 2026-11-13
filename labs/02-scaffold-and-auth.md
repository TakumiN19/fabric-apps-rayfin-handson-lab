# Lab 02 — Rayfin Universal App の作成・構成理解・Fabric Entra SSO 認証

所要時間: 約 20 分
前提:
- [Lab 00](00-prerequisites.md) 完了
- [Lab 01](01-seed-fabric-foundation.md) の 1-1・1-2（サインインとワークスペース確認）完了

このラボでは、**Fabric Apps by Rayfin（v1.36.2）** の標準スターターである **Universal App** をスキャフォールドし、Rayfin アプリの内部構造（`rayfin/rayfin.yml`、Capability Router、ドキュメント MCP）を理解したうえで、**Microsoft Entra ID（Fabric SSO）認証**を組み込み、Fabric ワークスペースへ最初のネイティブ `AppBackend` アイテムとしてデプロイします。

```text
npm create @microsoft/rayfin@latest (Universal App)
   │
   ├─ AGENTS.md + .agents/skills/capability-router/ (必要な機能パックだけを段階有効化)
   ├─ .mcp.json (@microsoft/rayfin-mcp: バージョン固定 SDK ドキュメント検索)
   ├─ rayfin/rayfin.yml (auth / data / staticHosting / functions / storage / connectors)
   │
   ▼ authentication パック有効化 ＋ npx rayfin up
[ Fabric Workspace: smart-ops-hub (AppBackend) ] ──▶ Entra SSO 保護された Web アプリ公開！
```

---

## 2-1. Universal App テンプレートで `smart-ops-hub` を作成する

Rayfin 1.36.2 の既定スキャフォールドは、最初は最小構成の React + Vite アプリとして立ち上がり、AI エージェントが要件に応じて必要なサービス・スキルだけを有効化していく **Universal App（Capability Router 内蔵）** 構造を採用しています。

> 🗣️ **プロンプト**
> ```text
> Rayfin CLI を使って、ルート直下に `smart-ops-hub` という Fabric App プロジェクトを作成して依存関係をインストールして。
> 作成後、生成されたディレクトリ構成、`rayfin/rayfin.yml`、同梱された AI スキル（`.agents/skills/`）と `.mcp.json` の役割を整理して教えて。
> ```

🤖 **Copilot の動き**
- `rayfin@rayfin-skills` に従い、`npm create @microsoft/rayfin@latest smart-ops-hub`（または `npx @microsoft/rayfin-cli init smart-ops-hub`）を実行し、`npm install` まで完了します。
- 自動配置された `AGENTS.md`、`.mcp.json`、`.agents/skills/`、`rayfin/rayfin.yml` を読み取り、構成をわかりやすく要約します。

✅ **期待する結果**
`smart-ops-hub/` が作成され、次のコア要素が確認できる：

| パス | 役割 |
|------|------|
| `rayfin/rayfin.yml` | Fabric Apps のバックエンド宣言ファイル（`auth`, `data`, `staticHosting` 等の有効／無効と設定） |
| `AGENTS.md` / `.agents/skills/` | **Capability Router** と機能別スキル（`authentication`, `data-modeling`, `graphein-visuals`, `analytics` 等）。エージェントが API を推測せず正しい手順を踏むための設計図 |
| `.mcp.json` | `@microsoft/rayfin-mcp` サーバー設定（`search_docs`, `discover_packages`, `get_doc` で `node_modules` 内のバージョン一致ドキュメントを検索） |
| `src/`（または `packages/frontend/src/`） | React 19 + TypeScript (ES2022) + Vite + Tailwind CSS v4 フロントエンド |

> 💡 **エージェント時代の Rayfin 最大の特徴**:
> 各 `@microsoft/rayfin-*` パッケージは自身の `assets/docs/` にドキュメントを同梱しています。CLI でも `npx rayfin docs discover` / `npx rayfin docs search "permissions"` のように、**インストール済みバージョンと 100% 一致する仕様**を引くことができます。

---

## 2-2. ローカル静的プレビュー（バックエンド不要）を確認する

デプロイ前に、まずはフロントエンド単体でビルドとローカルプレビューが通ることを確認します。

> 🗣️ **プロンプト**
> ```text
> smart-ops-hub の型チェックとビルドが通ることを確認して、
> Rayfin CLI のドキュメント検索コマンドで fabric authentication の仕様ページを確認して。
> ```

🤖 **Copilot の動き**
- `smart-ops-hub` 内で `npm run build` を実行し、TypeScript コンパイルと Vite バンドルが正常終了することを確認します。
- `npx rayfin docs search "fabric authentication"`（または同梱スキル参照）で、現在の SDK バージョンにおける Fabric SSO 実装方法を確認します。

✅ **期待する結果**
`dist/` がエラーなく生成され、Fabric SSO プロバイダー（`@microsoft/rayfin-auth-provider-fabric`）の仕様が確認できる。

---

## 2-3. Fabric Entra SSO 認証（`authentication` パック）を組み込む

`Smart Ops Hub` のヘッダーを作成し、サインイン中の Microsoft Entra ユーザー情報（表示名／メールアドレス・セッション状態）を表示できるようにします。また、ローカルプレビュー（`localhost` でバックエンド未接続時）でも白い画面でクラッシュせず、開発モードであることが分かるようにします。

> 🗣️ **プロンプト**
> ```text
> smart-ops-hub に Fabric Entra SSO 認証を有効化して組み込んで。
> - Universal App の authentication スキルに従い、`rayfin/rayfin.yml` で `services.auth.enabled: true` と `fabric.enabled: true`、`allowedRedirectUris`（localhost:5173 を含む）を設定する
> - ポータル埋め込み時（`initEmbeddedAuth`）とスタンドアロン表示時（ユーザークリックでの `ensureSignedInWithFabric` ポップアップ）の両方に対応させる
> - セッション変更の購読には `client.auth.onSessionChange` を使う（`onAuthStateChange` は使わない）
> - アプリ名を「Smart Ops Hub」にし、ヘッダー右上にサインイン状態バッジ（認証済みユーザー識別子／サインアウトボタン、未接続ローカル時は `Preview Mode` バッジ）を表示して
> ```

🤖 **Copilot の動き**
- `.agents/skills/authentication/SKILL.md` と `@microsoft/rayfin-auth-provider-fabric` のドキュメントを参照します。
- `ensureSignedInWithFabric` はポップアップを開くため **ボタンクリック等のユーザー操作（user gesture）** から呼び出し、ポータル iframe 内では `initEmbeddedAuth` でシームレスにハンドシェイクするよう実装します。
- `npm run build` と `npm test`（存在する場合）を実行して型エラーがないことを検証します。

> ⚠️ **認証の重要ポイント（つまずき防止）**:
> 1. **デプロイ環境で使える認証は Entra SSO のみ**: メール／パスワード認証（`password.enabled: true`）はローカル Docker 実験モード専用です。本番・Fabric 環境では Fabric SSO を使います。
> 2. **`onSessionChange` を使う**: 他社 BaaS（Supabase 等）の記憶で AI が `onAuthStateChange` と書きがちですが、Rayfin Auth Client の正しいメソッド名は **`onSessionChange`** です。
> 3. **ポップアップブロック回避**: 初回ロードの `useEffect` 内でいきなり `ensureSignedInWithFabric` を呼ぶとブラウザにポップアップブロックされます。「Fabric でサインイン」ボタンの `onClick` から呼び出します。

✅ **期待する結果**
認証プロバイダーとヘッダー UI が実装され、`npm run build` がグリーンで完了する。

---

## 2-4. 自分の Fabric ワークスペースへ初回デプロイ（`rayfin up`）する

いよいよ `smart-ops-hub` を自分のワークスペースへデプロイし、Fabric 上のネイティブアイテムとして公開します。

> 🗣️ **プロンプト**
> ```text
> smart-ops-hub を自分の Fabric ワークスペースにデプロイして。
> まず `--dry-run` で設定を検証してから本デプロイを実行し、完了後に `rayfin up status`、公開 URL、Fabric ポータルのアイテムリンクを教えて。
> ```

🤖 **Copilot の動き**
- `.github/student.local.md` のワークスペース名／`Workspace ID` とテナント ID を照合します。
- `npx rayfin up --workspace-id "$WS_ID" --dry-run` で `rayfin.yml` の構文検証を行います。
- `npx rayfin up --workspace-id "$WS_ID" --yes` を実行し、`AppBackend` アイテムと管理対象 SQL Database（`data.enabled: true` の場合）をプロビジョニングし、静的アセットを OneLake へアップロードします（初回は 2〜5 分ほどかかります）。
- `npx rayfin up status` でサービス状態を確認し、公開 URL（`https://<app>-app.rayfin.windows.net/` または `*.webapp.fabricapps.net`）と Fabric ポータル URL を表示します。

✅ **期待する結果**
1. 自分の Fabric ワークスペースに **`smart-ops-hub`** アイテムが作成される。
2. ブラウザ（InPrivate）で Fabric ポータルから `smart-ops-hub` を開く（または公開 URL にアクセスしてサインインボタンを押す）と、登録済みアカウントで Entra SSO 認証が通り、ヘッダーに認証済み状態が表示される 🎉

---

## 🔍 （参考）`rayfin dev` と `rayfin up` の違い

| コマンド | 動き | 使いどころ |
|---|---|---|
| `npm run preview` | バックエンド無しでローカル静的画面だけを起動 | UI レイアウト・デザインの高速確認 |
| `npx rayfin dev` | Fabric 上に **開発用 AppBackend** を作成／再利用し、`.env.local` を自動生成してローカル Vite（`localhost:5173`）からリモート DB・Auth に接続 | 日常のコーディング・ホットリロード開発（本番公開はされない） |
| `npx rayfin up` | ビルド済みフロントエンド・DB スキーマ・Functions・Storage・Connectors を Fabric アイテムへ **本番デプロイ** | チーム共有・ステージング／本番反映 |
| `npx rayfin up staticapp deploy` | フロントエンドの静的ビルドだけを再アップロード（約 30〜60 秒） | TS/React の画面修正だけを素早く反映したいとき |

> 💡 ポータル埋め込みのままローカル Vite を試したい場合は、`npm run dev` 起動中にポータルのアプリ URL 末尾へ `&devUri=http://localhost:5173` を付与するテクニック（`caldova-reorder` パターン）も使えます。

---

## ✅ チェックポイント

- [ ] `smart-ops-hub` をスキャフォールドし、`rayfin.yml`・Capability Router・`.mcp.json` の役割を確認した
- [ ] Fabric Entra SSO 認証（`onSessionChange` / `initEmbeddedAuth` / `ensureSignedInWithFabric`）を組み込んだ
- [ ] `npx rayfin up` で自分のワークスペースにデプロイし、ブラウザで SSO サインインを確認できた

---

## 🧹 トラブルシュート（プロンプトで対処）

| 症状 | プロンプト例 / 対処 |
|------|---------------------|
| テナントで Fabric Apps が無効と言われる | 管理ポータルで `Fabric Apps (preview)` が有効か、ワークスペースに Fabric 容量が付いているか確認 |
| サインイン時に別アカウントでループする | InPrivate ウィンドウで `app.fabric.microsoft.com` に登録済みアカウントでサインインし直す |
| リダイレクト URI エラーが出る | 「`rayfin/rayfin.yml` の `allowedRedirectUris` にデプロイ先のオリジンと `http://localhost:5173` を確認して再デプロイして」 |
| 別名アプリとして出したいのに既存アプリが上書きされる | `rayfin/.deployments.json` に前回デプロイ先 ID が記録されているため、新規アイテムにする場合は削除してから `rayfin up` する |

次は Rayfin の真骨頂である宣言的データモデル・行／列レベルセキュリティ・OneLake 自動ミラーリングを実装する [Lab 03 — 宣言的データモデル・`@role` 認可・OneLake 自動ミラー](03-data-modeling-rls-mirroring.md) へ進みます 🚀
