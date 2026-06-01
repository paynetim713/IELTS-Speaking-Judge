"""Extract IELTS Speaking test questions from Cambridge IELTS 4-18 PDFs.

Uses BLOCK-level extraction to separate the main content column from the
procedural sidebar ("You will have to talk about the topic for one to two
minutes..." which would otherwise leak into questions).
"""
import pymupdf
import os
import re
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

PDF_DIR = r"F:\网盘下载"

PROCEDURAL_PATTERNS = [
    r"talk about the\s*topic for one to two minutes",
    r"one minute to think",
    r"some notes to\s*help you if you wish",
    r"You can make some notes",
    r"You have one minute",
    r"You will have to talk",
]
PROCEDURAL_RE = re.compile("|".join(PROCEDURAL_PATTERNS), re.I | re.S)


def is_procedural(text: str) -> bool:
    return bool(PROCEDURAL_RE.search(text or ""))


def get_clean_page_text(page) -> str:
    """Extract text via blocks, filtering out procedural sidebar blocks."""
    try:
        blocks = page.get_text("blocks")
    except Exception:
        return page.get_text()
    # Sort blocks by y (top-to-bottom) then x (left-to-right)
    blocks = sorted(blocks, key=lambda b: (round(b[1] / 5), b[0]))
    out = []
    for b in blocks:
        if len(b) < 5:
            continue
        x0, y0, x1, y1, txt = b[0], b[1], b[2], b[3], b[4]
        if not txt or not txt.strip():
            continue
        if is_procedural(txt):
            continue  # skip the sidebar
        out.append(txt)
    return "\n".join(out)


def is_speaking_page(text: str) -> bool:
    if not text:
        return False
    has_speaking_header = bool(
        "SPEAKING" in text
        or "Speaking" in text.split("\n", 1)[0]
        or re.search(r"S\s*P\s*E\s*[A\\][KX]\W*[IiTI]\W*[~NM]\W*G", text)
    )
    has_part1 = bool(re.search(r"\bPART\s*[1I]\b", text))
    has_part2 = bool(re.search(r"\bPART\s*[2II]+\b", text))
    has_part3 = bool(re.search(r"\bPART\s*[3]\b", text)) or "PART III" in text
    has_example = "EXAMPLE" in text
    has_describe = "Describe" in text
    # Need most signals
    return has_part1 and has_part2 and has_part3 and has_example and has_describe


def normalise(text: str) -> str:
    lines = text.split("\n")
    out = []
    for ln in lines:
        s = ln.rstrip()
        if not s.strip():
            continue
        if re.fullmatch(r"\d{1,3}", s.strip()):
            continue
        out.append(s)
    return "\n".join(out)


def collapse_bullets(text: str) -> str:
    """Cam 12 style: '•' alone, next line has the text → merge."""
    out = []
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        ln = lines[i].strip()
        if ln in {"•", "-", "·"} and i + 1 < len(lines):
            nxt = lines[i + 1].strip()
            out.append(f"• {nxt}")
            i += 2
        else:
            out.append(lines[i])
            i += 1
    return "\n".join(out)


def parse_speaking_section(page) -> dict:
    raw = get_clean_page_text(page)
    t = normalise(raw)
    t = collapse_bullets(t)

    # Normalise Roman PART I/II/III → PART 1/2/3
    t = re.sub(r"\bPART\s*III\b", "PART 3", t)
    t = re.sub(r"\bPART\s*II\b", "PART 2", t)
    t = re.sub(r"\bPART\s*I\b", "PART 1", t)
    parts = re.split(r"\bPART\s*([123])\b", t)
    sections = {}
    i = 1
    while i + 1 < len(parts):
        sections[f"part{parts[i]}"] = parts[i + 1]
        i += 2

    out = {"part1": [], "part2": None, "part3": []}

    # PART 1
    p1 = sections.get("part1", "")
    p1 = strip_examiner_intro(p1)
    p1 = re.sub(r"\bEXAMPLE\b\s*", "", p1)
    out["part1"] = _split_part1_topics(p1)

    # PART 2
    p2 = sections.get("part2", "")
    out["part2"] = _parse_cue_card(p2)

    # PART 3
    p3 = sections.get("part3", "")
    out["part3"] = _split_part3_topics(p3)

    return out


