"""Command line: `he-checks stain <images...>`, `he-checks tcga <ids...>`, `he-checks tint <images...>`."""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np


def _stain(paths: list[str], centre: bool) -> int:
    from PIL import Image

    from .stain import diagnose_image

    worst = 0
    for p in paths:
        try:
            d = diagnose_image(np.asarray(Image.open(p).convert("RGB")), centre=centre)
        except (OSError, ValueError) as e:  # unreadable file, or too little tissue to estimate
            print(json.dumps({"image": p, "status": "error", "error": str(e)}))
            worst = max(worst, 1)
            continue
        print(json.dumps({"image": p, **d.as_dict()}))
        worst = max(worst, {"ok": 0, "suspect": 1, "degenerate": 2}[d.status])
    return worst


def _tcga(ids: list[str]) -> int:
    from .tcga import is_derivative_slide

    hit = 0
    for i in ids:
        flag = is_derivative_slide(i)
        hit |= flag
        print(f"{i}\t{'DERIVATIVE: stated pixel spacing unreliable' if flag else 'not in list'}")
    return int(hit)


def _tint(paths: list[str]) -> int:
    from PIL import Image

    from .tiles import tile_tint

    flagged = 0
    for p in paths:
        try:
            t = tile_tint(np.asarray(Image.open(p).convert("RGB")))
        except (OSError, ValueError) as e:
            print(json.dumps({"image": p, "status": "error", "error": str(e)}))
            flagged = 1
            continue
        print(json.dumps({"image": p, **t.as_dict()}))
        flagged |= t.status != "neutral"
    return int(flagged)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="he-checks")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("stain", help="diagnose Macenko stain estimation on RGB images")
    s.add_argument("images", nargs="+")
    s.add_argument("--centre", action="store_true", help="mean-centre OD before the SVD")
    t = sub.add_parser("tcga", help="flag TCGA slides with unreliable pixel spacing")
    t.add_argument("ids", nargs="+", help="GDC file ids, slide file names, barcodes or patient ids")
    b = sub.add_parser("tint", help="check whether background tiles are neutral glass")
    b.add_argument("images", nargs="+")
    a = ap.parse_args(argv)
    if a.cmd == "stain":
        return _stain(a.images, a.centre)
    return _tcga(a.ids) if a.cmd == "tcga" else _tint(a.images)


if __name__ == "__main__":
    sys.exit(main())
