# 25 TCGA colorectal slides with the wrong pixel spacing

## The slides

Of the TCGA-COAD and TCGA-READ diagnostic (DX) slides in GDC, 25 from tissue source sites AA and AG (17 COAD, 8 READ, all Indivumed) are small derivative files rather than scanner output:

- JPEG 2000 compression, long edge exactly 10,000 px, 4.7–12.8 MiB;
- no microns-per-pixel or magnification tag in the file;
- their DICOM copies in the Imaging Data Commons (IDC v25) state `PixelSpacing` 0.0005 mm, i.e. **0.5 µm/px**.

Every other AA and AG diagnostic slide in IDC states 0.23 µm/px (228 series), apart from these. The same patients' frozen sections (TS, BS) are ordinary scans at about 0.50 µm/px and are not affected.

## How far off

The true spacing is not recorded anywhere we could find. Three kinds of measurement on the 17 COAD slides, each independent of the stated value, place it near 0.9–1.3 µm/px:

| bearing | what it uses | cohort median (µm/px) |
|---|---|---|
| scan-field grid | the scanner camera's field grid, visible in the outline of the scanned area, sized on regular AA slides of known scale | **0.90** (IQR 0.82–0.98) |
| tissue area | slide tissue area matched to the patients' regular slides | 1.20 |
| structure scale | the autocorrelation scale of tissue texture matched to regular slides | 1.26 |
| tile archive | the pixel-grid ratio implied by a public tile archive cut from these slides | 1.28 |

The scan-field grid is the most direct of these. Every median and IQR, and every per-slide value from the three measured bearings (lowest 0.54), is above 0.5 µm/px: the true pixels are roughly 2× (between about 1.8× and 2.6×) larger than stated. The 8 READ slides share the file format, site, size and IDC value, and were not measured separately.

**Per-slide values in the CSV are noisy.** The per-slide bearings do not agree with each other (Spearman ρ 0.04 between tissue area and structure scale; the structure bearing is accurate to about ±40% on held-out slides). Use the cohort range, not a per-slide column, as a calibration.

## What to do with them

- In any analysis that uses physical scale (µm, magnification-matched tiling, nucleus size, density per mm²), exclude these slides or treat their scale as unknown within about 0.9–1.3 µm/px.
- In analyses at a fixed pixel size, note that their tiles cover roughly 2× more tissue per side than the same pixel size elsewhere in TCGA, and carry the flag as a covariate or sensitivity exclusion.
- Tile archives cut from these slides inherit the problem. In the Kather et al. 2020 TCGA tile archive (Zenodo 3784345), all 25 are present as 200-px crops enlarged to 512 px.

## Status

Reported to the IDC and GDC helpdesks on 6 November 2026; no reply yet. If you know how the 0.5 value was assigned, or whether full-resolution originals exist, please open an issue.

Full methods and figures: the [technical note on parallaxmetrology.com](https://www.parallaxmetrology.com/TCGA_Derivative_Slides_NOTE.html).
