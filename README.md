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
