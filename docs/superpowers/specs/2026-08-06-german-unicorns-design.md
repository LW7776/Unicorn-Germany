# German Unicorns — Design Spec

**Date:** 2026-08-06
**Status:** Approved
**Supersedes:** the light "Register" design in the sibling project `VC Germany Website`. That
project's inclusion rules, source allowlist and citation-integrity concept are carried over
deliberately; its visual direction, page structure and Astro toolchain are not.

## Purpose

A public directory of every current German unicorn, dark and cinematic, where every published
figure carries the date it was true and a link to who reported it.

Success is not coverage — Dealroom and Tracxn have more companies and more money. Success is
that a reader can open any profile, check any number against its source in one click, and find
the site more rigorous than the commercial directories it sits beside. That rigour is also what
makes automated updating safe: a pipeline that cannot publish an unsourced number cannot quietly
corrupt the dataset.

Language: English.

## Scope

A company is included if **all** of the following hold:

- Founded in Germany **or** headquartered in Germany. Recorded explicitly per company, so
  dual-HQ cases (Celonis: Munich + New York) are visible rather than hidden. Being German only
  by investor base does not qualify.
- Currently **independent and private** — not IPO'd, not acquired, not insolvent.
- Reached a publicly reported post-money valuation of **≥ $1B or ≥ €1B, as reported**. The
  currency the source used is stored and displayed unchanged; no FX conversion is applied to a
  company's own figures. Either threshold qualifies, so a company reported at "$1B" is included
  without being silently restated in euros.

Expected size: 30–45 companies. The launch dataset aims for full coverage, researched in
verified batches of roughly eight companies rather than in one pass.

Out of scope: exited unicorns, fallen unicorns, soonicorns, and any company whose €1B valuation
is not traceable to a public announcement.

### Known boundary problem

"Current unicorn" is not an observable fact. Private valuations are stale by construction — a
company that raised at €1.2B in 2022 may be worth far less today. The site does not resolve
this; it **exposes** it. Valuations always render with their as-of date, figures older than 24
months are visually aged, and membership is determined by the last public valuation. The
Method page says so plainly.

## Concept and voice

Working name and wordmark: **GERMAN UNICORNS**.

Landing statement:

> **Europe's industrial heart now runs on software.**
> N German companies are worth more than a billion euros. Every number here is sourced, and
> every date is disclosed.
> `[ Enter the register ↓ ]`

`N` is rendered from the dataset, never hard-coded.

Voice rules: confident, never defensive. No "Germany's answer to Silicon Valley" — Germany is
not answering anyone. Pro-European and pro-ecosystem, but factual. Ecosystem pull-quotes (e.g.
the Draghi report on European scale-up capital, EU Inc) appear in a footer band, each cited
under the same source rules as any other claim.

## The experience

Single page, three screens plus a modal. Deep-linkable throughout.

### Screen 1 — Hero

Full viewport, near-black. A canvas constellation drifts slowly behind the type: **each point of
light is one company**, faintly linked to its nearest neighbours. The field is generated from
the dataset, not decorative filler.

### The transition

On CTA click, the particles fly into formation — each travels to the position of its own grid
cell while the headline blurs and lifts away, and the cells materialise around the landed
points. One continuous motion, roughly 1.2s. Under `prefers-reduced-motion` this degrades to a
plain cross-fade with no particle motion.

### Screen 2 — The register

- **Top bar**, revealed after the hero: wordmark left; navigator right —
  `Companies · Map · Method · About`, plus search. `Companies` and `Map` switch the view in
  place; `Method` and `About` are separate static pages (`method.html`, `about.html`) sharing
  the same stylesheet, alongside `impressum.html`.
- **Stat bar:** *N unicorns · ~€X bn combined · Y new in the last 12 months · median Z years
  founding→€1bn*, and a **"Data as of <month year>"** freshness badge linking to Method.
  The combined figure is the one place mixed currencies must be added together: USD figures are
  converted at a **single fixed rate stored in the dataset and disclosed on the Method page**,
  and the stat is labelled approximate. No per-company figure is ever converted.
