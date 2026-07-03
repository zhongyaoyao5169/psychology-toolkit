#!/usr/bin/env python3
"""为经典实验生成示意 SVG 图（setup / flow）。"""

from pathlib import Path

ASSETS = Path(__file__).resolve().parent / "assets"

STYLE = """
<style>
  .bg { fill: #FAF7F0; }
  .frame { fill: #FFFFFF; stroke: #E5DFD3; stroke-width: 2; }
  .ink { fill: #2B2622; font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; }
  .muted { fill: #9A9388; font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; }
  .accent { fill: #7C7AE0; }
  .accent2 { fill: #3AA984; }
  .accent3 { fill: #E2566B; }
  .line { stroke: #2B2622; stroke-width: 2; fill: none; }
  .dash { stroke: #9A9388; stroke-width: 1.5; fill: none; stroke-dasharray: 6 4; }
</style>
"""

DIAGRAMS = {
    "wundt-reaction-time": {
        "setup": ("反应时实验装置示意", [
            ("rect", "40,30,520,260", "frame"),
            ("text", "280,58", "莱比锡心理学实验室 · 隔音反应室", "ink", 15, "middle"),
            ("rect", "80,90,160,120", "frame"),
            ("text", "160,115", "刺激呈现器", "muted", 12, "middle"),
            ("text", "160,140", "光 / 声", "ink", 13, "middle"),
            ("rect", "360,90,160,120", "frame"),
            ("text", "440,115", "反应键", "muted", 12, "middle"),
            ("text", "440,145", "按键记录", "ink", 13, "middle"),
            ("circle", "280,150,28", "accent"),
            ("text", "280,155", "被试", "ink", 12, "middle"),
            ("line", "240,150,200,150", "line"),
            ("line", "320,150,360,150", "line"),
            ("text", "280,230", "计时器记录：刺激 onset → 反应 onset（毫秒）", "muted", 12, "middle"),
        ]),
        "flow": ("反应时任务流程", [
            ("rect", "30,40,540,240", "frame"),
            ("rect", "50,80,130,70", "frame"),
            ("text", "115,110", "简单反应时", "ink", 12, "middle"),
            ("text", "115,135", "一种刺激→一种反应", "muted", 11, "middle"),
            ("rect", "215,80,130,70", "frame"),
            ("text", "280,110", "选择反应时", "ink", 12, "middle"),
            ("text", "280,135", "多刺激→择一反应", "muted", 11, "middle"),
            ("rect", "380,80,130,70", "frame"),
            ("text", "445,110", "辨别反应时", "ink", 12, "middle"),
            ("text", "445,135", "辨别后反应", "muted", 11, "middle"),
            ("text", "300,210", "任务越复杂 → 反应时越长", "accent3", 14, "middle"),
        ]),
    },
    "ebbinghaus-forgetting": {
        "setup": ("无意义音节学习材料", [
            ("rect", "40,35,520,250", "frame"),
            ("text", "300,65", "艾宾浩斯记忆实验", "ink", 16, "middle"),
            ("rect", "70,95,460,60", "frame"),
            ("text", "300,125", "DAX · BOK · YAT · LEF · …（无意义音节表）", "ink", 14, "middle"),
            ("text", "300,175", "控制：学习遍数固定 · 朗读合节拍", "muted", 13, "middle"),
            ("text", "300,215", "间隔：20 分 · 1 小时 · 1 天 · … · 31 天", "muted", 13, "middle"),
        ]),
        "flow": ("遗忘曲线测量流程", [
            ("rect", "40,40,520,230", "frame"),
            ("text", "120,85", "学习至标准", "ink", 13, "middle"),
            ("text", "280,85", "等待间隔", "ink", 13, "middle"),
            ("text", "440,85", "再学习", "ink", 13, "middle"),
            ("line", "170,85,220,85", "line"),
            ("line", "330,85,380,85", "line"),
            ("path", "80,160 140,200 200,175 260,150 320,130 380,120 460,115", "accent2"),
            ("text", "300,230", "节省率 → 遗忘曲线（先快后慢）", "muted", 13, "middle"),
        ]),
    },
    "pavlov-conditioning": {
        "setup": ("经典条件反射装置", [
            ("rect", "40,30,520,260", "frame"),
            ("ellipse", "150,150,80,50", "accent2"),
            ("text", "150,155", "实验犬", "ink", 12, "middle"),
            ("rect", "320,80,100,50", "frame"),
            ("text", "370,110", "铃声 CS", "ink", 12, "middle"),
            ("rect", "320,170,100,50", "frame"),
            ("text", "370,200", "食物 US", "ink", 12, "middle"),
            ("text", "150,230", "唾液分泌记录（非条件反应 / 条件反应）", "muted", 12, "middle"),
        ]),
        "flow": ("配对训练阶段", [
            ("rect", "40,40,520,230", "frame"),
            ("text", "130,90", "配对前", "muted", 12, "middle"),
            ("text", "130,120", "铃声 → 无唾液", "ink", 12, "middle"),
            ("text", "130,150", "食物 → 分泌", "ink", 12, "middle"),
            ("text", "370,90", "配对后", "muted", 12, "middle"),
            ("text", "370,130", "铃声 alone", "ink", 12, "middle"),
            ("text", "370,160", "→ 分泌唾液 CR", "accent3", 13, "middle"),
            ("text", "300,210", "CS + US 反复结合 → 条件反应建立", "muted", 13, "middle"),
        ]),
    },
}


