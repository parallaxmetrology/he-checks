import numpy as np
import pytest

from hechecks import angle_deg, check_stain_matrix, diagnose_image, macenko_stain_matrix
from hechecks import stain as st

H = np.array([0.65, 0.70, 0.29])
E = np.array([0.07, 0.99, 0.11])


def synthetic_he(seed=0, n=256):
    """An RGB tile mixed from known H and E directions (Beer-Lambert)."""
    rng = np.random.default_rng(seed)
    h = rng.gamma(2.0, 0.35, (n, n))
    e = rng.gamma(2.0, 0.30, (n, n))
    od = h[..., None] * (H / np.linalg.norm(H)) + e[..., None] * (E / np.linalg.norm(E))
    return np.clip(255 * np.exp(-od), 0, 255).astype(np.uint8)


def test_safe_estimator_recovers_known_vectors():
    # Macenko takes the 1st/99th percentile angles, which are still slight mixtures
    # of the two stains, so a few degrees of bias toward each other is expected.
    m = macenko_stain_matrix(synthetic_he())
    assert angle_deg(m[0], H) < 5
    assert angle_deg(m[1], E) < 5
    assert check_stain_matrix(m).status == "ok"


def test_negative_first_axis_collapses_the_naive_estimate():
    od = st.optical_density(synthetic_he())
    plane = st._plane(od, centre=False)
    plane[:, 0] *= -np.sign((od @ plane[:, 0]).mean())  # force the bad sign
    v1, v2, phi = st._extremes(od, plane, 1.0)
    assert angle_deg(v1, v2) < st.DEGENERATE_DEG
    lo, hi = np.percentile(phi, [1, 99])
    assert lo < -np.pi / 2 and hi > np.pi / 2  # the percentiles sit either side of the wrap


def test_check_flags_parallel_rows():
    historical = np.array([[0.5378, 0.7968, 0.2754], [0.5362, 0.7986, 0.2735]])  # docs/stain-sign.md
    c = check_stain_matrix(historical)
    assert c.status == "degenerate"
    assert c.angle_deg == pytest.approx(0.17, abs=0.02)
    assert c.condition_number > 100


def test_check_accepts_3x2_and_rejects_bad_shapes():
    assert check_stain_matrix(np.array([H, E]).T).status == "ok"
    with pytest.raises(ValueError):
        check_stain_matrix(np.ones((3, 3)))


def test_diagnose_reports_safe_angle():
    d = diagnose_image(synthetic_he(1))
    assert d.safe_angle_deg > st.SUSPECT_DEG
    assert 0 <= d.share_negative_on_axis0 <= 1


def test_too_little_tissue_raises():
    with pytest.raises(ValueError):
        macenko_stain_matrix(np.full((32, 32, 3), 250, np.uint8))


def test_centred_safe_estimate_also_recovers_vectors():
    m = macenko_stain_matrix(synthetic_he(2), centre=True)
    assert angle_deg(m[0], H) < 5
    assert angle_deg(m[1], E) < 5


def test_rows_point_into_positive_od_and_h_first():
    m = macenko_stain_matrix(synthetic_he(3))
    assert (m.sum(axis=1) > 0).all()
    assert m[0, 0] > m[1, 0]
    assert np.allclose(np.linalg.norm(m, axis=1), 1)


def test_check_ignores_row_sign():
    assert check_stain_matrix(np.array([-H, E])).angle_deg == pytest.approx(angle_deg(H, E))