- **Controls:** ⌘K search, sector chips, city filter, sort (newest unicorn / highest valuation /
  latest round / A–Z), and a **Grid ⇄ Map** view toggle.
- **Grid cell:** dark glass panel. The logo sits **unaltered and full-colour on a white rounded
  plate**, so black-on-white logos stay legible against a black page without being modified.
  Beneath, in mono: indicative valuation (`~€13 bn`) and date of last funding round
  (`Last round · Mar 2024`). Hover lifts the cell and blooms its glow.
- **Map view:** Germany outline with glowing city clusters sized by company count. Selecting a
  city filters the grid to that city.

There is no timeline view on this screen. The only timeline in the product is the funding
timeline inside the detail window.

### Screen 3 — Detail window

A lightbox over the blurred, dimmed grid. Deep-linkable (`#/celonis`), with a focus trap.
Closes via a **visible ✕ button in the window's top-right corner**, via ESC, and via a click on
the backdrop. ←/→ move between companies.

Fixed content order:

1. Logo · name · HQ city · sector · founded year · **website ↗**
2. Figure row: indicative valuation with as-of date · last round (stage, month + year) ·
   total capital raised · years from founding to €1bn
3. **The problem** / **The technology & business model** — two short prose blocks
4. **Funding timeline** — animated horizontal track, one node per round (month + year, stage,
   amount, lead investor). The round that crossed €1bn carries a distinct marker.
5. Investors — lead investors first
6. Founders — names and roles, text only
7. Sources — every citation with publication and date

**Any field without a public source renders as `—`.** The site never guesses and never fills
gaps with inference. Chasing a number the sources do not support is wasted effort; implying
precision they do not support is the actual error.

### Personal data

Founder names and roles only — publicly announced, low risk. **No photos:** they are personal
data and the images are almost always copyrighted press shots. Company logos are used
nominatively to identify the company they belong to, unaltered.

## Content model

One JSON record per company in `data/companies/<slug>.json`.

| Field | Notes |
|---|---|
| `slug`, `name`, `website`, `logo` | Identity |
| `hq` (city, country), `foundedCountry` | Makes the inclusion test auditable |
| `sector[]` | Drives filter chips |
| `foundedYear` | |
| `thesis.problem`, `thesis.solution` | The two prose blocks in the detail window |
| `valuation` | Amount + currency + `approximate` + as-of date + round + source id |
| `becameUnicorn` | Date of the first round whose post-money crossed €1B + source id |
| `totalRaised` | Amount + currency + `approximate` + source id |
| `rounds[]` | Date, stage, amount, post-money, lead investors, all investors, source id |
| `founders[]` | Name, role, still-at-company. No photos. |
| `investors[]` | Notable backers |
| `sources[]` | id, publication, title, URL, `publishedOn`, verbatim `quote` |

Precision is deliberately loose and disclosed. "Nearly $13 billion" is stored as `13000` with
`approximate: true` and rendered `~$13B`. Dates may be month-precision (`2019-11`) and are
stored and displayed as `YYYY-MM` rather than padded to a day the source never gave.

## The correctness mechanism

**No bare numbers.** Every figure carries an as-of date and a source id; every source carries a
publication, a dated resolvable URL, and the verbatim sentence containing the figure. A claim
that cannot be sourced is not published. This constraint is the product.

`tools/validate.py` runs locally and on every push and pull request, and fails the build when:

1. A figure references a missing source id, or the source's `quote` does not contain the figure.
2. A source is not on the allowlist, or has no genuine publication date.
3. Rounds are out of chronological order.
4. The `becameUnicorn` round does not exist, or its post-money is below the inclusion threshold
   in the currency the source reported ($1B or €1B).
5. A valuation's as-of date predates the company's last recorded round.
6. Required identity fields are missing or malformed (dates not `YYYY` or `YYYY-MM`).

Two conditions are rendered rather than hidden: figures older than 24 months get an **aged**
badge, and a claim conflicting with existing data is marked **disputed** on the profile instead
of silently overwriting it.

### Sources

Allowlisted only, and kept deliberately short:

