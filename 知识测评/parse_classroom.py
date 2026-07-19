#!/usr/bin/env python3
"""Parse 文都比邻经典题库 PDFs into per-chapter classroom quizzes."""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    import fitz
    import pytesseract
    from PIL import Image
    import io
except ImportError:
    print("请先安装: pip install pymupdf pytesseract pillow", file=sys.stderr)
    raise

ROOT = Path(__file__).parent
CACHE = ROOT / "data" / "ocr_cache"
DATA = ROOT / "data"

Q_PDF = Path("/Users/zhongyaoyao/Downloads/2026心理学经典题库-试题册-文都比邻.pdf")
A_PDF = Path("/Users/zhongyaoyao/Downloads/2026心理学经典题库-解析册-文都比邻.pdf")

# printed page from TOC +7 ≈ PDF page (part 1); refined by cache scan
PART_END_PAGE = {
    "普通心理学": 69,
    "发展心理学": 113,
    "实验心理学": 182,
    "心理与教育统计学": 230,
    "心理与教育测验学": 267,
}

MANUAL_PARTS = [
    {
        "subject": "普通心理学",
        "id": "general",
        "chapters": [
            ("第一章 心理学概述", 10),
            ("第二章 心理和行为的生物学基础", 14),
            ("第三章 意识", 18),
            ("第四章 感觉", 23),
            ("第五章 知觉", 28),
            ("第六章 记忆", 33),
            ("第七章 思维", 39),
            ("第八章 语言", 46),
            ("第九章 情绪和情感", 50),
            ("第十章 动机", 55),
            ("第十一章 能力", 59),
            ("第十二章 人格", 64),
        ],
    },
    {
        "subject": "发展心理学",
        "id": "development",
        "chapters": [
            ("第一章 发展心理学概述", 83),
            ("第二章 心理发展的基本理论", 87),
            ("第三章 婴儿心理发展", 93),
            ("第四章 幼儿心理发展", 98),
            ("第五章 童年期儿童的心理发展", 103),
            ("第六章 青少年的心理发展", 108),
            ("第七章 成年期个体心理发展", 109),
        ],
    },
    {
        "subject": "实验心理学",
        "id": "experimental",
        "chapters": [
            ("第一章 实验心理学概述", 133),
            ("第二章 心理学实验的变量与设计", 135),
            ("第三章 反应时法", 148),
            ("第四章 心理物理法", 158),
            ("第五章 主要的心理学实验", 166),
        ],
    },
    {
        "subject": "心理与教育统计学",
        "id": "statistics",
        "chapters": [
            ("第一章 绪论", 184),
            ("第二章 统计图表", 185),
            ("第三章 集中量数", 187),
            ("第四章 差异量数", 190),
            ("第五章 相对量数", 191),
            ("第六章 相关量数", 194),
            ("第七章 推断统计基础", 198),
            ("第八章 参数估计", 205),
            ("第九章 假设检验", 207),
            ("第十章 方差分析", 212),
            ("第十一章 统计功效与效果量", 219),
            ("第十二章 一元线性回归分析", 220),
            ("第十三章 χ²检验", 224),
            ("第十四章 非参数检验", 227),
            ("第十五章 多元统计分析初步", 229),
        ],
    },
    {
        "subject": "心理与教育测验学",
        "id": "measurement",
        "chapters": [
            ("第一章 心理测量的基础", 232),
            ("第二章 经典测量理论", 236),
            ("第三章 测量理论的新发展", 244),
            ("第四章 心理测验", 248),
            ("第五章 常用的心理测验", 257),
        ],
    },
]


@dataclass
class ChapterRange:
    subject: str
    subject_id: str
    chapter: str
    start: int
    end: int


def ocr_page(pdf_path: Path, pi: int, prefix: str) -> str:
    CACHE.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE / f"{prefix}_page_{pi + 1:03d}.txt"
    if cache_file.exists():
        return cache_file.read_text(encoding="utf-8")
    doc = fitz.open(pdf_path)
    page = doc[pi]
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    text = pytesseract.image_to_string(img, lang="chi_sim+eng")
    cache_file.write_text(text, encoding="utf-8")
    doc.close()
    return text


def ensure_ocr(pdf_path: Path, prefix: str, max_page: int | None = None) -> None:
    doc = fitz.open(pdf_path)
    total = max_page or doc.page_count
    for pi in range(total):
        if pi % 20 == 0:
            print(f"  OCR {prefix} {pi + 1}/{total}", flush=True)
        ocr_page(pdf_path, pi, prefix)
    doc.close()


