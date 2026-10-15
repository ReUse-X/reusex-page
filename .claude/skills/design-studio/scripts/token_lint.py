#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Povl Filip Sonne-Frederiksen
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guard the site's colour-token rule: colours come from the CSS custom
properties in themes/reuse-x/assets/css/tokens.css (vendored product tokens)
and site-tokens.css, never from literals.

Why: the site has two themes switched by data-theme on <html>. A literal
colour (or a Tailwind palette class like `bg-white` / `text-gray-600`) is the
same in both themes, so it is the usual cause of "dark text on dark
background" or "white card in dark mode" bugs. A token flips with the theme.

What it flags:
  templates (themes/reuse-x/layouts/**/*.html, layouts/**/*.html)
    - hex / rgb() / hsl() colours (in style="", <style>, SVG fill/stroke)
    - Tailwind palette colour utilities: bg-/text-/border-/from-/via-/to-/
      ring-/fill-/stroke-/divide-/outline-/shadow- + white|black|<palette>-<n>
    - var(--x) naming a token no token file defines
  component CSS (themes/reuse-x/assets/css/**, except *tokens.css)
    - colour literals OUTSIDE the token blocks (`:root { … }` and
      `[data-theme="light"] { … }` — only those define values)
    - var(--x) naming an undefined token

A line containing `token-lint: allow` is exempt (e.g. a brand/partner logo
colour or an image overlay that must be identical in both themes).

Usage:
  token_lint.py                 # whole site, from the repo root
  token_lint.py FILE ...        # just these files
  token_lint.py --summary       # counts per file only (for a baseline)
Exit status 1 if anything is flagged.
"""
import argparse
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

HEX = re.compile(r"(?<![&\w])#[0-9a-fA-F]{3,8}\b")
FUNC = re.compile(r"\b(?:rgba?|hsla?)\s*\(", re.I)
PALETTE = ("slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|"
           "teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose")
TW = re.compile(
    r"(?<![\w-])(?:[a-z]+:)*(?:bg|text|border(?:-[trblxy])?|from|via|to|ring|fill|stroke|"
    r"divide|outline|shadow|placeholder|accent|caret|decoration)-"
    rf"(?:white|black|(?:{PALETTE})-\d{{2,3}})(?:/\d+)?(?![\w-])")
VAR = re.compile(r"var\(\s*(--[\w-]+)")
DEF = re.compile(r"(--[\w-]+)\s*:")
TOKEN_BLOCK = re.compile(r"^\s*(?::root|\[data-theme=[\"']?\w+[\"']?\])\s*\{")
ALLOW = "token-lint: allow"


def root() -> Path:
    return Path(subprocess.run(["git", "rev-parse", "--show-toplevel"],
                               capture_output=True, text=True, check=True).stdout.strip())


def strip_comments(text: str) -> str:
    """Blank out /* … */ (CSS) and <!-- … --> (HTML), keeping line numbers."""
    blank = lambda m: re.sub(r"[^\n]", " ", m.group(0))  # noqa: E731
    return re.sub(r"/\*.*?\*/|<!--.*?-->", blank, text, flags=re.S)


def defined_tokens(files: list[Path]) -> set[str]:
    """Every --x: defined anywhere: main.css, plus templates that set a
    component-local property (timeline.html's --gap) or one from a content
    param (home.html's style="--hero-bg-light: …")."""
    return {t for f in files for t in DEF.findall(strip_comments(f.read_text()))}


def lint_template(path: Path, tokens: set[str]):
    for n, line in enumerate(strip_comments(path.read_text()).splitlines(), 1):
        if ALLOW in line:
            continue
        # Hugo template actions can contain '#' in strings; ignore {{ … }}.
        text = re.sub(r"\{\{.*?\}\}", "", line)
        for m in HEX.finditer(text):
            yield n, "colour", m.group(0)
        for m in FUNC.finditer(text):
            yield n, "colour", m.group(0) + "…)"
        for m in TW.finditer(text):
            yield n, "tailwind-colour", m.group(0)
        for m in VAR.finditer(text):
            if m.group(1) not in tokens:
                yield n, "unknown-token", m.group(1)


def lint_css(path: Path, tokens: set[str]):
    depth = 0
    in_tokens = False
    raw = path.read_text().splitlines()
    for n, line in enumerate(strip_comments(path.read_text()).splitlines(), 1):
        if ALLOW in raw[n - 1]:
            continue
        if depth == 0 and TOKEN_BLOCK.match(line):
            in_tokens = True
        if not in_tokens:
            for m in HEX.finditer(line):
                yield n, "colour", m.group(0)
            for m in FUNC.finditer(line):
                yield n, "colour", m.group(0) + "…)"
        for m in VAR.finditer(line):
            if m.group(1) not in tokens:
                yield n, "unknown-token", m.group(1)
        depth += line.count("{") - line.count("}")
        if depth <= 0:
            depth = 0
            in_tokens = False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*", type=Path)
    ap.add_argument("--summary", action="store_true")
    a = ap.parse_args()

    r = root()
    theme = r / "themes/reuse-x"
    token_files = sorted((theme / "assets/css").glob("*tokens.css"))
    generated = {theme / "assets/css/tailwind-theme.css"}
    css_files = sorted(p for p in (theme / "assets/css").rglob("*.css")
                       if p not in token_files and p not in generated and "generated" not in p.parts)
    templates = sorted([*theme.glob("layouts/**/*.html"), *r.glob("layouts/**/*.html")])
    tokens = defined_tokens([*token_files, *css_files, *templates])
    files = a.files or [*templates, *css_files]

    total = 0
    per_file: Counter = Counter()
    for f in files:
        f = f if f.is_absolute() else Path.cwd() / f
        if f.name.endswith("tokens.css"):
            continue  # token files define the values
        hits = lint_css(f, tokens) if f.suffix == ".css" else lint_template(f, tokens)
        rel = f.relative_to(r) if f.is_relative_to(r) else f
        for n, kind, what in hits:
            total += 1
            per_file[str(rel)] += 1
            if not a.summary:
                print(f"{rel}:{n}: {kind}: {what}")
    if a.summary:
        for f, c in per_file.most_common():
            print(f"{c:5d}  {f}")
    print(f"token_lint: {total} finding(s) in {len(per_file)} of {len(files)} file(s) scanned", file=sys.stderr)
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
