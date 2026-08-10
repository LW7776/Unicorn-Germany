# Design system — German Unicorns

Locked. This file supersedes `design-system/german-unicorns/MASTER.md`, whose generated
defaults (light background, pink accent, Orbitron) contradict the approved brief.

## Direction: Constellation

Near-black, cinematic, institutional. The constellation is the dataset — each point of
light is one company — and it becomes the grid in one continuous motion. That transition
is the signature; everything else stays quiet.

## Colour

**This site is dark only, and that is a decision, not an omission.** There is no light
theme, no `prefers-color-scheme` branch and no theme toggle, and none should be added.
The direction above is the reason: a constellation on a near-black field is the product,
and it does not survive being inverted. `--plate` and `--plate-ink` are the one light
surface, and they exist solely so company logos sit on the white they were drawn for.
Anyone reading this file because a light mode "seems to be missing" has found the answer.

| Token | Hex | Use |
|---|---|---|
| `--void` | `#07080B` | Page |
| `--deep` | `#0C0E14` | Raised surfaces |
| `--panel` | `rgba(255,255,255,.045)` | Glass cells over `--deep` |
| `--panel-hover` | `rgba(255,255,255,.075)` | Glass cells on hover |
| `--stroke` | `rgba(255,255,255,.10)` | Hairlines, cell borders |
| `--ink` | `#ECEEF3` | Primary text |
| `--muted` | `#9AA1B1` | Metadata and labels (4.5:1 on `--void`) |
| `--beam` | `#4C7DFF` | Graphics, particles, focus ring |
| `--beam-text` | `#8FB0FF` | Link and accent **text** only (4.5:1 on `--void`) |
| `--violet` | `#A97BFF` | Gradient partner; the €1bn marker |
| `--amber` | `#E0A24B` | Aged and disputed signals |
| `--plate` | `#F7F8FA` | The white plate logos sit on |
| `--plate-ink` | `#14161A` | Text on the white logo plate — the only token for light surfaces |

Two accents exist because `--beam` is a graphics colour and fails 4.5:1 as text. Never set
type in `--beam`.

**Blue and violet are the only accents, and amber is not a third one.** Amber carries every
caveat on the site — `aged`, `disputed`, `Undisclosed`, `>1bn` — and a second warm colour
used decoratively would make a reader work out which warm thing is a warning. If something
needs emphasis, reach for weight, size or space first.

## Depth

The page is layered rather than flat, and every layer is a new strength of a colour already
in the table above.

| Token | Made of | Use |
|---|---|---|
| `--ghost-ink` | `--ink` at 5% | The enormous `MADE IN GERMANY` set behind the hero |
| `--ambient-beam` | `--beam` at 8% | Pool one of the field behind the register |
| `--ambient-violet` | `--violet` at 6% | Pool two |
| `--glass-highlight` | `--ink` at 16% | The hairline catching the top edge of a stat card |
| `--plate-inset` / `--plate-inset-ring` | `--plate-ink` at 20% / 9% | Seats a logo plate into its card |

Two rules govern all of it. **A depth cue is never legible as a colour** — the moment one
reads as blue rather than as distance, it has started competing with the content in front of
it. And **each one is in `tools/check_contrast.py`**, because glass over both ambient pools
is the lightest surface any body text on this site is set against, and it still has to clear
4.5:1. Changing a percentage here means changing it there.

The hero's field also drifts, very slowly, painted on the constellation canvas rather than on
a second surface. The register's does not: something moving behind the figures is a different
proposition from something moving behind a headline.

## Type

- **Display — Archivo Variable**, width axis pushed wide (`font-stretch: 112%`), weight 700–800,
  tight tracking. Monumental and DIN-adjacent: this is industrial capital, not science fiction.
- **Prose — Source Serif 4**, used *only* for the problem and technology blocks. The serif is
  what makes the site read as reported rather than generated.
- **Data — IBM Plex Mono**, every figure, label, date, stat and timeline node.

Self-hosted `woff2`. Never the Google Fonts CDN — embedding it has been ruled a GDPR breach in
German courts, and this site carries an Impressum.

## Motion

Hand-rolled: Web Animations API and `requestAnimationFrame`. No GSAP, no dependency.
Micro-interactions 150–250ms `--ease-out`; the hero→grid FLIP ~1200ms. Under
`prefers-reduced-motion` the particle field stops painting and every transition becomes an
opacity fade. The CSS `prefers-reduced-motion` block cannot stop a JavaScript animation loop,
so the canvas particle field must check `matchMedia("(prefers-reduced-motion: reduce)")` itself
and skip scheduling its own `requestAnimationFrame` calls.

Three more pieces of motion, and what keeps each of them modest:

- **The hero headline** rises out of a blur, word by word, over 700ms, and **once a session**
  (`assets/js/hero.js`, `sessionStorage`). An arrival that happens every time you come back
  from the About page is a tic rather than an arrival.
- **Section reveals** (`assets/js/reveal.js`): fourteen pixels and one fade, once per element,
  never repeated on scroll-back. This is the effect most likely to make the site feel generic,
  so it is the one held tightest. The hidden starting state is CSS scoped to
  `prefers-reduced-motion: no-preference`, and every path that cannot animate — no observer, a
  throw, no JavaScript, printing — reveals everything instead.
- **Body copy is never animated.** Anywhere.

Verify reduced motion by counting, not by looking: with the media query forced, both
`requestAnimationFrame` and `Element.animate` must stay at zero across load and the register
transition.

## Discipline

Glow is a signal — hover, the €1bn marker — and it never attaches itself to an object that is
not signalling. The ambient field in Depth above is not an exception to this: it is a ground,
held below the threshold at which it could be mistaken for a highlight, and no element on the
page glows because of it. Logos are never altered. Numbers are always mono, always beside their
date. One bold element per screen; everything else recedes.

The gradient tint (`--beam-text` into `--violet`, on `.intro__accent`) belongs to exactly one
phrase, `Built by startups.` in the Companies intro. A signature used twice is a habit, and
`tests/test_pages.py` counts the declarations so a second one cannot arrive quietly.