def title_in_line(line: str, title: str, *, header: bool = False) -> bool:
    idx = line.find(title)
    if idx < 0:
        if header:
            return False
        return len(title) >= 6 and title[:5] in line and "章" in line
    if idx > 0:
        prev = line[idx - 1]
        if "\u4e00" <= prev <= "\u9fff":
            return False
    if header:
        return idx > 0 and "章" in line[:idx]
    return bool(re.search(rf"章[\s\"\"''""\u201c\u201d]*{re.escape(title)}", line)) or (
        len(title) >= 6 and bool(re.search(rf"章[\s\"\"''""\u201c\u201d]*{re.escape(title[:5])}", line))
    )


def refine_start(page_texts: dict[int, str], est: int, chapter: str) -> int:
    chap_num = chapter.split("章", 1)[0]
    chap_short = chap_num.lstrip("第")
    title = chapter.split("章", 1)[-1].strip() if "章" in chapter else chapter
    best = est
    best_score = 0
    for pi in range(max(1, est - 6), est + 7):
        text = page_texts.get(pi, "")
        if not text:
            continue
        for line in text.splitlines()[:12]:
            line = line.strip()
            if not line or "章" not in line:
                continue
            if chap_num not in line and chap_short not in line:
                continue
            if not title_in_line(line, title, header=True):
                continue
            score = 6
            if score > best_score:
                best_score = score
                best = pi
    return best if best_score >= 6 else est


def build_ranges(q_pages: int) -> list[ChapterRange]:
    flat: list[tuple[str, str, str, int]] = []
    for part in MANUAL_PARTS:
        for chapter, est in part["chapters"]:
            flat.append((part["subject"], part["id"], chapter, est))

    page_texts = {}
    for _, _, _, est in flat:
        for pi in range(max(1, est - 6), est + 7):
            if pi not in page_texts:
                f = CACHE / f"q_page_{pi:03d}.txt"
                if f.exists():
                    page_texts[pi] = f.read_text(encoding="utf-8")

    ranges: list[ChapterRange] = []
    for i, (subject, sid, chapter, est) in enumerate(flat):
        start = refine_start(page_texts, est, chapter)
        if i + 1 < len(flat) and flat[i + 1][0] == subject:
            next_start = refine_start(page_texts, flat[i + 1][3], flat[i + 1][2])
            end = next_start - 1
        else:
            end = PART_END_PAGE.get(subject, q_pages)
        end = max(start, min(end, q_pages))
        ranges.append(ChapterRange(subject, sid, chapter, start, end))
    return ranges


def normalize_ocr_text(text: str) -> str:
    text = text.replace("\u3000", " ")
    text = re.sub(r"\bAL\s", "A. ", text)
    text = re.sub(r"\bBL\s", "B. ", text)
    text = re.sub(r"\bCL\s", "C. ", text)
    text = re.sub(r"\bDL\s", "D. ", text)
    text = re.sub(r"\bFEM\b", "詹姆斯", text)
    text = re.sub(r"\bHHT\b", "合理宣泄", text)
    text = re.sub(r"\bFSH\s*-\s*IE\b", "詹姆斯-兰格", text)
    return text


SECTION_END = (
    r"(?=二[\.\、]\s*多项选择题|三[\.\、]|Part\s*B|基础提高模拟|From\s+a\s*基础|\Z)"
)
SECTION_SINGLE_CHOICE = r"(?:一[\.\、]\s*|[\u4e00-\u9fff]+[\.\、]\s*)?单项选择题"


def preprocess_question_text(text: str) -> str:
    text = re.sub(r"ME4[A-Z0-9]{5,}|bilin\.\s*wendu\.?\s*com[^\n]*", "", text, flags=re.I)
    text = re.sub(r"^[\s=@xacsaQko]+$\n?", "", text, flags=re.M | re.I)

    lines = text.split("\n")
    out: list[str] = []
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        m = re.match(r"^(\d+)\.\s*$", stripped)
        if m:
            num = m.group(1)
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and not re.match(r"^\d+\.\s*$", lines[j].strip()):
                nxt = lines[j].strip()
                if not re.match(r"^\d+\.\s*\S", nxt):
                    out.append(f"{num}. {nxt}")
                    i = j + 1
                    continue
        if re.match(r"^\.\s*[\u4e00-\u9fff]", stripped):
            stripped = re.sub(r"^\.\s*", "", stripped)
        out.append(stripped if stripped != lines[i].strip() else lines[i])
        i += 1

    merged = "\n".join(out)
    merged = re.sub(
        r"(?:^|\n)((?:\d+\.\s*\n\s*){3,})",
        lambda m: m.group(1),
        merged,
    )
    return merged


