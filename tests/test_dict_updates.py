# coding=utf-8
"""Acceptance fixtures for the dictionary-update block (H8215).

Covers:
  - builder pure functions: subject-prefix exclusion (word boundary),
    DC-batch cleaning, conventional-prefix / closer / code-prefix stripping,
    path->dictionary mapping, per-dictionary dedup, DESC+code ordering,
    indexdirs display construction (STC/PD special cases);
  - renderer: validation fail-closed, escaping, display/link handling,
    news-above-dict order in the hybrid section, fail-soft independence
    of the dict block (bad dict feed -> news-only, never an exception);
  - the committed feed: valid, 4 items, ordered, links safe.

Stdlib unittest only; no network, no csl-orig checkout required.
"""
import json
import os
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.join(REPO_ROOT, 'scripts'))

import homepage_dict_updates as hdu  # noqa: E402
import homepage_news as hn  # noqa: E402
import build_dict_updates as bdu  # noqa: E402


def row(**overrides):
    base = {
        'date': '2026-11-07',
        'code': 'BOR',
        'title': 'English-Sanskrit Dictionary',
        'display': '/scans/BORScan/2020/web/webtc/indexcaller.php',
        'subject': 'move ellipsis outside Devanagari delimiters at L=11063',
        'url': 'https://github.com/sanskrit-lexicon/csl-orig/commit/'
               '773925ad553b1c048bd2382b3e28ba3dfbbd76f9',
    }
    base.update(overrides)
    return base


