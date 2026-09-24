# -*- coding: utf-8 -*-
"""Builds assets/banner.svg: animated banner with a pseudo-3D effect.

Usage:  python build_banner.py <background.png> <output.svg>
        (the current banner: python build_banner.py LIBE.jpg banner.svg)

The background is embedded as a data URI because GitHub (camo) blocks
external references inside an SVG. The portrait is a five-leaf black clover
drawn as vectors in a manga ink style. The animation uses SMIL, which is what
already works in the README (readme-typing-svg).
"""
import base64
import io
import math
import random
import sys

from PIL import Image, ImageFilter

W, H = 1000, 320          # banner canvas
FACE_R = 104              # radius of the circular portrait
FACE_CX, FACE_CY = 208, 160
SURGE = 12.0              # how often (seconds) the surge fires


def _b64(img, fmt="JPEG", **kw):
    buf = io.BytesIO()
    img.save(buf, fmt, **kw)
    mime = "jpeg" if fmt == "JPEG" else fmt.lower()
    return "data:image/%s;base64,%s" % (mime, base64.b64encode(buf.getvalue()).decode())


def build_bg(path):
    """Background: landscape crop, darkened and slightly blurred (adds depth)."""
    im = Image.open(path).convert("RGB")
    # center crop with the banner ratio, 15% wider for the parallax
    tw, th = int(W * 1.15), int(H * 1.15)
    scale = max(tw / im.width, th / im.height)
    im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.LANCZOS)
    left = (im.width - tw) // 2
    top = int((im.height - th) * BG_FOCUS_Y)    # eye/fangs band
    im = im.crop((left, top, left + tw, top + th))
    im = im.filter(ImageFilter.GaussianBlur(1.6))
    im = Image.eval(im, lambda v: int(v * BG_DARKEN))   # so it does not fight with the text
    return _b64(im, "JPEG", quality=78, optimize=True)


BG_FOCUS_Y = 0.62         # which vertical band of the background is cropped, 0..1
BG_DARKEN = 0.50          # how much the background is darkened
CLOVER_SIZE = 92          # clover radius, just inside the portrait ring

# one heart-shaped leaf in a 93-unit box: tip near the center, lobes towards -y
LEAF = [
    ((0, -8), (-10, -18), (-38, -38), (-36, -63)),
    ((-36, -63), (-34, -87), (-10, -93), (0, -76)),
    ((0, -76), (10, -93), (34, -87), (36, -63)),
    ((36, -63), (38, -38), (10, -18), (0, -8)),
]


def _bez(seg, t):
    """Point at t on a cubic Bezier segment."""
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = seg
    u = 1 - t
    return (u ** 3 * x0 + 3 * u * u * t * x1 + 3 * u * t * t * x2 + t ** 3 * x3,
            u ** 3 * y0 + 3 * u * u * t * y1 + 3 * u * t * t * y2 + t ** 3 * y3)


def _leaf_path(k):
    d = "M%.1f %.1f " % (LEAF[0][0][0] * k, LEAF[0][0][1] * k)
    for seg in LEAF:
        d += "C%.1f %.1f %.1f %.1f %.1f %.1f " % tuple(v * k for pt in seg[1:] for v in pt)
    return d + "Z"


def _hatches(k, rng):
    """Manga ink strokes: short dashes along the lobes pointing into the leaf,
    plus an inner broken heart outline, like the reference sticker."""
    out = []
    inner = (0, -55 * k)
    for seg_i, n in ((0, 8), (1, 9), (2, 9), (3, 8)):
        for j in range(n):
            t = (j + 0.5 + rng.uniform(-.25, .25)) / n
            if seg_i == 0 and t < .5 or seg_i == 3 and t > .5:
                continue            # keep the stems clean
            x, y = _bez(LEAF[seg_i], t)
            x, y = x * k, y * k
            dx, dy = inner[0] - x, inner[1] - y
            ln = math.hypot(dx, dy)
            a, b = rng.uniform(2.5, 4.5), rng.uniform(5, 9)
            out.append("M%.1f %.1f L%.1f %.1f" % (
                x + dx / ln * a, y + dy / ln * a, x + dx / ln * (a + b), y + dy / ln * (a + b)))
    for seg_i in (1, 2):
        for j in range(7):
            x, y = _bez(LEAF[seg_i], (j + .5) / 7)
            x, y = x * k * .6, (y * .6 - 18) * k
            dx, dy = inner[0] - x, inner[1] - y
            ln = math.hypot(dx, dy) or 1
            b = rng.uniform(4, 7)
            out.append("M%.1f %.1f L%.1f %.1f" % (x, y, x + dx / ln * b, y + dy / ln * b))
    return " ".join(out)


