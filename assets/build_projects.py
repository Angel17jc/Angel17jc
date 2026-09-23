# -*- coding: utf-8 -*-
"""Builds the featured project cards (assets/project-*.svg).

Usage:  python build_projects.py <output_dir>

Each card is a standalone SVG that the README wraps in a link to the repo.
Edit PROJECTS to change the text; descriptions are split into lines by hand
because SVG text does not wrap.
"""
import sys
from xml.sax.saxutils import escape

W, H = 440, 230

PROJECTS = [
    {
        "file": "project-asistcontrol.svg",
        "name": "AsistControl",
        "tag": "FULL STACK",
        "lines": [
            "Attendance and workday platform that syncs",
            "with biometric devices over LAN. Vendor-agnostic",
            "adapters, configurable rules, payroll reports.",
        ],
        "stack": ["NestJS", "React", "PostgreSQL", "Prisma", "Docker"],
        "delay": 0,
    },
    {
        "file": "project-inventario.svg",
        "name": "Inventario",
        "tag": "LIVE DEMO",
        "lines": [
            "Multi-tenant inventory and store credit app for",
            "liquor stores: purchases, multi-product sales",
            "and credit accounts, each store fully isolated.",
        ],
        "stack": ["React", "Express", "Drizzle", "PostgreSQL", "Vercel"],
        "delay": -0.9,
    },
    {
        "file": "project-enertech.svg",
        "name": "Enertech",
        "tag": "WCAG 2.2 AA",
        "lines": [
            "Energy consumption tracker with savings goals,",
            "cost calculation and personalized tips. Bilingual,",
            "keyboard and screen reader friendly.",
        ],
        "stack": ["React", "TypeScript", "Supabase", "Recharts", "Tailwind"],
        "delay": -1.8,
    },
    {
        "file": "project-splitfair.svg",
        "name": "SplitFair",
        "tag": "FULL STACK",
        "lines": [
            "Shared expenses for roommates and trips:",
            "automatic balances, debts simplified to the",
            "fewest payments and analytics computed in SQL.",
        ],
        "stack": ["Java 21", "Spring Boot", "React", "PostgreSQL", "Docker"],
        "delay": -2.7,
    },
]

CHAR_W = 6.9          # average width of an 11px Verdana character
CHIP_PAD = 9
CHIP_GAP = 6


def chips(stack):
    out, x = [], 26
    for i, name in enumerate(stack):
        w = round(len(name) * CHAR_W + CHIP_PAD * 2)
        # visible by default: the animation only adds the entrance, so the
        # chips still show up where SMIL does not run
        start = 0.3 + i * 0.1
        dur = start + 0.45
        out.append(
            '<g>\n'
            '      <animate attributeName="opacity" values="0;0;1" keyTimes="0;{k:.3f};1"'
            ' dur="{d:.2f}s" fill="freeze"/>\n'
            '      <rect x="{x}" y="160" width="{w}" height="22" rx="11" fill="#1c0808" stroke="#7a1414"/>\n'
            '      <text x="{tx}" y="175" text-anchor="middle" class="chip">{n}</text>\n'
            '    </g>'.format(k=start / dur, d=dur, x=x, w=w, tx=x + w / 2.0, n=escape(name)))
        x += w + CHIP_GAP
    return "\n    ".join(out)


def build(p):
    desc = "\n    ".join(
        '<text x="26" y="%d" class="desc">%s</text>' % (92 + i * 20, escape(line))
        for i, line in enumerate(p["lines"]))
    tag_w = round(len(p["tag"]) * 6.4 + 18)
    return TPL.format(
        W=W, H=H, W1=W - 2, H1=H - 2, CTA_X=W - 44, ARROW_X=W - 36,
        NAME=escape(p["name"]), TAG=escape(p["tag"]),
        TAG_X=W - 24 - tag_w, TAG_W=tag_w, TAG_TX=W - 24 - tag_w / 2.0,
        DESC=desc, CHIPS=chips(p["stack"]), DELAY=p["delay"],
        LABEL=escape("%s - %s" % (p["name"], " ".join(p["lines"]))))


