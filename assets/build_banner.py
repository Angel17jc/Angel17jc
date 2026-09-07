# -*- coding: utf-8 -*-
"""Genera assets/banner.svg: banner animado con efecto pseudo-3D.

Uso:  python build_banner.py <fondo.png> <personaje.png> <salida.svg>

El PNG se incrusta como data URI porque GitHub (camo) bloquea las
referencias externas dentro de un SVG. La animacion usa SMIL, que es lo
que ya funciona en el README (readme-typing-svg).
"""
import base64
import io
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter

W, H = 1000, 320          # lienzo del banner
FACE_R = 104              # radio del retrato circular
FACE_CX, FACE_CY = 208, 160


def _b64(img, fmt="JPEG", **kw):
    buf = io.BytesIO()
    img.save(buf, fmt, **kw)
    mime = "jpeg" if fmt == "JPEG" else fmt.lower()
    return "data:image/%s;base64,%s" % (mime, base64.b64encode(buf.getvalue()).decode())


def build_bg(path):
    """Fondo: recorte apaisado, oscurecido y algo desenfocado (da profundidad)."""
    im = Image.open(path).convert("RGB")
    # recorte central con la proporcion del banner, un 15% mas ancho para el parallax
    tw, th = int(W * 1.15), int(H * 1.15)
    scale = max(tw / im.width, th / im.height)
    im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.LANCZOS)
    left = (im.width - tw) // 2
    top = int((im.height - th) * BG_FOCUS_Y)    # banda del ojo/colmillos
    im = im.crop((left, top, left + tw, top + th))
    im = im.filter(ImageFilter.GaussianBlur(1.6))
    im = Image.eval(im, lambda v: int(v * BG_DARKEN))   # que no pelee con el texto
    return _b64(im, "JPEG", quality=78, optimize=True)


BG_FOCUS_Y = 0.62         # que banda vertical del fondo se recorta, 0..1
BG_DARKEN = 0.50          # cuanto se oscurece el fondo
FACE_ZOOM = 0.72          # fraccion del lado menor que se recorta (menos = mas zoom)
FACE_FOCUS_X = 0.50       # centro del recorte, 0..1
FACE_FOCUS_Y = 0.32