def strip_examiner_intro(text: str) -> str:
    text = re.sub(
        r"The examiner asks (the candidate|you) about (him/herself|yourself)[^\.]*?\.\s*",
        "",
        text,
        flags=re.S,
    )
    text = re.sub(
        r"asks the candidate about him/herself.*?familiar topics\.\s*", "", text, flags=re.S
    )
    text = re.sub(
        r"asks you about yourself.*?familiar topics\.\s*", "", text, flags=re.S
    )
    return text


def _split_part1_topics(text: str) -> list[dict]:
    topics = []
    current_topic = None
    current_qs = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("•") or line.startswith("-") or line.startswith("·"):
            q = re.sub(r"^[•\-·]\s*", "", line).strip()
            if q:
                current_qs.append(q)
        else:
            if current_topic and current_qs:
                topics.append({"topic": _clean_topic_name(current_topic), "questions": current_qs})
                current_qs = []
            current_topic = line if (not current_topic or current_qs) else (current_topic + " " + line)
            if current_qs:
                current_qs = []
    if current_topic and current_qs:
        topics.append({"topic": _clean_topic_name(current_topic), "questions": current_qs})
    topics = [t for t in topics if t["questions"] and t["topic"]]
    # Merge consecutive topics with the same name (PDF column wraps caused split)
    merged = []
    for tp in topics:
        if merged and merged[-1]["topic"].lower() == tp["topic"].lower():
            merged[-1]["questions"].extend(tp["questions"])
        else:
            merged.append(tp)
    return merged


def _clean_topic_name(name: str) -> str:
    # Strip artefacts like "' s : SPEAKJNG Speaking" / "Test1" / "Test 4" prefixes
    name = re.sub(r"^[\'\"\s\.\:,;]+", "", name).strip()
    name = re.sub(r"\b(SPEAKING|SPEAKJNG|Speaking)\b", "", name).strip()
    name = re.sub(r"\bTest\s*\d+\b", "", name).strip()
    name = re.sub(r"\bEXAMPLE\b", "", name).strip()
    name = re.sub(r"\bPART\s*1\b", "", name).strip()
    name = re.sub(r"\[Why\??/Why not\??\]", "", name).strip()
    name = re.sub(r"\s+", " ", name).strip(" ,.:;")
    # If still messy (very long), take last short title-cased chunk
    if len(name) > 60:
        chunks = re.split(r"[\.\?\n]", name)
        for c in reversed(chunks):
            c = c.strip()
            if 2 <= len(c) <= 40:
                return c
    return name


def _parse_cue_card(text: str) -> dict | None:
    if not text.strip():
        return None
    text = re.sub(PROCEDURAL_RE, "", text)

    m = re.search(
        r"(Describe[^\n]*(?:\n[^\n:]*?)*?)\s*You should say\s*:?\s*(.*?)(?:and explain|And explain)\s+(.*?)$",
        text,
        flags=re.S,
    )
    if not m:
        # Try a fallback: just grab "Describe ..." topic line, no bullets
        m2 = re.search(r"(Describe[^\n]*)", text)
        if m2:
            topic = re.sub(r"^Describe\s+", "", m2.group(1)).strip().rstrip(".")
            return {"topic": topic, "bullets": [], "explain": ""}
        return None

    topic = re.sub(r"\s+", " ", m.group(1)).strip()
    topic = re.sub(r"^Describe\s+", "", topic, flags=re.I).rstrip(".")
    bullets_blob = m.group(2)
    explain = re.sub(r"\s+", " ", m.group(3)).strip().rstrip(".")

    raw_bullets = []
    for ln in bullets_blob.split("\n"):
        ln = ln.strip()
        if not ln:
            continue
        if ln.lower().startswith("you should say"):
            continue
        ln = re.sub(r"^[•\-·]\s*", "", ln).strip()
        if ln:
            raw_bullets.append(ln)
    # Merge wrapped lines: ONLY if the prior bullet looks unfinished (very short
    # OR ends with a strict connector like "or"/"and") AND current bullet is also
    # a short fragment (< 4 words). Otherwise treat as a complete separate bullet.
    bullets = []
    HARD_CONN = {"and", "or"}
    for b in raw_bullets:
        if bullets and b:
            prev = bullets[-1]
            prev_words = prev.split()
            last_word = prev_words[-1].lower().rstrip(",.;") if prev_words else ""
            looks_unfinished = (
                last_word in HARD_CONN
                or len(prev_words) <= 3
            )
            is_fragment = len(b.split()) <= 3
            if looks_unfinished and is_fragment:
                bullets[-1] = prev + " " + b
                continue
        bullets.append(b)
    return {
        "topic": topic,
        "bullets": bullets,
        "explain": explain,
    }


