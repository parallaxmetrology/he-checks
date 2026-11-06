# `tcga_derivative_slides.csv`

One row per affected diagnostic slide (25 rows: 17 TCGA-COAD, 8 TCGA-READ). Methods and caveats: [docs/derivative-slides.md](../docs/derivative-slides.md).

| column | meaning |
|---|---|
| `patient` | TCGA patient barcode |
| `project` | TCGA-COAD or TCGA-READ |
| `file_id` | GDC file UUID of the diagnostic slide |
| `file_name` | GDC file name |
| `md5` | GDC md5 checksum |
| `size_mib` | file size in MiB (2^20 bytes) |
| `width`, `height` | full-resolution size in pixels, read from the file |
| `idc_pixel_spacing_um` | pixel spacing stated by the IDC v25 DICOM copy, µm |
| `field_grid_um_per_px` | per-slide scan-field-grid bearing (mean of the two axes), COAD only |
| `tissue_area_um_per_px` | per-slide tissue-area bearing, COAD only |
| `structure_um_per_px` | per-slide structure-scale bearing, COAD only |

The three bearing columns are per-slide measurements kept for provenance. They disagree with each other slide by slide; use the cohort range (about 0.9–1.3 µm/px), not a single column, as a calibration.

Sources: GDC files API and slide headers (read 4 November 2026; file ids, names, sizes, md5s and projects re-checked against the live GDC API on 6 November 2026, all 25 matching); IDC v25 DICOM metadata. The listed fields are open-access TCGA metadata; the slides themselves are open-access files in GDC and IDC, subject to their data-use terms at [gdc.cancer.gov](https://gdc.cancer.gov). No images are included here.