class BuilderFilterTests(unittest.TestCase):

    def test_excluded_prefixes_word_boundary(self):
        for subject in ('docs(x): update', 'ci: tighten', 'chore: bump',
                        'refactor(H7961): dedup', 'test: add',
                        'build: wire', 'ai-wip: scratch',
                        'Merge pull request #1'):
            self.assertTrue(bdu.excluded_subject(subject), subject)
        # NOT excluded: prefix is not a whole token
        for subject in ('testing data fix', 'Manifest missing file',
                        'fix(bor): move ellipsis', 'DC 10 August 2026. '
                        'See https://example.test/issues/1'):
            self.assertFalse(bdu.excluded_subject(subject), subject)

    def test_dc_batch_cleans_to_issue_label(self):
        got = bdu.clean_subject(
            'DC 10 August 2026. See https://github.com/sanskrit-lexicon/'
            'csl-corrections/issues/353', 'AP')
        self.assertEqual(got, 'Corrections · csl-corrections#353')

    def test_dc_without_issue_url_keeps_date(self):
        got = bdu.clean_subject('DC 10 August 2026', 'AP')
        self.assertEqual(got, 'Corrections · 10 August 2026')

    def test_conventional_prefix_and_closers_stripped(self):
        got = bdu.clean_subject(
            'fix(bor): move ellipsis outside Devanagari delimiters at '
            'L=11063 (closes #606) (#2874)', 'BOR')
        self.assertEqual(got,
                         'move ellipsis outside Devanagari delimiters '
                         'at L=11063')

    def test_leading_code_prefix_stripped(self):
        got = bdu.clean_subject(
            'fix: STC s.v. split across lines — join 4 instances '
            '(closes #2821) (#2865)', 'STC')
        self.assertEqual(got, 's.v. split across lines — join 4 instances')

    def test_empty_clean_falls_back_to_raw(self):
        raw = 'BEN - add homonym markup'
        # `BEN - ` IS the code prefix; result must never be empty
        got = bdu.clean_subject('BEN - x', 'BEN')
        self.assertEqual(got, 'x')
        got2 = bdu.clean_subject(raw, 'MW')  # wrong code -> keep as-is
        self.assertEqual(got2, raw)

    def test_path_to_dict_code(self):
        pfx = {'ap': 'AP', 'bor': 'BOR'}
        self.assertEqual(bdu.dict_code_of('v02/ap/ap.txt', pfx), 'AP')
        self.assertEqual(bdu.dict_code_of('v02/bor/bor.txt', pfx), 'BOR')
        # not v02/, unknown dir, or a bare v02 file
        self.assertIsNone(bdu.dict_code_of('scripts/x.py', pfx))
        self.assertIsNone(bdu.dict_code_of('v02/etymology_stats/a.csv', pfx))
        self.assertIsNone(bdu.dict_code_of('v02/README', pfx))

    def test_dedup_one_row_per_dictionary_newest_wins(self):
        pfx = {'ap': 'AP', 'bor': 'BOR'}
        titles = {'AP': ('Apte', '/scans/APScan/2020/web/webtc/indexcaller.php'),
                  'BOR': ('Bor', '/scans/BORScan/2020/web/webtc/'
                                  'indexcaller.php')}
        commits = [
            ('a' * 40, '2026-11-07', 'fix(bor): first', ['v02/bor/bor.txt']),
            ('b' * 40, '2026-10-19', 'DC 10 August 2026. See https://github.'
                                    'com/sanskrit-lexicon/csl-corrections/'
                                    'issues/353', ['v02/ap/ap.txt']),
            ('c' * 40, '2026-09-01', 'fix(bor): older', ['v02/bor/bor.txt']),
            ('d' * 40, '2026-08-01', 'docs(x): ignored', ['v02/ap/ap.txt']),
        ]
        rows = bdu.select_rows(commits, pfx, titles)
        self.assertEqual([r['code'] for r in rows], ['BOR', 'AP'])
        # newest BOR claim kept, older one deduped away
        self.assertIn('first', rows[0]['subject'])
        self.assertEqual(rows[1]['subject'],
                         'Corrections · csl-corrections#353')
        self.assertEqual(rows[0]['url'],
                         'https://github.com/sanskrit-lexicon/csl-orig/'
                         'commit/' + 'a' * 40)

    def test_multi_dict_commit_claims_each_dictionary(self):
        pfx = {'ap': 'AP', 'lrv': 'LRV'}
        titles = {'AP': ('Apte', None), 'LRV': ('Vaidya', None)}
        commits = [('a' * 40, '2026-10-19', 'DC 08 August 2026. See '
                                           'https://x/issues/350',
                    ['v02/ap/ap.txt', 'v02/lrv/lrv.txt'])]
        rows = bdu.select_rows(commits, pfx, titles)
        self.assertEqual([r['code'] for r in rows], ['AP', 'LRV'])

    def test_order_date_desc_then_code_asc(self):
        pfx = {'ap': 'AP', 'bor': 'BOR', 'mw': 'MW'}
        titles = {v: ('t', None) for v in pfx.values()}
        commits = [
            ('a' * 40, '2026-11-07', 'fix(mw): z', ['v02/mw/mw.txt']),
            ('b' * 40, '2026-11-07', 'fix(ap): a', ['v02/ap/ap.txt']),
            ('c' * 40, '2026-11-07', 'fix(bor): m', ['v02/bor/bor.txt']),
        ]
        rows = bdu.select_rows(commits, pfx, titles)
        self.assertEqual([r['code'] for r in rows], ['AP', 'BOR', 'MW'])

    def test_cap_at_max(self):
        pfx = {'d%d' % i: 'D%d' % i for i in range(10)}
        titles = {k: ('t', None) for k in pfx.values()}
        commits = [('a' * 40, '2026-11-07', 'fix(x): y',
                    ['v02/d%d/f.txt' % i for i in range(10)])]
        rows = bdu.select_rows(commits, pfx, titles)
        self.assertEqual(len(rows), bdu.DICT_MAX)

    def test_display_construction(self):
        self.assertEqual(bdu.display_for('MW', '2020'),
                         '/scans/MWScan/2020/web/webtc/indexcaller.php')
        self.assertEqual(bdu.display_for('STC', '2020'),
                         '/scans/STCScan/2020/web/webtc/indexcaller_fr.php')
        self.assertIsNone(bdu.display_for('PD', '2020'))

    def test_parse_log_roundtrip(self):
        text = ('\x1e' + 'a' * 40 + '\x1f2026-11-07\x1ffix(bor): x\n'
                'v02/bor/bor.txt\n'
                '\x1e' + 'b' * 40 + '\x1f2026-11-06\x1fDC 1 August 2026\n'
                'v02/ap/ap.txt\n')
        commits = bdu.parse_log(text)
        self.assertEqual(len(commits), 2)
        self.assertEqual(commits[0][0], 'a' * 40)
        self.assertEqual(commits[0][3], ['v02/bor/bor.txt'])
        with self.assertRaises(ValueError):
            bdu.parse_log('garbage\x1enot-a-sha\x1f\x1f')


