# -*- coding: utf-8 -*-
"""Builds assets/typing.svg: phrases that type and erase themselves.

Usage:  python build_typing.py <output.svg>

Each phrase is revealed by clipping the text character by character
(clipPath with a discrete animation). textLength fixes the width of every
character, so the clip and the cursor line up with any monospace font.
"""
import sys
from xml.sax.saxutils import escape

W, H = 720, 56
FS = 22                   # font size
CW = FS * 0.6             # width of a monospace character
BASE_Y = 36

TYPE = 0.075              # seconds per character when typing
HOLD = 1.9                # pause with the full phrase
ERASE = 0.03              # seconds per character when erasing
GAP = 0.35                # pause with an empty line

# whatever comes before " · " is painted red
PHRASES = [
    "Frontend · React + TypeScript + Tailwind",
    "Backend · Node.js + NestJS + Express",
    "REST APIs · PostgreSQL · SQL",
    "Clean Architecture · code that scales",
    "Think before you code",
]

PROMPT = "> "
LONGEST = max(len(p) for p in PHRASES) + len(PROMPT)
X0 = round((W - LONGEST * CW) / 2, 1)          # the longest block is centered
TX = round(X0 + len(PROMPT) * CW, 1)            # where the phrase starts


def timeline():
    """Returns [(t, visible_chars), ...] per phrase and the total duration."""
    t, tracks = 0.0, []
    for p in PHRASES:
        n = len(p)
        pts = [(t, 0)]
        for k in range(1, n + 1):
            pts.append((t + k * TYPE, k))
        t += n * TYPE + HOLD
        for k in range(n - 1, -1, -1):
            t += ERASE
            pts.append((t, k))
        t += GAP
        tracks.append(pts)
    return tracks, t


def discrete(attr, pts, total, fmt):
    """Discrete animate from (t, value) points."""
    if pts[0][0] > 0:
        pts = [(0.0, 0)] + pts
    keys = ";".join("%.4f" % (t / total) for t, _ in pts)
    vals = ";".join(fmt(v) for _, v in pts)
    return ('<animate attributeName="%s" calcMode="discrete" dur="%.2fs" '
            'repeatCount="indefinite"\n               keyTimes="%s"\n               values="%s"/>'
            % (attr, total, keys, vals))


def phrase_text(p):
    """Text with the category in red if the phrase has one."""
    if " · " in p:
        head, tail = p.split(" · ", 1)
        return ('<tspan class="hi">%s</tspan><tspan class="lo"> · %s</tspan>'
                % (escape(head), escape(tail)))
    return '<tspan class="lo">%s</tspan>' % escape(p)


def main():
    tracks, total = timeline()
    fmt_w = lambda k: "%.1f" % (k * CW)

    clips, texts, cursor_pts = [], [], []
    for i, (p, pts) in enumerate(zip(PHRASES, tracks)):
        clips.append(
            '<clipPath id="c%d"><rect x="%s" y="0" width="0" height="%d">\n'
            '        %s\n      </rect></clipPath>'
            % (i, TX, H, discrete("width", pts, total, fmt_w)))
        texts.append(
            '<text x="%s" y="%d" textLength="%.1f" lengthAdjust="spacing" '
            'clip-path="url(#c%d)">%s</text>'
            % (TX, BASE_Y, len(p) * CW, i, phrase_text(p)))
        cursor_pts += pts

    fmt_x = lambda k: "%.1f" % (TX + k * CW)
    cursor = discrete("x", cursor_pts, total, fmt_x)

    svg = TPL.format(
        W=W, H=H, FS=FS, X0=X0, Y=BASE_Y, TX=TX, CW=round(CW - 2, 1),
        CY=BASE_Y - FS + 3, CH=FS + 2,
        CLIPS="\n    ".join(clips), TEXTS="\n    ".join(texts), CURSOR=cursor,
        LABEL=escape(" | ".join(PHRASES)))
    with open(sys.argv[1], "w", encoding="utf-8", newline="\n") as f:
        f.write(svg)


TPL = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}"
     role="img" aria-label="{LABEL}">
  <title>{LABEL}</title>
  <defs>
    <filter id="glow" x="-10%" y="-60%" width="120%" height="220%">
      <feGaussianBlur stdDeviation="2.6" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    {CLIPS}
  </defs>

  <style>
    text {{ font-family: Consolas, 'DejaVu Sans Mono', 'Courier New', monospace;
            font-size: {FS}px; }}
    .hi {{ fill: #ff4d4d; }}
    .lo {{ fill: #e8dada; }}
    .cur {{ fill: #ff2f2f; }}
    .fx {{ filter: url(#glow); }}
    @media (prefers-color-scheme: light) {{
      .hi {{ fill: #d11a1a; }}
      .lo {{ fill: #2a1c1c; }}
      .fx {{ filter: none; }}
    }}
  </style>

  <g class="fx">
    <!-- fixed prompt pulsing like the banner ember -->
    <text x="{X0}" y="{Y}" class="hi" font-weight="bold">&gt;
      <animate attributeName="opacity" values=".45;1;.45" dur="3.4s" repeatCount="indefinite"/>
    </text>

    {TEXTS}

    <!-- cursor: follows the last character and blinks -->
    <rect class="cur" x="{TX}" y="{CY}" width="{CW}" height="{CH}" rx="1" opacity=".85">
      {CURSOR}
      <animate attributeName="opacity" values=".9;.9;0;0" keyTimes="0;.5;.5;1"
               dur="0.9s" repeatCount="indefinite"/>
    </rect>
  </g>
</svg>
"""

if __name__ == "__main__":
    main()
