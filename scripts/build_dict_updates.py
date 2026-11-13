# coding=utf-8
"""Build homepage_dict_updates.json from a csl-orig checkout (H8215).

Usage:
  python scripts/build_dict_updates.py --orig /path/to/csl-orig
  python scripts/build_dict_updates.py --orig /path/to/csl-orig --check

Contract (hybrid widget, grill-with-docs 13-11-2026):
  - A dictionary-update row is MECHANICAL: it is derived from csl-orig git
    history, never editorially marked (the H8170 `eligible` marker governs
    the NEWS block only — the two contracts sit side by side in one section).
  - Window: `git log --since="6 months ago" --no-merges` over `v02/` only.
  - A commit enters the feed only when it touches at least one path
    `v02/<code>/...` whose first segment maps (case-insensitively) to an
    indexdirs.xml `<pfx>`, and its subject does NOT start with one of the
    excluded prefixes (docs|ci|chore|refactor|test|build|ai-wip|Merge —
    word-boundary match, so `testing data` is NOT excluded but `test(x):` is).
  - Dedup: one row PER DICTIONARY = its newest eligible commit (git log
    order, newest first, first claim wins).  A multi-dict commit may claim
    several dictionaries.
  - Order: date DESC, then code ASC (deterministic for same-day batches).
    Output = the top DICT_MAX rows — exactly what the widget renders, so
    the wall-clock window can only drift the check when a RENDERED row
    ages out (effectively never: rendered rows are days old).
  - Subject cleaning (row-level, per that row's code):
      * `DC <date>. See <url-with-/issues/N>` -> `Corrections · csl-corrections#N`
      * `DC <date> [See <url>]`             -> `Corrections · <date>`
      * conventional prefix `type(scope): ` stripped
      * trailing closers stripped: `(closes ...)`, `[closes ...]`, `(#1234)`,
        `. See <url>` / `. Close <url>` connector+URL
      * leading `<CODE> ` / `<CODE> - ` / `<CODE>: ` stripped (redundant with
        the row label, e.g. `fix: STC s.v. ...` -> `s.v. ...`)
      * whitespace collapsed; empty result falls back to the raw subject
  - display: host-relative basic-display path built from indexdirs.xml
    (`/scans/<PFX>Scan/<year>/web/webtc/indexcaller.php`, STC ->
    `indexcaller_fr.php`, PD -> null: no standard display, per
    index_cologne.dict_line_links).
  - Output is a pure function of (csl-orig history, indexdirs.xml): no
    timestamps, deterministic key order -> byte-exact `--check` in CI against
    a shallow blobless clone (see .github/workflows/news-widget.yml).

Stdlib only.
"""
from __future__ import print_function

import argparse
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EXCLUDED_PREFIXES = ('docs', 'ci', 'chore', 'refactor', 'test', 'build',
                     'ai-wip', 'merge')
# Word boundary after the token: `refactor(`, `refactor:`, `refactor ` match;
# `testing data` / `Manifest ...` do not.
_EXCLUDE_RE = re.compile(
    r'^(?:%s)(?=[\s(:]|$)' % '|'.join(re.escape(p) for p in EXCLUDED_PREFIXES),
    re.IGNORECASE)

_CONVENTIONAL_RE = re.compile(
    r'^(?:feat|fix|perf|refactor|chore|docs|style|test|build|ci)'
    r'(?:\([^)]*\))?:\s*', re.IGNORECASE)
_DC_RE = re.compile(r'^DC\s+(?P<rest>.+?)?(?:\.\s+See\s+(?P<url>\S+))?$')
_CLOSER_RE = re.compile(
    r'\s*[\(\[](?:closes?|see|fixes|resolves)[^\)\]]*[\)\]]\s*$', re.IGNORECASE)
_PRREF_RE = re.compile(r'\s*\(#\d+\)\s*$')
_CONNECTOR_URL_RE = re.compile(
    r'\s*[.,;]?\s+(?:see|close|closes|see also)\s+https?://\S+\s*$',
    re.IGNORECASE)

WINDOW = '6 months'
DICT_MAX = 4
DEFAULT_OUTPUT = os.path.join(REPO_ROOT, 'homepage_dict_updates.json')


# --------------------------------------------------------------------------- #
# Pure functions (unit-tested without git)
# --------------------------------------------------------------------------- #

def excluded_subject(subject):
    """True for dev/tooling subjects; word-boundary match (see module doc)."""
    return bool(_EXCLUDE_RE.match(subject))


def clean_subject(subject, code):
    """Row-level subject cleaning; falls back to the raw subject if empty."""
    s = subject.strip()

    m = _DC_RE.match(s)
    if m:
        url = m.group('url') or ''
        issue = re.search(r'/issues/(\d+)', url)
        if issue:
            return 'Corrections · csl-corrections#%s' % issue.group(1)
        rest = (m.group('rest') or '').strip().rstrip('.')
        return ('Corrections · %s' % rest) if rest else 'Corrections'

    s = _CONVENTIONAL_RE.sub('', s)
    # Trailing closers / PR refs / connector+URL, iteratively (they stack).
    for _ in range(5):
        before = s
        s = _CLOSER_RE.sub('', s)
        s = _PRREF_RE.sub('', s)
        s = _CONNECTOR_URL_RE.sub('', s)
        s = s.strip()
        if s == before:
            break
    # Leading row-code prefix: `STC s.v. ...` -> `s.v. ...`, `BEN - x` -> `x`.
    s = re.sub(r'^(?:%s)(?:\s*[-\u2013\u2014:]\s*|\s+)' % re.escape(code),
               '', s, count=1)
    s = ' '.join(s.split())
    return s or subject.strip()


