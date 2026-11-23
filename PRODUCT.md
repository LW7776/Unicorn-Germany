# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Founders and the German startup scene. Someone arrives tracking who crossed a billion, who
raised money last week, and where the money is going. They are scanning for movement and
recency rather than looking up one company, which means the weekly funding ledger outranks the
register in importance even though the register is the larger dataset.

Journalists, researchers and investors are real secondary readers and the sourcing discipline
is what makes the register usable to them, but the first screen is not designed for them.

## Product Purpose

A free public register of Germany's currently private companies valued at a billion euros or
more, alongside a weekly record of German funding rounds. It exists because Germany's
billion-euro companies sit behind paywalled databases and scattered press releases, and no
public list carries its evidence with it. Success is that a reader can check any figure on the
site against a public, dated page without asking anyone to take it on trust.

## Positioning

**Every figure traces to a dated, public page, and a validator refuses to publish a number
unless the quote behind it states that number.** Other trackers of German unicorns publish
estimated valuations, which is why their counts run higher. This register publishes only
figures somebody published, marks what it cannot verify rather than hiding it, and keeps the
evidence attached to the number on the page rather than in a methodology note.

That is the claim a neighbouring tracker could not truthfully copy without rebuilding its
dataset, because it is enforced mechanically rather than asserted.

## Operating Context

- The dataset is a Git repository, one JSON file per company and one per week, so every
  correction is a readable diff with an author and a date.
- Research and drafting are done with an AI assistant. The operator reviews every change
  before it is published. Nothing is published on a schedule.
- A scheduled scan reads allowlisted feeds each Monday and opens an issue saying there is work
  to do. It publishes nothing. Every eighth week it also sweeps the register for changes no
  funding wire reports, such as a company listing, being acquired, or going quiet.
- `admin.html` is a local form editor that mirrors the validator's rules in the browser. It
  never writes to the repository.

## Capabilities and Constraints

- **Zero build step.** Hand-written HTML, CSS and vanilla ES modules. No framework, no
  bundler, no server. Served as static files from the repository root by GitHub Pages.
- **Python computes, JavaScript renders.** Every label, percentage, sort key, derived figure
  and staleness flag is settled in `tools/build.py`. Browser code stays thin and does no
  arithmetic on published figures.
- **Fail-closed validation.** `tools/validate.py` is the only gate that can block a publish.
  `quote_states_figure()` requires a verbatim quote to state the figure, with digit-boundary
  matching, so a figure spelled out in words or attributed to an unallowlisted paper cannot be
  published as the number.
- **Fonts must be self-hosted woff2.** Embedding the Google Fonts CDN has been ruled a GDPR
  breach in German courts and this site carries an Impressum.
- **No em dashes and no semicolons** anywhere in user-facing copy. Enforced by
  `tests/test_copy.py`.
- **Company logos are never altered.** No recolouring, cropping, masking or redrawing. Where
  a company publishes only a light-on-dark mark, a smaller official mark is used instead of an
  edited one.
- Two publication tiers: `verified` and `reported`. A reported company is one an outside count
  treats as a unicorn where this register's standard could not be met. Reported entries are
  shown, marked, excluded from the combined value and counted separately.
- Three inclusion rules, all of which must hold: German by founding or headquarters, currently
  independent and private, and publicly reported to be worth at least one billion dollars or
  euros.
- The weekly ledger runs a deliberately lighter standard than the register: every round
  linked, dated and from an allowlisted publication, but not quote-checked. The two standards
  live behind separate validators so neither can quietly become the other.
- A week's `more` list is capped at five rounds so a week stays readable.
- 293 pytest tests, two contrast checks and both validators run on every push and pull request.

## Brand Commitments

- Name: German Unicorns.
- **Language is English, deliberately and durably.** The audience is international. German
  appears only inside verbatim source quotes, which are never translated and never tidied.
- The operator is named on the site and reachable: Lan Lukas Welge, Berlin, with a public
  issue tracker. Corrections are treated as the point rather than an inconvenience.
- The voice is plain and factual, and says what is not known as readily as what is.

## Evidence on Hand

- 40 company records in `data/companies/`, 37 verified and 3 reported, each with its sources,
  verbatim quotes and publication dates.
- 16 weekly funding files in `data/funding/`, 74 rounds.
- 36 company logo files in `assets/logos/`, each recorded in that folder's README with the
  exact URL it came from, the date retrieved, and any deviation.
- `docs/CANDIDATES.md`: every company considered, with its verdict and the evidence behind it.
  37 include, 3 reported, 23 exclude, 6 cannot be established.
- **No photography of any kind, and none is to be invented or licensed.** Stock imagery would
  contradict the register's own standard. Company logos are the only imagery on the site.
- No testimonials, no customers, no usage figures, no press coverage of the site itself. None
  of these are to be fabricated.

## Product Principles

1. **No number without its date and its proof.** A figure on this site always carries when it
   was true and a link to the page that states it. This survives any redesign.
2. **Say what is not known.** Undisclosed, disputed, aged and reported are published as
   markers rather than resolved silently or omitted. A gap stated is worth more than a gap
   filled.
3. **The machine says there is work to do, a person does it.** Nothing is published without
   review, and no machine-generated list of rounds has ever been published here.
4. **Recency is the reason to return.** The reader comes back for what moved this week, so the
   newest thing must be the easiest thing to find.
5. **Corrections are the product working, not the product failing.**

## Accessibility & Inclusion

WCAG AA is the binding floor: every text token clears 4.5:1 against every surface it is set
on, enforced by `tools/check_contrast.py` in CI rather than by inspection. Motion honours
`prefers-reduced-motion` by not scheduling animation at all rather than by shortening it, and
that is verified by counting `requestAnimationFrame` and `Element.animate` calls rather than
by looking at the page.
