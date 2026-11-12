# coding=utf-8
"""Acceptance fixtures for the homepage news widget (H8170).

Covers, per the handoff's acceptance list:
  - selection with MORE than three eligible items,
  - unselected (eligible: false) and unpublished drafts,
  - stable publication ordering after text edits,
  - author fallback and optional personal byline,
  - all three work statuses,
  - the completion / earlier-announcement relation (status flips, date stable),
  - deterministic handling of equal publication dates,
  - HTML escaping and unsafe-link handling,
  - absent/malformed feed data (fail soft, no crash),
  - fewer than three real entries (never invented filler).

Stdlib unittest only; no network, no csl-guides checkout required.
"""
import json
import os
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

import homepage_news as hn  # noqa: E402


def item(**overrides):
    base = {
        'date': '2026-08-31',
        'slug': 'news-a',
        'title': 'A news item',
        'summary': 'Summary of the item.',
        'status': 'Published',
        'url': 'https://sanskrit-lexicon.github.io/csl-guides/news/news-a',
        'eligible': True,
        'draft': False,
    }
    base.update(overrides)
    return base


class SelectTests(unittest.TestCase):

    def test_more_than_three_eligible_takes_three_latest(self):
        items = [
            item(date='2026-01-01', slug='old-1'),
            item(date='2026-06-28', slug='mid'),
            item(date='2026-07-28', slug='new-2'),
            item(date='2026-08-31', slug='new-1'),
            item(date='2025-05-05', slug='old-2'),
        ]
        got = hn.select_items(items)
        self.assertEqual([i['slug'] for i in got],
                         ['new-1', 'new-2', 'mid'])

    def test_unselected_item_never_selected(self):
        items = [
            item(date='2026-09-09', slug='unselected', eligible=False),
            item(date='2026-08-01', slug='selected'),
        ]
        got = hn.select_items(items)
        self.assertEqual([i['slug'] for i in got], ['selected'])

    def test_draft_never_selected_even_when_marked(self):
        items = [
            item(date='2026-09-30', slug='sept-draft', draft=True),
            item(date='2026-08-31', slug='published'),
        ]
        got = hn.select_items(items)
        self.assertEqual([i['slug'] for i in got], ['published'])

    def test_ordering_stable_after_text_edit(self):
        # Text edits preserve publication date and must not bump an item
        # upward: same dates in, same order out, regardless of summary text.
        before = [
            item(date='2026-08-31', slug='a', summary='original text'),
            item(date='2026-07-28', slug='b', summary='original text'),
            item(date='2026-06-28', slug='c', summary='original text'),
        ]
        after = [
            item(date='2026-08-31', slug='a', summary='edited, longer, text'),
            item(date='2026-07-28', slug='b', summary='x'),
            item(date='2026-06-28', slug='c', summary='y'),
        ]
        self.assertEqual([i['slug'] for i in hn.select_items(before)],
                         [i['slug'] for i in hn.select_items(after)])

    def test_equal_dates_deterministic_slug_asc(self):
        items = [
            item(date='2026-06-28', slug='zeta-news'),
            item(date='2026-06-28', slug='alpha-news'),
            item(date='2026-06-28', slug='mid-news'),
        ]
        got = hn.select_items(items)
        self.assertEqual([i['slug'] for i in got],
                         ['alpha-news', 'mid-news', 'zeta-news'])

    def test_completion_relation_date_stable_status_flips(self):
        # Completion produces a separate result article linked to the earlier
        # announcement; the earlier announcement's status updates WITHOUT
        # changing its publication date.
        announcement = item(date='2026-07-01', slug='announce',
                            status='In progress')
        result = item(date='2026-08-15', slug='result',
                      status='Published', related='announce')
        got = hn.select_items([announcement, result])
        self.assertEqual([i['slug'] for i in got], ['result', 'announce'])
        # flip the earlier announcement to Published: date/order unchanged
        announcement_done = dict(announcement, status='Published')
        got2 = hn.select_items([announcement_done, result])
        self.assertEqual([i['slug'] for i in got2], ['result', 'announce'])
        self.assertEqual(got2[1]['date'], '2026-07-01')
        self.assertEqual(got2[1]['status'], 'Published')

    def test_all_three_statuses_rendered(self):
        items = [
            item(date='2026-08-31', slug='p', status='Published'),
            item(date='2026-07-28', slug='i', status='In progress'),
            item(date='2026-06-28', slug='l', status='Planned'),
        ]
        html_out = '\n'.join(hn.render_widget(hn.select_items(items)))
        for label in ('[Published]', '[In progress]', '[Planned]'):
            self.assertIn(label, html_out)

    def test_invalid_status_or_url_or_date_skipped(self):
        items = [
            item(date='2026-09-01', slug='bad-status', status='Done'),
            item(date='2026-09-02', slug='bad-url',
                 url='javascript:alert(1)'),
            item(date='not-a-date', slug='bad-date'),
            item(date='9999-99-99', slug='impossible-date'),
            item(date='2026-08-01', slug='good'),
        ]
        got = hn.select_items(items)
        self.assertEqual([i['slug'] for i in got], ['good'])

    def test_draft_string_true_fails_closed(self):
        # Reviewer nit (H8170): a hand-edited feed with draft: "true"
        # (string) must be excluded exactly like the boolean.
        items = [
            item(date='2026-09-30', slug='str-draft', draft='true'),
            item(date='2026-08-31', slug='published'),
        ]
        self.assertEqual([i['slug'] for i in hn.select_items(items)],
                         ['published'])

    def test_fewer_than_three_yields_fewer_never_filler(self):
        got = hn.select_items([item(date='2026-08-31', slug='only')])
        self.assertEqual(len(got), 1)

    def test_empty_feed_renders_no_section(self):
        self.assertEqual(hn.select_items([]), [])
        self.assertEqual(hn.render_widget([]), [])