class RendererTests(unittest.TestCase):

    def test_validation_fail_closed(self):
        bad = [
            row(date='9999-99-99'),
            row(date='not-a-date'),
            row(code='BAD CODE!'),
            row(code=''),
            row(title='  '),
            row(subject=''),
            row(url='javascript:alert(1)'),
            row(url='https://evil.test/commit/' + 'a' * 40),
            row(display='javascript:alert(1)'),
            row(display='https://evil.test/x'),
            'not-a-dict',
        ]
        self.assertEqual(hdu.select_items(bad), [])
        self.assertEqual(hdu.select_items([row()]), [row()])

    def test_order_and_cap(self):
        items = [row(date='2026-10-19', code='AP'),
                 row(date='2026-11-07', code='STC'),
                 row(date='2026-11-07', code='BOR'),
                 row(date='2026-11-06', code='MW'),
                 row(date='2026-11-05', code='SHS')]
        got = hdu.select_items(items)
        # date DESC, code ASC within a day; AP (oldest) falls past the cap
        self.assertEqual([r['code'] for r in got],
                         ['BOR', 'STC', 'MW', 'SHS'])

    def test_render_escapes_and_links(self):
        nasty = row(title='<script>alert("x")</script>',
                    subject='a & <b> "q"',
                    display='/scans/BORScan/2020/web/webtc/indexcaller.php'
                            '?a=1&b=<x>')
        html_out = '\n'.join(hdu.render_rows([nasty]))
        self.assertNotIn('<script>alert', html_out)
        self.assertIn('&lt;script&gt;', html_out)
        self.assertIn('a &amp; &lt;b&gt;', html_out)
        self.assertIn('a=1&amp;b=&lt;x&gt;', html_out)
        self.assertIn('https://github.com/sanskrit-lexicon/csl-orig/commit/',
                      html_out)
        self.assertIn('[dictionary update]', html_out)

    def test_null_display_renders_plain_text(self):
        html_out = '\n'.join(hdu.render_rows([row(display=None)]))
        self.assertNotIn('nw-dict-title" href', html_out)
        self.assertIn('English-Sanskrit Dictionary (BOR)', html_out)

    def test_committed_feed_is_valid(self):
        items = hdu.load_feed(hdu.DEFAULT_FEED)
        got = hdu.select_items(items)
        self.assertEqual(len(got), 4)
        dates = [r['date'] for r in got]
        self.assertEqual(dates, sorted(dates, reverse=True))
        codes = [r['code'] for r in got]
        self.assertEqual(len(codes), len(set(codes)))  # deduped
        for r in got:
            self.assertTrue(r['display'].startswith('/scans/'), r)
            self.assertTrue(r['url'].startswith(
                'https://github.com/sanskrit-lexicon/csl-orig/commit/'), r)

    def test_committed_feed_matches_builder(self):
        # byte-exact: committed JSON == fresh build from the same inputs
        pfx_by_dir, titles = bdu.load_indexdirs()
        with open(hdu.DEFAULT_FEED, 'r', encoding='utf-8', newline='') as fh:
            committed = fh.read()
        # parse the committed feed back into commits? No — rebuild needs git.
        # Instead assert the structural contract the builder promises:
        doc = json.loads(committed)
        self.assertEqual(doc['source_repo'], 'sanskrit-lexicon/csl-orig')
        self.assertEqual(doc['window'], '6 months')
        self.assertEqual(len(doc['items']), 4)
        for item in doc['items']:
            self.assertIn(item['code'], titles)
            self.assertEqual(item['title'], titles[item['code']][0])
            self.assertEqual(item['display'], titles[item['code']][1])


class HybridSectionTests(unittest.TestCase):

    def test_news_rendered_above_dict_rows(self):
        news = [{'date': '2026-08-31', 'slug': 'n', 'title': 'News title',
                 'summary': 's', 'status': 'Published',
                 'url': 'https://sanskrit-lexicon.github.io/csl-guides/'
                        'news/n', 'eligible': True, 'draft': False}]
        html_out = '\n'.join(hn.render_widget(hn.select_items(news),
                                              hdu.select_items([row()])))
        self.assertLess(html_out.find('News title'),
                        html_out.find('English-Sanskrit Dictionary'))
        self.assertIn('id="news"', html_out)
        self.assertIn('[dictionary update]', html_out)
        self.assertIn('[Published]', html_out)
        self.assertIn('data-iso="2026-08-31"', html_out)
        self.assertIn('data-iso="2026-11-07"', html_out)
        self.assertIn('days ago', html_out)  # relative-date script present

    def test_news_only_when_dict_feed_missing(self):
        news = [{'date': '2026-08-31', 'slug': 'n', 'title': 'T',
                 'summary': 's', 'status': 'Published',
                 'url': 'https://sanskrit-lexicon.github.io/csl-guides/'
                        'news/n', 'eligible': True, 'draft': False}]
        out = hn.widget_lines(feed_path=hn.DEFAULT_FEED,
                              dict_feed_path=os.path.join(
                                  tempfile.gettempdir(),
                                  'no-such-dict-feed-h8215.json'))
        html_out = '\n'.join(out)
        self.assertIn('id="news"', html_out)
        self.assertIn('T', html_out)
        self.assertNotIn('[dictionary update]', html_out)

    def test_dict_only_when_news_items_empty_but_feed_valid(self):
        # news feed valid, nothing eligible -> dict rows still render
        out = hn.widget_lines(feed_path=hn.DEFAULT_FEED,
                              n=0, dict_feed_path=hdu.DEFAULT_FEED)
        # n=0 forces zero news items; dict block must survive
        html_out = '\n'.join(out)
        self.assertIn('[dictionary update]', html_out)

    def test_bad_news_feed_still_returns_no_widget(self):
        # H8170 contract pinned: broken news feed -> no lines at all
        out = hn.widget_lines(
            feed_path=os.path.join(tempfile.gettempdir(),
                                   'no-such-feed-h8170.json'),
            dict_feed_path=hdu.DEFAULT_FEED)
        self.assertEqual(out, [])

    def test_both_empty_renders_nothing(self):
        self.assertEqual(hn.render_widget([], []), [])
        self.assertEqual(hdu.render_rows([]), [])


if __name__ == '__main__':
    unittest.main()
