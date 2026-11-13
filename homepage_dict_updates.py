# coding=utf-8
"""Dictionary-update rows for the hybrid homepage "Latest news" section.

Mechanical half of the hybrid widget (design tree closed by interactive
grill-with-docs, 13-11-2026): one row per dictionary = that dictionary's
most recent eligible commit in csl-orig touching ``v02/<code>/`` inside
the fixed build window.  These rows are NOT editorial news — they are
derived from git history by ``scripts/build_dict_updates.py`` and
rendered BELOW the H8170 editorial news block.  Approved ordering: news
always above commits (13-11-2026).

Domain glossary additions (the news half lives in homepage_news.py):

- dictionary update row  one (date, dictionary) row whose commit is the
                         newest eligible csl-orig commit touching that
                         dictionary's source directory within the window
- code                    the indexdirs.xml ``<pfx>`` of the dictionary,
                          matched case-insensitively against the first
                          path segment under ``v02/``
- subject                 the commit subject after cleaning: DC batches
                          become ``Corrections · csl-corrections#N``,
                          conventional prefixes, redundant per-row code
                          prefixes and trailing issue/PR references are
                          stripped; an empty result falls back to the
                          raw subject
- window                  the fixed ``--since "6 months ago"`` build
                          window: the feed is a pure function of
                          (csl-orig history, window, indexdirs.xml) —
                          no wall-clock in the output, so the CI check
                          is byte-exact

Fail soft, same contract as the news half: a missing or malformed feed
degrades to *no dictionary rows* (the news block still renders); it can
never break page generation or dictionary access.
"""
from __future__ import print_function

import html
import os
import re

import homepage_news as hn  # shared contract: FeedError, load_feed, valid_date

DEFAULT_FEED = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'homepage_dict_updates.json')
DICT_MAX = 4
COMMIT_BASE = 'https://github.com/sanskrit-lexicon/csl-orig/commit/'
CODE_RE = re.compile(r'^[A-Za-z0-9]{1,10}$')

BADGE_TEXT = '[dictionary update]'
BADGE_COLOR = '#0969da'   # GitHub blue — distinct from work-status colors


def load_feed(path=DEFAULT_FEED):
    """Read homepage_dict_updates.json -> raw items list.

    Reuses the news-half loader: raises hn.FeedError for a missing file
    or a malformed document (no "items" list).
    """
    return hn.load_feed(path)


def _valid_commit_url(url):
    """Fail closed: only github.com/.../csl-orig/commit/<hex> links."""
    if not isinstance(url, str) or not url.startswith(COMMIT_BASE):
        return False
    sha = url[len(COMMIT_BASE):]
    return bool(re.match(r'^[0-9a-f]{7,40}$', sha))


def _valid_display(display):
    """A display link must be a host-relative /scans/ path (never a
    scheme, so javascript:/data: are impossible)."""
    return (display is None
            or (isinstance(display, str)
                and display.startswith('/scans/')
                and '://' not in display
                and '\n' not in display))


def select_items(items, n=DICT_MAX):
    """Validate, deterministically order, cap at n rows.

    Order: date DESC, then code ASC (deterministic even for same-day
    batches — the builder emits the same order).
    """
    picked = []
    for item in items:
        if not isinstance(item, dict):
            continue
        date = item.get('date')
        if not hn.valid_date(date):
            continue
        code = item.get('code')
        if not isinstance(code, str) or not CODE_RE.match(code):
            continue
        title = item.get('title')
        if not isinstance(title, str) or not title.strip():
            continue
        subject = item.get('subject')
        if not isinstance(subject, str) or not subject.strip():
            continue
        if not _valid_commit_url(item.get('url')):
            continue
        if not _valid_display(item.get('display')):
            continue
        picked.append(item)
    picked.sort(key=lambda it: (tuple(-int(p) for p in it['date'].split('-')),
                                it['code']))
    return picked[:n]


def render_rows(items):
    """Render validated dictionary rows to <li> HTML lines; [] when empty.

    All text and attribute values are escaped context-correctly.  The
    dictionary title links to the basic display (same-host /scans/ path
    as the catalogue above), the subject line links to the csl-orig
    commit.  Rows never render without validation — select first.
    """
    lines = []
    for item in items:
        date = html.escape(str(item['date']))
        code = html.escape(item['code'])
        title = html.escape(item['title'].strip())
        subject = html.escape(' '.join(item['subject'].split()))
        commit = html.escape(item['url'], quote=True)
        display = item.get('display')

        label = '%s (%s)' % (title, code)
        if display:
            name = ('<a class="nw-dict-title" href="%s">%s</a>'
                    % (html.escape(display, quote=True), label))
        else:
            name = '<span class="nw-dict-title">%s</span>' % label

        lines.append('  <li class="nw-item">')
        lines.append('   <time class="nw-date" datetime="%s" '
                     'data-iso="%s">%s</time>' % (date, date, date))
        lines.append('   %s <span class="nw-badge nw-badge-dict" '
                     'style="color:%s;">%s</span>'
                     % (name, BADGE_COLOR, BADGE_TEXT))
        lines.append('   <p class="nw-sub">%s '
                     '<a class="nw-commit" href="%s" target="_blank" '
                     'rel="noopener">&rarr; commit</a></p>'
                     % (subject, commit))
        lines.append('  </li>')
    return lines
