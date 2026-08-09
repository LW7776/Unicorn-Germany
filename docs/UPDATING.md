# Updating the register

Nothing here edits the dataset automatically. The monthly scan only *proposes*. There are
three ways to change the content, and all three end in the same place: a validated commit.

| Route | Needs | Use it when |
|---|---|---|
| **A. GitHub web editor** | A browser | Fixing a figure, a date, a typo — the fastest path |
| **B. `admin.html` form** | A browser | Adding a whole company, or editing many fields at once |
| **C. Files and terminal** | Python | Bulk edits, or when you are already in the repository |

## Inclusion rules

A company qualifies only if all three hold:

1. **Founded in Germany, or headquartered in Germany.** Record this explicitly — dual-HQ cases
   (Celonis is headquartered in both Munich and New York) use the optional `alsoBasedIn` field
   rather than being hidden. Being German only by investor base does not qualify.
2. **Currently independent and private.** Not IPO'd, not acquired, not insolvent.
3. **A publicly reported post-money valuation of at least $1B or €1B**, in the currency the
   source used. Either threshold qualifies, and a company's own figures are never converted
   between currencies. The register also publishes valuations struck by a secondary sale of
   existing shares rather than a primary round (Trade Republic, n8n) — a secondary prices the
   company too, just not by new capital entering it, and every such case is labelled as a
   secondary rather than left to read as a post-money it isn't.

## Monthly, automatic

On the 1st of each month the `watch` workflow reads the allowlisted feeds and opens an issue
listing candidate changes. Trigger it early from **Actions → watch → Run workflow**.

## Route A — edit in the browser

Open any company on the live site and click **Edit this entry** at the bottom of its detail
window. That opens `data/companies/<slug>.json` in GitHub's editor. Change what you need and
commit.

On commit, `rebuild.yml` validates the file. If it passes, it regenerates `data/companies.json`
and the live site updates within a minute or two. **If it fails, nothing is published** — the
site keeps serving the last good data and the workflow posts the errors as a comment on your
commit. A bad manual edit can never break the live site, because validation always runs
*before* the rebuild that would publish it.

The same rules still apply: every figure needs a source in `sources[]` whose `quote` contains
that figure. The validator will tell you exactly which figure is unsourced.

## Route B — the form editor

Open `admin.html` (locally, or on the live site) and either pick an existing company to load
or start a blank record. The form knows the schema: required fields, allowed publications, date
formats, and the quote-contains-the-figure rule, all checked as you type.

When it is valid, download the file or copy the JSON. Then either drop it into
`data/companies/` and commit, or paste it into GitHub's editor via Route A.

The form never writes to the repository by itself — that is deliberate. Every change stays a
reviewable commit with your name on it.

## Acting on candidates

Paste this into Claude Code:

> Process the open candidates issue in this repository. For each candidate: open the linked
> article, and only if the publication is on the allowlist in `tools/schema.py`, extract the
> figures with the verbatim sentence containing each one. Update the matching file in
> `data/companies/`, or create a new one if the company qualifies under the inclusion rules
> above. Amounts are millions of the stated currency; dates are
> `YYYY` or `YYYY-MM`. Then run `python3 tools/build.py && python3 -m pytest && python3
> tools/validate.py` and open a pull request. If a figure has no quotable source sentence,
> leave the field out and say so in the pull request — never fill a gap by inference.

## Route C — files and terminal

1. Edit or add `data/companies/<slug>.json`.
2. `python3 tools/build.py`
3. `python3 -m pytest && python3 tools/validate.py`
4. Commit both the company file and the regenerated `data/companies.json`.

On a pull request, CI fails if `data/companies.json` does not match the source files, so step 2
is not optional there. On a direct push to `main`, `rebuild.yml` regenerates it for you.

## Removing a company

A company that IPOs, is acquired, or becomes insolvent no longer qualifies. Delete its file,
rebuild, and note the reason in the commit message — git keeps the record.
