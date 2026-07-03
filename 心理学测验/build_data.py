#!/usr/bin/env python3
"""生成 tests.js 与 sample_tests.js"""

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent


def write_js(name: str, var: str, data):
    path = BASE / name
    path.write_text(
        f"window.{var} = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8",
    )
    print(f"已生成 {name}，共 {len(data) if isinstance(data, list) else len(data.keys())} 条")


def main():
    import enrich_tests

    enrich_tests.main()
    tests = json.loads((BASE / "data" / "tests.json").read_text(encoding="utf-8"))
    samples = json.loads((BASE / "data" / "sample_tests.json").read_text(encoding="utf-8"))
    write_js("tests.js", "TESTS", tests)
    write_js("sample_tests.js", "SAMPLE_TESTS", samples)


if __name__ == "__main__":
    main()