def svg_wrap(title, shapes, w=600, h=300):
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
        STYLE,
        f'<rect class="bg" width="{w}" height="{h}"/>',
    ]
    for item in shapes:
        kind = item[0]
        if kind == "rect":
            coords, cls = item[1], item[2]
            x, y, rw, rh = coords.split(",")
            parts.append(f'<rect class="{cls}" x="{x}" y="{y}" width="{rw}" height="{rh}" rx="10"/>')
        elif kind == "ellipse":
            coords, cls = item[1], item[2]
            cx, cy, rx, ry = coords.split(",")
            parts.append(f'<ellipse class="{cls}" cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" opacity="0.35"/>')
        elif kind == "circle":
            coords, cls = item[1], item[2]
            cx, cy, r = coords.split(",")
            parts.append(f'<circle class="{cls}" cx="{cx}" cy="{cy}" r="{r}" opacity="0.5"/>')
        elif kind == "line":
            coords, cls = item[1], item[2]
            x1, y1, x2, y2 = coords.split(",")
            parts.append(f'<line class="{cls}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')
        elif kind == "path":
            d, cls = item[1], item[2]
            parts.append(f'<path class="{cls}" d="M{d}" fill="none" stroke-width="3"/>')
        elif kind == "text":
            coords, text, cls = item[1], item[2], item[3]
            size = item[4] if len(item) > 4 else 13
            anchor = item[5] if len(item) > 5 else "start"
            x, y = coords.split(",")
            parts.append(f'<text class="{cls}" x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}">{text}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def generic_setup(exp_id, title):
    return svg_wrap(
        title,
        [
            ("rect", "40,35,520,230", "frame"),
            ("text", "300,70", title, "ink", 17, "middle"),
            ("rect", "100,110,400,80", "frame"),
            ("text", "300,145", "实验情境 · 变量操纵 · 反应记录", "muted", 14, "middle"),
            ("text", "300,175", "（示意简图，详见右侧文字说明）", "muted", 12, "middle"),
        ],
    )


def generic_flow(exp_id, title):
    return svg_wrap(
        title,
        [
            ("rect", "40,40,520,220", "frame"),
            ("text", "130,100", "准备", "ink", 13, "middle"),
            ("text", "300,100", "操纵", "ink", 13, "middle"),
            ("text", "470,100", "测量", "ink", 13, "middle"),
            ("line", "180,100,240,100", "line"),
            ("line", "350,100,410,100", "line"),
            ("text", "300,180", title, "muted", 13, "middle"),
        ],
    )


def main():
    ASSETS.mkdir(exist_ok=True)
    ids = [
        "wundt-reaction-time", "ebbinghaus-forgetting", "pavlov-conditioning", "thorndike-puzzle-box",
        "wertheimer-phi", "kohler-insight", "watson-little-albert", "skinner-operant", "stroop-effect",
        "piaget-conservation", "asch-conformity", "milgram-obedience", "bandura-bobo", "festinger-dissonance",
        "zimbardo-prison", "loftus-misinformation", "hawthorne", "sperry-split-brain",
    ]
    titles = {eid: eid.replace("-", " ") for eid in ids}
    count = 0
    for eid in ids:
        for suffix in ("setup", "flow"):
            path = ASSETS / f"{eid}-{suffix}.svg"
            if eid in DIAGRAMS and suffix in DIAGRAMS[eid]:
                title, shapes = DIAGRAMS[eid][suffix]
                content = svg_wrap(title, shapes)
            else:
                label = "实验装置示意" if suffix == "setup" else "实验流程示意"
                content = generic_setup(eid, label) if suffix == "setup" else generic_flow(eid, label)
            path.write_text(content, encoding="utf-8")
            count += 1
    print(f"生成 {count} 个 SVG")


if __name__ == "__main__":
    main()
