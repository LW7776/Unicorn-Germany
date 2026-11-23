---
name: German Unicorns
description: A register of billion-euro German companies rendered as a lit room rather than a spreadsheet.
colors:
  bone: "#FAF8F4"
  bone-2: "#F3EFE8"
  card: "#FFFFFF"
  ink: "#15130F"
  muted: "#544F46"
  faint: "#726C62"
  line: "rgba(21, 19, 15, .10)"
  line-2: "rgba(21, 19, 15, .16)"
  action: "#2D3BC9"
  action-ink: "#FFFFFF"
  mark: "#544F46"
  indigo: "#3D4EF5"
  rose: "#F2567E"
  amber: "#F2A33C"
typography:
  display:
    fontFamily: "Mona Sans, ui-sans-serif, system-ui, sans-serif"
    fontSize: "clamp(42px, 6.6vw, 92px)"
    fontWeight: 600
    lineHeight: 1.04
    letterSpacing: "-0.035em"
    fontVariation: "'wdth' 112"
  headline:
    fontFamily: "Mona Sans, ui-sans-serif, system-ui, sans-serif"
    fontSize: "clamp(28px, 3.2vw, 46px)"
    fontWeight: 600
    lineHeight: 1.04
    letterSpacing: "-0.035em"
    fontVariation: "'wdth' 112"
  title:
    fontFamily: "Mona Sans, ui-sans-serif, system-ui, sans-serif"
    fontSize: "20px"
    fontWeight: 600
    lineHeight: 1.04
    letterSpacing: "-0.02em"
    fontVariation: "'wdth' 104"
  figure:
    fontFamily: "Spline Sans Mono, ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
    fontSize: "26px"
    fontWeight: 500
    lineHeight: 1.1
    letterSpacing: "-0.02em"
    fontFeature: "'tnum' 1, 'lnum' 1"
  body:
    fontFamily: "Mona Sans, ui-sans-serif, system-ui, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.6
  lede:
    fontFamily: "Mona Sans, ui-sans-serif, system-ui, sans-serif"
    fontSize: "18px"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "Spline Sans Mono, ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
    fontSize: "12px"
    fontWeight: 400
    letterSpacing: "0.08em"
  note:
    fontFamily: "Spline Sans Mono, ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
    fontSize: "12px"
    fontWeight: 400
    letterSpacing: "normal"
rounded:
  md: "14px"
  card: "20px"
  pill: "999px"
spacing:
  s1: "8px"
  s2: "16px"
  s3: "24px"
  s4: "40px"
  s5: "64px"
  s6: "96px"
  s7: "128px"
components:
  button-primary:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.bone}"
    rounded: "{rounded.pill}"
    padding: "14px 26px"
    height: "48px"
  button-primary-hover:
    backgroundColor: "#241F19"
  button-accent:
    backgroundColor: "{colors.action}"
    textColor: "{colors.action-ink}"
    rounded: "{rounded.pill}"
    padding: "14px 26px"
  button-accent-hover:
    backgroundColor: "#2432B4"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
    padding: "14px 26px"
  button-ghost-hover:
    backgroundColor: "{colors.bone-2}"
  cell:
    backgroundColor: "{colors.card}"
    textColor: "{colors.ink}"
    rounded: "{rounded.card}"
    padding: "{spacing.s3}"
  register-box:
    backgroundColor: "{colors.card}"
    rounded: "{rounded.card}"
    height: "min(76vh, 760px)"
  segmented-track:
    backgroundColor: "{colors.bone-2}"
    rounded: "{rounded.pill}"
    padding: "4px"
  segmented-button:
    backgroundColor: "transparent"
    textColor: "{colors.muted}"
    rounded: "{rounded.pill}"
    padding: "9px 20px"
    height: "40px"
  segmented-button-selected:
    backgroundColor: "{colors.card}"
    textColor: "{colors.ink}"
  field-input:
    backgroundColor: "{colors.card}"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
    padding: "11px 18px"
    height: "44px"
  detail-sheet:
    backgroundColor: "{colors.card}"
    textColor: "{colors.ink}"
    padding: "64px 40px 96px"
    width: "min(620px, 94vw)"
  quote-block:
    backgroundColor: "{colors.bone}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    padding: "{spacing.s3}"
---

# Design System: German Unicorns

## Overview

**Creative North Star: "The Lit Room"**

