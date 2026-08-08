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

## Include — verified, queued for a later batch

| Company | HQ | Why it qualifies | Still needed |
|---|---|---|---|
| **Quantum Systems** | Munich | Reached unicorn status with a €160m Series C in May 2025 ([Sifted](https://sifted.eu/articles/quantum-systems-160m-unicorn)); EU-Startups reports a later €180m extension above €3bn | A quotable sentence carrying the valuation figure — the Sifted piece states the company did not disclose one |
| **Isar Aerospace** | Munich (Ottobrunn) | Independent, private, €270m Series D closed Jun 2026 ([company press release](https://isaraerospace.com/press/isar-aerospace-secures-eur-270m-to-provide-sovereign-space-capabilities-globally)) | The press release states no valuation; an allowlisted source for the post-money is still missing |
| **Black Forest Labs** | Freiburg | German-founded AI image-model company, reported at a $3.25bn post-money in Dec 2025 | The reporting found so far is on excluded publications; needs an allowlisted source |

## Exclude — verified

| Company | Reason | Source |
|---|---|---|
| **HappyRobot** | The "Telekom-backed AI unicorn" from the August 2026 scan is headquartered in San Francisco and founded by a Spanish team. German by investor base only, which does not qualify. | [Gründerszene, 2026-08-07](https://www.businessinsider.de/gruenderszene/ki-startup-ist-jetzt-ein-unicorn-150-konzerne-nutzen-es-bereits/) |
| **Solaris** | No longer independent: SBI Holdings took a majority stake of more than 70% in the February 2025 Series G. | [Tech.eu, 2025-05-06](https://tech.eu/2025/05/06/solaris-co-founder-takes-legal-action-over-japanese-conglomerate-sbi-takeover/) |
| **Gorillas** | Acquired by Getir in December 2022. | [TechCrunch, 2022-12-09](https://techcrunch.com/2022/12/09/instant-grocery-app-getir-acquires-its-competitor-gorillas/) |
| **Flink** | The most surprising exclusion. Berlin quick commerce, once one of Germany's most valuable startups, raised roughly $100m in March 2026 at a **$900m** valuation — below the threshold, so it is now a former unicorn rather than a current one. | Reported by [Bloomberg, 2026-03-03](https://www.bloomberg.com/news/articles/2026-03-03/flink-raises-funds-at-higher-valuation-following-delivery-slump); the figure needs re-confirming against the article body before it is quoted anywhere |
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

## Undecided — queued for verification

Not yet checked against a current source. Listed so that the queue is visible and nothing is
quietly dropped. For each, the same three questions apply: German by founding or HQ, still
independent and private, and a publicly reported post-money at or above the threshold.

Enpal · 1Komma5° · Raisin · sennder · Forto · Choco · Taxfix · Grover · Agile Robots ·
Scalable Capital · commercetools · Staffbase · EGYM · Razor Group · Flix · Black Semiconductor ·
Osapiens · Marvel Fusion · Proxima Fusion · Neura Robotics · instagrid · The Exploration Company

Two of these deserve a note:

- **Flix** shelved its 2024 listing plans and remains private, so the question is only whether
  a post-money at or above the threshold has been publicly reported and when.
- **Osapiens** (Mannheim) was reported as Germany's first new unicorn of 2026 and should be
  checked early.
