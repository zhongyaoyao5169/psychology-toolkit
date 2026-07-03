#!/usr/bin/env python3
"""为尚未裁剪的教材插图生成 SVG 占位图。"""

from pathlib import Path

from book_figures import BOOK_FIGURES

BASE = Path(__file__).resolve().parent
BOOK = BASE / "assets" / "book"
BOOK.mkdir(parents=True, exist_ok=True)


def placeholder_svg(title: str, hint: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 360" width="640" height="360">
  <rect fill="#FAF7F0" width="640" height="360"/>
  <rect fill="#FFFFFF" x="24" y="24" width="592" height="312" rx="12" stroke="#E5DFD3" stroke-width="2"/>
  <text x="320" y="150" text-anchor="middle" fill="#2B2622" font-size="18" font-family="PingFang SC, Microsoft YaHei, sans-serif">{title}</text>
  <text x="320" y="185" text-anchor="middle" fill="#9A9388" font-size="13" font-family="PingFang SC, Microsoft YaHei, sans-serif">教材插图占位</text>
  <text x="320" y="215" text-anchor="middle" fill="#9A9388" font-size="12" font-family="PingFang SC, Microsoft YaHei, sans-serif">{hint}</text>
</svg>'''


def main():
    count = 0
    for fig in BOOK_FIGURES:
        path = BOOK / f"{fig['file']}.svg"
        hint = f"assets/book/{fig['file']}.png"
        path.write_text(placeholder_svg(fig["title"], hint), encoding="utf-8")
        count += 1
    readme = BOOK / "README.md"
    readme.write_text(
        """# 教材插图目录

仅存放教材中的**图表、示意图、表格**裁剪图，不用整页截图。

## 命名规则

在 `book_figures.py` 中配置，输出为 `{file}.png`。

## 更新

```bash
python3 extract_from_pdf.py   # 从 PDF 裁剪插图
python3 build_data.py           # 同步 experiments.js
```
""",
        encoding="utf-8",
    )
    print(f"已生成 {count} 个插图占位 SVG + README")


if __name__ == "__main__":
    main()