def recover_orphan_number_batch(section: str) -> str:
    """OCR may list '10.' '11.' … alone, then question bodies without numbers."""
    m = re.search(r"(?:^|\n)((?:[""\"']?\s*\d+\.\s*\n\s*){2,})", section)
    if not m:
        return section

    nums = re.findall(r"(\d+)\.", m.group(1))
    body = section[m.end() :]
    end = re.search(r"\n\s*\d+\.\s*\S", body)
    if end:
        body = body[: end.start()]
    chunks = re.split(r"(?=\([^\)]*\d{4}\.\d+[^\)]*\))", body)
    chunks = [
        re.sub(r"^\.\s*", "", c.strip())
        for c in chunks
        if c.strip() and re.search(r"[A-D][\.\、、]\s", c)
    ]
    if len(chunks) < 2:
        return section

    assigned = [f"{num}. {chunk}" for num, chunk in zip(nums, chunks)]
    tail = section[m.end() + (end.start() if end else len(body)) :]
    return section[: m.start()] + "\n" + "\n\n".join(assigned) + tail


def prepend_missing_first_question(section: str, full_text: str) -> str:
    m = re.match(r"^(\d+)\.", section.strip())
    if not m or int(m.group(1)) <= 1:
        return section
    first_num = int(m.group(1))
    m2 = re.search(
        rf"([\u4e00-\u9fff\"\"].*?(?:^|\n|\s)(?:[A-D][\.\、、]\s).+?)(?=\n\s*{first_num}\.\s*\S)",
        preprocess_question_text(normalize_ocr_text(full_text)),
        re.S,
    )
    if m2:
        return f"1. {m2.group(1).strip()}\n\n{section}"
    return section


def extract_single_choice_section(text: str) -> str:
    raw = preprocess_question_text(normalize_ocr_text(text))

    m = re.search(rf"{SECTION_SINGLE_CHOICE}\s*(.*?){SECTION_END}", raw, re.S | re.I)
    if m:
        section = recover_orphan_number_batch(m.group(1).strip())
        return prepend_missing_first_question(section, raw)

    m = re.search(rf"((?:^|\n)\d+\.\s*\S[\s\S]*?){SECTION_END}", raw, re.S)
    if m:
        section = recover_orphan_number_batch(m.group(1).strip())
        return prepend_missing_first_question(section, raw)

    m = re.search(rf"第[一二三四五六七八九十]+章[^\n]*\n([\s\S]*?){SECTION_END}", raw, re.S)
    if m:
        chunk = recover_orphan_number_batch(m.group(1).strip())
        m2 = re.search(r"(\d+\.\s*\S[\s\S]+)", chunk)
        if m2:
            section = m2.group(1).strip()
            return prepend_missing_first_question(section, raw)
        m3 = re.search(
            r"([\u4e00-\u9fff\"\"].*?(?:^|\n|\s)(?:[A-D][\.\、、]\s).*)",
            chunk,
            re.S,
        )
        if m3:
            return "1. " + m3.group(1).strip()
    return ""


def clean_stem(raw: str) -> str:
    stem = re.sub(r"\s+", " ", raw).strip()
    stem = re.sub(r"\(\s*(?:[。\.]\s*)+\)", "()", stem)
    stem = re.sub(r"\(\s*\)", "", stem)
    stem = re.sub(r"\s*\(\d{4}[^)]*\)\s*", "", stem)
    stem = re.sub(r"\s*\(\s*\)\s*", "", stem)
    return stem.strip(" .，,")


NEXT_Q_PATTERNS = (
    r"\s+\d{1,2}\.\s*[\u4e00-\u9fff\(（「]",
    r"\s+\d{1,2}[\"\"''""]\s*[\u4e00-\u9fff\(（「]",
    r"\s+\d{1,2}\s+[\u4e00-\u9fff\(（「]",
    r"\s+[A-Z]{1,2}\.\s*[\u4e00-\u9fff\(（「]",  # OCR: LL. → 11.
)


def truncate_at_next_question(text: str) -> str:
    """Cut off OCR bleed from the next question."""
    best = len(text)
    for pat in NEXT_Q_PATTERNS:
        m = re.search(pat, text)
        if m:
            best = min(best, m.start())
    m = re.search(r"\s+Part\s+[A-Z]\b", text, re.I)
    if m:
        best = min(best, m.start())
    return text[:best].strip()


def option_looks_corrupt(text: str) -> bool:
    if len(text) > 55:
        return True
    for pat in NEXT_Q_PATTERNS:
        if re.search(pat, text):
            return True
    if re.search(r"[=£]{2,}", text):
        return True
    return False


