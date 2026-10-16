#!/usr/bin/env python3
"""Prueba de fidelidad: compara los glifos de Diddo Sans con las letras de los logos.

Para cada letra de referencia se lleva el contorno visible del logo al sistema
de coordenadas final de la fuente (mismo engrosado y reescalado que aplica
diddoize.py), se alinea por el borde izquierdo y se calcula la IoU
(intersección / unión) píxel a píxel. También guarda imágenes de superposición:
negro = coinciden, rojo = solo logo, azul = solo fuente.

Para pad (trazo de 105 UPM) se informa además de la IoU con el esqueleto del
logo engrosado al trazo de la fuente, para separar forma y peso.

Uso:
    python scripts/overlay_test.py [sources/DiddoSans-Bold.ufo] [--min 0.98]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import ufoLib2
from fontTools.misc.transform import Transform
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_reference import reference_letters  # noqa: E402
from diddolib import ROOT, embolden, glyph_to_path, iou, render, transformed  # noqa: E402

CASES = [  # (logo, letra del logo, glifo)
    ("diddo", "i", "i"),
    ("diddo", "d", "d"),
    ("diddo", "o", "o"),
    ("pad", "p", "p"),
    ("pad", "a", "a"),
    ("pad", "d", "d"),
]
PX_PER_UNIT = 1.0


def overlay_image(a, b):
    """a = logo, b = fuente → RGB."""
    w, h = a.size
    out = Image.new("RGB", (w, h), (255, 255, 255))
    pa, pb, po = a.load(), b.load(), out.load()
    for y in range(h):
        for x in range(w):
            ia, ib = pa[x, y] > 127, pb[x, y] > 127
            if ia and ib:
                po[x, y] = (30, 30, 30)
            elif ia:
                po[x, y] = (220, 40, 40)
            elif ib:
                po[x, y] = (40, 90, 220)
    return out


def compare(font, logo_path, glyph_name, out_png: Path | None):
    cfg = json.loads(font.lib["com.diddo.config"])
    r = cfg["stroke"] / 2
    s = cfg["cap_height"] / (700 + 2 * r)
    ref = transformed(logo_path, Transform().scale(s).translate(r, r))
    g = glyph_to_path(font[glyph_name], font)
    # Alineación horizontal: por el borde izquierdo y luego el mejor desplazamiento
    # en ±12 UPM (el espaciado del logo no es el de la fuente). En vertical, la línea base.
    ref = transformed(ref, Transform().translate(g.bounds[0] - ref.bounds[0], 0))
    x0 = min(ref.bounds[0], g.bounds[0]) - 20
    y0 = min(ref.bounds[1], g.bounds[1]) - 10
    x1 = max(ref.bounds[2], g.bounds[2]) + 20
    y1 = max(ref.bounds[3], g.bounds[3]) + 10
    box = (x0, y0, x1, y1)
    size = (int((x1 - x0) * PX_PER_UNIT), int((y1 - y0) * PX_PER_UNIT))
    b = render(g, box, size)
    best = None
    for dx in range(-12, 13, 2):
        a = render(transformed(ref, Transform().translate(dx, 0)), box, size)
        v = iou(a, b)
        if best is None or v > best[0]:
            best = (v, dx, a)
    v, dx, a = best
    if out_png:
        out_png.parent.mkdir(parents=True, exist_ok=True)
        overlay_image(a, b).save(out_png)
    return v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ufo", nargs="?", default=str(ROOT / "sources" / "DiddoSans-Bold.ufo"))
    ap.add_argument("--min", type=float, default=0.98, help="IoU mínima exigida")
    ap.add_argument("--out", default=str(ROOT / "proofs" / "overlay"))
    args = ap.parse_args()
    font = ufoLib2.Font.open(args.ufo)
    cfg = json.loads(font.lib["com.diddo.config"])
    refs = {logo: reference_letters(logo) for logo in ("diddo", "pad")}
    results = []
    ok = True
    print(f"{'logo':6} {'letra':5} {'IoU':>6} {'IoU mismo peso':>15}")
    for logo, letter, glyph in CASES:
        L = refs[logo][letter]
        v = compare(font, L["visible"], glyph, Path(args.out) / f"{logo}-{letter}.png")
        same = None
        if abs(L["stroke"] - cfg["stroke"]) > 1:
            same = compare(font, embolden(L["skeleton"], cfg["stroke"]), glyph,
                           Path(args.out) / f"{logo}-{letter}-mismo-peso.png")
        key = same if same is not None else v
        ok &= key >= args.min
        results.append({"logo": logo, "letter": letter, "iou": round(v, 4),
                        "iou_same_weight": None if same is None else round(same, 4)})
        flag = "" if key >= args.min else "  ✗"
        print(f"{logo:6} {letter:5} {v:6.3f} {'' if same is None else f'{same:15.3f}'}{flag}")
    Path(args.out).mkdir(parents=True, exist_ok=True)
    (Path(args.out) / "results.json").write_text(json.dumps(results, indent=2) + "\n")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
