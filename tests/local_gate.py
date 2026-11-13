# coding=utf-8
"""One-command local gate for csl-homepage (H8170, extended H8215).

Runs, in order (stops at the first failure, prints every command + exit code):
  1. python -m unittest discover -s tests   (news + dict-update fixtures)
  2. python scripts/check_cite_dois.py      (existing cite-guard check)
  3. python scripts/check_xampp_regen.py    (committed xampp page == regen)
  4. with --guides: build_newsfeed.py --check   (news feed vs csl-guides)
  5. with --orig:   build_dict_updates.py --check (dict feed vs csl-orig)

Usage:
  python tests/local_gate.py
  python tests/local_gate.py --guides /path/to/csl-guides --orig /path/to/csl-orig
"""
from __future__ import print_function

import argparse
import os
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable


def run(cmd, cwd=REPO_ROOT):
    print('+ %s' % ' '.join(cmd))
    code = subprocess.call(cmd, cwd=cwd)
    print('  exit %d' % code)
    return code


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--guides', default=None,
                        help='csl-guides checkout for the news feed drift check')
    parser.add_argument('--orig', default=None,
                        help='csl-orig checkout for the dict-updates drift check')
    args = parser.parse_args(argv)

    steps = [
        ([PY, '-m', 'unittest', 'discover', '-s', 'tests', '-v'], 'tests'),
        ([PY, 'scripts/check_cite_dois.py'], 'cite-dois'),
        ([PY, 'scripts/check_xampp_regen.py'], 'xampp-regen'),
    ]
    if args.guides:
        steps.append(([PY, 'scripts/build_newsfeed.py',
                       '--guides', args.guides, '--check'], 'news-feed-check'))
    if args.orig:
        steps.append(([PY, 'scripts/build_dict_updates.py',
                       '--orig', args.orig, '--check'], 'dict-feed-check'))

    for cmd, name in steps:
        print('== %s ==' % name)
        code = run(cmd)
        if code != 0:
            print('LOCAL GATE FAILED at step: %s' % name)
            return code
    print('LOCAL GATE OK (%d steps)' % len(steps))
    return 0


if __name__ == '__main__':
    sys.exit(main())
