# Lab 04 — ネイティブ Fabric Data Connectors（Semantic Model・Warehouse・Lakehouse 連携）

所要時間: 約 25 分
前提:
- [Lab 01](01-seed-fabric-foundation.md) 完了（`ops_lakehouse`, `ops_warehouse`, `sm_ops_inventory` がワークスペースに存在）
- [Lab 03](03-data-modeling-rls-mirroring.md) 完了

以前のバージョンでは、セマンティックモデルの集計値をアプリに表示するために「事前に DAX で JSON を書き出してフロントに埋め込む」か「バッチスクリプトでアプリ DB にスナップショット投入する」必要がありました。

Rayfin 1.36.2 の **Fabric Data Connectors** を使うと、ワークスペース内の **Semantic Model・Warehouse・Lakehouse・SQL Database** に対して、宣言的設定と型安全なクライアントだけで **ライブ接続** できます！

```text
npx rayfin connector search / connector add
   │
   ├─ opsModel     (type: fabric-semanticmodel, auth: delegated)
   │    └─ client.connectors.opsModel.executeQuery({ query: 'EVALUATE ...' })  ◀── Apache Arrow 自動デコード + モデル RLS 継承
   │
   └─ opsWarehouse (type: fabric-warehouse, auth: application または delegated)
        └─ Source({ schema: 'dbo', table: 'dim_store', primaryKey: 'store_id' }) ◀── 型付き GraphQL クエリ
```

---

## 📊 サポートされる Fabric Data Connectors 一覧（Rayfin 1.36.2）

| 接続先 Fabric アイテム | コネクタ `type` | サポートされる操作 | 認証モード（`auth.type`） | 呼び出しスタイル |
|---|---|---|---|---|
| **Semantic Model** | `fabric-semanticmodel` | `executeQuery`（DAX） | **`delegated` 専用**（利用者委任） | `executeQuery({ query })`（Arrow 自動デコード） |
| **Warehouse** | `fabric-warehouse` | `read`, `create`, `update`, `delete` | `application`（既定）または `delegated` | `Source` 継承の型付きエンティティ GraphQL |
| **Lakehouse SQL 分析エンドポイント** | `fabric-sqlanalytics` | `read`（読み取り専用） | `application`（既定）または `delegated` | `Source` 継承の型付きエンティティ GraphQL |
| **Fabric SQL Database** | `fabric-sqldatabase` | `read`, `create`, `update`, `delete` | `application`（既定）または `delegated` | `Source` 継承の型付きエンティティ GraphQL |
| *Eventhouse / KQL（実験的）* | *`kusto` (experimental)* | *`executeQuery`, `executeCommand`* | *`delegated`* | *KQL 実行（実験的機能）* |

> 💡 **`application` と `delegated` の使い分け**:
> - **`delegated`（利用者委任）**: アプリを開いているサインインユーザー本人の権限でデータソースにアクセスします。セマンティックモデルの **RLS（行レベルセキュリティ）** がそのまま効くため、地域マネージャーごとに自分の担当地域だけを見せる設計がアプリ側コードゼロで成立します（利用者にモデルの `Read + Build` 権限が必要です）。
> - **`application`（アプリ ID＝アイテム所有者）**: アプリ所有者（Owner）の権限で共通マスタ等を参照します。全利用者に Warehouse 直接権限を配らず、アプリ経由の制御された読み取りだけを提供したい場合に有効です。

---

## 4-1. `rayfin connector search` でワークスペース内の接続先を検出する

> 🗣️ **プロンプト**
> ```text
> smart-ops-hub ディレクトリで `rayfin connector search` を使って、
> 自分のワークスペースにある Semantic Model（`sm_ops_inventory`）と Warehouse（`ops_warehouse`）と Lakehouse（`ops_lakehouse`）の Item ID を検索して確認して。
> ```

🤖 **Copilot の動き**
- 次のコマンドを実行して、各アイテムの ID を JSON で正確に取得します：
  - `npx rayfin connector search --workspace-id "$WS_ID" --type fabric-semanticmodel --json`
  - `npx rayfin connector search --workspace-id "$WS_ID" --type fabric-warehouse --json`
  - `npx rayfin connector search --workspace-id "$WS_ID" --type fabric-sqlanalytics --json`

✅ **期待する結果**
`sm_ops_inventory`、`ops_warehouse`、`ops_lakehouse` の 3 つの Item ID が検出される。

---

## 4-2. Semantic Model コネクタ（`opsModel`）と Warehouse コネクタ（`opsWarehouse`）を追加する