def clean_option_text(raw: str) -> str:
    txt = truncate_at_next_question(re.sub(r"\s+", " ", raw).strip())
    txt = re.split(r"\s+[A-D][\.\、、]\s", txt)[0]
    txt = re.sub(r"[=£]{3,}.*$", "", txt)
    return txt.strip(" .，,")


def split_options(rest: str) -> list[dict] | None:
    rest = normalize_ocr_text(rest)
    markers = list(re.finditer(r"(?:^|\n|\s)([A-D])[\.\、、]\s*", rest))
    if len(markers) < 2:
        return None
    options = []
    for i, m in enumerate(markers[:4]):
        key = m.group(1)
        start = m.end()
        end = markers[i + 1].start() if i + 1 < len(markers) else len(rest)
        txt = clean_option_text(rest[start:end])
        if not txt or len(txt) > 55:
            return None
        options.append({"key": key, "text": txt})
    if len(options) < 2:
        return None
    # dedupe keys
    keys = [o["key"] for o in options]
    if len(set(keys)) != len(keys):
        return None
    return options


def parse_questions(text: str) -> list[dict]:
    section = extract_single_choice_section(text)
    if not section:
        return []

    questions: list[dict] = []
    blocks = re.split(r"(?=^\d+\.\s*\S)", section, flags=re.M)
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        m = re.match(r"^(\d+)\.\s*(.+)", block, re.S)
        if not m:
            continue
        source_num = int(m.group(1))
        rest = m.group(2)
        opt_mark = re.search(r"(?:^|\n|\s)([A-D])[\.\、、]\s*", rest)
        if not opt_mark:
            continue
        stem = clean_stem(rest[: opt_mark.start()])
        if len(stem) < 4:
            continue
        options = split_options(rest[opt_mark.start() :])
        if not options or len(options) < 3:
            continue
        if any(option_looks_corrupt(o["text"]) for o in options):
            continue
        questions.append(
            {
                "sourceNumber": source_num,
                "stem": stem,
                "options": options,
                "score": None,
            }
        )

    # sequential display numbers
    for i, q in enumerate(questions, 1):
        q["number"] = i
    return questions


ANSWER_KEY = r"(Al|Bl|Cl|Dl|[A-D])"


def normalize_answer_key(raw: str) -> str:
    return raw[0].upper()


def find_answer_start(a_pages: dict[int, str], chapter: str) -> int | None:
    chap_num = chapter.split("章", 1)[0]
    chap_short = chap_num.lstrip("第")
    title = chapter.split("章", 1)[-1].strip() if "章" in chapter else chapter
    for pi in sorted(a_pages.keys()):
        text = a_pages[pi]
        if "答案解析" not in text and "答案要点" not in text:
            continue
        for line in text.splitlines()[:80]:
            if "章" not in line:
                continue
            if chap_num not in line and f"{chap_short}章" not in line:
                continue
            if title_in_line(line, title, header=True):
                return pi
    return None


def extract_answer_section(text: str) -> str:
    """Limit to 统考 Part A single-choice answers."""
    text = normalize_ocr_text(text)
    m = re.search(r"(?:Part\s*A|统考历年真[题古])", text, re.I)
    if m:
        text = text[m.start() :]
    m2 = re.search(
        r"(?:Part\s*B|基础提高模拟|二[\.\、]\s*多项选择题|三[\.\、])",
        text,
        re.I,
    )
    if m2:
        text = text[: m2.start()]
    return text


def answer_page_range(
    a_pages: dict[int, str],
    chapter: str,
    next_chapter: str | None,
    a_total: int,
    q_fallback_start: int,
) -> tuple[int, int]:
    start = find_answer_start(a_pages, chapter)
    if start is None:
        start = max(1, q_fallback_start - 1)
    end = min(a_total, start + 4)
    if next_chapter:
        next_start = find_answer_start(a_pages, next_chapter)
        if next_start and next_start > start:
            end = next_start - 1
    return start, min(a_total, max(start, end))


def parse_answers(text: str) -> dict[int, dict]:
    answers: dict[int, dict] = {}
    last_num = 0
    pattern = re.compile(
        rf"(?:^|\n)\s*(?:(\d+)\.\s*)?[\.]?\s*{ANSWER_KEY}\s*[\s\[]*[【\[]?\s*答案解析[\]】]?\s*(.*?)"
        rf"(?=(?:\n\s*(?:(?:\d+)\.\s*)?[\.]?\s*{ANSWER_KEY}\s*[\s\[]*[【\[]?\s*答案解析)|\Z)",
        re.S | re.I,
    )
    for m in pattern.finditer(text):
        if m.group(1):
            num = int(m.group(1))
        else:
            num = last_num + 1 if last_num else 1
        last_num = num
        key = normalize_answer_key(m.group(2))
        expl = re.sub(r"\s+", " ", m.group(3).strip())
        expl = re.split(rf"\s*[\.]?\s*{ANSWER_KEY}\s*[\s\[]*[【\[]?\s*答案解析", expl)[0].strip()
        answers[num] = {"correctKey": key, "explanation": expl or f"正确答案：{key}"}
    return answers


