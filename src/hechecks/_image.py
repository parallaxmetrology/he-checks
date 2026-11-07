"""Shared input handling: every check works in 8-bit intensity units (0-255)."""
from __future__ import annotations

import numpy as np


def rgb_0_255(image: np.ndarray) -> np.ndarray:
    """Return an H x W x 3 float array in 0-255 units, whatever the input dtype.

    uint8 is used as is; other integer types are rescaled from their full range
    (uint16 0-65535 -> 0-255); floats with a maximum of at most 1 are treated as
    0-1 and multiplied by 255, other floats as already 0-255. A fourth (alpha)
    channel is dropped. Raises ValueError for anything that is not an RGB image.
    """
    a = np.asarray(image)
    if a.ndim != 3 or a.shape[2] < 3:
        raise ValueError("expected an H x W x 3 RGB image")
    if a.dtype == bool or not (np.issubdtype(a.dtype, np.integer) or np.issubdtype(a.dtype, np.floating)):
        raise ValueError(f"unsupported image dtype {a.dtype}")
    a = a[..., :3]
    if a.size == 0:
        raise ValueError("empty image")
    if a.dtype == np.uint8:
        return a.astype(float)
    if np.issubdtype(a.dtype, np.integer):
        return a.astype(float) * (255.0 / np.iinfo(a.dtype).max)
    f = a.astype(float)
    if not np.isfinite(f).all():
        raise ValueError("image contains non-finite values")
    if f.min() < 0 or f.max() > 255:
        raise ValueError("float image values outside 0-255")
    return f * 255.0 if f.max() <= 1.0 else f
