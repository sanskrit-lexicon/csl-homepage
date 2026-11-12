# coding=utf-8
"""Build homepage_news.json from a csl-guides checkout (H8170).

Usage:
  python scripts/build_newsfeed.py --guides /path/to/csl-guides
  python scripts/build_newsfeed.py --guides /path/to/csl-guides --check

Contract:
  - An article enters the homepage feed ONLY through the explicit editorial
    frontmatter marker `homepage: true` — never inferred from a commit,
    release, filename or mere file existence.
  - Draft articles are refused even when marked: frontmatter `draft: true`
    or a body containing the `<!-- DRAFT` marker.
  - Required frontmatter: slug, title, description (summary), date (ISO).
  - Optional frontmatter: work_status (default "Published"; must be one of
    Published | In progress | Planned), author (personal byline; default
    applied at render time), related (slug of the earlier announcement this
    article completes).
  - Output items are ordered publication date DESC, slug ASC — the same
    deterministic rule the widget selector applies.
  - --check regenerates in memory and exits 1 on drift vs the committed file.

Stdlib only; minimal frontmatter parsing (no YAML dependency).
"""
from __future__ import print_function

import argparse
import glob
import json
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
import homepage_news  # noqa: E402  (shared contract: statuses, URL base)

FRONT_RE = re.compile(r'\A---\s*\n(.*?)\n---\s*\n', re.S)


def parse_frontmatter(text):
    """Return (frontmatter_dict, body). Minimal key: value parsing."""
    m = FRONT_RE.match(text)
    if not m:
        return None, text
    front = {}
    for line in m.group(1).splitlines():
        if not line or line.lstrip().startswith('#') or ':' not in line:
            continue
        key, _, value = line.partition(':')
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in '"\'':
            value = value[1:-1]
        front[key] = value
    body = text[m.end():]
    return front, body


def _is_draft(front, body):
    if (front.get('draft') or '').lower() == 'true':
        return True
    return '<!-- DRAFT' in body


def extract_articles(guides_root):
    """Return (items, warnings) for marked, non-draft articles."""
    blog_dir = os.path.join(guides_root, 'blog')
    if not os.path.isdir(blog_dir):
        raise SystemExit('not a csl-guides checkout (no blog/): %s' % guides_root)
    items, warnings = [], []
    for path in sorted(glob.glob(os.path.join(blog_dir, '*.md'))):
        with open(path, 'r', encoding='utf-8') as fin:
            text = fin.read()
        front, body = parse_frontmatter(text)
        name = os.path.basename(path)
        if front is None:
            continue
        if (front.get('homepage') or '').lower() != 'true':
            continue                      # no explicit editorial marker
        if _is_draft(front, body):
            warnings.append('skipped marked DRAFT: %s' % name)
            continue
        missing = [k for k in ('slug', 'title', 'description', 'date')
                   if not front.get(k)]
        if missing:
            warnings.append('skipped %s: missing frontmatter %s'
                            % (name, ', '.join(missing)))
            continue
        status = front.get('work_status', 'Published')
        if status not in homepage_news.STATUSES:
            warnings.append('skipped %s: invalid work_status %r'
                            % (name, status))
            continue
        if not DATE_OK(front['date']):
            warnings.append('skipped %s: invalid date %r'
                            % (name, front['date']))
            continue
        item = {
            'date': front['date'],
            'slug': front['slug'],
            'title': front['title'],
            'summary': front['description'],
            'status': status,
            'url': homepage_news.NEWS_URL_BASE + front['slug'],
            'eligible': True,      # propagated explicit editorial marker
            'draft': False,        # drafts were refused above
        }
        if front.get('author'):
            item['author'] = front['author']
        if front.get('related'):
            item['related'] = front['related']
        items.append(item)
    items = homepage_news._order(items)
    return items, warnings


DATE_OK_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')


def DATE_OK(value):
    return bool(DATE_OK_RE.match(value))


def build_document(items):
    return {
        'source_repo': 'sanskrit-lexicon/csl-guides',
        'items': items,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--guides', required=True,
                        help='path to a csl-guides checkout')
    parser.add_argument('--output',
                        default=os.path.join(REPO_ROOT, 'homepage_news.json'))
    parser.add_argument('--check', action='store_true',
                        help='exit 1 if the committed feed differs')
    args = parser.parse_args(argv)

    items, warnings = extract_articles(args.guides)
    for warning in warnings:
        print('warning: %s' % warning, file=sys.stderr)
    doc = build_document(items)
    rendered = json.dumps(doc, ensure_ascii=False, indent=2) + '\n'

    if args.check:
        try:
            with open(args.output, 'r', encoding='utf-8') as fin:
                current = fin.read()
        except FileNotFoundError:
            print('CHECK FAILED: %s missing — run build_newsfeed.py'
                  % args.output, file=sys.stderr)
            return 1
        if current != rendered:
            print('CHECK FAILED: %s is stale — run '
                  'scripts/build_newsfeed.py --guides <csl-guides> and '
                  'commit the result' % args.output, file=sys.stderr)
            return 1
        print('check ok: %s matches csl-guides (%d items)'
              % (args.output, len(items)))
        return 0

    with open(args.output, 'w', encoding='utf-8', newline='\n') as fout:
        fout.write(rendered)
    print('wrote %s (%d items)' % (args.output, len(items)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
