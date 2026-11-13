# Fabric Apps by Rayfin ハンズオン共通指示（参加者設定・Rayfin 1.36.2 ガードレール）

## 1. 参加者設定（一度だけ登録し、全 Lab で自動補完する）

ユーザーが次のいずれかの形式で参加者設定の登録・記憶を依頼したら、教材ルートの `.github/student.local.md` に Markdown で保存する。

1. **配布アカウント（student 番号）モード**（集合ハンズオン既定）:
   - student 番号は数字だけであることを確認し、先頭の 0 を含めて入力された表記を保持する。
   - ワークスペース名: `student` の直後にその番号を連結した文字列（例: `student3`）
   - アカウント: ワークスペース名の直後に `@M365x43914722.onmicrosoft.com` を連結した文字列（配布ドメインが別途指定された場合はそのドメインを使用）
   - テナント ID: `e6c1292e-65b7-4e2d-9e1b-13f24e7753fd`（別途指定された場合はそのテナント ID）
2. **自習・自社テナントモード**:
   - ユーザーが自分のメールアドレス（UPN）、テナント ID、ワークスペース名を伝えた場合は、その 3 点をそのまま保存する。

共通ルール:
- 既存の登録と同一アカウント・同一ワークスペース名なら確認済みの Workspace ID や Item ID メモを保持し、番号またはワークスペース名を変更した場合は以前の ID を削除する。
- 保存後に `.github/student.local.md` を読み直し、保存済みの設定を表示して確認できるようにする。
- 登録の依頼だけでは Azure / Fabric / Rayfin へのサインインやアイテム作成は実行しない。
- パスワード、MFA コード、アクセストークン、シークレットは `.github/student.local.md` に絶対に保存しない。`.github/student.local.md` はコミット・共有しない。

Lab 01 以降は、Azure / Fabric / Rayfin の操作を行う前に必ず `.github/student.local.md` を読み込む。
- ユーザーにアカウント名、ワークスペース名、Workspace ID、Lakehouse / Warehouse / Semantic Model / SQL Database / AppBackend の Item ID、SQL サーバー名、公開 URL を手入力・置換させない。
- 初回接続時に登録済みのワークスペース名と完全一致するワークスペースを Fabric REST API で一意に特定し、Workspace ID を `.github/student.local.md` に追記する。複数候補や不一致がある場合は推測せず操作を止めて理由を伝える。
- パスワード入力、MFA、ブラウザでのアカウント選択・同意（`az login`、`npx rayfin login`、ポータル初回アクセス）はユーザー本人に行ってもらう。

## 2. 本物の Fabric Apps（Rayfin）実装ガードレール（必須遵守）

- **ローカル Python / Streamlit / FastAPI 等を「Fabric Apps」と呼ばない**:
  - `skills-for-fabric` 内の `FabricAppDev` エージェントは Python + ODBC 構成を既定で提案することがあるが、本ハンズオンで構築するのは **Rayfin SDK（TypeScript）によるネイティブ Fabric Apps（`AppBackend` アイテム）** である。
  - 必ず `rayfin@rayfin-skills` プラグイン、スキャフォールド後のプロジェクト内 `.agents/skills/`（`capability-router` / `rayfin` 等）、および `node_modules/@microsoft/rayfin-*/assets/docs` のインストール済みドキュメントを参照して実装すること。Rayfin API を記憶だけで推測しない。
- **Rayfin 1.36.2 の厳守事項（アンチパターン防止）**:
  - エンティティの文字列列 `@text()` には **必ず `max` を指定する**（例: `@text({ max: 200 })`）。省略すると MSSQL で `NVARCHAR(MAX)` となり GraphQL 実行時に Internal Server Error になる。
  - 真偽値デコレータは **`@boolean()`** を使う（`@bool()` は存在しない）。省略可能フィールドは `@optional()` ではなくオプション `{ optional: true }` を使う。
  - TC39 Stage 3 デコレータを使用するため、`tsconfig.json` で `experimentalDecorators` や `emitDecoratorMetadata` を有効化しない。相対 import には `.js` 拡張子を付ける。
  - **すべての `@entity()` と Storage フォルダーに必ず `@role(...)` または `@authenticated(...)` を明示する**。権限デコレータの省略はアンチパターンである。
  - 認証状態購読は `client.auth.onSessionChange(...)` を使う（`onAuthStateChange` ではない）。
  - データ読み取りは `client.data.<Entity>.select([...]).execute()` を使う。1 ページの既定上限（約 100 件）を超える可能性がある一覧・集計では `executePaginated()` を使い、無言の切り捨てを起こさない。`count()` や `totalCount` は存在しない前提で設計する。
  - コネクタは `npx rayfin connector add` が表示するバージョン一致の `npm install` コマンドを実行する。`fabric-semanticmodel` コネクタは `delegated` 認証専用であり、`application` を設定しない。
  - Functions を有効化する場合は `rayfin/rayfin.yml` の `services.functions.auth.type: application` を明示する。
  - 既存プロジェクトを複製して別名の Fabric App として新規デプロイする場合は、`rayfin/.deployments.json` を削除してから `npx rayfin up` を実行する（残っていると既存アイテムを上書きする）。

## 3. UI デザイン・Spec-Driven 開発・検証の原則

- **UI デザイン原則（Linear スタイル × Z の法則）**:
  - アクセントカラーはアプリ全体で 1 色に絞り、信号色（緑・黄・赤）はステータスや閾値超過のバッジにのみ使う。グラデーション・過度なドロップシャドウ・発光エフェクトは使わない。
  - ダッシュボード配置は **Z の法則** に従い、各帯の左端に「結論」（達成状況・欠品リスク件数・要対応数）を置き、右へ根拠・内訳・時系列、下段にアクションキューと書き込み（Write-back）ドロワーを配置する。
  - ライブ接続時とオフライン／サンプルフォールバック時を UI バッジ（`Live: Fabric` / `Sample: ※サンプル値`）で正直に区別し、接続失敗をサンプル値で隠蔽しない。
- **機能ゲートと既知制約の正直な報告**:
  - テナント設定未有効、容量未割当、リージョン未対応、権限不足（Semantic Model の Build 権限欠如、OneLake 外部アクセス設定オフ、Data Agent 未公開など）でブロックされた場合は、別手段で成功したように装わず、原因と必要な設定を明示して **BLOCKED** として報告する。
- **決定論的なデータ検証**:
  - Lab 01 のシードデータや各 Lab の確認では、`data/expected_metrics.json` および教材記載の件数・合計値・固定キー条件（`WHERE` + `ORDER BY`）と照合し、期待値・実測値・差異を報告する。順序なしの `TOP` / `LIMIT` 先頭行だけで合格としない。
