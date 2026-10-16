#!/usr/bin/env python3
"""Descarga Montserrat en el commit fijado y verifica las sumas SHA-256.

Los archivos van a sources/upstream/ (ignorada en git). Si ya existen y la suma
coincide, no se vuelven a descargar.

Uso:  python scripts/fetch_upstream.py
"""

import hashlib
import sys
import urllib.request
from pathlib import Path

COMMIT = "555facfb2a18c72c3c0380f0d9c0f060453a9058"
BASE = f"https://raw.githubusercontent.com/JulietaUla/Montserrat/{COMMIT}/"
DEST = Path(__file__).resolve().parent.parent / "sources" / "upstream"

# ruta en el repositorio de Montserrat -> (nombre local, sha256)
FILES = {
    "sources/Montserrat.glyphs": (
        "Montserrat.glyphs",
        "da03bda8ca63f7820cd029373c6683bc48801903d5c031232f36045fb0a31c3d"),
    "fonts/variable/Montserrat%5Bwght%5D.ttf": (
        "Montserrat[wght].ttf",
        "1e2c44ef8c956ed66998649d8c832d221e22c04eaab63c044f18eb05d1c63b7c"),
    "OFL.txt": (
        "OFL.txt",
        "8b7141c03fa4f8d44e6345d5d4931709290f0f67875e452e95ac1fd3a027802e"),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    DEST.mkdir(parents=True, exist_ok=True)
    ok = True
    for remote, (local, expected) in FILES.items():
        target = DEST / local
        if target.exists() and sha256(target) == expected:
            print(f"ok         {local}")
            continue
        print(f"descargando {local} …")
        with urllib.request.urlopen(BASE + remote, timeout=120) as resp:
            data = resp.read()
        got = hashlib.sha256(data).hexdigest()
        if got != expected:
            print(f"ERROR: suma distinta en {local}\n  esperada {expected}\n  obtenida {got}",
                  file=sys.stderr)
            ok = False
            continue
        target.write_bytes(data)
        print(f"ok         {local}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
