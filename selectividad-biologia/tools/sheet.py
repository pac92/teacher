"""Hoja de revisión visual: todas las preguntas de un examen en una imagen."""
import json
import os
import sys

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "build", "out")
REV = os.path.join(ROOT, "build", "review")


def sheet(exam, qs, W=420, crit=False, cols=4):
    ims = []
    for q in qs:
        paths = [q["img"]] + (q["crit"] if crit else [])
        for p in paths:
            im = Image.open(os.path.join(OUT, p)).convert("RGB")
            s = W / im.width
            im = im.resize((W, max(1, int(im.height * s))))
            lab = Image.new("RGB", (W, 18), (255, 230, 150) if p == q["img"] else (200, 230, 255))
            ImageDraw.Draw(lab).text((4, 3), f"{q['sec']}{q['num']} {os.path.basename(p)}", fill="black")
            ims.append((lab, im))
    colh = [0] * cols
    place = []
    for lab, im in ims:
        c = colh.index(min(colh))
        place.append((c, colh[c], lab, im))
        colh[c] += lab.height + im.height + 8
    out = Image.new("RGB", (cols * (W + 10), max(colh)), (120, 120, 120))
    for c, y, lab, im in place:
        out.paste(lab, (c * (W + 10), y))
        out.paste(im, (c * (W + 10), y + lab.height))
    os.makedirs(REV, exist_ok=True)
    p = os.path.join(REV, exam + ("-c" if crit else "") + ".png")
    out.save(p)
    return p


if __name__ == "__main__":
    db = json.load(open(os.path.join(OUT, "questions.json")))
    pat = sys.argv[1]
    crit = "-c" in sys.argv
    exams = sorted({q["exam"] for q in db if q["exam"].startswith(pat)})
    for e in exams:
        print(sheet(e, [q for q in db if q["exam"] == e], crit=crit))
