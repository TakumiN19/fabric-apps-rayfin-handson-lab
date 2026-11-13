# Microsoft Fabric Apps by Rayfin × GitHub Copilot CLI ハンズオン

GitHub Copilot CLI と **`rayfin-skills`**・**`skills-for-fabric`** を使い、
**Microsoft Fabric Apps（powered by Project Rayfin）** の主要機能をエンドツーエンドで体験するプロンプト駆動＆仕様駆動（Spec-Driven）ハンズオンです。

各ラボは [TakumiN19/fabric-handson-lab-v3](https://github.com/TakumiN19/fabric-handson-lab-v3) と同じフォーマットの独立した Markdown 手順書になっており、
**Fabric Apps Gallery / `microsoft/awesome-rayfin`** の実践パターンと、FabCon セッション（**Sujata Narayana 氏**）で紹介された **Spec-Driven 開発（仕様駆動開発）** を統合しています。

> 🤖 **プロンプト駆動 × Spec-Driven ハンズオン**
> コマンドやボイラープレートを手で書くのではなく、「やりたいこと」や「Markdown 仕様書（`specs/spec.md`）」を Copilot CLI に渡すだけ。
> 各ステップは 🗣️ **プロンプト** → 🤖 **Copilot の動き** → ✅ **期待する結果** の 3 点セットで記載しています。
> （仕組みを深く理解したい人向けに、裏側の Rayfin CLI コマンド・TypeScript 定義・`rayfin.yml` も併記しています）

---

## 🎯 このハンズオンで学ぶこと（Rayfin 1.36.2 全機能網羅）

単なる「ダッシュボード表示」にとどまらず、**分析から業務アクションまで（From Insight to Action）** を Microsoft Fabric のガバナンス下で完結させる **Fabric Apps by Rayfin** の全機能を体系的に学びます。

1. **Universal App ＆ Capability Router ＆ Entra SSO 認証**（Lab 02）
   - `npm create @microsoft/rayfin@latest`、`rayfin.yml`、`.mcp.json`（バージョン固定ドキュメント MCP）、`ensureSignedInWithFabric` / `initEmbeddedAuth`
2. **宣言的データモデル・`@role` 行／列レベル認可・OneLake 自動ミラーリング**（Lab 03）
   - `@entity()`、`@text({ max })`、`@boolean()`、`@one` / `@many`、`toStandardSchema` バリデーション、`claims.sub.eq(...)` ポリシー、Fabric SQL Database → `MirroredWarehouse` の Zero-ETL ミラー
3. **ネイティブ Fabric Data Connectors**（Lab 04）
   - `fabric-semanticmodel`（Apache Arrow によるライブ DAX ＆ モデル RLS 継承）、`fabric-warehouse` / `fabric-sqlanalytics` / `fabric-sqldatabase`（型付き GraphQL エンティティ、`application` vs `delegated` 認証）
4. **Visuals / Analytics Pack ＆ 洗練された業務 UX（Linear スタイル × Z の法則）**（Lab 05）
   - `graphein-visuals` / `analytics` パック、単一アクセント配色、Z の法則による結論先行レイアウト、データ粒度に誠実なクロスフィルタ、`Live` / `Sample` 明示バッジ
5. **サーバーサイド Functions（UDF）による監査付き書き込み＆ Data Agent / AI 連携**（Lab 06）
   - `UserDataFunctions`（`udf.func`）、`RayfinContext`、`AudienceType` トークン、`npx rayfin secret set`、サーバー側 ID 刻印による改ざん防止発注フロー、会話型 AI ドロワー統合
6. **OneLake ベースのマネージド Storage（ファイル・証憑管理）**（Lab 07）
   - `@blob()` / `StorageObject` による型付きフォルダー定義、サイズ・MIME 制限、OneLake 上への現場写真・納品書 PDF アップロード
7. **【補足＆実践】Spec-Driven 開発（FabCon — Sujata Narayana 氏セッション）**（Lab 08）
   - なぜ Vibe Coding は本番の残り 20% で止まるのか、`specs/constitution.md` → `spec.md` → `plan.md` → `tasks.md` による仕様駆動開発、仕様更新による 3 ペルソナ切替・ホバーカード・補充スケジュールタブへの反復収束（Converge）
8. **ポータル埋め込み・ディープリンク（App State）・マルチ環境昇格・CI/CD・ガバナンス**（Lab 09）
   - `@microsoft/rayfin-app-state-fabric`、Dev → Prod 昇格（`rayfin up switch`）、サービスプリンシパルによる GitHub Actions 自動デプロイ、CU 課金と権設計
9. **Fabric Apps Gallery ＆ `awesome-rayfin` 全 20 テンプレート解剖カタログ**（Lab 10）
   - `Caldova Reorder`、`Field Technician`、`Fabric User Manager`、`Power BI Fixer`、`Schedule Inventory` 等のアーキテクチャ比較と顧客提案時の選定マトリクス

---

## 🏗️ 全体アーキテクチャ（構築するアプリ: `Smart Ops Hub`）

全国 4 リージョン・12 店舗 × 20 商品（240 在庫スナップショット）を対象に、在庫欠品リスクの検知から補充発注・現場メモ・検品証憑添付・OneLake 還流までを 1 つの Fabric App で完結させます。

```text
[ Lakehouse: ops_lakehouse ] ──▶ [ Warehouse: ops_warehouse ] ──▶ [ Semantic Model: sm_ops_inventory ]
                                            │                                      │
                        fabric-warehouse    │                                      │ fabric-semanticmodel
                        Connector (GraphQL) │                                      │ Connector (Delegated DAX)
                                            ▼                                      ▼
                    ┌──────────────────────────────────────────────────────────────────────┐
                    │               Fabric App: smart-ops-hub (Rayfin 1.36.2)              │
                    │  React 19 + Vite + Tailwind v4 + Graphein/Recharts + Entra SSO       │
                    │  ・Zの法則 KPI ＆ リージョン横断クロスフィルタ                        │
                    │  ・要補充アクションキュー ＆ ペルソナ別ビュー（Spec v2）             │
                    │  ・Ask Ops Advisor（AI / Data Agent チャットドロワー）               │
                    └───────────┬──────────────────────────┬───────────────────────┬───────┘
          client.data (@role)   │   client.functions       │    client.storage     │
                                ▼                          ▼                       ▼
                   [ App SQL Database (MSSQL) ] ◀── [ Rayfin Functions ]   [ Rayfin Storage ]
                     RestockOrders / StoreNotes       submitRestockOrder     OneLake Typed
                                │                     Audience Tokens        Folders (PDF/PNG)
                                │ 自動ミラー (Zero-ETL)
                                ▼
                   [ OneLake: MirroredWarehouse ] ──▶ レポート・Data Agent へ即時還流
```

---

## 🚀 GitHub Codespaces で開始（推奨）

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/TakumiN19/fabric-apps-rayfin-handson-lab?quickstart=1)

