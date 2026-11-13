# Data Fit Assessment Gate（データ配置・粒度適合性確認票）

| 観点 | 確認項目 | 本アプリの設計判断 |
|---|---|---|
| 読み取り元（Analytical Read） | 既存のセマンティックモデル／Warehouse を使うか、スナップショットを取り込むか | KPI と在庫状況は `sm_ops_inventory`（`fabric-semanticmodel` コネクタ）および `ops_warehouse` から直接参照し、メジャー定義の二重管理を防ぐ |
| 書き込み先（Operational Write-back） | 業務トランザクションをどこに保存するか | アプリ専用の Fabric SQL Database（`RestockOrder`, `StoreNote`）に保存し、OneLake 自動ミラー経由で分析基盤へ還流させる（Lakehouse SQL Endpoint への直接 DML は不可） |
| バイナリ・証憑（Unstructured Files） | 画像・PDF を SQL 列に入れないか | SQL の `NVARCHAR` にはファイルパス（`attachment_path`）のみ保持し、実体は OneLake ベースの Rayfin Storage（`attachments`）に格納する |
| クエリ件数・ページング | 100 件超のテーブルで `.execute()` 切り捨てが起きないか | `inventory_daily` は 240 行あるため、全件走査や一覧表示では `executePaginated()` またはサーバー／DAX 側集計を使う |
| データ粒度の正直さ | 存在しない交差軸でフィルタできるかのように見せていないか | 店舗（`store_id`）× 商品（`sku`）× 日付（`snapshot_date`）粒度に忠実にクロスフィルタを構成する |