The register is a warm, well-lit room rather than a spreadsheet. One slow field of light
carries the whole page, a single faceted object stands in that field and is lit by it, and
every company is a soft card you could pick up. The world is called Aurora, and it was
chosen by the client by name against a cooler and a darker alternative. It refuses two
things explicitly: the dark analytics tracker with its glass panels and neon accent, and
the clinical white data sheet that is that tracker's polite opposite.

Density is generous rather than efficient. The page runs on an 8pt rhythm with real air:
128px between sections, 64px between blocks inside the detail sheet, and a reading column
held to a measured 52 characters. The surfaces are nearly flat. Depth comes from one soft,
wide, low-opacity elevation and from tonal layering between three grounds (bone, a tinted
bone, and white card), never from a hard edge or a dark border.

The whole visual argument is that colour is light and ink is evidence. Indigo, rose and
amber exist in the aurora, in the landing object and in two drawn data marks, and they are
never set as type. Everything a reader actually reads is ink, muted ink, or the one
darkened indigo that was made for the job. Figures are the exception to the sans: every
measured quantity on the site is set in a mono face with tabular lining numerals, so the
numbers line up as a column of evidence wherever they appear.

**Key Characteristics:**
- One warm bone ground, lit by a single slow aurora of indigo, rose and amber.
- Colour lives in the light field and in drawn data, never in type.
- Pill controls, 20px cards, one soft elevation, an 8pt rhythm with real air.
- Mona Sans with its width axis pushed to 112% for headings; Spline Sans Mono for every
  figure, date and label.
- Zero build step, no framework, no npm dependency, no photography, both faces self-hosted.
- Motion plays once and is not scheduled at all under reduced motion.

## Colors

A warm bone ground with near-black ink, lit by three saturated field colours that are
forbidden from ever being text.

### Primary
- **Field Indigo** (`{colors.indigo}`): the dominant light in the aurora, the lower-left
  lobe of the landing field, the first stop of the scroll progress bar and of the sector
  bar fills, and the cool side of the landing object's facets. Never type.
- **Action Indigo** (`{colors.action}`): indigo darkened until it clears the body floor.
  This is the only chromatic colour allowed to be text: source links, the accent button,
  map dots and rings, focus rings, the caret and the selection background. Measured 7.67:1
  on bone, 7.10:1 on tinted bone, 8.14:1 on card.

### Secondary
- **Field Rose** (`{colors.rose}`): the lower-right lobe of the aurora, the warm side of
  the object's facets, the middle stop of the progress and sector gradients, and the stroke
  on the growth curve's year dots. Never type.

### Tertiary
- **Field Amber** (`{colors.amber}`): the lowest lobe of the aurora, under the object, and
  the last stop of the progress and sector gradients. Never type.

### Neutral
- **Bone** (`{colors.bone}`): the page ground, the landing ground, the veil laid back over
  the light field, and the quote block inside the detail sheet.
- **Tinted Bone** (`{colors.bone-2}`): alternating section tint, the segmented-control
  track, the map's landmass fill, the bar track, and ghost-button hover.
- **Card White** (`{colors.card}`): every card, the register box, the control bar, the
  detail sheet, the flying arrival cards, and the selected segment.
- **Ink** (`{colors.ink}`): all headings and body copy, the primary button ground, and the
  scrim at 28% opacity. 17.49:1 on bone.
- **Muted Ink** (`{colors.muted}`): running copy that is not a heading. Held to 7:1 rather
  than the AA floor. Measured 7.66:1 on bone, 7.09:1 on tinted bone, 8.13:1 on card.
- **Faint Ink** (`{colors.faint}`): labels, dates and meta only, never a sentence. Measured
  4.90:1 on bone, 4.54:1 on tinted bone, 5.20:1 on card.
- **Hairline** (`{colors.line}`) and **Hairline Strong** (`{colors.line-2}`): the only
  borders in the system, ink at 10% and 16%.
- **Mark Ink** (`{colors.mark}`): the four drawn caveat marks, which share muted ink's value
  on purpose.

### Named Rules

**The Light-Not-Type Rule.** Indigo, rose and amber live in the aurora, in the landing
object, in the progress bar and in the sector bar gradients. They are never set as a text
colour, a link colour, a border or an icon fill. `--action` is the darkened indigo that
exists for that job, and it is the only chromatic text colour on the site.

