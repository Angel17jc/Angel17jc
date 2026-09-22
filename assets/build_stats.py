# -*- coding: utf-8 -*-
"""Genera assets/stats.svg: tarjeta de estadisticas con el estilo del banner.

Uso:  GITHUB_TOKEN=... python build_stats.py <usuario> <salida.svg>

Solo usa la libreria estandar para que el workflow no tenga que instalar
nada. Las barras se llenan una vez al cargar (fill="freeze") y despues
queda un brillo recorriendolas en bucle.
"""
import json
import os
import sys
import urllib.request
from xml.sax.saxutils import escape

W, H = 900, 250
TOP_LANGS = 5
# lenguajes que inflan el porcentaje sin decir nada del stack
EXCLUDE = {"HTML", "CSS", "SCSS", "Jupyter Notebook", "Batchfile", "Shell", "PowerShell", "Dockerfile"}
# repos que no cuentan para los lenguajes (Examenmodelado trae un venv subido)
EXCLUDE_REPOS = {"Examenmodelado", "Angel17jc"}

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      contributionCalendar { totalContributions }
    }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC) {
      totalCount
      nodes {
        name
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name } }
        }
      }
    }
  }
}
"""


def fetch(login, token):
    body = json.dumps({"query": QUERY, "variables": {"login": login}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql", data=body,
        headers={"Authorization": "bearer " + token, "User-Agent": "build_stats"})
    with urllib.request.urlopen(req) as r:
        data = json.load(r)
    if data.get("errors"):
        sys.exit("GraphQL: %s" % data["errors"])
    return data["data"]["user"]


def summarize(user):
    cc = user["contributionsCollection"]
    repos = user["repositories"]
    sizes = {}
    for repo in repos["nodes"]:
        if repo["name"] in EXCLUDE_REPOS:
            continue
        for e in repo["languages"]["edges"]:
            name = e["node"]["name"]
            if name not in EXCLUDE:
                sizes[name] = sizes.get(name, 0) + e["size"]
    total = sum(sizes.values()) or 1
    langs = sorted(sizes.items(), key=lambda kv: -kv[1])[:TOP_LANGS]
    return {
        "stats": [
            ("Contributions (last year)", cc["contributionCalendar"]["totalContributions"]),
            ("Commits", cc["totalCommitContributions"]),
            ("Pull requests", cc["totalPullRequestContributions"]),
            ("Public repos", repos["totalCount"]),
            ("Stars", sum(r["stargazerCount"] for r in repos["nodes"])),
        ],
        "langs": [(n, s * 100.0 / total) for n, s in langs],
    }


def stat_rows(stats):
    rows = []
    for i, (label, value) in enumerate(stats):
        y = 92 + i * 30
        begin = "%.2fs" % (0.15 + i * 0.12)
        rows.append(
            '<g opacity="0" transform="translate(-12 0)">\n'
            '      <animate attributeName="opacity" to="1" dur=".5s" begin="{b}" fill="freeze"/>\n'
            '      <animateTransform attributeName="transform" type="translate" to="0 0" dur=".5s"\n'
            '                        begin="{b}" fill="freeze" calcMode="spline" keyTimes="0;1"\n'
            '                        keySplines=".2 .7 .3 1"/>\n'
            '      <rect x="44" y="{ry}" width="7" height="7" fill="#ff2f2f" transform="rotate(45 47.5 {cy})"/>\n'
            '      <text x="64" y="{y}" class="lbl">{label}</text>\n'
            '      <text x="410" y="{y}" class="num" text-anchor="end">{value}</text>\n'
            '    </g>'.format(b=begin, ry=y - 9, cy=y - 5.5, y=y,
                              label=escape(label), value="{:,}".format(value)))
    return "\n    ".join(rows)


def lang_rows(langs):
    bar_w = 370
    rows = []
    top = max((p for _, p in langs), default=1)
    for i, (name, pct) in enumerate(langs):
        y = 92 + i * 30
        w = max(4.0, bar_w * pct / top)      # la barra mayor ocupa todo el ancho
        begin = "%.2fs" % (0.4 + i * 0.15)
        rows.append(
            '<text x="490" y="{y}" class="lbl">{name}</text>\n'
            '    <text x="860" y="{y}" class="pct" text-anchor="end">{pct:.1f}%</text>\n'
            '    <rect x="490" y="{by}" width="{bw}" height="6" rx="3" fill="#2a0e0e"/>\n'
            '    <rect x="490" y="{by}" width="0" height="6" rx="3" fill="url(#bar)">\n'
            '      <animate attributeName="width" to="{w:.1f}" dur="1.1s" begin="{b}" fill="freeze"\n'
            '               calcMode="spline" keyTimes="0;1" keySplines=".2 .7 .3 1"/>\n'
            '    </rect>\n'
            '    <rect x="490" y="{by}" width="0" height="6" rx="3" fill="url(#sweep)">\n'
            '      <animate attributeName="width" to="{w:.1f}" dur="1.1s" begin="{b}" fill="freeze"\n'
            '               calcMode="spline" keyTimes="0;1" keySplines=".2 .7 .3 1"/>\n'
            '    </rect>'.format(y=y, name=escape(name), pct=pct, by=y + 8, bw=bar_w, w=w, b=begin))
    return "\n    ".join(rows)


TPL = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}"
     role="img" aria-label="GitHub stats">
  <title>GitHub stats</title>
  <defs>
    <clipPath id="frame"><rect x="0" y="0" width="{W}" height="{H}" rx="16"/></clipPath>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#140606"/>
      <stop offset="1" stop-color="#050202"/>
    </linearGradient>
    <radialGradient id="ember" cx="50%" cy="50%" r="50%">
      <stop offset="0%"   stop-color="#ff2b2b" stop-opacity=".35"/>
      <stop offset="100%" stop-color="#000000" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="bar" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#7a1414"/>
      <stop offset="1" stop-color="#ff4040"/>
    </linearGradient>
    <!-- brillo que recorre las barras una vez llenas -->
    <linearGradient id="sweep" gradientUnits="userSpaceOnUse" x1="330" y1="0" x2="490" y2="0">
      <stop offset="0"   stop-color="#fff0f0" stop-opacity="0"/>
      <stop offset=".5"  stop-color="#fff0f0" stop-opacity=".55"/>
      <stop offset="1"   stop-color="#fff0f0" stop-opacity="0"/>
      <animate attributeName="x1" values="330;900" dur="3.2s" begin="1.8s" repeatCount="indefinite"/>
      <animate attributeName="x2" values="490;1060" dur="3.2s" begin="1.8s" repeatCount="indefinite"/>
    </linearGradient>
    <filter id="textGlow" x="-25%" y="-60%" width="150%" height="220%">
      <feGaussianBlur stdDeviation="2.6" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <style>
    text {{ font-family: Verdana, 'DejaVu Sans', sans-serif; }}
    .h   {{ fill: #ffffff; font-size: 15px; font-weight: bold; letter-spacing: 2.4px; }}
    .lbl {{ fill: #c9b8b8; font-size: 13px; }}
    .num {{ fill: #ffffff; font-size: 15px; font-weight: bold; }}
    .pct {{ fill: #ff8a8a; font-size: 12px; }}
  </style>

  <g clip-path="url(#frame)">
    <rect width="{W}" height="{H}" fill="url(#bg)"/>

    <!-- brasa que late detras de cada columna -->
    <ellipse cx="200" cy="140" rx="260" ry="150" fill="url(#ember)">
      <animate attributeName="opacity" values=".5;1;.5" dur="3.4s" repeatCount="indefinite"/>
    </ellipse>
    <ellipse cx="680" cy="140" rx="260" ry="150" fill="url(#ember)" opacity=".6">
      <animate attributeName="opacity" values="1;.5;1" dur="3.4s" repeatCount="indefinite"/>
    </ellipse>

    <g filter="url(#textGlow)">
      <text x="40" y="48" class="h">ACTIVITY</text>
      <text x="490" y="48" class="h">TOP LANGUAGES</text>
    </g>
    <rect x="40" y="60" width="0" height="2" fill="#ff2f2f">
      <animate attributeName="width" values="0;370;370;0" keyTimes="0;.35;.8;1"
               dur="6s" repeatCount="indefinite"/>
    </rect>
    <rect x="490" y="60" width="0" height="2" fill="#ff2f2f">
      <animate attributeName="width" values="0;370;370;0" keyTimes="0;.35;.8;1"
               dur="6s" begin="-3s" repeatCount="indefinite"/>
    </rect>

    <!-- separador vertical -->
    <rect x="449.5" y="40" width="1" height="{SEP}" fill="#ff2f2f" opacity=".25"/>

    {STATS}

    {LANGS}

    <!-- el marco se enciende con la descarga de 12s del banner -->
    <rect width="{W}" height="{H}" fill="#ff5252" opacity="0">
      <animate attributeName="opacity" values="0;.08;0;0" keyTimes="0;.012;.07;1"
               dur="12s" repeatCount="indefinite"/>
    </rect>
    <rect width="{W}" height="{H}" fill="none" stroke="#7a1414" stroke-width="2" rx="16">
      <animate attributeName="stroke" values="#7a1414;#ff4040;#7a1414;#7a1414"
               keyTimes="0;.015;.12;1" dur="12s" repeatCount="indefinite"/>
    </rect>
  </g>
</svg>
"""


def main():
    login, out = sys.argv[1], sys.argv[2]
    token = os.environ.get("GITHUB_TOKEN") or sys.exit("falta GITHUB_TOKEN")
    data = summarize(fetch(login, token))
    svg = TPL.format(W=W, H=H, SEP=H - 80,
                     STATS=stat_rows(data["stats"]), LANGS=lang_rows(data["langs"]))
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(svg)
    print("stats:", data["stats"])
    print("langs:", ["%s %.1f%%" % l for l in data["langs"]])


if __name__ == "__main__":
    main()
