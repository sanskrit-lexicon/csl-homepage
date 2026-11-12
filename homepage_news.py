# coding=utf-8
"""Homepage news widget — selection and rendering for the CDSL landing page (H8170).

Domain glossary (approved decisions, 12-11-2026):

- news article        a published page in the csl-guides news section
                      (https://sanskrit-lexicon.github.io/csl-guides/news/<slug>).
- publication date    the article's editorial publication date (ISO YYYY-MM-DD).
                      Text edits NEVER bump it; ordering is by this date only.
- work status         one of "Published", "In progress", "Planned" — it describes
                      the ANNOUNCED WORK, not the article's own draft state.
                      Draft news is never public just because its work status
                      is Planned.
- homepage eligibility an EXPLICIT editorial marker: frontmatter `homepage: true`
                      in csl-guides, propagated as `eligible: true` in
                      homepage_news.json. Eligibility is NEVER inferred from a
                      commit, GitHub release, Markdown filename or mere file
                      existence.

The feed (homepage_news.json) is a committed artifact produced by
scripts/build_newsfeed.py from a csl-guides checkout — the generator has no
runtime GitHub/API dependence and no dependency on a csl-guides clone.

Selection contract:
  - keep items with eligible is true AND draft is not true,
  - keep items with a valid ISO date, an https:// URL and a known work status,
  - order by publication date DESC, ties broken by slug ASC (deterministic),
  - take the first MAX_ITEMS (3); fewer eligible items => fewer real items,
    never invented filler.

Fail-soft rule: load_feed raises FeedError on missing/malformed data; the
page generators catch everything and render NO widget, so missing or
malformed news data can never break dictionary access.
"""
from __future__ import print_function

import html
import json
import os
import re

DEFAULT_AUTHOR = 'CDSL Editorial Team'
STATUSES = ('Published', 'In progress', 'Planned')
STATUS_COLORS = {
    'Published': '#2e7d32',
    'In progress': '#e65100',
    'Planned': '#1565c0',
}
NEWS_URL_BASE = 'https://sanskrit-lexicon.github.io/csl-guides/news/'
MAX_ITEMS = 3
DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')

DEFAULT_FEED = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'homepage_news.json')


class FeedError(Exception):
    """Missing or malformed homepage news feed data."""


def load_feed(path=DEFAULT_FEED):
    """Read homepage_news.json and return the raw items list.

    Raises FeedError for a missing file or a malformed document. Callers on
    the generation path must catch FeedError (fail soft); tests assert it.
    """
    try:
        with open(path, 'r', encoding='utf-8') as fin:
            data = json.load(fin)
    except FileNotFoundError as exc:
        raise FeedError('feed missing: %s' % path) from exc
    except (ValueError, OSError) as exc:
        raise FeedError('feed unreadable: %s (%s)' % (path, exc)) from exc
    if not isinstance(data, dict) or not isinstance(data.get('items'), list):
        raise FeedError('feed must be an object with an "items" list: %s' % path)
    return data['items']


def _valid_url(url):
    """https:// only — never javascript:, data: or other unsafe schemes."""
    return isinstance(url, str) and url.startswith('https://')


def select_items(items, n=MAX_ITEMS):
    """Return up to n eligible items in deterministic publication order."""
    selected = []
    for item in items:
        if not isinstance(item, dict):
            continue
        if item.get('eligible') is not True:
            continue          # explicit marker required — never inferred
        if item.get('draft') is True:
            continue          # draft news is never homepage material
        date = item.get('date')
        if not isinstance(date, str) or not DATE_RE.match(date):
            continue          # malformed date: skip, never crash
        status = item.get('status')
        if status not in STATUSES:
            continue          # unknown work status: skip
        if not _valid_url(item.get('url')):
            continue          # unsafe or missing link: skip
        if not isinstance(item.get('title'), str) or not item['title'].strip():
            continue          # no visible title: skip
        selected.append(item)
    return _order(selected)[:n]


def _slug_of(item):
    slug = item.get('slug')
    return slug if isinstance(slug, str) else ''


def _order(items):
    """date DESC, then slug ASC."""
    return sorted(items,
                  key=lambda it: (tuple(-int(p) for p in it['date'].split('-')),
                                  _slug_of(it)))


def author_of(item):
    """Optional personal byline, else the default editorial byline."""
    author = item.get('author')
    if isinstance(author, str) and author.strip():
        return author.strip()
    return DEFAULT_AUTHOR


def render_widget(items):
    """Render the selected items to homepage HTML lines; [] when empty.

    All text and attribute values are escaped context-correctly. The widget
    section is omitted entirely when there is nothing real to show.
    """
    if not items:
        return []
    lines = [
        '<hr style="width:89%; margin-left:0px;"/>',
        '<div id="news">',
        ' <h2>Latest news '
        '<a href="%s" target="_blank" rel="noopener" '
        'style="font-size:0.6em; font-weight:normal;">'
        '(all news)</a></h2>' % html.escape(NEWS_URL_BASE, quote=True),
        ' <ul style="width:89%; list-style:none; padding-left:0;">',
    ]
    for item in items:
        date = html.escape(str(item['date']))
        title = html.escape(item['title'])
        url = html.escape(item['url'], quote=True)
        status = item['status']
        color = STATUS_COLORS[status]
        author = html.escape(author_of(item))
        summary = item.get('summary')
        lines.append('  <li style="margin-bottom:0.7em;">')
        lines.append('   <span style="font-weight:bold;">%s</span> ' % date)
        lines.append('   <a href="%s" target="_blank" rel="noopener">%s</a> '
                     % (url, title))
        lines.append('   <span style="color:%s; font-weight:bold;">'
                     '[%s]</span> ' % (html.escape(color, quote=True), status))
        lines.append('   <span style="color:#555;">— %s</span>' % author)
        if isinstance(summary, str) and summary.strip():
            lines.append('<br/>   %s' % html.escape(summary))
        lines.append('  </li>')
    lines.append(' </ul>')
    lines.append('</div>')
    return lines


def widget_lines(feed_path=DEFAULT_FEED, n=MAX_ITEMS):
    """Generation-path entry point: feed -> HTML lines, fail soft to []."""
    try:
        items = load_feed(feed_path)
    except FeedError as exc:
        import sys
        sys.stderr.write('homepage news widget skipped: %s\n' % exc)
        return []
    return render_widget(select_items(items, n))
