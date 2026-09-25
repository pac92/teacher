"""Extrae cada pregunta (y su criterio de corrección) de los PDF como imagen
recortada + texto para el buscador.

- Detecta el inicio de cada pregunta (ancla) según el formato de cada época:
    era 1 (2008-2019): OPCIÓN A/B + 1.- … 7.-
    era 2 (2020-2024): BLOQUE A/B/C(/D) + A.1. … C.5.
    era 3 (2025):      EJERCICIO n + Pregunta n(.m)
- Asigna a cada pregunta sus líneas de texto y sus figuras (imágenes y
  dibujos vectoriales), aunque la figura empiece por encima del número de la
  pregunta o la pregunta continúe en la página siguiente.
- Renderiza cada trozo de página, blanquea lo que pertenece a otras preguntas
  y apila los trozos en una sola imagen (preguntas partidas entre páginas).
- 2009 está escaneado: se usa OCR (tesseract) para el texto y la posición.

Uso: python3 tools/extract.py [filtro_año]
"""
import difflib
import io
import json
import os
import re
import sys
import unicodedata

import numpy as np
import pymupdf
import pytesseract
from PIL import Image
from scipy import ndimage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from catalog import E, era  # noqa: E402

pymupdf.TOOLS.mupdf_display_errors(False)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "build", "raw")
OUT = os.path.join(ROOT, "build", "out")
ZOOM_Q = 2.0
ZOOM_C = 1.8
OCR_DPI = 300

# ---------------------------------------------------------------- utilidades


def nfold(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s).strip().lower()


def area(b):
    return max(0, b[2] - b[0]) * max(0, b[3] - b[1])


def inter(a, b):
    return (max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3]))


def overlaps(a, b, pad=0):
    return a[0] - pad < b[2] and b[0] - pad < a[2] and a[1] - pad < b[3] and b[1] - pad < a[3]


def union(a, b):
    return (min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3]))


class El:
    __slots__ = ("page", "bbox", "text", "kind", "owner", "role")

    def __init__(self, page, bbox, text="", kind="text"):
        self.page, self.bbox, self.text, self.kind = page, tuple(bbox), text, kind
        self.owner = None
        self.role = None  # header / footer / frame / marker


# ------------------------------------------------------- lectura de elementos


def cluster_boxes(boxes, gap=3.0):
    """Une rectángulos que se tocan (con tolerancia) en grupos."""
    boxes = [list(b) for b in boxes]
    changed = True
    while changed and len(boxes) > 1:
        changed = False
        boxes.sort(key=lambda b: b[0])
        out = []
        for b in boxes:
            merged = False
            for o in out[-40:]:
                if overlaps(o, b, gap):
                    o[0], o[1] = min(o[0], b[0]), min(o[1], b[1])
                    o[2], o[3] = max(o[2], b[2]), max(o[3], b[3])
                    merged = changed = True
                    break
            if not merged:
                out.append(b)
        boxes = out
    return [tuple(b) for b in boxes]


def vector_elements(page, pi):
    els = []
    pr = page.rect
    d = page.get_text("dict")
    for b in d["blocks"]:
        if b["type"] != 0:
            continue
        for ln in b["lines"]:
            txt = "".join(s["text"] for s in ln["spans"])
            if not txt.strip():
                continue
            els.append(El(pi, ln["bbox"], txt, "text"))
    gboxes, rules = [], []
    for info in page.get_image_info():
        bb = inter(info["bbox"], tuple(pr))
        if area(bb) > 4:
            gboxes.append(bb)
    for dr in page.get_drawings():
        fill = dr.get("fill")
        stroke = dr.get("color")
        if dr.get("type") == "f" and fill and min(fill) > 0.97:
            continue  # relleno blanco invisible
        if stroke is None and fill is None:
            continue
        # un mismo trazado puede contener segmentos muy separados: se
        # descompone en sus elementos (líneas, rectángulos, curvas)
        sub = []
        if dr.get("type") == "s" or (dr.get("type") == "fs" and fill and min(fill) > 0.97):
            for it in dr["items"]:
                pts = [v for v in it[1:] if isinstance(v, pymupdf.Point)]
                if it[0] == "re":
                    sub.append(tuple(it[1]))
                elif it[0] == "qu":
                    sub.append(tuple(it[1].rect))
                elif pts:
                    sub.append((min(q.x for q in pts), min(q.y for q in pts), max(q.x for q in pts), max(q.y for q in pts)))
            sub = cluster_boxes(sub, 1.0) if len(sub) < 400 else [tuple(dr["rect"])]
        else:
            sub = [tuple(dr["rect"])]
        lw = (dr.get("width") or 1) / 2
        for r in sub:
            bb = inter((r[0] - lw, r[1] - lw, r[2] + lw, r[3] + lw), tuple(pr))
            w, h = bb[2] - bb[0], bb[3] - bb[1]
            if w < 0 or h < 0:
                continue
            if (h < 3 and w > 150) or (w < 3 and h > 150):
                rules.append(bb)
                continue
            if w < 0.5 and h < 0.5:
                continue
            gboxes.append(bb)
    for bb in cluster_boxes(gboxes):
        if area(bb) < 30:
            continue
        els.append(El(pi, bb, "", "graphic"))
    for bb in rules:
        r = El(pi, bb, "", "rule")
        r.role = "rule"
        els.append(r)
    return els


