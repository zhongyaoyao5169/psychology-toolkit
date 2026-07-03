#!/usr/bin/env python3
"""为 tests.json 补充版本信息与样题试测关联。"""

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
DATA = BASE / "data" / "tests.json"

VERSIONS = {
    "wechsler": [
        {"name": "WAIS-IV", "note": "成人版（16—90 岁），四指数 + 全量表 IQ，当前临床常用。"},
        {"name": "WISC-V", "note": "儿童版（6—16 岁），指数结构与成人版对应，分测验更适配儿童。"},
        {"name": "WPPSI-IV", "note": "学前版（2.5—7.5 岁），题项与施测方式适合低幼，指数名称略有差异。"},
        {"name": "早期修订（W-B / WAIS-R / WAIS-III 等）", "note": "指数/分测验组成与常模随修订变化，不可混用记分规则。"},
    ],
    "binet": [
        {"name": "比奈-西蒙（1905 起）", "note": "首创心理年龄概念，按通过项目确定 MA。"},
        {"name": "斯坦福-比奈（SB 系列）", "note": "Terman 美国修订，引入 IQ=MA/CA×100，后改为离差智商。"},
        {"name": "SB5（第五版）", "note": "覆盖 2 岁至成人，提供合成分数与五因素认知指数。"},
    ],
    "kaufman-kabc": [
        {"name": "K-ABC（1983）", "note": "序列/同时加工理论首版，含心理加工与成就量表。"},
        {"name": "K-ABC-II（2004）", "note": "扩展理论模型与分测验，非言语量表更突出。"},
    ],
    "raven": [
        {"name": "SPM（标准推理测验）", "note": "60 题，适用于 6 岁以上及成人，最常用。"},
        {"name": "CPM（彩色推理测验）", "note": "A/B/C 三 sets，适用于幼儿及智力落后者筛查。"},
        {"name": "APM（高级推理测验）", "note": "48 题，适用于高能力大学生及专业人员。"},
        {"name": "CRT（联合型，中国常模）", "note": "SPM 彩色 + 部分 APM 组合，本土化常模。"},
    ],
    "mmpi": [
        {"name": "MMPI（1943）", "note": "原版 504/566 题，奠定效度 + 临床量表结构。"},
        {"name": "MMPI-2（1989）", "note": "修订题项与常模，增加内容量表与补充量表。"},
        {"name": "MMPI-2-RF（2008）", "note": "更短、更同质化的 RC 量表结构，自适应版常见。"},
    ],
    "cpi": [
        {"name": "CPI（早期版）", "note": "面向正常人群，20 余个人格量表。"},
        {"name": "CPI-434 / CPI 434", "note": "434 题修订，更新常模与部分量表定义。"},
    ],
    "epq": [
        {"name": "EPQ（成人版）", "note": "P/E/N/L 四量表，是/否作答。"},
        {"name": "EPQ-R（修订版）", "note": "题项与常模更新，仍保留四量表框架。"},
        {"name": "EPQ-C（儿童版）", "note": "适用于 7—15 岁，指导语与题量适配儿童。"},
    ],
    "16pf": [
        {"name": "16PF A / B", "note": "完整版，题量最多，信度较高。"},
        {"name": "16PF C / D", "note": "缩减版，施测时间更短。"},
        {"name": "16PF E", "note": "适用于文化程度较低者，用语更简易。"},
        {"name": "16PF-5（计算机版）", "note": "现代记分与报告系统，常模更新。"},
    ],
    "neo": [
        {"name": "NEO-PI-R", "note": "240 题完整版，五因素 + 30 facet。"},
        {"name": "NEO-FFI", "note": "60 题简式，仅五因素总分。"},
        {"name": "NEO-PI-3", "note": "最新修订，题项与常模更新。"},
    ],
    "projective-intro": [
        {"name": "经典投射范式", "note": "联想 / 构造 / 完成 / 选择 / 表达五类，无单一「版本」，依具体测验而定。"},
    ],
    "rorschach": [
        {"name": "Rorschach 综合系统（CS）", "note": "Exner 系统，变量丰富，培训体系成熟。"},
        {"name": "R-PAS", "note": "Rorschach 性能评估系统，强调常模与简化编码。"},
    ],
    "tat": [
        {"name": "TAT（Murray 原版）", "note": "31 张图卡，成人常用 20 张子集。"},
        {"name": "CAT（儿童版）", "note": "图片与情境适合儿童，施测程序类似。"},
    ],
}

SAMPLE_TEST = {
    "raven": "raven",
    "epq": "epq",
}


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    for item in data:
        eid = item["id"]
        if eid in VERSIONS:
            item["versions"] = VERSIONS[eid]
        if eid in SAMPLE_TEST:
            item["sampleTestId"] = SAMPLE_TEST[eid]
        else:
            item.pop("sampleTestId", None)
    DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已补充版本与样题关联，共 {len(data)} 条")


if __name__ == "__main__":
    main()
