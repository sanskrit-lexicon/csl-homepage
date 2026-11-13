# csl-homepage

_Created: 08-08-2018 · Last updated: 11-07-2026_

CDSL **web-frontend** repository in the [sanskrit-lexicon](https://github.com/sanskrit-lexicon) project. It holds the code and data that **generate the landing page** of the Cologne Digital Sanskrit Dictionaries site at [www.sanskrit-lexicon.uni-koeln.de](https://www.sanskrit-lexicon.uni-koeln.de/).

This repository is a fork of [funderburkjim/old-sanlexhome](https://github.com/funderburkjim/old-sanlexhome).

## What this repo is (and is not)

- **This repo generates static HTML** that is then installed on the Cologne server (`uni-koeln.de`) and on a local XAMPP test server. GitHub Pages is **not** enabled here — the built page is not served from GitHub.
- It is **distinct from** [sanskrit-lexicon.github.io](https://github.com/sanskrit-lexicon/sanskrit-lexicon.github.io), which is the org's GitHub-Pages content repo. Do not confuse the two: `csl-homepage` produces the Cologne-hosted dictionary landing page; `sanskrit-lexicon.github.io` is the separately-deployed Pages site.

## How it works

The dictionary catalogue lives in [`indexdirs.xml`](https://github.com/sanskrit-lexicon/csl-homepage/blob/main/indexdirs.xml) (one `<entry>` per dictionary — currently 44). Two generator scripts read it and emit the homepage HTML for the two target environments:

- [`index_cologne.py`](https://github.com/sanskrit-lexicon/csl-homepage/blob/main/index_cologne.py) — builds the production page for the Cologne server.
- [`index_xampp.py`](https://github.com/sanskrit-lexicon/csl-homepage/blob/main/index_xampp.py) — builds the equivalent page for the local XAMPP test server; its committed output is [`index_xampp.html`](https://github.com/sanskrit-lexicon/csl-homepage/blob/main/index_xampp.html).

Version stamping is handled by [`update_version.sh`](https://github.com/sanskrit-lexicon/csl-homepage/blob/main/update_version.sh) (semantic version `majorminor.patch`, where `patch` is the number of `csl-orig` commits since the last `majorminor` bump — currently `majorminor="2.10"`). The regeneration is driven by [`redo_cologne.sh`](https://github.com/sanskrit-lexicon/csl-homepage/blob/main/redo_cologne.sh) and [`redo_xampp.sh`](https://github.com/sanskrit-lexicon/csl-homepage/blob/main/redo_xampp.sh).

The step-by-step operator recipe for adding a new dictionary to the homepage (edit `indexdirs.xml`, revise both generators, bump the version, rebuild, install on both servers) is kept in [`readme_update.txt`](https://github.com/sanskrit-lexicon/csl-homepage/blob/main/readme_update.txt).

## Homepage news widget (H8170)

The generated landing page carries a **Latest news** section directly after the
dictionary catalogue: the three latest explicitly eligible news items with
publication date, title, work status, author and a link to the full article in
the [csl-guides news section](https://sanskrit-lexicon.github.io/csl-guides/news/).
Fewer eligible items means fewer real items — never invented filler.

**Approved decisions (interactive design interview, 12-11-2026):** a mixed feed
of dictionary/data updates, site capabilities, editorial materials, plans and
work in progress; English public-facing text; widget after the catalogue (not
before it, not in a sidebar); the three latest eligible items by publication
date; each item shows date, short outcome/plan, author, status and full-article
link (archive included); default author *CDSL Editorial Team* with an optional
personal byline; statuses *Published / In progress / Planned* describe the
announced work (draft news is never public just because its work status is
Planned); eligibility only via an explicit editorial marker — never inferred
from a commit, GitHub release, Markdown filename or file existence; text edits
preserve publication dates and never bump an item upward; completion produces a
separate result article linked to the earlier announcement and updates the
earlier announcement's status without changing its date; source is CDSL news
content (csl-guides articles), not the csl-guides software CHANGELOG.md.

**Domain glossary**

| Term | Meaning |
|---|---|
| news article | a published page under `sanskrit-lexicon.github.io/csl-guides/news/<slug>` |
| publication date | the article's editorial date (ISO `YYYY-MM-DD`); stable across text edits |
| work status | `Published` · `In progress` · `Planned` — the state of the *announced work* |
| homepage eligibility | the explicit frontmatter marker `homepage: true` in csl-guides, propagated as `eligible: true` in `homepage_news.json` |

**How the data flows (no runtime API):**

1. Publish (or update) a news article in `csl-guides` `blog/`, and set its
   frontmatter: `homepage: true` plus `work_status:` (`Published` default).
   Optional: `author:` for a personal byline, `related:` for a completion
   article's link back to its earlier announcement.
2. Rebuild the committed feed from a csl-guides checkout:
   `python scripts/build_newsfeed.py --guides /path/to/csl-guides`
   and commit `homepage_news.json`. Drafts (`draft: true` or a `<!-- DRAFT`
   body marker) are refused by the extractor even when marked.
3. Regenerate the pages (`python index_cologne.py indexdirs.xml …`,
   `python index_xampp.py indexdirs.xml …`). A missing or malformed feed
   degrades to *no widget* — it can never break dictionary access.
4. Gate: `python tests/local_gate.py [--guides /path/to/csl-guides]`
   (selection/render fixtures + cite check + feed drift check).

Selection rules live in [`homepage_news.py`](homepage_news.py): explicit
eligibility only, drafts excluded, valid ISO date / https link / known status
required, ordered publication date DESC with equal dates broken by slug ASC.
The feed is never fetched at page-view time; the widget is static HTML in the
generated page. A merged source change is *not* a live university publication —
installing on the Cologne server follows the existing `redo_*.sh` operator
recipe and is out of scope for the widget work itself.

## Dictionary-update rows (H8215, hybrid extension 13-11-2026)

The **same section** carries a second, mechanically-derived block below the
editorial news: up to **4 dictionary-update rows**, one per dictionary, each
linking that dictionary's basic display and the responsible csl-orig commit.
Approved by interactive grill-with-docs on 13-11-2026 as the hybrid of two
earlier rulings: the H8170 editorial contract (12-11-2026) stays untouched
for the news block, and a new mechanical feed covers «what changed in the
dictionaries» — news first, commits below, strictly one section on the page.

**Approved decisions (grill-with-docs, 13-11-2026):**

- Source is csl-orig **git history**, never an editorial marker: commits
  touching `v02/<code>/` where `<code>` maps to an `indexdirs.xml` `<pfx>`,
  inside a fixed 6-month window, excluding subject prefixes
  `docs|ci|chore|refactor|test|build|ai-wip|Merge` (word-boundary — `test(x):`
  out, `testing data` in) and non-dictionary dirs (`etymology_stats`).
- **Dedup per dictionary**: one row per dictionary = its newest eligible
  commit (a multi-dict commit may claim several rows); order date DESC, code
  ASC; cap 4. Output is exactly what renders, so the wall-clock window can
  only drift the CI check when a *rendered* row ages out.
- Row = dictionary title from `indexdirs.xml` → basic display link
  (`/scans/<PFX>Scan/<year>/web/webtc/indexcaller.php`, STC → `_fr`, PD → no
  link) + cleaned commit subject → commit link. Cleaning: `DC <date>. See
  …/issues/N` → `Corrections · csl-corrections#N`, conventional prefixes and
  trailing closer/PR refs stripped, leading row-code prefix stripped,
  empty result falls back to the raw subject.
- Dates: absolute ISO in the HTML (no-JS fallback), a tiny inline vanilla
  script swaps them for viewer-relative labels ("3 days ago") on load — the
  guides behavior without a framework.
- Visual language: the csl-guides card (border, dot timeline, sans-serif
  inside the widget only) ported as plain HTML+CSS onto the static page.
- Fail soft per feed: a broken news feed keeps its H8170 contract (no widget
  at all); a broken dict feed degrades to the news block only — page
  generation never breaks.

**How the dict feed flows (no runtime API):**

1. Build from a csl-orig checkout: `python scripts/build_dict_updates.py
   --orig /path/to/csl-orig`, commit `homepage_dict_updates.json`.
   Deterministic output (no timestamps; date+code ordering) so the same
   inputs always produce the same bytes.
2. Gate: `python tests/local_gate.py --guides <csl-guides> --orig <csl-orig>`
   runs the fixtures + cite check + xampp regen check + **both** feed
   drift checks. CI (`.github/workflows/news-widget.yml`) clones csl-orig
   as a **shallow blobless clone** (`--shallow-since="6 months ago"`,
   ~118 MiB vs ~895 MiB full) and runs the same gate.
3. Regenerate pages (`python index_xampp.py indexdirs.xml index_xampp.html`,
   `index_cologne.py` likewise); `scripts/check_xampp_regen.py` proves the
   committed xampp page equals a fresh generation after masking the two
   volatile stamps (calendar date, csl-orig version) — catching a forgotten
   regen the way PR #28's regression class did.

**Domain glossary additions**

| Term | Meaning |
|---|---|
| dictionary update row | one (date, dictionary) row whose commit is the newest eligible csl-orig commit touching that dictionary's source dir in the window — mechanical, never editorially marked |
| code | the `indexdirs.xml` `<pfx>` of a dictionary; matched case-insensitively against the first path segment under `v02/` |
| subject (cleaned) | commit subject after DC→issue-label, conventional-prefix, closer and row-code stripping; empty ⇒ raw subject |
| window | fixed `--since "6 months ago"` in `build_dict_updates.py`; output = pure function of (csl-orig history, indexdirs.xml) — the CI check is byte-exact against a fresh shallow clone |
| regen check | committed `index_xampp.html` == fresh generation after masking only the calendar-date and version stamps |

Rejected: replacing the H8170 widget (two widgets on one page definitively
not wanted — hybrid chosen); client-side GitHub API fetch (no runtime API on
a university static page); full csl-orig checkout in CI (895 MiB vs a
118 MiB window clone). See `docs/adr/0001-hybrid-news-two-tier-feed.md`.

## Tech stack

- **Runtime**: Python (standard library only; XML via `xml.etree`) plus small POSIX shell wrappers.
- **Input data**: [`indexdirs.xml`](https://github.com/sanskrit-lexicon/csl-homepage/blob/main/indexdirs.xml).
- **Assets**: Cologne university seal, CLARIN logo, `Cologne.css`, and sample dictionary displays under [`ap_pd_samples/`](https://github.com/sanskrit-lexicon/csl-homepage/tree/main/ap_pd_samples).

## GitHub issue conventions

This repository follows the [Cologne tooling-repo taxonomy](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/runbook/cologne-tooling-runbook.md): exactly one **type** label, one **severity** level, and one **milestone** per issue. Details are in [`CLAUDE.md`](https://github.com/sanskrit-lexicon/csl-homepage/blob/main/CLAUDE.md). Tool work across the org is tracked on the [Tooling Roadmap](https://github.com/orgs/sanskrit-lexicon/projects/9).

## License

This repository contains both source code and dictionary/data files, licensed separately (dual-license approved 2026-06-18):

- **Source code** (`*.py`, `*.php`, `*.js`, `*.sh`) is licensed under the **GNU General Public License v3.0** — see [`licenses/GPL-3.0.txt`](https://github.com/sanskrit-lexicon/csl-homepage/blob/main/licenses/GPL-3.0.txt).
- **Dictionary and data files** are licensed under **Creative Commons Attribution-ShareAlike 4.0 International (CC-BY-SA-4.0)** — see [`LICENSE`](https://github.com/sanskrit-lexicon/csl-homepage/blob/main/LICENSE).

The Cologne university seal and CLARIN logo are third-party assets — see [`NOTICE`](https://github.com/sanskrit-lexicon/csl-homepage/blob/main/NOTICE).

_Dr. Mārcis Gasūns_
