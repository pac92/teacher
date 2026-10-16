#!/usr/bin/env python3
"""Pruebas: espécimen HTML, hojas PNG y variantes para decidir el brief (fase 2).

Genera:
  proofs/specimen.html          espécimen con la WOFF2 compilada
  proofs/alfabeto.png           juego de caracteres completo
  proofs/brief/*.png            comparación de opciones del brief (una variante por fila)
  proofs/overlay/*.png          superposición con los logos (lo genera overlay_test.py)

Uso:
    python scripts/specimen.py [--no-variants]
"""

from __future__ import annotations

import argparse
import html
import sys
from pathlib import Path

import ufoLib2
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from diddoize import CHARSET, diddoize, load_config  # noqa: E402
from proof import proof  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PROOFS = ROOT / "proofs"
UFO = ROOT / "sources" / "DiddoSans-Bold.ufo"

SAMPLE_LINES = [
    "diddo pad",
    "Hamburgefonstiv",
    "¿Bailó el pingüino?",
    "El veloz murciélago hindú comía feliz cardillo y kiwi.",
    "La cigüeña tocaba el saxofón detrás del palenque de paja.",
]

VARIANTS = {
    "peso": [
        ("trazo 95 (diddo, propuesto)", {}),
        ("trazo 105 (pad)", {"stroke": 105}),
    ],
    "ascendentes": [
        ("ascendente 857 / descendente -331 (logo, propuesto)", {}),
        ("ascendente 742 / descendente -194 (Montserrat)", {"ascender": 742, "descender": -194}),
    ],
    "ahusado": [
        ("asta Diddo en b d i l k a p q (propuesto)", {}),
        ("asta de Montserrat (solo engrosado)", {"tapered": [], "stems": {}}),
    ],
}
VARIANT_TEXT = ["diddo pad", "bdhiklmnpqu", "hablando del lápiz"]


def label_image(img: Image.Image, text: str) -> Image.Image:
    pad = 44
    out = Image.new("L", (img.width, img.height + pad), 255)
    out.paste(img, (0, pad))
    d = ImageDraw.Draw(out)
    try:
        f = ImageFont.load_default(size=26)
    except TypeError:  # Pillow antiguo
        f = ImageFont.load_default()
    d.text((20, 8), text, fill=90, font=f)
    return out


def stack(images: list[Image.Image]) -> Image.Image:
    w = max(i.width for i in images)
    h = sum(i.height for i in images) + 20 * (len(images) - 1)
    out = Image.new("L", (w, h), 255)
    y = 0
    for i in images:
        out.paste(i, (0, y))
        y += i.height + 20
    return out


def variants():
    tmp = ROOT / "build" / "variants"
    out_dir = PROOFS / "brief"
    out_dir.mkdir(parents=True, exist_ok=True)
    for topic, options in VARIANTS.items():
        rows = []
        for i, (label, overrides) in enumerate(options):
            cfg = load_config(None)
            cfg.update(overrides)
            ufo = tmp / f"{topic}-{i}.ufo"
            font, _ = diddoize(cfg, ufo, verbose=False)
            png = tmp / f"{topic}-{i}.png"
            proof(font, VARIANT_TEXT, png, px_per_em=110)
            rows.append(label_image(Image.open(png).convert("L"), label))
        stack(rows).save(out_dir / f"{topic}.png")
        print(out_dir / f"{topic}.png")


def charset_lines(per_line: int = 26) -> list[str]:
    chars = [c for c in CHARSET if c not in (" ", " ")]
    return ["".join(chars[i : i + per_line]) for i in range(0, len(chars), per_line)]


def specimen_html():
    chars = "".join(c for c in CHARSET if c not in (" ", " "))
    sample = "\n".join(f'<p class="s{i}">{html.escape(t)}</p>' for i, t in enumerate(SAMPLE_LINES))
    page = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Diddo Sans Bold</title>
<style>
@font-face {{
  font-family: "Diddo Sans";
  font-weight: 700;
  src: url("../fonts/webfonts/DiddoSans-Bold.woff2") format("woff2"),
       url("../fonts/ttf/DiddoSans-Bold.ttf") format("truetype");
}}
:root {{ --ink: #1d2433; --paper: #ffffff; --accent: #4a67b5; --muted: #6b7385; }}
@media (prefers-color-scheme: dark) {{
  :root {{ --ink: #e9ecf3; --paper: #12151c; --accent: #8aa2e6; --muted: #9aa2b3; }}
}}
body {{ margin: 0; background: var(--paper); color: var(--ink);
  font-family: system-ui, sans-serif; line-height: 1.4; }}
main {{ max-width: 1100px; margin: 0 auto; padding: 32px 16px 64px; }}
h1, h2 {{ font-family: "Diddo Sans"; font-weight: 700; }}
h1 {{ font-size: clamp(56px, 12vw, 140px); line-height: 1; margin: 0 0 8px; color: var(--accent); }}
h2 {{ font-size: 28px; margin: 48px 0 12px; }}
.note {{ color: var(--muted); font-size: 14px; }}
.d {{ font-family: "Diddo Sans"; font-weight: 700; overflow-wrap: anywhere; }}
.chars {{ font-size: clamp(28px, 5vw, 48px); letter-spacing: .02em; }}
.s0 {{ font-size: clamp(64px, 14vw, 160px); line-height: 1; margin: 0; }}
.s1 {{ font-size: clamp(40px, 8vw, 96px); margin: 0; }}
.s2 {{ font-size: clamp(32px, 6vw, 64px); margin: 0; }}
.s3, .s4 {{ font-size: clamp(20px, 3.4vw, 32px); margin: 8px 0; }}
.sizes p {{ margin: 4px 0; }}
.pairs {{ font-size: clamp(24px, 4vw, 40px); }}
</style>
</head>
<body>
<main>
<h1>Diddo Sans</h1>
<p class="note">Bold · versión de prueba · derivada de Montserrat (SIL OFL 1.1) con la transformación Diddo.</p>

<h2>Muestras</h2>
<div class="d">
{sample}
</div>

<h2>Juego de caracteres</h2>
<p class="d chars">{html.escape(chars)}</p>

<h2>Tamaños</h2>
<div class="d sizes">
{"".join(f'<p style="font-size:{s}px">{s} px · diddo pad · Ñandú ágil</p>' for s in (12, 16, 24, 36, 48))}
</div>

<h2>Pares de espaciado</h2>
<p class="d pairs">nnonnoonn HHOHHOOHH ddoddpaad Ta Te To Ya Yo AV AT LT P. F, r. y, «Hola» ¿Qué? ¡Sí!</p>
</main>
</body>
</html>
"""
    (PROOFS / "specimen.html").write_text(page)
    print(PROOFS / "specimen.html")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-variants", action="store_true")
    args = ap.parse_args()
    PROOFS.mkdir(exist_ok=True)
    font = ufoLib2.Font.open(UFO)
    proof(font, charset_lines() + SAMPLE_LINES[:3], PROOFS / "alfabeto.png", px_per_em=110)
    print(PROOFS / "alfabeto.png")
    specimen_html()
    if not args.no_variants:
        variants()


if __name__ == "__main__":
    main()
