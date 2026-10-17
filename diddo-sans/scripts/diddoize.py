#!/usr/bin/env python3
"""Transformación "Diddo": Montserrat Regular → fuente de diseño Diddo Sans Bold.

Uso:
    python scripts/diddoize.py [--config scripts/config.json] [--out sources/DiddoSans-Bold.ufo]

Pasos (ver PLAN.md, fase 4):
  1. Carga la instancia Regular de Montserrat (UFO generado con fontmake) y
     se queda con el juego de caracteres v1.
  2. Rasgos de esqueleto Diddo: asta ahusada, ascendentes y descendentes largos,
     a de un piso, p = d girada, punto de la i del logo, diacríticos separados.
  3. Engrosado: relleno ∪ trazo redondo (como en los logos).
  4. Reescalado a las métricas finales y márgenes laterales.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import pathops
import ufoLib2
from fontTools.misc.transform import Transform

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fixes  # noqa: E402
from diddolib import ROOT, difference, embolden, glyph_to_path, path_to_glyph, transformed, union  # noqa: E402

UPSTREAM_UFO = ROOT / "build" / "instance_ufo" / "Montserrat-Regular.ufo"

# Juego de caracteres v1 (PLAN.md): ASCII imprimible + español + tipografía básica.
CHARSET = (
    " !\"#$%&'()*+,-./0123456789:;<=>?@"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`"
    "abcdefghijklmnopqrstuvwxyz{|}~"
    " ¡¿«»€ºª·…‘’“”•©®°§´¨–—"
    "áéíóúüñÁÉÍÓÚÜÑ"
)

DEFAULTS = {
    # Ancho total del trazo redondo, en UPM de Montserrat (diddo = 95, pad = 105).
    "stroke": 95,
    # Altura del esqueleto de las ascendentes (logo: 857; Montserrat: 742).
    "ascender": 857,
    # Profundidad del esqueleto de las descendentes (logo, p = d girada: −331,5; Montserrat: −194).
    "descender": -331.5,
    # Asta Diddo, regla general: ancho del relleno en la base y pendiente del borde exterior.
    "stem_base_width": 110,
    "stem_slope": 0.053,  # ≈ 3°
    # Asta medida en el logo, por glifo (se impone a la regla general):
    #   w0/w1 = diámetro de la base/cabeza; top = altura de la cabeza (None = la de Montserrat);
    #   foot = desplazamiento hacia fuera de la base (el "pie" de la d);
    #   knee = altura hasta la que el borde interior es vertical; top_dx = inclinación de la cabeza.
    "stems": {
        "d": {"w0": 103, "w1": 64, "foot": 20, "knee": 300, "inner_dx": -3, "outer_knee": [200, 105]},
        "b": {"w0": 103, "w1": 64, "foot": 20, "knee": 300, "inner_dx": -3, "outer_knee": [200, 105]},
        "a": {"w0": 103, "w1": 78, "foot": 20, "knee": 200, "top": 532, "top_dx": 9, "inner_dx": -3,
              "outer_knee": [200, 106]},
        "idotless": {"w0": 117, "w1": 93, "top": 532},
    },
    # Glifos con asta Diddo (p y q se derivan de la d). Los demás solo se engrosan.
    "tapered": ["b", "d", "idotless", "l", "k", "a", "p", "q"],
    # Las contraformas de la Montserrat de 2024 son ≈ 4 % más altas que las de los logos (2021).
    # [escala x, escala y, ancla x ("center" o "left")], medidas en reference/normalized.
    "counters": {
        "o": [1.0, 0.96, "center"],
        "d": [0.992, 0.954, "center"],
        "b": [0.992, 0.954, "center"],
        "a": [0.964, 0.954, "left"],  # en pad, el asta de la a invade la contraforma
        "g": [1.0, 0.958, "center"],
    },
    # Punto de la i (logo): diámetro y posición de su borde inferior.
    "dot_diameter": 125,
    "dot_bottom": 669,
    # Extremos libres de trazo en semicírculo (brief, decisión 3): segmento recto del
    # esqueleto que se redondea si el trazo mide entre [mín, máx] UPM de ancho.
    "round_terminals": True,
    "terminal_width": [30, 170],
    # Separación extra de los diacríticos superiores (2 × desplazamiento = no pierden hueco).
    "mark_lift": 95,
    # Correcciones (scripts/fixes.py): huecos mínimos visibles y proporciones.
    "dieresis_gap": 50,
    "percent_gap": 45,
    "at_bowl_scale": 0.86,
    "ordinal_scale": 0.58,
    "ordinal_underline": False,
    "ordinal_underline_gap": 60,
    "ordinal_underline_weight": 50,
    "ring_stroke": 40,
    "ring_letter_scale": 0.55,
    # Altura visible de mayúsculas tras reescalar.
    "cap_height": 700,
}

# Letras cuya parte superior se estira hasta la ascendente Diddo (puntos por encima de 600).
ASCENDER_GLYPHS = ["b", "d", "f", "h", "k", "l"]
# Letras cuya parte inferior se estira hasta la descendente Diddo (puntos por debajo de −100).
DESCENDER_GLYPHS = ["g", "jdotless", "y"]
LEGACY_ACCENTS = ["grave", "acute", "dieresis"]
COMPONENT_ONLY = ["acutecomb.case", "dieresiscomb.case", "tildecomb.case", "dotaccentcomb.i"]
TOP_MARKS = [
    "acutecomb", "gravecomb", "dieresiscomb", "tildecomb", "circumflexcomb",
]


# --------------------------------------------------------------------------
# Geometría del esqueleto
# --------------------------------------------------------------------------

K = 0.5522847498  # aproximación de un cuarto de círculo con una cúbica


def circle(cx: float, cy: float, r: float) -> pathops.Path:
    p = pathops.Path()
    pen = p.getPen()
    k = K * r
    pen.moveTo((cx + r, cy))
    pen.curveTo((cx + r, cy + k), (cx + k, cy + r), (cx, cy + r))
    pen.curveTo((cx - k, cy + r), (cx - r, cy + k), (cx - r, cy))
    pen.curveTo((cx - r, cy - k), (cx - k, cy - r), (cx, cy - r))
    pen.curveTo((cx + k, cy - r), (cx + r, cy - k), (cx + r, cy))
    pen.closePath()
    return p


def polygon(pts) -> pathops.Path:
    p = pathops.Path()
    pen = p.getPen()
    pen.moveTo(pts[0])
    for pt in pts[1:]:
        pen.lineTo(pt)
    pen.closePath()
    return p


def diddo_stem(
    x_inner, y0, y1, w0, w1, outer=+1, foot=0.0, knee=None, top_dx=0.0, inner_dx=0.0, outer_knee=None
) -> pathops.Path:
    """Asta Diddo: envolvente de dos círculos (base y cabeza) con el borde interior vertical.

    - `x_inner`: borde interior (el que mira al cuenco, o el izquierdo si no hay cuenco).
    - `w0`, `w1`: diámetros de la base (que apoya en y0) y de la cabeza (que llega a y1).
    - `outer`: +1 si el borde exterior está a la derecha, −1 si está a la izquierda.
    - `foot`: la base se desplaza hacia fuera (pie de la d); entre `knee` y la base,
      el borde interior se inclina hasta el círculo de la base (muesca con el cuenco).
    - `top_dx`: la cabeza se desplaza hacia fuera (asta de la a, algo inclinada).
    - `inner_dx`: corrección de la posición del borde interior respecto a Montserrat.
    - `outer_knee` = [y, w]: el borde exterior pasa por x_inner + w a la altura y
      (en la d se abre poco hasta y ≈ 200 y luego se ensancha hacia el pie).
    """
    x_inner += outer * inner_dx
    r0, r1 = w0 / 2, w1 / 2
    c0 = (x_inner + outer * (r0 + foot), y0 + r0)
    c1 = (x_inner + outer * (r1 + top_dx), y1 - r1)
    inner = [(x_inner + outer * top_dx, c1[1])]
    if knee is not None and c0[1] < knee < c1[1]:
        inner.append((x_inner, knee))
    inner.append((x_inner + outer * foot, c0[1]))
    outer_pts = [(c0[0] + outer * r0, c0[1])]
    if outer_knee is not None:
        outer_pts.append((x_inner + outer * outer_knee[1], outer_knee[0]))
    outer_pts.append((c1[0] + outer * r1, c1[1]))
    pts = inner + outer_pts
    return union([polygon(pts), circle(*c0, r0), circle(*c1, r1)])


def _unit(x, y):
    n = math.hypot(x, y)
    return (x / n, y / n) if n else (0.0, 0.0)


def _edges(contour: pathops.Path):
    """Segmentos de un contorno como (verbo, inicio, puntos), con el cierre explícito."""
    out, start, cur = [], None, None
    for verb, pts in contour.segments:
        if verb == "moveTo":
            start = cur = pts[0]
            continue
        if verb in ("closePath", "endPath"):
            if math.dist(cur, start) > 0.01:
                out.append(("lineTo", cur, [start]))
            break
        out.append((verb, cur, list(pts)))
        cur = pts[-1]
    return out


def _tangent_in(edge):
    """Dirección con la que el segmento llega a su punto final."""
    _, a, pts = edge
    for q in reversed([a] + pts[:-1]):
        if math.dist(q, pts[-1]) > 0.01:
            return _unit(pts[-1][0] - q[0], pts[-1][1] - q[1])
    return (0.0, 0.0)


def _tangent_out(edge):
    """Dirección con la que el segmento sale de su punto inicial."""
    _, a, pts = edge
    for q in pts:
        if math.dist(q, a) > 0.01:
            return _unit(q[0] - a[0], q[1] - a[1])
    return (0.0, 0.0)


def _extent(edge, d) -> float:
    """Longitud del segmento medida en la dirección `d`."""
    _, a, pts = edge
    ps = [q[0] * d[0] + q[1] * d[1] for q in [a] + pts]
    return max(ps) - min(ps)


def _slice_width(path: pathops.Path, s, u, nrm, lat, span):
    """Corta `path` en perpendicular a `u` a la distancia `s` y mide el trozo más cercano
    a `lat`: devuelve (ancho, centro lateral) o None."""
    proj = lambda p, d: p[0] * d[0] + p[1] * d[1]  # noqa: E731
    pt = lambda al, la: (u[0] * al + nrm[0] * la, u[1] * al + nrm[1] * la)  # noqa: E731
    band = polygon([pt(s - 0.25, lat - span), pt(s + 0.25, lat - span), pt(s + 0.25, lat + span), pt(s - 0.25, lat + span)])
    cut = pathops.Path()
    pathops.intersection([path], [band], cut.getPen())
    best = None
    for c in cut.contours:
        ys = [proj(q, nrm) for q in c.points]
        lo, hi = min(ys), max(ys)
        d = 0 if lo <= lat <= hi else min(abs(lat - lo), abs(lat - hi))
        if best is None or d < best[0]:
            best = (d, lo, hi)
    if best is None:
        return None
    return best[2] - best[1], (best[1] + best[2]) / 2


def round_terminals(path: pathops.Path, min_w=30.0, max_w=170.0, parallel=-0.8) -> tuple[pathops.Path, int]:
    """Redondea en semicírculo los extremos libres de trazo, como las astas del logo.

    Un extremo es un segmento recto y convexo cuyos vecinos van en sentidos opuestos: el
    contorno llega por un lado del trazo y vuelve por el otro. Se mide el ancho del trazo
    cortándolo en perpendicular, se quita lo que queda por delante del centro del disco y
    se pone un disco de ese ancho lo más adelante posible sin pasar del corte original
    (así la letra no crece y, en los trazos diagonales cortados en la base o la altura x,
    como v, x o k, el disco no se sale de esas líneas). Sirve igual para cortes oblicuos
    (el gancho de la g o la y). Devuelve el trazado y el número de extremos redondeados.
    """
    path = union([path])
    proj = lambda p, d: p[0] * d[0] + p[1] * d[1]  # noqa: E731
    cuts, discs = [], []
    for contour in path.contours:
        edges = _edges(contour)
        n = len(edges)
        for i, (verb, a, pts) in enumerate(edges):
            b = pts[-1]
            if verb != "lineTo" or not (min_w <= math.dist(a, b) <= 2 * max_w):
                continue
            t_in = _tangent_in(edges[i - 1])
            t_out = _tangent_out(edges[(i + 1) % n])
            if proj(t_in, t_out) > parallel:
                continue
            u = _unit(t_in[0] - t_out[0], t_in[1] - t_out[1])  # hacia fuera del trazo
            # Convexo: fuera del segmento no hay relleno y dentro sí (descarta, p. ej.,
            # el hueco entre dos brazos de la E, que también tiene vecinos opuestos).
            mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            if path.contains((mid[0] + 2 * u[0], mid[1] + 2 * u[1])) or not path.contains(
                (mid[0] - 2 * u[0], mid[1] - 2 * u[1])
            ):
                continue
            nrm = (-u[1], u[0])
            # Normal del corte, hacia fuera: el disco no puede pasar de él.
            m = _unit(-(b[1] - a[1]), b[0] - a[0])
            if proj(m, u) < 0:
                m = (-m[0], -m[1])
            mu, mn, limit = proj(m, u), proj(m, nrm), proj(a, m)
            if mu < 0.2:
                continue
            tip = max(proj(a, u), proj(b, u))
            lat = (proj(a, nrm) + proj(b, nrm)) / 2
            span = math.dist(a, b)
            # Centro del disco: se mide el ancho donde el trazo aún está entero y se
            # retrocede hasta que el disco cabe detrás del corte (se repite porque el
            # ancho cambia si el trazo se abre o se curva).
            rear = s = min(proj(a, u), proj(b, u))
            w = None
            for _ in range(4):
                sw = _slice_width(path, s, u, nrm, lat, span)
                if sw is None:
                    break
                w, lat_c = sw
                s_new = (limit - w / 2 - lat_c * mn) / mu
                if abs(s_new - s) < 0.25:
                    break
                s = min(s_new, rear)
            if w is None or not (min_w <= w <= max_w):
                continue
            # El corte atraviesa el trazo: su anchura lateral se parece a la del trazo
            # (≥ 0,73 en los extremos de verdad, incluidos los ganchos oblicuos de g e y;
            # ≤ 0,51 en los lados largos que no lo son: banderín del 7 y del 1, J, [, acento).
            if w < 0.65 * abs(proj((b[0] - a[0], b[1] - a[1]), nrm)):
                continue
            # Los dos lados del trazo siguen al menos medio ancho por detrás del extremo
            # (descarta, p. ej., la parte de arriba del corchete, cuyo brazo es corto).
            if min(_extent(edges[i - 1], u), _extent(edges[(i + 1) % n], u)) < w / 2:
                continue
            c = (u[0] * s + nrm[0] * lat_c, u[1] * s + nrm[1] * lat_c)
            discs.append(circle(c[0], c[1], w / 2))
            # Lo que queda por delante del centro del disco, a lo ancho del trazo.
            lats = [lat_c - w / 2, lat_c + w / 2, proj(a, nrm), proj(b, nrm)]
            lo, hi = min(lats) - 1, max(lats) + 1
            cuts.append(polygon([
                (u[0] * al + nrm[0] * la, u[1] * al + nrm[1] * la)
                for al, la in ((s - 0.5, lo), (tip + 1, lo), (tip + 1, hi), (s - 0.5, hi))
            ]))
    if not cuts:
        return path, 0
    out = union([difference(path, union(cuts))] + discs)
    return _tidy(out), len(discs)


def _tidy(path: pathops.Path, eps: float = 1.0, min_area: float = 20.0) -> pathops.Path:
    """Quita las astillas y los segmentos de menos de `eps` UPM que dejan los cortes donde
    el disco toca el lado del trazo: el trazo redondo los convertiría en arcos espurios."""
    out = pathops.Path()
    pen = out.getPen()
    for c in path.contours:
        if abs(c.area) < min_area:
            continue
        cur = None
        for verb, pts in c.segments:
            if verb == "moveTo":
                cur = pts[0]
                pen.moveTo(cur)
            elif verb in ("closePath", "endPath"):
                pen.closePath()
            else:
                poly = [cur] + list(pts)
                if sum(math.dist(poly[k], poly[k + 1]) for k in range(len(poly) - 1)) < eps:
                    continue
                getattr(pen, verb)(*pts)
                cur = pts[-1]
    return union([out])


def stem_spec(cfg, name: str, y0: float, y1: float) -> dict:
    spec = dict(cfg["stems"].get(name, {}))
    top = spec.pop("top", None)
    if top is not None:
        y1 = top
    w0 = spec.pop("w0", cfg["stem_base_width"])
    w1 = spec.pop("w1", w0 - cfg["stem_slope"] * (y1 - y0))
    return {"y0": y0, "y1": y1, "w0": w0, "w1": w1, **spec}


def scale_counters(glyph, sx: float, sy: float, anchor: str = "center") -> None:
    """Escala los contornos interiores (contraformas) respecto a su centro o a su borde izquierdo."""
    paths = contours_as_paths(glyph)
    for c, p in zip(glyph.contours, paths):
        b = p.bounds
        inside = any(
            q is not p and q.bounds[0] < b[0] and q.bounds[1] < b[1] and q.bounds[2] > b[2] and q.bounds[3] > b[3]
            for q in paths
        )
        if not inside:
            continue
        cx = b[0] if anchor == "left" else (b[0] + b[2]) / 2
        cy = (b[1] + b[3]) / 2
        for pt in c.points:
            pt.x = cx + (pt.x - cx) * sx
            pt.y = cy + (pt.y - cy) * sy


def contours_as_paths(glyph):
    out = []
    for c in glyph.contours:
        p = pathops.Path()
        c.draw(p.getPen())
        out.append(p)
    return out


def is_stem_contour(p: pathops.Path, min_h: float = 400) -> bool:
    x0, y0, x1, y1 = p.bounds
    return (x1 - x0) < 90 and (y1 - y0) > min_h


def stretch(glyph, above: float | None = None, below: float | None = None, dy: float = 0) -> None:
    """Desplaza en vertical los puntos por encima de `above` (o por debajo de `below`)."""
    for c in glyph.contours:
        for pt in c.points:
            if above is not None and pt.y > above:
                pt.y += dy
            if below is not None and pt.y < below:
                pt.y += dy
    for a in glyph.anchors:
        if above is not None and a.y > above:
            a.y += dy


def apply_skeleton(font, cfg) -> None:
    asc_dy = cfg["ascender"] - 742
    desc_dy = cfg["descender"] - (-194)

    # 1. Ascendentes y descendentes largas (se estira el esqueleto de Montserrat).
    for n in ASCENDER_GLYPHS:
        stretch(font[n], above=600, dy=asc_dy)
    for n in DESCENDER_GLYPHS:
        stretch(font[n], below=-100, dy=desc_dy)

    # 2. a de un piso: la a pasa a ser la a.ss01 de Montserrat (cuenco de la d).
    a = font["a"]
    a.clearContours()
    for c in font["a.ss01"].contours:
        a.appendContour(c)
    a.width = font["a.ss01"].width
    a.clearAnchors()
    for an in font["a.ss01"].anchors:
        a.appendAnchor({"name": an.name, "x": an.x, "y": an.y})

    # 3. Contraformas como en los logos.
    for n, (sx, sy, anchor) in cfg["counters"].items():
        scale_counters(font[n], sx, sy, anchor)

    # 4. Asta Diddo en los glifos con asta independiente.
    xh = font.info.xHeight  # 525,5
    for target in cfg["tapered"]:
        if target in ("p", "q"):
            continue  # se derivan de la d más abajo
        g = font[target]
        paths = contours_as_paths(g)
        stems = [p for p in paths if is_stem_contour(p, min_h=300)]
        if not stems:
            print(f"aviso: {target} no tiene un asta independiente", file=sys.stderr)
            continue
        stem = max(stems, key=lambda p: p.bounds[3] - p.bounds[1])
        rest = [p for p in paths if p is not stem]
        sx0, sy0, sx1, sy1 = stem.bounds
        # b: el cuenco está a la derecha del asta, así que el borde exterior es el izquierdo
        bowl_right = target != "k" and bool(rest) and max(p.bounds[2] for p in rest) > sx1
        x_inner, outer = (sx1, -1) if bowl_right else (sx0, +1)
        spec = stem_spec(cfg, target, max(sy0, 0), sy1)
        new_stem = diddo_stem(x_inner, outer=outer, **spec)
        path_to_glyph(union(rest + [new_stem]), g, round_coords=False)

    # 5. p = d girada 180° alrededor del centro del cuenco; q = p reflejada.
    d = font["d"]
    dpath = glyph_to_path(d, font)
    w = d.width
    rot = Transform().translate(w / 2, xh / 2).rotate(math.pi).translate(-w / 2, -xh / 2)
    if "p" in cfg["tapered"]:
        ppath = transformed(dpath, rot)
        path_to_glyph(union([ppath]), font["p"], round_coords=False)
        font["p"].width = w
    if "q" in cfg["tapered"]:
        mir = Transform().translate(w, 0).scale(-1, 1)
        qpath = transformed(transformed(dpath, rot), mir)
        path_to_glyph(union([qpath]), font["q"], round_coords=False)
        font["q"].width = w
    # 6. Punto de la i del logo: círculo mayor y más alto.
    dot = font["dotaccentcomb.i"]
    x0, y0, x1, y1 = glyph_to_path(dot, font).bounds
    r = cfg["dot_diameter"] / 2
    path_to_glyph(circle((x0 + x1) / 2, cfg["dot_bottom"] + r, r), dot, round_coords=False)

    # 7. Diacríticos superiores: se suben para que no se fundan con la letra.
    for n in TOP_MARKS:
        if n not in font:
            continue
        g = font[n]
        for c in g.contours:
            for pt in c.points:
                pt.y += cfg["mark_lift"]
        for an in g.anchors:
            if not an.name.startswith("_"):
                an.y += cfg["mark_lift"]
    reposition_marks(font)


def anchors_of(font, name: str) -> dict[str, tuple[float, float]]:
    """Anclajes de un glifo; si es compuesto sin anclajes, los hereda de su primer componente."""
    g = font[name]
    if g.anchors:
        return {a.name: (a.x, a.y) for a in g.anchors}
    if g.components:
        c = g.components[0]
        dx, dy = c.transformation[4], c.transformation[5]
        return {k: (x + dx, y + dy) for k, (x, y) in anchors_of(font, c.baseGlyph).items()}
    return {}


def reposition_marks(font) -> None:
    """Recoloca los diacríticos de los compuestos según los anclajes (base.top ↔ marca._top)."""
    for g in font:
        comps = list(g.components)
        if len(comps) < 2:
            continue
        base = comps[0]
        base_anchors = anchors_of(font, base.baseGlyph)
        bx, by = base.transformation[4], base.transformation[5]
        for comp in comps[1:]:
            mark_anchors = anchors_of(font, comp.baseGlyph)
            for name, (mx, my) in mark_anchors.items():
                if name.startswith("_") and name[1:] in base_anchors:
                    ax, ay = base_anchors[name[1:]]
                    t = comp.transformation
                    comp.transformation = (t[0], t[1], t[2], t[3], ax + bx - mx, ay + by - my)
                    break


# --------------------------------------------------------------------------
# Subconjunto
# --------------------------------------------------------------------------

def required_glyphs(font) -> list[str]:
    cmap = {}
    for g in font:
        for u in g.unicodes:
            cmap[u] = g.name
    names = [".notdef"]
    missing = []
    for ch in CHARSET:
        n = cmap.get(ord(ch))
        if n is None:
            missing.append(ch)
        elif n not in names:
            names.append(n)
    if missing:
        raise SystemExit(f"Montserrat no tiene: {missing!r}")
    # glifos auxiliares que hacen falta para la a de un piso
    names.append("a.ss01")
    # cierre transitivo de componentes
    i = 0
    while i < len(names):
        for c in font[names[i]].components:
            if c.baseGlyph not in names:
                names.append(c.baseGlyph)
        i += 1
    return names


def subset(font, keep: list[str]) -> None:
    keepset = set(keep)
    for name in list(font.keys()):
        if name not in keepset:
            del font[name]
    font.glyphOrder = [n for n in keep if n in font]
    # grupos y kerning
    groups = {}
    for gname, members in font.groups.items():
        m = [x for x in members if x in keepset]
        if m:
            groups[gname] = m
    font.groups.clear()
    font.groups.update(groups)
    kerning = {}
    for (l, r), v in font.kerning.items():
        if (l in keepset or l in groups) and (r in keepset or r in groups):
            kerning[(l, r)] = v
    font.kerning.clear()
    font.kerning.update(kerning)
    font.features.text = ""  # las funciones OpenType se regeneran (fase 7)
    font.lib.pop("public.postscriptNames", None)
    cats = {k: v for k, v in font.lib.get("public.openTypeCategories", {}).items() if k in keepset}
    # Acentos sueltos (´ ` ¨): son caracteres de espaciado, no diacríticos combinables.
    for n in LEGACY_ACCENTS:
        if n in keepset:
            cats[n] = "base"
            font[n].clearAnchors()
    font.lib["public.openTypeCategories"] = cats
    # Variantes que solo se usan como componentes: se descomponen al compilar.
    font.lib["public.skipExportGlyphs"] = [n for n in COMPONENT_ONLY if n in keepset]


# --------------------------------------------------------------------------
# Engrosado y métricas
# --------------------------------------------------------------------------

def round_all_terminals(font, cfg) -> dict[str, int]:
    """Redondea los extremos libres de los contornos (no de los componentes)."""
    lo, hi = cfg["terminal_width"]
    rounded = {}
    for g in font:
        if not g.contours:
            continue
        p, count = round_terminals(glyph_to_path(g, font, decompose=False), lo, hi)
        if count:
            path_to_glyph(p, g, round_coords=False)
            rounded[g.name] = count
    return rounded


def embolden_all(font, width: float) -> dict[str, tuple[int, int]]:
    """Engrosa los contornos (no los componentes). Devuelve los cambios de nº de contornos."""
    changed = {}
    for g in font:
        if not g.contours:
            continue
        p = glyph_to_path(g, font, decompose=False)
        before = len(list(union([p]).contours))
        out = embolden(p, width)
        after = len(list(out.contours))
        if before != after:
            changed[g.name] = (before, after)
        path_to_glyph(out, g, round_coords=False)
    return changed


def rescale(font, r: float, s: float) -> None:
    """x' = (x + r)·s, y' = (y + r)·s; avance' = (avance + 2r)·s."""
    t = Transform().scale(s).translate(r, r)
    for g in font:
        for c in g.contours:
            for pt in c.points:
                pt.x, pt.y = t.transformPoint((pt.x, pt.y))
        for a in g.anchors:
            a.x, a.y = t.transformPoint((a.x, a.y))
        for comp in g.components:
            tr = comp.transformation
            comp.transformation = (tr[0], tr[1], tr[2], tr[3], tr[4] * s, tr[5] * s)
        if g.width:
            g.width = (g.width + 2 * r) * s
    for k in list(font.kerning.keys()):
        font.kerning[k] = font.kerning[k] * s


