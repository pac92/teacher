"""Utilidades comunes de Diddo Sans.

- Lectura de los SVG de referencia como trazados de skia-pathops.
- Engrosado "Diddo": relleno ∪ trazo redondo (lo mismo que hace Inkscape con
  `paint-order: markers fill stroke`, `stroke-linejoin/linecap: round`).
- Conversión entre trazados de pathops y glifos UFO.
- Renderizado a imagen (Pillow) para pruebas visuales y de superposición.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path as FsPath

import pathops
from fontTools.misc.transform import Transform
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.svgLib.path import parse_path

ROOT = FsPath(__file__).resolve().parent.parent

SVG_NS = "{http://www.w3.org/2000/svg}"


# --------------------------------------------------------------------------
# Lectura de SVG
# --------------------------------------------------------------------------

@dataclass
class SvgShape:
    """Un <path> del SVG ya transformado a coordenadas del lienzo (y hacia abajo)."""

    id: str | None
    path: pathops.Path
    fill: bool
    stroke_width: float  # en unidades de lienzo, ya multiplicado por la escala
    linecap: str
    linejoin: str


def _style_dict(el) -> dict[str, str]:
    d = {}
    for k in ("fill", "stroke", "stroke-width", "stroke-linecap", "stroke-linejoin"):
        if el.get(k) is not None:
            d[k] = el.get(k)
    style = el.get("style")
    if style:
        for item in style.split(";"):
            if ":" in item:
                k, v = item.split(":", 1)
                d[k.strip()] = v.strip()
    return d


def _parse_transform(s: str | None) -> Transform:
    t = Transform()
    if not s:
        return t
    for name, args in re.findall(r"(\w+)\s*\(([^)]*)\)", s):
        v = [float(x) for x in re.split(r"[\s,]+", args.strip()) if x]
        if name == "translate":
            t = t.translate(v[0], v[1] if len(v) > 1 else 0)
        elif name == "matrix":
            t = t.transform(v)
        elif name == "scale":
            t = t.scale(v[0], v[1] if len(v) > 1 else v[0])
        else:
            raise ValueError(f"transformación SVG no soportada: {name}")
    return t


def load_svg(path: str | FsPath) -> list[SvgShape]:
    """Devuelve los <path> del SVG con estilos heredados y transformaciones aplicadas."""
    tree = ET.parse(path)
    shapes: list[SvgShape] = []

    def walk(el, transform: Transform, style: dict[str, str]):
        style = {**style, **_style_dict(el)}
        transform = transform.transform(_parse_transform(el.get("transform")))
        if el.tag == SVG_NS + "path":
            p = pathops.Path()
            parse_path(el.get("d"), TransformPen(p.getPen(), transform))
            scale = (abs(transform[0] * transform[3] - transform[1] * transform[2])) ** 0.5
            has_stroke = style.get("stroke", "none") != "none"
            sw = float(style.get("stroke-width", "1")) if has_stroke else 0.0
            shapes.append(
                SvgShape(
                    id=el.get("id"),
                    path=p,
                    fill=style.get("fill", "black") != "none",
                    stroke_width=sw * scale,
                    linecap=style.get("stroke-linecap", "butt"),
                    linejoin=style.get("stroke-linejoin", "miter"),
                )
            )
        for child in el:
            walk(child, transform, style)

    walk(tree.getroot(), Transform(), {})
    return shapes


# --------------------------------------------------------------------------
# Operaciones geométricas
# --------------------------------------------------------------------------

def copy_path(p: pathops.Path) -> pathops.Path:
    q = pathops.Path()
    p.draw(q.getPen())
    return q


def union(paths) -> pathops.Path:
    paths = [p for p in paths if p is not None]
    if not paths:
        return pathops.Path()
    out = pathops.Path()
    pathops.union(paths, out.getPen())
    return out


def difference(a: pathops.Path, b: pathops.Path) -> pathops.Path:
    out = pathops.Path()
    pathops.difference([a], [b], out.getPen())
    return out


def round_stroke(p: pathops.Path, width: float) -> pathops.Path:
    """Trazo de anchura `width` con uniones y extremos redondos."""
    s = copy_path(p)
    s.stroke(width, pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 4)
    s.convertConicsToQuads()
    return s


def embolden(p: pathops.Path, width: float) -> pathops.Path:
    """Relleno ∪ trazo redondo: desplaza el contorno width/2 hacia fuera."""
    if width <= 0:
        return union([p])
    filled = union([p])  # normaliza dirección y solapamientos
    return union([filled, round_stroke(filled, width)])


def transformed(p: pathops.Path, t: Transform) -> pathops.Path:
    q = pathops.Path()
    p.draw(TransformPen(q.getPen(), t))
    return q


def shape_outline(shape: SvgShape) -> pathops.Path:
    """Contorno visible de un <path> del SVG (relleno ∪ trazo)."""
    if shape.fill and shape.stroke_width:
        return embolden(shape.path, shape.stroke_width)
    if shape.stroke_width:
        return union([round_stroke(shape.path, shape.stroke_width)])
    return union([shape.path])


# --------------------------------------------------------------------------
# Glifos UFO <-> pathops
# --------------------------------------------------------------------------

def glyph_to_path(glyph, font, decompose: bool = True) -> pathops.Path:
    """Contornos del glifo (y componentes, si `decompose`) como trazado de pathops."""
    p = pathops.Path()
    if decompose:
        rec = DecomposingRecordingPen(font)
        glyph.draw(rec)
        rec.replay(p.getPen())
    else:
        for c in glyph.contours:
            c.draw(p.getPen())
    return p


def path_to_glyph(p: pathops.Path, glyph, round_coords: bool = True) -> None:
    """Sustituye los contornos del glifo por `p` (los componentes se conservan)."""
    glyph.clearContours()
    pen = glyph.getPen()
    if round_coords:
        from fontTools.pens.roundingPen import RoundingPen

        pen = RoundingPen(pen)
    p.draw(pen)


# --------------------------------------------------------------------------
# Renderizado
# --------------------------------------------------------------------------

def flatten(p: pathops.Path, steps: int = 12) -> list[list[tuple[float, float]]]:
    """Aproxima el trazado por polígonos (uno por contorno)."""
    polys: list[list[tuple[float, float]]] = []
    cur: list[tuple[float, float]] = []
    last = (0.0, 0.0)
    for verb, pts in p.segments:
        if verb == "moveTo":
            if cur:
                polys.append(cur)
            cur = [pts[0]]
            last = pts[0]
        elif verb == "lineTo":
            cur.append(pts[0])
            last = pts[0]
        elif verb == "qCurveTo":
            # pathops entrega cuadráticas de un solo punto de control tras convertConicsToQuads,
            # pero `segments` puede agrupar varias (TrueType implícito).
            ctrl = list(pts[:-1])
            end = pts[-1]
            # descompone puntos implícitos
            segs = []
            p0 = last
            for i, c in enumerate(ctrl):
                if i < len(ctrl) - 1:
                    nxt = ctrl[i + 1]
                    e = ((c[0] + nxt[0]) / 2, (c[1] + nxt[1]) / 2)
                else:
                    e = end
                segs.append((p0, c, e))
                p0 = e
            for a, c, e in segs:
                for i in range(1, steps + 1):
                    t = i / steps
                    mt = 1 - t
                    cur.append(
                        (
                            mt * mt * a[0] + 2 * mt * t * c[0] + t * t * e[0],
                            mt * mt * a[1] + 2 * mt * t * c[1] + t * t * e[1],
                        )
                    )
            last = end
        elif verb == "curveTo":
            c1, c2, e = pts
            a = last
            for i in range(1, steps + 1):
                t = i / steps
                mt = 1 - t
                cur.append(
                    (
                        mt**3 * a[0] + 3 * mt * mt * t * c1[0] + 3 * mt * t * t * c2[0] + t**3 * e[0],
                        mt**3 * a[1] + 3 * mt * mt * t * c1[1] + 3 * mt * t * t * c2[1] + t**3 * e[1],
                    )
                )
            last = e
        elif verb in ("closePath", "endPath"):
            if cur:
                polys.append(cur)
            cur = []
    if cur:
        polys.append(cur)
    return polys


def render(p: pathops.Path, box, size, flip_y: bool = True):
    """Rasteriza `p` en una imagen "L" de `size` (ancho, alto) que cubre `box` = (xmin, ymin, xmax, ymax).

    Se usa la regla par-impar sobre el trazado ya simplificado (sin solapamientos),
    que en ese caso equivale a la regla no nula.
    """
    from PIL import Image, ImageChops, ImageDraw

    W, H = size
    xmin, ymin, xmax, ymax = box
    sx = W / (xmax - xmin)
    sy = H / (ymax - ymin)
    img = Image.new("L", size, 0)
    for poly in flatten(union([p])):
        if len(poly) < 3:
            continue
        if flip_y:
            pts = [((x - xmin) * sx, (ymax - y) * sy) for x, y in poly]
        else:
            pts = [((x - xmin) * sx, (y - ymin) * sy) for x, y in poly]
        layer = Image.new("L", size, 0)
        ImageDraw.Draw(layer).polygon(pts, fill=255)
        img = ImageChops.logical_xor(img.convert("1"), layer.convert("1")).convert("L")
    return img


def iou(a, b) -> float:
    """Intersección sobre unión de dos imágenes binarias del mismo tamaño."""
    from PIL import ImageChops

    a1, b1 = a.convert("1"), b.convert("1")
    inter = ImageChops.logical_and(a1, b1).histogram()[-1]
    uni = ImageChops.logical_or(a1, b1).histogram()[-1]
    return inter / uni if uni else 1.0