class AuthorTests(unittest.TestCase):

    def test_default_author_fallback(self):
        self.assertEqual(hn.author_of(item()), 'CDSL Editorial Team')

    def test_optional_personal_byline(self):
        self.assertEqual(
            hn.author_of(item(author='Dr. Mārcis Gasūns')),
            'Dr. Mārcis Gasūns')

    def test_blank_author_falls_back(self):
        self.assertEqual(hn.author_of(item(author='   ')),
                         'CDSL Editorial Team')


class RenderTests(unittest.TestCase):

    def test_html_escaping_in_title_summary_author(self):
        nasty = item(
            title='<script>alert("x")</script>',
            summary='"quoted" & <b>bold</b>',
            author='Eve <eve@evil.example>',
        )
        html_out = '\n'.join(hn.render_widget([nasty]))
        self.assertNotIn('<script>alert', html_out)
        self.assertIn('&lt;script&gt;', html_out)
        self.assertIn('&amp;', html_out)
        self.assertNotIn('<b>bold</b>', html_out)
        self.assertIn('Eve &lt;eve@evil.example&gt;', html_out)

    def test_url_escaped_in_href_attribute(self):
        risky = item(url='https://example.test/?a=1&b=<x>')
        html_out = '\n'.join(hn.render_widget([risky]))
        self.assertIn('a=1&amp;b=&lt;x&gt;', html_out)
        self.assertNotIn('b=<x>', html_out)

    def test_widget_placement_helpers_output(self):
        html_out = '\n'.join(hn.render_widget([item()]))
        self.assertIn('id="news"', html_out)
        self.assertIn('Latest news', html_out)
        self.assertIn('2026-08-31', html_out)
        self.assertIn('CDSL Editorial Team', html_out)


class FeedErrorTests(unittest.TestCase):

    def test_missing_feed_raises_feed_error(self):
        with self.assertRaises(hn.FeedError):
            hn.load_feed(os.path.join(tempfile.gettempdir(),
                                      'no-such-feed-h8170.json'))

    def test_malformed_json_raises_feed_error(self):
        with tempfile.NamedTemporaryFile('w', suffix='.json',
                                         delete=False) as tmp:
            tmp.write('{not json')
            path = tmp.name
        try:
            with self.assertRaises(hn.FeedError):
                hn.load_feed(path)
        finally:
            os.unlink(path)

    def test_wrong_shape_raises_feed_error(self):
        with tempfile.NamedTemporaryFile('w', suffix='.json',
                                         delete=False) as tmp:
            json.dump(['not', 'an', 'object'], tmp)
            path = tmp.name
        try:
            with self.assertRaises(hn.FeedError):
                hn.load_feed(path)
        finally:
            os.unlink(path)

    def test_widget_lines_fail_soft_on_bad_feed(self):
        # Generation path: bad feed => no widget lines, no exception.
        out = hn.widget_lines(os.path.join(tempfile.gettempdir(),
                                           'no-such-feed-h8170.json'))
        self.assertEqual(out, [])

    def test_real_committed_feed_is_valid_and_selects_three(self):
        items = hn.load_feed(hn.DEFAULT_FEED)
        got = hn.select_items(items)
        self.assertEqual(len(got), 3)
        self.assertEqual(got[0]['date'], '2026-08-31')
        dates = [i['date'] for i in got]
        self.assertEqual(dates, sorted(dates, reverse=True))


if __name__ == '__main__':
    unittest.main()