**The Two-Gate Rule.** A palette gate cannot see a light field. `tools/check_contrast.py`
compares tokens against bone and reported a clean pass while the landing shipped with its
stat labels at 1.51:1 and its figures at 5.93:1 over the aurora. Any text that sits over
the field is measured in a real browser by `tools/check_landing_contrast.js` against the
ground actually behind its glyphs, or it does not ship.

**The Drawn-Caveat Rule.** The four caveats (undisclosed, disputed, aged, reported) are
drawn marks at one stroke weight in one colour. No caveat depends on hue to be read, which
is why there is no red, amber or green anywhere in the data layer.

## Typography

**Display Font:** Mona Sans (variable, 200–900 weight, 75–125% width axis), self-hosted woff2
**Body Font:** Mona Sans (with `ui-sans-serif, system-ui, sans-serif`)
**Label/Mono Font:** Spline Sans Mono (variable, 300–700), self-hosted woff2

**Character:** A broad, confident grotesque set tight and wide at once, against a quiet
mono that does nothing but carry evidence. Headings push Mona Sans's width axis to 112%
with -3.5% tracking, which makes a short headline read as a cast object rather than as a
line of text. The mono is deliberately unassertive: its job is to make forty figures line
up, not to be noticed.

### Hierarchy
- **Display** (600, `clamp(42px, 6.6vw, 92px)`, 1.04, -0.035em, width 112%): the landing
  wordmark and each page's `h1`. The landing's `h1` is held to a 9ch measure (11ch under
  900px) so it breaks where it was meant to.
- **Headline** (600, `clamp(28px, 3.2vw, 46px)`, 1.04, -0.035em, width 112%): section
  headings.
- **Title** (600, 20px, -0.02em, width 104%): sub-headings, the About page's question
  headings at 21px, the detail sheet's company name at 30px with -0.03em.
- **Figure** (500, mono, tabular lining numerals): every measured quantity. 26px on a
  register cell, 22px on a week lead, `clamp(40px, 5vw, 58px)` in the detail sheet,
  `clamp(34px, 3.4vw, 50px)` for the big growth stats.
- **Body** (400, 16px, 1.6): running copy in ink, or muted ink at 1.68–1.75 line-height on
  the reading pages. Held to `--measure`.
- **Lede** (400, 18–19px, 1.6, muted): the one line under a page heading. Held to
  `--measure-wide`.
- **Label** (mono, 12px, +0.08em, faint): a count, a key, two or three words.
- **Note** (mono, 12px, normal tracking, faint): a mono sentence. Wide tracking actively
  slows a sentence down, so running mono takes this instead of Label.

### Named Rules

**The Self-Hosted Faces Rule.** Both faces are self-hosted variable woff2 in
`assets/fonts/`. The Google Fonts CDN is forbidden: embedding it has been ruled a GDPR
breach in German courts and this site carries an Impressum. No webfont service, no
`<link>` to a third-party font host, ever.

**The Measured Measure Rule.** The reading column is `--measure: 52ch` and the lede column
is `--measure-wide: 56ch`, and those numbers are browser measurements rather than character
counts. `ch` is the advance of the zero glyph, and Mona Sans's zero at this width is about
40% wider than its average character, so every measure written in `ch` was letting roughly
40% more text onto the line than it looked like: 68ch rendered 94 characters, 64ch rendered
91, against a 65–75 bar. Set a new measure by measuring the rendered line, not by counting
characters.

**The Mono-Carries-Evidence Rule.** Every figure, date and source timestamp is mono with
`font-variant-numeric: tabular-nums lining-nums`. Prose is never mono and a figure is never
sans. A reader who learns the pairing once reads every number on the site.

## Layout

A single centred container, `width: min(100% - 2 * var(--gut), 1280px)` with a 48px gutter
that drops to 20px under 720px. Vertical rhythm is an 8pt scale: 8 / 16 / 24 / 40 / 64 / 96
/ 128px. Sections are separated by the 128px step (88px on phones) and alternate between
bone and tinted bone; they carry no inset padding of their own because the container insets
their contents with `margin-inline: auto` against a constrained width.

The register is the exception to page scroll: it lives in a fixed-height box,
`min(76vh, 760px)` on desktop and `min(78vh, 600px)` on phones, with a pinned control bar
and its own scroller beneath. The grid inside it is `repeat(auto-fill, minmax(248px, 1fr))`
at a 16px gap.

