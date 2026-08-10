# Updating the register

Nothing here edits the dataset automatically, and nothing in CI writes a word of the site. One
scheduled job reads the feeds and, when there is something to report, opens **one issue** saying
so. Everything after that is a person and their assistant, working locally against a validated
commit. There are three ways to change the content, and all three end in the same place.

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

## The Monday reminder

One scheduled workflow, `.github/workflows/monday-reminder.yml`. It runs at **20:00 Berlin time
every Monday**, covers the week that just ended, and **publishes nothing**: no commit, no pull
request, no file. It reads the allowlisted feeds and, if there is anything worth reporting, opens
**one issue**.

| | Every Monday | Every eighth Monday |
|---|---|---|
| Scans | The feeds, for the week that just ended | The same, plus the full register sweep |
| Looks for | German funding rounds — any company, not only unicorns | Anything that changes the register |
| Produces | A checklist in an issue | A second section in that *same* issue |
| Touches the dataset | No | No |

**Why CI no longer drafts the round-up.** It used to: a job compiled the week and opened a pull
request. Writing a week well is a model call, this repository holds no `ANTHROPIC_API_KEY`, and
so the scheduled job could only ever publish a bare list of rounds parsed out of headlines —
visibly thinner than the weeks already on the site. A register that gets a little worse every
Monday is worse than one a person updates, so the drafting job was deleted. The reminder took its
place: CI now says there is work to do, and the work is done by a person with an assistant and
pushed. Every published week stays at the quality of the ones before it.

**A week with nothing to report opens no issue.** That is deliberate. A weekly mail that usually
says "nothing happened" gets filtered, and then the one that matters is filtered with it. If
every feed fails, the issue *is* opened and says so at the top, because a blind scan must never
be mistaken for a quiet week.

**Why the sweep runs every eight weeks and not monthly.** The weekly scan is what catches a new
unicorn: a company that crosses a billion does it *by raising*, and that round is announced, so
it appears in the funding feeds within days. What the sweep is for is everything a funding
announcement never announces. A company that IPOs stops qualifying, and there is no round to
report. So does one that is acquired, and one that becomes insolvent. And a valuation nobody has
repriced for two years goes stale without any event at all. None of that arrives on a funding
wire, and none of it is urgent to the day, which is why it suits a slower pass.

### The issue arrives as an email, and you have to be watching

GitHub emails a new issue to everyone **watching** the repository. That is the whole notification
path: no mail server, no address stored anywhere, nothing to configure in this repository.

**Confirm it once.** On the repository page, open the **Watch** menu and choose **All Activity**,
or **Custom** with **Issues** ticked. On "Participating and @mentions" no mail arrives at all, and
the Monday reminder silently becomes something you have to remember to go and look for, which is
exactly what it exists to avoid. Being the repository owner is not enough by itself, and the
setting can be changed by accident.

### Starting a run yourself

**Actions → monday-reminder → Run workflow.** Two optional inputs: `week` ("2026-W30", blank
means the week that just ended) and **register sweep**, which includes the sweep section even in a
week that is not an eighth. Manual runs are never gated on the Berlin clock, so one runs now.

The same trigger over HTTP. `ref` is required and names the branch the workflow file is read from:

```bash
curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/LW7776/Unicorn-Germany/actions/workflows/monday-reminder.yml/dispatches \
  -d '{"ref":"main","inputs":{"week":"2026-W30"}}'
```

That needs a token with write access to Actions on this repository: a **fine-grained personal
access token** scoped to it with **Actions: Read and write**, or a **classic** token with the
`repo` scope. The repository's own `GITHUB_TOKEN` cannot start it, which is GitHub's loop guard
working as intended. **Never put a real token in this file, in a workflow, or in a commit.**

### Running the scan on your own machine

The workflow runs exactly this, and so can you. Neither command writes into `data/`:

```bash
python3 tools/weekly_funding.py --last-complete-week      # the week's funding candidates
python3 tools/weekly_funding.py --week 2026-W30 --report /tmp/week.json
python3 tools/watch.py --out /tmp/sweep.json              # the register sweep
```

`tools/weekly_funding.py` is a library now, not a drafter. It fetches the allowlisted feeds (the
same `tools/watch.py` code the sweep uses, walking a few pages back so a Monday run still sees the
previous Tuesday), keeps the articles published inside the week that mention Germany and a funding
event, and splits them in two: the headlines it can read as a closed round, and everything else it
collected. It carries each article's body text through, so whoever writes the week works from the
reporting rather than from a headline. It decides nothing and writes no week file.

### If an API key were ever added

Nothing in the repository looks for one today, and adding a secret alone would change nothing —
the drafting code is gone. What a key would buy is the option to bring back an automated first
draft, at the cost this project already weighed once: a scheduled draft is only as good as the
model call behind it, and it publishes on a timer rather than when someone has read the sources.
If you ever want it, the shape to rebuild is a job that calls the model on the articles
`tools/weekly_funding.py` already collects, checks every company, founder and figure back against
the text of the article cited for it, and opens a **pull request** rather than committing. The
history of `tools/weekly_funding.py` and `.github/workflows/weekly-funding.yml` has a working
version of all of that. The reason it is not running is quality, not difficulty.

