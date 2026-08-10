# QA — Task 19: accessibility, responsive and performance pass

Run against the real dataset (27 companies, 9 cities/HQs, 1 unplaced) on `python3 -m http.server`,
via a real browser (not just source review) wherever a live check was possible. **A note for the
next person, learned the hard way this session:** this browser pane caches CSS and ES modules
aggressively — a `force` reload was not enough to see an edited stylesheet applied. The only
reliable fix was serving from a port the browser had never visited (confirmed via the parsed
CSSOM, not just a visual glance). If you edit a `.css`/`.js` file mid-session and a render looks
unchanged, distrust it before you distrust the file.

## The four logged items

### 1 — `<svg role="img">` wrapping `role="button"` children

**Fixed.** `role="img"` tells assistive tech to treat the element as one flat image and stop
descending into its children — exactly wrong for a map whose children are independently
operable buttons. `assets/js/map.js` now sets `role="group"` on the `<svg>` (keeping the
`aria-label="German unicorns by headquarters city"` as the group's accessible name) and marks
the decorative outline `<path>` `aria-hidden="true"` — it carries no information of its own now
that the parent no longer hides it automatically. Each `<g class="map__city" role="button"
tabindex="0" aria-label="…">` stays exactly as it was: individually reachable, individually
announced. Verified live: all 8 rendered cities report `tabIndex === 0` and a non-empty
`aria-label`.

### 2 — `.map__label` duplicating each city's `aria-label`

**Fixed.** Added `aria-hidden="true"` to the `<text class="map__label">` node. The parent `<g>`
already carries the full "City, N company/companies" name; the visible label text was a sighted
echo of the same fact and would otherwise be read a second time.

### 3 — Focus lands on the Add button after "+ Add a round/founder/source"

**Fixed.** `assets/js/admin.js`'s click handler now tracks the index of the row it just pushed
and calls a new `focusFirstFieldInRow(arrayKey, index)` instead of re-focusing the Add button —
falling back to the Add button only if the row can't be found (defensive, never drops focus
silently). Remove is unchanged: refocusing the Add button there is still the right call, since
the removed row has nothing to hand focus to. Verified live for all three repeatable groups:

- Add a round → focus lands on `#f-rounds-0-id` (Round id), not the Add button.
- Add a founder → focus lands on `#f-founders-0-name`.
- Add a source → focus lands on `#f-sources-0-id`.
- Remove still returns focus to the Add button (unchanged, confirmed no regression).

### 4 — Hit-target bounds check uses the bubble's centre