Breakpoints are few and each one exists for a named reason. 900px collapses the landing to
one column and moves the object behind the words as a 50%-opacity layer, so the first screen
stays one screen; it also stacks the week and the growth section. 860px drops the nav links.
760px collapses the sector bars to one column and hides the map's city labels, which collide
and shrink past reading below that width. 720px is the phone gutter, the stacked control bar
and the smaller detail-sheet padding. 560px stacks the Impressum's operator record.

Sticky elements: the nav at 68px with a translucent bone ground and a 14px backdrop blur,
and the 3px scroll progress bar above everything at z-index 90. The layer order is ink and
content, nav at 30, the detail sheet at 80 over a scrim at 70, the landing at 60 over all
of it, and the arrival layer at 5 inside the register box.

## Elevation & Depth

Nearly flat, with one soft elevation and three tonal grounds doing most of the work. Depth
reads as the difference between bone, tinted bone and white card, plus hairlines at 10% and
16% ink. There is not a single hard-edged or offset shadow in the system: every shadow is
wide, low-opacity and directly beneath its surface, so a card reads as a sheet lying on a
lit table rather than as a box floating over a page.

### Shadow Vocabulary
- **Resting card** (`0 1px 2px rgba(21,19,15,.04)`): every register cell at rest. Barely
  there, and that is the point.
- **Register box** (`0 1px 2px rgba(21,19,15,.04), 0 18px 48px rgba(21,19,15,.06)`): the one
  large container that is lifted off the page.
- **Lifted card** (`0 2px 4px rgba(21,19,15,.05), 0 12px 28px rgba(21,19,15,.09)`): a cell
  under a fine-pointer hover, paired with a 2px rise.
- **Selected segment** (`0 1px 2px rgba(21,19,15,.08), 0 4px 12px rgba(21,19,15,.06)`): the
  pressed state of the grid/map toggle.
- **In flight** (`0 10px 30px rgba(21,19,15,.16), 0 2px 6px rgba(21,19,15,.07)`): an arrival
  card while it is off the surface. It is the deepest shadow in the system because it is the
  only element genuinely in the air.
- **Drawer** (`-24px 0 60px rgba(21,19,15,.16)`): the detail sheet against the page it
  covers, cast sideways because the sheet arrives sideways.

### Named Rules

**The Soft-Elevation Rule.** Every shadow is ink at 4–16% alpha with a blur at least five
times its offset, and no shadow is coloured. Hover adds elevation and 2px of rise; nothing
else changes on hover.

**The Hairline Rule.** Borders are `rgba(21,19,15,.10)` or `.16` and 1px. There are no dark
rules, no double rules and no boxes drawn in ink.

## Shapes

Two radii and a pill. Containers that hold a record (the register box, every cell, the week
aside) take the 20px card radius. Smaller inner surfaces (the arrival cards, the quote block
in the detail sheet) take 14px. Everything interactive is a pill: buttons, the segmented
control and its track, search and select fields, the skip link, the bar tracks and fills.
The detail sheet's close control is the one circle, at 40px.

The silhouette the system repeats is a soft rectangle on a lit ground with a hairline edge
and a shadow directly under it. The one geometric exception is the landing object: forty
thin plates on a common axis, one per company, drawn as projected polygons on a 2D canvas
and shaded from the aurora's own three lights with one emissive edge. The map is the other
drawn surface, a filled landmass with circular dots at the aurora's action indigo.

## Components

### Buttons
- **Shape:** fully pill (`999px`), minimum 48px tall, 14px by 26px of padding, 10px gap.
- **Primary:** ink ground, bone label, weight 500 at 16px. Hover darkens to `#241F19`,
  press scales to 97% over 160ms on the exit curve.
- **Accent:** action indigo on white, hover `#2432B4`. Used where the action is the
  evidence rather than the navigation.
- **Ghost:** transparent with an inset 1px hairline-strong ring, ink label, hover fills
  with tinted bone.
- **Focus:** 2px action-indigo outline at 3px offset, shared by buttons, segments, cells
  and links. Hover effects are gated behind `(hover: hover) and (pointer: fine)`.

### Segmented Control (grid / map)
- A tinted-bone pill track with 4px of padding holding two pill buttons at 40px tall. The
  pressed one takes a white ground, ink text and the selected-segment shadow; the other is
  transparent with muted text. Press scales to 97%. At phone width the track takes the full
  row and each button flexes to half of it.

