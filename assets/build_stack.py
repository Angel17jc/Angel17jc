# -*- coding: utf-8 -*-
"""Builds assets/stack.svg: the tech stack as one animated card.

Usage:  python build_stack.py <output.svg>

Icons come from skillicons.dev and are embedded as data URIs, because
GitHub (camo) blocks external references inside an SVG. Tools without an
icon are drawn as chips. Every item is visible by default; the cascade
only animates its entrance.
"""
import base64
import sys
import urllib.request
from xml.sax.saxutils import escape

W = 900
ROW_H, ROW_GAP, TOP = 62, 10, 28
ICON, ICON_STEP = 44, 54
ITEMS_X = 206

# (label, skillicons ids, chips for tools without an icon)
ROWS = [
    ("FRONTEND", ["ts", "react", "nextjs", "tailwind", "vite"], []),
    ("BACKEND", ["nodejs", "nestjs", "express", "python", "java", "spring"], []),
    ("APIS", ["graphql"], ["REST", "WebSockets"]),
    ("DATA", ["postgres", "supabase", "firebase"], ["TypeORM", "Prisma"]),
    ("DEVOPS", ["docker", "git", "githubactions", "linux"], []),
    ("AUTH", [], ["JWT", "Passport.js"]),
    ("ALSO USED", ["kotlin", "angular", "mongodb", "mysql", "azure"], []),
]


def icon_uri(name):
    req = urllib.request.Request(
        "https://skillicons.dev/icons?i=%s&theme=dark" % name,
        headers={"User-Agent": "build_stack"})
    with urllib.request.urlopen(req) as r:
        svg = r.read()
    return "data:image/svg+xml;base64," + base64.b64encode(svg).decode()


def entrance(j):
    """Opacity + small rise, delayed by the item's position in the cascade."""
    start = 0.2 + j * 0.05
    dur = start + 0.45
    k = start / dur
    return ('<animate attributeName="opacity" values="0;0;1" keyTimes="0;%.3f;1"'
            ' dur="%.2fs" fill="freeze"/>\n'
            '        <animateTransform attributeName="transform" type="translate"'
            ' values="0 8;0 8;0 0" keyTimes="0;%.3f;1" dur="%.2fs" fill="freeze"'
            ' calcMode="spline" keySplines="0 0 1 1;.2 .7 .3 1"/>' % (k, dur, k, dur))


def rows_markup():
    out, j = [], 0
    for i, (label, icons, chips) in enumerate(ROWS):
        y0 = TOP + i * (ROW_H + ROW_GAP)
        cy = y0 + ROW_H / 2.0
        items = []
        x = ITEMS_X
        for name in icons:
            items.append(
                '<g>\n        %s\n'
                '        <image x="%d" y="%.1f" width="%d" height="%d" xlink:href="%s"/>\n'
                '      </g>' % (entrance(j), x, cy - ICON / 2.0, ICON, ICON, icon_uri(name)))
            x += ICON_STEP
            j += 1
        for chip in chips:
            w = round(len(chip) * 7.6 + 26)
            items.append(
                '<g>\n        %s\n'
                '        <rect x="%d" y="%.1f" width="%d" height="30" rx="15" fill="#1c0808"'
                ' stroke="#7a1414"/>\n'
                '        <text x="%.1f" y="%.1f" text-anchor="middle" class="chip">%s</text>\n'
                '      </g>' % (entrance(j), x, cy - 15, w, x + w / 2.0, cy + 4.5, escape(chip)))
            x += w + 10
            j += 1
        out.append(ROW.format(
            y0=y0, cy=cy, ty=cy + 5, h=ROW_H, rw=W - 60, dy=cy - 4,
            label=escape(label), delay=-1.1 * i, items="\n      ".join(items)))
    return "\n\n    ".join(out)


ROW = """<g>
      <!-- row frame with a light running along its border -->
      <rect x="30" y="{y0}" width="{rw}" height="{h}" rx="12" fill="#140606" fill-opacity=".85"
            stroke="#3a0d0d"/>
      <rect x="30" y="{y0}" width="{rw}" height="{h}" rx="12" fill="none" stroke="#ff4d4d"
            stroke-width="1.5" pathLength="100" stroke-dasharray="8 92" stroke-linecap="round"
            opacity=".8" filter="url(#glow)">
        <animate attributeName="stroke-dashoffset" from="0" to="-100" dur="9s"
                 begin="{delay:.1f}s" repeatCount="indefinite"/>
      </rect>
      <rect x="{lx}" y="{dy}" width="8" height="8" fill="#ff2f2f"
            transform="rotate(45 {dcx} {cy})">
        <animate attributeName="opacity" values=".55;1;.55" dur="3.4s"
                 begin="{delay:.1f}s" repeatCount="indefinite"/>
      </rect>
      <text x="72" y="{ty}" class="lbl">{label}</text>
      {items}
    </g>""".replace("{lx}", "48").replace("{dcx}", "52")

TPL = """<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Tech stack">
  <title>Tech stack</title>
  <defs>
    <clipPath id="frame"><rect x="0" y="0" width="{W}" height="{H}" rx="16"/></clipPath>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#140606"/>
      <stop offset="1" stop-color="#050202"/>
    </linearGradient>
    <radialGradient id="ember" cx="50%" cy="50%" r="50%">
      <stop offset="0%"   stop-color="#ff2b2b" stop-opacity=".3"/>
      <stop offset="100%" stop-color="#000000" stop-opacity="0"/>
    </radialGradient>
    <filter id="glow" x="-10%" y="-60%" width="120%" height="220%">
      <feGaussianBlur stdDeviation="2.2" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <style>
    text  {{ font-family: Verdana, 'DejaVu Sans', sans-serif; }}
    .lbl  {{ fill: #ffffff; font-size: 13px; font-weight: bold; letter-spacing: 2px; }}
    .chip {{ fill: #ff8a8a; font-size: 12.5px; font-weight: bold; }}
  </style>

  <g clip-path="url(#frame)">
    <rect width="{W}" height="{H}" fill="url(#bg)"/>

    <!-- ember pulsing behind the card -->
    <ellipse cx="{CX}" cy="{CY}" rx="520" ry="{RY}" fill="url(#ember)">
      <animate attributeName="opacity" values=".5;1;.5" dur="3.4s" repeatCount="indefinite"/>
    </ellipse>

    {ROWS}

    <!-- the frame lights up with the banner 12s surge -->
    <rect width="{W}" height="{H}" fill="none" stroke="#7a1414" stroke-width="2" rx="16">
      <animate attributeName="stroke" values="#7a1414;#ff4040;#7a1414;#7a1414"
               keyTimes="0;.015;.12;1" dur="12s" repeatCount="indefinite"/>
    </rect>
  </g>
</svg>
"""


def main():
    h = TOP * 2 + len(ROWS) * (ROW_H + ROW_GAP) - ROW_GAP
    svg = TPL.format(W=W, H=h, CX=W // 2, CY=h // 2, RY=h // 2 + 60, ROWS=rows_markup())
    with open(sys.argv[1], "w", encoding="utf-8", newline="\n") as f:
        f.write(svg)
    print("written %s  (%.0f KB)" % (sys.argv[1], len(svg.encode("utf-8")) / 1024.0))


if __name__ == "__main__":
    main()