def clover_markup():
    """Five leaves at 72 degrees joined by a solid center, and their hatching."""
    rng = random.Random(5)
    k = CLOVER_SIZE / 93.0
    leaf = _leaf_path(k)
    leaves = ['<path d="%s" transform="rotate(%d)"/>' % (leaf, i * 72) for i in range(5)]
    leaves.append('<circle r="%.1f"/>' % (15 * k))
    marks = ['<path d="%s" transform="rotate(%d)"/>' % (_hatches(k, rng), i * 72)
             for i in range(5)]
    return "\n            ".join(leaves), "\n            ".join(marks)


SVG = u"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img"
     aria-label="Angel Conforme - animated banner">
  <title>Angel Conforme</title>
  <defs>
    <clipPath id="frame"><rect x="0" y="0" width="{W}" height="{H}" rx="16"/></clipPath>

    <radialGradient id="emberGlow" cx="50%" cy="50%" r="50%">
      <stop offset="0%"   stop-color="#ff2b2b" stop-opacity=".85"/>
      <stop offset="45%"  stop-color="#c40d0d" stop-opacity=".35"/>
      <stop offset="100%" stop-color="#000000" stop-opacity="0"/>
    </radialGradient>

    <linearGradient id="fade" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%"   stop-color="#050202" stop-opacity="0"/>
      <stop offset="55%"  stop-color="#050202" stop-opacity=".72"/>
      <stop offset="100%" stop-color="#050202" stop-opacity=".93"/>
    </linearGradient>

    <radialGradient id="vignette" cx="50%" cy="50%" r="72%">
      <stop offset="55%"  stop-color="#000" stop-opacity="0"/>
      <stop offset="100%" stop-color="#000" stop-opacity=".8"/>
    </radialGradient>

    <!-- core glow: white to red, fading out -->
    <radialGradient id="eyeGlow">
      <stop offset="0%"   stop-color="#fff0f0" stop-opacity=".95"/>
      <stop offset="28%"  stop-color="#ff3b3b" stop-opacity=".75"/>
      <stop offset="100%" stop-color="#ff0000" stop-opacity="0"/>
    </radialGradient>

    <!-- shine sweep over the title, same as the name -->
    <linearGradient id="titleShine" gradientUnits="userSpaceOnUse" x1="150" y1="0" x2="410" y2="0">
      <stop offset="0"    stop-color="#ffffff"/>
      <stop offset="0.42" stop-color="#ffffff"/>
      <stop offset="0.5"  stop-color="#ff7a7a"/>
      <stop offset="0.58" stop-color="#ffffff"/>
      <stop offset="1"    stop-color="#ffffff"/>
      <animate attributeName="x1" from="150" to="1000" dur="5.2s" repeatCount="indefinite"/>
      <animate attributeName="x2" from="410" to="1260" dur="5.2s" repeatCount="indefinite"/>
    </linearGradient>

    <!-- disc behind the clover -->
    <radialGradient id="disc">
      <stop offset="0" stop-color="#3a0808"/>
      <stop offset="1" stop-color="#070202"/>
    </radialGradient>

    <!-- mottled ink texture, only where the leaves are -->
    <filter id="grain" x="-10%" y="-10%" width="120%" height="120%">
      <feTurbulence type="fractalNoise" baseFrequency=".7" numOctaves="3" seed="7" result="n"/>
      <feColorMatrix in="n" type="matrix"
        values="0 0 0 0 .2  0 0 0 0 .17  0 0 0 0 .17  3 0 0 0 -1.75" result="g"/>
      <feComposite in="g" in2="SourceAlpha" operator="in" result="gi"/>
      <feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="gi"/></feMerge>
    </filter>

    <!-- sticker-like pale outline plus a red glow around the clover -->
    <filter id="rim" x="-20%" y="-20%" width="140%" height="140%">
      <feMorphology in="SourceAlpha" operator="dilate" radius="2" result="d1"/>
      <feFlood flood-color="#e8dada"/><feComposite in2="d1" operator="in" result="edge"/>
      <feMorphology in="SourceAlpha" operator="dilate" radius="4" result="d2"/>
      <feFlood flood-color="#ff2f2f"/><feComposite in2="d2" operator="in" result="red"/>
      <feGaussianBlur in="red" stdDeviation="6" result="glow"/>
      <feMerge><feMergeNode in="glow"/><feMergeNode in="edge"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>

    <filter id="soft" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="7"/>
    </filter>
    <filter id="textGlow" x="-25%" y="-60%" width="150%" height="220%">
      <feGaussianBlur stdDeviation="3.2" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <g clip-path="url(#frame)">
    <rect width="{W}" height="{H}" fill="#050202"/>

    <!-- LAYER 1 - background with slow parallax (moves little = feels "far") -->
    <g>
      <animateTransform attributeName="transform" type="translate"
                        values="-38,-14; -8,-24; -38,-14" dur="19s"
                        calcMode="spline" keyTimes="0;0.5;1"
                        keySplines=".42 0 .58 1;.42 0 .58 1" repeatCount="indefinite"/>
      <!-- very slow zoom: the camera moves in and out, never stops -->
      <animateTransform attributeName="transform" type="scale" additive="sum"
                        values="1;1.045;1" dur="27s"
                        calcMode="spline" keyTimes="0;0.5;1"
                        keySplines=".42 0 .58 1;.42 0 .58 1" repeatCount="indefinite"/>
      <image xlink:href="{BG}" x="0" y="0" width="{BW}" height="{BH}"
             preserveAspectRatio="xMidYMid slice" opacity=".85"/>
    </g>

    <!-- ember pulsing behind the portrait -->
    <ellipse cx="{FCX}" cy="{FCY}" rx="190" ry="150" fill="url(#emberGlow)">
      <animate attributeName="opacity" values=".45;.9;.45" dur="3.4s" repeatCount="indefinite"/>
      <animateTransform attributeName="transform" type="scale" additive="sum"
                        values="1;1.07;1" dur="3.4s" repeatCount="indefinite"/>
    </ellipse>

    <!-- gradient separating the portrait from the text -->
    <rect width="{W}" height="{H}" fill="url(#fade)"/>

    <!-- LAYER 2 - clover portrait: floats and tilts (fake Y rotation) -->
    <g>
      <!-- vertical float -->
      <animateTransform attributeName="transform" type="translate"
                        values="0,0; 0,-9; 0,0" dur="5.5s"
                        calcMode="spline" keyTimes="0;0.5;1"
                        keySplines=".45 0 .55 1;.45 0 .55 1" repeatCount="indefinite"/>
      <!-- tilt: horizontal scale + skew = fake 3D turn -->
      <g>
        <animateTransform attributeName="transform" type="matrix"
                          values="1,0,0,1,0,0;
                                  0.965,0.022,-0.014,1,7.1,-4.4;
                                  1,0,0,1,0,0;
                                  0.965,-0.022,0.014,1,-7.1,4.4;
                                  1,0,0,1,0,0"
                          dur="11s" calcMode="spline" keyTimes="0;0.25;0.5;0.75;1"
                          keySplines=".42 0 .58 1;.42 0 .58 1;.42 0 .58 1;.42 0 .58 1"
                          repeatCount="indefinite"/>
        <circle cx="{FCX}" cy="{FCY}" r="{FRG}" fill="#ff1e1e" opacity=".30" filter="url(#soft)"/>
        <circle cx="{FCX}" cy="{FCY}" r="{FR}" fill="url(#disc)"/>
        <!-- black clover: turns slowly, its ink strokes light up on every surge -->
        <g transform="translate({FCX} {FCY})" filter="url(#rim)">
          <g>
            <animateTransform attributeName="transform" type="rotate"
                              from="0" to="360" dur="48s" repeatCount="indefinite"/>
            <g fill="#0a0606" filter="url(#grain)">
            {LEAVES}
            </g>
            <g fill="none" stroke="#7d6f6f" stroke-width="1.4" stroke-linecap="round">
              <animate attributeName="stroke" values="#7d6f6f;#ff4d4d;#7d6f6f;#7d6f6f"
                       keyTimes="0;.015;.12;1" dur="{SURGE}s" repeatCount="indefinite"/>
            {MARKS}
            </g>
          </g>
        </g>
        <!-- the heart of the clover flares with the surge -->
        <circle cx="{FCX}" cy="{FCY}" r="30" fill="url(#eyeGlow)" opacity="0">
          <animate attributeName="opacity" values="0;1;.15;0;0" keyTimes="0;.012;.06;.12;1"
                   dur="{SURGE}s" repeatCount="indefinite"/>
        </circle>
        <!-- outer ring that spins and breathes -->
        <circle cx="{FCX}" cy="{FCY}" r="{FRR}" fill="none" stroke="#ff2f2f"
                stroke-width="2" stroke-dasharray="26 14" opacity=".8">
          <animateTransform attributeName="transform" type="rotate"
                            from="0 {FCX} {FCY}" to="360 {FCX} {FCY}"
                            dur="26s" repeatCount="indefinite"/>
        </circle>
        <!-- second ring spinning the other way: counter-rotation adds depth -->
        <circle cx="{FCX}" cy="{FCY}" r="{FRR2}" fill="none" stroke="#ff5a5a"
                stroke-width="1" stroke-dasharray="4 12" opacity=".55">
          <animateTransform attributeName="transform" type="rotate"
                            from="360 {FCX} {FCY}" to="0 {FCX} {FCY}"
                            dur="17s" repeatCount="indefinite"/>
        </circle>
        <circle cx="{FCX}" cy="{FCY}" r="{FR}" fill="none" stroke="#ff6b6b" stroke-width="1.4">
          <animate attributeName="opacity" values=".35;1;.35" dur="3.4s" repeatCount="indefinite"/>
        </circle>
      </g>
    </g>

    <!-- surge: shockwaves and arcs, visible only for an instant each cycle -->
    <g>{SHOCK}</g>
    <g>{ARCS}</g>

    <!-- sparks in a real orbit around the portrait (animateMotion) -->
    <g>{SPARKS}</g>

    <!-- LAYER 3 - embers in front (move more = feel "close") -->
    <g fill="#ff5a3c">{EMBERS}</g>

    <!-- text (without the name: it is already at the top of the README) -->
    <g filter="url(#textGlow)">
      <text x="452" y="150" font-family="Verdana,DejaVu Sans,sans-serif" font-size="29"
            font-weight="bold" fill="url(#titleShine)" letter-spacing="3.4">SOFTWARE DEVELOPER
        <animate attributeName="opacity" values=".85;1;.85" dur="4.6s" repeatCount="indefinite"/>
      </text>
    </g>
    <rect x="452" y="170" width="0" height="2" fill="#ff2f2f">
      <animate attributeName="width" values="0;420;420;0" keyTimes="0;.35;.8;1"
               dur="6s" repeatCount="indefinite"/>
    </rect>
    <text x="454" y="202" font-family="Verdana,DejaVu Sans,sans-serif" font-size="14"
          fill="#c9b8b8" letter-spacing="1.0">Frontend &#183; Backend &#183; Full Stack &#183; Cloud &#183; DevOps</text>

    <!-- the whole frame lights up for a split second -->
    <rect width="{W}" height="{H}" fill="#ff5252" opacity="0">
      <animate attributeName="opacity" values="0;.14;0;0" keyTimes="0;.012;.07;1"
               dur="{SURGE}s" repeatCount="indefinite"/>
    </rect>

    <rect width="{W}" height="{H}" fill="url(#vignette)"/>
    <rect width="{W}" height="{H}" fill="none" stroke="#7a1414" stroke-width="2" rx="16">
      <animate attributeName="stroke" values="#7a1414;#ff4040;#7a1414;#7a1414"
               keyTimes="0;.015;.12;1" dur="{SURGE}s" repeatCount="indefinite"/>
    </rect>
  </g>
