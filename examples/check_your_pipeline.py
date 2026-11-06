"""Check a stain estimator on a folder of H&E tiles, and flag TCGA slides with unreliable scale.

    python examples/check_your_pipeline.py tiles/ --slides slide_ids.txt
"""
import argparse
import glob
import os
from collections import Counter

import numpy as np
from PIL import Image

import hechecks as hc


def my_estimator(image):
    """Replace with the stain-matrix step of your own pipeline (image -> 2 x 3, row 0 = H)."""
    return hc.macenko_stain_matrix(image)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tiles")
    ap.add_argument("--slides", help="text file of TCGA ids, one per line")
    a = ap.parse_args()

    paths = sorted(glob.glob(os.path.join(a.tiles, "*.png")) + glob.glob(os.path.join(a.tiles, "*.jpg")))
    images = [np.asarray(Image.open(p).convert("RGB")) for p in paths]
    checks = hc.check_estimator(my_estimator, images)
    print(Counter(c.status for c in checks))
    print("median H/E angle:", np.median([c.angle_deg for c in checks]).round(2), "degrees")
    for p, c in zip(paths, checks):
        if c.status != "ok":
            print(c.status, p, round(c.angle_deg, 3))

    if a.slides:
        with open(a.slides) as f:
            ids = [line.strip() for line in f if line.strip()]
        flagged = [i for i in ids if hc.is_derivative_slide(i)]
        print(f"{len(flagged)} of {len(ids)} slides have unreliable stated pixel spacing:", *flagged, sep="\n  ")


if __name__ == "__main__":
    main()
