#!/usr/bin/env python3
"""Generate assets/demo.gif — animated walkthrough of one feature going from a
backlog line to a verified-red test file.

Usage: python3 assets/generate-demo.py   (requires Pillow, run from repo root)
"""
import re

from PIL import Image, ImageDraw, ImageFont

SCALE = 2  # render at 2x then downscale for crisp text
W, H = 820, 404
FONT_SIZE = 13

BG = "#11111b"
PANEL = "#1e1e2e"
BORDER = "#45475a"
TEXT = "#cdd6f4"
DIM = "#7f849c"
MAUVE = "#cba6f7"
GREEN = "#a6e3a1"
YELLOW = "#f9e2af"
PEACH = "#fab387"
BLUE = "#89b4fa"
RED = "#f38ba8"
TEAL = "#94e2d5"

KEYWORDS = {"import", "from", "def", "with", "as", "not", "in", "return"}

CONTRACT = [
    ("Partition", "Values to test", "Expected"),
    ("valid", "1, 9999, 10000", "returns, no error"),
    ("invalid above", "10001, 2**31", "TransferLimitError"),
    ("invalid below", "0, -1", "ValueError"),
    ("degenerate", 'None, "abc", 10000.5', "TypeError"),
]


def contract_rows():
    """Render the contract table with columns padded to the widest cell."""
    widths = [max(len(row[i]) for row in CONTRACT) for i in range(3)]
    out = []
    for n, row in enumerate(CONTRACT):
        line = "| " + " | ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)) + " |"
        out.append((line, DIM if n == 0 else TEXT))
        if n == 0:
            out.append(("|" + "|".join("-" * (w + 2) for w in widths) + "|", BORDER))
    return out


def load_font(size):
    for path in ("/System/Library/Fonts/Menlo.ttc", "/System/Library/Fonts/Monaco.ttf"):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


FONT = load_font(FONT_SIZE * SCALE)


def highlight(line):
    """Split a Python line into (text, color) spans. Deliberately simple."""
    spans, i = [], 0
    pattern = re.compile(
        r'(?P<str>"[^"]*")'
        r"|(?P<dec>@[\w.]+)"
        r"|(?P<num>\b\d+\b)"
        r"|(?P<word>\b\w+\b)"
    )
    for m in pattern.finditer(line):
        if m.start() > i:
            spans.append((line[i:m.start()], TEXT))
        text = m.group()
        if m.lastgroup == "str":
            color = GREEN
        elif m.lastgroup == "dec":
            color = PEACH
        elif m.lastgroup == "num":
            color = PEACH
        elif text in KEYWORDS:
            color = MAUVE
        elif text.startswith("test_"):
            color = BLUE
        else:
            color = TEXT
        spans.append((text, color))
        i = m.end()
    if i < len(line):
        spans.append((line[i:], TEXT))
    return spans


def make_frame(title, body, footer, footer_color=MAUVE, code=False):
    img = Image.new("RGB", (W * SCALE, H * SCALE), BG)
    d = ImageDraw.Draw(img)
    pad = 20 * SCALE

    d.rounded_rectangle(
        [pad // 2, pad // 2, W * SCALE - pad // 2, H * SCALE - pad // 2],
        radius=10 * SCALE, fill=PANEL, outline=BORDER, width=SCALE,
    )
    for i, c in enumerate((RED, YELLOW, GREEN)):
        d.ellipse(
            [pad + i * 22 * SCALE, pad, pad + i * 22 * SCALE + 12 * SCALE, pad + 12 * SCALE],
            fill=c,
        )
    tw = d.textlength(title, font=FONT)
    d.text((W * SCALE // 2 - tw / 2, pad - 2 * SCALE), title, font=FONT, fill=DIM)

    y = pad + 34 * SCALE
    line_h = int(FONT_SIZE * SCALE * 1.72)

    for line in body:
        text, color = line if isinstance(line, tuple) else (line, TEXT)
        if code and text.strip():
            x = pad
            for span, span_color in highlight(text):
                d.text((x, y), span, font=FONT, fill=span_color)
                x += d.textlength(span, font=FONT)
        else:
            d.text((pad, y), text, font=FONT, fill=color)
        y += line_h

    fy = H * SCALE - pad - line_h - 4 * SCALE
    d.line([pad, fy - line_h // 2, W * SCALE - pad, fy - line_h // 2], fill=BORDER, width=SCALE)
    d.text((pad, fy), footer, font=FONT, fill=footer_color)

    return img.resize((W, H), Image.LANCZOS)


frames = [
    make_frame(
        "your request",
        [
            ("❯ Cover this feature. Tests only, no implementation.", TEXT),
            "",
            ("  Transfer limit — a transfer above 10 000 € must be rejected.", DIM),
            ("  Amounts are in euros, whole numbers only.", DIM),
        ],
        "Phase 0 — pytest detected · your conventions copied · baseline green (14 passed)",
        GREEN,
    ),
    make_frame(
        "Phase 1 — clarification",
        [
            ("? Is 10 000 itself accepted, or is the limit exclusive?", YELLOW),
            ("    accepted — the limit is inclusive", DIM),
            "",
            ("? What should zero or a negative amount raise?", YELLOW),
            ("    ValueError — a different error from the limit one", DIM),
            "",
            ("? And a non-integer amount?", YELLOW),
            ("    TypeError", DIM),
        ],
        "One feature at a time · never asks about storage, framework or algorithm",
    ),
    make_frame(
        "docs/test-contracts/transfer-limit.md",
        contract_rows(),
        "Phase 2 — validate this before I write a single test   → OK ?",
        BLUE,
    ),
    make_frame(
        "tests/test_transfer_limit.py",
        [
            "import pytest",
            "",
            "from transfers.limits import TransferLimitError, check_transfer_limit",
            "",
            '@pytest.mark.parametrize("amount", [1, 9999, 10000])',
            "def test_accepts_amounts_up_to_the_limit(amount):",
            "    check_transfer_limit(amount)",
            "",
            '@pytest.mark.parametrize("amount", [10001, 2**31])',
            "def test_rejects_amounts_above_the_limit(amount):",
            "    with pytest.raises(TransferLimitError):",
            "        check_transfer_limit(amount)",
        ],
        "Phase 3 — one table per distinguishable outcome · 0 production files touched",
        code=True,
    ),
    make_frame(
        "pytest --continue-on-collection-errors",
        [
            ("ERROR tests/test_transfer_limit.py", RED),
            ("E   ModuleNotFoundError: No module named 'transfers.limits'", RED),
            "",
            ("14 passed, 1 error in 0.11s", DIM),
            "",
            ("  ↳ the missing module IS the expected failure", TEAL),
            ("  ↳ your 14 existing tests still ran — the flag keeps the suite alive", TEAL),
        ],
        "Phase 4 — verified red, and red for the right reason",
        PEACH,
    ),
    make_frame(
        "report",
        [
            ("Test files:               tests/test_transfer_limit.py", TEXT),
            ("Expected reds:            ModuleNotFoundError: No module named", TEXT),
            ("                          'transfers.limits'  (collection error)", DIM),
            ("Already implemented:      none", TEXT),
            ("Not covered:              none", TEXT),
            ("Production files touched: none", GREEN),
            ("Hand-off:                 superpowers:test-driven-development", TEXT),
        ],
        "✔ The tests are the contract. Implementing them is someone else's turn.",
        GREEN,
    ),
]

frames[0].save(
    "assets/demo.gif",
    save_all=True,
    append_images=frames[1:],
    duration=[3000, 4200, 3800, 4500, 4000, 4500],
    loop=0,
)
print("wrote assets/demo.gif")
