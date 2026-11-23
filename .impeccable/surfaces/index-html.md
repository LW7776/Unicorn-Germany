---
version: 1
slug: "index-html"
primary_target: "index.html"
related_targets: ["about.html"]
---

# index.html

Scope: the register's single page, its landing, the companies register with grid and map views, the
weekly funding section, the company detail sheet, and the About page. Visitor mode: Read.

Audience and job: a founder in the German startup scene. **The register leads, not the week.** The
reader arrives to look across forty companies and to open one of them; the week is a single section
further down, never repeated.

Primary action: enter the register from the landing.

Content and proof: 40 company records, 18 weekly funding files, 37 logo files. No photography, no
testimonials, no customers, no pricing, and none of these may be invented. The logos are the only
borrowed imagery and are never altered. 3D objects and icons are authored in code, so they are not
borrowed imagery at all.

Constraints that bind the build: zero build step, self-hosted woff2 only, three.js vendored rather
than loaded from a CDN for the same Impressum reason, WCAG AA enforced in CI, no em dashes and no
semicolons, 293 tests green, Python computes and JavaScript renders.

## Direction contract

THESIS: a register of billion-euro companies rendered as a lit room rather than a spreadsheet. One
warm field of light carries the whole page, a single object stands in it, and every company is a
soft card you can pick up. It refuses the dark analytics tracker with its glass panels and neon
accent, and it refuses the clinical white data sheet that is that tracker's polite opposite.

OWN-WORLD: warm bone ground #FAF8F4 with a slow aurora of indigo #3D4EF5, rose #F2567E and amber
#F2A33C that lives only in the light field and never in type. Ink #15130F. Pill controls, 20px
cards, one soft elevation, an 8pt rhythm with real air. Mona Sans at 600 with the width axis pushed
to 112% and -3.5% tracking, Spline Sans Mono for figures and dates. **The aurora is the light source for
the landing's 3D object**, so the facets carry its colours and one edge is emissive: the field and
the object are one device, not two competing ones.

STORY: the visitor arrives in a lit room, enters the register with one press, understands within a
screen that this is every German company past a billion with its evidence attached, scans or maps
them, opens one, and reads the sentence that proves its figure.

FIRST VIEWPORT: the landing. The aurora fills the lower two thirds, a faceted object turns slowly
in it, lit by that field with one emissive edge. The wordmark sits on the left line at display
scale with one plain line under it and a single pill button, "Enter the register". Nothing else.

FORM: Aurora, the first of the three layouts put to the user, chosen by them and amended by them to
carry the lit 3D object from the second. The object is procedural: forty thin plates, one per
company, arranged radially. seed: none (pinned)

Pinned by the user, in their words: "proceed with A - Aurora. But also use a lit 3D object on the
landing with one emissive edge. Generally, include (3D) objects and icons in the website where
appropriate."

Signature interaction and motion grammar: the landing lifts away by 14% over 760ms on
cubic-bezier(.23,1,.32,1) while the site fades up beneath it, so entering reads as the room opening
rather than a page swap. Cards deal in on a 40ms stagger, once. The grid-to-map toggle crossfades
in place. The detail sheet enters from the right over 420ms on the drawer curve. Figures count once
on first view and never again. Nothing animates on a repeat action. Under prefers-reduced-motion
nothing is scheduled at all, the object renders one static frame, and that is verified by counting
requestAnimationFrame and Element.animate rather than by looking.

Memorable moment: the object in its field of light, turning, with one lit edge.

Unresolved: whether the map view keeps the old city-window behaviour or opens the same detail sheet.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the
verdict, DESIGN.md, and every shipping raster carrying its provenance

## Detector suppressions, and why

Two detector rules are suppressed in `.impeccable/config.json`. Both were checked against the
rendered page before being silenced, because a suppression nobody can audit is worse than a finding
nobody fixed.

- **`cream-palette`** flags the page ground `rgb(250, 248, 244)` as the default warm off-white that
  generated interfaces reach for by reflex. The rule is a fair one in general. It is suppressed here
  because this ground is the client's own decision: three directions were put side by side and this
  one was chosen by name, over a cooler and a darker alternative. The detector cannot tell a reflex
  from a choice, so the record of the choice lives here instead.
- **`cramped-padding`** flags the two tinted sections for having children "flush against bg on all
  sides (no inset)". Measured in the browser at 701px wide, the children of both sit 88px from the
  top and bottom of the tint and 20px from its left and right edges. The rule reads the section's own
  `padding` and does not see that `.wrap` insets its contents with `margin-inline: auto` against a
  constrained width, which is how every section on this site is built. The finding is wrong about
  this page, so it is suppressed rather than designed around.

`overused-font` is **not** suppressed. It is a true observation about both faces and is left standing
for the client to decide on.

`repeating-stripes-gradient` is advisory and stays. The pattern it finds is the hatch inside the
`reported` caveat mark, which carries the publication tier so a caveat can be read without relying
on hue. It is semantic, not surface decoration.

## Amended after the finish review

The contract above was written before the build and two of its lines no longer describe what
shipped. They are corrected in place rather than left to rot, and the reasons are here:

- **The mono is Spline Sans Mono, not Geist Mono.** The design detector flags Geist by name as a
  face that is now on enough sites to have stopped being a choice, and avoiding work that reads as
  default output is the whole reason for this redesign. Spline Sans Mono is OFL, variable from 300
  to 700, a true monospace at 0.6em, and smaller than what it replaced at 58KB against 71KB. Mona
  Sans was flagged too and was kept deliberately, which is why `overused-font` is still standing in
  the detector rather than suppressed.
- **The first viewport no longer carries the stat row.** It held three figures that the Growth
  section already presents against the curve, so the landing was repeating itself, and FIRST
  VIEWPORT says the landing is the headline, the lede, the object and the button. It was also where
  the contrast failure was worst. The row is gone.

## Files the detector no longer reads, and why

These are suppressed by path in `.impeccable/config.json`. None of them is the site.

- **`design-system/**`** is a portable specification committed in August. It opens by saying that
  everything in it is what the site actually ships, and it lifts its values from
  `assets/css/tokens.css`. That was true of the dark world it was written for and is not true of
  anything now: Aurora replaced those tokens, and that directory is the only place left that still
  describes the retired palette and the Archivo, Source Serif 4 and IBM Plex Mono faces. It is
  stale documentation rather than a surface with design problems, so the detector is pointed away
  from it. The document itself still needs a decision: regenerate it against the new DESIGN.md, or
  remove it. Left for the owner.
- **`assets/css/base.css`, `assets/css/tokens.css`, `assets/css/admin.css` and `admin.html`** are
  the local-only editor. No public page links them, and the three retired faces they load exist to
  serve that tool. They are outside the world on purpose.

- **`design-options/**`** holds the three directions put side by side before the build, plus a test
  page for the landing object. Two of them are the dark ones that were not chosen, so they still
  carry Geist Mono and coloured glows on dark grounds. That is correct for what they are. They are
  untracked and do not ship.

`overused-font` on **Mona Sans** is suppressed by value, on the owner's decision, taken with the
finding in front of them. Geist Mono was the other half of that finding and was replaced rather
than silenced, which is the difference between a choice and an excuse: the face that nothing
depended on went, and the one doing real work in the headlines stayed.

The three shipped pages are read in full and are clean.
