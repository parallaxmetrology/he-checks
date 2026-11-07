"""Checks for two widely used colorectal tile collections (docs/kather-datasets.md).

1. The Kather et al. 2020 TCGA tile archive (Zenodo 3784345): tiles cut from the
   25 derivative slides are 200-px crops enlarged to 512 px. Use
   `hechecks.is_derivative_slide(tile_file_name)`; it accepts tile names directly.
2. CRC-VAL-HE-7K, as distributed (already Macenko-normalised by its authors): its
   background ("BACK") tiles are dark purple instead of near-white glass. Use
   `tile_tint` to see whether a collection's background tiles are neutral.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np

from ._image import rgb_0_255

# Heuristics from the data in docs/kather-datasets.md: unnormalised background tiles
# had median colour spread 0.3 and brightness about 243; all 847 CRC-VAL-HE-7K
# background tiles had spread 37 or more and brightness under 200.
TINT_SPREAD = 20.0
GLASS_BRIGHTNESS = 200.0


@dataclass
class TileTint:
    mean_rgb: tuple[float, float, float]
    brightness: float      # mean of the three channel means, 0-255
    colour_spread: float   # largest minus smallest channel mean, 0-255
    status: str            # "neutral", "tinted" or "dark"

    def as_dict(self) -> dict:
        return asdict(self)


def tile_tint(image: np.ndarray) -> TileTint:
    """Mean colour of a tile and whether it looks like neutral glass.

    Meant for tiles that should be blank or nearly blank (a background class).
    "tinted": channel means differ by more than 20; "dark": neutral but darker
    than 200; "neutral" otherwise, all in 0-255 units (other dtypes and 0-1 floats
    are rescaled first). Tissue tiles are tinted by design.
    """
    m = rgb_0_255(image).reshape(-1, 3).mean(0)
    spread = float(m.max() - m.min())
    bright = float(m.mean())
    status = "tinted" if spread > TINT_SPREAD else "dark" if bright < GLASS_BRIGHTNESS else "neutral"
    return TileTint((float(m[0]), float(m[1]), float(m[2])), bright, spread, status)
