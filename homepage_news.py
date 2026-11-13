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

import datetime
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


def valid_date(value):
    """ISO shape AND a real calendar date (9999-99-99 must not sort to #1)."""
    if not isinstance(value, str) or not DATE_RE.match(value):
        return False
    try:
        datetime.date(int(value[0:4]), int(value[5:7]), int(value[8:10]))
    except ValueError:
        return False
    return True

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
        if item.get('draft') in (True, 'true'):
            continue          # draft news is never homepage material
        date = item.get('date')
        if not valid_date(date):
            continue          # malformed/impossible date: skip, never crash
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


def render_widget(items, dict_items=None):
    """Render the hybrid section to homepage HTML lines; [] when empty.

    `items`      — validated news rows (H8170 contract, rendered first);
    `dict_items` — validated dictionary-update rows (H8215, below news).
    Both empty -> no section at all.  News feed problems are load-bearing
    for the section (H8170 fail-soft contract, pinned by fixtures); a bad
    dict feed simply means no dict rows — callers catch and pass [].
    All text and attribute values are escaped context-correctly.
    """
    if not items and not dict_items:
        return []
    lines = [
        '<hr style="width:89%; margin-left:0px;"/>',
        '<style>',
        ' #news { box-sizing:border-box; width:89%; background:#ffffff;',
        '  border:1px solid #d0d7de; border-radius:8px;',
        '  padding:16px 20px 14px; margin:1em 0;',
        '  font-family:-apple-system,"Segoe UI",Helvetica,Arial,sans-serif;',
        '  color:#1f2328; }',
        ' #news h2 { margin:0 0 .8em; font-size:1.05rem; }',
        ' #news ul { list-style:none; margin:0; padding:0 0 0 1.4rem; }',
        ' #news li { position:relative; padding-bottom:1rem; }',
        ' #news li:last-child { padding-bottom:0; }',
        # Dot + rail timeline (guides card language, fixed light colors).
        ' #news li::before { content:""; position:absolute; left:-1.4rem;',
        '  top:.45rem; width:10px; height:10px; border-radius:50%;',
        '  background:#8c959e; z-index:1; }',
        ' #news li::after { content:""; position:absolute;',
        '  left:calc(-1.4rem + 4px); top:16px; bottom:-.25rem; width:2px;',
        '  background:#d0d7de; }',
        ' #news li:last-child::after { display:none; }',
        ' #news time.nw-date { display:block; font-size:.8rem;',
        '  color:#57606a; margin-bottom:.15rem; }',
        ' #news .nw-sub { margin:.2rem 0 0; font-size:.9rem; color:#57606a;',
        '  line-height:1.45; }',
        ' #news .nw-sub a { color:#0969da; text-decoration:none; }',
        ' #news .nw-sub a:hover { text-decoration:underline; }',
        ' #news .nw-dict-title { font-weight:600; color:#1f2328;',
        '  text-decoration:none; }',
        ' #news .nw-dict-title:hover { color:#0969da; }',
        ' #news .nw-badge-dict { font-size:.72em; font-weight:700;',
        '  color:#0969da; margin-left:.35em; }',
        ' #news .nw-author { color:#57606a; font-size:.85em; }',
        ' #news .nw-summary { margin:.2rem 0 0; font-size:.9rem;',
        '  color:#57606a; line-height:1.45; }',
        '</style>',
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
        lines.append('  <li class="nw-item">')
        lines.append('   <time class="nw-date" datetime="%s" '
                     'data-iso="%s">%s</time>' % (date, date, date))
        lines.append('   <a href="%s" target="_blank" rel="noopener">%s</a> '
                     % (url, title))
        lines.append('   <span style="color:%s; font-weight:bold;">'
                     '[%s]</span> ' % (html.escape(color, quote=True), status))
        lines.append('   <span class="nw-author">— %s</span>' % author)
        if isinstance(summary, str) and summary.strip():
            lines.append('   <p class="nw-summary">%s</p>'
                         % html.escape(summary))
        lines.append('  </li>')
    if dict_items:
        import homepage_dict_updates as hdu  # lazy: that module imports us
        lines.extend(hdu.render_rows(dict_items))
    lines.append(' </ul>')
    # Absolute ISO dates are in the HTML (no-JS fallback); this tiny inline
    # script swaps them for viewer-relative labels ("3 days ago") on load —
    # the guides mount-effect behavior without a framework (H8215).
    lines.append(' <script>')
    lines.append('  (function(){')
    lines.append('   var M=["Jan","Feb","Mar","Apr","May","Jun",'
                 '"Jul","Aug","Sep","Oct","Nov","Dec"];')
    lines.append('   function rel(iso){')
    lines.append('    var p=iso.split("-");')
    lines.append('    var then=new Date(+p[0],+p[1]-1,+p[2]);')
    lines.append('    var now=new Date();')
    lines.append('    var today=new Date(now.getFullYear(),now.getMonth(),'
                 'now.getDate());')
    lines.append('    var n=Math.round((today-then)/86400000);')
    lines.append('    if(n<=0)return "today";')
    lines.append('    if(n===1)return "yesterday";')
    lines.append('    if(n<7)return n+" days ago";')
    lines.append('    if(n<14)return "last week";')
    lines.append('    if(n<60)return Math.floor(n/7)+" weeks ago";')
    lines.append('    if(n<365)return Math.floor(n/30)+" months ago";')
    lines.append('    return (+p[2])+" "+M[+p[1]-1]+" "+p[0];')
    lines.append('   }')
    lines.append('   var nodes=document.querySelectorAll('
                 '"#news time.nw-date[data-iso]");')
    lines.append('   for(var i=0;i<nodes.length;i++){')
    lines.append('    var iso=nodes[i].getAttribute("data-iso");')
    lines.append('    if(/^\\d{4}-\\d{2}-\\d{2}$/.test(iso))'
                 'nodes[i].textContent=rel(iso);')
    lines.append('   }')
    lines.append('  })();')
    lines.append(' </script>')
    lines.append('</div>')
    return lines


def widget_lines(feed_path=DEFAULT_FEED, n=MAX_ITEMS, dict_feed_path=None):
    """Generation-path entry point: both feeds -> HTML lines, fail soft.

    H8170 contract (pinned by fixtures): a missing/malformed NEWS feed
    degrades to NO widget lines at all.  H8215 addition: the dictionary
    block fails independently — a bad dict feed yields news-only lines,
    never an exception on the generation path.
    """
    try:
        items = load_feed(feed_path)
    except FeedError as exc:
        import sys
        sys.stderr.write('homepage news widget skipped: %s\n' % exc)
        return []
    news = select_items(items, n)
    dict_items = []
    try:
        import homepage_dict_updates as hdu  # lazy: that module imports us
        path = dict_feed_path or hdu.DEFAULT_FEED
        dict_items = hdu.select_items(hdu.load_feed(path))
    except Exception as exc:  # fail-soft by contract — never break generation
        import sys
        sys.stderr.write('homepage dict-updates block skipped: %s\n' % exc)
    return render_widget(news, dict_items)
