# Brand — German Unicorns

How the site sounds and how it looks. `DESIGN.md` owns the visual system in full;
this file is the short version plus the rules about words, which live nowhere else.

## The line

> **Made in Germany. Built by startups.**

Three places, and no more:

1. the hero,
2. the heading over the Companies intro,
3. the close of a week's lead funding write-up, where it lands naturally.

It is a punchline. A punchline repeated on every block stops being one.

## Voice

Bullish, enthusiastic, professional. Confident and concrete.

- **Facts carry the weight, not adjectives.** "Eleven crossed a billion in the
  last twelve months" beats "extraordinary momentum". If a sentence needs
  "world-leading" or "revolutionary" to land, it has no number in it yet.
- **Short sentences.** The funding write-ups are the model: name the round, the
  lead investor, what the company actually does, and one number that puts it in
  context. Four or five sentences, then stop.
- **Never a claim the sources do not carry.** If a fact is not in that record's
  cited sources, it does not go in the copy. Leave it out and close the sentence
  up around the gap.
- **Answers are short.** The About page caps every answer at three sentences.
  That cap is the reason the page works.
- **Say what is missing.** An unknown is stated, never smoothed over. Undisclosed
  means undisclosed.

## Punctuation

Two hard bans, enforced by `tests/test_copy.py`:

- **No em dash (—).** Rewrite the sentence. A comma pair, a full stop, or a
  restructure. Do not substitute a different dash to get around it.
- **No semicolon.** Two sentences, or a conjunction.

Also:

- **Minimise colons.** One before a genuine list or a quotation is fine. A colon
  standing in for a verb is not.
- **En dash (–)** stays. It is the register's "no value" glyph and it sets date
  ranges ("20–26 Jul 2026") and spans ("A–Z").
- **Middle dot (·)** is the separator, in metadata rows, page titles and footers.

Two documented exceptions, both quotations:

- **Source titles are verbatim.** A publisher who put an em dash in their own
  headline wrote that headline. Editing it would falsify a citation on a site
  whose whole claim is that its citations are exact. New offenders are surfaced
  by `test_a_source_title_keeps_its_publishers_punctuation`, not silently allowed.
- **Source quotes are verbatim** and are not rendered anywhere, so the ban does
  not reach them.

## Visual identity

Near-black, cinematic, institutional. Full detail in `DESIGN.md`.

**Dark only, on purpose.** No light theme, no `prefers-color-scheme` branch, no toggle,
and none to be added later. The single light surface is `--plate`, which exists so
company logos sit on the white they were drawn for. If a light mode looks missing, it
was declined rather than forgotten.

| | |
|---|---|
| Page | `--void` `#07080B`, raised surfaces `--deep` |
| Text | `--ink` for prose, `--muted` for metadata and labels |
| Accent | `--beam` for graphics only, `--beam-text` for accent **text** |
| Gradient | `--beam-text` into `--violet`, on one phrase at a time |
| Signal | `--amber` for aged, disputed and undisclosed markers, never decoration |
| Display | Archivo, weight 800, `font-stretch: 112%`, tight tracking |
| Prose | Source Serif 4, for running argument only |
| Data | IBM Plex Mono, for every figure, label, date and stat |

Rules that get broken most often:

- **Glow is a signal.** Hover states and the €1bn marker. Never ambient.
- **One bold element per screen.** Everything else recedes.
- **Numbers are mono and always beside their date.**
- **Logos are never altered.**
- **Fonts are self-hosted.** Never a font CDN. The site carries an Impressum and
  German courts have ruled on this.
- **No third-party requests at all.** No analytics, no cookies, no external
  anything.

## Labels

- Detail window headings are `Problem` and `Technology and business model`.
  Not "The Problem".
- The freshness stat reads as a value with a label under it, like every other
  stat. Not a sentence stuffed into the value slot.
- Amber markers are qualifications on a figure, never errors. `aged`,
  `disputed`, `Undisclosed`, `>1bn`.
- `aged` is deliberately rare. See the rule and its reasoning at the top of
  `tools/build.py`.
