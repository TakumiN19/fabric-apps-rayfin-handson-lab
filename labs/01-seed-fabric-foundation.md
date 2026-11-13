# Lab 01 — サインインとハンズオン用データ基盤（Lakehouse・Warehouse・セマンティックモデル）の準備

所要時間: 約 20 分
前提:
- [Lab 00](00-prerequisites.md) 完了（`.github/student.local.md` 登録済み）
- [Fabric ポータルへのサインイン](fabric-portal-login.md) 完了

このラボでは、**Azure CLI** と **Rayfin CLI** の双方で認証を済ませたあと、以降の Lab 04〜08 で Fabric Apps から接続する **信頼された分析データ基盤**（Lakehouse → Warehouse → セマンティックモデル）をプロンプト駆動で一括構築し、決定論的な期待値と照合します。

> 💡 **時間短縮オプション**:
> すでに接続対象のセマンティックモデル／Warehouse がある場合や、まず Rayfin アプリ本体の機能（認証・データモデル・Storage）だけをすぐ触りたい場合は、**1-1 と 1-2（サインインとワークスペース確認）だけ実施して [Lab 02](02-scaffold-and-auth.md) へ進むことも可能**です（Lab 04 の前に 1-3〜1-5 を実施すれば OK です）。

```text
data/*.csv (店舗12・商品20・在庫240行)
   │
   ▼ 1-3: 取り込み・構築
[ ops_lakehouse ] ──▶ [ ops_warehouse ] ──▶ [ sm_ops_inventory (DAX 5メジャー) ]
   │
   ▼ 1-4: 決定論的データ検証（件数・KPI・固定アンカー行を expected_metrics.json と完全照合）
```

---

## 1-1. Azure CLI と Rayfin CLI にサインインする

> 🗣️ **プロンプト**
> ```text
> 登録済みの自分のテナントに対して、Azure CLI と Rayfin CLI の両方でブラウザ認証サインインして、
> サインイン中のアカウントとテナントが参加者設定と一致しているか確認して。
> ```

🤖 **Copilot の動き**
- `.github/student.local.md` から登録済みのテナント ID とアカウントを読み取ります。
- `az login --tenant "$TENANT_ID" --allow-no-subscriptions`（Codespaces やリモート環境では `--use-device-code`）を実行します。
- 続けて `npx rayfin login -t "$TENANT_ID" --select` を実行し、ブラウザ認証を案内します。
- `az account show` で現在のアカウント・テナントを参加者設定と照合します。

✅ **期待する結果**
Azure CLI と Rayfin CLI の両方で `Signed in` となり、登録済みアカウント・テナント ID と一致していることが報告される。

---

## 1-2. 自分のワークスペースを特定して接続確認する

> 🗣️ **プロンプト**
> ```text
> Fabric に接続して、自分のワークスペースの Workspace ID と現在のアイテム一覧を確認して。
> ```

🤖 **Copilot の動き**
- Fabric REST API（`GET /v1/workspaces`）を呼び出し、登録済みのワークスペース名と完全一致するワークスペースを一意に特定します。
- 確認できた `Workspace ID` を `.github/student.local.md` に保存し、現在のアイテム一覧を表示します。

✅ **期待する結果**
自分のワークスペース名と `Workspace ID` が表示され、`.github/student.local.md` に記録される。

---

## 1-3. Lakehouse・Warehouse・セマンティックモデルを一括シード構築する

リポジトリ同梱の `data/`（`stores.csv` 12 行、`products.csv` 20 行、`inventory_daily.csv` 240 行）を Fabric ワークスペースに投入し、Lab 04 で Rayfin Connectors から接続する 3 アイテムを作成します。

> 🗣️ **プロンプト**
> ```text
> リポジトリの data/ にある stores.csv、products.csv、inventory_daily.csv を使って、
> 自分のワークスペースに次のハンズオン用データ基盤を構築して。
> 1. Lakehouse `ops_lakehouse` を作成し、Files/seed/ に3つのCSVをアップロードして Delta テーブル（stores, products, inventory_daily）として保存する
> 2. Warehouse `ops_warehouse` を作成し、dbo.dim_store（主キー store_id）、dbo.dim_product（主キー sku）、dbo.fact_inventory_daily（主キー snapshot_id）を作成して全行ロードする
> 3. `ops_warehouse` を参照する Direct Lake セマンティックモデル `sm_ops_inventory` を作成し、リレーションシップ（fact_inventory_daily.store_id -> dim_store.store_id、fact_inventory_daily.sku -> dim_product.sku）と次の5つの ASCII メジャーを定義する:
>    - `Total Stock Units` = SUM(fact_inventory_daily[on_hand_qty])
>    - `Low Stock SKU Count` = SUM(fact_inventory_daily[is_low_stock])
>    - `Stockout Risk Amount` = SUM(fact_inventory_daily[stockout_risk_jpy])
>    - `Suggested Reorder Units` = SUM(fact_inventory_daily[suggested_reorder_qty])
>    - `Avg Days of Supply` = AVERAGE(fact_inventory_daily[days_of_supply])
> ```