</svg>
"""


def embers(n=13):
    """Rising embers, each with its own rhythm."""
    random.seed(7)
    out = []
    for i in range(n):
        x = random.randint(30, W - 30)
        r = round(random.uniform(1.0, 2.6), 1)
        dur = round(random.uniform(6.0, 13.0), 1)
        delay = round(random.uniform(0, 9.0), 1)
        drift = random.randint(-26, 26)
        out.append(
            '<circle cx="%d" cy="%d" r="%s" opacity="0">'
            '<animate attributeName="cy" values="%d;%d" dur="%ss" begin="%ss" repeatCount="indefinite"/>'
            '<animate attributeName="cx" values="%d;%d" dur="%ss" begin="%ss" repeatCount="indefinite"/>'
            '<animate attributeName="opacity" values="0;.9;.35;.8;.2;0" dur="%ss" begin="%ss" repeatCount="indefinite"/>'
            '<animate attributeName="r" values="%s;%s;%s" dur="%ss" begin="%ss" repeatCount="indefinite"/>'
            "</circle>"
            % (x, H + 12, r, H + 12, -14, dur, delay, x, x + drift, dur, delay, dur, delay,
               r, round(r * 1.6, 1), r, round(dur / 3.0, 1), delay)
        )
    return "".join(out)


def shockwaves():
    """Shockwaves coming out of the portrait on every surge.

    They last a fraction of the cycle: the rest of the time they are
    invisible, which is exactly what makes them stand out when they appear.
    """
    out = []
    for i, (delay, w) in enumerate(((0, 3.2), (-0.45, 2.0))):
        out.append(
            '<circle cx="%d" cy="%d" r="%d" fill="none" stroke="#ff3b3b"'
            ' stroke-width="%s" opacity="0">'
            '<animate attributeName="r" values="%d;%d;%d;%d" keyTimes="0;.015;.13;1"'
            ' dur="%ss" begin="%ss" repeatCount="indefinite" calcMode="spline"'
            ' keySplines="0 0 1 1;.12 .7 .3 1;0 0 1 1"/>'
            '<animate attributeName="opacity" values="0;.9;0;0" keyTimes="0;.015;.13;1"'
            ' dur="%ss" begin="%ss" repeatCount="indefinite"/>'
            '<animate attributeName="stroke-width" values="%s;%s;.4;.4" keyTimes="0;.015;.13;1"'
            ' dur="%ss" begin="%ss" repeatCount="indefinite"/>'
            "</circle>"
            % (FACE_CX, FACE_CY, FACE_R, w,
               FACE_R, FACE_R, FACE_R + 145, FACE_R + 145, SURGE, delay,
               SURGE, delay, w, w, SURGE, delay)
        )
    return "".join(out)


def sparks(n=5):
    """Sparks travelling a real orbit around the portrait.

    animateMotion over a circular path: each one with its own radius,
    speed and starting point, so they do not form a pattern.
    """
    random.seed(13)
    out = []
    for i in range(n):
        r = FACE_R + 14 + i * 7
        dur = round(random.uniform(7.0, 15.0), 1)
        begin = round(-random.uniform(0, dur), 1)
        rad = round(random.uniform(1.4, 2.6), 1)
        path = "M %d,%d A %d,%d 0 1,1 %d,%d A %d,%d 0 1,1 %d,%d" % (
            FACE_CX, FACE_CY - r, r, r, FACE_CX, FACE_CY + r, r, r, FACE_CX, FACE_CY - r)
        out.append(
            '<circle r="%s" fill="#ffb08a" opacity=".9">'
            '<animateMotion dur="%ss" begin="%ss" repeatCount="indefinite" path="%s"/>'
            '<animate attributeName="opacity" values=".25;1;.4;.95;.25" dur="%ss"'
            ' begin="%ss" repeatCount="indefinite"/>'
            "</circle>" % (rad, dur, begin, path, round(dur / 2.5, 1), begin)
        )
    return "".join(out)


def arcs(n=7):
    """Jagged energy arcs that only appear during the surge."""
    import math
    random.seed(29)
    out = []
    for i in range(n):
        a0 = random.uniform(0, math.pi * 2)
        span = random.uniform(0.35, 0.85)
        r0 = FACE_R + random.uniform(4, 26)
        pts = []
        steps = 6
        for k in range(steps + 1):
            a = a0 + span * k / float(steps)
            rr = r0 + random.uniform(-9, 9)
            pts.append("%.1f,%.1f" % (FACE_CX + rr * math.cos(a), FACE_CY + rr * math.sin(a)))
        off = round(-random.uniform(0, 0.35), 2)
        out.append(
            '<polyline points="%s" fill="none" stroke="#ff8f6b" stroke-width="1.4"'
            ' stroke-linecap="round" opacity="0">'
            '<animate attributeName="opacity" values="0;.95;0;0" keyTimes="0;.012;.075;1"'
            ' dur="%ss" begin="%ss" repeatCount="indefinite"/>'
            "</polyline>" % (" ".join(pts), SURGE, off)
        )
    return "".join(out)


def main():
    bg_path, out_path = sys.argv[1], sys.argv[2]
    leaves, marks = clover_markup()
    svg = SVG.format(
        W=W, H=H,
        BW=int(W * 1.15), BH=int(H * 1.15),
        BG=build_bg(bg_path), LEAVES=leaves, MARKS=marks,
        FCX=FACE_CX, FCY=FACE_CY, FR=FACE_R, FRG=FACE_R + 16, FRR=FACE_R + 11,
        FRR2=FACE_R + 24,
        EMBERS=embers(),
        SHOCK=shockwaves(), SPARKS=sparks(), ARCS=arcs(), SURGE=SURGE,
    )
    with io.open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(svg)
    print("written %s  (%.0f KB)" % (out_path, len(svg.encode("utf-8")) / 1024.0))


if __name__ == "__main__":
    main()
