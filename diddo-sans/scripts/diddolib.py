"""Utilidades compartidas de Diddo Sans.

- Lectura de los SVG de referencia (con transformaciones y grosor de trazo).
- Acceso a Montserrat (instancias de la fuente variable fijada en sources/upstream/).
- Engrosado "Diddo": relleno ∪ trazo redondo, con skia-pathops.
- Utilidades geométricas (cortes horizontales, muestreo de contornos) y de dibujo.

Convención: todas las funciones devuelven trazados en coordenadas con el eje y
hacia arriba (como en una fuente). Los SVG se voltean al leerlos.
"""

from __future__ import annotations

import math
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path as FsPath

import pathops
from fontTools.pens.basePen import BasePen
from fontTools.pens.transformPen import TransformPen
from fontTools.svgLib.path import parse_path
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = FsPath(__file__).resolve().parent.parent
UPSTREAM = ROOT / "sources" / "upstream"
MONTSERRAT_VF = UPSTREAM / "Montserrat[wght].ttf"
REFERENCE = ROOT / "reference"

# Trazo de referencia del logo "diddo", en UPM (ver docs/analisis-logos.md §2).
STROKE_DIDDO = 95.0
# Trazo del logo "pad", en UPM.
STROKE_PAD = 105.0

SVG_NS = "{http://www.w3.org/2000/svg}"


# ---------------------------------------------------------------------------
# Trazados
# ---------------------------------------------------------------------------

def new_path() -> pathops.Path:
    return pathops.Path()


def draw_to_path(draw_fn, transform=None) -> pathops.Path:
    """Ejecuta draw_fn(pen) sobre un pen de pathops, con transformación opcional."""
    path = pathops.Path()
    pen = path.getPen()
    if transform is not None:
        pen = TransformPen(pen, transform)
    draw_fn(pen)
    return path


def transformed(path: pathops.Path, t) -> pathops.Path:
    """Copia de `path` transformada por la matriz afín t = (a, b, c, d, e, f)."""
    return draw_to_path(path.draw, t)


def simplify(path: pathops.Path) -> pathops.Path:
    out = pathops.Path()
    out.addPath(path)
    out.simplify(fix_winding=True, keep_starting_points=False)
    return out


def union(*paths: pathops.Path) -> pathops.Path:
    result = pathops.Path()
    for p in paths:
        result = pathops.op(result, p, pathops.PathOp.UNION, fix_winding=True)
    return result


def difference(a: pathops.Path, b: pathops.Path) -> pathops.Path:
    return pathops.op(a, b, pathops.PathOp.DIFFERENCE, fix_winding=True)


def intersection(a: pathops.Path, b: pathops.Path) -> pathops.Path:
    return pathops.op(a, b, pathops.PathOp.INTERSECTION, fix_winding=True)


def rect(x0, y0, x1, y1) -> pathops.Path:
    p = pathops.Path()
    p.moveTo(x0, y0)
    p.lineTo(x1, y0)
    p.lineTo(x1, y1)
    p.lineTo(x0, y1)
    p.close()
    return p


def stroke_outline(path: pathops.Path, width: float) -> pathops.Path:
    """Contorno del trazo redondo (uniones y extremos redondos) de `path`."""
    s = pathops.Path()
    s.addPath(path)
    s.stroke(width, pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 4)
    s.convertConicsToQuads(0.25)
    return simplify(s)


def thicken(path: pathops.Path, width: float = STROKE_DIDDO) -> pathops.Path:
    """La "transformación Diddo" básica: relleno ∪ trazo redondo de grosor `width`.

    Equivale a pintar el relleno y después un trazo con `stroke-linejoin:round` y
    `stroke-linecap:round`, como en los logos (paint-order: fill stroke).
    """
    if width <= 0:
        return simplify(path)
    return union(simplify(path), stroke_outline(path, width))


def bounds(path: pathops.Path):
    """(xMin, yMin, xMax, yMax) exactos (no de puntos de control)."""
    return path.bounds


def n_contours(path: pathops.Path) -> int:
    return len(list(path.contours))


# ---------------------------------------------------------------------------
# Aplanado y medidas
# ---------------------------------------------------------------------------

