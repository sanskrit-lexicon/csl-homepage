#!/usr/bin/env python3
"""H7887 — cite-DOI drift guard for the uni-koeln homepage surfaces.

The umbrella corpus DOI (10.5281/zenodo.21319331) was added to the How-to-cite
Bibliographic reference by PR #28 (merged 2026-10-05) and clobbered eight days
later by commit 819eba7: the How-to-cite block lives in the *generators*
(index_xampp.py / index_cologne.py), PR #28 had patched the generated
index_xampp.html only, and the next redo_xampp.sh regen wiped the line.

This guard fails loud unless the DOI line is present in ALL of:
  1. index_xampp.py   (generator template — the fix point)
  2. index_cologne.py (generator template — the uni-koeln regen path)
  3. index_xampp.html (the committed, deployed artifact)
  4. cite.html        (the standalone uni-koeln cite page)
Date- and version-agnostic: it checks presence, not a byte regen diff (the
"accessed on" date changes on every legitimate regen).
"""
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DOI_LINE = "DOI 10.5281/zenodo.21319331"
SURFACES = [
    "index_xampp.py",
    "index_cologne.py",
    "index_xampp.html",
    "cite.html",
]


def main():
    missing = []
    for name in SURFACES:
        path = os.path.join(ROOT, name)
        with open(path, encoding="utf-8") as f:
            if DOI_LINE not in f.read():
                missing.append(name)
    if missing:
        sys.exit(
            "CITE-DOI DRIFT: umbrella DOI line missing from: "
            + ", ".join(missing)
            + " — restore it in the generator templates AND regenerate "
              "(redo_xampp.sh); PR #28 lost the line to regen because only "
              "the HTML artifact had been patched (H7887)."
        )
    print(f"CITE-DOI OK: {DOI_LINE} present in {len(SURFACES)} surfaces")


if __name__ == "__main__":
    main()
