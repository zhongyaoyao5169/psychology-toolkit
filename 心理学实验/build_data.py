#!/usr/bin/env python3
"""从 data/experiments.json 生成 experiments.js"""

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
DATA = BASE / "data" / "experiments.json"
OUT = BASE / "experiments.js"


def main():
    experiments = json.loads(DATA.read_text(encoding="utf-8"))
    OUT.write_text(
        "window.EXPERIMENTS = " + json.dumps(experiments, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8",
    )
    print(f"已生成 {OUT.name}，共 {len(experiments)} 条实验")


def build_all():
    """扩充详情 → 裁剪教材插图 → 占位 SVG → 生成 JS"""
    import enrich_data
    import prepare_book_assets

    enrich_data.main()
    try:
        import extract_from_pdf
        extract_from_pdf.main()
    except SystemExit as e:
        print(f"跳过 PDF 提取：{e}")
    except Exception as e:
        print(f"PDF 提取失败：{e}")
    prepare_book_assets.main()
    main()


if __name__ == "__main__":
    main()