class _FlattenPen(BasePen):
    """Convierte curvas en polilíneas (una lista de puntos por contorno)."""

    def __init__(self, steps: int = 24):
        super().__init__(None)
        self.steps = steps
        self.contours: list[list[tuple[float, float]]] = []
        self._cur: list[tuple[float, float]] | None = None

    def _moveTo(self, pt):
        self._cur = [pt]
        self.contours.append(self._cur)

    def _lineTo(self, pt):
        self._cur.append(pt)

    def _curveToOne(self, p1, p2, p3):
        p0 = self._cur[-1]
        for i in range(1, self.steps + 1):
            t = i / self.steps
            mt = 1 - t
            x = mt**3 * p0[0] + 3 * mt**2 * t * p1[0] + 3 * mt * t**2 * p2[0] + t**3 * p3[0]
            y = mt**3 * p0[1] + 3 * mt**2 * t * p1[1] + 3 * mt * t**2 * p2[1] + t**3 * p3[1]
            self._cur.append((x, y))

    def _qCurveToOne(self, p1, p2):
        p0 = self._cur[-1]
        for i in range(1, self.steps + 1):
            t = i / self.steps
            mt = 1 - t
            x = mt**2 * p0[0] + 2 * mt * t * p1[0] + t**2 * p2[0]
            y = mt**2 * p0[1] + 2 * mt * t * p1[1] + t**2 * p2[1]
            self._cur.append((x, y))

    def _closePath(self):
        if self._cur and self._cur[0] != self._cur[-1]:
            self._cur.append(self._cur[0])
        self._cur = None

    _endPath = _closePath


def flatten(path: pathops.Path, steps: int = 24) -> list[list[tuple[float, float]]]:
    pen = _FlattenPen(steps)
    path.draw(pen)
    return [c for c in pen.contours if len(c) > 2]


def hslice(path: pathops.Path, y: float) -> list[tuple[float, float]]:
    """Intervalos [x0, x1] rellenos en la horizontal y (regla nonzero ya resuelta)."""
    xs = []
    for contour in flatten(simplify(path), 48):
        for (x0, y0), (x1, y1) in zip(contour, contour[1:]):
            if (y0 <= y < y1) or (y1 <= y < y0):
                xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
    xs.sort()
    return [(xs[i], xs[i + 1]) for i in range(0, len(xs) - 1, 2)]


def resample(contour, n: int = 400):
    """Remuestrea una polilínea cerrada en n puntos equidistantes."""
    seg = [math.dist(a, b) for a, b in zip(contour, contour[1:])]
    total = sum(seg)
    out, acc, i = [], 0.0, 0
    for k in range(n):
        target = total * k / n
        while i < len(seg) - 1 and acc + seg[i] < target:
            acc += seg[i]
            i += 1
        t = 0 if seg[i] == 0 else (target - acc) / seg[i]
        (x0, y0), (x1, y1) = contour[i], contour[i + 1]
        out.append((x0 + t * (x1 - x0), y0 + t * (y1 - y0)))
    return out


def hausdorff(a, b) -> float:
    def one(p, q):
        return max(min(math.dist(x, y) for y in q) for x in p)

    return max(one(a, b), one(b, a))


# ---------------------------------------------------------------------------
# SVG
# ---------------------------------------------------------------------------

def _parse_transform(s: str | None):
    m = (1, 0, 0, 1, 0, 0)
    if not s:
        return m
    for name, args in re.findall(r"(\w+)\s*\(([^)]*)\)", s):
        v = [float(x) for x in re.split(r"[\s,]+", args.strip()) if x]
        if name == "matrix":
            t = tuple(v)
        elif name == "translate":
            t = (1, 0, 0, 1, v[0], v[1] if len(v) > 1 else 0)
        elif name == "scale":
            t = (v[0], 0, 0, v[1] if len(v) > 1 else v[0], 0, 0)
        else:
            raise ValueError(f"transformación no soportada: {name}")
        m = _mul(m, t)
    return m


def _mul(m, n):
    a, b, c, d, e, f = m
    a2, b2, c2, d2, e2, f2 = n
    return (
        a * a2 + c * b2,
        b * a2 + d * b2,
        a * c2 + c * d2,
        b * c2 + d * d2,
        a * e2 + c * f2 + e,
        b * e2 + d * f2 + f,
    )


def _style(el) -> dict:
    out = {k: v for k, v in el.attrib.items()}
    for item in (el.get("style") or "").split(";"):
        if ":" in item:
            k, v = item.split(":", 1)
            out[k.strip()] = v.strip()
    return out


@dataclass
class SvgShape:
    """Un <path> del SVG ya transformado a coordenadas del lienzo (y hacia arriba)."""

    path: pathops.Path       # relleno (o el trazado abierto si fill = none)
    stroke_width: float      # grosor efectivo en unidades del lienzo
    filled: bool
    source_d: str

    @property
    def x_min(self):
        return self.path.bounds[0]


