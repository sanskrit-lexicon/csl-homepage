# coding=utf-8
"""Regen-check: committed index_xampp.html == fresh generation (H8215).

The generator stamps two VOLATILE values into every page: the calendar
date (`Last modified` / `accessed on`, from datetime.now()) and the
csl-orig version (from ../csl-orig/.version).  Everything else — the
catalogue, og-less head, the whole news/dict-update section — is a pure
function of committed inputs (indexdirs.xml, homepage_news.json,
homepage_dict_updates.json, the *.py sources).

So the check:
  1. ensures ../csl-orig/.version exists (writes a neutral 0.0.0 stub
     when absent — the value is normalized away; a real file is never
     touched);
  2. regenerates the page to a temp file;
  3. normalizes `version X.Y.Z` and `Month D, YYYY` in BOTH texts;
  4. byte-diffs. Any residual difference = forgotten regen (or generator
     drift) -> exit 1 with a unified diff head.

Stdlib only; run from the repo root (CWD), like the other gate steps.
"""
from __future__ import print_function

import difflib
import os
import re
import subprocess
import sys
import tempfile

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMMITTED = os.path.join(REPO_ROOT, 'index_xampp.html')

_MONTHS = ('January|February|March|April|May|June|July|August|September|'
           'October|November|December')
VOLATILE = (
    (re.compile(r'version \d+\.\d+\.\d+'), 'version X.Y.Z'),
    (re.compile(r'(?:%s) \d{1,2}, \d{4}' % _MONTHS), 'DATE STAMP'),
)


def normalize(text):
    for pattern, repl in VOLATILE:
        text = pattern.sub(repl, text)
    return text


def ensure_version_file():
    """The generator reads ../csl-orig/.version at IMPORT time (fail loud
    mid-generation would be worse than a neutral stub we normalize away)."""
    path = os.path.join(REPO_ROOT, '..', 'csl-orig', '.version')
    if os.path.exists(path):
        return  # a real checkout's stamp; normalization makes its value moot
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('0.0.0\n')
    print('note: stubbed missing ../csl-orig/.version with 0.0.0 '
          '(normalized away)')


def main():
    if not os.path.exists(COMMITTED):
        print('FAIL: %s missing' % COMMITTED, file=sys.stderr)
        return 1
    ensure_version_file()
    fd, tmp = tempfile.mkstemp(suffix='.html', prefix='xampp-regen-')
    os.close(fd)
    try:
        proc = subprocess.run(
            [sys.executable, 'index_xampp.py', 'indexdirs.xml', tmp],
            cwd=REPO_ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proc.returncode != 0:
            print('FAIL: generator exited %d\n%s\n%s'
                  % (proc.returncode, proc.stdout.decode('utf-8', 'replace'),
                     proc.stderr.decode('utf-8', 'replace')), file=sys.stderr)
            return 1
        with open(COMMITTED, 'r', encoding='utf-8', newline='') as fh:
            committed = fh.read()
        with open(tmp, 'r', encoding='utf-8', newline='') as fh:
            fresh = fh.read()
        a = normalize(committed).splitlines(keepends=True)
        b = normalize(fresh).splitlines(keepends=True)
        if a != b:
            diff = list(difflib.unified_diff(
                a, b, fromfile='committed index_xampp.html',
                tofile='fresh regeneration', n=2))
            print('FAIL: committed index_xampp.html differs from a fresh '
                  'generation (after masking date/version stamps) — '
                  'regenerate: python index_xampp.py indexdirs.xml '
                  'index_xampp.html', file=sys.stderr)
            sys.stdout.writelines(diff[:80])
            if len(diff) > 80:
                print('... %d more diff lines' % (len(diff) - 80),
                      file=sys.stderr)
            return 1
        print('regen ok: index_xampp.html matches fresh generation '
              '(date/version stamps masked)')
        return 0
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass


if __name__ == '__main__':
    sys.exit(main())
