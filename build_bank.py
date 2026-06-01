"""Combine the curated bank (from webapp.py) with Cambridge-extracted data
into a single clean question_bank.py module.
"""
import json
import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding="utf-8")


# ─── Existing curated bank (verified, kept verbatim) ────────────────────
PART1_BANK_CURATED = {
    "work_study": [
        "What do you do — work or study?",
        "What is your job?",
        "Why did you choose that job or subject?",
        "Do you enjoy your work or studies? Why?",
    ],
    "hometown": [
        "Where is your hometown?",
        "Tell me about the city where you live.",
        "What do you like most about your hometown?",
        "Has your hometown changed much since you were a child?",
    ],
    "home_accommodation": [
        "Do you live in a house or an apartment?",
        "Which is your favourite room in your home? Why?",
        "How long have you lived there?",
        "Would you like to move to a different home in the future?",
    ],
    "food": [
        "Can you find food from many different countries where you live?",
        "How often do you eat typical food from other countries?",
        "Have you ever tried making food from another country?",
        "What food from your country would you recommend to people from other countries?",
    ],
    "fruit": [
        "Which fruit do you enjoy eating the most?",
        "Are there any fruits that you prefer not to eat? Why?",
        "Do you like meals that include fruit as an ingredient?",
        "Where do you usually buy fresh fruit near your home?",
    ],
    "sleep": [
        "How many hours do you usually sleep at night?",
        "Do you sometimes sleep during the day?",
        "What do you do if you can't get to sleep at night?",
        "Do you ever remember the dreams you've had while you were asleep?",
    ],
    "museums": [
        "Did you enjoy going to museums when you were a child?",
        "Are there any interesting museums near where you live now?",
        "Do you think it is best to go to museums by yourself or with friends?",
        "When you visit another city or country, do you think it's important to go to a museum there?",
    ],
    "walking": [
        "How much walking do you do in your daily life?",
        "Do you prefer walking alone or with other people?",
        "Is there anywhere near where you live that is good for walking?",
        "Do you think people walk less than they did in the past? Why?",
    ],
    "weather": [
        "What's the weather usually like where you live?",
        "What kind of weather do you like best? Why?",
        "Does the weather affect what you do during the day?",
        "Do you prefer hot weather or cold weather?",
    ],
    "music": [
        "What kind of music do you usually listen to?",
        "Do you ever listen to live music?",
        "Has the kind of music you like changed since you were a child?",
        "Do you think it's important for children to learn an instrument?",
    ],
    "weekends": [
        "What do you usually do on weekends?",
        "Do you prefer to spend weekends with family or with friends?",
        "Are your weekends now different from when you were a child?",
        "What would be your ideal way to spend a weekend?",
    ],
    "shopping": [
        "Do you enjoy shopping?",
        "Do you prefer shopping online or in actual shops?",
        "How often do you go shopping for clothes?",
        "Has the way you shop changed in recent years?",
    ],
    "photos": [
        "Do you often take photos?",
        "Do you prefer taking photos of people or of places?",
        "Do you usually keep your photos on your phone or print them?",
        "When was the last time you took a photo that you really liked?",
    ],
    "friends": [
        "Do you have many friends?",
        "How often do you see your friends?",
        "Do you prefer to have a few close friends or many friends?",
        "Have you known any of your friends for a long time?",
    ],
    "technology": [
        "How much time do you spend on your phone each day?",
        "What apps do you use most often?",
        "Has technology changed the way you communicate with friends?",
        "Do you think people rely on technology too much?",
    ],
}