def read_svg(file: FsPath) -> list[SvgShape]:
    """Lee los <path> de un SVG con su transformación acumulada y su trazo efectivo."""
    tree = ET.parse(file)
    shapes: list[SvgShape] = []

    def walk(el, ctm, inherited):
        style = {**inherited, **{k: v for k, v in _style(el).items()
                                 if k in ("fill", "stroke", "stroke-width")}}
        ctm = _mul(ctm, _parse_transform(el.get("transform")))
        if el.tag == SVG_NS + "path":
            # Volteo vertical: y_fuente = -y_svg.
            t = _mul((1, 0, 0, -1, 0, 0), ctm)
            path = pathops.Path()
            parse_path(el.get("d"), TransformPen(path.getPen(), t))
            scale = math.sqrt(abs(ctm[0] * ctm[3] - ctm[1] * ctm[2]))
            shapes.append(SvgShape(
                path=path,
                stroke_width=float(style.get("stroke-width", 0)) * scale,
                filled=style.get("fill", "black") != "none",
                source_d=el.get("d"),
            ))
        for child in el:
            walk(child, ctm, style)

    walk(tree.getroot(), (1, 0, 0, 1, 0, 0), {})
    return shapes


# ---------------------------------------------------------------------------
# Montserrat
# ---------------------------------------------------------------------------

@lru_cache(maxsize=None)
def montserrat(wght: float = 400) -> TTFont:
    """Instancia estática de la Montserrat variable fijada (sin hinting)."""
    if not MONTSERRAT_VF.exists():
        raise SystemExit(
            f"Falta {MONTSERRAT_VF.relative_to(ROOT)}. Ejecuta antes: make upstream"
        )
    vf = TTFont(MONTSERRAT_VF)
    return instantiateVariableFont(vf, {"wght": wght}, inplace=False)


def glyph_path(font: TTFont, char_or_name: str) -> pathops.Path:
    """Contorno de un glifo (por carácter o por nombre de glifo)."""
    name = char_or_name
    if len(char_or_name) == 1:
        name = font.getBestCmap()[ord(char_or_name)]
    gs = font.getGlyphSet()
    path = pathops.Path()
    gs[name].draw(path.getPen(glyphSet=gs))
    return simplify(path)


def glyph_advance(font: TTFont, char_or_name: str) -> int:
    name = char_or_name
    if len(char_or_name) == 1:
        name = font.getBestCmap()[ord(char_or_name)]
    return font["hmtx"][name][0]


# ---------------------------------------------------------------------------
# Salida: SVG y PNG
# ---------------------------------------------------------------------------

def svg_d(path: pathops.Path, ndigits: int = 1) -> str:
    """Datos 'd' de SVG (en coordenadas y-arriba; quien lo use debe voltear)."""
    from fontTools.pens.svgPathPen import SVGPathPen

    pen = SVGPathPen(None, ntos=lambda v: f"{round(v, ndigits):g}")
    path.draw(pen)
    return pen.getCommands()


def render_png(items, file: FsPath, *, height: int = 300, margin: int = 20,
               y_range=(-300, 1000), x_range=None, guides=(), labels=()):
    """Dibuja trazados en un PNG con antialias (freetype).

    items: lista de (path, (r, g, b, a)) en UPM; se pintan en orden.
    guides: lista de valores y (UPM) para líneas guía horizontales.
    labels: lista de (x_upm, y_upm, texto).
    """
    from PIL import Image, ImageDraw, ImageFont
    from fontTools.pens.freetypePen import FreeTypePen

    if x_range is None:
        xs = [b for p, _ in items for b in (p.bounds[0], p.bounds[2]) if list(p.contours)]
        x_range = (min(xs) - 60, max(xs) + 60)
    y0, y1 = y_range
    s = (height - 2 * margin) / (y1 - y0)
    width = int((x_range[1] - x_range[0]) * s + 2 * margin)
    img = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    for gy in guides:
        py = height - margin - (gy - y0) * s
        draw.line([(0, py), (width, py)], fill=(200, 205, 215, 255), width=1)
    tx = margin - x_range[0] * s
    ty = margin - y0 * s
    for path, color in items:
        if not list(path.contours):
            continue
        pen = FreeTypePen(None)
        path.draw(pen)
        mask = pen.image(width=width, height=height,
                         transform=(s, 0, 0, s, tx, ty), contain=False, evenOdd=False)
        alpha = mask.getchannel("A")
        layer = Image.new("RGBA", (width, height), color[:3] + (0,))
        layer.putalpha(alpha.point(lambda v: v * color[3] // 255))
        img = Image.alpha_composite(img, layer)
    if labels:
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", 14)
        except OSError:
            font = ImageFont.load_default()
        for lx, ly, text in labels:
            draw.text((tx + lx * s, height - (ty + ly * s)), text, fill=(60, 60, 70, 255), font=font)
    file.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(file, optimize=True)
    return file
