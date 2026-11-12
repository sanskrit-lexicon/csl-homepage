# coding=utf-8
"""One-command local gate for csl-homepage (H8170).

Runs, in order (stops at the first failure, prints every command + exit code):
  1. python -m unittest discover -s tests   (widget selection/render fixtures)
  2. python scripts/check_cite_dois.py      (existing cite-guard check)
  3. with --guides: build_newsfeed.py --check  (committed feed vs csl-guides)

Usage:
  python tests/local_gate.py
  python tests/local_gate.py --guides /path/to/csl-guides
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
                        help='csl-guides checkout for the feed drift check')
    args = parser.parse_args(argv)

    steps = [
        ([PY, '-m', 'unittest', 'discover', '-s', 'tests', '-v'], 'tests'),
        ([PY, 'scripts/check_cite_dois.py'], 'cite-dois'),
    ]
    if args.guides:
        steps.append(([PY, 'scripts/build_newsfeed.py',
                       '--guides', args.guides, '--check'], 'feed-check'))

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
