# Candidates

Every company considered for the register, with its status and the reason. Kept in the open
because the exclusions are as much a result as the inclusions — a name dropping off this list
is usually a fact (an IPO, an acquisition, an insolvency, a markdown), and the fact is worth
publishing.

A company qualifies only if all three of the [inclusion rules](UPDATING.md#inclusion-rules)
hold: German by founding **or** headquarters, currently independent and private, and a
publicly reported post-money valuation of at least $1B or €1B as reported.

**Status meanings**

| Status | Means |
|---|---|
| **include** | All three rules verified against a source that was opened and read. |
| **exclude** | One rule verifiably fails. The reason is recorded with its source. |
| **undecided** | Not yet checked against a current source. Never a judgement — only a queue. |

Last reviewed: **2026-08-08**.

**Blocked publishers.** Several allowlisted publications return 403 to an automated
fetch. That is not the same as unobtainable, and this file previously treated it as if it
were: three entries were parked on "Bloomberg 403s". **A publisher that blocks direct
fetching must be tried through a [Wayback Machine](https://web.archive.org) snapshot
before its reporting is recorded as unreadable.** Two of those three entries changed on
that check alone. Where a snapshot is used, the record still cites the publisher's own
canonical URL — the archive is how the page was read, not a second source, and a snapshot
that captured the publisher's own block page (HTTP 403) is not a read at all.

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

Five, not eight. The other three names in the queue did not clear the bar on evidence that
exists today, and each is left below with the exact sentence that is missing.

Notes carried into the records:

- **Two of the five crossed earlier than the round they are famous for**, which is the
  batch-1 Celonis error and the reason `postMoney` is now filled in wherever a source states
  one. **Enpal** is dated to a €2.2bn Series D of January 2023 in every list, but TechCrunch
  reported the October 2021 Series C close at "€950 million ($1.1 billion) post-money, the
  company has confirmed" — under the threshold in euros, over it in dollars, and the dollar
  figure is the source's own, not a conversion of ours. Sifted's January 2023 piece gives the
  game away in its own first line, calling Enpal a "solar unicorn" a year before the round
  the register would otherwise have credited. **Scalable Capital**'s crossing is named inside
  the very article that carries its published valuation: the December 2023 round was flat at
  $1.4bn because that "was the same valuation Scalable Capital had the last time it raised
  money — $180 million in 2021". The crossing is June 2021, not December 2023.
- **Proxima Fusion** carries a `disputed` note. Its own announcement and EU-Startups give
  €2.4bn; [Sifted](https://sifted.eu/articles/google-proxima-fusion-411m-raise) gives €2.5bn,
  same day, same round. The record publishes the company's own figure and shows Sifted's
  beside it. Note this is the opposite of what the batch-2 queue expected — the queue assumed
  Sifted's €2.5bn was the headline figure, because the company's own release had not been
  opened.
- **1KOMMA5°** carries a `disputed` note on the round rather than the valuation. The round is
  universally reported as €430m; the company's own release splits it into "215 million Euro
  in equity" plus "an additional 215 million Euro in re-participation options, which can be
  paid as part of the purchase price for new acquisitions". Only the first half is money
  raised. This is the Razor Group problem in a new costume — a headline number that measures
  something wider than the round — so the record publishes the equity and keeps €430m in the
  note.
- **sennder** carries a `disputed` note for the reverse reason: a €2bn figure is attached to
  it by a Tech.eu headline about a raise that was being *prepared* in December 2022 and never
  closed. Talks are not a post-money, as the Agile Robots entry below already says.
- **Two schema limits were hit and fixed** rather than worked around by dropping facts.
  `postMoneyCurrency` exists because Enpal's Series C was raised in euros and priced by its
  source in dollars; without it, 1100 would have had to be filed under EUR, a figure no
  source states. `postMoneySource` exists because 1KOMMA5°'s own release states the equity
  raised in one paragraph and the valuation in another, and one source per round would have
  forced the record to drop one of them. Neither relaxes a check: whichever source is named
  must still be allowlisted, dated, and carry a quote stating that figure in that currency.

## Include — verified, queued for a later batch

These meet all three rules, but the register cannot yet publish an honest record. In every
case the blocker is named precisely, so the next batch can act on it directly.

| Company | HQ | Why it qualifies | What blocks the record |
|---|---|---|---|
| **Quantum Systems** | Gilching, near Munich | The largest of them all: $1.2bn Series D at "~$8 billion on a post-money basis" ([company press release, 2026-07-02](https://quantum-systems.com/news/quantum-systems-raises-1-2bn-series-d-to-accelerate-growth-and-scale-software-defined-autonomous-systems-across-air-land-and-sea/)) | Still the **crossing**, not the valuation, and this batch could not shift it. It became a unicorn at the €160m Series C in May 2025; no allowlisted account prints that valuation as a numeral. Checked again and re-read this time: [Sifted, 2025-05-06](https://sifted.eu/articles/quantum-systems-160m-unicorn) says only "making it one of only a few unicorns in the European defence tech field"; [Tech.eu, 2025-11-28](https://tech.eu/2025/11/28/quantum-systems-180m-series-c-extension-lifts-company-to-3b/) and its lead investor's own release ([Balderton](https://www.balderton.com/news/quantum-systems-triples-valuation/)) both say the November extension "tripled its valuation" to "above €3 billion" but never state what it tripled *from*. Dividing €3bn by three would be arithmetic, not a source. quantum-systems.com returns 403 to this crawler on every page including its own Series C release, so the company's own wording cannot be read either. Needs one allowlisted page that prints the May 2025 figure |
| **Neura Robotics** | Metzingen | $1.4bn Series C, Jun 2026, backed by Tether, Qualcomm, Amazon and Nvidia | Weaker on a first-hand read than the queue expected, so it was left out rather than published thin. The company's own release ([2026-06-10](https://neura-robotics.com/record-series-c/)) — opened and read in full — announces "a landmark Series C financing with a total round size of **up to** $1.4 billion" and states **no valuation at all**. The $7bn reaches an allowlisted page only at third hand: [Sifted](https://sifted.eu/articles/neura-robotics-1-4bn-series-c) writes "The new funding brings Neura's valuation to $7bn, the Financial Times reported, citing people familiar with the deal", and contemporaneous reporting adds that Neura declined to comment on the figure. A milestone-contingent round size and an unconfirmed, anonymously-sourced number that nobody calls a post-money is two of the three known error shapes at once. Publishable only if the FT's own page can be opened, or if the company states a figure |
| **wefox** | Berlin | $4.5bn post-money at the May 2023 round ([TechCrunch](https://techcrunch.com/2023/05/16/wefox-secures-new-funding-at-45-billion-valuation-as-it-aims-for-profitability/)) | **Moved up from the exclusion list, but not on the reason first given here.** That reason — "no allowlisted publication has printed any valuation since 2023" — was wrong, and it was wrong because Bloomberg had been recorded as unreadable without trying the archive. Read through a Wayback snapshot, [Bloomberg, 2024-06-13](https://www.bloomberg.com/news/articles/2024-06-13/mubadala-favors-selling-fintech-wefox-against-founders-wishes) reports: "The Abu Dhabi sovereign wealth fund has told Wefox shareholders it expects an offer from Ardonagh that would give the German firm an **enterprise value** of as much as €550 million ($595 million), according to a presentation from Mubadala that was seen by Bloomberg." That figure does **not** settle wefox against rule 3, for the reason Razor Group and 1KOMMA5° already establish here: an enterprise value is not a post-money, and this one prices an *expected offer* in a sale the board went on to reject, not a completed round. So the €550m is neither a post-money nor a transaction. wefox is German, private, independent and not insolvent, and its last reported post-money is $4.5bn. **What would settle it either way is a post-money on a round since May 2023** — most obviously the €151m raised in 2025, for which no allowlisted source states a price |
| **Flix** | Munich | More than €3bn at the EQT / Kühne Holding transaction, Jul 2024 | **Settled by the archive, having been parked on "Bloomberg 403s".** Read through a Wayback snapshot, [Bloomberg, 2024-07-04](https://www.bloomberg.com/news/articles/2024-07-04/eqt-german-tycoon-buy-1-billion-stake-in-greyhound-owner-flix) reports: "They are investing around €1 billion ($1.2 billion) in Flix in a deal valuing the business at more than €3 billion, people with knowledge of the matter said." EQT's own release, opened and read, confirms the structure — a 35% stake, "[i]n addition to a primary investment in Flix … shares from existing shareholders" — and states no figure. Flix is Munich-based, private (its listing was shelved) and independent. Nothing blocks a record except the writing of one. Two things it must say plainly: the figure is attributed to people with knowledge of the matter rather than disclosed, and the deal is part primary and part secondary, so it prices the company at the transaction rather than being a clean post-money |

## Exclude — verified

| Company | Reason | Source |
|---|---|---|
| **HappyRobot** | The "Telekom-backed AI unicorn" from the August 2026 scan is headquartered in San Francisco and founded by a Spanish team. German by investor base only, which does not qualify. | [Gründerszene, 2026-08-07](https://www.businessinsider.de/gruenderszene/ki-startup-ist-jetzt-ein-unicorn-150-konzerne-nutzen-es-bereits/) |
| **Solaris** | No longer independent: SBI Holdings took a majority stake of more than 70% in the February 2025 Series G. | [Tech.eu, 2025-05-06](https://tech.eu/2025/05/06/solaris-co-founder-takes-legal-action-over-japanese-conglomerate-sbi-takeover/) |
| **Gorillas** | Acquired by Getir in December 2022. | [TechCrunch, 2022-12-09](https://techcrunch.com/2022/12/09/instant-grocery-app-getir-acquires-its-competitor-gorillas/) |
| **Flink** | Berlin quick commerce, once one of Germany's most valuable startups, raised $100m in March 2026 at a **$900m** valuation — below the threshold, so it is now a former unicorn rather than a current one. Sifted: "Speedy grocery startup Flink has raised $100m in funding, in a deal which reportedly values the Berlin-based company at $900m". | [Sifted, 2026-03-03](https://sifted.eu/articles/flink-100m-900m-valuation) |
| **EGYM** | The most surprising exclusion of this round. Munich's connected-fitness company was, on Handelsblatt's account, the *only* German startup to reach $1bn in 2024 — and it no longer exists as an independent company. It merged into Playlist, the American parent of ClassPass and Mindbody; the deal closed on 31 March 2026 and "EGYM will operate under Playlist alongside its other brands". Fails rule 2. | [TechCrunch, 2026-03-31](https://techcrunch.com/2026/03/31/the-company-behind-classpass-and-mindbody-just-got-a-lot-bigger-with-a-7-5b-merger/) |
| **Zalando**, **Delivery Hero**, **HelloFresh**, **Auto1**, **Ottobock** | Publicly listed, so not private. Ottobock is the most recent, listing in Frankfurt in October 2025. | Listed on the Frankfurt Stock Exchange |
| **About You** | Acquired by Zalando and delisted; no longer independent. | Zalando/About You combination completed 2025 |
| **Contentful** | The most surprising exclusion of this batch, and it was not on anyone's list of doubts. The Berlin-founded headless CMS closed a $175m Series F in 2021 at over $3bn — comfortably the largest valuation in the undecided pile — and it was **acquired by Salesforce**, announced 1 June 2026. Tech.eu: "Contentful, the German-founded content management company, is to be acquired by US software giant Salesforce, the companies announced today." The same piece notes it "closed a $175 million funding round in 2021, at a valuation of over $3 billion", so a company that would have entered the register near the top of it instead leaves at a reported discount to that price. Fails rule 2. | [Tech.eu, 2026-06-01](https://tech.eu/2026/06/01/berlin-based-contentful-snapped-up-by-salesforce/) |
| **Volocopter** | Insolvent: "German electric air taxi company Volocopter has filed for bankruptcy protection". Fails rule 2. (An earlier draft of this row added that proceedings opened at the Karlsruhe local court. The cited piece does not say so, and nothing else opened here does either, so the detail is gone and the exclusion stands on what the source states.) | [TechCrunch, 2024-12-30](https://techcrunch.com/2024/12/30/mercedes-backed-volocopter-files-for-bankruptcy/) |
| **Lilium** | Insolvent and wound down; TechCrunch's October 2025 piece describes it in the past tense as the "defunct electric aircraft startup" whose technology has ended up at Archer. Fails rule 2. | [TechCrunch, 2025-10-16](https://techcrunch.com/2025/10/16/defunct-electric-aircraft-startup-liliums-tech-lives-on-over-at-archer/) |
| **Cognigy** | Acquired by NiCE — "US customer service giant NICE has paid almost $1bn to acquire Düsseldorf-based Cognigy in what is Europe's biggest AI acquisition to date". Fails rule 2, and note the price is *below* the threshold in any case. | [Sifted](https://sifted.eu/articles/cognigy-sells-for-almost-1bn-in-europes-biggest-ai-acquisition-yet), [Tech.eu, 2025-07-28](https://tech.eu/2025/07/28/german-ai-startup-cognigy-hoovered-up-by-us-customer-service-firm-nice/) |
| **Tier Mobility** | Merged with Dott and the brand retired: "Tier becomes Dott following the merger of the two micromobility companies". No longer a standalone German company. Fails rule 2. | [TechCrunch, 2024-09-30](https://techcrunch.com/2024/09/30/tier-becomes-dott-following-the-merger-of-the-two-micromobility-companies/) |

## Exclude — pending a first-hand check

Believed not to qualify, but not yet settled against a page that was opened and read. The
list is much shorter than it was: **Volocopter, Lilium, Cognigy, Tier Mobility and
Contentful moved up to the verified table above**, and **wefox moved the other way** — the
reason given for excluding it turned out not to be a fact anyone has published.

| Company | Reason believed | What is still missing |
|---|---|---|
| **GoStudent** | Austrian, not German — fails the founding/HQ test | An allowlisted page stating the Vienna founding or HQ. Nothing about this is in doubt; it simply has not been opened |
| **Mambu** | Not German enough to pass rule 1 | Half-settled, and against the company. TechCrunch, opened and read, calls it "Amsterdam/London-based Mambu" at the €4.9bn Series E ([2021-12-09](https://techcrunch.com/2021/12/09/mambu-nabs-266m-at-a-5-5b-valuation-to-double-down-on-embedded-financial-service-and-banking-apis/)), so the HQ limb of rule 1 fails outright. The founding limb rests on a Berlin origin that no allowlisted publication states. It stays out until one does — the register does not fill that gap from memory |
| **SumUp** | Same shape as Mambu | Weaker again: no allowlisted page opened in this batch calls SumUp either German-founded or German-headquartered, and the €8bn figure most often quoted for it is attached to a debt financing, not a post-money. Two separate gaps, both real |

## Rule 3 not established — a unicorn label without a post-money

All three of these are routinely called German unicorns, and in each case the *figure* behind
the label turns out to be missing, to describe something else, or to belong to a round that
never happened. That is worth publishing on its own, so they sit here rather than in the
undecided queue.

| Company | HQ | What the source actually says |
|---|---|---|
| **Grover** | Berlin | Tech.eu's own piece announcing unicorn status is careful about what the money was: "As tech rental platform Grover achieves unicorn status, it's also raised over $2 billion in funding, the vast majority of which is debt" — and, later, "To date, Grover has raised over $2 billion, 90% of which is debt funding." No post-money equity valuation is stated anywhere in it. A subscription-rental company financing inventory with debt is not the same as a company valued above $1bn. ([Tech.eu, 2022-04-07](https://tech.eu/2022/04/07/berlins-grover-hits-super-grover-status-with-unicorn-valuation-but/)) |
| **Agile Robots** | Munich | The most recent allowlisted reporting is about a round that has not happened: Sifted's June 2026 piece is headlined "SoftBank in talks to back Agile Robots' $800m round, reports say". Talks are not a post-money. ([Sifted, 2026-06-02](https://sifted.eu/articles/softbank-in-talks-to-back-agile-robotics-in-800m-round-reports-say)) |
| **Isar Aerospace** | Munich (Ottobrunn) | Resolved this round, and it turns out to fail rule 3 rather than to be merely unread. Its **own** press release on the €270m Series D ([2026-06-09](https://isaraerospace.com/press/isar-aerospace-secures-eur-270m-to-provide-sovereign-space-capabilities-globally)) was opened and read end to end: round, investors, factory, headcount, and no valuation anywhere. The €2bn everyone quotes traces to Bloomberg's March 2026 piece, whose own URL slug is `isar-aerospace-in-talks-to-raise-250-million-ahead-of-launch` — talks, and about a €250m round that was superseded by the larger €270m one that actually closed three months later with no price attached. Talks are not a post-money, as Agile Robots above already establishes. The archive was tried, per the note at the top of this file, and does not rescue it either: all three Wayback captures of that Bloomberg URL are themselves HTTP 403 block pages, so there is no snapshot of the article to read |

## Undecided — queued for verification

Not yet checked against a source that was opened and read, or checked and found to have no
publishable figure. Listed so that the queue is visible and nothing is quietly dropped. For
each, the same three questions apply: German by founding or HQ, still independent and
private, and a publicly reported post-money at or above the threshold.

Raisin · Black Semiconductor · Marvel Fusion · instagrid · The Exploration Company

Notes on what specifically to settle:

- **Raisin** is reported at over €2bn after a secondary in which existing holders sold more
  than €100m of stock. Every route to that figure this batch could find runs through
  publications that are not on the allowlist. Note also that a secondary sets a price for
  shares changing hands, not a post-money — which the register can carry (Trade Republic is
  published on one) but should label as what it is.
- **The Exploration Company** is still "in talks": a $300m round at more than $2bn,
  attributed to the FT and unconfirmed by the company, with the reporting itself cautioning
  that the terms could move or the deal fall away. Talks are not a post-money.
- **Marvel Fusion**, **instagrid** and **Black Semiconductor** have all raised in the tens or
  low hundreds of millions. None is likely to clear the threshold, but "likely" is not a
  reason this file accepts, so they stay here until a source has been opened.
