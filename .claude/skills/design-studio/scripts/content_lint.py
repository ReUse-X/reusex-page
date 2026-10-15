#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Povl Filip Sonne-Frederiksen
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guard the content model: content says WHAT, templates decide HOW.

For every Markdown page under content/ (and gallery snippets, *.txt under
content/**/examples/):
  - front matter is at most 10 lines and uses only the allowed keys
    (title, description, layout, draft, date, aliases, weight, translationKey,
    summary, linkTitle) — menus live in hugo.toml, lists of things in data/
  - layout is one of the theme's page layouts (landing, article, deck)
  - no hand-written HTML in the body (use a content element instead); HTML
    comments and code are fine
  - every {{< element >}} exists in themes/reuse-x/layouts/_shortcodes/

Hugo itself validates element parameters (file:line in the server overlay);
this script covers what Hugo cannot see. Exit 1 on any finding.

Usage:  content_lint.py [FILE ...]      (default: all of content/)
"""
import re
import subprocess
import sys
from pathlib import Path

ALLOWED_KEYS = {"title", "description", "layout", "draft", "date", "aliases", "weight",
                "translationkey", "summary", "linktitle"}
LAYOUTS = {"landing", "article", "deck"}
MAX_FRONT_MATTER = 10

SHORTCODE = re.compile(r"\{\{[<%]\s*/?\s*([\w-]+)")
SHORTCODE_SPAN = re.compile(r"\{\{[<%].*?[>%]\}\}", re.S)
FENCE = re.compile(r"^(```|~~~).*?^\1", re.S | re.M)
INLINE_CODE = re.compile(r"`[^`\n]*`")
HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)
HTML_TAG = re.compile(r"</?[a-zA-Z][\w-]*(\s[^<>]*)?/?>")
AUTOLINK = re.compile(r"<(https?://|mailto:)[^>]+>")


def root() -> Path:
    return Path(subprocess.run(["git", "rev-parse", "--show-toplevel"],
                               capture_output=True, text=True, check=True).stdout.strip())


def split_front_matter(text: str):
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            return text[4:end], text[end + 4:], 2
    if text.startswith("+++\n"):
        end = text.find("\n+++", 4)
        if end != -1:
            return text[4:end], text[end + 4:], 2
    return None, text, 0


def lint(path: Path, elements: set[str]):
    text = path.read_text()
    fm, body, _ = split_front_matter(text) if path.suffix == ".md" else (None, text, 0)
    body_offset = text.count("\n", 0, len(text) - len(body))

    if fm is not None:
        lines = [l for l in fm.splitlines() if l.strip()]
        if len(lines) > MAX_FRONT_MATTER:
            yield 1, f"front matter has {len(lines)} lines (max {MAX_FRONT_MATTER}) — move lists to data/ or elements in the body"
        for n, line in enumerate(fm.splitlines(), 2):
            m = re.match(r"^([A-Za-z_][\w-]*)\s*[:=]", line)
            if not m:
                continue  # continuation line (lists, nested values)
            key = m.group(1)
            if key.lower() not in ALLOWED_KEYS:
                yield n, f"front matter key {key!r} is not part of the content model"
            if key == "layout":
                val = line.split(":", 1)[1].strip().strip("'\"") if ":" in line else line.split("=", 1)[1].strip().strip("'\"")
                if val not in LAYOUTS:
                    yield n, f"layout {val!r} — must be one of {', '.join(sorted(LAYOUTS))}"

    # Element names.
    for m in SHORTCODE.finditer(body):
        name = m.group(1)
        if name not in elements:
            n = body_offset + body.count("\n", 0, m.start()) + 1
            yield n, f"unknown element {{{{< {name} >}}}} (see themes/reuse-x/layouts/_shortcodes/)"

    # Raw HTML: blank out code, comments and element tags first (keep newlines).
    blank = lambda m: re.sub(r"[^\n]", " ", m.group(0))  # noqa: E731
    scrubbed = FENCE.sub(blank, body)
    scrubbed = HTML_COMMENT.sub(blank, scrubbed)
    scrubbed = SHORTCODE_SPAN.sub(blank, scrubbed)
    scrubbed = INLINE_CODE.sub(blank, scrubbed)
    scrubbed = AUTOLINK.sub(blank, scrubbed)
    for m in HTML_TAG.finditer(scrubbed):
        n = body_offset + scrubbed.count("\n", 0, m.start()) + 1
        yield n, f"hand-written HTML {m.group(0)[:40]!r} — use Markdown or a content element"


def main() -> int:
    r = root()
    elements = {p.stem for p in (r / "themes/reuse-x/layouts/_shortcodes").glob("*.html")}
    files = [Path(f) for f in sys.argv[1:]] or sorted(
        [*(r / "content").rglob("*.md"), *(r / "content").rglob("examples/*.txt")])
    # Only the new content tree is held to the model; the old tree is being migrated.
    files = [f for f in files if "content/en" in str(f) or "content/da" in str(f) or sys.argv[1:]]
    total = 0
    for f in files:
        f = f if f.is_absolute() else Path.cwd() / f
        for n, msg in lint(f, elements):
            total += 1
            print(f"{f.relative_to(r) if f.is_relative_to(r) else f}:{n}: {msg}")
    print(f"content_lint: {total} finding(s) in {len(files)} file(s)", file=sys.stderr)
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