PART2_BANK_CURATED = [
    {"topic": "a person you admire", "bullets": ["who this person is", "how you know them", "what qualities they have"], "explain": "why you admire this person", "p3_key": "person_admire"},
    {"topic": "a memorable journey you have taken", "bullets": ["where you went", "who you went with", "what you did during the journey"], "explain": "why this journey was memorable for you", "p3_key": "memorable_journey"},
    {"topic": "a useful skill you learned", "bullets": ["what the skill is", "when and where you learned it", "how you learned it"], "explain": "why this skill has been useful for you", "p3_key": "useful_skill"},
    {"topic": "a situation when you had to adjust your original plans unexpectedly", "bullets": ["what your initial plans were", "what caused you to change them", "what new arrangements you made"], "explain": "how you felt about having to make these changes", "p3_key": "changed_plan"},
    {"topic": "a book you have recently read", "bullets": ["what kind of book it is", "what it is about", "what sort of people would enjoy it"], "explain": "why you liked it", "p3_key": "book_read"},
    {"topic": "a film you would like to watch again", "bullets": ["what the film is", "when you first saw it", "who you would watch it with"], "explain": "why you would like to watch it again", "p3_key": "film_again"},
    {"topic": "a foreign country you would like to visit", "bullets": ["which country it is", "how you first heard about it", "what you would do there"], "explain": "why you would like to visit this country", "p3_key": "foreign_country"},
    {"topic": "an important decision you made", "bullets": ["what the decision was", "when and where you made it", "what the result of the decision was"], "explain": "why this decision was important to you", "p3_key": "important_decision"},
    {"topic": "a place you like to spend time in", "bullets": ["where this place is", "how often you go there", "what you do there"], "explain": "why you like spending time there", "p3_key": "place_to_spend_time"},
    {"topic": "a piece of work you felt satisfied with", "bullets": ["what the work was", "when you did it", "how you did it"], "explain": "why you felt satisfied with this piece of work", "p3_key": "satisfying_work"},
    {"topic": "some food or drink that you learned to prepare", "bullets": ["what food or drink it is", "when and how you learned to prepare it", "who taught you to prepare it"], "explain": "how you felt when you first prepared it", "p3_key": "food_prepared"},
    {"topic": "a law that was introduced in your country and that you thought was a very good idea", "bullets": ["what the law was", "who introduced it", "when and why it was introduced"], "explain": "why you thought this law was such a good idea", "p3_key": "good_law"},
]

PART3_THEMES_CURATED = {
    "person_admire": [
        ("Role models in society", ["What kinds of people do young people admire today?", "Do you think celebrities make good role models? Why or why not?", "How has the idea of a role model changed compared with the past?"]),
        ("Qualities society values", ["Which personal qualities are most respected in your country?", "Do schools do enough to teach children about good values?", "Are the qualities people admire the same in every culture?"]),
    ],
    "memorable_journey": [
        ("Travelling abroad", ["Why do people like to travel to other countries?", "How has international travel changed in the last twenty years?", "What do young people gain from travelling abroad?"]),
        ("Cultural understanding through travel", ["Does travelling really change the way people see other cultures?", "What do tourists often miss when they visit a foreign country?", "Are there good alternatives to travel for learning about other cultures?"]),
    ],
    "useful_skill": [
        ("Learning new skills", ["What skills are most useful for young people to learn today?", "Is it better to learn a skill from a teacher or by yourself?", "Do you think adults find it harder to learn new skills than children?"]),
        ("Skills and work", ["Which skills do employers value most in your country?", "Should schools focus more on practical skills or academic knowledge?", "How will the skills people need at work change in the future?"]),
    ],
    "changed_plan": [
        ("Planning and flexibility", ["Why do some people plan everything in detail while others do not?", "Is it better to make detailed plans or to be flexible?", "How do people react when their plans are suddenly disrupted?"]),
        ("Dealing with change", ["Why do many people find change difficult?", "How can people prepare for unexpected changes in life?", "Do you think modern life requires people to be more adaptable than before?"]),
    ],
    "book_read": [
        ("Reading habits", ["Do people in your country read as much as they used to?", "What kinds of books are most popular with young readers today?", "Why do some people prefer e-books to paper books?"]),
        ("Books and education", ["How important is reading for children's development?", "Should schools choose the books children read, or should children choose themselves?", "Can books teach values better than films or television?"]),
    ],
    "film_again": [
        ("Films and entertainment", ["What kinds of films are most popular in your country?", "Do you think people watch more films now than in the past? Why?", "How have streaming services changed the way people watch films?"]),
        ("Cinema vs home viewing", ["Is going to the cinema still a popular activity?", "What are the advantages of watching films at home?", "Do you think cinemas will exist in twenty years' time?"]),
    ],
    "foreign_country": [
        ("Reasons for international travel", ["Why do people choose to visit certain countries over others?", "How important is the cost of travel when choosing a destination?", "Do social media and the internet influence where people travel?"]),
        ("Tourism and local communities", ["What problems can large groups of tourists create for local residents?", "How can tourism benefit a local economy?", "Should governments limit the number of tourists in popular places?"]),
    ],
    "important_decision": [
        ("Decision-making in daily life", ["Do you think people make decisions too quickly nowadays?", "Is it better to make decisions alone or to ask others for advice?", "What kinds of decisions do young people find most difficult?"]),
        ("Decisions and consequences", ["How can people learn from the wrong decisions they make?", "Should parents make important decisions for their children?", "Do you think technology helps people make better decisions?"]),
    ],
    "place_to_spend_time": [
        ("Public spaces in cities", ["What kinds of public places do people in your country enjoy?", "Are there enough green spaces in cities today?", "How can governments make cities more pleasant to live in?"]),
        ("Relaxation and wellbeing", ["Why is it important for people to have places where they can relax?", "Do you think modern life gives people enough time to relax?", "How do people's ways of relaxing change as they get older?"]),
    ],
    "satisfying_work": [
        ("Job satisfaction", ["What makes a job satisfying for most people?", "Is money the most important factor when choosing a job?", "Do you think people are more satisfied with their work today than in the past?"]),
        ("Work and personal growth", ["How does work contribute to a person's sense of identity?", "Should people change jobs often to grow, or stay in one career?", "What can employers do to make work more meaningful?"]),
    ],
    "food_prepared": [
        ("Cooking skills for young people", ["Do you think it is important for children to learn to cook?", "Should young people learn to cook at home or at school?", "Why do many young people today prefer fast food to home cooking?"]),
        ("Food culture and career", ["How enjoyable would it be to work as a professional chef?", "How do celebrity chefs influence people's eating habits?", "How has the food people eat in your country changed in recent years?"]),
    ],
    "good_law": [
        ("School rules", ["What kinds of rules are common in a school?", "How important is it to have rules in a school?", "What do you recommend should happen if children break school rules?"]),
        ("Working in the legal profession", ["Can you suggest why many students decide to study law at university?", "What are the key personal qualities needed to be a successful lawyer?", "Do you agree that working in the legal profession is very stressful?"]),
    ],
}