TPL = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}"
     role="img" aria-label="{LABEL}">
  <title>{NAME}</title>
  <defs>
    <clipPath id="frame"><rect x="0" y="0" width="{W}" height="{H}" rx="14"/></clipPath>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#160707"/>
      <stop offset="1" stop-color="#060202"/>
    </linearGradient>
    <radialGradient id="ember" cx="50%" cy="50%" r="50%">
      <stop offset="0%"   stop-color="#ff2b2b" stop-opacity=".4"/>
      <stop offset="100%" stop-color="#000000" stop-opacity="0"/>
    </radialGradient>
    <!-- shine sweep over the project name, same as the name -->
    <linearGradient id="shine" gradientUnits="userSpaceOnUse" x1="-260" y1="0" x2="-60" y2="0">
      <stop offset="0"    stop-color="#ffffff"/>
      <stop offset="0.42" stop-color="#ffffff"/>
      <stop offset="0.5"  stop-color="#ff7a7a"/>
      <stop offset="0.58" stop-color="#ffffff"/>
      <stop offset="1"    stop-color="#ffffff"/>
      <animate attributeName="x1" from="-260" to="{W}" dur="4.5s" begin="{DELAY}s" repeatCount="indefinite"/>
      <animate attributeName="x2" from="-60" to="640" dur="4.5s" begin="{DELAY}s" repeatCount="indefinite"/>
    </linearGradient>
    <filter id="glow" x="-20%" y="-60%" width="140%" height="220%">
      <feGaussianBlur stdDeviation="2.6" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <style>
    text  {{ font-family: Verdana, 'DejaVu Sans', sans-serif; }}
    .name {{ font-size: 21px; font-weight: bold; letter-spacing: 1px; }}
    .desc {{ fill: #c9b8b8; font-size: 12.5px; }}
    .chip {{ fill: #ff8a8a; font-size: 11px; }}
    .tag  {{ fill: #ff6b6b; font-size: 10px; font-weight: bold; letter-spacing: 1px; }}
    .cta  {{ fill: #e8dada; font-size: 11.5px; font-weight: bold; letter-spacing: 1px; }}
  </style>

  <g clip-path="url(#frame)">
    <rect width="{W}" height="{H}" fill="url(#bg)"/>

    <!-- ember pulsing in the corner -->
    <ellipse cx="{W}" cy="0" rx="240" ry="170" fill="url(#ember)">
      <animate attributeName="opacity" values=".45;1;.45" dur="3.4s" begin="{DELAY}s" repeatCount="indefinite"/>
    </ellipse>

    <!-- diamond + name -->
    <g transform="translate(33 47) rotate(45)">
      <rect x="-5" y="-5" width="10" height="10" fill="#ff2f2f" filter="url(#glow)">
        <animateTransform attributeName="transform" type="scale"
                          values="1;1.2;1" dur="3.4s" begin="{DELAY}s" repeatCount="indefinite"/>
      </rect>
    </g>
    <text x="50" y="55" class="name" fill="url(#shine)" filter="url(#glow)">{NAME}</text>

    <!-- tag in the top right corner -->
    <rect x="{TAG_X}" y="36" width="{TAG_W}" height="20" rx="4" fill="none" stroke="#ff2f2f" stroke-opacity=".6"/>
    <text x="{TAG_TX}" y="50" text-anchor="middle" class="tag">{TAG}</text>

    <!-- underline that draws in and out -->
    <rect x="26" y="68" width="0" height="2" fill="#ff2f2f">
      <animate attributeName="width" values="0;150;150;0" keyTimes="0;.35;.8;1"
               dur="6s" begin="{DELAY}s" repeatCount="indefinite"/>
    </rect>

    {DESC}

    <!-- tech chips come in one by one -->
    {CHIPS}

    <!-- call to action with an arrow nudging outwards -->
    <text x="{CTA_X}" y="210" text-anchor="end" class="cta">VIEW REPO</text>
    <path d="M{ARROW_X} 201 l5 5 l-5 5" fill="none" stroke="#ff4d4d" stroke-width="2"
          stroke-linecap="round" stroke-linejoin="round">
      <animateTransform attributeName="transform" type="translate"
                        values="0,0; 4,0; 0,0" dur="1.6s"
                        calcMode="spline" keyTimes="0;0.5;1"
                        keySplines=".45 0 .55 1;.45 0 .55 1" repeatCount="indefinite"/>
    </path>

    <!-- the frame lights up with the banner 12s surge -->
    <rect x="1" y="1" width="{W1}" height="{H1}" rx="13" fill="none" stroke="#5a1414" stroke-width="1.5">
      <animate attributeName="stroke" values="#5a1414;#ff4040;#5a1414;#5a1414"
               keyTimes="0;.015;.12;1" dur="12s" repeatCount="indefinite"/>
    </rect>

    <!-- light running along the border -->
    <rect x="1" y="1" width="{W1}" height="{H1}" rx="13" fill="none" stroke="#ff4d4d"
          stroke-width="2" pathLength="100" stroke-dasharray="12 88" stroke-linecap="round"
          filter="url(#glow)">
      <animate attributeName="stroke-dashoffset" from="0" to="-100" dur="6s"
               begin="{DELAY}s" repeatCount="indefinite"/>
    </rect>
  </g>
</svg>
"""


def main():
    out_dir = sys.argv[1]
    for p in PROJECTS:
        svg = build(p)
        with open("%s/%s" % (out_dir, p["file"]), "w", encoding="utf-8", newline="\n") as f:
            f.write(svg)
        print(p["file"])


if __name__ == "__main__":
    main()
