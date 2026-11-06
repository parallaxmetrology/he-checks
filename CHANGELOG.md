# Changelog

## 0.1.0 (draft, not released)

- `hechecks.stain`: stain-matrix check, per-image diagnosis, sign-safe Macenko estimator (uncentred or mean-centred), estimator harness.
- `hechecks.tcga` and `data/tcga_derivative_slides.csv`: the 25 TCGA-COAD/READ derivative diagnostic slides, re-checked against the live GDC API on 6 November 2026.
- CLI: `he-checks stain` (exit 0 ok, 1 suspect or unreadable, 2 degenerate), `he-checks tcga` (exit 1 if any id is listed).
