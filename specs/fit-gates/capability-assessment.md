# Capability Assessment Gate（テナント・リージョン機能確認票）

実装コミット前に、対象テナント・容量・ワークスペースで各 Rayfin 機能が利用可能かをプローブして記録します（利用不可の機能をモックで「成功」と偽装しないためのゲートです）。

| 機能 | 必須テナント設定 / 前提 | 確認コマンド / 方法 | 判定 (`PASS` / `BLOCKED`) | 備考 |
|---|---|---|---|---|
| Fabric Apps 基本 (`AppBackend` + Static Hosting + Entra SSO) | 管理ポータル: `Fabric Apps (preview)` 有効、有料または対応 Fabric 容量、WS `Contributor` 以上 | `npx rayfin up --dry-run` / 初回 `npx rayfin up` | `[ ]` | |
| Data サービス (`mssql` + OneLake 自動ミラー) | Fabric SQL Database が対象容量リージョンで利用可能 | `npx rayfin up db apply` → ポータルで SQL DB & MirroredWarehouse 確認 | `[ ]` | |
| Semantic Model Connector (`fabric-semanticmodel`) | `Dataset Execute Queries REST API` 有効、利用者にモデルの `Read + Build` 権限 | `npx rayfin connector search --type fabric-semanticmodel` | `[ ]` | `delegated` 専用 |
| Warehouse / Lakehouse SQL Connector | 対象アイテムへのアクセス権（`application` はアプリ所有者、`delegated` は各利用者） | `npx rayfin connector search --type fabric-warehouse` | `[ ]` | |
| Rayfin Functions (`UserDataFunctions`) | Functions プレビュー対応リージョン、発行者がアイテム所有者（Owner） | `npx rayfin functions init` → `npx rayfin up functions deploy` | `[ ]` | 再発行間隔 2 分制限に注意 |
| Rayfin Storage (OneLake Experimental) | `Users can access data stored in OneLake with apps external to Fabric` 有効、Pro WS 不可 | `npx rayfin up storage apply` | `[ ]` | Docker ローカルエミュレータなし |
| Fabric Data Agent 連携 | 有料 F2+ / P1+ 容量（Trial 不可）、Copilot / Data Agent テナント設定有効、Agent 公開済み | Data Agent エンドポイント疎通確認 | `[ ]` | 未有効時は決定論的集計モードと明示 |
