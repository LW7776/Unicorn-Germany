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

## Include — verified, queued for a later batch

These meet all three rules, but the register cannot yet publish an honest record. In every
case the blocker is named precisely, so the next batch can act on it directly.

> **Three of these are no longer blocked.** `validate.py` used to reject any record whose
> `valuation.asOf` predated its most recent round, on dates alone. That is right when the
> newer round disclosed a price — the record would be showing a superseded figure — but wrong
> when it disclosed none, which is ordinary and honest: the company raised and said nothing
> about valuation, so the last publicly reported figure genuinely is still the earlier one.
> The check now fires only when a round *after* the valuation carries a post-money of its own.
> **Enpal, Scalable Capital and 1KOMMA5° were queued solely behind that check and are now
> writable — batch 3 should pick them up first, after Proxima Fusion.** Nothing about their
> evidence changed; the rule did.

| Company | HQ | Why it qualifies | What blocks the record |
|---|---|---|---|
| **Proxima Fusion** | Munich | €411m round, Jul 2026, Max Planck stellarator spin-out. Sifted: "Munich-headquartered Proxima Fusion has raised €411m at a €2.5bn valuation in a round led by XTX Ventures and East X Ventures" ([Sifted, 2026-07-07](https://sifted.eu/articles/google-proxima-fusion-411m-raise)) | Nothing — but it arrived after this batch's eight were written. Note that [EU-Startups](https://www.eu-startups.com/2026/07/largest-european-fusion-investment-on-record-sees-proxima-fusion-raise-e411-million/) gives the same round at **€2.4bn** where Sifted gives **€2.5bn**: a genuine conflict between two allowlisted publications, so the record needs a `disputed` note |
| **Quantum Systems** | Gilching, near Munich | Now the largest of them all: $1.2bn Series D at "~$8 billion on a post-money basis" ([company press release, 2026-07-02](https://quantum-systems.com/news/quantum-systems-raises-1-2bn-series-d-to-accelerate-growth-and-scale-software-defined-autonomous-systems-across-air-land-and-sea/)) | The **crossing**, not the valuation. It became a unicorn at the €160m Series C in May 2025, but every allowlisted account of that moment states the figure in words rather than digits — Handelsblatt, "mit mehr als einer Milliarde Dollar bewertet"; Gründerszene, "mehr als einer Milliarde Dollar"; [Sifted](https://sifted.eu/articles/quantum-systems-160m-unicorn), "hits unicorn status" with no figure at all. A quote with no numeral cannot carry a post-money, so the record would have to date the crossing to the November 2025 extension — which is the batch-1 Celonis error again. Needs one source that prints the May 2025 valuation as a number |
| **Enpal** | Berlin | €2.2bn at the €215m Series D ([Sifted, 2023-01-09](https://sifted.eu/articles/enpal-215m-solar-panels-news)) | **Unblocked — writable now.** The April 2025 €110m round postdates the valuation, but [Sifted](https://sifted.eu/articles/enpal-e110m-tpg-equity) records that "Enpal declined to comment on the valuation the round gives the company", so it discloses no post-money and no longer bars the record. Publish €2.2bn as of Jan 2023, with the April 2025 round carrying `postMoney: null`; the aged badge will mark the gap |
| **1KOMMA5°** | Hamburg | Unicorn at 23 months on a €430m Series B, "valued at over $1 billion" ([Tech.eu, 2023-06-23](https://tech.eu/2023/06/23/hamburg-s-1komma5-has-raised-430-million-and-just-become-a-unicorn-at-just-23-months-old/)) | **Unblocked — writable now.** Same shape as Enpal: the €150m pre-IPO round closed Dec 2024 and was extended Jul 2025, but [Sifted](https://sifted.eu/articles/1komma5-e150m-pre-ipo-news) reports "a slight increase in valuation" and that the company "did not disclose an updated figure" — no post-money, so no bar |
| **Scalable Capital** | Munich | Flat $1.4bn at the Dec 2023 round ([TechCrunch](https://techcrunch.com/2023/12/06/european-neobroker-scalable-capital-raises-65m-on-a-flat-1-4b-valuation/)) | **Unblocked — writable now.** The €155m June 2025 round — its largest — postdates the valuation, but neither the company nor [EU-Startups](https://www.eu-startups.com/2025/06/german-startup-scalable-capital-receives-e155-million-to-continue-to-expand-its-digital-investment-platform/) gives a figure for it, so it discloses no post-money and no longer bars the record |
| **Neura Robotics** | Metzingen | $1.4bn Series C, Jun 2026, backed by Tether, Qualcomm, Amazon and Nvidia | Both headline numbers are soft. The company's own release calls it a round "of **up to** $1.4 billion", and the only valuation reaches an allowlisted page second-hand: [Sifted](https://sifted.eu/articles/neura-robotics-1-4bn-series-c) — "The new funding brings Neura's valuation to $7bn, the Financial Times reported, citing people familiar with the deal." Publishable, but only with the sourcing chain shown; worth one more attempt at a first-hand figure |
| **Isar Aerospace** | Munich (Ottobrunn) | €270m Series D closed Jun 2026 ([Sifted, 2026-06-09](https://sifted.eu/articles/isar-aerospace-raises-e270m-to-scale-launch-operations)) | Still no allowlisted post-money. Neither the company release nor Sifted states one, and Bloomberg — which is on the allowlist — returns 403 to this crawler, so its March 2026 piece cannot be opened and therefore cannot be cited |
| **sennder** | Berlin | Crossed $1bn on a $160m round in January 2021 | The rule no longer blocks it — the newer raise never closed, so nothing later discloses a post-money: [Tech.eu (2022-12-14)](https://tech.eu/2022/12/14/sennder/) reports sennder "**taking on** funds at around double the $1 billion or so value it received for equity issued January 2021". What is still missing is first-hand reading: the January 2021 source has not been opened, so its quote cannot yet be cited |

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

## Exclude — pending a first-hand check

Widely reported as no longer qualifying, but recorded here only from search results rather
than from a page opened and read. Each needs one allowlisted source before the reason above
is treated as settled.

| Company | Reason believed |
|---|---|
| **wefox** | Marked down far below its 2022 peak after warning shareholders of insolvency risk in 2024 and restructuring; no current valuation at or above the threshold |
| **Volocopter** | Insolvency proceedings opened at Karlsruhe in December 2024 |
| **Lilium** | Filed for insolvency a second time in February 2025 after the rescue funding failed; operations stopped |
| **Cognigy** | Acquired by NiCE, closed September 2025 |
| **Tier Mobility** | Combined with Dott; no longer standalone |
| **GoStudent** | Austrian, not German — fails the founding/HQ test |
| **Mambu**, **SumUp**, **Contentful** | Headquarters and founding country both need establishing before either rule can be applied |

## Rule 3 not established — a unicorn label without a post-money

Both of these are routinely called German unicorns, and for both the *figure* behind the
label turns out to be missing or to describe something else. That is worth publishing on its
own, so they sit here rather than in the undecided queue.

| Company | HQ | What the source actually says |
|---|---|---|
| **Grover** | Berlin | Tech.eu's own piece announcing unicorn status is careful about what the money was: "As tech rental platform Grover achieves unicorn status, it's also raised over $2 billion in funding, the vast majority of which is debt" — and, later, "To date, Grover has raised over $2 billion, 90% of which is debt funding." No post-money equity valuation is stated anywhere in it. A subscription-rental company financing inventory with debt is not the same as a company valued above $1bn. ([Tech.eu, 2022-04-07](https://tech.eu/2022/04/07/berlins-grover-hits-super-grover-status-with-unicorn-valuation-but/)) |
| **Agile Robots** | Munich | The most recent allowlisted reporting is about a round that has not happened: Sifted's June 2026 piece is headlined "SoftBank in talks to back Agile Robots' $800m round, reports say". Talks are not a post-money. ([Sifted, 2026-06-02](https://sifted.eu/articles/softbank-in-talks-to-back-agile-robotics-in-800m-round-reports-say)) |

## Undecided — queued for verification

Not yet checked against a source that was opened and read. Listed so that the queue is
visible and nothing is quietly dropped. For each, the same three questions apply: German by
founding or HQ, still independent and private, and a publicly reported post-money at or above
the threshold.

Raisin · Flix · Black Semiconductor · Marvel Fusion · instagrid · The Exploration Company

Notes on what specifically to settle:

- **Flix** remains private and shelved its 2024 listing, but EQT and Kühne Holding are
  reported to have taken a 35% minority stake in 2024. If that is right, it postdates the
  $3bn valuation of June 2021 and the register would need a figure attached to the stake
  sale itself. Neither has been read first-hand yet.
- **The Exploration Company** appeared on Sifted's own sidebar during this review as
  "Bessemer, Atomico in talks to lead The Exploration Company funding at $2bn valuation" —
  a headline seen, not an article read, and "in talks" in any case.
- **Marvel Fusion**, **Proxima Fusion**'s smaller German fusion and hardware peers,
  **instagrid** and **Black Semiconductor** have all raised in the tens or low hundreds of
  millions. None is likely to clear the threshold, but "likely" is not a reason this file
  accepts, so they stay here until a source has been opened.
- **Raisin** last had a €60m round reported in March 2023 with no valuation attached to it in
  the search results; the question is whether any post-money has ever been published.
