# Hybrid news section: two-tier feed (editorial marker + mechanical git feed)

_Created: 13-11-2026 · Last updated: 13-11-2026_

The landing page's "Latest news" section (H8170) originally carried one
eligibility rule: an item reaches the homepage only through an explicit
editorial frontmatter marker — *never* inferred from a commit. The H8215
hybrid (grill-with-docs, 13-11-2026) adds a second block of up to four
**dictionary-update rows** derived mechanically from csl-orig git history
(`v02/<code>/` commits, 6-month window, per-dictionary dedup), because the
user's approved goal for the card is "what changed in the dictionaries" and
an editorial marker per dictionary fix would be pure ceremony nobody
maintains.

**Decision:** one section, two contracts, coexisting. The editorial rule is
NOT relaxed — it still governs every *news* row; the mechanical feed is a
SEPARATE row type (`[dictionary update]` badge, different fields, no
status/author) with its own validator, feed file
(`homepage_dict_updates.json`), builder (`scripts/build_dict_updates.py`)
and drift check. News always renders above dictionary rows; each feed fails
soft independently (broken dict feed ⇒ news only; broken news feed ⇒ no
widget, the H8170 contract pinned by fixtures).

Why not the alternatives: *replacing* the editorial widget was rejected in
the interview (two widgets on one page definitively not wanted — but so was
discarding H8170's contract); *extending eligibility to commits* inside the
news contract would have hollowed out the "never inferred" guarantee that
keeps drafts/unannounced work off the homepage; *client-side GitHub API
fetch* was rejected as a runtime dependency on a university static page.

Consequences: the section's content is now a pure function of two committed
JSON feeds; CI byte-diffs both against their sources (csl-guides checkout,
shallow csl-orig clone) plus a regen check for the committed xampp page;
changes to either contract require updating both validators and the README
glossary, not just one.
