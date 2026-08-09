# Candidates

**What this file is.** Every company considered for the register, each with a status —
**include**, **exclude**, or **cannot be established** (defined below) — and the reason for
it. It is not a shortlist or a backlog, and it is the only place a reader can check what was
looked at and why a name is, or isn't, on the register.

**It is not guaranteed to be complete.** Two kinds of gap are possible, and both are worth
naming rather than implying away. A company can simply not have been looked at yet — the
sweeps recorded near the end of this file are an attempt to close that gap, not proof it is
fully closed. And this file's write-up can lag the register it describes: as of the review
date below, **n8n** and **Stark** are published — `data/companies/n8n.json` and
`data/companies/stark.json` carry full sourcing — without a matching row here yet. Where the
two disagree, `data/companies/` is the current truth and this file is the reasoning trail
behind everything else in it.

**Exclusions are as deliberate as inclusions.** A name dropping off this list is usually a
fact — an IPO, an acquisition, an insolvency, a markdown, a headquarters that moved — and
that fact is worth publishing. Several of the entries below were more work than the records
that made it in.

**"Cannot be established" is a statement about evidence, not about the company.** It means
the register's [sourcing rules](UPDATING.md) could not confirm the figure: nobody on the
allowlist printed it, or what they printed measures something else, or the page that has it
cannot be opened. Some of the largest and best-known companies in German technology are in
that section. It is not a judgement that they are small, doubtful or unimportant, and it is
not a claim that they are *not* unicorns — only that this register will not print a number
it could not read.

