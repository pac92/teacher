#!/usr/bin/env python3
"""Fase 2 · Pruebas visuales para decidir el brief de diseño.

Genera un PROTOTIPO rápido de Diddo Sans a partir de Montserrat 400 (instancia de la
fuente variable) y compone muestras para comparar las opciones de docs/design-brief.md.
No es la fuente: el ahusado se hace por geometría (unión con un trapecio) y los
diacríticos se separan de forma provisional. La transformación definitiva irá en
scripts/diddoize.py (fase 4), sobre las fuentes .glyphs.

Salidas en proofs/brief/:
    1-peso.png          trazo 95 frente a 105
    2-ahusado.png       reglas de ahusado A, B y C
    3-extensiones.png   ascendentes/descendentes de Montserrat frente a las del logo
    4-mayusculas.png    mayúsculas sin ahusar y ahusadas
    5-superposicion.png prototipo sobre el logo, con IoU por letra
    resumen.json        IoU y datos de las muestras

Uso:  python scripts/proof_brief.py
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, replace

import pathops

import diddolib as dl

OUT = dl.ROOT / "proofs" / "brief"
MEDIDAS = dl.REFERENCE / "normalized" / "medidas.json"

XH = 525.5          # altura x de Montserrat 400 (parte plana)
STEM = 71.0         # asta de minúscula de Montserrat 400
BLUE = (74, 103, 181, 255)    # #4a67b5, el azul del logo
GHOST = (74, 103, 181, 70)
RED = (214, 69, 65, 150)

# Ahusado medido en el logo (reference/normalized/medidas.md): el ancho del relleno
# depende solo de la altura: 86 UPM en la altura x y +0,07 UPM por cada UPM hacia abajo
# (≈ 4°). El borde que da al cuenco o a la letra queda vertical; se mueve el exterior.
TAPER_W0 = 86.0
TAPER_K = 0.07

# Letras con una sola asta y sin nada a los lados: el logo (la i) mueve el borde derecho.
SINGLE = set("ijlıȷ")
# Astas descendentes: en la p del logo (la d girada) el ancho crece hacia la altura x.
DESCENDING = set("pq")

LOGO_LETTERS = set("dbpqaijl")   # regla B: letras del logo y sus parientes directos


@dataclass(frozen=True)
class Variant:
    name: str
    stroke: float = dl.STROKE_DIDDO
    taper: str = "C"            # "A" sin ahusado · "B" letras del logo · "C" todas
    taper_caps: bool = False
    long_extenders: bool = False
    one_story_a: bool = True
    extra: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Esqueleto
# ---------------------------------------------------------------------------

def map_points(path: pathops.Path, fn) -> pathops.Path:
    """Aplica fn(x, y) -> (x, y) a todos los puntos (también los de control)."""
    out = pathops.Path()
    pen = out.getPen()
    for verb, pts in path.segments:
        pts = [fn(*p) for p in pts]
        if verb == "moveTo":
            pen.moveTo(pts[0])
        elif verb == "lineTo":
            pen.lineTo(pts[0])
        elif verb == "qCurveTo":
            pen.qCurveTo(*pts)
        elif verb == "curveTo":
            pen.curveTo(*pts)
        elif verb == "closePath":
            pen.closePath()
        elif verb == "endPath":
            pen.endPath()
    return out


def stretch_extenders(path, asc_from, asc_to, desc_from, desc_to, margin=12):
    """Alarga ascendentes y descendentes sin tocar la franja de la altura x."""
    top = XH + margin
    fa = (asc_to - top) / (asc_from - top)
    fd = (desc_to + margin) / (desc_from + margin)

    def fn(x, y):
        if y > top:
            return x, top + (y - top) * fa
        if y < -margin:
            return x, -margin + (y + margin) * fd
        return x, y

    return map_points(path, fn)


def vertical_edges(path, min_len=120):
    """Segmentos rectos verticales: (x, y0, y1)."""
    edges = []
    for contour in path.contours:
        prev = None
        first = None
        for verb, pts in contour.segments:
            if verb == "moveTo":
                prev = first = pts[0]
                continue
            if verb == "closePath":
                cur = first
            else:
                cur = pts[-1]
            if verb in ("lineTo", "closePath") and prev is not None:
                if abs(cur[0] - prev[0]) < 0.6 and abs(cur[1] - prev[1]) >= min_len:
                    edges.append((round((cur[0] + prev[0]) / 2, 1),
                                  min(cur[1], prev[1]), max(cur[1], prev[1])))
            prev = cur
    return edges


def find_stems(path, stem_w):
    """Empareja bordes verticales en astas: (x_izq, x_der, y0, y1)."""
    edges = vertical_edges(path)
    stems = []
    for xl, l0, l1 in edges:
        for xr, r0, r1 in edges:
            if not (0.8 * stem_w <= xr - xl <= 1.2 * stem_w):
                continue
            overlap = min(l1, r1) - max(l0, r0)
            if overlap < 100:
                continue
            # El rango del asta es el del borde más largo (el exterior suele ser entero).
            y0, y1 = (l0, l1) if l1 - l0 >= r1 - r0 else (r0, r1)
            stems.append((overlap, (xl, xr, y0, y1)))
    # Un borde interior partido por un arco (n, h, m…) da varias parejas para la
    # misma asta: se queda la de mayor solape y se descartan las que comparten borde.
    chosen = []
    for _, s in sorted(stems, key=lambda t: -t[0]):
        if all(abs(s[0] - c[0]) > 5 and abs(s[1] - c[1]) > 5 for c in chosen):
            chosen.append(s)
    return sorted(chosen)


def taper_glyph(path, char, stem_w=STEM, xh=XH, round_ends=True):
    """Sustituye las astas verticales rectas por astas ahusadas (regla del logo)."""
    xmin, _, xmax, _ = path.bounds
    stems = find_stems(path, stem_w)
    if not stems:
        return path
    descending = char in DESCENDING
    pieces = [path]
    for xl, xr, y0, y1 in stems:
        if char in SINGLE or char == "I":
            move = "right"
        elif abs(xl - xmin) < 2:
            move = "left"
        elif abs(xr - xmax) < 2:
            move = "right"
        else:
            continue  # asta central (m, M…): sin ahusar

        # El extremo ancho tiene que ser libre (la base, o la altura x en p/q); si acaba
        # en una curva (u, j) el trapecio dejaría un escalón: esa asta no se ahúsa.
        if descending:
            if y1 < xh - 1:
                continue
        elif abs(y0) > 1:
            continue  # no llega a la base: acaba en curva (u) o en gancho (j)
        top_is_joint = not descending and y1 < xh - 1   # pata derecha de h, m, n

        def width(y):
            if descending:
                # d girada 180° alrededor del centro del cuenco.
                return TAPER_W0 + TAPER_K * y
            if top_is_joint:
                # Arranca con el ancho original donde se une al arco.
                return stem_w + TAPER_K * (y1 - y)
            return TAPER_W0 + TAPER_K * (xh - y)

        # «Asta Diddo»: trapecio con extremos redondos donde el asta acaba libre
        # (como la i del logo, y el pie y el remate de la d). Sustituye al asta
        # rectangular de Montserrat.
        free_bottom = round_ends and (y0 <= -150 if descending else y0 <= 1)
        free_top = round_ends and y1 >= xh - 1
        sign = 1 if move == "right" else -1
        x_fixed = xl if move == "right" else xr
        # Se quita el asta original con 1 UPM de margen: con bordes colineales, pathops
        # deja espigas de ancho cero que el engrosado convertiría en rebabas. Lo que
        # cuelga del asta por dentro (cuenco, arco) y cae en ese margen se repone, y el
        # borde fijo de la nueva asta entra 0,5 UPM para solaparse con ello.
        capsule = stem_capsule(x_fixed - 0.5 * sign, sign, y0, y1,
                               lambda y: width(y) + 0.5, free_bottom, free_top)
        stem_box = dl.rect(xl - 1, y0 - 1, xr + 1, y1 + 1)
        band = dl.rect(min(x_fixed - 0.3 * sign, x_fixed - 1.5 * sign), y0 - 1,
                       max(x_fixed - 0.3 * sign, x_fixed - 1.5 * sign), y1 + 1)
        capsule = dl.union(capsule, dl.intersection(path, band))
        pieces = [dl.union(dl.difference(pieces[0], stem_box), capsule)]
    return pieces[0]


def circle(cx, cy, r):
    k = 0.5523 * r
    c = pathops.Path()
    c.moveTo(cx + r, cy)
    c.cubicTo(cx + r, cy + k, cx + k, cy + r, cx, cy + r)
    c.cubicTo(cx - k, cy + r, cx - r, cy + k, cx - r, cy)
    c.cubicTo(cx - r, cy - k, cx - k, cy - r, cx, cy - r)
    c.cubicTo(cx + k, cy - r, cx + r, cy - k, cx + r, cy)
    c.close()
    return c


def stem_capsule(x_fixed, sign, y0, y1, width, round_bottom, round_top):
    """Asta con un borde vertical en x_fixed y el otro a `width(y)` hacia `sign`."""
    yb, yt = y0, y1
    parts = []
    if round_bottom:
        r = width(y0 + width(y0) / 2) / 2
        yb = y0 + r
        parts.append(circle(x_fixed + sign * r, yb, r))
    if round_top:
        r = width(y1 - width(y1) / 2) / 2
        yt = y1 - r
        parts.append(circle(x_fixed + sign * r, yt, r))
    trap = pathops.Path()
    trap.moveTo(x_fixed, yb)
    trap.lineTo(x_fixed + sign * width(yb), yb)
    trap.lineTo(x_fixed + sign * width(yt), yt)
    trap.lineTo(x_fixed, yt)
    trap.close()
    return dl.union(trap, *parts)


def one_story_a(font, v: Variant):
    """a de un piso: la d (ya ahusada) recortada a la altura x, como en el logo."""
    d = skeleton(font, "d", replace(v, long_extenders=False))
    return dl.intersection(d, dl.rect(-1e4, -1e4, 1e4, XH))


# ---------------------------------------------------------------------------
# Glifos
# ---------------------------------------------------------------------------

def skeleton(font, char, v: Variant):
    """Esqueleto (antes de engrosar) de un carácter sin diacríticos."""
    if char == "a" and v.one_story_a:
        return one_story_a(font, v)
    path = dl.glyph_path(font, char)
    if v.long_extenders and char.islower():
        path = stretch_extenders(path, *v.extra.get("ext", (742, 857, -194, -326)))
        if char in "ij":
            path = fix_dot(path)
    tapered = (v.taper == "C" and char.islower()) or \
              (v.taper == "B" and char in LOGO_LETTERS) or \
              (v.taper_caps and char.isupper())
    if tapered:
        path = taper_glyph(path, char, 74.0 if char.isupper() else STEM,
                           round_ends=char.islower() or char == "I")
    return path


def fix_dot(path):
    """Tras alargar, el punto de la i/j sale ovalado: se rehace redondo como en el logo
    (centro 730, diámetro de relleno 125; ver medidas.md)."""
    stem = dl.intersection(path, dl.rect(-1e4, -1e4, 1e4, XH + 40))
    x0, _, x1, _ = stem.bounds
    return dl.union(stem, circle((x0 + x1) / 2, 730.0, 62.5))


def components(font, char):
    """[(nombre, dx, dy)] si el glifo es compuesto; None si no."""
    name = font.getBestCmap()[ord(char)]
    g = font["glyf"][name]
    if not g.isComposite():
        return None
    return [(c.glyphName, c.x, c.y) for c in g.components]


def glyph(font, char, v: Variant):
    """(contorno final engrosado, avance). Diacríticos separados de forma provisional."""
    comps = components(font, char) if char not in "ij" else None
    if comps:
        base_name = comps[0][0]
        base_char = next((chr(u) for u, n in font.getBestCmap().items() if n == base_name), None)
        base = dl.thicken(skeleton(font, base_char, v), v.stroke)
        marks = pathops.Path()
        for name, dx, dy in comps[1:]:
            mark = dl.transformed(dl.glyph_path(font, name), (1, 0, 0, 1, dx, dy))
            # Provisional: el engrosado come 2·r del hueco; se sube la marca lo mismo
            # y un poco más, para que no se funda.
            lift = 0.85 * v.stroke
            marks = dl.union(marks, dl.transformed(dl.thicken(mark, v.stroke), (1, 0, 0, 1, 0, lift)))
        final = dl.union(base, marks)
        ref = base_char
    else:
        final = dl.thicken(skeleton(font, char, v), v.stroke)
        ref = char
    orig = dl.glyph_path(font, ref)
    adv = dl.glyph_advance(font, ref)
    ob, nb = orig.bounds, final.bounds
    lsb, rsb = ob[0], adv - ob[2]
    dx = lsb - nb[0]
    return dl.transformed(final, (1, 0, 0, 1, dx, 0)), lsb + (nb[2] - nb[0]) + rsb


def typeset(font, text, v: Variant, *, tracking=0.0):
    """Compone una línea (sin kerning). Devuelve (trazado, anchura)."""
    x = 0.0
    out = pathops.Path()
    cache = {}
    for ch in text:
        if ch == " ":
            x += dl.glyph_advance(font, " ") + v.stroke * 0.6
            continue
        if ch not in cache:
            cache[ch] = glyph(font, ch, v)
        g, adv = cache[ch]
        out.addPath(dl.transformed(g, (1, 0, 0, 1, x, 0)))
        x += adv + tracking
    return out, x


def block(font, rows, *, line_h=1350):
    """rows: lista de (texto, Variant, etiqueta). Devuelve (items, etiquetas)."""
    items, labels = [], []
    for i, (text, v, label) in enumerate(rows):
        path, _ = typeset(font, text, v)
        y = -i * line_h
        items.append((dl.transformed(path, (1, 0, 0, 1, 0, y)), BLUE))
        labels.append((0, y + 1060, label))
    return items, labels


def save_block(name, rows, font, *, line_h=1350, px_per_line=210):
    items, labels = block(font, rows, line_h=line_h)
    n = len(rows)
    guides = []
    for i in range(n):
        guides += [-i * line_h, -i * line_h + XH]
    top = 1150
    bottom = -(n - 1) * line_h - 450
    height = int(px_per_line * (top - bottom) / line_h)
    return dl.render_png(items, OUT / name, height=height, y_range=(bottom, top),
                         guides=guides, labels=labels)


# ---------------------------------------------------------------------------
# Superposición con el logo
# ---------------------------------------------------------------------------

def overlay(font):
    """Compone d, i, o, p, a con la variante del logo y la compara con las letras reales."""
    from xml.etree import ElementTree as ET

    v = Variant("logo", taper="C", long_extenders=True)
    results = {}
    items = []
    x_off = 0.0
    for key, letters in (("diddo", ["i", "d", "d2", "o"]), ("pad", ["p", "a", "d"])):
        tree = ET.parse(dl.REFERENCE / "normalized" / f"{key}.svg")
        groups = {g.get("id"): g for g in tree.getroot().iter(dl.SVG_NS + "g") if g.get("id")}
        for name in letters:
            if name == "i":
                logo = dl.union(_svg_final(groups["i_punto"]), _svg_final(groups["i_asta"]))
            else:
                logo = _svg_final(groups[name])
            proto, _ = glyph(font, name[0], replace(v, stroke=float(groups[name if name != "i" else "i_asta"]
                                                                    .get("data-trazo-upm"))))
            # Alinear por el borde izquierdo y la línea base.
            dx = logo.bounds[0] - proto.bounds[0]
            proto = dl.transformed(proto, (1, 0, 0, 1, dx, 0))
            inter = dl.intersection(logo, proto).area
            uni = dl.union(logo, proto).area
            results[f"{key}:{name}"] = round(inter / uni, 4)
            items.append((dl.transformed(logo, (1, 0, 0, 1, x_off, 0)), GHOST))
            items.append((dl.transformed(proto, (1, 0, 0, 1, x_off, 0)), RED))
        x_off += 3300
    dl.render_png(items, OUT / "5-superposicion.png", height=420, y_range=(-450, 1000),
                  guides=(0, XH), labels=[(0, 960, "diddo"), (3300, 960, "pad")])
    return results


def _svg_final(group):
    from fontTools.svgLib.path import parse_path

    d = next(p.get("d") for p in group if p.get("class") == "final")
    path = pathops.Path()
    parse_path(d, path.getPen())
    return dl.simplify(path)


# ---------------------------------------------------------------------------

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    f = dl.montserrat(400)
    sample = "diddo pad hamburguesa"
    lower = "abcdefghijklmn"
    lower2 = "ñopqrstuvwxyz"
    words = "el kiwi y la piña"

    base = Variant("C")
    A = replace(base, name="A", taper="A")
    B = replace(base, name="B", taper="B")

    save_block("1-peso.png", [
        (sample, base, "trazo 95 (diddo)"),
        (sample, replace(base, stroke=dl.STROKE_PAD), "trazo 105 (pad)"),
    ], f)

    save_block("2-ahusado.png", [
        (lower, A, "A · sin ahusado"),
        (lower, B, "B · solo d b p q a i j l"),
        (lower, base, "C · todas las astas"),
        (lower2, A, "A"),
        (lower2, B, "B"),
        (lower2, base, "C"),
    ], f)

    save_block("3-extensiones.png", [
        ("diddo bly pq", base, "ascendentes y descendentes de Montserrat (742 / -194)"),
        ("diddo bly pq", replace(base, long_extenders=True), "las del logo (857 / -326)"),
    ], f, line_h=1500)

    save_block("4-mayusculas.png", [
        ("DIDDO PAD HLKN", base, "mayúsculas sin ahusar"),
        ("DIDDO PAD HLKN", replace(base, taper_caps=True), "mayúsculas ahusadas"),
        ("Diddo Pad 2026", base, "texto mixto"),
        (words, base, "diacríticos (separación provisional)"),
    ], f)

    iou = overlay(f)
    (OUT / "resumen.json").write_text(json.dumps({"iou_superposicion": iou}, indent=2) + "\n")
    for k, val in iou.items():
        print(f"IoU {k:10s} {val:.3f}")


if __name__ == "__main__":
    main()
