# Technical Implementation Plan — Smart Ops Hub

## 1. Rayfin サービス構成（`rayfin/rayfin.yml`）

| サービス / 機能 | 有効化 | 設定・パッケージ | 役割 |
|---|---|---|---|
| `services.auth` | `true` | `@microsoft/rayfin-auth`, `@microsoft/rayfin-auth-provider-fabric` | Entra ID / Fabric SSO 認証（`ensureSignedInWithFabric` / `initEmbeddedAuth`） |
| `services.data` | `true` | `dialect: mssql`, `@microsoft/rayfin-core`, `@microsoft/rayfin-data` | アプリ専用 Fabric SQL Database + DAB GraphQL + OneLake 自動ミラー |
| `connectors.opsModel` | `true` | `type: fabric-semanticmodel`, `auth.type: delegated` | `sm_ops_inventory` へのライブ DAX クエリ（Arrow デコード） |
| `connectors.opsWarehouse` | `true` | `type: fabric-warehouse`, `auth.type: application`（または `delegated`） | `ops_warehouse` の `dim_store` / `dim_product` 型付き参照 |
| `services.functions` | `true` | `auth.type: application`, `@microsoft/fabric-user-data-functions` | `submitRestockOrder`（発注検証・ID 刻印書き込み）、`askOpsAdvisor`（Data Agent / AI 連携） |
| `services.storage` | `true` | `@microsoft/rayfin-storage` (experimental) | `attachments` フォルダー（現場写真・納品書 PDF 保管、最大 10 MiB） |
| `services.staticHosting` | `true` | `folder: dist`, `assetAccess: protected` | OneLake 静的配信・Fabric ポータル埋め込み |
| Portal App State | 任意 | `@microsoft/rayfin-app-state-fabric` | 選択中リージョン／店舗のポータル URL ディープリンク同期 |

## 2. データモデル設計（`packages/data` または `rayfin/data`）

1. **`RestockOrder`**:
   - `id`: `@uuid()`
   - `store_id`: `@text({ max: 20 })`
   - `sku`: `@text({ max: 20 })`
   - `qty`: `@int({ min: 1, max: 10000 })`
   - `status`: `@set('submitted', 'approved', 'shipped', 'cancelled')`
   - `requested_by_upn`: `@text({ max: 200 })`
   - `requested_by_id`: `@text({ max: 100 })`
   - `note`: `@text({ max: 500, optional: true })`
   - `requested_at`: `@date()`
   - 権限: `@role('authenticated', 'read')`（作成・取消は Functions `submitRestockOrder` 経由で統制、または Lab 03 段階では `@authenticated('*')` から段階的に強化）
2. **`StoreNote`**:
   - `id`: `@uuid()`
   - `store_id`: `@text({ max: 20 })`
   - `sku`: `@text({ max: 20, optional: true })`
   - `severity`: `@set('info', 'warning', 'critical')`
   - `body`: `@text({ max: 1000 })`
   - `attachment_path`: `@text({ max: 300, optional: true })`
   - `resolved`: `@boolean()`
   - `author_id`: `@text({ max: 100 })`
   - `created_at`: `@date()`
   - 権限: 全認証ユーザーが閲覧可（`@role('authenticated', ['read', 'create'])`）、更新・削除は作成者本人のみ（`@role('authenticated', ['update', 'delete'], { policy: (claims, item) => claims.sub.eq(item.author_id) })`）

## 3. フロントエンド＆状態管理設計

- React 19 + TypeScript (ES2022) + Tailwind CSS v4 + Graphein / Recharts
- データレイヤーを `src/services/` に分離し、`VITE_RAYFIN_API_URL` 未設定時（`npm run preview`）は `data/` 同等の決定論的シードデータにフォールバックしつつ `Sample: ※サンプル値` バッジを表示する。