> 🗣️ **プロンプト**
> ```text
> smart-ops-hub に次の2つの Fabric コネクタを追加して、CLI が表示したバージョン一致のパッケージインストールコマンドも実行して。
> 1. Semantic Model `sm_ops_inventory` へのコネクタ `opsModel`（`--operations executeQuery`、`delegated` 認証）
> 2. Warehouse `ops_warehouse` への読み取り専用コネクタ `opsWarehouse`（`--operations read`）
> ```

🤖 **Copilot の動き**
- `npx rayfin connector add --type fabric-semanticmodel --workspace-id "$WS_ID" --item-id "$SM_ID" --name opsModel --operations executeQuery` を実行します。
- `npx rayfin connector add --type fabric-warehouse --workspace-id "$WS_ID" --item-id "$WH_ID" --name opsWarehouse --operations read` を実行します。
- CLI が出力したバージョン固定の `npm install @microsoft/rayfin-connectors@1.36.2 @microsoft/rayfin-connector-fabric-semanticmodel@1.36.2 @microsoft/rayfin-connector-fabric-graphql@1.36.2` 等をそのまま実行します。
- `rayfin/rayfin.yml` の `connectors:` セクションを確認します（`opsModel` が `auth.type: delegated` になっていることを確認）。

> ⚠️ **重要**: `npx rayfin connector add` が表示するバージョン一致の `npm install` コマンドは省略せず必ず実行してください。CLI とコネクタランタイムのマイナーバージョンがずれると型解決やランタイム通信で不整合が起きます。

✅ **期待する結果**
`rayfin/rayfin.yml` に `opsModel` と `opsWarehouse` が追記され、`rayfin/connectors/opsModel/` および `rayfin/connectors/opsWarehouse/`（スキーマ検出結果 `metadata.json` を含む）が生成される。

---

## 4-3. Warehouse コネクタの型付きエンティティと `ConnectorsRayfinClient` を構成する

1. `opsWarehouse` コネクタで `dbo.dim_store` と `dbo.dim_product` を型付きエンティティとして公開します。
2. `opsModel` コネクタで `sm_ops_inventory` に対してライブ DAX クエリ（KPI 取得・地域別集計・安全在庫割れキュー取得）を実行するクライアントを構成します。

> 🗣️ **プロンプト**
> ```text
> 追加した2つのコネクタをアプリから使えるように構成して。
> 1. `opsWarehouse` コネクタに `metadata.json` に基づいて `DimStore`（`dbo.dim_store`, primaryKey: `store_id`）と `DimProduct`（`dbo.dim_product`, primaryKey: `sku`）の型付き Source エンティティを定義する
> 2. `ConnectorsRayfinClient` と `fabricSemanticModel()` ランタイムを使って、`opsModel` と `opsWarehouse` の両方と既存の `data`（RestockOrder / StoreNote）を1つのクライアントシングルトンに統合する（コールドスタート対策として `timeout: 60_000` を設定）
> 3. `opsModel.executeQuery` で次の3つのライブ DAX クエリを実行するデータ取得サービスを実装する（必ず `result.status === 'success'` を検証すること）:
>    - 全社 KPI 5指標（Total Stock Units / Low Stock SKU Count / Stockout Risk Amount / Suggested Reorder Units / Avg Days of Supply）
>    - リージョン別集計（Region ごとの Low Stock SKU Count と Stockout Risk Amount）
>    - 安全在庫割れ（`is_low_stock = 1`）の店舗×SKU 一覧（`stockout_risk_jpy` 降順）
> 4. 未接続ローカル時（`localhost` プレビュー）は `data/expected_metrics.json` 等と整合する決定論的サンプルデータにフォールバックし、接続状態バッジ（`Live: Fabric` / `Sample: ※サンプル値`）を返すようにして
> ```

🤖 **Copilot の動き**
- `@microsoft/rayfin-connectors` の `Source` を使って `DimStore` / `DimProduct` を定義します：
  ```typescript
  import { Source } from '@microsoft/rayfin-connectors';
  import { text, int } from '@microsoft/rayfin-core';

  export class DimProduct extends Source({
    schema: 'dbo',
    table: 'dim_product',
    primaryKey: 'sku',
  }) {
    @text({ column: 'sku', max: 20 }) sku!: string;
    @text({ column: 'product_name', max: 200 }) product_name!: string;
    @text({ column: 'category', max: 50 }) category!: string;
    @int({ column: 'unit_price' }) unit_price!: number;
    @int({ column: 'lead_time_days' }) lead_time_days!: number;
    @int({ column: 'reorder_pack_qty' }) reorder_pack_qty!: number;
  }
  ```
- `@microsoft/rayfin-client`（または `./experimental`）の `ConnectorsRayfinClient` と `@microsoft/rayfin-connector-fabric-semanticmodel` の `fabricSemanticModel()` を組み合わせ、Apache Arrow 応答を自動デコードするクライアントを構成します。
- HTTP 200 でも DAX エラー時はペイロード内の `status` が失敗を示すため、`result.status === 'success'` を必ず検査します。