- **Primary:** company and investor press releases; official registries; regulatory filings.
- **Trade press:** Gründerszene, Sifted, EU-Startups, Tech.eu, TechCrunch.
- **Business press with editorial standards:** Handelsblatt, Reuters, Bloomberg, Financial Times.

**Excluded without exception:** licensed-database profile pages (Crunchbase, Dealroom,
PitchBook, Tracxn) — a ToS and redistribution problem, not a quality one; Wikipedia; and
aggregators or SEO republishers carrying no original reporting. Tracxn is a useful *model* for
what to show. It is not a source.

**Every source must have a genuine publication date.** Continuously-updated pages with no
publication date — real-time profiles, "about us" pages, live rankings — are not citable,
because `publishedOn` would be an access date pretending to be a publication date.

No paid APIs and no licensed data. **The initial dataset is researched against live sources,
never recalled from model memory.** Unicorn status changes, and remembered valuations are not
citable.

## Updating — automatic and manual

`tools/watch.py`, run monthly by GitHub Actions and on demand via `workflow_dispatch` or
locally:

1. Reads the RSS feeds of the allowlisted trade press.
2. Matches articles against tracked company names and trigger words (*raises, Series,
   valuation, unicorn, IPO, insolvency*), and flags **new candidates** — German companies newly
   reported above €1B.
3. Opens or updates a GitHub issue — *"6 candidate updates — Sep 2026"* — listing company,
   headline, publication and link.

Extraction then happens on request: the flagged articles are read, JSON edits are proposed with
their quotes attached, `validate.py` runs, and the change lands as a pull request for approval.
Zero API cost, and the human stays the gate. `docs/UPDATING.md` documents the flow with a
copy-pasteable prompt so it works without this conversation.

Because the pipeline only ever maintains a human-verified dataset, it never creates a profile
from nothing.

## Design

Direction: **Constellation**.

```
--void:   #07080B   page
--panel:  rgba(255,255,255,0.04) over blur
--stroke: rgba(255,255,255,0.10)
--ink:    #ECEEF3   primary text
--muted:  #8A90A0   metadata, labels
--beam:   #4C7DFF   accent, links, particle core
--violet: #A97BFF   gradient partner, the €1bn marker
--amber:  #E0A24B   aged and disputed signals
```

- Display grotesk for headings, tight tracking
- Mono for every figure, label, date and stat
- Body sans for prose only
- Vendored `woff2` files where they can be fetched; a system stack otherwise

**Signature:** the constellation is the dataset. Points of light become grid cells in one
continuous motion, so the transition teaches what the page contains rather than decorating it.

**Discipline:** dark and cinematic, not neon. Glow is a signal (hover, the €1bn marker), never
ambient noise. Logos are never recoloured, cropped or masked.

**Quality floor:** responsive from 375px, visible keyboard focus, `prefers-reduced-motion`
respected throughout, 4.5:1 contrast minimum, SVG icons only, no analytics, no cookies.

## Architecture

**Git is the database.** One data file per company. This gives an append-only fact log, an audit
trail, and a reviewable diff for every automated change — no database to run, nothing to pay for.

Zero-build static site: hand-written `index.html`, CSS, and vanilla JS modules reading JSON. No
Node is required anywhere, locally or in CI. The only build step is `tools/build.py`, a
one-second script that merges the per-company files into a single `data/companies.json` and
recomputes the stats; its output is committed.

Local preview: `python3 -m http.server`.

- Public GitHub repository, Pages served from `main` at the repository root, with `.nojekyll`
- All asset paths relative, so the project-subpath URL works
- Workflows: `validate.yml` (push and pull request) and `watch.yml` (monthly cron plus manual
  dispatch)
- Cost: €0

## Legal

- Impressum and a privacy note (no analytics, no cookies, no third-party requests)
- A visible "report an error" link, so corrections have a path
- Logos used nominatively, unaltered

## Open decisions

- **Custom domain.** The free `*.github.io` subpath is assumed. A `.de` domain costs ~€10/yr and
  changes nothing structurally.
- **Vendored fonts.** If the `woff2` files cannot be fetched in this environment, the site falls
  back to a system grotesk and mono stack. Decided at implementation time, not blocking.
