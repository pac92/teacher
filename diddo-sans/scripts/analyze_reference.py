#!/usr/bin/env python3
"""Fase 1 · Análisis reproducible de los logos de referencia.

Lee los SVG de reference/original/ (que nunca se modifican) y:

1. Identifica cada letra, la pasa a unidades de fuente (UPM, 1000/em) con la línea
   base en y = 0 y la guarda en reference/normalized/ (relleno y aspecto final).
2. Mide escala, grosor del trazo, métricas verticales, astas y proporciones.
3. Compara la o con varias instancias de Montserrat para confirmar el peso de origen.
4. Comprueba las relaciones de construcción (p = d girada, a = d recortada).

Salidas:
    reference/normalized/diddo.svg, pad.svg   letras en UPM (capas «relleno» y «final»)
    reference/normalized/medidas.json         todas las medidas, legibles por programa
    reference/normalized/medidas.md           informe legible (se regenera, no editar)

Uso:  python scripts/analyze_reference.py
"""

from __future__ import annotations

import json
import math
import statistics

import diddolib as dl

ORIGINAL = dl.REFERENCE / "original"
OUT = dl.REFERENCE / "normalized"

# Orden de izquierda a derecha de los <path> de cada SVG (por xMin).
LAYOUT = {
    "diddo": ("diddo-full-bold.svg", ["simbolo", "i_punto", "i_asta", "d", "d2", "o"]),
    "pad": ("pad-bold-dark.svg", ["p", "a", "d"]),
}

WEIGHTS = [300, 350, 400, 450, 500]


def r(v, n=1):
    return round(v, n)


def load_logo(key):
    file, names = LAYOUT[key]
    shapes = sorted(dl.read_svg(ORIGINAL / file), key=lambda s: s.x_min)
    assert len(shapes) == len(names), f"{file}: se esperaban {len(names)} trazados"
    return dict(zip(names, shapes))


def outer_inner(path):
    """(exterior, interior) de un trazado con dos contornos, como polilíneas."""
    cs = sorted(dl.flatten(path, 64), key=lambda c: -_area(c))
    return cs[0], (cs[1] if len(cs) > 1 else None)


def _area(c):
    return abs(sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(c, c[1:]))) / 2


def _bbox(c):
    xs, ys = zip(*c)
    return min(xs), min(ys), max(xs), max(ys)


def edges_at(path, y):
    """Intervalos rellenos en la altura y."""
    return dl.hslice(path, y)


def linear_fit(pts):
    """Recta x = a·y + b por mínimos cuadrados."""
    ys = [p[1] for p in pts]
    xs = [p[0] for p in pts]
    my, mx = statistics.fmean(ys), statistics.fmean(xs)
    a = sum((y - my) * (x - mx) for x, y in pts) / sum((y - my) ** 2 for y in ys)
    return a, mx - a * my


