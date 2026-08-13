# German Unicorns design system

A portable specification of the system behind [lw7776.github.io/Unicorn-Germany](https://lw7776.github.io/Unicorn-Germany/).
Everything here is what the site actually ships, not an aspiration: the hex values, the
clamps, the ratios and the component anatomies are lifted from `assets/css/tokens.css` and
the stylesheets beside it.

Use this as the input when extending the system or building a new surface for it. Where a
rule is stated as a prohibition, the prohibition is the point.

---

## 1. The subject

A public register of every German company valued above one billion, plus a weekly record of
German funding rounds. Its distinguishing claim is evidential: **no figure appears without
the date it was true and a link to the page that reports it.** The audience is founders,
investors and journalists who will check.

That claim is the design brief. A reader should be able to tell, at a glance, that this was
compiled rather than generated.

**Direction: Constellation.** Near-black, cinematic, institutional. Industrial capital, not
science fiction.

---

## 2. The signature: the sourced figure

One repeated unit carries the whole identity. It appears wherever a number appears, at three
sizes, and nowhere else.

```
$18 bn              value    mono, the largest thing in its box, tabular-nums
──────────────      rule     1px, --rule, full width of the unit
Jul 2026 · ↗        meta     --step--1, --muted, the date then the link
```

| Size | Value type | Where |
|---|---|---|
| Large | display face, `--step-4` | The two headline figures in the summary row |
| Medium | mono, `--step-1` | A grid card's valuation |
| Small | mono, `--step-0` | A round in the weekly ledger |

**Rules.**

1. The value is mono and `--ink`. The meta line is `--step--1` and `--muted`. Never the
   reverse.
2. The rule is a hairline. It joins the value to its date, and that is its only job. A rigid
   repeated unit executed loosely stops being a signature and becomes a table.
3. Figures always use `font-variant-numeric: tabular-nums`, so a column of them lines up and
   a rebuild that changes 32 to 33 does not shift the label under it.
4. On a **card** the link goes to the company's own site: a card is an index. On a
   **detail surface** the evidence is reachable in the source list. Never present a
   navigational link as if it were a citation.
5. A figure nobody published prints the word `Undisclosed`, one type step down and in
   `--muted`, with an amber `>1bn` marker beside it. Never a zero, never a dash, never an
   empty box.

---

## 3. Colour

**This system is dark only, and that is a decision.** There is no light theme, no
`prefers-color-scheme` branch and no toggle. A constellation on a near-black field is the
product and it does not survive inversion. `--plate` and `--plate-ink` are the one light
surface and exist solely so company logos sit on the white they were drawn for.

### Base

| Token | Value | Use |
|---|---|---|
| `--void` | `#07080B` | Page ground |
| `--deep` | `#0C0E14` | Raised surfaces, dialogs |
| `--panel` | `rgba(255,255,255,.045)` | Cards over the ground |
| `--panel-hover` | `rgba(255,255,255,.075)` | The same on hover |
| `--stroke` | `rgba(255,255,255,.10)` | Hairlines and card borders |
| `--ink` | `#ECEEF3` | Primary text |
| `--muted` | `#9AA1B1` | Metadata, labels, captions |
| `--beam` | `#4C7DFF` | Graphics, particles, focus ring, bar fills |
| `--beam-text` | `#8FB0FF` | Link and accent **text** only |
| `--violet` | `#A97BFF` | Gradient partner, the crossing marker |
| `--amber` | `#E0A24B` | Every caveat: aged, disputed, undisclosed, `>1bn` |
| `--plate` | `#F7F8FA` | The white plate a logo sits on |
| `--plate-ink` | `#14161A` | Text on the plate, and nowhere else |

### Depth

Every depth cue is a new *strength* of a colour already above, never a new hue.

| Token | Made of | Use |
|---|---|---|
| `--rule` | `--ink` at 16% | The hairline under a figure |
| `--track` | `--ink` at 7% | The unfilled part of a threshold bar |
| `--ghost-ink` | `--ink` at 5% | The oversized wordmark behind the hero |
| `--ambient-beam` | `--beam` at 8% | Pool one of the field behind the register |
| `--ambient-violet` | `--violet` at 6% | Pool two |
| `--plate-inset` / `--plate-inset-ring` | `--plate-ink` at 20% / 9% | Seats a logo plate into its card |

Two rules govern them. **A depth cue is never legible as a colour.** The moment one reads
as blue rather than as distance it has started competing with the content. And each one is
carried in the contrast checker, because glass over both ambient pools is the lightest
surface any body text meets.

### Colour rules

- **Two accents, blue and violet. Amber is not a third.** Amber carries every caveat on the
  site. A second warm colour used decoratively would make a reader work out which warm thing
  is a warning.
- **Never set type in `--beam`.** It fails 4.5:1 as text. That is why `--beam-text` exists.
- **Glow is a signal**, meaning hover or the crossing marker, and it never attaches to an
  object that is not signalling.
- If something needs emphasis, reach for weight, size or space before colour.
- The gradient tint (`--beam-text` into `--violet`, `background-clip: text`) belongs to
  **exactly one phrase on the site**. A signature used twice is a habit. This is enforced by
  a test that counts the declarations.

---

## 4. Typography

Three faces, three jobs. Self-hosted `woff2`, never a font CDN.

| Role | Face | Applies to |
|---|---|---|
| Display | **Archivo Variable**, weight 700–800, `font-stretch: 112%`, tracking `-.02em`, line-height `.95` | Headings, the wordmark, the two headline figures |
| Prose | **Source Serif 4**, 300–700, line-height 1.6 | Running argument only: thesis blocks, write-ups, long-form answers |
| Data | **IBM Plex Mono**, 400 | Every figure, label, date, stat, timeline node, and the body default |

The serif is what makes the site read as reported rather than generated. It is never used
for a label, a figure or a date, and the mono is never used for a paragraph of argument.

### Scale

Fluid, `clamp(min, preferred, max)`, and nothing outside it.

| Token | Value | Use |
|---|---|---|
| `--step--1` | `clamp(.75rem, .72rem + .15vw, .8125rem)` | Labels, metadata, captions |
| `--step-0` | `clamp(.9375rem, .9rem + .2vw, 1rem)` | Body |
| `--step-1` | `clamp(1.125rem, 1rem + .4vw, 1.375rem)` | Card figures, lead-in prose |
| `--step-2` | `clamp(1.5rem, 1.25rem + .9vw, 2rem)` | Section headings |
| `--step-3` | `clamp(2rem, 1.5rem + 2vw, 3rem)` | Dialog titles |
| `--step-4` | `clamp(2.75rem, 1.8rem + 4vw, 5rem)` | Page titles, headline figures |
| `--step-5` | `clamp(2.5rem, 1.5rem + 4.6vw, 5.5rem)` | Section openers |
| `--step-6` | `clamp(2.5rem, .5rem + 6.5vw, 5.75rem)` | The hero statement |

### The label

One shared treatment for every eyebrow, field label and section marker:

```css
font-size: var(--step--1);
letter-spacing: .14em;
text-transform: uppercase;
color: var(--muted);
```

Always mono, even on a page whose running text is serif.

---

## 5. Space, shape, layout

```
--space-1  .25rem     --space-5  1.5rem
--space-2  .5rem      --space-6  2rem
--space-3  .75rem     --space-7  3rem
--space-4  1rem       --space-8  5rem
--radius   14px       (10px for nested surfaces: plates, tiles)
--content  84rem      one content width for every block on the site
```

**One measure, held.** Every block, whether the register, the weekly round-up, the footer or
a static page, is capped at `--content` and centred, with a `--space-6` gutter inside. The reading measure is
held on the *text* (44rem for a Q&A column, 38rem for legal prose), never by giving a
section a narrower container. Section openers are the only elements allowed past the
measure, because a headline is not read a line at a time.

`--content` is a border-box width, so a block's own gutter sits inside it. Anything aligning
to the content column from outside (a fixed header) must add that gutter itself:

```css
padding-inline: max(var(--space-6), calc((100% - var(--content)) / 2 + var(--space-6)));
```

**Breakpoints**, used sparingly and always as a layout decision rather than a device:

| Width | What changes |
|---|---|
| 480px | Grid to one column, nav wraps to its own row, gutters to `--space-4` |
| 560px | Ledger rows collapse from two columns to one |
| 600px | Dialogs go to 96vw with tighter padding |
| 992px (62rem) | The section lede sets in two columns |

Layout is grid or flex with `gap`, never per-element margins that collapse or double. Wide
content gets `overflow-x: auto` on its own container so the page body never scrolls
sideways.

---

## 6. Motion

Hand-rolled: Web Animations API and `requestAnimationFrame`. No animation library.

| Token | Value | Use |
|---|---|---|
| `--dur-fast` | 180ms | Colour and border changes |
| `--dur-med` | 240ms | A hover that travels: a card lifting, a halo swelling |
| `--dur-slow` | 1200ms | Reserved for the page-scale move |
| `--ease-out` | `cubic-bezier(.22, 1, .36, 1)` | Anything arriving |

**Set pieces.**

- **Hero to register**, 820ms, `cubic-bezier(.65, 0, .35, 1)`. The hero and the content are
  locked to one distance, one duration and one curve, so it reads as the page travelling
  upward by exactly one screen. Symmetric ease-in-out, not `--ease-out`: an ease-out is
  right for something arriving from nowhere and jumps on the first frame for something
  already on screen.
- **Headline arrival**, word by word out of a blur, 700ms, **once a session**. An arrival
  that happens on every visit is a tic.
- **Section reveals**, fourteen pixels and one fade, once per element, never repeated on
  scroll back. This is the effect most likely to make a site feel generic, so it is the one
  held tightest.
- **Body copy is never animated.** Anywhere.

**The reduced-motion contract.** A CSS media query cannot stop a JavaScript loop, so every
animated module checks `matchMedia("(prefers-reduced-motion: reduce)")` itself and skips
scheduling. Verify by counting, not by looking: with the query forced, both
`requestAnimationFrame` and `Element.animate` must stay at zero across load and navigation.

Any element hidden for a reveal must have a path that reveals it when the animation cannot
run, whether that is a missing observer, a thrown error, no JavaScript at all, or printing.

---

## 7. Components

### 7.1 Logo plate

The one light surface. Grid, centred, `--plate` ground, 10px radius, `--space-4` padding,
seated into its card with `inset 0 1px 3px --plate-inset` and a `--plate-inset-ring`
hairline. Inside a card it takes an **exact height** (5.5rem), not a minimum: some logos
have no intrinsic aspect ratio and resolve a fraction taller, which is enough to put a card
out of step with its neighbours.

**Logos are never altered.** No recolouring, no monochrome treatment, no mask.

### 7.2 Grid card

The register's unit. Every card is exactly the same height and every row inside it sits at
the same offset as the equivalent row in every other card.

```
┌────────────────────────┐
│ [ logo plate ]         │  exact 5.5rem
│ €12.5 bn        aged   │  figure + optional markers, one line
│ ────────────────────── │  --rule
│ Dec 2025               │  as-of date, one line
│ traderepublic.com ↗    │  the company's own site, one line
│ ▓▓▓▓▓▓▓░│░░░░░░░░░░░░  │  threshold bar, 3px
│ Fintech           2021 │  sector and crossing year
└────────────────────────┘
```

Rules that keep it uniform, and each of them was a real bug:

- Every text row is **one line tall**. Text that will not fit is cut with an ellipsis, never
  wrapped. A card that wraps is taller than the one beside it and the grid stops being a
  grid.
- The figure row carries a `min-height` of a full-size line, so a value set one step down
  does not shorten it.
- `align-content: start` on the card. A grid container defaults to `stretch`, which quietly
  distributes slack into every row of a card that was stretched to match a neighbour.
- The date and the link get **separate rows**. Sharing one row means the layout depends on
  how long a domain happens to be.
- Optional elements never disappear. A row that cannot render its link renders it as plain
  text, because a card one line shorter than its neighbours is worse than an unclickable
  domain.

**Interaction.** The card is a container, not a control: a transparent button is stretched
across it, inset to zero on all four sides, and carries the accessible name, while the site
link is raised above it with `z-index: 1`. An `<a>` inside a `<button>` is invalid markup that
browsers repair by discarding one of the two. Event handlers key on the stretched button,
never on the card, so the anchor is excluded by construction.

**Hover.** `translateY(-3px)`, border to `--beam` at 55%, and a soft `--beam` shadow, over
`--dur-fast`.

### 7.3 Threshold bar

A hairline chart, not a chart. 3px tall, `--track` ground, `--beam` to `--violet` gradient
fill, a 1px `--ink` tick at 55% opacity marking the qualifying threshold.

`aria-hidden`: it is a second reading of the figure printed directly above it, so it owes a
screen reader nothing.

Scale is settled server-side, never in the browser: the track runs from zero to the largest
value in the whole set, so every bar is that item against the biggest one. The tick does not
move when the set is filtered. It is a property of the register, not of the view.

**A value nobody published gets no fill.** It gets dashed amber, masked to fade out to the
right: over the line, ending nowhere in particular. A bar of zero length says "worth
nothing", which is the exact misreading the system exists to prevent.

### 7.4 Summary row

Two ranks, never a row of equal tiles.

- **Headline stat.** Display face, `--step-4`, `tabular-nums`, a `--rule` hairline, then a
  `.label`. Two of these, side by side past 40rem. These are the only figures on the site
  not set in mono, which is what makes them read as a headline.
- **Rank row.** A list of `label` against `value` rows separated by `--stroke` hairlines,
  a `--step--1` muted label against a `--step-0` ink value.

Only one row is a link, so only that row carries a mark (`↗`), takes `--beam-text` on its
value and answers the pointer. A tile that lifts under the cursor and then does nothing is a
promise the design cannot keep.

### 7.5 Ledger row

For lists of money. Two columns, two rows:

```
Blacklane                                    €24 m
Series C · Berlin · Jens Wohltorf   EU-Startups · 5 Aug ↗
```

`grid-template-columns: 1fr auto`, baseline aligned, `--stroke` hairline above each row and
below the last. Amounts are right-aligned, `nowrap` and `tabular-nums`, so the eye runs down
the column and stops where it wants. Below 560px it becomes one column and everything
aligns left.

Prose is the wrong shape here: five sentences put the figure in a different place five
times.

Citations go compact, with publication and date as the link text and the headline on the
`title` attribute. A right-hand column of forty-word headlines buries the column of figures beside
it.

### 7.6 Badges and markers

All amber, all the same shape: `--step--1`, `--amber` text, 1px border of `--amber` at 45%,
4px radius, `0 var(--space-2)` padding.

| Marker | Means |
|---|---|
| `aged` | Positive reason to think the figure has been overtaken |
| `>1bn` | Over the threshold, amount unpublished |
| `disputed` | Sources disagree and both are shown |
| `undisclosed` | No figure was ever published |

A badge is a qualification on a figure, **never an error state**, and never a third accent
colour. Keep them rare: a marker on half the set is wallpaper.

An extended note (disputed or undisclosed) renders as a block with a 2px `--amber` left
border at 55% over `--panel`, the badge, the note in `--ink`, then its own source link.
Notes stay under fifteen words.

### 7.7 Dialog

`--deep` ground, `--stroke` border, `--radius`, `min(64rem, 92vw)`, `max-height: 88vh`,
`--space-7` padding, native `<dialog>` with `showModal()`.

Backdrop `rgba(4,5,8,.72)` with a 10px blur. Close button sticky at the top right, 44px
circle. Entry animation 260ms, opacity and a small rise, skipped under reduced motion.

Every route out, meaning the button, the backdrop, Escape and a programmatic close, must
converge on one cleanup that runs exactly once. Escape fires the native `close` event and never reaches
a click handler, so `close` is the only signal on that path.

### 7.8 Timeline node

A vertical `--stroke` rule with a 9px dot per entry. The marked entry takes `--violet` with
a 4px glow ring. Date and stage in `--step--1` `--muted`, amount in `--step-1`. Nodes
stagger in at `calc(var(--i) * 70ms)`.

Under reduced motion, `animation-delay` must be zeroed as well as `animation-duration`:
staggering by timing rather than by motion still fails the requirement.

### 7.9 Controls

| Control | Spec |
|---|---|
| Button, primary | 999px radius, `--panel` over `--stroke`, `--step--1` uppercase with `.14em` tracking, hover to `--panel-hover` with a `--beam` border |
| Search field | 999px radius, min-height 44px, `--panel`, keyboard shortcut hinted in a `kbd` at the right |
| Chip (filter) | 999px, transparent, `--stroke` border, `--muted`. Checked takes a `--beam` border, `--panel` and `--ink`. Hover lifts 1px |
| Segmented toggle | Two buttons in one 999px pill, `aria-pressed`, the active one on `--panel-hover` |
| Disclosure row | Native `<details>`/`<summary>`, hairline separated, display face question, chevron rotates 180° when open |

Every control is at least 44px tall. A secondary inline link inside a larger primary target
may be smaller, with 24px the floor.

---

## 8. Accessibility contract

Non-negotiable, and machine-checked rather than remembered.

- **4.5:1 minimum** for every text token against every surface it can land on, including
  translucent panels composited over the ambient field. Measured worst case in this system:
  `--muted` on a hovered panel over both pools, **5.57:1**. Best case `--ink` on `--void`,
  17.25:1.
- Dark inks are asserted to **fail** on `--plate`, so nobody sets body ink on the light
  surface by accident.
- Focus is always visible: `2px solid var(--beam)`, `outline-offset: 3px`. On a card the
  outline traces the card, because the stretched button is exactly the card's size.
- Touch targets 44px, secondary inline links 24px.
- An accessible name must carry every qualification a sighted reader can see. A card reading
  "Isar Aerospace, Undisclosed" tells a screen-reader user strictly less than the visible
  `>1bn` marker does, so the spoken name says "valuation undisclosed, over 1 bn".
- Decorative second readings of a visible figure are `aria-hidden`.
- Roving `tabindex` for tablists and radiogroups: one Tab stop, arrows move within.
- Every disclosure is a native `<details>`, so it is keyboard operable, announced as
  expandable and readable with JavaScript off. Never a div with `aria-expanded`.

---

## 9. Voice and content

- **No em dashes. No semicolons.** Minimise colons. Both are easy to type, impossible to
  spot in review, and enforced by a test over every user-facing string.
- The one exception is a quoted headline, which stays verbatim on a named allowlist. Editing
  a publisher's punctuation falsifies a citation.
- Sentence case everywhere except `.label`, which is uppercase by rule.
- Active voice. A control says exactly what happens, and keeps the same word through the
  flow: "Publish" produces "Published".
- Name things by what a person recognises, not by how the system is built.
- **Every figure carries its date.** A number without one is not publishable.
- Emptiness is information, not a fault. "No further rounds were reported this week" beats a
  heading over blank space. An empty container reads as something that failed.
- Never invent a value to fill a template. A clause with no source is dropped and the
  sentence closes up around it.
- Where a fact is weaker than the system's usual standard, say so in the interface rather
  than in a footnote.

---

## 10. Anti-patterns

Things that were tried here and are wrong for this system:

- A light theme, or a theme toggle.
- A third accent colour, or amber used decoratively.
- Type set in `--beam`.
- Equal-weight tiles for figures that are not equal.
- A row of cards where one wraps and the rest do not.
- Prose stretched to a 110-character line, or held to measure by shrinking its container
  instead of its text.
- A gradient on more than one phrase.
- A reveal animation on body copy.
- Numbered markers (01 / 02 / 03) on content that is not a sequence.
- A badge common enough to become wallpaper.
- Raw hex anywhere outside the token file.

---

## 11. Implementation notes

- Zero build. Hand-written HTML, CSS custom properties and vanilla ES modules. No framework,
  no bundler, no dependency.
- **Design tokens only.** `tokens.css` is the sole file containing a raw colour value.
- **Compute in the backend, render in the browser.** Every label, percentage, sort key and
  formatted date is settled before it reaches the page, so fragile logic is unit-tested and
  the browser code stays thin enough to read.
- All rendered data is treated as untrusted: escaped for HTML, and any URL scheme-checked
  before it becomes an `href`. Escaping does not make a `javascript:` URL safe.
- The contrast checker, the punctuation ban and the single-gradient rule are tests. A design
  rule that lives only in a document is a rule that will be broken.
