"""Genera el visor (carpeta visor/) y el zip final a partir de build/out.

- data/db.js: base de datos de preguntas (window.DB) para que funcione
  abriendo index.html directamente desde el disco (sin servidor).
- Detecta preguntas repetidas entre exámenes (mismo enunciado).
"""
import json
import os
import re
import shutil
import sys
import unicodedata
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from classify import TOPICS  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "build", "out")
SRC = os.path.join(ROOT, "visor-src")
VIS = os.path.join(ROOT, "build", "visor")
ZIP = os.path.join(ROOT, "selectividad-biologia-visor.zip")

LOMCE = {
    1: "La base molecular y fisicoquímica de la vida",
    2: "Morfología, estructura y funciones celulares",
    3: "Genética y evolución",
    4: "Microorganismos y sus aplicaciones. Biotecnología",
    5: "Inmunología: la autodefensa de los organismos",
}
LOMLOE = {
    "A": "Las biomoléculas",
    "B": "Genética molecular",
    "C": "Biología celular",
    "D": "Metabolismo",
    "E": "Biotecnología",
    "F": "Inmunología",
    "X": "Fuera del currículo LOMLOE (genética mendeliana)",
}


def fold(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return s


def shingles(text):
    t = fold(text)
    t = re.sub(r"\[[^\]]*\]", " ", t)  # puntuaciones [0,5]
    t = re.sub(r"^\s*(pregunta\s+)?[a-d]?\.?\s*\d+(\.\d)?\.?-?\s*(\(\d puntos\))?", " ", t)
    w = re.findall(r"[a-z0-9]+", t)
    w = [x for x in w if len(x) > 2]
    return {" ".join(w[i:i + 3]) for i in range(max(1, len(w) - 2))}


def find_dups(db):
    sh = [shingles(q["text"]) for q in db]
    dups = [[] for _ in db]
    for i in range(len(db)):
        a = sh[i]
        if len(a) < 4:
            continue
        for j in range(i + 1, len(db)):
            if db[i]["exam"] == db[j]["exam"]:
                continue
            b = sh[j]
            if len(b) < 4:
                continue
            inter = len(a & b)
            if inter and inter / min(len(a), len(b)) >= 0.8 and inter / max(len(a), len(b)) >= 0.55:
                dups[i].append(j)
                dups[j].append(i)
    return dups


def sec_label(q):
    if q["era"] == 1:
        return f"Opción {q['sec']}", f"Pregunta {q['num']}"
    if q["era"] == 2:
        return f"Bloque {q['sec']}", f"{q['sec']}.{q['num']}"
    return f"Ejercicio {q['sec']}", f"Pregunta {q['num']}"


def main():
    db = json.load(open(os.path.join(OUT, "questions.json")))
    dups = find_dups(db)
    ndup = sum(1 for d in dups if d)
    rows = []
    for i, q in enumerate(db):
        s1, s2 = sec_label(q)
        rows.append({
            "id": q["id"], "ex": q["exam"], "y": q["year"], "t": q["tipo"], "c": q["conv"],
            "l": q["label"], "e": q["era"], "s1": s1, "s2": s2,
            "tx": q["text"], "ct": q["crit_text"],
            "i": q["img"], "wh": q["size"], "cr": q["crit"],
            "tp": q["topics"], "b1": q["lomce"], "b2": q["lomloe"],
            "f": 1 if q.get("fig") else 0, "o": 1 if q["ocr"] else 0,
            "d": [db[j]["id"] for j in dups[i]], "src": q["src"],
        })
    meta = {
        "topics": {k: {"label": v[0], "lomce": v[1], "lomloe": v[2]} for k, v in TOPICS.items()},
        "lomce": LOMCE, "lomloe": LOMLOE,
    }
    if os.path.exists(VIS):
        shutil.rmtree(VIS)
    shutil.copytree(SRC, VIS)
    os.makedirs(os.path.join(VIS, "data"), exist_ok=True)
    with open(os.path.join(VIS, "data", "db.js"), "w") as fh:
        fh.write("window.DB=")
        json.dump({"meta": meta, "q": rows}, fh, ensure_ascii=False, separators=(",", ":"))
        fh.write(";\n")
    shutil.copytree(os.path.join(OUT, "img"), os.path.join(VIS, "img"))
    if os.path.exists(ZIP):
        os.remove(ZIP)
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(VIS):
            for f in sorted(files):
                p = os.path.join(root, f)
                arc = os.path.join("selectividad-biologia", os.path.relpath(p, VIS))
                # las imágenes webp ya van comprimidas
                ct = zipfile.ZIP_STORED if f.endswith(".webp") else zipfile.ZIP_DEFLATED
                zf.write(p, arc, compress_type=ct)
    print(f"{len(rows)} preguntas, {ndup} con repeticiones; zip {os.path.getsize(ZIP) / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
