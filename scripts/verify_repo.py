#!/usr/bin/env python3
"""Validate repository structure, deterministic seed data, shell scripts, and relative Markdown links."""

from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
FENCE_RE = re.compile(r"^```")


def strip_code_fences(text: str) -> str:
    lines = []
    in_fence = False
    for line in text.splitlines():
        if FENCE_RE.match(line.strip()):
            in_fence = not in_fence
            continue
        if not in_fence:
            lines.append(line)
    return "\n".join(lines)


def check_seed_data(errors: list[str]) -> None:
    metrics_path = ROOT / "data" / "expected_metrics.json"
    if not metrics_path.exists():
        errors.append("Missing data/expected_metrics.json")
        return

    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    for name in ("stores", "products", "inventory_daily"):
        csv_path = ROOT / "data" / f"{name}.csv"
        if not csv_path.exists():
            errors.append(f"Missing data/{name}.csv")
            continue
        with csv_path.open(encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        expected_count = metrics["counts"][name]
        if len(rows) != expected_count:
            errors.append(f"data/{name}.csv row count {len(rows)} != expected {expected_count}")

        if name == "inventory_daily":
            total_qty = sum(int(r["on_hand_qty"]) for r in rows)
            low_cnt = sum(int(r["is_low_stock"]) for r in rows)
            risk_jpy = sum(int(r["stockout_risk_jpy"]) for r in rows)
            if total_qty != metrics["kpis"]["total_on_hand_qty"]:
                errors.append(f"total_on_hand_qty mismatch: {total_qty}")
            if low_cnt != metrics["kpis"]["low_stock_sku_pairs"]:
                errors.append(f"low_stock_sku_pairs mismatch: {low_cnt}")
            if risk_jpy != metrics["kpis"]["total_stockout_risk_jpy"]:
                errors.append(f"total_stockout_risk_jpy mismatch: {risk_jpy}")


def check_markdown_links(errors: list[str]) -> int:
    md_files = sorted(ROOT.rglob("*.md"))
    checked = 0
    for md in md_files:
        content = strip_code_fences(md.read_text(encoding="utf-8"))
        for raw_target in LINK_RE.findall(content):
            target = raw_target.strip().split()[0]
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            rel_path = target.split("#", 1)[0]
            if not rel_path:
                continue
            resolved = (md.parent / rel_path).resolve()
            checked += 1
            if not resolved.exists():
                errors.append(f"{md.relative_to(ROOT)} -> broken link '{target}'")
    return checked


def check_shell_scripts(errors: list[str]) -> None:
    for sh in sorted(ROOT.rglob("*.sh")):
        proc = subprocess.run(["bash", "-n", str(sh)], capture_output=True, text=True)
        if proc.returncode != 0:
            errors.append(f"Shell syntax error in {sh.relative_to(ROOT)}: {proc.stderr.strip()}")


def main() -> int:
    errors: list[str] = []
    check_seed_data(errors)
    checked_links = check_markdown_links(errors)
    check_shell_scripts(errors)

    if errors:
        print("VALIDATION FAILED:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print(f"[OK] Seed data verified, shell scripts valid, and {checked_links} relative Markdown links checked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