## Writing the week from the issue

The Monday issue is a checklist. Paste this into Claude Code, with the issue open:

> Write the funding round-up for the ISO week in the open Monday issue in this repository. For
> each candidate: open the linked article, confirm the company is German and the round closed and
> announced, and take the amount, currency, stage, founders and investors off the page rather than
> off the headline. Write one or two lead rounds up in the site's voice per `docs/BRAND.md` and
> list the rest without prose, following the file shape below. Never state a figure, a founder or
> a valuation the article does not. Where a candidate is marked as already in the register, update
> `data/companies/<slug>.json` in the same change so the two never disagree. Then run
> `python3 tools/build.py && python3 tools/validate.py && python3 tools/validate_funding.py &&
> python3 -m pytest` and push.

Close the issue when the week is pushed. Nothing closes it for you, and an issue left open is the
only record that a week was skipped.

## The funding round-up, by hand

One file per ISO week, `data/funding/<year>-W<week>.json`:

```jsonc
{
  "week": "2026-W30",
  "start": "2026-07-20",             // must be that week's Monday
  "end": "2026-07-26",               //  ... and its Sunday
  "lead": [ /* 0-2 rounds, each with a `text` write-up */ ],
  "more": [ /* up to 5 rounds, listed only, no `text` */ ]
}
```

`lead` may be **empty**, which publishes the week as a plain list: same rounds, same sourcing
rule, no prose, and the page says so where a write-up would be. The validator allows it, and a
week you are short of time for is better listed than missed — but nothing produces that shape
automatically any more, and no week on the site currently uses it. What is rejected is a week
with *neither* a lead nor a list, because an empty week is a page announcing nothing. Writing a
listed week up properly later is just an edit to the same file.

Every round in either list:

```jsonc
{
  "id": "l1",
  "company": "telli",
  "hq": "Berlin",                    // or null when no source says
  "stage": "Seed",                   // or null
  "amount": 13.1,                    // millions of `currency`
  "currency": "EUR",                 // EUR or USD
  "approximate": false,              // true for "over €10 million"
  "valuation": null,                 // millions, or null when none was reported
  "valuationCurrency": null,         // required whenever `valuation` is set
  "founders": ["..."],               // [] when the source names none — never guessed
  "investors": ["..."],
  "text": "One paragraph.",          // lead rounds only
  "source": {
    "publication": "EU-Startups",    // same allowlist as the register
    "title": "...",
    "url": "https://...",
    "publishedOn": "2026-07-23"
  },
  "note": {                          // optional: a conflicting figure, recorded
    "text": "€35m is the company's own figure; the trade press reports €30m.",
    "source": { /* same four fields, for the *other* figure */ }
  }
}
```

### When sources disagree about a round

They do, often: a company announces €35m and the trade press reports €30m. Resolve it the way
the register already does — **publish the company's own figure for its own round, cite the
company's own announcement, and record the disagreement in `note` with its own link.** Do not
silently pick one. The `note` carries a full source of its own, held to the same allowlist and
date rules, so the figure you did *not* publish is exactly as traceable as the one you did.

Moss's W32 Series C is the worked example: `data/funding/2026-W32.json` publishes €35m sourced
to Moss's own release, with Sifted's €30m in the note — and `data/companies/moss.json` publishes
the same €35m with the same disagreement in its `disputed` field. **If a round appears in both
datasets, they must not state different figures.** A test asserts exactly that for Moss.

The Monday scan cannot see a disagreement: it reads one headline per link and never compares two.
Spotting one is a reading job, which is why the issue asks you to open every source link before
writing anything.

**The sourcing standard is lighter than the register's, and the site says so.** Every round needs
a real link, a real publication date, an allowlisted publication, and figures a source states.
There is **no quote gate** — you do not record a verbatim sentence per figure, and
`tools/validate_funding.py` does not ask for one. What has not changed: you may never invent a
figure, a founder or a round. If a source does not name the founders, leave the list empty; the
page drops the clause and the sentence closes up around it.

The two standards must never be confused by a reader, which is why the block states its own in a
line under its heading, and why the round-up lives in its own files behind its own validator.

Then:

```
python3 tools/build.py            # regenerates data/funding.json (and companies.json)
python3 tools/validate_funding.py
python3 -m pytest
```

Commit the week file *and* the regenerated `data/funding.json`. CI fails on a pull request if
the generated file does not match its sources.

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

## Acting on register candidates

The register section of the eight-weekly issue. Paste this into Claude Code:

> Process the register sweep candidates in the open Monday issue in this repository. For each
> candidate: open the linked
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
3. `python3 -m pytest && python3 tools/validate.py && python3 tools/validate_funding.py`
4. Commit both the company file and the regenerated `data/companies.json`.

On a pull request, CI fails if `data/companies.json` or `data/funding.json` does not match its
source files, so step 2 is not optional there. On a direct push to `main`, `rebuild.yml`
regenerates both for you.

## Removing a company

A company that IPOs, is acquired, or becomes insolvent no longer qualifies. Delete its file,
rebuild, and note the reason in the commit message — git keeps the record.
