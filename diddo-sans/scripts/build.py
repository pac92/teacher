#!/usr/bin/env python3
"""Compila sources/DiddoSans-Bold.ufo en fonts/ (OTF, TTF con ttfautohint y WOFF2).

Uso:
    python scripts/build.py [--ufo sources/DiddoSans-Bold.ufo] [--out fonts]
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
NAME = "DiddoSans-Bold"


def run(cmd):
    print("$", " ".join(str(c) for c in cmd))
    subprocess.run([str(c) for c in cmd], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ufo", default=str(ROOT / "sources" / f"{NAME}.ufo"))
    ap.add_argument("--out", default=str(ROOT / "fonts"))
    args = ap.parse_args()
    out = Path(args.out)
    for sub in ("otf", "ttf", "webfonts"):
        (out / sub).mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        run([sys.executable, "-m", "fontmake", "-u", args.ufo, "-o", "otf", "ttf",
             "--output-dir", tmp, "--keep-overlaps"])  # los contornos ya vienen unidos
        shutil.copy(tmp / f"{NAME}.otf", out / "otf" / f"{NAME}.otf")
        run([sys.executable, "-m", "ttfautohint", "--no-info", tmp / f"{NAME}.ttf", out / "ttf" / f"{NAME}.ttf"])

    font = TTFont(out / "ttf" / f"{NAME}.ttf")
    font.flavor = "woff2"
    font.save(out / "webfonts" / f"{NAME}.woff2")
    for f in sorted(out.rglob(f"{NAME}.*")):
        print(f"{f.relative_to(ROOT) if f.is_relative_to(ROOT) else f}: {f.stat().st_size / 1024:.1f} KiB")


if __name__ == "__main__":
    main()
