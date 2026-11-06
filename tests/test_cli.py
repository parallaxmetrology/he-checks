import numpy as np
from PIL import Image
from test_stain import synthetic_he

from hechecks.cli import main


def test_tcga_exit_codes(capsys):
    assert main(["tcga", "TCGA-AA-3514"]) == 0
    assert main(["tcga", "tcga-aa-3488-01z-00-dx1", "TCGA-AA-3514"]) == 1
    assert main(["tcga", "/data/slides/TCGA-AG-3725-01Z-00-DX1.86CF8220-F410-49E4-A840-E42AE8C5D8B2.svs"]) == 1
    assert "DERIVATIVE" in capsys.readouterr().out


def test_stain_reports_and_survives_bad_inputs(tmp_path, capsys):
    good = tmp_path / "tile.png"
    Image.fromarray(synthetic_he()).save(good)
    blank = tmp_path / "blank.png"
    Image.fromarray(np.full((32, 32, 3), 250, np.uint8)).save(blank)
    code = main(["stain", str(good), str(blank), str(tmp_path / "missing.png")])
    out = capsys.readouterr().out.strip().splitlines()
    assert len(out) == 3
    assert '"status": "error"' in out[1] and '"status": "error"' in out[2]
    assert code >= 1