def build_face(path):
    """Personaje: recorte a la cara, tinte calido y desvanecido radial.

    El desvanecido evita el borde duro del circulo: el fondo verde del
    original se disuelve en negro y el personaje parece emerger.
    """
    im = Image.open(path).convert("RGBA")
    side = int(min(im.width, im.height) * FACE_ZOOM)
    cx, cy = int(im.width * FACE_FOCUS_X), int(im.height * FACE_FOCUS_Y)
    left = max(0, min(cx - side // 2, im.width - side))
    top = max(0, min(cy - side // 2, im.height - side))
    im = im.crop((left, top, left + side, top + side)).resize((512, 512), Image.LANCZOS)

    rgb = im.convert("RGB")
    r, g, b = rgb.split()

    # "verdor" = cuanto supera G al mayor de R y B. Es ~0 en el pelo blanco,
    # la piel, los cuernos negros y los ojos rojos; alto solo en la hierba.
    green = ImageChops.subtract(g, ImageChops.lighter(r, b))
    green = green.point(lambda v: min(255, int(v * 5.0)))
    green = green.filter(ImageFilter.GaussianBlur(1.5))

    # la hierba se funde a rojo muy oscuro...
    rgb = Image.composite(Image.new("RGB", (512, 512), (46, 8, 10)), rgb, green)
    # ...y un tinte global suave une el personaje con la paleta del banner
    rgb = Image.blend(rgb, Image.new("RGB", (512, 512), (110, 16, 18)), 0.16)
    rgb = Image.eval(rgb, lambda v: int(v * 0.92))
    im = rgb.convert("RGBA")

    # alfa radial: opaco hasta el 58% del radio, transparente al 100%
    mask = Image.new("L", (512, 512), 0)
    d = ImageDraw.Draw(mask)
    steps = 64
    for i in range(steps, 0, -1):
        f = i / float(steps)                      # 1.0 borde -> 0 centro
        r = 256 * f
        t = max(0.0, 1 - (f - 0.58) / 0.42)      # acotado: evita base negativa
        a = 255 if f <= 0.58 else int(255 * t ** 1.5)
        d.ellipse((256 - r, 256 - r, 256 + r, 256 + r), fill=a)
    mask = mask.filter(ImageFilter.GaussianBlur(4))
    # donde habia hierba, ademas, se vuelve transparente
    mask = ImageChops.subtract(mask, green.point(lambda v: int(v * 0.85)))
    im.putalpha(mask)
    return _b64(im, "PNG", optimize=True)


SVG = u"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img"
     aria-label="Angel Conforme - banner animado">
  <title>Angel Conforme</title>
  <defs>
    <clipPath id="frame"><rect x="0" y="0" width="{W}" height="{H}" rx="16"/></clipPath>
    <clipPath id="face"><circle cx="{FCX}" cy="{FCY}" r="{FR}"/></clipPath>

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

    <!-- CAPA 1 - fondo con parallax lento (se mueve poco = queda "lejos") -->
    <g>
      <animateTransform attributeName="transform" type="translate"
                        values="-38,-14; -8,-24; -38,-14" dur="19s"
                        calcMode="spline" keyTimes="0;0.5;1"
                        keySplines=".42 0 .58 1;.42 0 .58 1" repeatCount="indefinite"/>
      <image xlink:href="{BG}" x="0" y="0" width="{BW}" height="{BH}"
             preserveAspectRatio="xMidYMid slice" opacity=".85"/>
    </g>

    <!-- brasa que late detras del retrato -->
    <ellipse cx="{FCX}" cy="{FCY}" rx="190" ry="150" fill="url(#emberGlow)">
      <animate attributeName="opacity" values=".45;.9;.45" dur="3.4s" repeatCount="indefinite"/>
      <animateTransform attributeName="transform" type="scale" additive="sum"
                        values="1;1.07;1" dur="3.4s" repeatCount="indefinite"/>
    </ellipse>

    <!-- degradado que separa el retrato del texto -->
    <rect width="{W}" height="{H}" fill="url(#fade)"/>

    <!-- CAPA 2 - retrato: flota y se inclina (pseudo rotacion en Y) -->
    <g>
      <!-- flotacion vertical -->
      <animateTransform attributeName="transform" type="translate"
                        values="0,0; 0,-9; 0,0" dur="5.5s"
                        calcMode="spline" keyTimes="0;0.5;1"
                        keySplines=".45 0 .55 1;.45 0 .55 1" repeatCount="indefinite"/>
      <!-- inclinacion: escala horizontal + sesgo = giro 3D falso -->
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
        <image xlink:href="{FACE}" clip-path="url(#face)"
               x="{FX}" y="{FY}" width="{FS}" height="{FS}"/>
        <!-- anillo exterior que gira y respira -->
        <circle cx="{FCX}" cy="{FCY}" r="{FRR}" fill="none" stroke="#ff2f2f"
                stroke-width="2" stroke-dasharray="26 14" opacity=".8">
          <animateTransform attributeName="transform" type="rotate"
                            from="0 {FCX} {FCY}" to="360 {FCX} {FCY}"
                            dur="26s" repeatCount="indefinite"/>
        </circle>
        <circle cx="{FCX}" cy="{FCY}" r="{FR}" fill="none" stroke="#ff6b6b" stroke-width="1.4">
          <animate attributeName="opacity" values=".35;1;.35" dur="3.4s" repeatCount="indefinite"/>
        </circle>
      </g>
    </g>

    <!-- CAPA 3 - brasas al frente (se mueven mas = quedan "cerca") -->
    <g fill="#ff5a3c">{EMBERS}</g>

    <!-- texto (sin el nombre: ya va en el h1 del README) -->
    <g filter="url(#textGlow)">
      <text x="452" y="150" font-family="Verdana,DejaVu Sans,sans-serif" font-size="21"
            font-weight="bold" fill="#ffffff" letter-spacing="2.2">SOFTWARE ENGINEERING STUDENT
        <animate attributeName="opacity" values=".85;1;.85" dur="4.6s" repeatCount="indefinite"/>
      </text>
    </g>
    <rect x="452" y="170" width="0" height="2" fill="#ff2f2f">
      <animate attributeName="width" values="0;420;420;0" keyTimes="0;.35;.8;1"
               dur="6s" repeatCount="indefinite"/>
    </rect>
    <text x="454" y="202" font-family="Verdana,DejaVu Sans,sans-serif" font-size="14"
          fill="#c9b8b8" letter-spacing="1.0">Frontend &#183; Backend &#183; Full Stack &#183; Cloud &#183; DevOps</text>

    <rect width="{W}" height="{H}" fill="url(#vignette)"/>
    <rect width="{W}" height="{H}" fill="none" stroke="#7a1414" stroke-width="2" rx="16"/>
  </g>
</svg>
"""


def embers(n=13):
    """Brasas subiendo, cada una con su propio ritmo."""
    import random
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
            '<animate attributeName="opacity" values="0;.85;.6;0" dur="%ss" begin="%ss" repeatCount="indefinite"/>'
            "</circle>"
            % (x, H + 12, r, H + 12, -14, dur, delay, x, x + drift, dur, delay, dur, delay)
        )
    return "".join(out)


def main():
    bg_path, face_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    svg = SVG.format(
        W=W, H=H,
        BW=int(W * 1.15), BH=int(H * 1.15),
        BG=build_bg(bg_path), FACE=build_face(face_path),
        FCX=FACE_CX, FCY=FACE_CY, FR=FACE_R, FRG=FACE_R + 16, FRR=FACE_R + 11,
        FX=FACE_CX - FACE_R, FY=FACE_CY - FACE_R, FS=FACE_R * 2,
        EMBERS=embers(),
    )
    with io.open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(svg)
    print("escrito %s  (%.0f KB)" % (out_path, len(svg.encode("utf-8")) / 1024.0))


if __name__ == "__main__":
    main()
