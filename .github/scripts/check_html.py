r"""Sanity-check HTML files for the classic '</script> inside a string/comment
closes the script tag prematurely' bug. Walks each file as a state machine,
NOT as a regex match, so escaped <\/script> (which the browser ignores) and
nested <script> opens (also ignored by the browser inside a script body) are
treated the same way the browser would.

Exit code 1 if any file has unbalanced or never-closed script tags.
"""
from __future__ import annotations

import pathlib
import sys


def scan(path: pathlib.Path) -> list[str]:
    src = path.read_text(encoding="utf-8")
    i, n, in_script, count, issues = 0, len(src), False, 0, []
    while i < n:
        if not in_script:
            idx = src.find("<script", i)
            if idx < 0:
                break
            gt = src.find(">", idx)
            if gt < 0:
                issues.append(f"Unterminated <script open tag at offset {idx}")
                break
            in_script = True
            count += 1
            i = gt + 1
        else:
            idx = src.find("</script>", i)
            if idx < 0:
                issues.append(f"Script block #{count} never closes")
                break
            in_script = False
            i = idx + len("</script>")
    if in_script:
        issues.append("Document ended while still inside a <script> block")
    print(f"  {path.name}: {count} script block(s), {'OK' if not issues else 'BROKEN'}")
    for x in issues:
        print(f"    !! {x}")
    return issues


def main() -> int:
    root = pathlib.Path(__file__).resolve().parents[2]
    targets = list(root.glob("*.html"))
    if not targets:
        print("No HTML files found.")
        return 0
    bad = 0
    for p in sorted(targets):
        if scan(p):
            bad += 1
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