DEFAULT_PART3 = [
    ("Society in general", [
        "why this is becoming more or less common in society",
        "how this has changed over the past few decades",
        "whether this is more important in your country than elsewhere",
    ]),
    ("People's daily lives", [
        "how this affects different age groups",
        "what role technology plays in this",
    ]),
]


# ─── OCR / cleanup helpers ───────────────────────────────────────────────

def fix_ocr(text: str) -> str:
    """Repair common OCR artefacts in Cambridge PDF text."""
    if not text:
        return text
    # Full-width period substituted for 'o': "y。u" → "you", "phot。" → "photo"
    text = text.replace("。", "o")
    text = text.replace("「", "r")  # CJK bracket → r
    text = text.replace("」", "")
    text = text.replace("旦", "")
    text = text.replace("囸", "")
    text = text.replace("缸", "")
    text = text.replace("Y o·u", "You")
    text = text.replace("·", "")
    text = text.replace("\xa0", " ")
    # OCR mis-reads of trailing "?]" → "η" or "n]"
    text = re.sub(r"η$", "?]", text)
    text = re.sub(r"\bη\b", "?]", text)
    # "yourneighbours" → "your neighbours" (space dropped in OCR)
    text = re.sub(r"\byour([a-z])", r"your \1", text)
    # Known split-word OCR artefacts: rejoin internal space
    SPLITS = {
        "som ething": "something",
        "discussi on": "discussion",
        "discussi,on": "discussion",
        "coUege": "college",
        "anyth ing": "anything",
        "noth ing": "nothing",
        "everyth ing": "everything",
        "ev erybody": "everybody",
        "p eople": "people",
        "wo rk": "work",
        "ve叩often": "very often",
        "叩": "ry ",
        "give-their": "give their",
        "th ought": "thought",
        " .to ": " to ",
        " · ": " ",
        "tomeet": "to meet",
        "ofthis": "of this",
        "isthe": "is the",
    }
    for bad, good in SPLITS.items():
        text = text.replace(bad, good)
    # Multiple spaces
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def has_garbage(text: str) -> bool:
    """Detect OCR garbage we can't fix automatically (space-broken words, weird symbols)."""
    if not text:
        return True
    # Heuristic: a word with 1 letter between spaces inside (e.g. "som ething")
    # OR mostly non-ASCII letters
    if re.search(r"\b[a-z]{1,2}\s[a-z]{2,}\b", text.lower()):
        # Could be false positive ("a man"). Require more specific patterns:
        if re.search(r"\b(som|ething|y u|t meet|y u|w rk)\b", text.lower()):
            return True
    if re.search(r"[~←→€々々\\]", text):
        return True
    return False


