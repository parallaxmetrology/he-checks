"""Checks for Macenko-style H&E stain-vector estimation.

The Macenko method projects tissue optical density (OD) onto a plane found by
SVD or eigen-decomposition, measures each pixel's angle in that plane, and takes
the angles at the alpha and 100 - alpha percentiles as the two stain directions.

Singular and eigen vectors are only defined up to sign. If the first plane axis
comes out pointing away from the tissue (every pixel has a negative coordinate
on it), every pixel angle sits near +/-180 degrees, on the wrap of arctan2. The
low and high percentiles then fall on either side of that wrap, a fraction of a
degree from the same direction, and the two "stain" vectors are nearly
parallel. Nothing raises an error: the matrix is finite, normalised and
invertible, only very badly conditioned.

This module measures that failure on a stain matrix, on an image, and on any
estimator you pass in, and provides a sign-safe reference estimator.
"""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict, dataclass
from typing import Callable

import numpy as np

# Thresholds are heuristics from TCGA colorectal tiles (docs/stain-sign.md):
# healthy per-tile estimates had median H/E angles of 14-16 degrees; collapsed
# ones had medians of 0.13-0.17 degrees, 96-100% of tiles under 2 degrees.
DEGENERATE_DEG = 2.0
SUSPECT_DEG = 5.0

# Ruifrok and Johnston (2001) reference vectors, for orientation only.
RUIFROK_H = np.array([0.65, 0.70, 0.29])
RUIFROK_E = np.array([0.07, 0.99, 0.11])


def angle_deg(a: np.ndarray, b: np.ndarray) -> float:
    """Unsigned angle between two directions in degrees (sign of each ignored)."""
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    c = abs(a @ b) / (np.linalg.norm(a) * np.linalg.norm(b))
    return float(np.degrees(np.arccos(np.clip(c, -1.0, 1.0))))


def optical_density(image: np.ndarray, beta: float = 0.15) -> np.ndarray:
    """Per-pixel OD of an RGB uint8 image, keeping pixels with OD > beta in every channel."""
    rgb = np.asarray(image)
    if rgb.ndim != 3 or rgb.shape[2] < 3:
        raise ValueError("expected an H x W x 3 RGB image")
    od = -np.log(np.clip(rgb[..., :3].astype(float) / 255.0, 1e-6, 1.0)).reshape(-1, 3)
    return od[np.all(od > beta, axis=1)]


@dataclass
class MatrixCheck:
    angle_deg: float          # angle between the two stain rows
    condition_number: float   # of the 3x2 matrix used to unmix
    h_vs_ruifrok_h_deg: float
    e_vs_ruifrok_e_deg: float
    status: str               # "ok", "suspect" or "degenerate"

    def as_dict(self) -> dict:
        return asdict(self)


def check_stain_matrix(matrix: np.ndarray) -> MatrixCheck:
    """Check a 2 x 3 stain matrix (row 0 = H, row 1 = E) for collapse.

    The angle between the rows is the main reading. Two distinct stains measured
    on real tissue are rarely closer than a few degrees; a fraction of a degree
    means the estimator returned one direction twice.
    """
    m = np.asarray(matrix, float)
    if m.shape == (3, 2):
        m = m.T
    if m.shape != (2, 3):
        raise ValueError("expected a 2 x 3 (or 3 x 2) stain matrix")
    a = angle_deg(m[0], m[1])
    cond = float(np.linalg.cond(m.T))
    status = "degenerate" if a < DEGENERATE_DEG else "suspect" if a < SUSPECT_DEG else "ok"
    return MatrixCheck(a, cond, angle_deg(m[0], RUIFROK_H), angle_deg(m[1], RUIFROK_E), status)


def _plane(od: np.ndarray, centre: bool) -> np.ndarray:
    x = od - od.mean(0) if centre else od
    _, _, vt = np.linalg.svd(x, full_matrices=False)
    return vt[:2].T.copy()


