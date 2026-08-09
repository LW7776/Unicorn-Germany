# Candidates

**What this file is.** Every company considered for the register, each with a status —
**include**, **exclude**, or **cannot be established** (defined below) — and the reason for
it. It is not a shortlist or a backlog, and it is the only place a reader can check what was
looked at and why a name is, or isn't, on the register.

**It is not guaranteed to be complete.** A company can simply not have been looked at yet —
the sweeps recorded near the end of this file are an attempt to close that gap, not proof it
is fully closed — and this file's own write-up can in principle lag the register it
describes, if a record is ever added faster than its reasoning is written down. Where the two
would ever disagree, `data/companies/` is the current truth and this file is the reasoning
trail behind everything else in it.

**Exclusions are as deliberate as inclusions.** A name dropping off this list is usually a
fact — an IPO, an acquisition, an insolvency, a markdown, a headquarters that moved — and
that fact is worth publishing. Several of the entries below were more work than the records
that made it in.

**"Cannot be established" is a statement about evidence, not about the company.** It means
the register's [sourcing rules](UPDATING.md) could not confirm that the company is over the
threshold: nobody on the allowlist says so, or what they printed measures something else, or
the page that has it cannot be opened. Some of the largest and best-known companies in German
technology are in that section. It is not a judgement that they are small, doubtful or
unimportant, and it is not a claim that they are *not* unicorns — only that this register will
not publish a claim it could not read. It used to say "will not print a number it could not
read", and that was too narrow a test: a register can honestly publish a company without
publishing a number, and since August 2026 it does.

