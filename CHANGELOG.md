# Changelog

## 0.2.0 (2026-11-06)

- `is_derivative_slide` also matches tile names from the Kather TCGA tile archive (Zenodo 3784345) by slide-barcode prefix.
- `hechecks.tiles.tile_tint` and `he-checks tint`: whether background tiles are neutral glass; CRC-VAL-HE-7K's are all purple.
- `docs/kather-datasets.md`: the two traps, with the data behind them.

## 0.1.0 (draft, not released)

- `hechecks.stain`: stain-matrix check, per-image diagnosis, sign-safe Macenko estimator (uncentred or mean-centred), estimator harness.
- `hechecks.tcga` and `data/tcga_derivative_slides.csv`: the 25 TCGA-COAD/READ derivative diagnostic slides, re-checked against the live GDC API on 6 November 2026.
- CLI: `he-checks stain` (exit 0 ok, 1 suspect or unreadable, 2 degenerate), `he-checks tcga` (exit 1 if any id is listed).
