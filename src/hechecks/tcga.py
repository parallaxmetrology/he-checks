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
def derivative_slides() -> tuple[dict, ...]:
    """All 25 rows as dicts (patient, project, file_id, file_name, ... per-slide bearings)."""
    with open(_path(), newline="") as f:
        return tuple(csv.DictReader(f))


def is_derivative_slide(identifier: str) -> bool:
    """True if a GDC file id, slide file name, slide barcode or patient id is one of the 25.

    Patient ids match on the diagnostic slide only: these patients' frozen
    (TS/BS) slides are regular scans and are not affected.
    """
    s = identifier.strip().replace("\\", "/").split("/")[-1].casefold()  # paths reduce to the file name
    for row in derivative_slides():
        name = row["file_name"]
        barcode = name.split(".")[0]  # e.g. TCGA-AA-3488-01Z-00-DX1
        if s in {v.casefold() for v in (row["file_id"], name, barcode, row["patient"])}:
            return True
    return False