A company qualifies only if all three of the [inclusion rules](UPDATING.md#inclusion-rules)
hold: German by founding **or** headquarters, currently independent and private, and
publicly reported to be worth at least $1B or €1B as reported. A company that
cannot be shown to satisfy all three does not go in the register — "cannot be established" is
a reason to leave a name out, the same as "exclude", not a softer form of inclusion.

**Rule 3 changed in August 2026, and this whole file was re-read against the new version.** It
used to demand a quotable *numeral* — a post-money printed in digits somewhere on the
allowlist. It now asks whether the company is publicly reported to be over the threshold at
all, and a valuation nobody has ever put a number to can be recorded as
[undisclosed](UPDATING.md#inclusion-rules) rather than disqualifying the company. Nothing
about the sourcing discipline moved: every claim still needs an allowlisted, dated source and
a verbatim quote from a page that was opened, and no figure may ever be inferred to fill a
gap. What changed is that "an allowlisted source states this company is a unicorn, and none
prints the figure" became something the dataset can *say*, instead of a technicality that
deleted a company from a register of German unicorns. **Five entries moved out of "cannot be
established" on that basis** and are written up as batch 5 below. Every remaining row in that
section was re-checked against the new rule too, did not move, and now records why not — the
change is narrow, and it is not a licence to relax the other two rules or to read a headline
as a finding.

**Status meanings**

| Status | Means |
|---|---|
| **include** | All three rules verified against a source that was opened and read. |
| **exclude** | One rule verifiably fails. The reason is recorded with its source. |
| **cannot be established** | No rule is shown to fail, but the evidence the rules demand does not exist or cannot be reached. Each entry names the one thing that would settle it. |

There is no fourth status. The word *undecided* used to appear in this vocabulary and no
longer does — it described a queue kept open pending more research. Every row below now
carries one of the three statuses above rather than a placeholder, which is a statement about
the rows that exist, not a claim that every company that might ever qualify has a row (see
"not guaranteed to be complete", above) or that a settled status can never be revisited as new
rounds and reports appear.

Last reviewed: **2026-08-09**.

**Blocked publishers.** Several allowlisted publications return 403 to an automated
fetch. That is not the same as unobtainable, and this file once treated it as if it
were: three entries were parked on "Bloomberg 403s". **A publisher that blocks direct
fetching must be tried through a [Wayback Machine](https://web.archive.org) snapshot
before its reporting is recorded as unreadable.** Where a snapshot is used, the record
still cites the publisher's own canonical URL — the archive is how the page was read, not
a second source, and a snapshot that captured the publisher's own block page (HTTP 403)
is not a read at all. Batch 4 extended the practice from publishers to *companies*:
quantum-systems.com 403s this crawler on every page, and its own funding release was
recovered from the archive and read. It did not rescue the entry, but it settled it — and
batch 5 found a second route past the same block, since that site's WordPress media endpoint
answers normally even though every HTML page 403s, which is where its logo came from.
Batch 5 also retired a standing assumption: Business Insider's Gründerszene pages, recorded
here twice as unreadable behind "Lade Premium-Inhalte…", now return their full bodies. Three
of this batch's five rest on them.

---

## Include — written (batch 1)

| Company | HQ | Valuation as reported | Evidence |
|---|---|---|---|
| **Helsing** | Munich | $18bn, Jul 2026, Series E | [Company press release](https://helsing.ai/newsroom/helsing-raises-1-8bn-in-series-e) |
| **Trade Republic** | Berlin | €12.5bn, Dec 2025, secondary | [Company press release](https://assets.traderepublic.com/assets/files/251217_Secondary_PressRelease_BL_EN2.pdf) |
| **Celonis** | Munich / New York | ~$13bn, Aug 2022, Series D extension | [Company press release](https://www.celonis.com/news/press/celonis-secures-one-billion-to-help-customers-fight-economic-and-supply-change-challenges) |
| **N26** | Berlin | ~$9bn, Oct 2021, Series E | [Company press release](https://n26.com/en-eu/press/press-release/n26-announces-landmark-series-e-funding-round) |
| **Personio** | Munich | $8.5bn, Jun 2022, Series E second close | [TechCrunch](https://techcrunch.com/2022/06/21/personio-nabs-200m-at-a-8-5b-valuation-as-its-hr-for-small-businesses-hits-the-big-time/) |
| **DeepL** | Cologne | $2bn, May 2024 | [TechCrunch](https://techcrunch.com/2024/05/22/deepl-the-ai-language-translation-startup-nabs-300m-on-a-2b-valuation-to-focus-on-b2b-growth/) |
| **Parloa** | Berlin / New York | $1bn, May 2025, Series C | [Company press release](https://www.parloa.com/parloa-in-the-press/parloa-raises-120m-series-c-to-reinvent-customer-service-with-agentic-ai/) |
| **Moss** | Berlin | €1bn, Aug 2026, Series C | [Company press release](https://www.getmoss.com/magazine/moss-series-c) |

Notes carried into the records:

- **Celonis** and **Parloa** are dual-HQ and use `alsoBasedIn` rather than being forced into one city.
- **Moss**'s valuation carries a `disputed` note: Gründerszene reports the round in dollars
  where the company, Sifted and EU-Startups report €1bn. Separately, the company's own press
  release gives the round as **€35m** while Sifted, EU-Startups and Gründerszene all report
  **€30m**; the record follows the company on its own round size.
- **DeepL** has been reported since April 2025 as looking at a US listing
  ([Sifted](https://sifted.eu/articles/deepl-ipo-2026)). It had not listed as of this review,
  so it still qualifies — but it is the entry most likely to fall out.

## Include — written (batch 2)

| Company | HQ | Valuation as reported | Evidence |
|---|---|---|---|
| **osapiens** | Mannheim | over $1.1bn, Jan 2026, Series C | [Tech.eu](https://tech.eu/2026/01/14/german-startup-osapiens-becomes-unicorn-following-100m-funding-round/) |
| **Black Forest Labs** | Freiburg / San Francisco | $3.25bn post-money, Dec 2025, Series B | [Tech.eu](https://tech.eu/2025/12/01/black-forest-labs-secures-300m-series-b-at-325b-valuation/), [company blog](https://bfl.ai/blog/our-300m-series-b) |
| **Razor Group** | Berlin | $1.2bn, Apr 2023, Series C | [TechCrunch](https://techcrunch.com/2023/04/17/razor-group-aggregator-stryze/) |
| **Forto** | Berlin | $2.1bn, Mar 2022, Series D | [Company press release](https://forto.com/en/press-releases/forto-announces-new-investment-of-250-million-to-accelerate-international-expansion-and-broadening-of-product-offering/) |
| **commercetools** | Munich | $1.9bn, Sep 2021, Series C | [TechCrunch](https://techcrunch.com/2021/09/13/commercetools-raises-140m-at-a-1-9b-valuation-as-headless-commerce-continues-to-boom/) |
| **Choco** | Berlin | $1.2bn, Apr 2022, Series B2 | [Company press release](https://choco.com/us/press/choco-achieves-unicorn-status) |
| **Staffbase** | Chemnitz | $1.1bn, Mar 2022, Series E | [TechCrunch](https://techcrunch.com/2022/03/15/staffbase-raises-115m-at-a-1-1b-valuation-to-help-internal-comms-teams-get-their-message-across/) |
| **Taxfix** | Berlin | over $1bn, Apr 2022, Series D | [TechCrunch](https://techcrunch.com/2022/04/27/taxfix-the-berlin-based-mobile-tax-filing-app-raises-220m-at-a-1b-valuation/) |

Notes carried into the records:

- **Black Forest Labs** is dual-HQ (its own announcement says "our HQs in Freiburg and San
  Francisco") and uses `alsoBasedIn`.
- **Razor Group** publishes its $1.2bn post-money of April 2023, not the $1.7bn attached to
  the March 2024 Perch merger. TechCrunch's headline calls that larger figure a valuation;
  the same article's body calls it the *enterprise value* of the merged business, carried
  with about $400m of debt. Inclusion rule 3 names a post-money, and enterprise value counts
  debt that a post-money does not, so the record publishes the measure the rule names and
  carries the $1.7bn in a `disputed` note beside it. The March 2024 round therefore has
  `postMoney: null` — a field named post-money should not hold an enterprise value either.
- **Forto** crossed $1bn at the June 2021 round, not at the better-known $2.1bn Series D of
  March 2022 — the same trap Celonis fell into in batch 1, so `becameUnicorn` points at the
  earlier round.
- **Taxfix**, **Choco**, **Staffbase**, **commercetools** and **Forto** all last published a
  valuation between 2021 and 2024 and have raised no priced equity round since. They still
  qualify — the rule is *a publicly reported post-money*, not a recent one — and the site's
  own staleness flag marks the age rather than the register hiding it.

## Include — written (batch 3)

| Company | HQ | Valuation as reported | Evidence |
|---|---|---|---|
| **Proxima Fusion** | Munich | €2.4bn, Jul 2026, €411m financing round | [Company press release](https://www.proximafusion.com/press-news/proxima-fusion-raises-eu411-million-to-build-europes-commercial-fusion-champion) |
| **Enpal** | Berlin | €2.2bn, Jan 2023, Series D | [Sifted](https://sifted.eu/articles/enpal-215m-solar-panels-news) |
| **Scalable Capital** | Munich | $1.4bn, Dec 2023, Series E extension | [TechCrunch](https://techcrunch.com/2023/12/06/european-neobroker-scalable-capital-raises-65m-on-a-flat-1-4b-valuation/) |
| **1KOMMA5°** | Hamburg | $1bn, Jun 2023, Series B | [Company press release](https://1komma5.com/en/press/press-releases/1komma5-unicorn-en/) |
| **sennder** | Berlin | over $1bn, Jan 2021, Series D | [Tech.eu](https://tech.eu/2021/01/14/berlin-based-digital-freight-forwarder-sennder-bags-160-million-at-a-1-billion-valuation/) |

Notes carried into the records:

- **Two of the five crossed earlier than the round they are famous for**, which is the
  batch-1 Celonis error and the reason `postMoney` is now filled in wherever a source states
  one. **Enpal** is dated to a €2.2bn Series D of January 2023 in every list, but TechCrunch
  reported the October 2021 Series C close at "€950 million ($1.1 billion) post-money, the
  company has confirmed" — under the threshold in euros, over it in dollars, and the dollar
  figure is the source's own, not a conversion of ours. **Scalable Capital**'s crossing is
  named inside the very article that carries its published valuation: the December 2023
  round was flat at $1.4bn because that "was the same valuation Scalable Capital had the last
  time it raised money — $180 million in 2021". The crossing is June 2021, not December 2023.
- **Proxima Fusion** carries a `disputed` note. Its own announcement and EU-Startups give
  €2.4bn; [Sifted](https://sifted.eu/articles/google-proxima-fusion-411m-raise) gives €2.5bn,
  same day, same round. The record publishes the company's own figure and shows Sifted's
  beside it.
- **1KOMMA5°** carries a `disputed` note on the round rather than the valuation. The round is
  universally reported as €430m; the company's own release splits it into "215 million Euro
  in equity" plus "an additional 215 million Euro in re-participation options, which can be
  paid as part of the purchase price for new acquisitions". Only the first half is money
  raised.
- **sennder** carries a `disputed` note for the reverse reason: a €2bn figure is attached to
  it by a Tech.eu headline about a raise that was being *prepared* in December 2022 and never
  closed. Talks are not a post-money.
- **Two schema limits were hit and fixed** rather than worked around by dropping facts.
  `postMoneyCurrency` exists because Enpal's Series C was raised in euros and priced by its
  source in dollars. `postMoneySource` exists because 1KOMMA5°'s own release states the
  equity raised in one paragraph and the valuation in another. Neither relaxes a check.

## Include — written (batch 4)

| Company | HQ | Valuation as reported | Evidence |
|---|---|---|---|
| **Flix** | Munich | over $3bn, Jun 2021, Series G | [Company press release](https://corporate.flix.com/press_releases/flixmobility-raises-over-650m-in-funding-at-3b-valuation-planning-further-global-expansion/), [TechCrunch](https://techcrunch.com/2021/06/02/flixmobility-raises-650m-at-a-3b-valuation-to-double-down-on-buses-and-other-transport-in-the-us/) |
| **FINN** | Munich | over €1bn, Jun 2026, Series D | [Investor press release (Portage, lead)](https://portageinvest.com/blog/finn-raises-e140-million-and-achieves-unicorn-status/) |
| **CMBlu Energy** | Alzenau | over €1bn, Apr 2026, Series C initial close | [Company press release](https://www.cmblu.com/press-media/cmblu-surpasses-eu1b-unicorn-threshold-with-eu50m-initial-close-of-series-c-defining-baseload-infrastructure-for-ai-and-data-centers) |
| **Dash0** | New York (founded in Germany) | $1bn, Mar 2026, Series B | [Company press release](https://www.dash0.com/blog/dash0-raises-usd110m-series-b) |
| **n8n** | Berlin | $5.2bn, May 2026, secondary | [Tech.eu](https://tech.eu/2026/05/12/n8n-s-valuation-doubles-to-5-2bn-following-sap-strategic-investment/) |
| **Stark** | Berlin | €3.5bn, Jun 2026, funding round | [Tech.eu](https://tech.eu/2026/06/23/stark-bags-eur500-million-in-new-funding/) |

Six published here, from two different routes. Flix, FINN, CMBlu Energy and Dash0 are what
this batch's own queue produced — four, not the six or seven the queue implied, since two of
the names it carried did not survive contact with their own sources and are below instead.
n8n and Stark followed afterward on a direct instruction to add them, outside that queue's
own research; both were checked against the same three rules as everything else here rather
than taken on trust, and are written up below alongside the four the queue did produce.

Notes carried into the records:

- **Flix is not published on the figure it was queued for.** The queue expected Bloomberg's
  July 2024 transaction number, and the record carries it in a `disputed` note instead. Read
  through a Wayback snapshot, [Bloomberg, 2024-07-04](https://www.bloomberg.com/news/articles/2024-07-04/eqt-german-tycoon-buy-1-billion-stake-in-greyhound-owner-flix)
  says EQT and Kühne Holding are "investing around €1 billion ($1.2 billion) in Flix in a
  deal valuing the business at more than €3 billion, people with knowledge of the matter
  said." Two things keep that out of the valuation field. It is attributed rather than
  disclosed — Flix's own announcement and EQT's, both opened and read, describe the deal and
  state no figure at all. And the transaction is part primary and part secondary (EQT: "[i]n
  addition to a primary investment in Flix … acquire shares from existing shareholders"), so
  it prices the company at a deal rather than being a post-money struck by a round. What the
  record publishes instead is Flix's *own* stated valuation of "more than $3 billion" from
  June 2021 — a higher figure in any case, so nothing is understated. The July 2024 round
  therefore has `postMoney: null`, which is the honest shape for a round whose price nobody
  disclosed, and the validator's own comment says so.
- **Flix crossed in July 2019, not 2021.** This is the fourth time the crossing trap has
  caught a record, and the fourth time the answer was inside an article already being cited.
  TechCrunch's August 2019 piece on the Series F extension quotes co-founder Jochen Engert
  confirming it was "at the same valuation as the first close of the Series F (which was just
  over $2 billion)". `becameUnicorn` points at that first close.
- **FINN**'s round is reported everywhere as €140m; the lead investor's own announcement
  splits it into "nearly €100 million in equity financing" and "more than €40 million in debt
  capital". The register records the equity and keeps €140m in a `disputed` note. This is the
  1KOMMA5° problem again, and it matters more than usual here: FINN finances a vehicle fleet,
  so debt is a working input to the business model, not a rounding difference.
- **CMBlu Energy** is published on an *initial close*, not a completed round, and the record
  says so. Its `founders` array is empty and renders as "—": the company's own site names a
  CEO, a CTO and seven other executives and does not identify a founder anywhere, and no
  allowlisted publication opened here does either. An empty field is the correct output; a
  name recalled from memory is not. Alzenau is the first small town on the map, added to
  `data/geo/germany.json` by re-running `tools/fetch_geo.py` with coordinates read off
  OpenStreetMap's own record — no pixel value in that file is placed by hand.
- **Dash0 is the register's first record with a foreign headquarters**, and it is worth being
  explicit about why it is in. Rule 1 is a disjunction — founded in Germany **or**
  headquartered in Germany — and Dash0 satisfies the first limb on its own account: "Founded
  in 2023 in Germany and headquartered in New York". [Sifted](https://sifted.eu/articles/dash0-targets-1bn-valuation-with-balderton-led-funding-round-reports-say)
  independently calls it "[t]he German-founded startup". Its `hq` is recorded as New York, US,
  which means the map counts it under "not shown" — the honest result, rather than inventing a
  German office the company does not claim. Note also that the $1bn first reached an
  allowlisted page in February as an *in-talks* figure; the record publishes the round that
  closed four weeks later at that price, announced by the company, and keeps the earlier
  report in a `disputed` note.
- **n8n**'s $5.2bn is set by a secondary share sale, not a priced primary round, and the
  record labels it as one rather than letting it read as new money: Tech.eu, "SAP's
  investment in n8n comes courtesy of an n8n secondary share sale, which brings SAP to the
  n8n cap table for the first time." Rule 3 says "post-money" with no carve-out for this; the
  register already publishes a secondary elsewhere too (Trade Republic's €12.5bn), always
  labelled as what it is — see the note added to [UPDATING.md](UPDATING.md#inclusion-rules).
- **Stark**'s crossing round (Jan 2026, over $1bn) was never announced by the company at all.
  The register publishes it anyway because an allowlisted source states both the date and the
  threshold as its own confirmed finding, not a rumour: Sifted, in June 2026, "reached
  unicorn status in an unannounced January funding round valuing it at more than $1bn" — a
  figure that traces in turn to Manager Magazin and "a person close to the company," which is
  why that round carries no amount and no investors on file. **Open question, not resolved:**
  Bloomberg's own headline for the June 2026 round that made Stark's status public reads "at
  a €3.2 Billion Valuation," against the €3.5bn Tech.eu and the company itself state for the
  identical announcement — and Bloomberg's own URL for that piece keeps the slug
  `...at-3-5-billion-valuation`, so even Bloomberg's headline and its own link disagree.
  bloomberg.com 403s this crawler and no Wayback capture could be retrieved (rate-limited at
  every attempt), so the piece itself has not been read and no claim is made about what it
  says beyond its headline. Recorded here rather than as a `disputed` note on the record,
  because a conflict between an unread headline and a confirmed figure is not the same kind
  of thing as a quote that has actually been read and disagrees.

## Include — written (batch 5)

Five names, all five previously in "cannot be established", all five moved by the rule change
described at the top of this file. They are the whole of that section's movement: everything
else in it was re-checked and stayed.

| Company | HQ | Valuation as reported | Evidence |
|---|---|---|---|
| **Quantum Systems** | Gilching | $8bn, Jul 2026, Series D | [Tech.eu](https://tech.eu/2026/07/02/quantum-systems-raises-12bn-at-8bn-valuation/) |
| **Neura Robotics** | Metzingen | $7bn, Jun 2026, Series C | [Sifted](https://sifted.eu/articles/neura-robotics-1-4bn-series-c), [Gründerszene](https://www.businessinsider.de/gruenderszene/sieben-neue-unicorns-diese-deutschen-startups-sind-jetzt-milliarden-wert/) |
| **Raisin** | Berlin | **undisclosed** — "über zwei Milliarden Euro", Dec 2024, secondary | [Gründerszene](https://www.businessinsider.de/gruenderszene/business/kurz-vor-ipo-bewertung-von-raisin-steigt-auf-ueber-zwei-milliarden-euro/) |
| **Isar Aerospace** | Munich | **undisclosed** — "became a unicorn in June", Jun 2025, convertible bond | [TechCrunch](https://techcrunch.com/2025/09/08/more-than-10-european-startups-became-unicorns-this-year/) |
| **Focused Energy** | Darmstadt / Austin | **undisclosed** — "knackte die Milliarden-Bewertung", May 2026, Series A | [Gründerszene](https://www.businessinsider.de/gruenderszene/sieben-neue-unicorns-diese-deutschen-startups-sind-jetzt-milliarden-wert/) |

Three of the five are published with **no valuation figure at all**, which is the whole point
of the change. Each carries an `undisclosed` note naming what is known, what is not, and the
sentence that establishes membership — and each renders on the site as "Undisclosed" beside an
amber `>1bn` marker rather than as a blank, a dash or a zero.

Notes carried into the records:

- **Quantum Systems** is the case the rule was changed for, and it turned out to need only
  half of it. Its *valuation* was never the problem: Tech.eu prints "$1.2bn in fresh funding,
  in a round which more than doubles its valuation to $8bn" and the record publishes that.
  What kept it out was the **crossing**. It became a unicorn at the €160m Series C of May
  2025, and no allowlisted account prints that round's valuation as a numeral — Sifted says
  only "making it one of only a few unicorns in the European defence tech field"; the
  company's own release, recovered from the Wayback Machine because quantum-systems.com 403s
  this crawler, gives the round, the investors and the total raised and states no valuation;
  Tech.eu and Balderton both say the November extension "tripled its valuation" to above €3bn
  without saying what it tripled *from*. Two sources settled it in words rather than digits:
  Handelsblatt, the same week, "Mit der neuen Finanzierung wird das Start-up mit mehr als
  einer Milliarde Dollar bewertet", and TechCrunch four months later, "Quantum Systems became
  a unicorn in May 2025, according to PitchBook". So the record now has a numeric valuation
  and a *qualitative crossing round* — `postMoney: null` plus an `undisclosed` note — which is
  a shape that did not exist before this batch. Both figures the November extension disclosed
  (€180m raised, above €3bn post-money) are recorded on their own round, so the earlier-crossing
  check still has something to compare against.
- **Neura Robotics is published on a number, not on a note, and that is a judgement call worth
  showing.** The $7bn reaches an allowlisted page at second hand — Sifted, "the Financial
  Times reported, citing people familiar with the deal" — and Neura declined to comment on it.
  On its own that is the Flix shape, where an attributed figure was kept out of the valuation
  field. What tips it the other way is a second, independent allowlisted account stating the
  same figure flatly as fact rather than as a report: Gründerszene's round-up of 2026's German
  unicorns, "Die Bewertung: sieben Milliarden Dollar und damit Einhorn-Status." The figure is
  published with a `disputed` note saying exactly this, because the owner's rule explicitly
  allows a badge where the valuation is contestable. The round carries a second `disputed`
  note: Sifted reports "a $1.4bn Series C round", while the company and Tech.eu say "**up to**
  $1.4 billion" — a milestone ceiling, not a sum already wired.
- **Raisin's figure is in words, and that is the only reason it is undisclosed.** Gründerszene
  states it — "Raisin liegt nun bei einer Bewertung von über zwei Milliarden Euro" — and
  spells the number out, so there is no numeral for the quote check to match, exactly the
  situation the new rule exists for. Handelsblatt independently calls the company
  "milliardenschwer" and nothing more precise. Two further facts are carried into the record
  rather than smoothed over. The valuation was set by a **secondary** in which existing
  holders sold stock, not by a priced round, and is labelled as one. And Raisin's unicorn
  status has **not been continuous**: Kinnevik marked the merged Raisin DS at €1.3bn in July
  2021, wrote it down to €895m in 2022 — at which point Gründerszene's own headline was
  "Raisin verliert Unicorn-Status" — and the March 2023 Series E restored it, with co-founder
  Frank Freund saying so in that round's coverage: "Unser Unicorn-Status wurde mit der
  jetzigen Upround bestätigt." `becameUnicorn` therefore points at March 2023, the crossing
  that currently holds, not at 2021. Rule 2 was checked rather than assumed: Raisin has
  planned an IPO since 2024 and has not listed, and its CFO was still saying in December 2025
  that the company is run "ob gelistet oder nicht".
- **Isar Aerospace crossed on a convertible bond**, which is why no post-money exists to
  publish and why the previous rule could never have admitted it. TechCrunch states the
  instrument, the month and the status in one sentence: "German space startup Isar Aerospace
  became a unicorn in June after reaching an agreement with Eldridge Industries for a
  convertible bond of €150 million". Everything the earlier review found still stands — the
  company's own €270m Series D release states no valuation, Sifted's account of it states
  none, and the €2bn widely attached to the company traces to a Bloomberg piece whose own URL
  slug says "in-talks-to-raise-250-million" and whose three Wayback captures are all 403 block
  pages. None of that had to be resolved to publish the company; it only had to stop being
  *required*. Note that its own university's press release is titled "Isar Aerospace becomes a
  unicorn" — a primary source, but a university is not on the allowlist, so it is mentioned in
  the record's note and not cited.
- **Focused Energy is the one whose earlier exclusion actively pointed the wrong way.** The
  previous review found secondary write-ups putting it "close to one billion dollars", which
  if accurate would be *below* the threshold, and its own release claims only that the round
  "makes it the most valuable fusion company in Europe" — a superlative, not a figure.
  Gründerszene has since said the opposite in plain terms, twice: in the sentence quoted in
  the record ("sichert sich 240 Millionen US-Dollar und knackte die Milliarden-Bewertung") and
  by listing the company among the seven German startups that became unicorns in the first
  half of 2026. The record dates the round to **May** — when the company announced it and the
  German press reported it — rather than to TechCrunch's June write-up, which itself says the
  round was "announced last week". Darmstadt joins the map; Austin is recorded in
  `alsoBasedIn` on Sifted's own line, "HQ: Darmstadt, Germany and Austin, Texas, USA". Its
  $11m Series A of 2023 is deliberately **not** in the rounds list: the only allowlisted
  account of it (Sifted) attributes the figure to Dealroom, and a data platform relayed by a
  publisher is a lead rather than the publisher's own finding.
- **Gilching, Metzingen and Darmstadt** were added to `data/geo/germany.json` by re-running
  `tools/fetch_geo.py` with coordinates read off OpenStreetMap. Two of the three are towns
  rather than cities. Quantum Systems in particular is called "Munich-based" by Sifted and
  "aus Gilching bei München" by Handelsblatt; the register records the town and lets the map
  place it, rather than moving a company 25 km for the sake of a name a reader would
  recognise. Re-running the script left the outline byte-identical — no pixel in that file is
  placed by hand.

## Cannot be established

No rule is shown to fail. The evidence the rules demand either does not exist or cannot be
reached, and each row names the single thing that would change that. **Several of these are
larger than anything in the register.** They are absent for want of a readable sentence, not
for want of standing.

**Every row here was re-read against the August 2026 rule change**, which asks only whether an
allowlisted source reports the company over the threshold, in words or in digits. Five rows
left this section as a result and are written up as batch 5 above. The rows that remain are
not here because a numeral is missing — they are here because *no allowlisted sentence says
the company is a unicorn at all*, in any form, or because what exists describes a round that
has not closed. That is a different gap, and the change does not touch it. Each row below now
says so explicitly.

| Company | HQ | What is missing, and what would settle it |
|---|---|---|
| **The Exploration Company** | Munich | Still in talks: $300m at more than $2bn, attributed to the FT and unconfirmed by the company, with the reporting itself cautioning that terms could move or the deal fall away. Re-checked in August 2026 and nothing has closed. One caveat on the re-check, stated rather than glossed: a Bloomberg item of 26 July 2026 appears to relay the same FT report, and **that page was not opened** — bloomberg.com 403s this crawler and the archive was rate-limiting at the time of the check — so it is not cited here and nothing is claimed about its contents. The entry rests on the reporting already read. Talks are not a post-money. **Re-checked against the new rule and unmoved:** no allowlisted publication says this company *is* a unicorn, in words or digits — they say a round is being discussed at a price. Dropping the numeral requirement does not turn a deal that has not happened into one that has. **Settled by:** the round closing, or any allowlisted page stating the company has passed the threshold |
| **Agile Robots** | Munich | The most recent allowlisted reporting is about a round that has not happened: Sifted's June 2026 piece is headlined "SoftBank in talks to back Agile Robots' $800m round, reports say". Talks are not a post-money. ([Sifted, 2026-06-02](https://sifted.eu/articles/softbank-in-talks-to-back-agile-robotics-in-800m-round-reports-say)) **Re-checked against the new rule and unmoved.** The obvious hope was that some allowlisted piece calls it a unicorn in passing, since it is widely described as Germany's first robotics unicorn. TechCrunch's March 2026 piece on its Google DeepMind partnership was opened and read for exactly that: it gives the headquarters ("Munich, Germany-based Agile Robots"), the founding year and the funding ("has raised more than $270 million in venture capital funding"), and states no valuation and no unicorn status anywhere. **Settled by:** the round closing, or any allowlisted page stating the company is over the threshold |
| **Grover** | Berlin | Tech.eu's own piece announcing unicorn status is careful about what the money was: "As tech rental platform Grover achieves unicorn status, it's also raised over $2 billion in funding, the vast majority of which is debt" — and, later, "To date, Grover has raised over $2 billion, 90% of which is debt funding." No post-money equity valuation appears anywhere in it. ([Tech.eu, 2022-04-07](https://tech.eu/2022/04/07/berlins-grover-hits-super-grover-status-with-unicorn-valuation-but/)) **This is the row the new rule comes closest to moving, and it does not move it.** "Achieves unicorn status" is exactly the kind of qualitative statement that now counts — but rule 3 asks what a company *is* worth, not what it was worth in April 2022, and this sentence is four years old and the only one of its kind. Since then Grover has raised a €50m bridge (July 2024) rather than a priced up-round, and the same Tech.eu piece is at pains to say the money behind the label was "over $2 billion, 90% of which is debt". The register does publish valuations years old and flags them as aged; what it will not do is publish a four-year-old *status* claim, with no figure attached and a later down-round-shaped financing after it, as though it described the company today. **Settled by:** any allowlisted page from the last two years stating Grover is over the threshold, in words or digits |
| **Marvel Fusion** · **instagrid** · **Black Semiconductor** | — | Grouped because the gap is identical and the answer is the same. No allowlisted publication has printed a post-money at or above the threshold for any of the three, and their disclosed raises are an order of magnitude below the level at which one would be expected — Marvel Fusion's Series B extension runs to about €113m, Black Semiconductor's Series A to under $30m of equity. "Almost certainly below the threshold" is a good guess and this file does not publish guesses in either direction. **Re-checked against the new rule and unmoved:** none of the three has an allowlisted sentence calling it a unicorn either, so there is nothing for the qualitative route to carry. The gap here was never the numeral. **Settled by:** an allowlisted page stating a post-money, or stating the company has passed the threshold |
| **Mambu** | — | The HQ limb verifiably fails: TechCrunch, opened and read, calls it "Amsterdam/London-based Mambu" at the €4.9bn Series E ([2021-12-09](https://techcrunch.com/2021/12/09/mambu-nabs-266m-at-a-5-5b-valuation-to-double-down-on-embedded-financial-service-and-banking-apis/)). The founding limb rests on a Berlin origin that no allowlisted publication states. Same shape as wefox, arrived at from the opposite direction. Unaffected by the rule change, which touches rule 3 only. **Settled by:** an allowlisted or primary record of a German founding |
| **SumUp** | — | The gap is rule 1, not the figure. The HQ limb verifiably fails: TechCrunch, opened and read, calls it "the London-based company" in the same piece that reports its valuation ([2022-06-23](https://techcrunch.com/2022/06/23/sumup-raises-624m-at-8-5b-valuation-with-its-payments-and-business-tech-now-used-by-4m-smbs/): "values SumUp at €8 billion ($8.5 billion)") — a figure this file previously, and wrongly, characterised as debt rather than a post-money; the same sentence shows it is reported as the latter. That correction does not rescue the entry. The founding limb rests on a founding story no allowlisted publication states a location for. Same shape as Mambu, London standing in for Amsterdam. Unaffected by the rule change, which touches rule 3 only — SumUp's figure was never the problem. **Settled by:** an allowlisted or primary record of a German founding |

## Exclude — verified

| Company | Reason | Source |
|---|---|---|
| **GoStudent** | Austrian, not German — settled this batch against a page that was opened rather than assumed. Sifted: "GoStudent is one of just six unicorns in Austria", and, in the same piece, "the Vienna-based company picked up over €500m in funding". Fails rule 1. | [Sifted, 2023-08-04](https://sifted.eu/articles/gostudent-edtech-raises-95m-news) |
| **Vivid** | From Sifted's own list of German companies that could soon reach $1bn. That is the finding: it has not. Sifted names it as one of Germany's "soonicorns" — "companies that could soon achieve a $1bn valuation" — but states no figure for it; the number comes from Vivid's own release, a €100m Series C "reaching a valuation of 775 million Euros" in February 2022. Below the threshold, so rule 3 fails. | [Sifted, 2026-02-27](https://sifted.eu/articles/dash0-targets-1bn-valuation-with-balderton-led-funding-round-reports-say), [Company press release, 2022-02-08](https://press.vivid.money/press-releases-feed/vivid-money-raises-100-million-euro-series-c-to-further-transformation-into-financial-superapp) |
| **HappyRobot** | The "Telekom-backed AI unicorn" from the August 2026 scan is headquartered in San Francisco and founded by a Spanish team. German by investor base only, which does not qualify. | [Gründerszene, 2026-08-07](https://www.businessinsider.de/gruenderszene/ki-startup-ist-jetzt-ein-unicorn-150-konzerne-nutzen-es-bereits/) |
| **Solaris** | No longer independent: SBI Holdings took a majority stake of more than 70% in the February 2025 Series G. | [Tech.eu, 2025-05-06](https://tech.eu/2025/05/06/solaris-co-founder-takes-legal-action-over-japanese-conglomerate-sbi-takeover/) |
| **Gorillas** | Acquired by Getir in December 2022. | [TechCrunch, 2022-12-09](https://techcrunch.com/2022/12/09/instant-grocery-app-getir-acquires-its-competitor-gorillas/) |
| **Flink** | Berlin quick commerce, once one of Germany's most valuable startups, raised $100m in March 2026 at a **$900m** valuation — below the threshold, so it is now a former unicorn rather than a current one. Sifted: "Speedy grocery startup Flink has raised $100m in funding, in a deal which reportedly values the Berlin-based company at $900m". | [Sifted, 2026-03-03](https://sifted.eu/articles/flink-100m-900m-valuation) |
| **EGYM** | Munich's connected-fitness company was, on Handelsblatt's account, the *only* German startup to reach $1bn in 2024 — and it no longer exists as an independent company. It merged into Playlist, the American parent of ClassPass and Mindbody; the deal closed on 31 March 2026 and "EGYM will operate under Playlist alongside its other brands". Fails rule 2. | [TechCrunch, 2026-03-31](https://techcrunch.com/2026/03/31/the-company-behind-classpass-and-mindbody-just-got-a-lot-bigger-with-a-7-5b-merger/) |
| **Zalando**, **Delivery Hero**, **HelloFresh**, **Auto1**, **Ottobock** | Publicly listed, so not private. Ottobock is the most recent, listing in Frankfurt in October 2025. | Listed on the Frankfurt Stock Exchange |
| **About You** | Acquired by Zalando and delisted; no longer independent. | Zalando/About You combination completed 2025 |
| **Contentful** | The Berlin-founded headless CMS closed a $175m Series F in 2021 at over $3bn — which would have put it near the top of the register — and was **acquired by Salesforce**, announced 1 June 2026. Tech.eu: "Contentful, the German-founded content management company, is to be acquired by US software giant Salesforce, the companies announced today." Fails rule 2. | [Tech.eu, 2026-06-01](https://tech.eu/2026/06/01/berlin-based-contentful-snapped-up-by-salesforce/) |
| **Volocopter** | Insolvent: "German electric air taxi company Volocopter has filed for bankruptcy protection". Fails rule 2. | [TechCrunch, 2024-12-30](https://techcrunch.com/2024/12/30/mercedes-backed-volocopter-files-for-bankruptcy/) |
| **Lilium** | Insolvent and wound down; TechCrunch's October 2025 piece describes it in the past tense as the "defunct electric aircraft startup" whose technology has ended up at Archer. Fails rule 2. | [TechCrunch, 2025-10-16](https://techcrunch.com/2025/10/16/defunct-electric-aircraft-startup-liliums-tech-lives-on-over-at-archer/) |
| **Cognigy** | Acquired by NiCE — "US customer service giant NICE has paid almost $1bn to acquire Düsseldorf-based Cognigy in what is Europe's biggest AI acquisition to date". Fails rule 2, and note the price is *below* the threshold in any case. | [Sifted](https://sifted.eu/articles/cognigy-sells-for-almost-1bn-in-europes-biggest-ai-acquisition-yet), [Tech.eu, 2025-07-28](https://tech.eu/2025/07/28/german-ai-startup-cognigy-hoovered-up-by-us-customer-service-firm-nice/) |
| **Tier Mobility** | Merged with Dott and the brand retired: "Tier becomes Dott following the merger of the two micromobility companies". No longer a standalone German company. Fails rule 2. | [TechCrunch, 2024-09-30](https://techcrunch.com/2024/09/30/tier-becomes-dott-following-the-merger-of-the-two-micromobility-companies/) |
| **wefox** | Fails rule 1's headquarters limb, verifiably, and the founding limb is contested rather than established, so there is nothing left to qualify it on. wefox's own imprint gives "wefox Holding AG, Räffelstrasse 26, 8045 Zürich, Switzerland", "[e]ntered in the commercial register of the Canton of Zürich"; its own release of 31 July 2024, datelined Zurich, says "[t]hese two transactions largely complete the announced exit of wefox from the German market"; and its site now lists exactly three businesses — Austria, the Netherlands and Switzerland. The founding limb is all that could save it, and it is contested rather than settled: TechCrunch wrote "Founded out of Berlin in 2015" in July 2022, but its own March 2019 piece has co-founder Julian Teicke describing the company's revenue "since being founded in 2014" — a different year, from the company's own CEO, in a different TechCrunch piece than the one this row previously (and wrongly) cited — and wefox's own boilerplate says only "Founded in 2015", never where. The $4.5bn of May 2023 is real and sourced (TechCrunch, 2023-05-16: "Wefox managed to maintain the same valuation of $4.5 billion") but moot while rule 1 fails. Note separately that the [€550m Bloomberg figure of 2024](https://www.bloomberg.com/news/articles/2024-06-13/mubadala-favors-selling-fintech-wefox-against-founders-wishes) settles nothing either way: it is an enterprise value for an offer the board rejected, so it is neither a post-money nor a completed transaction. **Settled by:** a primary record — a Handelsregister entry or a company statement — of where wefox was originally incorporated, which would revisit this against rule 1's founding limb rather than its headquarters. | [wefox imprint](https://www.wefox.com/imprint), [wefox exit release, 2024-07-31](https://www.wefox.com/press/wefox-successfully-completes-two-transactions-to-exit-the-german-market), [TechCrunch, 2022-07-11](https://techcrunch.com/2022/07/11/wefox-grabs-400m-at-4-5b-valuation-to-buck-the-insurtech-downturn-trend/), [TechCrunch, 2019-03-05](https://techcrunch.com/2019/03/05/wefox-group-the-berlin-based-insurance-tech-startup-raises-125m-series-b-led-by-mubadala/), [TechCrunch, 2023-05-16](https://techcrunch.com/2023/05/16/wefox-secures-new-funding-at-45-billion-valuation-as-it-aims-for-profitability/), [Bloomberg, 2024-06-13](https://www.bloomberg.com/news/articles/2024-06-13/mubadala-favors-selling-fintech-wefox-against-founders-wishes) |

## How the list was swept for names nobody had considered

Three sweeps were run before this file was closed, because the risk at the end is not a wrong
figure but a company that was never looked at.

1. **Trade-press lists of new unicorns.** TechCrunch's running list of 2026's new unicorns
   ([2026-07-05](https://techcrunch.com/2026/07/05/almost-40-new-unicorns-have-been-minted-so-far-this-year-here-they-are/))
   was fetched and read in full: it contains **no German company at all**, which is itself
   worth recording — it is compiled from Crunchbase and PitchBook and is heavily American, so
   an absence there is not evidence about Germany.
2. **German-language trade press.** Gründerszene's 2026 and 2025 round-ups of German startups
   reaching a billion are behind Business Insider's paywall and their bodies could not be
   read — both pages were fetched and both stop at "Lade Premium-Inhalte…". Four names were
   nonetheless visible in search summaries of those pages, and because a summary is not a
   read, all four were then chased to primary sources independently and the summary discarded: **osapiens** (already published), **Dash0** and **CMBlu
   Energy** (both published in batch 4), and **Focused Energy** (chased, found to state no
   valuation, excluded — and published in batch 5 once the rule stopped requiring one).
   A paywalled list is a lead, never a source. **This changed in batch 5 and is worth
   recording**: the same Gründerszene round-up that stopped at "Lade Premium-Inhalte…" now
   returns its full body, so the 2026 list was finally *read* rather than inferred from a
   search summary. It names seven German companies that became unicorns in the first half of
   2026 — osapiens, Dash0, Stark, CMBlu, Focused Energy, Neura Robotics and FINN — six of
   which were already published from their own primary sources, and the seventh of which
   (Focused Energy) is published in batch 5 with that page as its evidence. A list that
   agrees, company for company, with a register assembled independently of it is the closest
   thing to an external check this file has. The same piece also reports **Clark** losing
   unicorn status on falling revenue, and **Contentful**'s sale to Salesforce, which is
   already recorded under exclusions.
3. **Sifted's German "soonicorn" list**, which names the companies closest to the threshold
   from below: **Vivid** (excluded above, €775m), **Proxima Fusion** (since crossed;
   published in batch 3) and **Finn** (since crossed; published in batch 4).
4. **TechCrunch's European unicorn round-ups**, added as a sweep in batch 5 and the source of
   two of its five. The [2025 list](https://techcrunch.com/2025/09/08/more-than-10-european-startups-became-unicorns-this-year/)
   names **Isar Aerospace** and **Quantum Systems** with the month each crossed and no figure
   for either — worthless under the old rule, decisive under the new one. Its
   [January 2026 list](https://techcrunch.com/2026/01/31/meet-the-new-european-unicorns-of-2026/)
   and its [deep-tech spinout survey](https://techcrunch.com/2025/12/30/76-european-deep-tech-university-spinouts-reached-unicorn-or-centaur-status/)
   were both read in full and produced no German name not already on this page.

Everything those sweeps produced now appears somewhere above with a verdict: 32 rows carry
**include**, matching the register's own count company for company, 19 carry **exclude**, and
8 carry **cannot be established** — every row settled, none left as a placeholder.

One row above carries no headquarters city, and deliberately: Marvel Fusion, instagrid and
Black Semiconductor are excluded from the register on rule 3, so no page stating their
headquarters was opened, and this file does not fill a column from memory any more than a
record does.
