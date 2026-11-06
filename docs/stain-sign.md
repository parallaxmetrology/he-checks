# The Macenko sign wrap

## What happens

Macenko stain estimation (Macenko et al., 2009) takes the optical density (OD) of tissue pixels, finds the plane that holds most of it, measures each pixel's angle in that plane with `arctan2`, and returns the directions at the 1st and 99th percentile angles as haematoxylin and eosin.

The plane comes from an SVD or an eigen-decomposition, and those vectors are defined only up to sign. If the first axis points away from the tissue, every tissue pixel has a negative coordinate on it, and every pixel angle sits close to +180° or -180°: on the wrap of `arctan2`. Sorted, the angles split into two clumps at the two ends of the range. The 1st percentile lands in the clump near -180° and the 99th in the clump near +180°. Both describe almost the same direction.

The result is a stain matrix with two nearly identical rows. It is finite, normalised and invertible, so nothing downstream raises an error. Unmixing with it is badly conditioned: the "H" and "E" concentrations it returns are mostly the same signal split in two, and the normalised image is mainly a brightness and colour rescaling.

Mean-centring the OD before the decomposition (as covariance-based implementations do) or orienting the first axis toward the tissue before taking angles both avoid it.

## How it was found

In August and November 2026 we audited earlier TCGA-COAD analyses of our own. Their stain normalisation used an uncentred `numpy.linalg.svd` with no orientation step. On its reference tile (`TCGA-AA-3710-01Z-00-DX1`, tile at (12916, 16341) in the Kather et al. 2020 TCGA tile archive):

| estimate | H row, E row (R, G, B OD) | H/E angle |
|---|---|---|
| historical, as written | [0.5378, 0.7968, 0.2754] and [0.5362, 0.7986, 0.2735] | 0.17° |
| the same estimator with the first axis oriented | [0.599, 0.719, 0.352] and [0.467, 0.863, 0.192] | 14.5° |
| mean-centred (`centre=True`), oriented | [0.604, 0.716, 0.349] and [0.485, 0.856, 0.178] | 14.4° |
| Ruifrok and Johnston reference vectors | [0.65, 0.70, 0.29] and [0.07, 0.99, 0.11] | 39.4° |

The mean-centred estimate matches the corrected reference matrix (within 0.001 on every entry) in our own frozen instrument release, which was computed independently. On that tile every tissue pixel (178,417 of 178,417) had a negative first-axis coordinate, and the 1st and 99th percentile angles were -179.9° and +179.9°.

Across 312 tiles from three TCGA-COAD slide groups, the historical estimator returned medians of 0.13–0.17° (96–100% of tiles under 2°); the same estimator with mean-centring returned medians of 14.0–15.8°. On a separate random draw of 60 tiles from 20 slides, made while writing this package, the naive angle was below 2° on all 60 (median 0.16°) and the sign-safe angle had median 16.4° (minimum 10.6°). numpy 2.4.2, macOS arm64.

Results of ours that depended on that normaliser were retracted or recomputed. Which ones, and why, is recorded in the [stain-normaliser technical note](https://www.parallaxmetrology.com/Stain_Normaliser_NOTE.html) and the [claim ledger](https://www.parallaxmetrology.com/Parallax_Pathology_Claim_Ledger.html).

## Thresholds

`check_stain_matrix` calls an H/E angle under 2° **degenerate** and under 5° **suspect**. These are heuristics from the tiles above, where healthy estimates sat at 10–20° and collapsed ones under 1°. They are not universal constants: a section stained almost entirely with one dye, or a tile that is mostly background, can legitimately give a small angle. A small angle is a reason to look, and `diagnose_image` shows whether the wrap is the cause (`straddles_wrap` true, `share_negative_on_axis0` near 1).

## What this does not check

- Whether the estimated vectors are good stain vectors, only whether they have collapsed into one.
- Other normalisers (Reinhard, Vahadane, learned ones).
- Whether a library you use has this problem. Several widely used implementations orient their vectors or mean-centre; run `check_estimator` on your own estimator rather than assume either way.

## Reference

Macenko M, Niethammer M, Marron JS, et al. A method for normalizing histology slides for quantitative analysis. *IEEE ISBI* 2009: 1107–1110.
Ruifrok AC, Johnston DA. Quantification of histochemical staining by color deconvolution. *Analytical and Quantitative Cytology and Histology* 2001; 23(4): 291–299.