### Cards / Containers
- **Corner Style:** 20px.
- **Background:** white card on bone or tinted bone.
- **Shadow Strategy:** resting card at rest, lifted card on fine-pointer hover with a 2px
  rise, both over 220ms on the exit curve.
- **Border:** 1px hairline.
- **Internal Padding:** 24px.

### Inputs / Fields
- **Style:** white ground, 1px hairline-strong border, pill radius, 11px by 18px of
  padding, 44px minimum height, 160px minimum width, 15px text.
- **Placeholder:** faint ink at full opacity.
- **Focus:** the shared 2px action outline at 3px offset.
- At phone width the field flexes to fill its row and drops to 14px text.

### Navigation
- A 68px sticky bar on `rgba(250,248,244,.86)` with a 14px backdrop blur and a hairline
  bottom. The wordmark is Mona Sans 600 at 112% width with -0.02em tracking; the links are
  15px muted ink, going to full ink on hover over 180ms. Links are hidden under 860px and
  the wordmark carries the bar alone.

### The Register Cell (signature)
A white 20px card holding, in order: a 34px logo plate (the logo is never recoloured,
cropped or redrawn), the company name at 13px muted, the figure at 26px mono, then a
hairline-topped meta row with the date in mono faint on the left and the source link in
action indigo on the right. A transparent full-bleed button sits at z-index 1 to open the
record, while the source link and the caveat marks sit at z-index 2 above it, so clicking
the proof does not also open the sheet on top of the tab it just launched. Caveat marks are
12px drawn squares at a 1.5px stroke: an empty square for undisclosed, two offset bars for
disputed, a diagonal for aged, a horizontal hatch for reported.

### The Caveat Key
A flat wrapped list directly beneath the register box, not inside it, at 13px faint with
each mark at its full colour. Inside the box it would sit below forty cells and be found by
nobody; beneath it, it is on screen whenever the register is.

### The Detail Sheet (signature)
A right-edge drawer at `min(620px, 94vw)`, white, over a 28%-ink scrim. It enters with
`translateX(100%) → none` over 420ms on the drawer curve while the scrim fades over 320ms.
Inside: a logo plate, the company name at 30px with -0.03em, its city and sector at 14px
faint, the figure at up to 58px mono, then a hairline meta row carrying the date and source.
Below that, blocks separated by 64px, each headed by a 13px faint label at +0.05em and
normal width, holding either a bone-grounded quote block at 14px radius, a muted paragraph
held to the measure, or a two-column definition list (140px label column, faint labels, ink
values) that collapses to one column under 720px.

### The Growth Curve and the Sector Bars
The curve is an inline SVG drawn from real figures with card-filled dots stroked in field
rose and mono year labels in faint. The sector bars are 6px pill tracks on tinted bone
(`#E5E0D7` inside a tinted section) with fills running the full aurora gradient from indigo
through rose to amber. Both are drawn from values `tools/build.py` already settled; the
browser does no arithmetic on a published figure.

### The Week
A two-column section, 1.15fr of leads against 0.85fr of aside, collapsing to one column
under 900px. A lead pairs a 22px name with a 22px mono figure pushed to the right edge of
the same baseline row, then mono meta at 13px faint, then a muted paragraph at 1.68 held to
the measure. The aside is a bordered 20px card listing capped rows of further rounds, each
a baseline flex with the name, a faint stage, and a right-aligned mono figure, separated by
hairlines.

### The Static Pages
About and the Impressum use the same world in one column. Questions are hairline-separated
blocks at 40px of vertical padding with a 21px heading and muted copy at 1.75. The
Impressum's operator record is a `max-content 1fr` definition list with mono faint labels
at +0.04em and ink values, collapsing to one column under 560px. Nothing moves on these
pages except the section reveals.

### Motion
- **Easings.** `--ease-out: cubic-bezier(.23,1,.32,1)` is the default for anything arriving
  or responding to a press. `--ease-io: cubic-bezier(.77,0,.175,1)` is used only inside the
  arrival, for cards travelling between two known places. `--ease-drawer:
  cubic-bezier(.32,.72,0,1)` belongs to the detail sheet alone.
- **The landing's leave, in two stages.** The words and object go first (460ms, opacity and
  a 26px rise with a 1.5% scale-down), then the landing itself lifts 14% over 760ms and
  fades over 520ms while the site fades up beneath it over 420ms after a 180ms delay. The
  field fades last over 560ms, so the cards burst into a room that is still lit.
