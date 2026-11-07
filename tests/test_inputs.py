"""Inputs that used to pass silently or crash."""
import numpy as np
import pytest
from test_stain import E, H, synthetic_he

import hechecks as hc


def test_zero_or_nonfinite_matrix_is_invalid_not_ok():
    assert hc.check_stain_matrix(np.array([np.zeros(3), E])).status == "invalid"
    assert hc.check_stain_matrix(np.full((2, 3), np.nan)).status == "invalid"
    assert hc.check_stain_matrix(np.array([H, [np.inf, 0, 0]])).status == "invalid"


def test_angle_of_zero_vector_is_nan():
    assert np.isnan(hc.angle_deg(np.zeros(3), H))


@pytest.mark.parametrize("convert", [
    lambda a: a.astype(float) / 255.0,                 # float 0-1
    lambda a: a.astype(float),                         # float 0-255
    lambda a: a.astype(np.uint16) * 257,               # uint16 full range
    lambda a: np.dstack([a, np.full(a.shape[:2], 255, np.uint8)]),  # RGBA
])
def test_dtypes_give_the_same_answer_as_uint8(convert):
    tile = synthetic_he()
    ref = hc.macenko_stain_matrix(tile)
    got = hc.macenko_stain_matrix(convert(tile))
    assert hc.angle_deg(ref[0], got[0]) < 0.01 and hc.angle_deg(ref[1], got[1]) < 0.01
    purple = np.zeros((16, 16, 3), np.uint8) + np.array([123, 79, 134], np.uint8)
    glass = np.full((16, 16, 3), 242, np.uint8)
    assert hc.tile_tint(convert(purple)).status == "tinted"
    assert hc.tile_tint(convert(glass)).status == "neutral"


def test_bad_images_raise():
    for bad in (np.zeros((8, 8)), np.zeros((8, 8, 3), bool), np.full((8, 8, 3), 300.0), np.full((8, 8, 3), np.nan), np.zeros((0, 0, 3))):
        with pytest.raises(ValueError):
            hc.tile_tint(bad)


@pytest.mark.parametrize("alpha", [0, 50, 60, -1])
def test_alpha_must_be_a_lower_percentile(alpha):
    with pytest.raises(ValueError):
        hc.macenko_stain_matrix(synthetic_he(), alpha=alpha)
    with pytest.raises(ValueError):
        hc.diagnose_image(synthetic_he(), alpha=alpha)


def test_returned_rows_cannot_change_the_list():
    hc.derivative_slides()[0]["patient"] = "changed"
    assert hc.derivative_slides()[0]["patient"] == "TCGA-AA-3488"
    assert hc.is_derivative_slide("TCGA-AA-3488")
