#!/usr/bin/env python3
"""Pruebas visuales rápidas: compone texto con un UFO y lo rasteriza a PNG.

Uso:
    python scripts/proof.py sources/DiddoSans-Bold.ufo proofs/alfabeto.png "abc" "ABC" ...
"""

from __future__ import annotations

import sys
from pathlib import Path

import ufoLib2
from PIL import Image, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
from diddolib import glyph_to_path, render, transformed, union  # noqa: E402
from fontTools.misc.transform import Transform  # noqa: E402


def cmap_of(font):
    cmap = {}
    for g in font:
        for u in g.unicodes:
            cmap[u] = g.name
    return cmap


def kern_value(font, left: str, right: str) -> float:
    kern1 = {m: g for g, ms in font.groups.items() if g.startswith("public.kern1.") for m in ms}
    kern2 = {m: g for g, ms in font.groups.items() if g.startswith("public.kern2.") for m in ms}
    for l in (left, kern1.get(left)):
        for r in (right, kern2.get(right)):
            if l and r and (l, r) in font.kerning:
                return font.kerning[(l, r)]
    return 0


def set_line(font, text: str, kern: bool = True, tracking: float = 0):
    """Devuelve (trazado, avance) de una línea de texto, con la línea base en y = 0."""
    cmap = cmap_of(font)
    x = 0.0
    paths = []
    prev = None
    for ch in text:
        name = cmap.get(ord(ch), ".notdef")
        if prev and kern:
            x += kern_value(font, prev, name)
        g = font[name]
        p = glyph_to_path(g, font)
        paths.append(transformed(p, Transform().translate(x, 0)))
        x += g.width + tracking
        prev = name
    return union(paths), x


def proof(font, lines, out: Path, px_per_em: int = 120, margin: float = 0.25):
    """Compone `lines` (una por fila) con el interlineado de la fuente y guarda un PNG."""
    em = font.info.unitsPerEm
    asc = font.info.openTypeOS2TypoAscender or font.info.ascender
    desc = font.info.openTypeOS2TypoDescender or font.info.descender
    line_h = asc - desc
    set_lines = [set_line(font, t) for t in lines]
    width = max(adv for _, adv in set_lines) + 2 * margin * em
    height = len(lines) * line_h + 2 * margin * em
    scale = px_per_em / em
    W, H = int(width * scale), int(height * scale)
    canvas = Image.new("L", (W, H), 0)
    band_h = int(line_h * scale)
    for i, (p, _) in enumerate(set_lines):
        top = margin * em + i * line_h
        img = render(p, (-margin * em, desc, width - margin * em, asc), (W, band_h))
        canvas.paste(img, (0, int(top * scale)))
    out.parent.mkdir(parents=True, exist_ok=True)
    ImageOps.invert(canvas).save(out)
    return out


def main():
    ufo, out, *lines = sys.argv[1:]
    font = ufoLib2.Font.open(ufo)
    proof(font, lines, Path(out))


if __name__ == "__main__":
    main()
