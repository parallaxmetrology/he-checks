# he-checks

**Two quiet failures in H&E image pipelines, and a check for each.**

Neither raises an error, and both quietly change what gets measured downstream.

1. **Macenko stain vectors that have collapsed into one.** An SVD sign convention can put every tissue pixel on the wrap of `arctan2`, so the "haematoxylin" and "eosin" vectors come back a fraction of a degree apart. It is a known pitfall that established libraries guard against, but a hand-written estimator still runs without it. We found it in our own TCGA work: 0.17° between H and E, against about 14° once fixed. With numpy, an uncentred estimator without the sign check collapsed on all 60 TCGA colorectal tiles we tested.
2. **25 TCGA colorectal slides whose stated pixel spacing is wrong.** 17 TCGA-COAD and 8 TCGA-READ diagnostic slides are small derivative files. IDC states 0.5 µm/px for them; independent measurements put the true value near 0.9–1.3 µm/px, so each pixel covers roughly twice the stated width.

## Install

```bash
pip install "he-checks @ git+https://github.com/parallaxmetrology/he-checks"
```

Python 3.9+, numpy and Pillow.

## 1. Check your stain estimator

```python
import numpy as np
from PIL import Image
import hechecks as hc

tile = np.asarray(Image.open("tile.png").convert("RGB"))

hc.diagnose_image(tile)          # on the TCGA reference tile in docs/stain-sign.md:
# ImageDiagnosis(tissue_pixels=178417, share_negative_on_axis0=1.0, straddles_wrap=True,
#                naive_angle_deg=0.17, safe_angle_deg=14.5, status='degenerate')

hc.check_stain_matrix(my_pipeline.stain_matrix)        # a 2 x 3 matrix, row 0 = H
hc.check_estimator(my_pipeline.estimate, tiles)        # your estimator over many tiles
M = hc.macenko_stain_matrix(tile)                      # sign-safe reference estimate
```

```bash
he-checks stain tiles/*.png   # one JSON line per tile; exit 0 ok, 1 suspect or unreadable, 2 degenerate
```

`diagnose_image` runs the textbook uncentred estimator twice, as written and with the first axis oriented toward the tissue, and reports both. `status` describes the naive estimate: `degenerate` (H/E angle under 2°), `suspect` (under 5°) or `ok`. The thresholds are heuristics from TCGA tiles, where sign-safe estimates had medians of 14–16° and none fell under 10° in a 60-tile check; a tile that is nearly all one stain can be small for real reasons. Mechanism, numbers and limits: [docs/stain-sign.md](docs/stain-sign.md).

## 2. Flag the mis-scaled TCGA slides

```python
hc.is_derivative_slide("TCGA-AA-3488-01Z-00-DX1")       # True
hc.is_derivative_slide("b8085eff-8407-4fd5-b2ba-70fa649aa07d")  # GDC file id: True
hc.derivative_slides()                                  # all 25 rows
```

```bash
he-checks tcga TCGA-AA-3488 TCGA-AA-3514    # exit code 1 if any is on the list
```

The list is also a plain CSV: [data/tcga_derivative_slides.csv](data/tcga_derivative_slides.csv). Patient ids match the diagnostic slide only; the same patients' frozen sections are ordinary scans.

| bearing on the 17 COAD slides | cohort median, µm/px |
|---|---|
| scanner field grid in the scanned-area outline | 0.90 (IQR 0.82–0.98) |
| tissue area | 1.20 |
| structure scale | 1.26 |
| grid ratio of a public tile archive cut from them | 1.28 |
| **stated by IDC** | **0.5** |

We reported the slides to the IDC and GDC helpdesks on 6 November 2026. Per-slide values disagree with each other; use the cohort range, not a per-slide number. If you use physical scale (µm, magnification-matched tiles, nucleus size, cells per mm²), exclude these slides or treat their scale as unknown. Methods: [docs/derivative-slides.md](docs/derivative-slides.md) and the [technical note](https://www.parallaxmetrology.com/TCGA_Derivative_Slides_NOTE.html).

## What this does not do

- It does not judge whether stain vectors are *good*, only whether they have collapsed.
- It does not cover other normalisers (Reinhard, Vahadane, learned ones), or other TCGA projects.
- It does not say any particular library has the sign problem; established ones correct the sign. Run the check on the code you actually use.
- It does not give a calibrated pixel spacing for any single derivative slide. Nobody we know of has one.

## Tests

```bash
pip install -e ".[dev]" && pytest
```

The tests build synthetic H&E tiles from known stain vectors, force the bad sign and check that the collapse is detected, check the slide list against the published note, and exercise the command line.

## Contribute

- Run `check_estimator` on the stain step of a pipeline you use and report what it finds, collapsed or not.
- If you know how the 0.5 µm/px value was assigned to these slides, or whether full-resolution originals exist, open an issue.
- Know another silent failure of this kind in H&E data? That is the most useful issue there is.

## Part of Parallax Metrology

Deterministic structural measurement across domains. Siblings: [visual-thinking-lens](https://github.com/parallaxmetrology/visual-thinking-lens), [structural-topology-kernel](https://github.com/parallaxmetrology/structural-topology-kernel), [how-measures-lie](https://github.com/parallaxmetrology/how-measures-lie) (nineteen ways an image measure returns a plausible, wrong number). Pathology work and its claim ledger: [parallaxmetrology.com](https://www.parallaxmetrology.com/parallax_pathology_pm.html).

## License and data

Code: MIT ([LICENSE](LICENSE)). Documentation: CC BY 4.0 ([LICENSE-CONTENT](LICENSE-CONTENT)). The slide list contains open-access TCGA metadata from GDC and IDC and no images.

## Cite

See [CITATION.cff](CITATION.cff). Russell Parrish, Parallax Metrology, with analysis carried out with Claude (Anthropic).
