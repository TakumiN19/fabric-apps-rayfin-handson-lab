# 用語集（Glossary）— Fabric Apps by Rayfin ＆ Microsoft Fabric

このハンズオン（Lab 00〜10）に登場する **Fabric Apps（Project Rayfin）・Spec-Driven 開発・Microsoft Fabric データ基盤** の用語を、**短い定義 ＋ 本ハンズオンでの使われ方 ＋ 参照先** でまとめた早見表です。

---

## 1. Fabric Apps / Rayfin のコア概念

### Fabric Apps（ファブリック アプリ）
Microsoft Fabric 上でデータ駆動の業務 Web アプリケーションを構築・ホスト・統制するためのネイティブ機能（Preview）。ワークスペース内に `AppBackend` アイテムとして作成され、OneLake や Entra ID のガバナンスをそのまま継承します。
- **本ハンズオン**: Lab 02〜09 を通じて `smart-ops-hub` を構築・デプロイします。

### Project Rayfin（レイフィン）
Fabric Apps の中核を支えるオープンソース・コードファーストの **TypeScript 製 Backend-as-a-Service (BaaS) SDK ＆ CLI**（`@microsoft/rayfin-*`）。データモデルや権限、コネクタ、関数、ストレージを宣言的に記述すると、DB スキーマ・GraphQL API・型付きクライアントを一括生成します。
- **本ハンズオン**: バージョン `1.36.2` を基準に全機能を使用します。

### Universal App ＆ Capability Router
`npm create @microsoft/rayfin@latest` の既定スターター構造。最初は最小の React + Vite 構成で起動し、`AGENTS.md` と `.agents/skills/capability-router/` がユーザーの要件に応じて必要な機能パック（`authentication`, `data-modeling`, `graphein-visuals`, `analytics` 等）だけを段階的に有効化します。
- **本ハンズオン**: Lab 02 でプロジェクトを作成し、段階的に機能を拡張します。

### `rayfin.yml`
プロジェクト内の `rayfin/rayfin.yml` に置かれる **バックエンド構成マニフェスト**。`auth`, `data`, `staticHosting`, `functions`, `storage` の各サービスと `connectors` を宣言します。
- **本ハンズオン**: Lab 02〜07 で各サービスを有効化します。

### Rayfin Skills（`rayfin@rayfin-skills`）＆ Rayfin MCP（`@microsoft/rayfin-mcp`）
AI コーディングエージェントが Rayfin の API を記憶で当て推量しないための公式スキルと MCP サーバー。各 npm パッケージ内の `assets/docs/` からインストール済みバージョンと完全一致する仕様を検索（`search_docs`, `discover_packages`, `get_doc`）します。
- **本ハンズオン**: Lab 00 でプラグイン導入し、Lab 02 で `.mcp.json` と `npx rayfin docs` を確認します。

---

## 2. データモデル・認可・ストレージ

### `@entity()` ＆ フィールドデコレータ
`@microsoft/rayfin-core` が提供する TypeScript クラス／プロパティ用デコレータ（`@uuid`, `@text({ max })`, `@int`, `@decimal`, `@boolean`, `@date`, `@email`, `@set`, `@one`, `@many`）。クラス定義から MSSQL テーブルと GraphQL API が自動生成されます。
- **本ハンズオン**: Lab 03 で `RestockOrder`, `StoreNote`, `ChecklistItem` を定義します（`@text` には必ず `max` を指定）。

### DAB（Data API Builder）
データベーステーブルから REST / GraphQL エンドポイントと認可ポリシーを自動構成するランタイム。Rayfin の `data` サービスおよび SQL コネクタの背後で動作します。
- **本ハンズオン**: Lab 03・04 で自動生成される型付きクエリ API の基盤として動作します。

### `@role()` / `@authenticated()`（行レベル・列レベル認可）
エンティティや Storage フォルダーに対するアクセス制御デコレータ。`policy: (claims, item) => claims.sub.eq(item.author_id)` で行所有者制限（RLS 相当）、`include` / `exclude` でフィールド公開制御を行えます。
- **本ハンズオン**: Lab 03 で `StoreNote` の更新・削除を作成者本人に限定します。

### Standard Schema（`toStandardSchema`）
Rayfin エンティティの制約（`min`, `max` 等）をフロントエンドのフォームバリデーションでもそのまま再利用できるスキーマ変換ヘルパー。
- **本ハンズオン**: Lab 03 の入力フォーム検証で使用します。

### `executePaginated()`
Rayfin Client でカーソルページネーション（`{ items, endCursor, hasNextPage }`）を使って全件・次ページを取得するメソッド。通常の `.execute()` は既定の 1 ページ（約 100 件）のみを返すため、100 件超を扱う際に必須です。
- **本ハンズオン**: Lab 03 で一覧取得ヘルパーとして実装します。

