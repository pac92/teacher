#!/usr/bin/env python3
"""Resume los informes JSON de fontbakery en qa/README.md y falla si hay FAIL/FATAL."""

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QA = ROOT / "qa"


def results(report):
    for section in report.get("sections", []):
        for check in section.get("checks", []):
            yield check


def _msg(log) -> str:
    m = log.get("message", "")
    if isinstance(m, dict):
        m = f"{m.get('message', '')} [{m.get('code', '')}]"
    return " ".join(str(m).split())[:200]


def main():
    lines = ["# Control de calidad (fontbakery check-universal)", ""]
    bad = False
    for path in sorted(QA.glob("fontbakery-*.json")):
        rep = json.loads(path.read_text())
        checks = list(results(rep))
        counts = Counter(c["result"] for c in checks)
        lines.append(f"## {path.stem.replace('fontbakery-', '').upper()}")
        lines.append("")
        lines.append(" · ".join(f"{k}: {counts[k]}" for k in ("FATAL", "FAIL", "ERROR", "WARN", "INFO", "PASS", "SKIP") if counts[k]))
        lines.append("")
        for c in checks:
            if c["result"] in ("FATAL", "FAIL", "ERROR", "WARN"):
                msgs = "; ".join(_msg(m) for m in c.get("logs", []) if m.get("status") == c["result"])
                check_id = c["key"][1].removeprefix("<FontBakeryCheck:").removesuffix(">")
                lines.append(f"- **{c['result']}** `{check_id}`: {msgs}")
                bad |= c["result"] in ("FATAL", "FAIL")
        lines.append("")
    (QA / "README.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