def slugify(name: str) -> str:
    """Turn 'Television programmes' → 'television_programmes'."""
    name = fix_ocr(name).lower()
    name = re.sub(r"[^a-z0-9]+", "_", name)
    name = name.strip("_")
    return name or "topic"


def clean_question(q: str) -> str:
    """Strip OCR noise from a question, leave punctuation."""
    q = fix_ocr(q)
    # Drop "[Why?]" / "[Why/Why not?]" trailing hints — they're a hint to the candidate, keep optional
    # Actually keep them — Cambridge prints them on real exam.
    return q.strip()


def is_clean_question(q: str) -> bool:
    if not q:
        return False
    if len(q) < 8 or len(q) > 280:
        return False
    if has_garbage(q):
        return False
    # Must end with ? or . or ] (Cambridge prints [Why?] hints after some Qs)
    if not (q.endswith("?") or q.endswith(".") or q.endswith("]")):
        return False
    # Must contain at least one '?' somewhere
    if "?" not in q and not q.endswith("."):
        return False
    return True


def is_clean_topic(t: str) -> bool:
    if not t:
        return False
    if len(t) < 3 or len(t) > 80:
        return False
    if has_garbage(t):
        return False
    # Leftover examiner-intro patterns
    if re.search(r"examiner|familiar topics|asks (the|you)", t, re.I):
        return False
    return True


# ─── Build merged bank ──────────────────────────────────────────────────

def _load_raw():
    """Merge PDF-extracted speaking_raw.json with cambridge_manual.json (user-provided
    transcriptions for image-only PDFs like Cam 9/14/15/16/18). Manual entries APPEND
    to the extracted ones — they do not replace, so a book with both gets all tests."""
    import os
    extracted = {}
    raw_path = r"F:\ollama_models\voice_ielts\speaking_raw.json"
    if os.path.exists(raw_path):
        extracted = json.load(open(raw_path, encoding="utf-8"))
    manual_path = r"F:\ollama_models\voice_ielts\cambridge_manual.json"
    if os.path.exists(manual_path):
        manual = json.load(open(manual_path, encoding="utf-8"))
        for book, tests in manual.items():
            extracted.setdefault(book, [])
            extracted[book].extend(tests)
    return extracted


def main():
    raw = _load_raw()

    # P1: start with curated, add Cambridge topics with unique slugs
    p1 = {k: list(v) for k, v in PART1_BANK_CURATED.items()}
    p1_sources = {k: "curated" for k in p1.keys()}
    added_p1_keys_to_topics = {}  # slug → friendly name (for /api/topics)

    p2 = list(PART2_BANK_CURATED)
    p2_topics_seen = {fix_ocr(c["topic"]).lower() for c in p2}

    p3 = {k: [(sub, list(qs)) for sub, qs in v] for k, v in PART3_THEMES_CURATED.items()}

    for book, tests in raw.items():
        for ti, test in enumerate(tests):
            # ─ Part 1 topics ─
            for tp in test.get("part1", []):
                topic_name = fix_ocr(tp.get("topic", ""))
                if not is_clean_topic(topic_name):
                    continue
                qs = [clean_question(q) for q in tp.get("questions", [])]
                qs = [q for q in qs if is_clean_question(q)]
                if len(qs) < 3:
                    continue
                slug = f"cam{book}_{slugify(topic_name)}"
                # Dedup: if a curated slug matches (e.g., "music"), keep curated; otherwise add
                # Allow multiple Cambridge variants since they're real exam history.
                p1[slug] = qs[:4]
                p1_sources[slug] = f"Cam{book} Test{ti+1}"

            # ─ Part 2 cue card ─
            card = test.get("part2") or {}
            topic = fix_ocr(card.get("topic", ""))
            bullets = [fix_ocr(b) for b in card.get("bullets", [])]
            bullets = [b for b in bullets if b and not has_garbage(b)]
            explain = fix_ocr(card.get("explain", ""))
            if (
                topic
                and len(topic) > 8
                and not has_garbage(topic)
                and len(bullets) >= 2
                and explain
                and not has_garbage(explain)
                and topic.lower() not in p2_topics_seen
            ):
                # Generate p3_key
                p3_key = f"cam{book}_{slugify(topic)[:30]}"
                # Try to attach Part 3 themes from same test
                themes_in = test.get("part3", [])
                themes_out = []
                for sub in themes_in:
                    sub_name = fix_ocr(sub.get("subtheme", ""))
                    sub_qs = [clean_question(q) for q in sub.get("questions", [])]
                    sub_qs = [q for q in sub_qs if is_clean_question(q)]
                    if is_clean_topic(sub_name) and len(sub_qs) >= 2:
                        themes_out.append((sub_name, sub_qs[:3]))
                if themes_out:
                    p3[p3_key] = themes_out
                    p2.append({
                        "topic": topic,
                        "bullets": bullets[:3],
                        "explain": explain,
                        "p3_key": p3_key,
                        "_source": f"Cam{book} Test{ti+1}",
                    })
                    p2_topics_seen.add(topic.lower())

    print(f"FINAL: P1 topics={len(p1)} | P2 cards={len(p2)} | P3 themes={len(p3)}")

    # Write question_bank.py
    out_path = r"F:\ollama_models\voice_ielts\question_bank.py"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(render_module(p1, p2, p3))
    print(f"Wrote → {out_path}")


