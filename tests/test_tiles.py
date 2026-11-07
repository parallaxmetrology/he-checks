import numpy as np
import pytest
from PIL import Image

from hechecks import is_derivative_slide, tile_tint
from hechecks.cli import main


def test_crcval_like_background_is_tinted():
    purple = np.zeros((64, 64, 3), np.uint8) + np.array([123, 79, 134], np.uint8)
    t = tile_tint(purple)
    assert t.status == "tinted"
    assert t.colour_spread == pytest.approx(55, abs=0.5)


def test_glass_is_neutral_and_grey_is_dark():
    assert tile_tint(np.full((32, 32, 3), 242, np.uint8)).status == "neutral"
    assert tile_tint(np.full((32, 32, 3), 150, np.uint8)).status == "dark"


def test_tile_names_from_the_tcga_archive():
    derivative = "TCGA-AA-3496-01Z-00-DX1.B109A6F3-02E0-4181-B69A-00CBA758C074_(3663,2051).jpg"
    regular = "TCGA-AA-3514-01Z-00-DX1.1C8D4A10-4C5D-4B4C-8E5E-1D3A1D0B2F5A_(2202,4404).jpg"
    assert is_derivative_slide(derivative)
    assert is_derivative_slide("tiles/TCGA-AA-3496-01Z-00-DX1.B109A6F3-02E0-4181-B69A-00CBA758C074/" + derivative)
    assert not is_derivative_slide(regular)


def test_tint_cli(tmp_path, capsys):
    p = tmp_path / "back.png"
    Image.fromarray(np.zeros((16, 16, 3), np.uint8) + np.array([123, 79, 134], np.uint8)).save(p)
    g = tmp_path / "glass.png"
    Image.fromarray(np.full((16, 16, 3), 242, np.uint8)).save(g)
    assert main(["tint", str(g)]) == 0
    assert main(["tint", str(p)]) == 1
    assert '"status": "tinted"' in capsys.readouterr().out