上のボタンから Codespace を作成すると、Dev Container のセットアップ完了後に次の検証済みツール・プラグインをすぐ利用できます。

| 自動導入されるもの | 固定バージョン |
|--------------------|----------------|
| Python | 3.12.11 |
| Node.js／npm／npx | 22.22.0／10.9.4 |
| Azure CLI | 2.89.1 |
| GitHub Copilot CLI | 1.0.111 |
| **Rayfin CLI (`@microsoft/rayfin-cli`)** | **1.36.2** |
| Azure Functions Core Tools (`func`) | 4.16.0 |
| Power BI レポート作成 CLI | 0.5.0 |
| go-sqlcmd | 1.10.0 |
| `fabric-skills`／`powerbi-authoring` | 0.3.21 |
| **`rayfin@rayfin-skills`（公式 Rayfin スキル）** | **0.4.2** |

Codespace のターミナルが開いたら、GitHub Copilot と Azure へサインインします（Azure サインインは [Lab 01](labs/01-seed-fabric-foundation.md) で実施しても構いません）。

```bash
copilot login --device-code
az login --allow-no-subscriptions --use-device-code

# 自動セットアップ結果を確認
bash .devcontainer/scripts/verify.sh
```

> [!IMPORTANT]
> Dev Container が自動化するのは **受講環境内のローカルツール** です。
> Fabric 容量、テナント管理設定（*Fabric Apps (preview)* 等）、ワークスペース権限は自動作成されないため、必ず下記の「講師・テナント管理者向け事前確認」を完了してください。

> [!NOTE]
> Docker デーモンは主経路（Fabric プロバイダーによる `rayfin dev` / `rayfin up`）では不要なため同梱していません。
> ローカル Vite プレビュー用ポート `5173` と Rayfin Functions ローカルデバッグ用ポート `7071` が自動フォワードされます。

---

## 🧰 受講者 PC の必須環境（ローカル実行時）