def normalized_shape_distance(a, b):
    """Desviación máxima (Hausdorff) entre dos polilíneas cerradas, normalizadas
    por la altura de `a` y centradas en su caja. Devuelve fracción de la altura."""

    def norm(c, h, box):
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        return [((x - cx) / h, (y - cy) / h) for x, y in dl.resample(c, 360)]

    ba, bb = _bbox(a), _bbox(b)
    return dl.hausdorff(norm(a, ba[3] - ba[1], ba), norm(b, bb[3] - bb[1], bb))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    m400 = dl.montserrat(400)
    mo = dl.glyph_path(m400, "o")
    mo_box = mo.bounds
    mo_h = mo_box[3] - mo_box[1]
    overshoot = -mo_box[1]

    diddo = load_logo("diddo")
    pad = load_logo("pad")
    M = {}  # medidas

    # --- 1. Escala lienzo → UPM: la o del logo con la o de Montserrat 400 ---------
    lo = diddo["o"].path.bounds
    scale = mo_h / (lo[3] - lo[1])
    base_diddo = lo[1] + overshoot / scale  # línea base en el lienzo (y arriba)
    # pad no tiene o: su d es la misma curva que la de diddo (mismo tamaño en el
    # lienzo), así que se cuadra por la contraforma de la d.
    cd_diddo = _bbox(outer_inner(diddo["d"].path)[1])
    cd_pad = _bbox(outer_inner(pad["d"].path)[1])
    scale_pad = scale * (cd_diddo[3] - cd_diddo[1]) / (cd_pad[3] - cd_pad[1])
    base_pad = cd_pad[1] - (cd_diddo[1] - base_diddo) * scale / scale_pad

    M["escala"] = {
        "upm_por_unidad_lienzo_diddo": r(scale, 3),
        "upm_por_unidad_lienzo_pad": r(scale_pad, 3),
        "altura_o_lienzo": r(lo[3] - lo[1], 2),
        "altura_o_montserrat400": r(mo_h, 1),
        "nota": "La o del logo se iguala a la o de Montserrat 400 (con rebases).",
    }

    # --- 2. Pasar todo a UPM -----------------------------------------------------
    def to_upm(logo, base, s, x0):
        out = {}
        for name, shape in logo.items():
            t = (s, 0, 0, s, -x0 * s, -base * s)
            out[name] = {"path": dl.transformed(shape.path, t),
                         "stroke": shape.stroke_width * s,
                         "filled": shape.filled}
        return out

    x0_diddo = diddo["i_punto"].path.bounds[0]
    x0_pad = pad["p"].path.bounds[0]
    U = {"diddo": to_upm(diddo, base_diddo, scale, x0_diddo),
         "pad": to_upm(pad, base_pad, scale_pad, x0_pad)}

    M["trazo_upm"] = {k: r(statistics.fmean(v["stroke"] for n, v in U[k].items()
                                            if v["filled"]), 1) for k in U}
    M["trazo_upm"]["simbolo_D"] = r(U["diddo"]["simbolo"]["stroke"], 1)

    # --- 3. La o frente a Montserrat ------------------------------------------------
    o_out, o_in = outer_inner(U["diddo"]["o"]["path"])
    ob, ib = _bbox(o_out), _bbox(o_in)
    comp = {}
    for w in WEIGHTS:
        mout, minn = outer_inner(dl.glyph_path(dl.montserrat(w), "o"))
        # Las dos contraformas se normalizan con la altura exterior de cada o.
        h_logo, h_m = ob[3] - ob[1], _bbox(mout)[3] - _bbox(mout)[1]
        dev_out = normalized_shape_distance(o_out, mout)
        inner_l = [((x - (ob[0] + ob[2]) / 2) / h_logo, (y - (ob[1] + ob[3]) / 2) / h_logo)
                   for x, y in dl.resample(o_in, 360)]
        mb = _bbox(mout)
        inner_m = [((x - (mb[0] + mb[2]) / 2) / h_m, (y - (mb[1] + mb[3]) / 2) / h_m)
                   for x, y in dl.resample(minn, 360)]
        dev_in = dl.hausdorff(inner_l, inner_m)
        mib = _bbox(minn)
        comp[str(w)] = {
            "desviacion_max_pct": r(100 * max(dev_out, dev_in), 2),
            "exterior_pct": r(100 * dev_out, 2),
            "contraforma_pct": r(100 * dev_in, 2),
            "contraforma_h_rel": r((mib[2] - mib[0]) / (mb[2] - mb[0]), 3),
            "contraforma_v_rel": r((mib[3] - mib[1]) / (mb[3] - mb[1]), 3),
        }
    M["o"] = {
        "ancho_alto": r((ob[2] - ob[0]) / (ob[3] - ob[1]), 3),
        "contraforma_h_rel": r((ib[2] - ib[0]) / (ob[2] - ob[0]), 3),
        "contraforma_v_rel": r((ib[3] - ib[1]) / (ob[3] - ob[1]), 3),
        "frente_a_montserrat": comp,
        "mejor_peso": min(comp, key=lambda k: comp[k]["desviacion_max_pct"]),
    }

    # --- 4. Métricas verticales del logo (relleno y aspecto final) ---------------
    D = U["diddo"]
    half = M["trazo_upm"]["diddo"] / 2
    half_pad = M["trazo_upm"]["pad"] / 2
    i_dot = D["i_punto"]["path"].bounds
    i_stem = D["i_asta"]["path"].bounds
    d_box = D["d"]["path"].bounds
    p_box = U["pad"]["p"]["path"].bounds
    a_box = U["pad"]["a"]["path"].bounds
    md = dl.glyph_path(m400, "d").bounds
    mp = dl.glyph_path(m400, "p").bounds
    mi_dot = _bbox(sorted(dl.flatten(dl.glyph_path(m400, "i")), key=lambda c: -_bbox(c)[1])[0])
    m_xh = dl.glyph_path(m400, "x").bounds[3]
    M["vertical_upm"] = {
        "nota": "Relleno = contorno sin trazo. Final = relleno + medio trazo (aspecto visible).",
        "altura_x_relleno": {"i": r(i_stem[3]), "a": r(a_box[3]), "o_sin_rebase": r(ob[3] - overshoot)},
        "altura_x_montserrat400": r(m_xh),
        "ascendente_d": {"relleno": r(d_box[3]), "final": r(d_box[3] + half),
                         "montserrat400": r(md[3])},
        "descendente_p": {"relleno": r(p_box[1]), "final": r(p_box[1] - half_pad),
                          "montserrat400": r(mp[1])},
        "punto_i": {"relleno": [r(i_dot[1]), r(i_dot[3])],
                    "diametro_relleno": r(i_dot[2] - i_dot[0]),
                    "montserrat400": [r(mi_dot[1]), r(mi_dot[3])],
                    "diametro_montserrat400": r(mi_dot[2] - mi_dot[0])},
        "pie_d_bajo_base": r(-d_box[1]),
    }

    # --- 5. Astas ---------------------------------------------------------------
    m_stem = dl.hslice(dl.glyph_path(m400, "l"), 300)[0]
    m_stem_w = m_stem[1] - m_stem[0]

    # d: el asta queda sola entre la altura x y el remate superior.
    xh = i_stem[3]
    dpath = D["d"]["path"]
    ys = [y for y in range(int(xh) + 20, int(d_box[3]) - 60, 10)]
    rights, lefts = [], []
    for y in ys:
        a, b = dl.hslice(dpath, y)[-1]
        lefts.append((a, y))
        rights.append((b, y))
    ka, kb = linear_fit(rights)
    left_x = statistics.fmean(x for x, _ in lefts)
    left_dev = max(abs(x - left_x) for x, _ in lefts)

    def d_width(y):
        return ka * y + kb - left_x

    # i: asta sola entre la base y la altura x.
    ipath = D["i_asta"]["path"]
    iys = list(range(60, int(xh) - 60, 10))
    irights = [(dl.hslice(ipath, y)[-1][1], y) for y in iys]
    ilefts = [dl.hslice(ipath, y)[0][0] for y in iys]
    ia, ib_ = linear_fit(irights)
    il = statistics.fmean(ilefts)

    def i_width(y):
        return ia * y + ib_ - il

    M["astas_upm"] = {
        "montserrat400_asta": r(m_stem_w),
        "d": {
            "borde_izquierdo": "vertical (desviación máx. %.1f UPM)" % left_dev,
            "angulo_borde_derecho_grados": r(math.degrees(math.atan(-ka)), 2),
            "ancho_relleno": {"base_extrapolado": r(d_width(0)), "altura_x": r(d_width(xh)),
                              "600": r(d_width(600)), "800": r(d_width(800))},
            "ancho_final": {"altura_x": r(d_width(xh) + 2 * half),
                            "800": r(d_width(800) + 2 * half)},
        },
        "i": {
            "borde_izquierdo": "vertical",
            "angulo_borde_derecho_grados": r(math.degrees(math.atan(-ia)), 2),
            "ancho_relleno": {"base_extrapolado": r(i_width(0)), "100": r(i_width(100)),
                              "altura_x": r(i_width(xh))},
            "ancho_final": {"100": r(i_width(100) + 2 * half),
                            "altura_x": r(i_width(xh) + 2 * half)},
        },
    }

    # --- 6. Relaciones de construcción ------------------------------------------
    P = U["pad"]
    pd_out, pd_in = outer_inner(P["d"]["path"])
    pp_out, pp_in = outer_inner(P["p"]["path"])
    rot = lambda c: [(-x, -y) for x, y in c]  # noqa: E731
    pa_out, pa_in = outer_inner(P["a"]["path"])
    dd1, dd2 = outer_inner(D["d"]["path"])[0], outer_inner(D["d2"]["path"])[0]
    dh = d_box[3] - d_box[1]
    M["construccion"] = {
        "p_es_d_girada_180_desv_pct": r(100 * normalized_shape_distance(pd_out, rot(pp_out)), 3),
        "las_dos_d_de_diddo_desv_pct": r(100 * normalized_shape_distance(dd1, dd2), 3),
        "d_de_pad_vs_d_de_diddo_desv_pct": r(100 * normalized_shape_distance(pd_out, dd1), 3),
        "contraforma_a_vs_d_desv_pct": r(100 * normalized_shape_distance(pa_in, pd_in), 3),
        "altura_d_upm": r(dh),
    }

    # --- 7. Salidas --------------------------------------------------------------
    for key in U:
        write_svg(key, U[key])
    (OUT / "medidas.json").write_text(json.dumps(M, ensure_ascii=False, indent=2) + "\n")
    (OUT / "medidas.md").write_text(report(M))
    print(report(M))


