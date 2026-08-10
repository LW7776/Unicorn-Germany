# Updating the register

Nothing here edits the dataset automatically. The scheduled scans only *propose* — one opens an
issue, the other opens a pull request, and both wait for a person unless the repository has been
told otherwise (see [Letting the pull request merge itself](#letting-the-pull-request-merge-itself)).
There are three ways to change the content, and all three end in the same place: a validated
commit.

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

## The two automations

Two jobs read the same allowlisted feeds, on different clocks, looking for different things.
Neither publishes anything by itself.

| | `weekly-funding` | `watch` |
|---|---|---|
| Runs | Every Monday 07:00 UTC. Also on demand, by API, and by webhook | Every 8 weeks, Monday 06:00 UTC |
| Looks for | German funding rounds — any company, not only unicorns | Anything that changes the register |
| Produces | A pull request with one week of the round-up | An issue listing candidate changes |
| Touches the dataset | No — a pull request you review | No — an issue you read |

**Why the sweep dropped from monthly to eight-weekly.** The weekly scan is now what catches a
new unicorn: a company that crosses a billion does it *by raising*, and that round is announced,
so it appears in the funding feeds within days. Waiting up to a month for the sweep to notice
was the slow path to the same fact.

What the eight-weekly sweep is for is everything a funding announcement never announces. A
company that IPOs stops qualifying, and there is no round to report. So does one that is
acquired, and one that becomes insolvent. And a valuation nobody has repriced for two years goes
stale without any event at all — no announcement is ever made about a number quietly ageing.
None of that arrives on a funding wire, and none of it is urgent to the day, which is exactly
why it suits a slower, more thorough pass.

Both can be triggered by hand from **Actions → (the workflow) → Run workflow**. A manual `watch`
run always sweeps, regardless of which week it is.

## The weekly round-up, in two modes

`weekly-funding` runs on a schedule and needs no attention. What it produces depends on one
thing: whether the repository holds an `ANTHROPIC_API_KEY`.

| | Full mode | List-only mode |
|---|---|---|
| Chosen when | The secret exists | The secret is absent, **or** the run was started with **List only** ticked |
| Model call | Yes, one | **None at all** |
| Lead rounds | 1-2, written up in the site's voice | `lead` is empty |
| Supporting list | Up to 5 rounds | Up to 5 rounds |
| Per round | Company, HQ, stage, amount, currency, founders, investors, source, date | Company, amount, currency, source, date, plus HQ and stage where the headline gives them. Founders and investors are always empty |

**The repository currently holds no key, so the schedule runs in list-only mode.** That is a
deliberate design, not a degraded one: the routine was rebuilt so a missing secret changes what a
week *says*, never whether a week *happens*. The site keeps moving, and it never claims a
write-up it did not produce.

**What list-only mode may and may not do.** Every field it publishes is lifted out of the
headline of the page it cites. It reads a company name, an amount and a currency out of that
headline, and if it cannot read all three cleanly it drops the article rather than half-parsing
it. It never infers a founder, an investor or a valuation, and it never carries anything over
from what a model happens to know. The consequence is that it misses real rounds whose headline
is phrased awkwardly, and that is the correct trade: a round the site missed is a gap, and a
wrong company name beside a real link is a falsehood. The page says which kind of week it is
showing in place of the write-up, so nobody is left assuming the prose went missing.

### Adding the key, if you want written weeks

1. Go to <https://console.anthropic.com/settings/keys> and **Create Key**. Copy it — the console
   shows it once.
2. In this repository, open **Settings → Secrets and variables → Actions**.
3. Click **New repository secret**.
4. Name it exactly `ANTHROPIC_API_KEY` — the workflow looks for that name and nothing else.
   Paste the key as the value, and **Add secret**.
5. Check it works: **Actions → weekly-funding → Run workflow**. Leave the week blank to draft
   the week that just ended.

The key is never printed, never committed, and is only readable by Actions. If it leaks, revoke
it in the console and add a new one — no code change is needed. Removing it later breaks nothing:
the next Monday simply produces a listed week instead of a written one.

### What the job actually does

1. Fetches the allowlisted feeds (the same `tools/watch.py` code the sweep uses), walking a few
   pages back so a Monday run still sees the previous Tuesday.
2. Keeps articles published inside the week that mention Germany and a funding event.
3. **Full mode:** asks Claude to pick the lead round(s), write them up, and list the rest —
   **from those articles only** — then checks the answer back against the fetched text. Every
   company, founder, amount and valuation must appear in the article cited beside it, and the
   citation must be a page this run actually fetched. Anything that fails is rejected and
   nothing is written.
   **List-only mode:** reads each headline mechanically into a round, drops the ones it cannot
   read, deduplicates by company, and keeps the largest five.
4. Validates the file with `tools/validate_funding.py`, which accepts both shapes of week and
   holds both to the same sourcing rule.
5. Opens a pull request. It never commits to `main`. If validation fails, nothing is proposed
   and the run fails loudly.

If a company already in `data/companies/` appears in the week, the pull request says so at the
top and its title is marked *(touches the register)* — that company's register entry now carries
an out-of-date figure, and the round-up must not be the only place the new one appears. A listed
week is marked *(listed, not written up)* in the title too, so the difference is visible before
the diff is opened.

A week with no qualifying German rounds is a real outcome: the job says so in the run log and
opens nothing. An empty pull request is never created, because a page announcing an empty week
is worse than no update at all.

### Starting a run yourself: three ways

**By hand.** **Actions → weekly-funding → Run workflow.** Two optional inputs: a `week`
("2026-W30", blank means the week that just ended) and **List only**, which forces the listed
shape even when the key exists. Useful for seeing what a listed week looks like before you have
to rely on one.

**By API.** The same manual trigger, over HTTP. `ref` is required and names the branch the
workflow file is read from.

```bash
curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/LW7776/Unicorn-Germany/actions/workflows/weekly-funding.yml/dispatches \
  -d '{"ref":"main","inputs":{"week":"2026-W30","list_only":"true"}}'
```

**By webhook.** `repository_dispatch` is the trigger an external system fires: a cron box, an
automation step, a script on someone else's machine. The event type must be exactly
`draft-funding-week`, and the optional week travels in `client_payload`, because
`repository_dispatch` has no `inputs`.

```bash
curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/LW7776/Unicorn-Germany/dispatches \
  -d '{"event_type":"draft-funding-week","client_payload":{"week":"2026-W30"}}'
```

Omit `client_payload` entirely, or send `{}`, to draft the week that just ended.

**Which token.** Both endpoints need a token with write access to Actions on this repository:

- A **fine-grained personal access token** scoped to this repository with **Actions: Read and
  write**. The `repository_dispatch` endpoint additionally needs **Contents: Read and write**.
- Or a **classic** personal access token with the `repo` scope.

The repository's own `GITHUB_TOKEN` cannot start either of these. A workflow triggered by that
token does not trigger further workflows, which is GitHub's loop guard and is working as
intended.

**Never put a real token in this file, in a workflow, or in a commit.** Export it in the shell
that runs the `curl`, or keep it in whatever secret store the calling system already has. A token
pasted into a repository is a token that has to be revoked.

Neither route publishes anything. Both end where the schedule ends, at an open pull request.

### Letting the pull request merge itself

By default the pull request waits for a person. That is the reviewed path, and it is what the
site's own About page promises when it says someone checks the links.

To hand that step over, set a repository **variable** (not a secret): **Settings → Secrets and
variables → Actions → Variables → New repository variable**, named `FUNDING_AUTO_MERGE`, with the
value `true`. The workflow then enables auto-merge on the pull request it opens, and the week
lands by itself as soon as `validate.yml` passes.

| `FUNDING_AUTO_MERGE` | What happens to the pull request |
|---|---|
| unset, or anything other than `true` (the default) | It stays open until a person merges it |
| `true` | It merges itself once `validate.yml` is green |

Two things are worth knowing before turning it on. **Auto-merge must also be enabled for the
repository** (Settings → General → Allow auto-merge), and if it is not, the run logs a warning
and the pull request simply stays open, which is the safe failure. And **validation is not
review**: CI checks that a week is well-formed, sourced, linked and dated, which is precisely
what cannot tell you that a headline was read correctly. With auto-merge on, a listed week
reaches the public site without anyone having opened a source link.

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
rule, no prose. That is the shape the weekly routine produces without an API key, and the page
says so where a write-up would be. What is rejected is a week with *neither* a lead nor a list,
because an empty week is a page announcing nothing. Writing one up by hand later is just an edit
to the same file.

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

The weekly job never writes a `note`: it cites one article per round, so it cannot see a
disagreement. Spotting one is a review job, which is why the pull request asks you to open every
source link.

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
3. `python3 -m pytest && python3 tools/validate.py && python3 tools/validate_funding.py`
4. Commit both the company file and the regenerated `data/companies.json`.

On a pull request, CI fails if `data/companies.json` or `data/funding.json` does not match its
source files, so step 2 is not optional there. On a direct push to `main`, `rebuild.yml`
regenerates both for you.

## Removing a company

A company that IPOs, is acquired, or becomes insolvent no longer qualifies. Delete its file,
rebuild, and note the reason in the commit message — git keeps the record.