| 要件 | 対象 | 推奨／対応バージョン | 確認コマンド |
|------|------|----------------------|--------------|
| Visual Studio Code | 全 Lab | 最新安定版 | `code --version` |
| Edge または Chrome | 全 Lab | 最新安定版（InPrivate 推奨） | — |
| ターミナル | 全 Lab | Windows: PowerShell 7+／WSL、macOS・Linux: bash／zsh | `pwsh --version` または `$SHELL --version` |
| GitHub Copilot CLI | 全 Lab | 最新安定版（検証時: 1.0.111） | `copilot --version` |
| Azure CLI (`az`) | Lab 01 以降 | 最新安定版 | `az version` |
| Node.js／npm／npx | 全 Lab | **22.x または 24.x LTS**（奇数系 21/23/25 は非推奨） | `node --version` / `npm --version` |
| Rayfin CLI | Lab 02 以降 | **1.36.2** | `rayfin --version` または `npx @microsoft/rayfin-cli@1.36.2 --version` |
| Azure Functions Core Tools | Lab 06（ローカルデバッグ時） | v4.x（検証時: 4.16.0） | `func --version` |
| Python | Lab 01・検証スクリプト | **3.10 以上 3.14 未満**（3.12／3.13 推奨） | `python3 --version` または `py --version` |
| `sqlcmd`（Go 版） | Lab 01・03 | go-sqlcmd（検証時: 1.10.0） | `sqlcmd --version` |
| `rayfin@rayfin-skills` | Lab 02 以降 | `microsoft/rayfin`（v0.4.2） | Copilot CLI 内で `/plugin list` |
| `fabric-skills`／`powerbi-authoring` | Lab 01 以降 | `microsoft/skills-for-fabric`（v0.3.21） | Copilot CLI 内で `/plugin list` |

### Copilot プラグインと CLI の手動導入（ローカル PC の場合）

```bash
npm install -g @microsoft/rayfin-cli@1.36.2 azure-functions-core-tools@4 @microsoft/powerbi-report-authoring-cli@0.5.0
```

続いて GitHub Copilot CLI 内で次を実行します：

```text
/plugin marketplace add microsoft/skills-for-fabric
/plugin install fabric-skills@fabric-collection
/plugin install powerbi-authoring@fabric-collection

/plugin marketplace add microsoft/rayfin
/plugin install rayfin@rayfin-skills
```

---

## 🧑‍🏫 講師・テナント管理者向け事前確認（preflight）

- [ ] 稼働中の **Fabric 容量**（推奨: 有料 F2 以上／集合研修では F32 等）に各受講者のワークスペースが割り当てられている
- [ ] 各受講者が自分のワークスペースに `Contributor`／`Member`／`Admin` のいずれかのロールを持つ（なお Lab 06 の Functions デプロイは **App アイテム所有者（Owner）** であることが必須）
- [ ] 管理ポータル > テナント設定で **`Fabric Apps (preview)`**（組織アプリ／データアプリの作成）が有効化されている
- [ ] 管理ポータル > テナント設定で **`Dataset Execute Queries REST API`** が有効化され、Lab 04 以降の受講者にセマンティックモデルの **Read ＋ Build** 権限がある
- [ ] Lab 07（Rayfin Storage）を実施する場合、管理ポータル > OneLake 設定で **`Users can access data stored in OneLake with apps external to Fabric`** が有効化されており、Power BI Pro ワークスペースではなく Fabric 容量ワークスペースを使用している
- [ ] Lab 06 で Fabric Data Agent 連携まで試す場合、**有料 F2+ / P1+ 容量**（Trial 容量不可）上で Copilot / Data Agent テナント設定を 1 時間以上前に有効化している

---

## 🧩 Lab 別の追加要件と機能ゲート（Feature Gate）

本教材では、テナント設定やプレビュー制約で利用できない機能をモックで「成功」と偽装せず、[specs/fit-gates/capability-assessment.md](specs/fit-gates/capability-assessment.md) に基づいて明確に切り分けます。

