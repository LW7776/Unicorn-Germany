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
3. **Publicly reported to be worth at least $1B or €1B.** Either threshold qualifies, in the
   currency the source used, and a company's own figures are never converted between
   currencies. The register also publishes valuations struck by a secondary sale of existing
   shares rather than a primary round (Trade Republic, n8n, Raisin) — a secondary prices the
   company too, just not by new capital entering it, and every such case is labelled as a
   secondary rather than left to read as a post-money it isn't.

**Membership is the test; the figure is a nice-to-have.** Rule 3 used to demand a *quotable
numeral* — a post-money a source had printed in digits — and that excluded companies nobody
disputes are unicorns, on a technicality about how a sentence happened to be written. Quantum
Systems was the clearest case: Sifted, Tech.eu, its own lead investor and Handelsblatt all
reported it had passed a billion, and not one of them printed the number, so it fell out of a
register of German unicorns.

So a valuation may now be recorded as **undisclosed**:

```jsonc
"valuation": {
  "amount": null,                       // no figure, because no source printed one
  "currency": null,
  "asOf": "2025-09",                    // when the *evidence* was reported
  "source": "s4",
  "undisclosed": {
    "note": "What is and isn't known, and why there is no number.",
    "source": "s4"                      // a quote establishing unicorn status in words
  }
}
```

The sourcing discipline is unchanged and non-negotiable. `undisclosed.source` must resolve to
an allowlisted, dated source with a real quote from a page someone actually opened, exactly
like every other cited claim — the validator checks all of that. What it cannot check is that
the quote *means* what the note says, because there is no figure to match: the sentence has to
establish unicorn status qualitatively ("became a unicorn in June", "mit mehr als einer
Milliarde Dollar bewertet", "knackte die Milliarden-Bewertung"), and only a person reading it
can confirm that. **Never fill the gap with a number no source printed.** Dividing a later
"tripled its valuation" by three is arithmetic, not a source.

Two consequences worth knowing before you use it:

- **`amount` and `undisclosed` are mutually exclusive, and a record must carry one.** If a
  source prints a figure, publish the figure. `undisclosed` is for when none does — not a way
  to avoid checking a quote.
- **`becameUnicorn` still names a round**, and that round's `postMoney` may be `null` if it
  carries its own `undisclosed` note. The rule that an *earlier* round with a post-money above
  the threshold means the company crossed there still applies, unchanged — a qualitative
  crossing is not a way around it.

On the site, an undisclosed valuation renders as **Undisclosed** with an amber `>1bn` marker
beside it, never as "—" and never as a zero, and such companies are left out of the "combined
value" headline rather than counted as nothing — the headline says how many of the register it
covers.

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