def write_svg(key, letters):
    """Letras en UPM: capa «relleno» (contorno limpio de pathops) y «final» (con trazo)."""
    allb = [v["path"].bounds for v in letters.values()]
    xmin = min(b[0] for b in allb) - 80
    xmax = max(b[2] for b in allb) + 80
    ymin, ymax = -450, 1000
    parts = []
    for name, v in letters.items():
        if v["filled"]:
            final = dl.thicken(v["path"], v["stroke"])
            fill = dl.simplify(v["path"])
        else:
            final = dl.stroke_outline(v["path"], v["stroke"])
            fill = v["path"]
        parts.append(
            f'  <g id="{name}" data-trazo-upm="{v["stroke"]:.1f}">\n'
            f'    <path class="final" d="{dl.svg_d(final)}"/>\n'
            f'    <path class="relleno" d="{dl.svg_d(fill)}"/>\n'
            "  </g>")
    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- Generado por scripts/analyze_reference.py a partir de reference/original/. No editar.
     Unidades: UPM (1000/em). Línea base en y = 0, eje y hacia arriba (por eso el scale(1,-1)).
     Capa «final»: relleno ∪ trazo redondo (aspecto del logo). Capa «relleno»: sin trazo. -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="{xmin:.0f} {-ymax} {xmax - xmin:.0f} {ymax - ymin}">
 <style>.final{{fill:#4a67b5}} .relleno{{fill:none;stroke:#fff;stroke-width:3}} .guia{{stroke:#c33;stroke-width:2}}</style>
 <g transform="scale(1,-1)">
  <line class="guia" x1="{xmin:.0f}" x2="{xmax:.0f}" y1="0" y2="0"/>
{chr(10).join(parts)}
 </g>
</svg>
"""
    (OUT / f"{key}.svg").write_text(svg)


def report(M):
    v, a, o, c = M["vertical_upm"], M["astas_upm"], M["o"], M["construccion"]
    lines = [
        "# Medidas de los logos (generado)",
        "",
        "Generado por `scripts/analyze_reference.py`. **No editar a mano.** Unidades en UPM (1000/em).",
        "",
        "## Escala y trazo",
        f"- 1 unidad de lienzo = {M['escala']['upm_por_unidad_lienzo_diddo']} UPM (diddo) y "
        f"{M['escala']['upm_por_unidad_lienzo_pad']} UPM (pad).",
        f"- Trazo: diddo **{M['trazo_upm']['diddo']}**, pad **{M['trazo_upm']['pad']}**, "
        f"símbolo D {M['trazo_upm']['simbolo_D']}.",
        "",
        "## La o frente a Montserrat",
        f"- Ancho/alto {o['ancho_alto']}; contraforma/exterior: horizontal {o['contraforma_h_rel']}, "
        f"vertical {o['contraforma_v_rel']}.",
        "",
        "| Peso | Desv. máx. | Exterior | Contraforma | Contraf. h | Contraf. v |",
        "|---|---|---|---|---|---|",
    ]
    for w, d in o["frente_a_montserrat"].items():
        mark = "**" if w == o["mejor_peso"] else ""
        lines.append(f"| {mark}{w}{mark} | {mark}{d['desviacion_max_pct']} %{mark} | "
                     f"{d['exterior_pct']} % | {d['contraforma_pct']} % | "
                     f"{d['contraforma_h_rel']} | {d['contraforma_v_rel']} |")
    lines += [
        "",
        "## Métricas verticales",
        "",
        "| | Logo (relleno) | Logo (final) | Montserrat 400 |",
        "|---|---|---|---|",
        f"| Altura x | {v['altura_x_relleno']['i']} (i) · {v['altura_x_relleno']['a']} (a) | "
        f"{r(v['altura_x_relleno']['i'] + M['trazo_upm']['diddo'] / 2)} | {v['altura_x_montserrat400']} |",
        f"| Ascendente (d) | {v['ascendente_d']['relleno']} | {v['ascendente_d']['final']} | "
        f"{v['ascendente_d']['montserrat400']} |",
        f"| Descendente (p) | {v['descendente_p']['relleno']} | {v['descendente_p']['final']} | "
        f"{v['descendente_p']['montserrat400']} |",
        f"| Punto de la i | {v['punto_i']['relleno'][0]}–{v['punto_i']['relleno'][1]} "
        f"(⌀ {v['punto_i']['diametro_relleno']}) | | {v['punto_i']['montserrat400'][0]}–"
        f"{v['punto_i']['montserrat400'][1]} (⌀ {v['punto_i']['diametro_montserrat400']}) |",
        f"| Pie de la d bajo la base | {v['pie_d_bajo_base']} | | — |",
        "",
        "## Astas",
        f"- Asta de Montserrat 400: {a['montserrat400_asta']} UPM (paralela).",
        f"- **d**: borde izquierdo {a['d']['borde_izquierdo']}; borde derecho inclinado "
        f"{a['d']['angulo_borde_derecho_grados']}°. Ancho de relleno: "
        f"{a['d']['ancho_relleno']['800']} a 800, {a['d']['ancho_relleno']['altura_x']} en la altura x, "
        f"{a['d']['ancho_relleno']['base_extrapolado']} extrapolado a la base. "
        f"Ancho final: {a['d']['ancho_final']['800']} → {a['d']['ancho_final']['altura_x']}.",
        f"- **i**: borde izquierdo vertical; borde derecho inclinado "
        f"{a['i']['angulo_borde_derecho_grados']}°. Ancho de relleno: "
        f"{a['i']['ancho_relleno']['altura_x']} arriba → {a['i']['ancho_relleno']['100']} a 100. "
        f"Ancho final: {a['i']['ancho_final']['altura_x']} → {a['i']['ancho_final']['100']}.",
        "",
        "## Construcción",
        f"- p = d girada 180°: desviación {c['p_es_d_girada_180_desv_pct']} % de la altura.",
        f"- Las dos d de diddo: {c['las_dos_d_de_diddo_desv_pct']} %. "
        f"d de pad frente a d de diddo: {c['d_de_pad_vs_d_de_diddo_desv_pct']} %.",
        f"- Contraforma de la a frente a la de la d: {c['contraforma_a_vs_d_desv_pct']} %.",
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