def py_repr_str(s: str) -> str:
    """Repr that prefers double-quotes when the string has ASCII apostrophes only."""
    if '"' not in s:
        return '"' + s.replace("\\", "\\\\").replace("\n", "\\n") + '"'
    return repr(s)


def render_module(p1: dict, p2: list, p3: dict) -> str:
    lines = [
        '"""IELTS Speaking question bank.',
        "",
        "Sources:",
        "    - Curated core: a verified deep-research pass over Cambridge IELTS 18/19/20,",
        "      IELTS Liz, Keith Speaking Academy, Goat Guru, IELTS Juice.",
        "    - Cambridge extractions: verbatim from Cambridge IELTS 4-17 PDFs",
        "      (those with extractable text — books 4-8, 10-13, 17).",
        "",
        "Bank shape:",
        "    PART1_BANK: dict[str, list[str]]   — topic slug → 3-4 Q",
        "    PART2_BANK: list[dict]             — cue cards with p3_key linking to PART3_THEMES",
        "    PART3_THEMES: dict[str, list[tuple[str, list[str]]]]   — p3_key → list of (sub-theme, [Q])",
        "    DEFAULT_PART3: fallback Part 3 when a cue card has no matching p3_key.",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "",
        "PART1_BANK: dict[str, list[str]] = {",
    ]
    for k, qs in p1.items():
        lines.append(f"    {py_repr_str(k)}: [")
        for q in qs:
            lines.append(f"        {py_repr_str(q)},")
        lines.append("    ],")
    lines.append("}")
    lines.append("")
    lines.append("")
    lines.append("PART2_BANK: list[dict] = [")
    for card in p2:
        lines.append("    {")
        lines.append(f"        \"topic\": {py_repr_str(card['topic'])},")
        lines.append("        \"bullets\": [")
        for b in card["bullets"]:
            lines.append(f"            {py_repr_str(b)},")
        lines.append("        ],")
        lines.append(f"        \"explain\": {py_repr_str(card['explain'])},")
        lines.append(f"        \"p3_key\": {py_repr_str(card['p3_key'])},")
        lines.append("    },")
    lines.append("]")
    lines.append("")
    lines.append("")
    lines.append("PART3_THEMES: dict[str, list[tuple[str, list[str]]]] = {")
    for k, themes in p3.items():
        lines.append(f"    {py_repr_str(k)}: [")
        for sub_name, qs in themes:
            lines.append("        (")
            lines.append(f"            {py_repr_str(sub_name)},")
            lines.append("            [")
            for q in qs:
                lines.append(f"                {py_repr_str(q)},")
            lines.append("            ],")
            lines.append("        ),")
        lines.append("    ],")
    lines.append("}")
    lines.append("")
    lines.append("")
    lines.append("DEFAULT_PART3: list[tuple[str, list[str]]] = [")
    for sub_name, qs in DEFAULT_PART3:
        lines.append("    (")
        lines.append(f"        {py_repr_str(sub_name)},")
        lines.append("        [")
        for q in qs:
            lines.append(f"            {py_repr_str(q)},")
        lines.append("        ],")
        lines.append("    ),")
    lines.append("]")
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