def ocr_elements(page, pi):
    pix = page.get_pixmap(dpi=OCR_DPI, colorspace=pymupdf.csGRAY)
    img = Image.frombytes("L", (pix.width, pix.height), pix.samples)
    sc = 72.0 / OCR_DPI
    data = pytesseract.image_to_data(img, lang="spa", config="--psm 3", output_type=pytesseract.Output.DICT)
    lines = {}
    wordboxes = []
    for i, w in enumerate(data["text"]):
        if not w.strip() or float(data["conf"][i]) < 0:
            continue
        x, y, ww, hh = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
        key = (data["block_num"][i], data["par_num"][i], data["line_num"][i])
        conf = float(data["conf"][i])
        good = conf > 55 and sum(c.isalpha() for c in w) >= max(1, len(w) // 2) and hh < 60
        if good:
            wordboxes.append((x, y, x + ww, y + hh))
        L = lines.setdefault(key, [])
        L.append((x, y, x + ww, y + hh, w, good))
    els = []
    for key, ws in lines.items():
        ws.sort()
        if not any(g for *_, g in ws) and not re.search(r"\[\s*\d", " ".join(w[4] for w in ws)):
            continue
        bb = (min(w[0] for w in ws), min(w[1] for w in ws), max(w[2] for w in ws), max(w[3] for w in ws))
        txt = " ".join(w[4] for w in ws)
        els.append(El(pi, tuple(v * sc for v in bb), txt, "text"))
    # figuras: píxeles oscuros que no son palabras reconocidas
    a = np.asarray(img) < 150
    mask = a.copy()
    for (x0, y0, x1, y1) in wordboxes:
        mask[max(0, y0 - 3):y1 + 3, max(0, x0 - 3):x1 + 3] = False
    mask = ndimage.binary_dilation(mask, iterations=12)
    lab, n = ndimage.label(mask)
    H, W = a.shape
    for sl in ndimage.find_objects(lab):
        ys, xs = sl
        h, w = ys.stop - ys.start, xs.stop - xs.start
        if h < 90 or w < 90:
            continue
        if w > 0.9 * W and h < 60:
            continue
        dens = a[sl].mean()
        if dens < 0.01:
            continue
        els.append(El(pi, (xs.start * sc, ys.start * sc, xs.stop * sc, ys.stop * sc), "", "graphic"))
    return els


# ------------------------------------------------------------ filas y anclas


def make_rows(texts):
    texts = sorted(texts, key=lambda e: (e.bbox[1] + e.bbox[3]) / 2)
    rows = []
    for e in texts:
        cy = (e.bbox[1] + e.bbox[3]) / 2
        h = e.bbox[3] - e.bbox[1]
        if rows:
            r = rows[-1]
            rcy = (r["bbox"][1] + r["bbox"][3]) / 2
            if abs(cy - rcy) < max(2.5, 0.45 * min(h, r["h"])):
                r["els"].append(e)
                r["bbox"] = union(r["bbox"], e.bbox)
                r["h"] = max(r["h"], h)
                continue
        rows.append({"els": [e], "bbox": e.bbox, "h": h})
    for r in rows:
        r["els"].sort(key=lambda e: e.bbox[0])
        r["text"] = " ".join(e.text.strip() for e in r["els"]).strip()
        r["page"] = r["els"][0].page
    return rows


RX = {
    1: dict(
        marker=re.compile(r"^OPC[I1l]?[OÓ0]N\s*([AB8])\b", re.I),
        anchor=re.compile(r"^(\d{1,2})\s*(?:\.\s*[-–—]?|[-–—]|,-)(?=\s*\S)"),
    ),
    2: dict(
        marker=re.compile(r"^BLOQUE\s+([A-D])\b"),
        anchor=re.compile(r"^([A-D])\s*\.\s*(\d)\s*\.?(?=\s|$)"),
    ),
    3: dict(
        marker=re.compile(r"^EJERCICIO\b\s*(\d)?"),
        anchor=re.compile(r"^(?:Pregunta|Ejercicio)\s+(\d)(?:\s*\.\s*(\d))?(?=[\s\.:(]|$)"),
    ),
}
OCR_ANCHOR = re.compile(r"^([0-9lI|])\s*[\.,]\s*[-–—~]")
FOOTER_RX = re.compile(r"^(p[aá]gina\s*\d+(\s*de\s*\d+)?|\d{1,2}(\s*/\s*\d)?)$", re.I)


def fuzzy_in(t, pool):
    if t in pool:
        return True
    if len(t) < 4:
        return False
    for p in pool:
        if abs(len(p) - len(t)) < 12 and difflib.SequenceMatcher(None, t, p).ratio() > 0.8:
            return True
    return False


def parse_doc(pdf, pages, er, ocr, kind):
    """Devuelve (lista de preguntas, elementos por página, rect de página)."""
    per_page = {}
    rows_all = []
    for pi in pages:
        page = pdf[pi]
        els = ocr_elements(page, pi) if ocr else vector_elements(page, pi)
        per_page[pi] = els
        rows_all.append(make_rows([e for e in els if e.kind == "text"]))
    rx = RX[er]

    def classify(row):
        t = row["text"]
        m = rx["marker"].match(t)
        if m:
            return ("marker", m)
        m = rx["anchor"].match(t)
        if m:
            return ("anchor", m)
        if ocr and er == 1:
            m = OCR_ANCHOR.match(t)
            if m:
                return ("anchor", m)
        return (None, None)

    # cabecera: filas previas al primer marcador/ancla en la primera página
    first_rows = rows_all[0]
    hdr_pool = set()
    for r in first_rows:
        if classify(r)[0]:
            break
        hdr_pool.add(nfold(r["text"]))
    ph = pdf[pages[0]].rect.height
    for rows in rows_all:
        for i, r in enumerate(rows):
            if r["bbox"][1] > 0.45 * ph:
                break
            if classify(r)[0]:
                break
            if fuzzy_in(nfold(r["text"]), hdr_pool) or i == 0 and r["bbox"][1] < 0.15 * ph:
                r["hdr"] = True
        # cabecera = hasta la última fila de cabecera contigua
        last = -1
        for i, r in enumerate(rows):
            if r.get("hdr"):
                last = i
            elif classify(r)[0] or i - last > 2:
                break
        for r in rows[: last + 1]:
            r["hdr"] = True
        for r in rows:
            if r["bbox"][1] > 0.9 * ph and FOOTER_RX.match(r["text"].strip()):
                r["ftr"] = True

    questions = []
    cur = None
    sec = None
    expect = None
    anchor_x = None
    events = []  # (page, y, owner)
    for rows in rows_all:
        for r in rows:
            if r.get("hdr") or r.get("ftr"):
                for e in r["els"]:
                    e.role = "header" if r.get("hdr") else "footer"
                continue
            k, m = classify(r)
            x0 = r["bbox"][0]
            if k == "anchor" and er == 1:
                n = int(m.group(1)) if m.group(1).isdigit() else -1
                if ocr and expect is not None and n != expect and OCR_ANCHOR.match(r["text"]):
                    n = expect  # el OCR confunde 1/4/7/l
                ok = (expect is None and n == 1) or n == expect
                if anchor_x is not None and abs(x0 - anchor_x) > 18:
                    ok = False
                if not ok:
                    k = None
            if k == "anchor" and er == 2:
                if sec is not None and m.group(1) != sec and m.group(2) != "1":
                    k = None
            if k == "marker":
                cur = None
                sec = (m.group(1) or "").upper().replace("8", "B")
                expect = 1
                events.append((r["page"], r["bbox"][1], None))
                for e in r["els"]:
                    e.role = "marker"
                continue
            if k == "anchor":
                if er == 1:
                    num = str(n)
                    expect = n + 1
                    if anchor_x is None:
                        anchor_x = x0
                elif er == 2:
                    sec = m.group(1)
                    num = m.group(2)
                else:
                    sec = m.group(1)
                    num = m.group(1) + ("." + m.group(2) if m.group(2) else "")
                cur = {"sec": sec, "num": num, "rows": [], "graphics": []}
                questions.append(cur)
                events.append((r["page"], r["bbox"][1] - 1.5, id(cur)))
            if cur is not None:
                cur["rows"].append(r)
                for e in r["els"]:
                    e.owner = id(cur)
    return questions, per_page, events


def assign_graphics(questions, per_page, events, ph):
    qmap = {id(q): q for q in questions}
    for pi, els in per_page.items():
        hdr_bottom = max([e.bbox[3] for e in els if e.role == "header"] or [0])
        texts = [e for e in els if e.kind == "text"]
        for g in els:
            if g.kind == "text":
                continue
            cy = (g.bbox[1] + g.bbox[3]) / 2
            if cy < hdr_bottom + 1 or g.bbox[3] <= hdr_bottom + 2:
                g.role = "header"
                continue
            # marco que engloba varias preguntas / marcadores
            inside = [t for t in texts if t.role in ("marker",) or (t.owner and t.bbox[0] >= g.bbox[0] - 1 and t.bbox[2] <= g.bbox[2] + 1 and t.bbox[1] >= g.bbox[1] - 1 and t.bbox[3] <= g.bbox[3] + 1)]
            owners = {t.owner for t in inside if t.owner and area(inter(t.bbox, g.bbox)) > 0.7 * area(t.bbox)}
            anchors_in = [t for t in inside if t.role == "marker" and overlaps(t.bbox, g.bbox)]
            if g.kind == "graphic" and (len(owners) > 1 and (g.bbox[3] - g.bbox[1]) > 0.35 * ph or anchors_in):
                g.role = "frame"
                continue
            owner = None
            for (p, y, o) in events:
                if (p, y) <= (pi, cy):
                    owner = o
                else:
                    break
            if owner is None:
                # en zona sin dueño: la pregunta con más solape vertical
                best, bo = 0, None
                for q in questions:
                    for r in q["rows"]:
                        if r["page"] == pi:
                            ov = min(r["bbox"][3], g.bbox[3]) - max(r["bbox"][1], g.bbox[1])
                            if ov > best:
                                best, bo = ov, id(q)
                owner = bo
            g.owner = owner
            if owner:
                qmap[owner]["graphics"].append(g)
        # etiquetas de texto dentro de una figura -> dueño de la figura
        for g in els:
            if g.kind != "graphic" or not g.owner or g.role:
                continue
            for t in texts:
                if t.role or t.owner == g.owner:
                    continue
                if area(inter(t.bbox, g.bbox)) > 0.6 * area(t.bbox) and len(t.text.strip()) < 40:
                    if t.owner and any(t is r["els"][0] for q in questions for r in q["rows"] if id(q) == t.owner):
                        continue  # es la primera palabra de una fila (posible ancla)
                    t.owner = g.owner


# ---------------------------------------------------------------- renderizado


def render_question(pdf, q, per_page, zoom, xrange_, members_fn=None):
    qid = id(q)
    segs = []
    for pi, els in per_page.items():
        mine = [e for e in els if e.owner == qid and e.role is None]
        if not mine:
            continue
        bb = mine[0].bbox
        for e in mine[1:]:
            bb = union(bb, e.bbox)
        clip = pymupdf.Rect(xrange_[0], bb[1] - 3, xrange_[1], bb[3] + 3)
        clip = clip & pdf[pi].rect
        pix = pdf[pi].get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), clip=clip, alpha=False)
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        arr = np.asarray(img).copy()
        mine_g = [e.bbox for e in mine if e.kind != "text"]
        mine_t = [e.bbox for e in mine if e.kind == "text"]
        for e in els:
            if e.owner == qid and e.role is None:
                continue
            if e.role == "frame":
                continue
            if not overlaps(e.bbox, tuple(clip)):
                continue
            if e.kind != "text" and any(overlaps(e.bbox, m, -1) for m in mine_g + mine_t):
                continue
            if e.kind == "text" and any(area(inter(e.bbox, m)) > 0.3 * area(e.bbox) for m in mine_g):
                continue
            if e.kind == "rule":
                continue
            x0 = int((e.bbox[0] - clip.x0) * zoom) - 1
            y0 = int((e.bbox[1] - clip.y0) * zoom) - 1
            x1 = int((e.bbox[2] - clip.x0) * zoom) + 2
            y1 = int((e.bbox[3] - clip.y0) * zoom) + 2
            # no borrar encima de texto propio
            for m in mine_t:
                my0 = int((m[1] - clip.y0) * zoom)
                my1 = int((m[3] - clip.y0) * zoom)
                mx0 = int((m[0] - clip.x0) * zoom)
                mx1 = int((m[2] - clip.x0) * zoom)
                if x0 < mx1 and mx0 < x1 and y0 < my1 and my0 < y1:
                    # recorta verticalmente el blanqueo para no tapar la línea propia
                    if my0 >= y0 and my0 < y1:
                        y1 = min(y1, my0)
                    elif my1 > y0:
                        y0 = max(y0, my1)
            if y1 > y0 and x1 > x0:
                arr[max(0, y0):max(0, y1), max(0, x0):max(0, x1)] = 255
        segs.append(Image.fromarray(arr))
    if not segs:
        return None
    segs = [trim(s) for s in segs]
    segs = [s for s in segs if s is not None]
    if not segs:
        return None
    gap = int(10 * zoom)
    W = max(s.width for s in segs)
    H = sum(s.height for s in segs) + gap * (len(segs) - 1)
    out = Image.new("RGB", (W, H), "white")
    y = 0
    for s in segs:
        out.paste(s, (0, y))
        y += s.height + gap
    pad = int(8 * zoom)
    framed = Image.new("RGB", (W + 2 * pad, H + 2 * pad), "white")
    framed.paste(out, (pad, pad))
    return framed