def round_all(font) -> None:
    for g in font:
        for c in g.contours:
            for pt in c.points:
                pt.x, pt.y = round(pt.x), round(pt.y)
        for a in g.anchors:
            a.x, a.y = round(a.x), round(a.y)
        for comp in g.components:
            tr = comp.transformation
            comp.transformation = (tr[0], tr[1], tr[2], tr[3], round(tr[4]), round(tr[5]))
        g.width = round(g.width)
    for k in list(font.kerning.keys()):
        font.kerning[k] = round(font.kerning[k])


def set_info(font, cfg, r: float, s: float) -> None:
    up = lambda y: round((y + r) * s)  # noqa: E731
    # Alturas visibles (contorno engrosado)
    x_height = up(font.info.xHeight + r)
    cap_height = up(700 + r)
    ascender = up(cfg["ascender"] + r)
    descender = up(cfg["descender"] - r)

    # Métricas verticales (esquema de Google Fonts): typo = hhea = win, lineGap = 0,
    # cubriendo el glifo más alto (Á) y el más bajo, con interlineado mínimo de 1,2 em.
    ymax = round(max(g.getBounds(font).yMax for g in font if g.getBounds(font)))
    ymin = round(min(g.getBounds(font).yMin for g in font if g.getBounds(font)))
    line_asc = max(ascender, ymax)
    line_desc = min(descender, ymin, line_asc - 1200)

    new = ufoLib2.objects.Info(
        familyName="Diddo Sans",
        styleName="Bold",
        styleMapFamilyName="Diddo Sans",
        styleMapStyleName="bold",
        versionMajor=0,
        versionMinor=101,
        copyright=(
            "Copyright 2011 The Montserrat Project Authors "
            "(https://github.com/JulietaUla/Montserrat); "
            "Copyright 2024 The Montserrat.Git Project Authors "
            "(https://github.com/JulietaUla/Montserrat.git); "
            "Copyright 2026 The Diddo Sans Project Authors"
        ),
        openTypeNameLicense=(
            "This Font Software is licensed under the SIL Open Font License, Version 1.1. "
            "This license is available with a FAQ at: https://openfontlicense.org"
        ),
        openTypeNameLicenseURL="https://openfontlicense.org",
        openTypeNameDescription="Diddo Sans Bold, derivada de Montserrat Regular con la transformación Diddo.",
        unitsPerEm=1000,
        xHeight=x_height,
        capHeight=cap_height,
        ascender=ascender,
        descender=descender,
        italicAngle=0,
        openTypeOS2WeightClass=700,
        openTypeOS2WidthClass=5,
        openTypeOS2Selection=[7],  # USE_TYPO_METRICS
        openTypeOS2Type=[],
        openTypeOS2TypoAscender=line_asc,
        openTypeOS2TypoDescender=line_desc,
        openTypeOS2TypoLineGap=0,
        openTypeHheaAscender=line_asc,
        openTypeHheaDescender=line_desc,
        openTypeHheaLineGap=0,
        openTypeOS2WinAscent=line_asc,
        openTypeOS2WinDescent=-line_desc,
        openTypeHeadFlags=[0, 1, 3],
        openTypeOS2VendorID="DIDO",
        postscriptFontName="DiddoSans-Bold",
        postscriptFullName="Diddo Sans Bold",
        postscriptUnderlinePosition=-round(100 * s),
        postscriptUnderlineThickness=round(95 * s),
        postscriptIsFixedPitch=False,
    )
    font.info = new