🤖 **Copilot の動き**
- `fabric-skills`（`spark-cli`, `sqldw-cli`, `semantic-model-authoring`）を使い、`ops_lakehouse` 作成 → OneLake DFS アップロード → Delta テーブル化を実行します。
- `ops_warehouse` を作成し、3 パート名（`ops_lakehouse.dbo.*`）または SQL 投入で `dim_store`（12 行）、`dim_product`（20 行）、`fact_inventory_daily`（240 行）を作成します。
- Direct Lake パーティション（OneLake 自動接続 — OAuth 手動設定エラーになりやすい Import `Sql.Database()` を回避）で `sm_ops_inventory` の TMDL を構成・デプロイします。
- 作成した 3 アイテムの Item ID を `.github/student.local.md` に控えます。

> ⚠️ **設計ポイント（Direct Lake と ASCII メジャー名）**:
> - API で `Import` モード（`Sql.Database()`）のモデルを作ると OAuth 資格情報未設定（`Premium_ASWL_Error`）で更新失敗しやすいため、OneLake 権限でそのまま動く **Direct Lake** 構成を採用します。
> - DAX の Execute Queries や Rayfin コネクタからの呼び出しで文字化け・エスケープ事故を防ぐため、**メジャー名は必ず ASCII 英語名**で定義します（画面上の日本語ラベルは React 側で付与します）。

✅ **期待する結果**
`ops_lakehouse`、`ops_warehouse`、`sm_ops_inventory` の 3 アイテムがワークスペースに作成される。

---

## 1-4. 決定論的データ検証（`data/expected_metrics.json` との完全照合）

加工・投入と検証は分けて実行します。投入されたデータと DAX メジャーが期待値と 1 円・1 件の狂いもなく一致するか確認します。

> 🗣️ **プロンプト**
> ```text
> ops_warehouse と sm_ops_inventory のデータを読み直して、data/expected_metrics.json の期待値と完全一致するか検証して。
> - 3テーブルの件数
> - 5つの DAX メジャー値
> - リージョン別（Kanto / Chubu / Kansai / Kyushu）の件数・要補充数・欠品リスク金額
> - snapshot_id = 'INV-0001' と欠品リスク金額1位（INV-0100）の固定レコード照合
> ```

🤖 **Copilot の動き**
- `ops_warehouse` への T-SQL クエリと、`sm_ops_inventory` への DAX `Execute Queries` の両方を実行し、`data/expected_metrics.json` と突合します。

✅ **期待する結果（すべて完全一致すること）**

| 検証項目 | 期待値 |
|---|---:|
| テーブル件数 (`dim_store` / `dim_product` / `fact_inventory_daily`) | **12 / 20 / 240 行** |
| `[Total Stock Units]` | **22,001** |
| `[Low Stock SKU Count]` | **72** |
| `[Stockout Risk Amount]` | **6,143,332** |
| `[Suggested Reorder Units]` | **6,578** |
| `[Avg Days of Supply]` | **7.92** |
| 地域別 要補充数（Kanto / Chubu / Kansai / Kyushu） | **21 / 20 / 17 / 14**（計 72） |
| 地域別 リスク金額（Chubu 最大） | **Chubu: ¥3,104,568** / Kansai: ¥1,366,620 / Kanto: ¥941,834 / Kyushu: ¥730,310 |
| 固定行 `INV-0001` (`ST-001 × SKU-101`) | `on_hand_qty = 72`, `safety_stock_qty = 27`, `is_low_stock = 0` |
| 欠品リスク 1 位 `INV-0100` (`ST-005 × SKU-120`) | `on_hand_qty = 30`, `safety_stock_qty = 192`, `suggested_reorder_qty = 360`, `stockout_risk_jpy = 1,441,800` |

---

## ✅ チェックポイント

- [ ] Azure CLI と Rayfin CLI の両方で登録済みテナントにサインインできた
- [ ] 自分のワークスペースの `Workspace ID` が `.github/student.local.md` に記録された
- [ ] `ops_lakehouse`、`ops_warehouse`、`sm_ops_inventory` が作成された
- [ ] `data/expected_metrics.json` の全件数・KPI・固定レコードと完全一致した

---

## 🧹 トラブルシュート（プロンプトで対処）

| 症状 | プロンプト例 / 対処 |
|------|---------------------|
| `No subscriptions found` で `az login` が止まる | `az login --tenant <テナントID> --allow-no-subscriptions --use-device-code` でサインイン |
| `Execute Queries` が 401 / 403 になる | テナント設定 `Dataset Execute Queries REST API` とモデルの `Read + Build` 権限を確認 |
| `sqlcmd` で `-G` エラーが出る | Go 版 `sqlcmd` では `-G` と `--authentication-method` を同時指定せず `--authentication-method=ActiveDirectoryDefault` のみ指定する |

次はよいよ本編、**Fabric Apps by Rayfin** のアプリ作成に入る [Lab 02 — Universal App スキャフォールドと Entra SSO 認証](02-scaffold-and-auth.md) です 🚀
