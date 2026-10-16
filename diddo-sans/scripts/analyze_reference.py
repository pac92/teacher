#!/usr/bin/env python3
"""Fase 1: análisis reproducible de los logos de referencia.

Lee `reference/original/*.svg`, identifica cada letra, pasa sus trazados a
unidades de fuente (UPM de Montserrat, y hacia arriba, línea base en 0) y
escribe:

  reference/normalized/<logo>-<letra>.svg   esqueleto (relleno) y contorno visible
  reference/normalized/measurements.json    medidas usadas en docs/analisis-logos.md

Uso:
    python scripts/analyze_reference.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pathops
from fontTools.misc.transform import Transform
from fontTools.pens.svgPathPen import SVGPathPen

sys.path.insert(0, str(Path(__file__).resolve().parent))
from diddolib import ROOT, embolden, load_svg, round_stroke, transformed, union  # noqa: E402

ORIGINAL = ROOT / "reference" / "original"
NORMALIZED = ROOT / "reference" / "normalized"

# Escala: la o del logo (96,80 de lienzo) mide 534,9 UPM en Montserrat 400 (de −4,7 a 530,2).
MONTSERRAT_O_HEIGHT = 534.9
MONTSERRAT_O_BOTTOM = -4.7

# Letras de cada logo, por orden de izquierda a derecha de los <path>.
LOGOS = {
    "diddo": ("diddo-full-bold.svg", ["symbol", "i.dot", "i.stem", "d", "d2", "o"]),
    "pad": ("pad-bold-dark.svg", ["p", "a", "d"]),
}


def _sorted_shapes(logo: str):
    file, names = LOGOS[logo]
    shapes = sorted(load_svg(ORIGINAL / file), key=lambda s: s.path.bounds[0])
    assert len(shapes) == len(names), (logo, len(shapes))
    return dict(zip(names, shapes))


def canvas_to_upm(logo: str) -> tuple[Transform, float]:
    """Transformación lienzo → UPM y escala (UPM por unidad de lienzo).

    Los dos logos comparten la misma d (mismas coordenadas relativas y tamaño),
    así que tienen la misma escala; la línea base de pad se obtiene alineando
    el contraforma de su d con la de diddo.
    """
    diddo = _sorted_shapes("diddo")
    o = union([diddo["o"].path])
    scale = MONTSERRAT_O_HEIGHT / (o.bounds[3] - o.bounds[1])
    baseline_diddo = o.bounds[3] + MONTSERRAT_O_BOTTOM / scale  # y del lienzo (hacia abajo)
    if logo == "diddo":
        baseline = baseline_diddo
        x0 = diddo["i.stem"].path.bounds[0]
    else:
        def counter_bottom(shape):
            cs = sorted(union([shape.path]).contours, key=lambda c: c.bounds[2] - c.bounds[0])
            return cs[0].bounds[3]

        pad = _sorted_shapes("pad")
        baseline = counter_bottom(pad["d"]) + (baseline_diddo - counter_bottom(diddo["d"]))
        x0 = pad["p"].path.bounds[0]
    t = Transform().scale(scale, -scale).translate(-x0, -baseline)
    return t, scale


def reference_letters(logo: str) -> dict[str, dict]:
    """Letras del logo en UPM: esqueleto (relleno), contorno visible y trazo."""
    shapes = _sorted_shapes(logo)
    t, scale = canvas_to_upm(logo)
    out: dict[str, dict] = {}
    for name, sh in shapes.items():
        skel = union([transformed(sh.path, t)])
        stroke = sh.stroke_width * scale
        if sh.fill:
            visible = embolden(skel, stroke)
        else:
            visible = union([round_stroke(transformed(sh.path, t), stroke)])
        out[name] = {"skeleton": skel, "visible": visible, "stroke": stroke, "fill": sh.fill}
    # la i son dos trazados
    if "i.dot" in out:
        out["i"] = {
            "skeleton": union([out["i.dot"]["skeleton"], out["i.stem"]["skeleton"]]),
            "visible": union([out["i.dot"]["visible"], out["i.stem"]["visible"]]),
            "stroke": out["i.stem"]["stroke"],
            "fill": True,
        }
    return out


def hslice(p: pathops.Path, y: float) -> list[tuple[float, float]]:
    """Intervalos [x0, x1] ocupados por `p` en la horizontal y."""
    r = pathops.Path()
    pen = r.getPen()
    x0, _, x1, _ = p.bounds
    pen.moveTo((x0 - 10, y - 0.01))
    pen.lineTo((x1 + 10, y - 0.01))
    pen.lineTo((x1 + 10, y + 0.01))
    pen.lineTo((x0 - 10, y + 0.01))
    pen.closePath()
    o = pathops.Path()
    pathops.intersection([p], [r], o.getPen())
    return sorted((c.bounds[0], c.bounds[2]) for c in o.contours)


def to_svg(paths: dict[str, pathops.Path], box) -> str:
    x0, y0, x1, y1 = box
    parts = []
    styles = {"visible": 'fill="#4a67b5" fill-opacity="0.35"', "skeleton": 'fill="#4a67b5"'}
    for kind, p in paths.items():
        pen = SVGPathPen(None, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip("."))
        p.draw(pen)
        parts.append(f'  <path id="{kind}" {styles[kind]} d="{pen.getCommands()}"/>')
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0:.0f} {-y1:.0f} {x1 - x0:.0f} {y1 - y0:.0f}">\n'
        f'  <!-- UPM de Montserrat, línea base en y = 0 (y hacia arriba: se invierte con el grupo) -->\n'
        f'  <g transform="scale(1 -1)">\n'
        + "\n".join("  " + s for s in parts)
        + "\n  </g>\n</svg>\n"
    )


def measure() -> dict:
    res: dict = {}
    for logo in LOGOS:
        _, scale = canvas_to_upm(logo)
        letters = reference_letters(logo)
        res[logo] = {"upm_per_canvas_unit": round(scale, 4), "letters": {}}
        for name, L in letters.items():
            if name in ("i.dot", "i.stem"):
                continue
            sk, vis = L["skeleton"], L["visible"]
            b = [round(v, 1) for v in sk.bounds]
            info = {
                "stroke_upm": round(L["stroke"], 1),
                "skeleton_bounds": b,
                "visible_bounds": [round(v, 1) for v in vis.bounds],
            }
            if name in ("d", "d2", "a", "i"):
                stem_x0 = sk.bounds[2] - 140 if name != "i" else sk.bounds[0] - 1
                widths = {}
                for y in (850, 800, 700, 600, 500, 450, 400, 300, 200, 100, 50, 20):
                    segs = [s for s in hslice(sk, y) if s[1] > stem_x0]
                    if segs:
                        a, z = segs[-1]
                        widths[str(y)] = [round(a - sk.bounds[0], 1), round(z - sk.bounds[0], 1), round(z - a, 1)]
                info["stem_slices_x0_x1_w"] = widths
            res[logo]["letters"][name] = info
        if logo == "diddo":
            dot = letters["i.dot"]["skeleton"].bounds
            stem = letters["i.stem"]["skeleton"].bounds
            res[logo]["i_dot"] = {
                "diameter_w": round(dot[2] - dot[0], 1),
                "diameter_h": round(dot[3] - dot[1], 1),
                "bottom": round(dot[1], 1),
                "center_x_from_stem_left": round((dot[0] + dot[2]) / 2 - stem[0], 1),
                "skeleton_gap_to_stem": round(dot[1] - stem[3], 1),
                "visible_gap_to_stem": round(dot[1] - stem[3] - letters["i.stem"]["stroke"], 1),
            }
    return res


def main():
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    for logo in LOGOS:
        for name, L in reference_letters(logo).items():
            if name in ("i.dot", "i.stem"):
                continue
            vb = L["visible"].bounds
            box = (vb[0] - 20, vb[1] - 20, vb[2] + 20, vb[3] + 20)
            paths = {"visible": L["visible"]}
            if L["fill"]:
                paths["skeleton"] = L["skeleton"]
            (NORMALIZED / f"{logo}-{name}.svg").write_text(to_svg(paths, box))
    m = measure()
    (NORMALIZED / "measurements.json").write_text(json.dumps(m, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(m, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