# --------------------------------------------------------------------------

def load_config(path: str | None) -> dict:
    cfg = json.loads(json.dumps(DEFAULTS))
    if path:
        cfg.update(json.loads(Path(path).read_text()))
    return cfg


def diddoize(cfg: dict, out: Path, upstream: Path = UPSTREAM_UFO, verbose: bool = True):
    font = ufoLib2.Font.open(upstream)
    keep = required_glyphs(font)
    subset(font, keep)

    apply_skeleton(font, cfg)
    # La a.ss01 ya se ha copiado en la a; no se exporta.
    del font["a.ss01"]
    font.glyphOrder = [n for n in font.glyphOrder if n != "a.ss01"]
    for gname in list(font.groups):
        font.groups[gname] = [m for m in font.groups[gname] if m != "a.ss01"]

    notes, skeletons = fixes.pre_embolden(font, cfg)
    # Después de las correcciones previas, que localizan los contornos por su índice.
    rounded = round_all_terminals(font, cfg) if cfg["round_terminals"] else {}
    width = cfg["stroke"]
    r = width / 2
    changed = embolden_all(font, width)
    notes.update(fixes.post_embolden(font, cfg, skeletons))
    s = cfg["cap_height"] / (700 + 2 * r)
    rescale(font, r, s)
    set_info(font, cfg, r, s)
    round_all(font)

    font.lib["com.diddo.config"] = json.dumps(cfg, ensure_ascii=False)
    font.lib["public.glyphOrder"] = font.glyphOrder
    out.parent.mkdir(parents=True, exist_ok=True)
    font.save(out, overwrite=True)
    if verbose:
        print(f"{out}: {len(font)} glifos, escala {s:.4f}")
        if rounded:
            print(f"Extremos redondeados: {sum(rounded.values())} en {len(rounded)} glifos")
        if changed:
            print("Cambian de nº de contornos al engrosar (revisar a mano):")
            for n, (a, b) in sorted(changed.items()):
                print(f"  {n}: {a} → {b}" + (f"  (corregido: {notes[n]})" if n in notes else ""))
        for n, note in sorted(notes.items()):
            if n not in changed:
                print(f"  corrección {n}: {note}")
    return font, changed


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", help="JSON con parámetros que sustituyen a DEFAULTS")
    ap.add_argument("--set", action="append", default=[], help="parámetro=valor_json (p. ej. stroke=105)")
    ap.add_argument("--out", default=str(ROOT / "sources" / "DiddoSans-Bold.ufo"))
    ap.add_argument("--upstream", default=str(UPSTREAM_UFO))
    args = ap.parse_args()
    cfg = load_config(args.config)
    for kv in args.set:
        k, v = kv.split("=", 1)
        cfg[k] = json.loads(v)
    diddoize(cfg, Path(args.out), Path(args.upstream))


if __name__ == "__main__":
    main()
