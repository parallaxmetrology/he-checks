# Two traps in the Kather colorectal tile collections

Both collections are widely used for colorectal histology models and benchmarks. Neither problem raises an error; both change what a model or a measurement sees.

## 1. The TCGA tile archive mixes two pixel scales (Zenodo 3784345)

The Kather 2020 archive of TCGA colorectal tumour tiles (non-normalised, tumour only) describes every tile as 512 px at 0.5 µm/px. All 25 derivative patients from [derivative-slides.md](derivative-slides.md) are in it, and their tiles were made differently:

- **Regular Indivumed (site AA) slides** were tiled on a 1,101-px grid from scans at 0.2325 µm/px: 1,101 × 0.2325 ≈ 256 µm, reduced to 512 px, which matches the stated 0.5 µm/px.
- **Derivative slides** were tiled on a 200-px grid from the small derivative files and enlarged to 512 px (2.56×). At their likely true spacing of 0.9–1.3 µm/px, a tile spans about 180–260 µm, so 0.35–0.51 µm per tile pixel, and contains no detail finer than the derivative's own pixels: the tiles are blurred enlargements.
- Two derivative archives, TCGA-AA-3488 and TCGA-AG-3732, are 1,008 bytes and hold no tiles.
- In the 15 COAD derivative archives with tiles that we read, every tile origin lies within the derivative's 10,000-px frame.

**Check:** tile file names start with the slide barcode, so `hechecks.is_derivative_slide` works on them directly:

```python
import hechecks as hc
hc.is_derivative_slide("TCGA-AA-3496-01Z-00-DX1.B109A6F3-02E0-4181-B69A-00CBA758C074_(3663,2051).jpg")  # True
```

```bash
ls tiles/*.jpg | xargs he-checks tcga | grep DERIVATIVE
```

What the difference does in practice: in a measurement of 181 TCGA-COAD patients with a fixed, named feature set, the derivative patients stood apart from all other patients without any labels, led by pixel-distance features ([parallax-core42 worked example](https://github.com/parallaxmetrology/parallax-core42/tree/main/examples/tcga_route_fingerprint)). A model trained on this archive can learn the same thing.

Zenodo 2530835 (the CRC_DX tiles, 360 patients) contains none of the 25.

## 2. CRC-VAL-HE-7K background tiles are purple

CRC-VAL-HE-7K is distributed already Macenko-normalised by its authors. Its 847 background (`BACK`) tiles are **all** dark purple rather than near-white glass:

| collection | background tiles | mean RGB | brightness | colour spread (max − min channel) |
|---|---|---|---|---|
| CRC-VAL-HE-7K, as distributed | 847 (all) | 123, 79, 134 | median 104; none above 200 | median 54; minimum 37 |
| NCT-CRC-HE-100K-NONORM (unnormalised training set) | 400 (sample) | about 240, 240, 240 | median 243 | median 0.3 |

This is consistent with stain normalisation applied to a nearly empty image: there is almost no stain to estimate, and rescaling to a stained target paints the glass. It matters for:
- any brightness, tonal or "how much empty space" measure on this set (blank glass reads as a dark, stained region);
- models compared across normalised and unnormalised versions, or trained on one and tested on the other, where "background" means a different colour in each;
- error analyses that read the `BACK` class as glass.

We did not check the normalised training set (NCT-CRC-HE-100K) in the same way.

**Check:**

```python
hc.tile_tint(tile)
# TileTint(mean_rgb=(123.2, 79.1, 134.2), brightness=..., colour_spread=..., status='tinted')
```

`tile_tint` is meant for tiles that should be blank. It reports `tinted` when the channel means differ by more than 20, `dark` when neutral but darker than 200, and `neutral` otherwise; the thresholds come from the two collections above. Tissue tiles are tinted by design.

## Sources

- Kather JN. Image tiles of TCGA-CRC-DX histological whole slide images, non-normalized, tumor only. Zenodo 2020. doi:10.5281/zenodo.3784345
- Kather JN. Histological images for MSI vs. MSS classification in gastrointestinal cancer, FFPE samples. Zenodo 2019. doi:10.5281/zenodo.2530835
- Kather JN, Halama N, Marx A. 100,000 histological images of human colorectal cancer and healthy tissue. Zenodo 2018. doi:10.5281/zenodo.1214456 (NCT-CRC-HE-100K, NCT-CRC-HE-100K-NONORM, CRC-VAL-HE-7K)
- Kather JN et al. Predicting survival from colorectal cancer histology slides using deep learning. *PLOS Medicine* 2019;16(1):e1002730.
- Parallax Metrology, [TCGA derivative slides technical note](https://www.parallaxmetrology.com/TCGA_Derivative_Slides_NOTE.html) and [stain-normaliser technical note](https://www.parallaxmetrology.com/Stain_Normaliser_NOTE.html).