def _extremes(od: np.ndarray, plane: np.ndarray, alpha: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    proj = od @ plane
    phi = np.arctan2(proj[:, 1], proj[:, 0])
    lo, hi = np.percentile(phi, [alpha, 100 - alpha])
    v1 = plane @ np.array([np.cos(lo), np.sin(lo)])
    v2 = plane @ np.array([np.cos(hi), np.sin(hi)])
    return v1, v2, phi


def _order(v1: np.ndarray, v2: np.ndarray) -> np.ndarray:
    m = np.array([v1, v2], dtype=float)
    m = m * np.where(m.sum(axis=1, keepdims=True) < 0, -1.0, 1.0)  # point both into positive OD
    m = m / np.linalg.norm(m, axis=1, keepdims=True)
    # Haematoxylin absorbs red more strongly than eosin: put the larger red OD first.
    return m if m[0, 0] >= m[1, 0] else m[::-1].copy()


def macenko_stain_matrix(image: np.ndarray, beta: float = 0.15, alpha: float = 1.0,
                         centre: bool = False) -> np.ndarray:
    """Sign-safe Macenko estimate: a 2 x 3 matrix, row 0 = H, row 1 = E.

    The first plane axis is oriented so tissue projects positively onto it
    before angles are taken, which keeps the pixel angles away from the
    arctan2 wrap. `centre=True` mean-centres OD before the SVD (equivalent to
    the covariance eigen-decomposition several libraries use).
    """
    od = optical_density(image, beta)
    if len(od) < 10:
        raise ValueError("too few tissue pixels above beta")
    plane = _plane(od, centre)
    if (od @ plane[:, 0]).mean() < 0:
        plane[:, 0] *= -1
    v1, v2, _ = _extremes(od, plane, alpha)
    return _order(v1, v2)


@dataclass
class ImageDiagnosis:
    tissue_pixels: int
    share_negative_on_axis0: float  # share of tissue pixels with a negative first-axis coordinate
    straddles_wrap: bool            # low and high percentile angles on opposite sides of +/-180
    naive_angle_deg: float          # H/E angle from the estimator as written, without the sign fix
    safe_angle_deg: float           # H/E angle after orienting the first axis
    status: str

    def as_dict(self) -> dict:
        return asdict(self)


def diagnose_image(image: np.ndarray, beta: float = 0.15, alpha: float = 1.0,
                   centre: bool = False) -> ImageDiagnosis:
    """Run the textbook estimator with and without the sign fix on one image.

    If the plain SVD happens to return a first axis pointing away from the
    tissue, the naive estimate collapses on this image; the safe estimate does
    not. The sign an SVD returns is a convention of the linear-algebra library,
    not a property of the tissue. With numpy on TCGA colorectal tiles it came
    out negative on every tile tested (docs/stain-sign.md), so an uncentred
    implementation without the fix collapses every time there; another
    library or another data set may differ. Run it on a sample of your tiles.
    """
    od = optical_density(image, beta)
    if len(od) < 10:
        raise ValueError("too few tissue pixels above beta")
    plane = _plane(od, centre)
    neg = float(((od @ plane[:, 0]) < 0).mean())
    v1, v2, phi = _extremes(od, plane, alpha)
    lo, hi = np.percentile(phi, [alpha, 100 - alpha])
    straddle = bool(lo < -np.pi / 2 and hi > np.pi / 2)
    naive = angle_deg(v1, v2)
    safe = check_stain_matrix(macenko_stain_matrix(image, beta, alpha, centre)).angle_deg
    status = "degenerate" if naive < DEGENERATE_DEG else "suspect" if naive < SUSPECT_DEG else "ok"
    return ImageDiagnosis(len(od), neg, straddle, naive, safe, status)


def check_estimator(estimator: Callable[[np.ndarray], np.ndarray],
                    images: Iterable[np.ndarray]) -> list[MatrixCheck]:
    """Apply your own estimator (image -> 2 x 3 stain matrix) to images and check each result."""
    return [check_stain_matrix(estimator(im)) for im in images]