def chapter_text(pages: dict[int, str], start: int, end: int) -> str:
    return "\n".join(pages.get(pi, "") for pi in range(start, end + 1))


def load_cached_pages(prefix: str, total: int) -> dict[int, str]:
    pages = {}
    for pi in range(1, total + 1):
        f = CACHE / f"{prefix}_page_{pi:03d}.txt"
        if f.exists():
            pages[pi] = f.read_text(encoding="utf-8")
    return pages


def slugify(s: str) -> str:
    s = re.sub(r"\s+", "-", s.strip())
    s = re.sub(r"[^\w\u4e00-\u9fff-]", "", s)
    return s[:40] or "chapter"


def main():
    if not Q_PDF.exists() or not A_PDF.exists():
        raise SystemExit(f"Missing PDF: {Q_PDF} or {A_PDF}")

    q_doc = fitz.open(Q_PDF)
    a_doc = fitz.open(A_PDF)
    q_total, a_total = q_doc.page_count, a_doc.page_count
    q_doc.close()
    a_doc.close()

    print("OCR question book (cached pages skipped)...")
    ensure_ocr(Q_PDF, "q", q_total)
    print("OCR answer book (cached pages skipped)...")
    ensure_ocr(A_PDF, "a", a_total)

    q_pages = load_cached_pages("q", q_total)
    a_pages = load_cached_pages("a", a_total)

    ranges = build_ranges(q_total)
    exams = []
    chapter_order = 0

    for idx, cr in enumerate(ranges):
        chapter_order += 1
        q_text = chapter_text(q_pages, cr.start, cr.end)
        questions = parse_questions(q_text)
        if not questions:
            print(f"  skip (no questions): {cr.subject} / {cr.chapter}")
            continue

        next_chapter = None
        if idx + 1 < len(ranges) and ranges[idx + 1].subject == cr.subject:
            next_chapter = ranges[idx + 1].chapter
        a_start, a_end = answer_page_range(
            a_pages, cr.chapter, next_chapter, a_total, cr.start
        )
        a_text = extract_answer_section(chapter_text(a_pages, a_start, a_end))
        ans_map = parse_answers(a_text)

        merged = []
        for q in questions:
            src = q.get("sourceNumber", q["number"])
            ans = ans_map.get(src, {})
            correct = ans.get("correctKey")
            expl = ans.get("explanation", "")
            if not expl and correct:
                opt = next((o["text"] for o in q["options"] if o["key"] == correct), "")
                expl = f"正确答案：{correct}. {opt}" if opt else f"正确答案：{correct}"
            merged.append(
                {
                    "number": q["number"],
                    "sourceNumber": src,
                    "stem": q["stem"],
                    "score": q["score"],
                    "options": q["options"],
                    "correctKey": correct,
                    "explanation": expl or "暂无解析",
                }
            )

        exam_id = f"classroom-{cr.subject_id}-{slugify(cr.chapter)}"
        exams.append(
            {
                "id": exam_id,
                "type": "classroom",
                "subject": cr.subject,
                "subjectId": cr.subject_id,
                "chapter": cr.chapter,
                "chapterOrder": chapter_order,
                "title": f"{cr.subject} · {cr.chapter}",
                "subtitle": f"{len(merged)} 题 · 随堂小测",
                "questionCount": len(merged),
                "questions": merged,
            }
        )
        matched = sum(1 for q in merged if q["correctKey"])
        print(f"  {cr.subject} / {cr.chapter}: {len(merged)} q, {matched} answers (q p{cr.start}-{cr.end}, a p{a_start}-{a_end})")

    DATA.mkdir(parents=True, exist_ok=True)
    json_path = DATA / "classroom.json"
    json_path.write_text(json.dumps(exams, ensure_ascii=False, indent=2), encoding="utf-8")
    js_path = DATA / "classroom.js"
    js_path.write_text(
        "/* Auto-generated by parse_classroom.py */\n"
        "window.CLASSROOM_EXAMS = "
        + json.dumps(exams, ensure_ascii=False, indent=2)
        + ";\n",
        encoding="utf-8",
    )
    print(f"\nWrote {len(exams)} chapter quizzes -> {json_path}")


if __name__ == "__main__":
    main()