def _split_part3_topics(text: str) -> list[dict]:
    text = re.sub(r"Discussion topics?:", "", text)
    chunks = re.split(r"Example questions?:", text)
    if len(chunks) < 2:
        return []
    topics = []
    subtheme = chunks[0].strip()
    for k in range(1, len(chunks)):
        body = chunks[k]
        lines = [ln.strip() for ln in body.split("\n") if ln.strip()]
        qs = []
        next_sub = None
        # Multi-line questions: a line that doesn't end with '?' is a continuation of the prior
        buffer = ""
        for ln in lines:
            if buffer:
                buffer = buffer + " " + ln
            else:
                buffer = ln
            if buffer.endswith("?"):
                # Complete question
                qs.append(buffer)
                buffer = ""
        # If buffer left without '?', it's the next subtheme name
        if buffer.strip():
            next_sub = buffer.strip()
        if qs:
            topics.append({"subtheme": _clean_subtheme(subtheme), "questions": qs})
        subtheme = next_sub or ""
        if not subtheme:
            break
    return [t for t in topics if t["subtheme"] and t["questions"]]


def _clean_subtheme(name: str) -> str:
    name = re.sub(r"\s+", " ", name).strip(" .,:;")
    # Tolerate OCR spaces "D iscussion topics" / "Discussion topic s"
    name = re.sub(r"\bD\s*iscussion\s+topic\s*s?\b\s*:?", "", name, flags=re.I).strip()
    name = re.sub(r"\bDiscussion topics?\b\s*:?", "", name).strip(" .,:;")
    return name


def main():
    all_books = {}
    for fname in sorted(os.listdir(PDF_DIR)):
        if not fname.endswith(".pdf"):
            continue
        m = re.search(r"(\d+)", fname)
        if not m:
            continue
        book_no = int(m.group(1))
        path = os.path.join(PDF_DIR, fname)
        try:
            doc = pymupdf.open(path)
        except Exception as e:
            print(f"[{fname}] open failed: {e}", file=sys.stderr)
            continue
        sp_pages = []
        for i in range(doc.page_count):
            try:
                t = doc.load_page(i).get_text()
            except Exception:
                continue
            if is_speaking_page(t):
                sp_pages.append(i + 1)
        tests = []
        for p in sp_pages:
            try:
                page = doc.load_page(p - 1)
            except Exception:
                continue
            parsed = parse_speaking_section(page)
            parsed["_page"] = p
            tests.append(parsed)
        doc.close()
        all_books[book_no] = tests
        ok = sum(
            1 for t in tests
            if t["part1"] and t["part2"] and t["part2"].get("bullets") and t["part3"]
        )
        print(f"Cam{book_no}: pages={sp_pages} ({len(tests)} tests, {ok} fully clean)")

    with open(
        r"F:\ollama_models\voice_ielts\speaking_raw.json", "w", encoding="utf-8"
    ) as f:
        json.dump(all_books, f, indent=2, ensure_ascii=False)
    print(f"\nSaved → speaking_raw.json")


if __name__ == "__main__":
    main()
