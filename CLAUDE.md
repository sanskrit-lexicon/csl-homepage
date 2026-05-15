# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**csl-homepage** generates the [Sanskrit Lexicon homepage](http://www.sanskrit-lexicon.uni-koeln.de/index.html) for both the Cologne server and local XAMPP installations. It reads dictionary metadata and version information from sibling repos and produces the `index.html`.

At Cologne, this repo lives at `/scans/csl-homepage/`.

## Architecture

| File/Directory | Purpose |
|---|---|
| `index_cologne.py` | Generates `index_cologne.html` for the Cologne server |
| `index_xampp.py` / `index_xampp.html` | Generates homepage for local XAMPP installation |
| `redo_cologne.sh` | Runs `index_cologne.py` and copies output to the Cologne web root |
| `redo_xampp.sh` | Runs `index_xampp.py` and copies output to local XAMPP web root |
| `update_version.sh` | Updates `../csl-orig/.version` file; **run this before** either redo script |
| `indexdirs/` | Directory listing data used by the homepage generator |
| `indexdirs.xml` | XML index of all dictionary directories |
| `Cologne.css` | Main stylesheet for the homepage |
| `ap_pd_samples/` | Sample pages for AP and PD dictionaries |
| `hack/` | Miscellaneous one-off fix scripts |

### Workflow

```bash
sh update_version.sh        # always run first
sh redo_cologne.sh          # for Cologne server deployment
sh redo_xampp.sh            # for local XAMPP testing
```

Local URL: `http://localhost/cologne/index.html`

## Dependencies

- **Python 3**
- **csl-orig** sibling repo — `.version` file updated by `update_version.sh`
