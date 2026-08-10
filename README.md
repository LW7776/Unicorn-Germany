# German Unicorns

A public register of Germany's currently private companies valued at a billion euros or
more, built so that every figure on it can be checked against a public, dated source rather
than taken on trust.

**Live site:** [lw7776.github.io/Unicorn-Germany](https://lw7776.github.io/Unicorn-Germany/)

This is a static, buildless site: plain HTML, CSS and vanilla JavaScript, served directly by
GitHub Pages with no framework, bundler or server. `data/companies.json` is the one generated
file, and it is committed like any other — nothing is built at deploy time.

## How it works

- `data/companies/<slug>.json` — one record per company, hand- or form-edited, where every
  figure carries a dated source and the verbatim sentence that states it.
- [`admin.html`](admin.html) — a local form editor (`assets/js/admin.js`) for one company at a time. It
  mirrors `tools/validate.py`'s rules in the browser so mistakes show up while typing, then
  downloads or copies the JSON to commit — it never writes to the repository itself.
- `tools/build.py` merges those files into `data/companies.json`, and the weekly funding
  files into `data/funding.json`, computing every derived label, sort key and staleness flag
  so the browser code stays thin.
- `tools/validate.py` refuses to publish a figure that isn't backed by a quoted, dated,
  allowlisted source. This is the sole gate that can block a publish — `admin.js`'s mirror of
  the same rules is a convenience, not an authority.
- `data/funding/<year>-W<week>.json` is the weekly funding round-up: German rounds generally,
  not only unicorns. `tools/validate_funding.py` gates it on a deliberately lighter standard —
  every round linked, dated and allowlisted, but **not** quote-checked. The two standards live
  in separate files behind separate validators so neither can quietly become the other.
- `tools/weekly_funding.py` gathers one week of German funding candidates from the feeds:
  which articles fall inside the week, which headlines read as a closed round, and which of
  them name a company the register already tracks. It is a library and a scan, not a drafter —
  it writes no week file and calls no model.
- `tools/watch.py` scans the same short allowlist of trade-press feeds for anything that would
  change the register — it never edits the dataset itself.
- `.github/workflows/rebuild.yml` regenerates `data/companies.json` after a push that edits
  `data/companies/**` directly on `main` (the GitHub-web-editor and files-and-terminal
  routes). It validates first and only then rebuilds, so a bad hand edit is never published —
  the site keeps serving the last good data and the workflow explains the failure on the
  commit.

See [`docs/UPDATING.md`](docs/UPDATING.md) for the inclusion rules and exactly how to add,
correct or remove a company.

## Local development

Requires Python 3.11+. The site itself has no dependencies; `pytest` is the only thing needed
to run the test suite.

```bash
python3 tools/build.py        # regenerate data/companies.json from data/companies/*.json
python3 -m http.server 8080   # serve the site at http://localhost:8080
python3 -m pytest             # run the test suite
```

Also useful while editing data:

```bash
python3 tools/validate.py        # check every company file against the schema and sourcing rules
python3 tools/check_contrast.py  # confirm the colour palette clears the WCAG AA 4.5:1 floor
python3 tools/validate_funding.py  # check the weekly funding files
python3 tools/watch.py           # run the register candidate scan locally
python3 tools/weekly_funding.py --last-complete-week   # last week's funding candidates
```

## Continuous integration

Every push and pull request runs the test suite, the contrast check and both validators
(`.github/workflows/validate.yml`). Pull requests additionally fail if `data/companies.json`
or `data/funding.json` is stale — that is, if it doesn't match what `tools/build.py` produces
from the current source files — so a regenerated file can never be forgotten in review.

One scheduled workflow reads the feeds. `.github/workflows/monday-reminder.yml` runs at 20:00
Berlin time every Monday, scans the allowlisted feeds for the week that just ended, and opens a
single GitHub **issue** listing what it found — every eighth week with the full register sweep
added as a second section of that same issue. A week with nothing to report opens nothing, so
the mail that does arrive is always worth reading. GitHub emails the issue to anyone watching
the repository, which is the whole notification path.

**No workflow writes site content.** An earlier `weekly-funding.yml` drafted the round-up and
opened a pull request; writing a week well is a model call, this repository holds no API key,
and so that job could only ever publish a bare list of parsed headlines. Rather than let the
site get slightly worse every Monday, the drafting job was deleted and CI now only says there
is work to do. The week is written locally by a person with an assistant and pushed. See
[`docs/UPDATING.md`](docs/UPDATING.md) for the route from an open issue to a validated commit.

A third workflow (`.github/workflows/rebuild.yml`) handles edits made straight to `main`
outside a pull request — the GitHub web editor and files-and-terminal routes in
`docs/UPDATING.md`. It runs the validator *before* `tools/build.py`, so a manual edit that
fails validation never reaches the build step: `data/companies.json` is left untouched, the
live site keeps serving the last good data, and the workflow explains the failure as a
comment on the commit.

Deployment is GitHub Pages, configured to serve directly from `main` at the repository root —
no build step, no deploy workflow; the repository *is* the site. `.nojekyll` disables Pages'
default Jekyll processing, which would otherwise ignore files and folders starting with `_`.

## Licence

Different parts of this repository carry different licences:

- **Code** — the site's HTML, CSS and JavaScript, and the Python tools in `tools/` — is
  licensed [MIT](https://opensource.org/licenses/MIT).
- **The dataset** — the company records in `data/companies/*.json` and the generated
  `data/companies.json` — is licensed
  [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/): reuse it, with attribution.
- **Fonts** (`assets/fonts/*.woff2` — Archivo, Source Serif 4 and IBM Plex Mono) are each
  licensed [SIL Open Font License 1.1](https://openfontlicense.org/), not MIT. See
  `assets/fonts/README.md` for the exact source and date of each file.
- **Map geometry** (`data/geo/germany.json`) is derived from Natural Earth via the
  `datasets/geo-countries` project and is public domain. See `data/geo/README.md` for
  full provenance.
- **Company logos** (`assets/logos/`) remain the property of their respective owners. They
  are used nominatively, solely to identify the companies they belong to, and are not
  covered by any licence granted above.

## Corrections

If something here is wrong, out of date, or missing a source, open an issue or use the
"Report an error" link in the footer of any page. See [`docs/UPDATING.md`](docs/UPDATING.md)
for the three ways to fix it directly.
