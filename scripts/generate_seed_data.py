#!/usr/bin/env python3
"""Generate deterministic seed datasets and expected KPI metrics for the Fabric Apps by Rayfin hands-on lab."""

from __future__ import annotations

import csv
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    rng = random.Random(20261113)

    stores = [
        {"store_id": "ST-001", "store_name": "東京丸の内フラッグシップ", "region": "Kanto", "manager_upn": "manager.kanto@contoso.com", "tier": "Flagship"},
        {"store_id": "ST-002", "store_name": "新宿西口メディカルプラザ", "region": "Kanto", "manager_upn": "manager.kanto@contoso.com", "tier": "Standard"},
        {"store_id": "ST-003", "store_name": "横浜みなとみらいセンター", "region": "Kanto", "manager_upn": "manager.kanto@contoso.com", "tier": "Standard"},
        {"store_id": "ST-004", "store_name": "大宮ステーションストア", "region": "Kanto", "manager_upn": "manager.kanto@contoso.com", "tier": "Compact"},
        {"store_id": "ST-005", "store_name": "名古屋栄セントラル", "region": "Chubu", "manager_upn": "manager.chubu@contoso.com", "tier": "Flagship"},
        {"store_id": "ST-006", "store_name": "浜松アクトプラザ", "region": "Chubu", "manager_upn": "manager.chubu@contoso.com", "tier": "Compact"},
        {"store_id": "ST-007", "store_name": "静岡駿府メディカル", "region": "Chubu", "manager_upn": "manager.chubu@contoso.com", "tier": "Standard"},
        {"store_id": "ST-008", "store_name": "大阪梅田グランドハブ", "region": "Kansai", "manager_upn": "manager.kansai@contoso.com", "tier": "Flagship"},
        {"store_id": "ST-009", "store_name": "京都烏丸ヘルスケア", "region": "Kansai", "manager_upn": "manager.kansai@contoso.com", "tier": "Standard"},
        {"store_id": "ST-010", "store_name": "神戸三宮ベイストア", "region": "Kansai", "manager_upn": "manager.kansai@contoso.com", "tier": "Standard"},
        {"store_id": "ST-011", "store_name": "福岡天神センター", "region": "Kyushu", "manager_upn": "manager.kyushu@contoso.com", "tier": "Flagship"},
        {"store_id": "ST-012", "store_name": "博多駅前アネックス", "region": "Kyushu", "manager_upn": "manager.kyushu@contoso.com", "tier": "Compact"},
    ]

    products = [
        {"sku": "SKU-101", "product_name": "高機能サージカルマスク 50枚", "category": "Hygiene", "unit_cost": 480, "unit_price": 780, "lead_time_days": 3, "reorder_pack_qty": 40},
        {"sku": "SKU-102", "product_name": "手指消毒エタノール 500mL", "category": "Hygiene", "unit_cost": 520, "unit_price": 880, "lead_time_days": 4, "reorder_pack_qty": 30},
        {"sku": "SKU-103", "product_name": "ニトリル検査手袋 M 100枚", "category": "Hygiene", "unit_cost": 690, "unit_price": 1180, "lead_time_days": 5, "reorder_pack_qty": 30},
        {"sku": "SKU-104", "product_name": "非接触赤外線体温計 Pro", "category": "Devices", "unit_cost": 2400, "unit_price": 3980, "lead_time_days": 7, "reorder_pack_qty": 15},
        {"sku": "SKU-105", "product_name": "上腕式デジタル血圧計", "category": "Devices", "unit_cost": 4200, "unit_price": 6980, "lead_time_days": 7, "reorder_pack_qty": 10},
        {"sku": "SKU-106", "product_name": "パルスオキシメーター 軽量型", "category": "Devices", "unit_cost": 3100, "unit_price": 5280, "lead_time_days": 6, "reorder_pack_qty": 12},
        {"sku": "SKU-107", "product_name": "経口補水パウダー 10包入", "category": "Nutrition", "unit_cost": 610, "unit_price": 1050, "lead_time_days": 3, "reorder_pack_qty": 36},
        {"sku": "SKU-108", "product_name": "高タンパク栄養ゼリー 6個詰", "category": "Nutrition", "unit_cost": 760, "unit_price": 1280, "lead_time_days": 4, "reorder_pack_qty": 24},
        {"sku": "SKU-109", "product_name": "マルチビタミン＆亜鉛 60粒", "category": "Nutrition", "unit_cost": 840, "unit_price": 1480, "lead_time_days": 5, "reorder_pack_qty": 24},
        {"sku": "SKU-110", "product_name": "低刺激保湿ローション 250mL", "category": "Care", "unit_cost": 920, "unit_price": 1580, "lead_time_days": 4, "reorder_pack_qty": 20},
        {"sku": "SKU-111", "product_name": "防水ハイドロ救急バン 20枚", "category": "FirstAid", "unit_cost": 430, "unit_price": 740, "lead_time_days": 3, "reorder_pack_qty": 40},
        {"sku": "SKU-112", "product_name": "滅菌ガーゼパッド L 12枚", "category": "FirstAid", "unit_cost": 390, "unit_price": 680, "lead_time_days": 3, "reorder_pack_qty": 40},
        {"sku": "SKU-113", "product_name": "伸縮サポーター膝用 M", "category": "FirstAid", "unit_cost": 1150, "unit_price": 1980, "lead_time_days": 5, "reorder_pack_qty": 18},
        {"sku": "SKU-114", "product_name": "冷却ジェルシート 16枚入", "category": "Care", "unit_cost": 340, "unit_price": 598, "lead_time_days": 3, "reorder_pack_qty": 48},
        {"sku": "SKU-115", "product_name": "アイケア温熱マスク 12枚", "category": "Care", "unit_cost": 650, "unit_price": 1120, "lead_time_days": 4, "reorder_pack_qty": 30},
        {"sku": "SKU-116", "product_name": "花粉・PM2.5ブロックスプレー", "category": "Seasonal", "unit_cost": 580, "unit_price": 980, "lead_time_days": 4, "reorder_pack_qty": 30},
        {"sku": "SKU-117", "product_name": "高保湿のど飴 プロポリス配合", "category": "Seasonal", "unit_cost": 260, "unit_price": 450, "lead_time_days": 2, "reorder_pack_qty": 60},
        {"sku": "SKU-118", "product_name": "薬用ハンドケアクリーム 80g", "category": "Care", "unit_cost": 470, "unit_price": 820, "lead_time_days": 3, "reorder_pack_qty": 36},
        {"sku": "SKU-119", "product_name": "携帯用防災救急ポーチセット", "category": "FirstAid", "unit_cost": 1850, "unit_price": 3180, "lead_time_days": 6, "reorder_pack_qty": 15},
        {"sku": "SKU-120", "product_name": "超音波メッシュネブライザー", "category": "Devices", "unit_cost": 5400, "unit_price": 8900, "lead_time_days": 8, "reorder_pack_qty": 8},
    ]

    tier_multiplier = {"Flagship": 1.45, "Standard": 1.0, "Compact": 0.7}
    snapshot_date = "2026-11-01"
    inventory_rows = []
    row_id = 1

    for store in stores:
        mult = tier_multiplier[store["tier"]]
        for prod in products:
            avg_daily_sales = max(2, round(rng.uniform(4.0, 18.0) * mult))
            safety_stock = avg_daily_sales * prod["lead_time_days"]

            # Deterministically create realistic low-stock / critical-stock / healthy distribution
            roll = rng.random()
            if roll < 0.16:
                on_hand = max(1, round(avg_daily_sales * rng.uniform(0.5, 1.8)))
            elif roll < 0.32:
                on_hand = max(2, round(avg_daily_sales * rng.uniform(1.9, float(prod["lead_time_days"]) - 0.2)))
            else:
                on_hand = max(safety_stock + 4, round(avg_daily_sales * rng.uniform(float(prod["lead_time_days"]) + 1.5, 14.0)))

            days_of_supply = round(on_hand / avg_daily_sales, 2)
            is_low_stock = 1 if on_hand < safety_stock else 0
            suggested_reorder_qty = max(
                prod["reorder_pack_qty"],
                ((safety_stock * 2 - on_hand + prod["reorder_pack_qty"] - 1) // prod["reorder_pack_qty"]) * prod["reorder_pack_qty"],
            ) if is_low_stock else 0
            stockout_risk_jpy = (safety_stock - on_hand) * prod["unit_price"] if is_low_stock else 0

            inventory_rows.append(
                {
                    "snapshot_id": f"INV-{row_id:04d}",
                    "snapshot_date": snapshot_date,
                    "store_id": store["store_id"],
                    "sku": prod["sku"],
                    "on_hand_qty": on_hand,
                    "avg_daily_sales": avg_daily_sales,
                    "safety_stock_qty": safety_stock,
                    "days_of_supply": days_of_supply,
                    "is_low_stock": is_low_stock,
                    "suggested_reorder_qty": suggested_reorder_qty,
                    "stockout_risk_jpy": stockout_risk_jpy,
                }
            )
            row_id += 1

    def write_csv(path: Path, rows: list[dict]) -> None:
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

    write_csv(DATA_DIR / "stores.csv", stores)
    write_csv(DATA_DIR / "products.csv", products)
    write_csv(DATA_DIR / "inventory_daily.csv", inventory_rows)

    by_region: dict[str, dict[str, int | float]] = {}
    store_region = {s["store_id"]: s["region"] for s in stores}
    for r in inventory_rows:
        reg = store_region[r["store_id"]]
        agg = by_region.setdefault(reg, {"rows": 0, "total_on_hand_qty": 0, "low_stock_count": 0, "total_stockout_risk_jpy": 0})
        agg["rows"] += 1
        agg["total_on_hand_qty"] += r["on_hand_qty"]
        agg["low_stock_count"] += r["is_low_stock"]
        agg["total_stockout_risk_jpy"] += r["stockout_risk_jpy"]

    top_risk = sorted(
        [r for r in inventory_rows if r["is_low_stock"] == 1],
        key=lambda x: (-x["stockout_risk_jpy"], x["store_id"], x["sku"]),
    )[:5]

    metrics = {
        "seed": 20261113,
        "snapshot_date": snapshot_date,
        "counts": {
            "stores": len(stores),
            "products": len(products),
            "inventory_daily": len(inventory_rows),
        },
        "kpis": {
            "total_on_hand_qty": sum(r["on_hand_qty"] for r in inventory_rows),
            "low_stock_sku_pairs": sum(r["is_low_stock"] for r in inventory_rows),
            "total_stockout_risk_jpy": sum(r["stockout_risk_jpy"] for r in inventory_rows),
            "total_suggested_reorder_qty": sum(r["suggested_reorder_qty"] for r in inventory_rows),
            "avg_days_of_supply": round(sum(r["days_of_supply"] for r in inventory_rows) / len(inventory_rows), 2),
        },
        "by_region": by_region,
        "verification_anchors": {
            "first_row_inv_0001": inventory_rows[0],
            "top_5_low_stock_by_risk": top_risk,
        },
    }

    (DATA_DIR / "expected_metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(metrics["counts"], ensure_ascii=False))
    print(json.dumps(metrics["kpis"], ensure_ascii=False))


if __name__ == "__main__":
    main()