**Verified, not changed.** `isPlaceable()` checks a city's centre point against the viewBox, not
its eventual halo radius (which can't be known yet — the radius depends on `max`, which depends
on `isPlaceable()`'s own result, so checking the full circle there is circular). Computed
against the shipped dataset:

| City | Radius (viewBox units) | Nearest viewBox edge |
|---|---|---|
| Berlin (12 companies) | 64.00 | 202.2 |
| Munich (8) | 48.67 | 228.5 |
| Alzenau, Chemnitz, Cologne, Freiburg, Hamburg, Mannheim (1 each) | 21.83 | 151.1 (Cologne, the closest) |

Every placed city clears its nearest edge by at least 151 units against a largest radius of 64
— not close, and New York (Dash0's HQ) is correctly excluded from placement entirely by the
separate off-canvas check added in Task 18. No current city is affected. Documented directly in
`map.js` with the exact numbers, so a future contributor adding a city near an edge knows to
recheck this rather than rediscover it.

## Additional defects found during the full pass and fixed

The four logged items were the known list; the full pass below surfaced four more real defects,
all fixed:

1. **Text over the white logo plate was 1.09:1, not the 17:1 the design system promises.**
   `--plate-ink` (`#14161A`, "the only token for text on `--plate`") was defined in
   `tokens.css` and guarded by `check_contrast.py`, but never actually applied to
   `.cell__plate`/`.detail__plate` — so a broken or slow-loading logo's alt text would render
   in `--ink` (near-white) on the near-white plate, effectively invisible. Confirmed via
   `getComputedStyle` before the fix (`rgb(236,238,243)` on `rgb(247,248,250)`) and after
   (`rgb(20,22,26)`, 17.04:1). Fixed with one line in `register.css`; `.detail__plate` inherits
   it automatically since `detail.js` renders both classes on the same element.
2. **Map city labels fell below the 12px floor at narrow widths.** `.map__label`'s CSS
   `font-size: 22px` is set in the SVG's *user* units, which scale down with the viewBox on a
   narrow viewport — measured **7.55px rendered at 375px wide**. Fixed by scaling a 13px floor
   back into user units the same way `map.js` already does for the 44px hit-target radius
   (`labelFontSize = Math.max(22, MIN_LABEL_PX / scale)`, applied as an inline `style` on each
   `<text>`, which — as a presentation-attribute-strength override — is needed to beat the CSS
   class rule). Verified: 13.00px at 375px, 15.49px at 768px, 16.19px at 1440px.
3. **Admin's inline `<code>` dropped to 11.48px at 375px.** `.admin__note`'s own font-size is
   already the site's smallest token (`--step--1`, ~12px), and `.admin__note code`'s `.95em`
   optical shrink pushed it under the floor at the narrow end of that token's clamp. Fixed with
   `font-size: max(12px, .95em)` on both `.admin__note code` and `.admin__lede code` (the
   second wasn't broken — `.admin__lede` inherits the larger body size — but the same guard
   costs nothing and prevents the same class of bug if the token scale ever changes). Verified:
   exactly 12.00px at 375px, comfortably above at 768/1440.
4. **Reduced motion didn't fully stop the funding timeline's stagger.** The global
   `@media (prefers-reduced-motion: reduce)` rule in `base.css` zeroed `animation-duration` and
   `animation-iteration-count` but not `animation-delay`. `.timeline__node` uses
   `animation-delay: calc(var(--i) * 70ms)` to stagger each round — with duration alone zeroed,
   each node's own animation became instant, but the nodes still *popped in* one after another
   at 70ms intervals, which still reads as staggering even though nothing visibly slides.
   Fixed by adding `animation-delay: 0s !important` to the same rule. Verified via the parsed
   CSSOM (browser-confirmed the rule text, universal selector and `!important` priority are all
   correct) rather than by eye — see the reduced-motion section below for why a literal live
   render wasn't possible.

## Full pass

### Viewports — 375, 768, 1440px

Checked programmatically (`document.documentElement.scrollWidth` vs `clientWidth`, and the
smallest computed `font-size` among visible text nodes) at every width, on: the hero, the
register grid, the map, an open detail window, and every static page (`about.html`,
`impressum.html`) plus `admin.html`. Screenshots taken at each width as a visual
cross-check.

**Result: zero horizontal scroll and no text under 12px at any width, on any page or state —
after the two fixes above (map labels, admin `<code>`).** Before those fixes this pass would
have failed at 375px on two different pages.

Visual spot-checks: topbar wraps to two rows below 480px as designed; the register grid drops
to two columns at the same breakpoint; the map's city labels stay legible without overlapping;
the detail window's figure cards reflow from four-across (1440px) to stacked (375px) cleanly;
dual-HQ text ("Freiburg · also San Francisco") doesn't collide with the metadata line at any
width; the Impressum's placeholder warnings stay fully legible and un-clipped at 375px.

### Keyboard only, no mouse

**Tooling note:** this pane's synthetic key dispatch was unreliable for anything except `Tab`
and `Escape` — `Enter`/`Space`/`Return` consistently arrived at the page with an empty
`event.key`, so the site's own `keydown` handlers (which check `event.key`) never saw them, and
a real OS-level `Escape` did not reach the native dialog's cancel handling either (both
reproduced independently of any site code — the same class of "ESC-key automation limitation"
already recorded in this project's history from Task 8's development). Distinguishing "the tool
can't dispatch this" from "the site is broken" mattered a great deal here; every finding below
was cross-checked against real, live application state (DOM, `location.hash`, `aria-checked`,
focus), not inferred from a keypress that might not have landed.

**Tab order** — confirmed twice: once via real `Tab` keypresses, once via a faithful DOM-order
walk (this site uses no positive `tabindex` anywhere — confirmed by grep — so visible,
non-negative-tabindex DOM order *is* the real order). Both agree exactly:
skip link → topbar wordmark → Companies/Map toggles → About → Search → freshness link
→ search input → sort select → city select → sector chips (**one** tab stop, "All sectors" —
roving tabindex correctly removes the other ~28 chips from the tab sequence) → grid cells. The
hidden topbar/register correctly contribute nothing to the tab order before "Enter the
register" is activated (the `[hidden]` cascade fix from earlier tasks holds).

**Opening a company** — a focused grid cell activated via Enter/Space (native button
activation, which is what dispatches a `click` event either way) opens the dialog, moves focus
to the visible close button, sets `dialog.open = true`, and updates the URL to `#/<slug>`.
The dialog is opened with `showModal()` (confirmed in `detail.js`), which gives it a
**native, browser-guaranteed focus trap** — not custom code, so its correctness doesn't depend
on this pane's flaky key dispatch.

**Closing and focus return** — verified end-to-end, in one atomic script so no state could be
lost between calls: focus a grid cell → activate it (dialog opens, focus → close button) →
activate the close button → dialog closes, `#/<slug>` is cleared, `body.style.overflow` resets,
**and focus returns to the exact origin cell**. Real `Escape` could not be made to reach the
native dialog in this pane (see the tooling note above) — including on a bare, throwaway
`<dialog>` element with zero site code involved, which is what confirms this is an environment
limitation and not a defect. The close-button path exercises the *application's* cleanup code
identically to what an `Escape` would (`closeDetail()`); the one thing it doesn't re-prove is
the native "Escape cancels a modal dialog" mechanism itself, which is a browser guarantee, not
custom code.

**Sector chips as a radiogroup** — dispatched real `ArrowRight`/`Home`/`End` keydown events at
the chip container and confirmed against live state: `ArrowRight` moved both focus and
`aria-checked` from "All sectors" to "Artificial Intelligence" and updated the roving
`tabindex` on both chips (`0`→`-1`, `-1`→`0`); the visible count updated (27→6); `End` jumped to
the last chip ("Travel"); `Home` returned to "All sectors" and the count back to 27.

**Every map city, Enter and Space** — confirmed structurally that all 8 rendered cities have
`tabIndex === 0` and a non-empty `aria-label`, then dispatched real `Enter` on Hamburg and real
`Space` on Freiburg (different cities, both keys) — both correctly filtered the grid to that
city, in both cases via the city dropdown's own `setCity()`, matching Task 7's ruling that the
map must never bypass the controls module.

### Reduced motion

Verified **by counting `requestAnimationFrame` and `Element.animate` calls**, not by eye, per
the brief — using a patched `window.matchMedia` and cache-busted dynamic `import()`s so each
module's module-level `const REDUCED = matchMedia(...)` re-evaluates against the override (this
site's own documented reason `prefers-reduced-motion` can't be read from plain CSS for the
canvas loop applies equally to testing it: JS state, needs a JS-level override).