A company qualifies only if all three of the [inclusion rules](UPDATING.md#inclusion-rules)
hold: German by founding **or** headquarters, currently independent and private, and a
publicly reported post-money valuation of at least $1B or €1B as reported. A company that
cannot be shown to satisfy all three does not go in the register — "cannot be established" is
a reason to leave a name out, the same as "exclude", not a softer form of inclusion.

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
is not a read at all. This batch extended the practice from publishers to *companies*:
quantum-systems.com 403s this crawler on every page, and its own funding release was
recovered from the archive and read. It did not rescue the entry, but it settled it.

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

## Include — written (batch 4, final)

| Company | HQ | Valuation as reported | Evidence |
|---|---|---|---|
| **Flix** | Munich | over $3bn, Jun 2021, Series G | [Company press release](https://corporate.flix.com/press_releases/flixmobility-raises-over-650m-in-funding-at-3b-valuation-planning-further-global-expansion/), [TechCrunch](https://techcrunch.com/2021/06/02/flixmobility-raises-650m-at-a-3b-valuation-to-double-down-on-buses-and-other-transport-in-the-us/) |
| **FINN** | Munich | over €1bn, Jun 2026, Series D | [Investor press release (Portage, lead)](https://portageinvest.com/blog/finn-raises-e140-million-and-achieves-unicorn-status/) |
| **CMBlu Energy** | Alzenau | over €1bn, Apr 2026, Series C initial close | [Company press release](https://www.cmblu.com/press-media/cmblu-surpasses-eu1b-unicorn-threshold-with-eu50m-initial-close-of-series-c-defining-baseload-infrastructure-for-ai-and-data-centers) |
| **Dash0** | New York (founded in Germany) | $1bn, Mar 2026, Series B | [Company press release](https://www.dash0.com/blog/dash0-raises-usd110m-series-b) |

Four, not the six or seven the queue implied. Two of the names this batch was sent to write
did not survive contact with their own sources; both are below.

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

## Cannot be established

No rule is shown to fail. The evidence the rules demand either does not exist or cannot be
reached, and each row names the single thing that would change that. **Several of these are
larger than anything in the register.** They are absent for want of a readable sentence, not
for want of standing.

| Company | HQ | What is missing, and what would settle it |
|---|---|---|
| **Quantum Systems** | Gilching, near Munich | Would be the largest entry in the register: $1.2bn Series D at "~$8 billion on a post-money basis" ([company press release, 2026-07-02](https://quantum-systems.com/news/quantum-systems-raises-1-2bn-series-d-to-accelerate-growth-and-scale-software-defined-autonomous-systems-across-air-land-and-sea/)). What is missing is the **crossing**, and this batch closed the last avenue for finding it. It became a unicorn at the €160m Series C of May 2025 and no allowlisted account prints that valuation as a numeral: [Sifted, 2025-05-06](https://sifted.eu/articles/quantum-systems-160m-unicorn) says only "making it one of only a few unicorns in the European defence tech field"; [EU-Startups, 2025-05-06](https://www.eu-startups.com/2025/05/german-quantum-systems-raises-e160-million-to-target-global-leadership-in-aerial-intelligence-solutions/) covers the identical round — same funding total, same lead, same day — and states neither a valuation nor even the word "unicorn"; eu-startups.com also 403s this crawler, so that page was read through a [Wayback snapshot](https://web.archive.org/web/20251206133222/https://www.eu-startups.com/2025/05/german-quantum-systems-raises-e160-million-to-target-global-leadership-in-aerial-intelligence-solutions) instead. [Tech.eu, 2025-11-28](https://tech.eu/2025/11/28/quantum-systems-180m-series-c-extension-lifts-company-to-3b/) and lead investor [Balderton](https://www.balderton.com/news/quantum-systems-triples-valuation/) both say the November extension "tripled its valuation" to "above €3 billion" without saying what it tripled *from*. quantum-systems.com 403s this crawler, so the company's own wording was previously unread — **that has now been fixed and it does not help**. The Series C release was recovered from the [Wayback Machine](https://web.archive.org/web/20250512124858/https://quantum-systems.com/au/2025/05/05/quantum-systems-raises-euro160m/) and read end to end: it gives the round (€160m), the investors, the total raised (€310m) and no valuation at all. Publishing it now would mean pointing `becameUnicorn` at November 2025 while knowing the company crossed in May — the exact error three published records were corrected for. **Settled by:** one allowlisted page printing the May 2025 figure as a numeral. Dividing €3bn by three is arithmetic, not a source |
| **Neura Robotics** | Metzingen | $1.4bn Series C, June 2026, backed by Tether, Qualcomm, Amazon and Nvidia. The $7bn everyone quotes reaches an allowlisted page only at third hand: [Sifted](https://sifted.eu/articles/neura-robotics-1-4bn-series-c) writes "The new funding brings Neura's valuation to $7bn, the Financial Times reported, citing people familiar with the deal", and Neura declined to comment on it. The company's own release ([2026-06-10](https://neura-robotics.com/record-series-c/)), opened and read in full, announces "a landmark Series C financing with a total round size of **up to** $1.4 billion" and states no valuation. A milestone-contingent round size plus an unconfirmed, anonymously-sourced number nobody calls a post-money is two known error shapes at once. Re-tried this batch: the FT is on the allowlist but ft.com is not reachable by this crawler, directly or through search, and no Wayback capture of the article was found. **Settled by:** the FT's own page becoming readable, or Neura stating a figure |
| **Raisin** | Berlin | Reported at over €2bn after a secondary in which existing holders sold more than €100m of stock to Tencent, Hedosophia and Vitruvian. Re-checked this batch: every route to that figure still runs through publications that are not on the allowlist. Note also that a secondary sets a price for shares changing hands rather than a post-money — the register can carry that (Trade Republic is published on one) but must label it as what it is. **Settled by:** any allowlisted publication printing the €2bn |
| **The Exploration Company** | Munich | Still in talks: $300m at more than $2bn, attributed to the FT and unconfirmed by the company, with the reporting itself cautioning that terms could move or the deal fall away. Re-checked in August 2026 and nothing has closed. One caveat on the re-check, stated rather than glossed: a Bloomberg item of 26 July 2026 appears to relay the same FT report, and **that page was not opened** — bloomberg.com 403s this crawler and the archive was rate-limiting at the time of the check — so it is not cited here and nothing is claimed about its contents. The entry rests on the reporting already read. Talks are not a post-money. **Settled by:** the round closing with a stated price |
| **Agile Robots** | Munich | The most recent allowlisted reporting is about a round that has not happened: Sifted's June 2026 piece is headlined "SoftBank in talks to back Agile Robots' $800m round, reports say". Talks are not a post-money. ([Sifted, 2026-06-02](https://sifted.eu/articles/softbank-in-talks-to-back-agile-robotics-in-800m-round-reports-say)) **Settled by:** the round closing with a stated price |
| **Isar Aerospace** | Munich (Ottobrunn) | Fails on the figure, not on obscurity. Its **own** release on the €270m Series D ([2026-06-09](https://isaraerospace.com/press/isar-aerospace-secures-eur-270m-to-provide-sovereign-space-capabilities-globally)) was opened and read end to end: round, investors, factory, headcount, no valuation anywhere. The €2bn everyone quotes traces to a Bloomberg piece whose own URL slug is `isar-aerospace-in-talks-to-raise-250-million-ahead-of-launch` — talks, and about a €250m round superseded by the larger €270m one that actually closed with no price attached. The archive was tried: all three Wayback captures of that URL are themselves HTTP 403 block pages. **Settled by:** any allowlisted page stating a post-money for a round that closed |
| **Grover** | Berlin | Tech.eu's own piece announcing unicorn status is careful about what the money was: "As tech rental platform Grover achieves unicorn status, it's also raised over $2 billion in funding, the vast majority of which is debt" — and, later, "To date, Grover has raised over $2 billion, 90% of which is debt funding." No post-money equity valuation appears anywhere in it. ([Tech.eu, 2022-04-07](https://tech.eu/2022/04/07/berlins-grover-hits-super-grover-status-with-unicorn-valuation-but/)) **Settled by:** an equity post-money, as distinct from cumulative funding |
| **Focused Energy** | Darmstadt | New to this file, and it arrived on a list of 2026's German unicorns. It does not clear rule 3. Its own release on the $240m Series A ([2026-05-27](https://www.focused-energy.co/news-release/focused-energy-sets-a-new-benchmark-240-million-for-the-largest-series-a-financing-in-the-global-fusion-industry)) was opened and read in full: it claims the round "makes it the most valuable fusion company in Europe" — a superlative, not a figure — and states no valuation. [TechCrunch's account](https://techcrunch.com/2026/06/02/focused-energy-raises-whopping-240m-series-a-for-laser-powered-fusion-tech/) of the same round, also read in full, contains no valuation either. Secondary write-ups put it "close to one billion dollars", which if accurate is *below* the threshold. **Settled by:** an allowlisted page stating a post-money at or above $1B/€1B |
| **Marvel Fusion** · **instagrid** · **Black Semiconductor** | — | Grouped because the gap is identical and the answer is the same. No allowlisted publication has printed a post-money at or above the threshold for any of the three, and their disclosed raises are an order of magnitude below the level at which one would be expected — Marvel Fusion's Series B extension runs to about €113m, Black Semiconductor's Series A to under $30m of equity. "Almost certainly below the threshold" is a good guess and this file does not publish guesses in either direction. **Settled by:** an allowlisted page stating a post-money |
| **Mambu** | — | The HQ limb verifiably fails: TechCrunch, opened and read, calls it "Amsterdam/London-based Mambu" at the €4.9bn Series E ([2021-12-09](https://techcrunch.com/2021/12/09/mambu-nabs-266m-at-a-5-5b-valuation-to-double-down-on-embedded-financial-service-and-banking-apis/)). The founding limb rests on a Berlin origin that no allowlisted publication states. Same shape as wefox, arrived at from the opposite direction. **Settled by:** an allowlisted or primary record of a German founding |
| **SumUp** | — | The gap is rule 1, not the figure. The HQ limb verifiably fails: TechCrunch, opened and read, calls it "the London-based company" in the same piece that reports its valuation ([2022-06-23](https://techcrunch.com/2022/06/23/sumup-raises-624m-at-8-5b-valuation-with-its-payments-and-business-tech-now-used-by-4m-smbs/): "values SumUp at €8 billion ($8.5 billion)") — a figure this file previously, and wrongly, characterised as debt rather than a post-money; the same sentence shows it is reported as the latter. That correction does not rescue the entry. The founding limb rests on a founding story no allowlisted publication states a location for. Same shape as Mambu, London standing in for Amsterdam. **Settled by:** an allowlisted or primary record of a German founding |

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
| **wefox** | Fails rule 1's headquarters limb, verifiably, and the founding limb is contested rather than established, so there is nothing left to qualify it on. wefox's own imprint gives "wefox Holding AG, Räffelstrasse 26, 8045 Zürich, Switzerland", "[e]ntered in the commercial register of the Canton of Zürich"; its own release of 31 July 2024, datelined Zurich, says "[t]hese two transactions largely complete the announced exit of wefox from the German market"; and its site now lists exactly three businesses — Austria, the Netherlands and Switzerland. The founding limb is all that could save it, and it is contested rather than settled: TechCrunch wrote "Founded out of Berlin in 2015" in July 2022 but "founded in 2014" in its own December 2019 piece, and wefox's own boilerplate says only "Founded in 2015", never where. The $4.5bn of May 2023 is real and sourced (TechCrunch, 2023-05-16: "Wefox managed to maintain the same valuation of $4.5 billion") but moot while rule 1 fails. Note separately that the €550m Bloomberg figure of 2024 settles nothing either way: it is an enterprise value for an offer the board rejected, so it is neither a post-money nor a completed transaction. **Settled by:** a primary record — a Handelsregister entry or a company statement — of where wefox was originally incorporated, which would revisit this against rule 1's founding limb rather than its headquarters. | [wefox imprint](https://www.wefox.com/imprint), [wefox exit release, 2024-07-31](https://www.wefox.com/press/wefox-successfully-completes-two-transactions-to-exit-the-german-market), [TechCrunch, 2022-07-11](https://techcrunch.com/2022/07/11/wefox-grabs-400m-at-4-5b-valuation-to-buck-the-insurtech-downturn-trend/), [TechCrunch, 2019-12-10](https://techcrunch.com/2019/12/10/wefox-unicorn/), [TechCrunch, 2023-05-16](https://techcrunch.com/2023/05/16/wefox-secures-new-funding-at-45-billion-valuation-as-it-aims-for-profitability/) |

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
   Energy** (both published in this batch), and **Focused Energy** (chased, and found to
   state no valuation — above). A paywalled list is a lead, never a source.
3. **Sifted's German "soonicorn" list**, which names the companies closest to the threshold
   from below: **Vivid** (excluded above, €775m), **Proxima Fusion** (since crossed;
   published in batch 3) and **Finn** (since crossed; published in this batch).

Everything those sweeps produced now appears somewhere above with a verdict: 25 rows carry
**include**, 19 carry **exclude**, and 13 carry **cannot be established** — every row settled,
none left as a placeholder. The register itself currently publishes 27 companies; the two not
yet written up as a row here (**n8n**, **Stark**) are named at the top of this file instead,
so the gap between what's published and what's written up is disclosed rather than silent.

One row above carries no headquarters city, and deliberately: Marvel Fusion, instagrid and
Black Semiconductor are excluded from the register on rule 3, so no page stating their
headquarters was opened, and this file does not fill a column from memory any more than a
record does.
