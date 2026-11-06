"""he-checks: two checks for H&E image pipelines.

1. Whether a Macenko-style stain estimate has collapsed (H and E vectors nearly
   parallel because of a sign ambiguity), and a sign-safe estimator.
2. Whether a TCGA colorectal slide is one of 25 small derivative files whose
   stated pixel spacing (0.5 um/px in IDC) is too fine by roughly 2x.
"""
from .stain import (
    DEGENERATE_DEG,
    SUSPECT_DEG,
    angle_deg,
    check_estimator,
    check_stain_matrix,
    diagnose_image,
    macenko_stain_matrix,
    optical_density,
)
from .tcga import derivative_slides, is_derivative_slide

__version__ = "0.1.0"

__all__ = [
    "DEGENERATE_DEG",
    "SUSPECT_DEG",
    "__version__",
    "angle_deg",
    "check_estimator",
    "check_stain_matrix",
    "derivative_slides",
    "diagnose_image",
    "is_derivative_slide",
    "macenko_stain_matrix",
    "optical_density",
]
