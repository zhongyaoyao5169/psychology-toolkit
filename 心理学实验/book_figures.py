"""教材插图配置：仅在有图/表/图例时裁剪，不用整页截图。"""

PRINTED_OFFSET = 16
PRINTED_OFFSET_FROM = 191


def printed_page(pdf_page: int) -> int:
    if pdf_page >= PRINTED_OFFSET_FROM:
        return pdf_page - PRINTED_OFFSET
    return pdf_page


# file  stem -> 实验 id、标题、PDF 页、归一化裁剪框 (x0,y0,x1,y1)
BOOK_FIGURES = [
    {
        "file": "donders-subtraction-fig412-413",
        "experimentId": "donders-subtraction",
        "title": "图4-12 / 4-13 唐德斯 B、C 反应任务示意",
        "pdfPage": 217,
        "rect": (0.05, 0.04, 0.98, 0.30),
    },
    {
        "file": "donders-subtraction-fig414",
        "experimentId": "donders-subtraction",
        "title": "图4-14 唐德斯减数法图解",
        "pdfPage": 217,
        "rect": (0.05, 0.48, 0.98, 0.88),
    },
    {
        "file": "weber-law-fig58",
        "experimentId": "weber-law",
        "title": "图5-8 重量判断的韦伯分数",
        "pdfPage": 267,
        "rect": (0.08, 0.38, 0.92, 0.78),
    },
    {
        "file": "ebbinghaus-forgetting-fig81",
        "experimentId": "ebbinghaus-forgetting",
        "title": "图8-1 遗忘曲线",
        "pdfPage": 449,
        "rect": (0.12, 0.06, 0.88, 0.42),
    },
    {
        "file": "stroop-effect-table1",
        "experimentId": "stroop-effect",
        "title": "表1 斯特鲁普实验记录表",
        "pdfPage": 366,
        "rect": (0.06, 0.18, 0.94, 0.52),
    },
]


def figures_for_experiment(experiment_id: str) -> list:
    out = []
    for fig in BOOK_FIGURES:
        if fig["experimentId"] != experiment_id:
            continue
        pdf_p = fig["pdfPage"]
        out.append({
            "title": fig["title"],
            "image": f"assets/book/{fig['file']}.png",
            "fallback": f"assets/book/{fig['file']}.svg",
            "bookPage": printed_page(pdf_p),
            "pdfPage": pdf_p,
        })
    return out