### Fabric SQL Database ＆ OneLake 自動ミラーリング（`MirroredWarehouse`）
Rayfin の `data` サービスが作成する書き込み可能なマネージド SQL データベースと、その更新内容を数秒で OneLake の Delta テーブル（SQL 分析エンドポイント）へ自動複製する仕組み。
- **本ハンズオン**: Lab 03 の 3-4 で、アプリからの書き込みが ETL なしで OneLake 側から参照できることを確認します。

### Rayfin Storage（`@blob()` / `StorageObject`）
OneLake をバックエンドとするマネージドファイルストレージ（Experimental）。フォルダー単位で最大サイズ（`mb(10)`）、許可 Content-Type、認証ルールを宣言し、`upload` / `list` / `download` / `delete` を行います。
- **本ハンズオン**: Lab 07 で店舗点検メモへの画像・PDF 添付に使用します。

---

## 3. コネクタ・サーバー関数・ポータル連携

### Fabric Data Connectors（`@microsoft/rayfin-connectors`）
ワークスペース内の既存 Fabric アイテムへ型安全に接続する仕組み。`fabric-semanticmodel`（DAX）、`fabric-warehouse`、`fabric-sqlanalytics`（Lakehouse）、`fabric-sqldatabase`（および実験的な `kusto`）をサポートします。
- **本ハンズオン**: Lab 04 で `sm_ops_inventory` と `ops_warehouse` に接続します。

### `delegated` 認証 vs `application` 認証
コネクタや関数の認証主体モード。`delegated` はサインイン中のアプリ利用者本人のトークンでアクセスし（セマンティックモデルの RLS が効く）、`application` はアプリアイテム所有者の ID でアクセスします。
- **本ハンズオン**: Lab 04 で `opsModel` に `delegated`、`opsWarehouse` に `application` を設定して違いを確認します。

### Apache Arrow ＆ `fabricSemanticModel()`
列指向の高速インメモリデータ形式。`fabric-semanticmodel` コネクタは DAX 応答を Arrow で返し、`fabricSemanticModel()` ランタイムが正規化された `{ status, table }` オブジェクトへ自動デコードします。
- **本ハンズオン**: Lab 04 のクライアント初期化で登録します。

### Rayfin Functions / User Data Functions（`@microsoft/fabric-user-data-functions`）
Fabric Apps 内でサーバーサイド実行される TypeScript 関数。`RayfinContext` を通じて `ctx.getDataClient()`、`ctx.Secrets`、各種 `AudienceType` トークン（`Fabric`, `AzureAI`, `Sql`, `Storage`, `ADO`）を安全に扱えます。
- **本ハンズオン**: Lab 06 で `submitRestockOrder`、`resetMyDemoOrders`、`askOpsAdvisor` を実装します。

### Portal Deep-Link App State（`@microsoft/rayfin-app-state-fabric`）
Fabric ポータル内に埋め込まれたアプリの状態（フィルタや選択タブ）をポータル URL と同期し、ディープリンク共有を可能にする SDK。
- **本ハンズオン**: Lab 09 で `isSupported()` 判定付きで実装します。

---

## 4. 開発手法・デザイン・データ基盤

### Spec-Driven Development（仕様駆動開発 / SDD）
FabCon で Sujata Narayana 氏らが紹介した AI 時代の開発手法。場当たり的なチャット（Vibe Coding）ではなく、Git 管理された Markdown 仕様書（`constitution.md` → `spec.md` → `plan.md` → `tasks.md`）を真実の源泉とし、仕様変更時は Markdown を更新して AI にアプリを収束（Converge）させます。
- **本ハンズオン**: `specs/` ディレクトリと Lab 08 で実践します。

### Z の法則（Z-Pattern Layout）
視線が「左上 → 右上 → 左下 → 右下」と動く特性に合わせ、左上に最重要結論 KPI、右上に根拠チャート、左下に優先対応キュー、右下にアクション実行パネルを置く業務画面設計原則。
- **本ハンズオン**: Lab 05 のコントロールタワー画面で適用します。

### Direct Lake セマンティックモデル
データのインポートコピーを行わず、OneLake 上の Delta テーブルをメモリへ直接読み込んで高速な DAX 分析を提供するモード。API 自動構築時に OAuth 資格情報設定で詰まりにくい利点もあります。
- **本ハンズオン**: Lab 01 で `sm_ops_inventory` を構築します。

### Fabric Apps Gallery ＆ `microsoft/awesome-rayfin`
Microsoft 公式およびコミュニティが公開している Fabric Apps（Rayfin）のショーケースギャラリーとテンプレート集。
- **本ハンズオン**: Lab 10 で全 20+ 事例を 7 類型に整理して解説します。
