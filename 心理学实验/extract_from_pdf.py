#!/usr/bin/env python3
"""从教材 PDF 裁剪插图/表格（非整页截图）。"""

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
DEPS = BASE / ".pydeps"
if DEPS.exists():
    sys.path.insert(0, str(DEPS))

import fitz  # noqa: E402

from book_figures import BOOK_FIGURES, figures_for_experiment, printed_page  # noqa: E402

PDF = Path("/Users/zhongyaoyao/Downloads/实验心理学-郭秀艳-人民教育出版社-2004.pdf")
OUT = BASE / "assets" / "book"
DATA = BASE / "data" / "experiments.json"
MATRIX = fitz.Matrix(2.5, 2.5)


def render_figure(doc, fig: dict, dest: Path) -> bool:
    pdf_page = fig["pdfPage"]
    idx = pdf_page - 1
    if idx < 0 or idx >= doc.page_count:
        return False
    page = doc[idx]
    r = page.rect
    x0, y0, x1, y1 = fig["rect"]
    clip = fitz.Rect(r.width * x0, r.height * y0, r.width * x1, r.height * y1)
    pix = page.get_pixmap(matrix=MATRIX, clip=clip)
    dest.parent.mkdir(parents=True, exist_ok=True)
    pix.save(str(dest))
    return True


def sync_json():
    if not DATA.exists():
        return
    data = json.loads(DATA.read_text(encoding="utf-8"))
    for item in data:
        eid = item["id"]
        figs = figures_for_experiment(eid)
        if figs:
            item["figures"] = figs
        else:
            item.pop("figures", None)
        for step in item.get("steps") or []:
            step.pop("image", None)
            step.pop("fallback", None)
            step.pop("bookPage", None)
            step.pop("pdfPage", None)
        item.pop("bookPages", None)
        item.pop("pdfPages", None)
    DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    if not PDF.exists():
        raise SystemExit(f"未找到 PDF：{PDF}")

    doc = fitz.open(PDF)
    count = 0
    for fig in BOOK_FIGURES:
        dest = OUT / f"{fig['file']}.png"
        if render_figure(doc, fig, dest):
            count += 1
            print(f"  {dest.name} <- p.{fig['pdfPage']} ({fig['title']})")

    doc.close()
    sync_json()
    print(f"共裁剪 {count} 张教材插图 -> {OUT}")


if __name__ == "__main__":
    main()