def trim(img):
    a = np.asarray(img.convert("L"))
    ys, xs = np.where(a < 235)
    if len(ys) == 0:
        return None
    return img.crop((0, max(0, ys.min() - 2), img.width, min(img.height, ys.max() + 3)))


def trim_x(img):
    a = np.asarray(img.convert("L"))
    ys, xs = np.where(a < 235)
    if len(xs) == 0:
        return img
    return img.crop((max(0, xs.min() - 16), 0, min(img.width, xs.max() + 17), img.height))


def is_gray(img):
    a = np.asarray(img).astype(np.int16)
    return int(np.abs(a[..., 0] - a[..., 1]).max()) < 24 and int(np.abs(a[..., 1] - a[..., 2]).max()) < 24


def save_img(img, path):
    img = trim_x(img)
    if is_gray(img):
        img = img.convert("L")
    img.save(path, "WEBP", quality=80, method=6)
    return img.size


def qtext(q):
    parts = []
    qid = id(q)
    for r in q["rows"]:
        parts.append(" ".join(e.text.strip() for e in r["els"] if e.owner == qid))
    t = " ".join(parts)
    t = re.sub(r"\.{4,}", " … ", t)
    return re.sub(r"\s+", " ", t).strip()


def content_xrange(per_page, pr):
    xs0, xs1 = [], []
    for els in per_page.values():
        for e in els:
            if e.role is None and e.owner:
                xs0.append(e.bbox[0])
                xs1.append(e.bbox[2])
    if not xs0:
        return (0, pr.width)
    return (max(0, min(xs0) - 6), min(pr.width, max(xs1) + 6))