✅ **期待する結果**
コネクタ定義・クライアント統合・DAX サービスが型安全にビルド通過（`npm run build` 成功）する。

---

## 4-4. コネクタをデプロイし、ライブ DAX ＆ Warehouse 参照を検証する

> 🗣️ **プロンプト**
> ```text
> コネクタ設定を含めて smart-ops-hub を Fabric にデプロイして（`rayfin up`）。
> デプロイ完了後、Fabric ポータルから smart-ops-hub を開いたときにライブ取得される数値が `data/expected_metrics.json` と一致するか確認手順を案内して。
> ```

🤖 **Copilot の動き**
- `npx rayfin up --workspace-id "$WS_ID" --yes`（またはコネクタのみ更新時は `npx rayfin up connector apply` 併用）を実行してデプロイします。

**Fabric ポータルで動作確認しましょう:**
1. Fabric ポータル（`https://app.fabric.microsoft.com`）の自分のワークスペースから **`smart-ops-hub`** アイテムをクリックして開きます。
   - 💡 **`fabric-semanticmodel` コネクタはポータルのホスト埋め込みプロキシとも連携して `delegated` トークンを受け渡すため、Fabric ポータル内からアイテムを開くのが最も確実な正規経路です。**
2. 初回クエリ時（コネクタブリッジのコールドスタートで数秒〜十数秒かかる場合があります）の後、ヘッダーバッジが **`Live: Fabric`** になり、以下のライブ数値が表示されることを確認します：
   - 要補充 SKU 数: **`72`**
   - 欠品リスク金額: **`¥6,143,332`**
   - 総在庫数: **`22,001`**
   - 平均在庫日数: **`7.92 日`**
   - 要補充キュー先頭: **`ST-005`（名古屋栄セントラル）× `SKU-120`（超音波メッシュネブライザー） / リスク金額 `¥1,441,800`**

---

## 🔍 （参考）従来方式（スナップショット橋渡し）とネイティブ Connector の比較

| 方式 | 仕組み | 向いているケース |
|---|---|---|
| **① `fabric-semanticmodel` コネクタ（本 Lab 推奨）** | `executeQuery`（Arrow）でセマンティックモデルをリアルタイム照会。`delegated` 認証でモデル RLS が自動適用 | メジャー定義の一元管理・利用者ごとの RLS 適用・リアルタイム分析＋アクション統合（`Caldova Reorder` 型） |
| **② `fabric-warehouse` / `fabric-sqlanalytics` コネクタ** | Warehouse / Lakehouse テーブルを型付き GraphQL エンティティとして直接参照（Warehouse は CRUD 可） | マスタ参照・明細検索・Warehouse 直接更新アプリ |
| **③ アプリ SQL DB スナップショット橋渡し（`fabric-handson-lab-v3` Lab 10 型）** | バッチスクリプトで DAX 結果をアプリ専用 SQL DB に投入し `client.data.*` で読む | 利用者にセマンティックモデルの `Build` 権限を付与したくない場合や、超高速キャッシュ表示が必要な場合 |

---

## ✅ チェックポイント

- [ ] `npx rayfin connector search` で Semantic Model と Warehouse の Item ID を特定できた
- [ ] `opsModel`（`fabric-semanticmodel`）と `opsWarehouse`（`fabric-warehouse`）を追加し、バージョン一致パッケージを導入した
- [ ] `DimStore` / `DimProduct` の `Source` エンティティと `executeQuery` DAX 呼び出しを実装できた
- [ ] Fabric ポータル上で `Live: Fabric` バッジとともに `72 件 / ¥6,143,332 / 22,001 個` のライブ数値を確認できた

---

## 🧹 トラブルシュート（プロンプトで対処）

| 症状 | プロンプト例 / 対処 |
|------|---------------------|
| 初回ロードで 30 秒タイムアウトする | `ConnectorsRayfinClient` のオプションに `timeout: 60_000` を設定する（初回コールドスタート対策） |
| Semantic Model クエリが権限エラーになる | サインイン中のユーザーに `sm_ops_inventory` の `Read + Build` 権限があるか、テナント設定 `Dataset Execute Queries REST API` が有効か確認 |
| 主キーの無いテーブルで `Source` が失敗する | 主キーが無いテーブルでは `Source({ schema, table })` の `primaryKey` を省略する（キー指定の単一行操作のみ無効になる） |

次は取得したライブデータと書き込みフォームを、**Visuals Pack と Linear スタイル × Z の法則** で洗練された業務コントロールタワー画面に仕上げる [Lab 05 — Visuals Pack と業務 UX デザイン](05-visuals-and-ux-design.md) へ進みます 🚀
