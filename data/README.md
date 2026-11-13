# ハンズオン用シードデータ（`Smart Ops Hub` — 医療・ヘルスケア小売 店舗在庫＆補充オペレーション）

このディレクトリには、[microsoft/awesome-rayfin](https://github.com/microsoft/awesome-rayfin) の `caldova-reorder`（LTG291 セッション事例）および `field-technician` の業務パターンを参考に、固定乱数シード（`20261113`）で決定論的に生成した **合成データ（実在の顧客・患者データは一切含みません）** を格納しています。

## ファイル一覧

| ファイル | 行数（ヘッダー除く） | 主キー | 用途 |
|---|---:|---|---|
| `stores.csv` | 12 | `store_id` (`ST-001`〜`ST-012`) | 4 リージョン（Kanto / Chubu / Kansai / Kyushu）の店舗マスタ |
| `products.csv` | 20 | `sku` (`SKU-101`〜`SKU-120`) | 6 カテゴリの取扱商品・単価・リードタイム・発注単位 |
| `inventory_daily.csv` | 240 | `snapshot_id` (`INV-0001`〜`INV-0240`) | 2026-11-01 時点の店舗×SKU 日次在庫スナップショット（12 × 20 = 240 行） |
| `expected_metrics.json` | — | — | 各 Lab の検証プロンプトで照合する期待値（KPI・地域別内訳・固定アンカー行） |

> 💡 **なぜ 240 行なのか？**
> Rayfin のデータクライアント `execute()` は 1 ページあたり約 100 件で切り捨てる仕様があるため、100 件超のレコード数（240 行）を用意することで、Lab 03・04 でカーソルページング（`executePaginated()`）とサーバー側集計（`groupBy().aggregate()` / DAX）の重要性を実践的に検証できます。

## 決定論的 KPI 期待値（`expected_metrics.json`）

| 指標 | メジャー名（ASCII） | 期待値 |
|---|---|---:|
| 総在庫数 | `Total Stock Units` | **22,001** |
| 安全在庫割れ（要補充）店舗×SKU 数 | `Low Stock SKU Count` | **72** |
| 欠品リスク金額合計（円） | `Stockout Risk Amount` | **¥6,143,332** |
| 推奨発注数合計 | `Suggested Reorder Units` | **6,578** |
| 平均在庫日数 | `Avg Days of Supply` | **7.92 日** |

再生成コマンド:

```bash
python3 scripts/generate_seed_data.py
```
