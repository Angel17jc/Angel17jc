# -*- coding: utf-8 -*-
"""Builds assets/stats.svg: stats card in the banner style.

Usage:  GITHUB_TOKEN=... python build_stats.py <user> <output.svg>

Uses only the standard library so the workflow does not need to install
anything. The bars fill once on load (fill="freeze") and then a shine
keeps running over them in a loop. Everything is visible by default, so the
card still reads fine where SMIL does not run.

Streaks are computed from the full contribution calendar, one year at a
time since the account was created.
"""
import datetime
import json
import os
import sys
import urllib.request
from xml.sax.saxutils import escape

W, H = 900, 350
TOP_LANGS = 5
# languages that inflate the percentage without saying anything about the stack
EXCLUDE = {"HTML", "CSS", "SCSS", "Jupyter Notebook", "Batchfile", "Shell", "PowerShell", "Dockerfile"}
# repos excluded from languages (Examenmodelado has a committed venv)
EXCLUDE_REPOS = {"Examenmodelado", "Angel17jc"}

QUERY = """
query($login: String!) {
  user(login: $login) {
    createdAt
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


def graphql(query, variables, token):
    body = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql", data=body,
        headers={"Authorization": "bearer " + token, "User-Agent": "build_stats"})
    with urllib.request.urlopen(req) as r:
        data = json.load(r)
    if data.get("errors"):
        sys.exit("GraphQL: %s" % data["errors"])
    return data["data"]["user"]


def fetch_days(login, token, since_year):
    """Returns {date: count} for every day since since_year.

    contributionsCollection covers at most one year, so each year goes in
    its own aliased field of a single query.
    """
    today = datetime.date.today()
    fields = []
    for year in range(since_year, today.year + 1):
        fields.append(
            'y%d: contributionsCollection(from: "%d-01-01T00:00:00Z", to: "%d-12-31T23:59:59Z") '
            '{ contributionCalendar { weeks { contributionDays { date contributionCount } } } }'
            % (year, year, year))
    query = "query($login: String!) { user(login: $login) { %s } }" % " ".join(fields)
    user = graphql(query, {"login": login}, token)
    days = {}
    for coll in user.values():
        for week in coll["contributionCalendar"]["weeks"]:
            for d in week["contributionDays"]:
                day = datetime.date.fromisoformat(d["date"])
                if day <= today:
                    days[day] = d["contributionCount"]
    return days


def streaks(days):
    """Current streak, longest streak and best single day.

    The current streak may still be alive if today has no contributions
    yet, so it is counted from yesterday in that case.
    """
    if not days:
        return 0, 0, 0
    last = max(days)
    day = last if days[last] else last - datetime.timedelta(days=1)
    current = 0
    while days.get(day, 0) > 0:
        current += 1
        day -= datetime.timedelta(days=1)

    longest = run = 0
    for day in sorted(days):
        run = run + 1 if days[day] else 0
        longest = max(longest, run)
    return current, longest, max(days.values())


def summarize(user, days):
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
        "streaks": streaks(days),
    }


def stat_rows(stats):
    rows = []
    for i, (label, value) in enumerate(stats):
        y = 92 + i * 30
        start = 0.15 + i * 0.12
        dur = start + 0.5
        rows.append(
            '<g>\n'
            '      <animate attributeName="opacity" values="0;0;1" keyTimes="0;{k:.3f};1"'
            ' dur="{d:.2f}s" fill="freeze"/>\n'
            '      <animateTransform attributeName="transform" type="translate"'
            ' values="-12 0;-12 0;0 0" keyTimes="0;{k:.3f};1"\n'
            '                        dur="{d:.2f}s" fill="freeze" calcMode="spline"'
            ' keySplines="0 0 1 1;.2 .7 .3 1"/>\n'
            '      <rect x="44" y="{ry}" width="7" height="7" fill="#ff2f2f" transform="rotate(45 47.5 {cy})"/>\n'
            '      <text x="64" y="{y}" class="lbl">{label}</text>\n'
            '      <text x="410" y="{y}" class="num" text-anchor="end">{value}</text>\n'
            '    </g>'.format(k=start / dur, d=dur, ry=y - 9, cy=y - 5.5, y=y,
                              label=escape(label), value="{:,}".format(value)))
    return "\n    ".join(rows)


def lang_rows(langs):
    bar_w = 370
    rows = []
    top = max((p for _, p in langs), default=1)
    for i, (name, pct) in enumerate(langs):
        y = 92 + i * 30
        w = max(4.0, bar_w * pct / top)      # the largest bar takes the full width
        start = 0.4 + i * 0.15
        dur = start + 1.1
        rows.append(
            '<text x="490" y="{y}" class="lbl">{name}</text>\n'
            '    <text x="860" y="{y}" class="pct" text-anchor="end">{pct:.1f}%</text>\n'
            '    <rect x="490" y="{by}" width="{bw}" height="6" rx="3" fill="#2a0e0e"/>\n'
            '    <rect x="490" y="{by}" width="{w:.1f}" height="6" rx="3" fill="url(#bar)">\n'
            '      <animate attributeName="width" values="0;0;{w:.1f}" keyTimes="0;{k:.3f};1"'
            ' dur="{d:.2f}s" fill="freeze"\n'
            '               calcMode="spline" keySplines="0 0 1 1;.2 .7 .3 1"/>\n'
            '    </rect>\n'
            '    <rect x="490" y="{by}" width="{w:.1f}" height="6" rx="3" fill="url(#sweep)">\n'
            '      <animate attributeName="width" values="0;0;{w:.1f}" keyTimes="0;{k:.3f};1"'
            ' dur="{d:.2f}s" fill="freeze"\n'
            '               calcMode="spline" keySplines="0 0 1 1;.2 .7 .3 1"/>\n'
            '    </rect>'.format(y=y, name=escape(name), pct=pct, by=y + 8, bw=bar_w, w=w,
                              k=start / dur, d=dur))
    return "\n    ".join(rows)


def streak_band(current, longest, best):
    """Bottom band: three big numbers, the current streak with a flame."""
    cols = [
        (150, current, "CURRENT STREAK", "days" if current != 1 else "day"),
        (450, longest, "LONGEST STREAK", "days" if longest != 1 else "day"),
        (750, best, "MOST IN A DAY", "contributions"),
    ]
    out = []
    for i, (cx, value, label, unit) in enumerate(cols):
        start = 0.9 + i * 0.15
        dur = start + 0.6
        out.append(
            '<g>\n'
            '      <animate attributeName="opacity" values="0;0;1" keyTimes="0;{k:.3f};1"'
            ' dur="{d:.2f}s" fill="freeze"/>\n'
            '      <text x="{cx}" y="292" class="big" text-anchor="middle"'
            ' filter="url(#textGlow)">{v}</text>\n'
            '      <text x="{cx}" y="312" class="unit" text-anchor="middle">{unit}</text>\n'
            '      <text x="{cx}" y="332" class="cap" text-anchor="middle">{label}</text>\n'
            '    </g>'.format(k=start / dur, d=dur, cx=cx, v="{:,}".format(value),
                             unit=unit, label=label))
    return "\n    ".join(out)


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
    <!-- shine running over the bars once filled -->
    <linearGradient id="sweep" gradientUnits="userSpaceOnUse" x1="330" y1="0" x2="490" y2="0">
      <stop offset="0"   stop-color="#fff0f0" stop-opacity="0"/>
      <stop offset=".5"  stop-color="#fff0f0" stop-opacity=".55"/>
      <stop offset="1"   stop-color="#fff0f0" stop-opacity="0"/>
      <animate attributeName="x1" values="330;900" dur="3.2s" begin="1.8s" repeatCount="indefinite"/>
      <animate attributeName="x2" values="490;1060" dur="3.2s" begin="1.8s" repeatCount="indefinite"/>
    </linearGradient>
    <linearGradient id="split" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0"  stop-color="#ff2f2f" stop-opacity="0"/>
      <stop offset=".5" stop-color="#ff2f2f" stop-opacity=".45"/>
      <stop offset="1"  stop-color="#ff2f2f" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="flame" x1="0" y1="1" x2="0" y2="0">
      <stop offset="0" stop-color="#ff2f2f"/>
      <stop offset="1" stop-color="#ffb08a"/>
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
    .big {{ fill: #ffffff; font-size: 30px; font-weight: bold; }}
    .unit {{ fill: #ff8a8a; font-size: 11px; }}
    .cap {{ fill: #c9b8b8; font-size: 11px; font-weight: bold; letter-spacing: 1.6px; }}
  </style>

  <g clip-path="url(#frame)">
    <rect width="{W}" height="{H}" fill="url(#bg)"/>

    <!-- ember pulsing behind each column -->
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

    <!-- vertical divider -->
    <rect x="449.5" y="40" width="1" height="{SEP}" fill="#ff2f2f" opacity=".25"/>

    {STATS}

    {LANGS}

    <!-- streaks: a faint line splits them from the columns above -->
    <rect x="40" y="244" width="820" height="1" fill="url(#split)"/>
    <rect x="299.5" y="262" width="1" height="72" fill="#ff2f2f" opacity=".2"/>
    <rect x="599.5" y="262" width="1" height="72" fill="#ff2f2f" opacity=".2"/>

    <!-- flame next to the current streak, flickering -->
    <g transform="translate({FLAME_X} 281)">
      <path d="M0 -15 C7 -6 11 1 7 9 C5 13 -5 13 -7 9 C-10 2 -5 -3 0 -15 Z" fill="url(#flame)"
            filter="url(#textGlow)">
        <animateTransform attributeName="transform" type="scale"
                          values="1 1;.94 1.08;1.04 .96;1 1" dur="1.3s" repeatCount="indefinite"/>
      </path>
      <path d="M0 -3 C3 1 4 4 2 8 C1 10 -1 10 -2 8 C-4 5 -2 2 0 -3 Z" fill="#fff0e0" opacity=".85">
        <animate attributeName="opacity" values=".85;.5;.9;.85" dur=".9s" repeatCount="indefinite"/>
      </path>
    </g>

    {STREAKS}

    <!-- the frame lights up with the banner 12s surge -->
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
    token = os.environ.get("GITHUB_TOKEN") or sys.exit("missing GITHUB_TOKEN")
    user = graphql(QUERY, {"login": login}, token)
    days = fetch_days(login, token, int(user["createdAt"][:4]))
    data = summarize(user, days)
    # the flame sits just left of the current streak number
    flame_x = 150 - 10 * len("{:,}".format(data["streaks"][0])) - 26
    svg = TPL.format(W=W, H=H, SEP=170, FLAME_X=flame_x,
                     STATS=stat_rows(data["stats"]), LANGS=lang_rows(data["langs"]),
                     STREAKS=streak_band(*data["streaks"]))
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(svg)
    print("stats:", data["stats"])
    print("langs:", ["%s %.1f%%" % l for l in data["langs"]])
    print("streaks (current, longest, best day):", data["streaks"])


if __name__ == "__main__":
    main()