MERGE_RX = re.compile(r"(pregunta anterior|misma[s]? (imagen|imágenes|figura|esquema)|mismo esquema|imagen anterior|figura anterior|imágenes anteriores|esquema anterior|figuras anteriores)", re.I)


def exam_key(ex):
    base = f"{ex['year']}-{nfold(ex['label']).replace(' ', '')}"
    if ex["conv"]:
        base += "-" + nfold(ex["conv"])[:4]
    return base


def process_exam(ex):
    er = era(ex["year"])
    ocr = ex["year"] == 2009
    key = exam_key(ex)
    epath = os.path.join(RAW, ex["exam"])
    crit = ex["crit"]
    if isinstance(crit, list):
        crit = next(c for c in crit if os.path.exists(os.path.join(RAW, c)))
    cpath = os.path.join(RAW, crit)
    pdf = pymupdf.open(epath)
    pages = ex["exam_pages"] or list(range(len(pdf)))
    qs, per_page, events = parse_doc(pdf, pages, er, ocr, "exam")
    ph = pdf[pages[0]].rect.height
    assign_graphics(qs, per_page, events, ph)

    # criterios
    cpdf = pymupdf.open(cpath)
    cpages = ex["crit_pages"] or list(range(len(cpdf)))
    cqs, cper, cev = parse_doc(cpdf, cpages, er, ocr, "crit")
    assign_graphics(cqs, cper, cev, cpdf[cpages[0]].rect.height)

    xr = content_xrange(per_page, pdf[pages[0]].rect)
    cxr = content_xrange(cper, cpdf[cpages[0]].rect)

    # fusionar preguntas que dependen de la imagen de la anterior (era 1: 6-7)
    groups = []
    for q in qs:
        t = qtext(q)
        if groups and er == 1 and MERGE_RX.search(t[:160]) and groups[-1][-1]["sec"] == q["sec"]:
            groups[-1].append(q)
        else:
            groups.append([q])

    cmap = {}
    for c in cqs:
        cmap.setdefault((c["sec"], c["num"]), c)

    os.makedirs(os.path.join(OUT, "img", "q"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "img", "c"), exist_ok=True)
    results = []
    for grp in groups:
        sec = grp[0]["sec"]
        nums = [g["num"] for g in grp]
        numlabel = "-".join(nums) if len(nums) < 3 else f"{nums[0]}-{nums[-1]}"
        qid = f"{key}-{(sec or '').lower()}{numlabel}".replace(".", "_")
        imgs = [render_question(pdf, g, per_page, ZOOM_Q, xr) for g in grp]
        imgs = [i for i in imgs if i is not None]
        if not imgs:
            print("  !! sin imagen", qid, file=sys.stderr)
            continue
        img = vstack(imgs)
        qpath = f"img/q/{qid}.webp"
        size = save_img(img, os.path.join(OUT, qpath))
        crit_paths, ctexts = [], []
        for g in grp:
            c = cmap.get((g["sec"], g["num"])) or cmap.get((g["sec"], g["num"] + ".1"))
            if c is None:
                continue
            ci = render_question(cpdf, c, cper, ZOOM_C, cxr)
            if ci is None:
                continue
            cp = f"img/c/{qid}-{g['num'].replace('.', '_')}.webp"
            save_img(ci, os.path.join(OUT, cp))
            crit_paths.append(cp)
            ctexts.append(qtext(c))
        results.append({
            "id": qid,
            "exam": key,
            "year": ex["year"],
            "tipo": ex["tipo"],
            "conv": ex["conv"],
            "label": ex["label"],
            "era": er,
            "sec": sec,
            "num": numlabel,
            "text": " ".join(qtext(g) for g in grp),
            "crit_text": " ".join(ctexts),
            "img": qpath,
            "size": size,
            "crit": crit_paths,
            "src": ex["exam"],
            "ocr": ocr,
            "fig": any(e.owner == id(g) and e.kind == "graphic" and e.role is None
                       and area(e.bbox) > 1500 for g in grp for els in per_page.values() for e in els),
        })
    summary = f"{key:32s} q={len(qs):2d} groups={len(groups):2d} crit={len(cqs):2d} " + " ".join(
        f"{g[0]['sec']}{'+'.join(x['num'] for x in g)}" for g in groups)
    return results, summary


def vstack(imgs):
    if len(imgs) == 1:
        return imgs[0]
    W = max(i.width for i in imgs)
    H = sum(i.height for i in imgs)
    out = Image.new("RGB", (W, H), "white")
    y = 0
    for i in imgs:
        out.paste(i, (0, y))
        y += i.height
    return out


def main():
    filt = sys.argv[1] if len(sys.argv) > 1 else None
    allres = []
    dbp = os.path.join(OUT, "questions.json")
    if filt and os.path.exists(dbp):
        allres = [q for q in json.load(open(dbp)) if not str(q["year"]).startswith(filt)]
    for ex in E:
        if filt and not str(ex["year"]).startswith(filt):
            continue
        res, summ = process_exam(ex)
        print(summ, flush=True)
        allres.extend(res)
    allres.sort(key=lambda q: (q["year"], q["exam"], q["id"]))
    os.makedirs(OUT, exist_ok=True)
    json.dump(allres, open(dbp, "w"), ensure_ascii=False, indent=0)
    print("total", len(allres))


if __name__ == "__main__":
    main()