| Check | Normal motion | Reduced motion |
|---|---|---|
| Constellation `requestAnimationFrame` calls | ≥1 (loop scheduled) | **0** |
| Constellation `.running` after `start()` | — | **false** |
| Transition `Element.animate` calls | — | **0** |
| Transition: hero hidden, register shown | — | **yes, no animation** |
| Transition: `.is-entering` scroll lock removed afterwards | **yes** | **yes** |
| Detail dialog `Element.animate` calls | 1 | **0** |
| Detail dialog still opens (`showModal`) | — | **yes** |

The funding timeline's staggering is CSS-driven (`animation-delay`), not JS-driven, so it can't
be tested the same way — and this pane's ambient `prefers-reduced-motion` is `false` with no
in-scope way to flip it (the OS-level accessibility setting is out of bounds for this pass; not
a browser-devtools-only override this environment exposes a tool for). Verified instead via the
browser's own parsed CSSOM: fetched the actual `@media (prefers-reduced-motion: reduce)` rule
from `document.styleSheets` and confirmed the selector (`*, ::before, ::after` — universal,
guaranteed to match `.timeline__node`), the property (`animation-delay`), the value (`0s`) and
the priority (`important`) are all exactly right. Combined with the media query itself being
browser-native (guaranteed to activate correctly when the real preference is set — not
something this site's code can get wrong), this is as strong a verification as was available
without an OS-level change, and it is what caught the one real gap in this section (see fix #4
above).

### Contrast

`python3 tools/check_contrast.py` → **exit 0**, every token pair clears 4.5:1 (worst case
`--violet` on `--panel-hover`, 5.40:1). Spot-checked the pairs the token matrix can't see by
composition alone:

- **Muted metadata on a glass cell** (`.cell__meta`, "Last round · …") — legible in every
  screenshot at every width; token pair is `--muted` on `--panel` (composited over `--void`),
  which the checker's `--panel`-over-`--deep` case already covers conservatively (`--deep` is
  the *lighter* of the two base surfaces, so if text passes against it, it passes by a wider
  margin against the darker `--void` composite too — same reasoning applies to every other
  `--panel`/`--panel-hover` pair below).
- **Amber aged badge** (`.cell__aged`, `.badge-note__aged`) — visibly legible throughout; token
  pair `--amber` on `--panel`, 7.90:1.
- **Disputed note** (`.fig__disputed`, e.g. Moss's valuation dialog) — visibly legible; same
  `--amber` on `--panel` pair.
- **Link text inside the detail window** (source citations, disputed-note source link) —
  visibly legible; `--beam-text` on `--panel`, 8.22:1.
- **Text over the white logo plate** — the one pair that was genuinely broken; see fix #1 above.
  Now `--plate-ink` on `--plate`, 17.04:1.

### Requests

Read the network log across every page and state exercised in this pass (hero, register, map,
detail, deep link, about/impressum/admin) — **every single request targets `localhost`**
(the dev server itself: HTML, CSS, JS, fonts, `data/companies.json`, `data/fx.json`,
`data/geo/germany.json`, every logo). Zero third-party requests anywhere.

### Console

Clean — zero console messages — on every page tested: `index.html` (hero, register, map,
detail open/closed), `index.html#/helsing` (deep link, dialog opens directly on load with no
errors), `about.html`, `impressum.html`, `admin.html`.

**One behavioural observation, not a defect:** a deep link (`#/helsing`) opens the correct
dialog immediately, but doesn't also reveal the register underneath — closing the dialog lands
back on the hero (fully functional, "Enter the register" still one click away), not the grid.
No broken state, no console error; recording it here in case a future pass wants the register
pre-revealed for deep links.

## Verification

```
python3 tools/validate.py   # All records valid.
python3 tools/build.py      # Built 27 companies -> data/companies.json (byte-identical, no diff)
python3 -m pytest           # 154 passed
python3 tools/check_contrast.py   # exit 0
```

Tree clean apart from the five files this pass touched: `assets/js/map.js`, `assets/js/admin.js`,
`assets/css/register.css`, `assets/css/admin.css`, `assets/css/base.css`.
