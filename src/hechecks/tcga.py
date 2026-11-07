"""The 25 TCGA colorectal diagnostic slides whose stated pixel spacing is wrong.

See data/README.md and docs/derivative-slides.md for provenance and methods.
"""
from __future__ import annotations

import csv
from functools import lru_cache
from importlib import resources
from pathlib import Path

_NAME = "tcga_derivative_slides.csv"


def _path() -> Path:
    try:
        p = resources.files("hechecks") / "data" / _NAME
        if p.is_file():
            return Path(str(p))
    except (ModuleNotFoundError, FileNotFoundError):
        pass
    return Path(__file__).resolve().parents[2] / "data" / _NAME  # source checkout


@lru_cache(maxsize=1)
def _rows() -> tuple[dict, ...]:
    with open(_path(), newline="") as f:
        return tuple(csv.DictReader(f))


def derivative_slides() -> tuple[dict, ...]:
    """All 25 rows as dicts (patient, project, file_id, file_name, ... per-slide bearings).

    Each call returns fresh copies, so changing a returned row does not change the list.
    """
    return tuple(dict(r) for r in _rows())


def is_derivative_slide(identifier: str) -> bool:
    """True if a GDC file id, slide file name, slide barcode, patient id or tile name is one of the 25.

    Tile names from the Kather TCGA tile archive (Zenodo 3784345) start with the
    slide barcode, e.g. `TCGA-AA-3496-01Z-00-DX1.B109..._(3663,2051).jpg`, and match
    on that prefix. Patient ids match on the diagnostic slide only: these patients'
    frozen (TS/BS) slides are regular scans and are not affected.
    """
    s = identifier.strip().replace("\\", "/").split("/")[-1].casefold()  # paths reduce to the file name
    for row in _rows():
        name = row["file_name"]
        barcode = name.split(".")[0]  # e.g. TCGA-AA-3488-01Z-00-DX1
        if s in {v.casefold() for v in (row["file_id"], name, barcode, row["patient"])}:
            return True
        if s.startswith(barcode.casefold() + "."):  # a tile or derived file named after the slide
            return True
    return False