| 対象 | 使用する Rayfin 機能 | 事前確認・機能ゲート |
|------|----------------------|----------------------|
| Lab 00〜01 | CLI・プラグイン・データ基盤シード | Lab 01 をスキップして Lab 02 から始めることも可能（アプリ単体・オフラインフォールバック対応） |
| Lab 02 | `auth` (Fabric SSO), `staticHosting` | `Fabric Apps (preview)` テナント設定が有効であること |
| Lab 03 | `data` (`dialect: mssql`), `@role`, OneLake ミラー | 対象リージョンで Fabric SQL Database が利用可能であること |
| Lab 04 | `connectors` (`fabric-semanticmodel`, `fabric-warehouse`, `fabric-sqlanalytics`) | Semantic Model の `Read + Build` 権限と `Execute Queries` 設定が有効であること |
| Lab 05 | `graphein-visuals` / `analytics` パック・UX 設計 | 追加テナント設定なし（Lab 02〜04 のアプリ上で動作） |
| Lab 06 | `functions` (`UserDataFunctions`), `Secrets`, AI 連携 | デプロイ実行者が App アイテムの Owner であること。Data Agent 未構成時は決定論的インサイトモードとして明示動作 |
| Lab 07 | `storage` (`@blob`, OneLake Storage — Experimental) | OneLake 外部アプリ設定が有効かつ Fabric 容量 WS であること |
| Lab 08 | Spec-Driven 開発（`specs/spec-v2-iteration.md`） | 追加テナント設定なし（仕様更新からの反復実装＆再デプロイ） |
| Lab 09 | `@microsoft/rayfin-app-state-fabric`, `rayfin up switch`, CI/CD | ポータル App State はテナント順次展開のため `isSupported()` で判定 |
| Lab 10 | Fabric Apps Gallery / `awesome-rayfin` カタログ | 参照・任意スキャフォールド演習 |

---

## ⚠️ 現在の既知制約・Rayfin 1.36.2 実装上の重要ポイント

以下は Microsoft Learn・`microsoft/rayfin` リポジトリ・実案件知見で確認済みの仕様と注意点です。

| 項目 | 仕様・制約（Rayfin 1.36.2 時点） | 本ハンズオンでの扱い |
|------|----------------------------------|----------------------|
| `@text()` の `max` 指定 | `@text()` に `max` を指定しないと MSSQL で `NVARCHAR(MAX)` となり、デプロイ成功後に GraphQL API が 500 エラーになる | すべての文字列列に `@text({ max: N })` を必須化 |
| 真偽値デコレータ名 | 一部ドキュメントに `@bool()` の記載があるが SDK 実体のエクスポートは **`@boolean()`** | `@boolean()` を使用 |
| `.execute()` の件数上限 | `client.data.<Entity>.select(...).execute()` は既定で約 100 件までの 1 ページのみ返す。`count()` や `totalCount` は未提供 | 100 件超（本教材の 240 行など）では `executePaginated()` またはサーバー集計を使用 |
| 権限デコレータ省略 | `@entity()` に権限デコレータを付けないと意図しない全 CRUD 許可や警告の原因になる | 全エンティティ・全 Storage フォルダーに `@role(...)` を明示 |
| Semantic Model コネクタの認証 | `fabric-semanticmodel` は **`delegated`（利用者委任）専用**。サービスプリンシパルや `application` モードは非対応 | `auth.type: delegated` を明示し、ポータル経由または利用者 SSO で実行 |
| Functions の制約 | パッケージ上限 30 MB、実行上限 240 秒、**再デプロイ間隔は最低 2 分**、発行できるのはアイテム Owner のみ | Lab 06 でローカル検証後にまとめて `rayfin up` する手順を採用 |
| Storage の制約 | Experimental 機能。Docker ローカルエミュレータは非対応（`rayfin dev` でもリモート OneLake を使用） | Lab 07 で機能ゲート確認後に実施 |
| 複製時のデプロイ先上書き | プロジェクトをコピーすると `rayfin/.deployments.json` が残り、元のアプリを上書きする | 別アプリとして出す際は `rayfin/.deployments.json` を削除 |

---

## 🌐 ネットワーク要件

企業ネットワークやプロキシ配下で実施する場合は、次の通信を許可してください。

| 通信 | 主な接続先 | 用途 |
|------|------------|------|
| HTTPS 443 | `github.com`, `api.github.com`, `raw.githubusercontent.com` | Copilot 認証、教材・`skills-for-fabric`・`microsoft/rayfin` 取得 |
| HTTPS 443 | `registry.npmjs.org`, `pypi.org`, `files.pythonhosted.org` | Rayfin パッケージ・フロントエンド依存関係取得 |
| HTTPS 443 | `login.microsoftonline.com`, `microsoft.com/devicelogin` | Microsoft Entra ID / Fabric SSO 認証 |
| HTTPS 443 | `app.fabric.microsoft.com`, `api.fabric.microsoft.com`, `api.powerbi.com` | Fabric ポータル／REST API／Semantic Model クエリ |
| HTTPS 443 | `onelake.dfs.fabric.microsoft.com` | OneLake データ・Storage アクセス |
| HTTPS 443 | `*.rayfin.windows.net`, `*.webapp.fabricapps.net` | Fabric Apps ホスティング・バックエンド API・Functions |
| TCP 1433 | `*.datawarehouse.fabric.microsoft.com`, `*.database.fabric.microsoft.com` | Lab 01・03 の `sqlcmd` による Warehouse / SQL DB / ミラー確認 |

