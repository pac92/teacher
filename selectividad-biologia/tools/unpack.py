"""Descomprime los zips de zips/ en build/raw/<año>/ normalizando los nombres
de fichero a ASCII (los zips usan cp850 y secuencias #U00cd)."""
import os
import re
import sys
import unicodedata
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZIPS = os.path.join(ROOT, "zips")
OUT = os.path.join(ROOT, "build", "raw")


def norm(name):
    name = name.replace("#U00cd", "Í").replace("#U00ed", "í")
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9._/-]+", "_", name)


def main():
    for z in sorted(os.listdir(ZIPS)):
        m = re.match(r"sel_(\d{4})_biologia\.zip", z)
        if not m:
            continue
        year = m.group(1)
        with zipfile.ZipFile(os.path.join(ZIPS, z)) as zf:
            for info in zf.infolist():
                if info.is_dir():
                    continue
                raw = info.filename
                if not info.flag_bits & 0x800:  # nombre no UTF-8 -> cp850
                    raw = raw.encode("cp437").decode("cp850")
                dest = os.path.join(OUT, year, norm(raw))
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                with open(dest, "wb") as fh:
                    fh.write(zf.read(info))
    print("ok", OUT, file=sys.stderr)


if __name__ == "__main__":
    main()
