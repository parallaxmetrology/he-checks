import statistics

from hechecks import derivative_slides, is_derivative_slide


def test_registry_shape():
    rows = derivative_slides()
    assert len(rows) == 25
    assert sum(r["project"] == "TCGA-COAD" for r in rows) == 17
    assert sum(r["project"] == "TCGA-READ" for r in rows) == 8
    assert len({r["file_id"] for r in rows}) == 25
    assert all(r["idc_pixel_spacing_um"] == "0.5" for r in rows)
    assert all(max(int(r["width"]), int(r["height"])) == 10000 for r in rows)


def test_field_grid_bearing_matches_note():
    v = [float(r["field_grid_um_per_px"]) for r in derivative_slides() if r["field_grid_um_per_px"]]
    assert len(v) == 17
    assert abs(statistics.median(v) - 0.90) < 0.01


def test_lookup_forms():
    assert is_derivative_slide("TCGA-AA-3488")
    assert is_derivative_slide("TCGA-AA-3488-01Z-00-DX1")
    assert is_derivative_slide("b8085eff-8407-4fd5-b2ba-70fa649aa07d")
    assert is_derivative_slide("TCGA-AG-3725-01Z-00-DX1.86CF8220-F410-49E4-A840-E42AE8C5D8B2.svs")
    assert not is_derivative_slide("TCGA-AA-3514")
    assert not is_derivative_slide("TCGA-AA-3488-01A-01-TS1")