- **The arrival, inside the box.** Forty cards burst from a point 46% down the frame on a
  deterministic seeded scatter: 620ms out on the exit curve with a 6ms stagger, a 520ms
  hold, then 900ms of settle on the in-out curve with an 11ms stagger. Cards whose cell is
  on screen land on that cell's measured bounds and fade their own label out before they
  arrive; the rest slide out through the bottom edge, because a card cannot land on a cell
  that is below the clip. The real grid fades up underneath. It plays once.
- **Elsewhere.** Section reveals are a 620ms rise of 14px on first intersection, once.
  Figures count once on first view. The grid-to-map toggle crossfades in place. Hovers are
  180–220ms. Nothing animates on a repeat action.

**The Reduced-Motion Contract.** Under `prefers-reduced-motion: reduce` nothing is
scheduled, rather than shortened: the arrival returns before building its layer, the section
reveals return before touching the DOM, the counters paint their final value, the landing
object paints a single frame, and the stylesheet sets `animation: none` and 1ms transitions
globally. Verified by counting, not by looking: zero `Element.animate` and zero
`requestAnimationFrame` on load and through entering the register. The single exception is
`wireProgress`, which coalesces one `requestAnimationFrame` per frame while the reader
scrolls. That bar is a readout of where the reader already is rather than motion of its own,
and making it paint synchronously would mean doing layout work on every scroll event to
satisfy a count.

## Do's and Don'ts

### Do:
- **Do** keep indigo, rose and amber in the light field, the landing object, the progress
  bar and the sector gradients, and use `#2D3BC9` whenever a chromatic colour has to be type.
- **Do** set every figure, date and source timestamp in Spline Sans Mono with
  `font-variant-numeric: tabular-nums lining-nums`.
- **Do** push Mona Sans's width axis to 112% with -0.035em tracking on display and headline,
  and 104% with -0.02em on titles.
- **Do** hold reading columns to `--measure` and ledes to `--measure-wide`, and set any new
  measure by measuring the rendered line in a browser.
- **Do** run `tools/check_contrast.py` for the palette and
  `playwright-cli run-code --filename=tools/check_landing_contrast.js` for anything set over
  the aurora, plus `tools/validate.py`, `tools/validate_funding.py` and the 293 pytest tests
  before shipping.
- **Do** keep every `:root` value in `assets/css/aurora.css` and the copy of it in
  `tools/check_contrast.py` in step; that duplication is the only reason the tokens can be
  trusted.
- **Do** hold running copy to 7:1 rather than the 4.5:1 AA floor, and reserve `--faint` for
  labels, dates and meta.
- **Do** make a new caveat or status readable by shape and stroke, so it survives being
  seen without colour.
- **Do** build on the 8pt scale (8 / 16 / 24 / 40 / 64 / 96 / 128) and the two radii plus
  the pill.
- **Do** plan every animation to play once, and to be skipped entirely rather than
  shortened under reduced motion.

### Don't:
- **Don't** set `--indigo`, `--rose` or `--amber` as a text colour, a link colour, a border
  or an icon fill.
- **Don't** link the Google Fonts CDN or any third-party webfont host. Both faces are
  self-hosted woff2, and this site carries an Impressum.
- **Don't** write a measure in `ch` and trust it; Mona Sans's zero is about 40% wider than
  its average character.
- **Don't** add a build step, a framework, a bundler or an npm dependency. The site is
  hand-written HTML, CSS and vanilla ES modules served from the repository root by GitHub
  Pages, and a browser gate borrows an already-installed CLI rather than adding a package.
- **Don't** do arithmetic on a published figure in browser code. Python computes, JavaScript
  renders.
- **Don't** add photography of any kind. Company logos are the only imagery, and they are
  never recoloured, cropped, masked or redrawn.
- **Don't** use an em dash or a semicolon in user-facing copy.
- **Don't** publish a figure without its date and a working link to the page that states it.
- **Don't** add a second progress bar or a second charging element. One bar at the top of
  the page is what keeps it meaning anything.
- **Don't** add a hard-edged or offset shadow, a dark border, or a shadow carrying colour.
- **Don't** trust the palette gate for text that sits over the aurora; it compares tokens
  against bone and cannot see the field.
