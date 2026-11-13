# Product Specification (v1) — Smart Ops Hub

## 1. 背景と解決する課題（From Insight to Action）

全国 4 リージョン・12 店舗を展開するヘルスケア小売チェーンでは、既存のレポートで「どの店舗のどの商品が安全在庫を割り込んでいるか」は見えていたものの、実際の **補充発注の起票・現場メモの共有・検品写真の添付** はスプレッドシートとチャットに分散していた。

**Smart Ops Hub** は、Microsoft Fabric 上の信頼された在庫データ（`sm_ops_inventory` / `ops_warehouse`）と、現場のアクション（発注起票・メモ・証憑保管・OneLake 自動ミラーリング）を 1 つの画面に統合する業務アプリケーションである。

## 2. 対象ユーザー

- **リージョンマネージャー**: 担当地域の欠品リスク金額と安全在庫割れ SKU を把握し、優先度の高い店舗×商品ペアに対して補充発注を実行する。

## 3. 画面構成（Z の法則・1 画面完結オペレーション v1）

### 帯 1（上段左 → 上段右）：結論 KPI から地域・カテゴリ根拠へ
- **上段左（結論 KPI ストリップ・4 枚）**:
  1. **要補充 SKU 数**（`Low Stock SKU Count` — 基準値: `72 件`、警告バッジ付）
  2. **欠品リスク金額**（`Stockout Risk Amount` — 基準値: `¥6,143,332`）
  3. **総在庫数**（`Total Stock Units` — 基準値: `22,001 個`）
  4. **平均在庫日数**（`Avg Days of Supply` — 基準値: `7.92 日`）
- **上段右（根拠ビジュアル）**:
  - **リージョン別 欠品リスク金額＆要補充件数**（横棒グラフ、クリックで下段キューをクロスフィルタ）

### 帯 2（下段左 → 下段右）：優先対応キューから即時アクションへ
- **下段左（Low-Stock Action Queue）**:
  - 安全在庫割れ（`is_low_stock = 1`）の店舗×SKU 一覧を `stockout_risk_jpy` 降順に表示（初期先頭は `ST-005 × SKU-120`、リスク金額 `¥1,441,800`、在庫日数 `1.25 日`）。
  - リージョン絞り込み・キーワード検索・行選択をサポート。
- **下段右（Action & Note Drawer）**:
  - 選択した店舗×SKU に対し、推奨発注数（`suggested_reorder_qty`）を初期値とした **補充発注ボタン**（Functions `submitRestockOrder` 経由で `RestockOrder` に保存）と、**現場点検メモ＋証憑ファイル添付**（`StoreNote` + Rayfin Storage `attachments`）を実行できる。
  - 直近の発注履歴と現在のデータ接続モードバッジ（`Live: Fabric` / `Sample: ※サンプル値`）を表示する。

## 4. 受入基準（Acceptance Criteria）

1. Fabric ポータルまたは公開 URL で Entra SSO サインイン後、4 つの結論 KPI が `data/expected_metrics.json` の期待値と一致すること。
2. リージョン横棒グラフで `Chubu` をクリックすると、要補充キューが Chubu の `20 件`（欠品リスク合計 `¥3,104,568`）に絞り込まれること。
3. 補充発注を実行すると `RestockOrders` テーブルに保存され、OneLake の `MirroredWarehouse` からも同一レコードが参照できること。
4. 自分が作成した `StoreNote` のみ更新・削除でき、他ユーザーのメモは改ざんできないこと（`@role` ポリシー検証）。