---

## 🔐 参加者設定（Lab 00 で一度だけ登録）

本教材は **集合ハンズオン（`student` 番号配布）** と **個人自習（自分のテナント・ワークスペース指定）** の両方に対応しています。
Lab 00 の登録プロンプトを一度実行すると `.github/student.local.md`（Git 管理外）に保存され、以降の全 Lab でアカウント・ワークスペース・各種 Item ID を Copilot が自動補完します。

---

## 📚 ラボ一覧

| # | ラボ | 学べる Rayfin / Fabric Apps 機能 | 所要時間 |
|---|------|----------------------------------|----------|
| — | [Fabric ポータルへのサインイン（受講者向け）](labs/fabric-portal-login.md) | InPrivate でのアカウント切替・ワークスペース確認・個人トライアル確認 | 5 分 |
| 00 | [前提条件のセットアップとスキル導入](labs/00-prerequisites.md) | Rayfin CLI 1.36.2・`rayfin@rayfin-skills`・`skills-for-fabric` 導入、参加者設定登録 | 10 分 |
| 01 | [サインインとデータ基盤（LH・WH・SM）のシード投入](labs/01-seed-fabric-foundation.md) | Azure & Rayfin サインイン、`ops_lakehouse` / `ops_warehouse` / `sm_ops_inventory`（240 行）の一括構築と決定論的検証 | 20 分 |
| 02 | [Universal App スキャフォールドと Entra SSO 認証](labs/02-scaffold-and-auth.md) | `Universal App`・Capability Router・`rayfin.yml`・ドキュメント MCP・Fabric SSO 認証・初回 `rayfin up` | 20 分 |
| 03 | [宣言的データモデル・`@role` 認可・OneLake 自動ミラー](labs/03-data-modeling-rls-mirroring.md) | `@entity`・リレーション・`toStandardSchema`・行／列レベルセキュリティ・`executePaginated`・`MirroredWarehouse` 確認 | 25 分 |
| 04 | [ネイティブ Fabric Data Connectors 連携](labs/04-fabric-data-connectors.md) | `fabric-semanticmodel`（ライブ DAX / Arrow）＋ `fabric-warehouse` / `fabric-sqlanalytics` 型付き連携 | 25 分 |
| 05 | [Visuals Pack と業務 UX デザイン（Linear × Z の法則）](labs/05-visuals-and-ux-design.md) | `graphein-visuals` / `analytics` パック、単一アクセント配色、Z の法則配置、クロスフィルタ、`Live`/`Sample` バッジ | 25 分 |
| 06 | [サーバーサイド Functions（UDF）と Data Agent / AI 連携](labs/06-functions-and-agentic-actions.md) | `UserDataFunctions`・`AudienceType`・`Secrets`・サーバー監査付き補充発注・会話型 AI ドロワー | 30 分 |
| 07 | [OneLake マネージド Storage（証憑・画像アップロード）](labs/07-onelake-managed-storage.md) | `@blob()` 型付きフォルダー・MIME／サイズ制限・現場検品写真／PDF のアップロード・一覧・取得 | 20 分 |
| 08 | [【補足＆実践】Spec-Driven 開発（FabCon Sujata 氏セッション）](labs/08-spec-driven-development.md) | Vibe Coding の限界と仕様駆動開発、`specs/` 4 文書体系、仕様更新による 3 ペルソナ・ホバーカード・日程タブへの収束 | 25 分 |
| 09 | [ポータル埋め込み・ディープリンク・マルチ環境 CI/CD・ガバナンス](labs/09-portal-deeplink-cicd-governance.md) | `@microsoft/rayfin-app-state-fabric`、`rayfin up switch`、GitHub Actions 自動デプロイ、CU 課金・運用統制 | 20 分 |
| 10 | [Fabric Apps Gallery ＆ `awesome-rayfin` 全テンプレートカタログ](labs/10-gallery-and-architecture-catalog.md) | 公式・コミュニティ全 20+ 事例の設計パターン比較、テンプレートからの起動レシピ、提案選定ガイド | 15 分 |
| 📖 | [用語集（Glossary）](labs/glossary.md) | Fabric Apps・Rayfin SDK・DAB・UDF・OneLake ミラー・Spec Kit 等の早見表 | — |
