# Changelog

## 0.2.1 (2026-11-07)

Fixes from a second code review; results on 8-bit images are unchanged (re-checked on the TCGA reference tile and all 847 CRC-VAL-HE-7K background tiles).

- Float images in 0-1, uint16 and RGBA input were read as if they were 8-bit and gave silently wrong answers (a 0-1 glass tile read as "dark"; a stain angle of 7° instead of 34°). All checks now rescale to 0-255 first, and reject non-finite, out-of-range, boolean and empty images.
- `check_stain_matrix` reported a matrix with an all-zero row as "ok" and crashed on NaN; both now return status "invalid".
- `alpha` outside 0-50 was accepted silently; it now raises.
- Rows returned by `derivative_slides()` are copies, so editing one no longer changes the list.
- The pipeline example stops with a message when the folder has no tiles.

## 0.2.0 (2026-11-06)

- `is_derivative_slide` also matches tile names from the Kather TCGA tile archive (Zenodo 3784345) by slide-barcode prefix.
- `hechecks.tiles.tile_tint` and `he-checks tint`: whether background tiles are neutral glass; CRC-VAL-HE-7K's are all purple.
- `docs/kather-datasets.md`: the two traps, with the data behind them.

## 0.1.0 (draft, not released)

- `hechecks.stain`: stain-matrix check, per-image diagnosis, sign-safe Macenko estimator (uncentred or mean-centred), estimator harness.
- `hechecks.tcga` and `data/tcga_derivative_slides.csv`: the 25 TCGA-COAD/READ derivative diagnostic slides, re-checked against the live GDC API on 6 November 2026.
- CLI: `he-checks stain` (exit 0 ok, 1 suspect or unreadable, 2 degenerate), `he-checks tcga` (exit 1 if any id is listed).
