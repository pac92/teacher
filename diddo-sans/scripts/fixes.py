"""Correcciones por glifo que el engrosado automático no resuelve (fase 5).

Hay dos momentos:
  - `pre_embolden`: sobre el esqueleto de Montserrat (unidades de Montserrat).
  - `post_embolden`: sobre los contornos ya engrosados, antes de reescalar.

Cada corrección está documentada en docs/design-brief.md (§ Correcciones).
"""

from __future__ import annotations

import pathops
from fontTools.misc.transform import Transform

from diddolib import embolden, glyph_to_path, path_to_glyph, round_stroke, transformed, union


def _contours(glyph):
    out = []
    for c in glyph.contours:
        p = pathops.Path()
        c.draw(p.getPen())
        out.append(p)
    return out


def _shift_contours(glyph, idxs, dx=0.0, dy=0.0):
    for i, c in enumerate(glyph.contours):
        if i in idxs:
            for pt in c.points:
                pt.x += dx
                pt.y += dy


def _gap_ok(a: pathops.Path, b: pathops.Path, stroke: float, min_gap: float) -> bool:
    """¿Quedan a y b separados al menos `min_gap` tras engrosarlos con `stroke`?"""
    inter = pathops.Path()
    pathops.intersection([embolden(a, stroke + min_gap)], [embolden(b, stroke + min_gap)], inter.getPen())
    return not list(inter.contours)


def _push_apart(glyph, left_idx, right_idx, others, stroke, min_gap, step=4.0, max_shift=300.0) -> float:
    """Separa en horizontal dos grupos de contornos (entre sí, o de los contornos `others`)."""
    moved = 0.0
    while moved < max_shift:
        paths = _contours(glyph)
        left = union([paths[i] for i in left_idx])
        right = union([paths[i] for i in right_idx])
        if others:
            rest = union([paths[i] for i in others])
            ok = _gap_ok(left, rest, stroke, min_gap) and _gap_ok(right, rest, stroke, min_gap)
        else:
            ok = _gap_ok(left, right, stroke, min_gap)
        if ok:
            break
        _shift_contours(glyph, left_idx, dx=-step / 2)
        _shift_contours(glyph, right_idx, dx=+step / 2)
        moved += step
    return moved


def pre_embolden(font, cfg) -> dict[str, str]:
    stroke = cfg["stroke"]
    notes = {}
    skeletons = {}

    # Diéresis: los dos puntos se funden. Se separan hasta dejar un hueco visible.
    g = font["dieresiscomb"]
    moved = _push_apart(g, [1], [0], [], stroke, min_gap=cfg["dieresis_gap"])
    notes["dieresiscomb"] = f"puntos separados {moved:.0f} UPM"

    # %: los círculos se pegan a la barra. Se apartan en horizontal y se ensancha el glifo.
    g = font["percent"]
    # contornos: 0 barra, 1-2 círculo izquierdo, 3-4 círculo derecho
    moved = _push_apart(g, [1, 2], [3, 4], [0], stroke, min_gap=cfg["percent_gap"])
    for c in g.contours:
        for pt in c.points:
            pt.x += moved / 2
    g.width += moved
    notes["percent"] = f"círculos separados {moved:.0f} UPM de la barra"

    # @: el cuenco interior casi toca la espiral. Se reduce respecto a su lado derecho (unión con el asta).
    g = font["at"]
    paths = _contours(g)
    bowl = union([paths[1], paths[2]])
    x0, y0, x1, y1 = bowl.bounds
    s = cfg["at_bowl_scale"]
    t = Transform().translate(x1, (y0 + y1) / 2).scale(s).translate(-x1, -(y0 + y1) / 2)
    for i in (1, 2):
        for pt in g.contours[i].points:
            pt.x, pt.y = t.transformPoint((pt.x, pt.y))
    notes["at"] = f"cuenco interior al {s:.0%}"

    # © y ®: se guardan los anillos para rehacerlos tras engrosar.
    for n in ("copyright", "registered"):
        skeletons[n] = _contours(font[n])
    return notes, skeletons


def post_embolden(font, cfg, skeletons) -> dict[str, str]:
    """Correcciones sobre contornos ya engrosados (unidades de Montserrat + trazo)."""
    stroke = cfg["stroke"]
    r = stroke / 2
    notes = {}

    # ª y º: la a de Diddo es de un piso, así que el ordinal también. Se toman la a y la o
    # ya engrosadas y se reducen (el peso se reduce con ellas, como en unos ordinales).
    for name, src in (("ordfeminine", "a"), ("ordmasculine", "o")):
        g = font[name]
        old = glyph_to_path(g, font)
        ox0, oy0, ox1, oy1 = old.bounds
        sp = glyph_to_path(font[src], font)
        sx0, sy0, sx1, sy1 = sp.bounds
        k = cfg["ordinal_scale"]
        top = 700 + r  # alineado con la altura de mayúsculas visible
        t = Transform().translate(ox0, top - (sy1 - sy0) * k).scale(k).translate(-sx0, -sy0)
        new = transformed(sp, t)
        if cfg["ordinal_underline"]:
            nx0, ny0, nx1, ny1 = new.bounds
            bar_y = ny0 - cfg["ordinal_underline_gap"]
            bar = round_stroke(_hline(nx0 + 20, nx1 - 20, bar_y), cfg["ordinal_underline_weight"])
            new = union([new, bar])
        path_to_glyph(new, g, round_coords=False)
        g.width = (new.bounds[2] - new.bounds[0]) + (g.width - (ox1 - ox0))
        notes[name] = f"{src} Diddo al {k:.0%}" + (" con subrayado" if cfg["ordinal_underline"] else "")

    # © y ®: anillo con un trazo menor que el general y la C/R Diddo reducida en el centro.
    for name, letter in (("copyright", "C"), ("registered", "R")):
        g = font[name]
        ring_parts = skeletons[name][:1] + skeletons[name][2:3] if name == "registered" else skeletons[name][:2]
        ring_skel = union(ring_parts)
        ring = embolden(ring_skel, cfg["ring_stroke"])
        x0, y0, x1, y1 = ring.bounds
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        lp = glyph_to_path(font[letter], font)
        lx0, ly0, lx1, ly1 = lp.bounds
        k = cfg["ring_letter_scale"]
        t = Transform().translate(cx, cy).scale(k).translate(-(lx0 + lx1) / 2, -(ly0 + ly1) / 2)
        path_to_glyph(union([ring, transformed(lp, t)]), g, round_coords=False)
        # el anillo crece r_ring hacia fuera: se mantiene el margen lateral original
        dx = cfg["ring_stroke"] / 2
        for c in g.contours:
            for pt in c.points:
                pt.x += dx - r
        g.width -= 2 * (r - dx)
        notes[name] = f"anillo con trazo {cfg['ring_stroke']} y {letter} Diddo al {k:.0%}"
    return notes


def _hline(x0, x1, y) -> pathops.Path:
    p = pathops.Path()
    pen = p.getPen()
    pen.moveTo((x0, y))
    pen.lineTo((x1, y))
    pen.endPath()
    return p