def parse_log(text):
    """Parse `git log --pretty=format:%x1e%H%x1f%cs%x1f%s --name-only` output.

    Returns [(sha, date, subject, paths)] in git log order (newest first).
    """
    commits = []
    for chunk in text.split('\x1e'):
        if not chunk.strip():
            continue
        lines = chunk.splitlines()
        header = lines[0]
        parts = header.split('\x1f', 2)
        if len(parts) != 3 or not re.match(r'^[0-9a-f]{40}$', parts[0]):
            raise ValueError('unparseable commit header: %r' % header)
        sha, date, subject = parts
        paths = [ln for ln in lines[1:] if ln.strip()]
        commits.append((sha, date, subject, paths))
    return commits


def dict_code_of(path, pfx_by_dir):
    """`v02/<code>/...` -> the indexdirs pfx (uppercased), else None."""
    parts = path.split('/')
    if len(parts) < 3 or parts[0] != 'v02':
        return None
    return pfx_by_dir.get(parts[1].lower())


def select_rows(commits, pfx_by_dir, titles, max_rows=DICT_MAX):
    """Dedup per dictionary (first/newest claim wins), order, cap."""
    rows_by_code = {}
    for sha, date, subject, paths in commits:
        if excluded_subject(subject):
            continue
        seen = []
        for path in paths:
            code = dict_code_of(path, pfx_by_dir)
            if code and code not in seen:
                seen.append(code)
        for code in seen:
            if code not in rows_by_code:
                title, display = titles[code]
                rows_by_code[code] = {
                    'date': date,
                    'code': code,
                    'title': title,
                    'display': display,
                    'subject': clean_subject(subject, code),
                    'url': 'https://github.com/sanskrit-lexicon/csl-orig/'
                            'commit/%s' % sha,
                }
    rows = sorted(rows_by_code.values(),
                  key=lambda r: (tuple(-int(p) for p in r['date'].split('-')),
                                 r['code']))
    return rows[:max_rows]


def display_for(pfx, year):
    """Basic-display path; mirrors index_cologne.dict_line_links."""
    if pfx == 'PD':
        return None  # special request — no standard display link
    fn = 'indexcaller_fr.php' if pfx == 'STC' else 'indexcaller.php'
    return '/scans/%sScan/%s/web/webtc/%s' % (pfx, year, fn)


def load_indexdirs(path=None):
    """-> (pfx_by_dir, titles): dir-name lookup + {pfx: (title, display)}."""
    path = path or os.path.join(REPO_ROOT, 'indexdirs.xml')
    root = ET.parse(path).getroot()
    pfx_by_dir = {}
    titles = {}
    for entry in root.findall('entry'):
        pfx = (entry.findtext('pfx') or '').strip()
        year = (entry.findtext('year') or '').strip()
        title = (entry.findtext('title') or '').strip()
        if not pfx or not title:
            continue
        pfx_by_dir[pfx.lower()] = pfx
        titles[pfx] = (title, display_for(pfx, year))
    return pfx_by_dir, titles


def build_document(commits, pfx_by_dir, titles):
    return {
        'source_repo': 'sanskrit-lexicon/csl-orig',
        'window': WINDOW,
        'items': select_rows(commits, pfx_by_dir, titles),
    }


# --------------------------------------------------------------------------- #
# git / CLI
# --------------------------------------------------------------------------- #

def git_log(orig):
    cmd = ['git', '-C', orig, 'log', '--no-merges',
           '--since=%s ago' % WINDOW, '--date=short',
           '--pretty=format:%x1e%H%x1f%cs%x1f%s',
           '--name-only', '--', 'v02/']
    proc = subprocess.run(cmd, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise SystemExit('git log failed in %s: %s'
                         % (orig, proc.stderr.decode('utf-8', 'replace')))
    return proc.stdout.decode('utf-8')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--orig', required=True,
                        help='path to a csl-orig checkout')
    parser.add_argument('--output', default=DEFAULT_OUTPUT)
    parser.add_argument('--check', action='store_true',
                        help='exit 1 if the committed feed differs')
    args = parser.parse_args(argv)

    pfx_by_dir, titles = load_indexdirs()
    commits = parse_log(git_log(args.orig))
    doc = build_document(commits, pfx_by_dir, titles)
    rendered = json.dumps(doc, ensure_ascii=False, indent=2) + '\n'

    if args.check:
        try:
            with open(args.output, 'r', encoding='utf-8', newline='') as fin:
                current = fin.read()
        except FileNotFoundError:
            print('CHECK FAILED: %s missing — run build_dict_updates.py'
                  % args.output, file=sys.stderr)
            return 1
        if current != rendered:
            print('CHECK FAILED: %s is stale — run '
                  'scripts/build_dict_updates.py --orig <csl-orig> and '
                  'commit the result' % args.output, file=sys.stderr)
            return 1
        print('check ok: %s matches csl-orig (%d items)'
              % (args.output, len(doc['items'])))
        return 0

    with open(args.output, 'w', encoding='utf-8', newline='\n') as fout:
        fout.write(rendered)
    print('wrote %s (%d items)' % (args.output, len(doc['items'])))
    return 0


if __name__ == '__main__':
    sys.exit(main())
