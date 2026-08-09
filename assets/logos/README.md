# Logos

Every file here was taken from the company's own website or press kit and is stored
**unaltered** — no recolouring, cropping, masking or re-drawing. Where a logo is served
inline in the page rather than as a downloadable file, the `<svg>` element was copied
verbatim from the live page; the only change permitted in that case is adding the
`xmlns="http://www.w3.org/2000/svg"` attribute a standalone file needs and an inline
fragment inherits from its host document. Any such change is noted per file below.

Logos are the trademarks of their owners and appear here to identify the company. They
are not covered by this repository's licence.

| File | Source URL | Retrieved | How |
|---|---|---|---|
| `black-forest-labs.svg` | https://bfl.ai/ (navbar wordmark, inline SVG) | 2026-08-08 | Copied verbatim from the page |
| `celonis.svg` | https://www.celonis.com/src/assets/icons/logo.svg | 2026-08-08 | Downloaded unchanged |
| `choco.svg` | https://choco.com/us/press (header wordmark, inline SVG) | 2026-08-08 | Copied verbatim; see note |
| `commercetools.svg` | https://cdn.prod.website-files.com/6989ba4b19f7ea51fb4fc517/698c995a04b388752a6f3f2a_commercetools-logo-2024-B4HERo5H.svg | 2026-08-08 | Downloaded unchanged |
| `forto.svg` | https://forto.com/wp-content/themes/forto-website/assets/images/logo.svg | 2026-08-08 | Downloaded unchanged |
| `osapiens.png` | https://osapiens.com/wp-content/uploads/2024/05/65081d253c3c6d169ca690f0_favicon.png | 2026-08-08 | Downloaded unchanged; see note |
| `razor-group.svg` | https://cdn.prod.website-files.com/659bd12259ec13f287424e42/659bd12259ec13f28742502c_razor%20logo-blu-01.svg | 2026-08-08 | Downloaded unchanged |
| `staffbase.svg` | https://www.staffbase.com/en/about-us/ (header wordmark, inline SVG sprite) | 2026-08-08 | Copied verbatim; see note |
| `taxfix.svg` | https://taxfix.de/en/about-us/ (header wordmark, inline SVG) | 2026-08-08 | Copied verbatim; `xmlns` added |
| `deepl.svg` | https://www.deepl.com/img/logo/deepl-logo-text-blue.svg | 2026-08-08 | Downloaded unchanged |
| `helsing.svg` | https://helsing.ai/ (header mark, inline SVG) | 2026-08-08 | Copied verbatim from the page |
| `moss.svg` | https://www.getmoss.com/favicon/icon.svg | 2026-08-08 | Downloaded unchanged |
| `n26.svg` | https://n26.com/en-eu/press (header wordmark, inline SVG) | 2026-08-08 | Copied verbatim; `xmlns` added |
| `parloa.svg` | https://www.parloa.com/ (header wordmark, inline SVG) | 2026-08-08 | Copied verbatim from the page |
| `personio.svg` | https://www.personio.com/ (header wordmark, inline SVG) | 2026-08-08 | Copied verbatim from the page |
| `trade-republic.svg` | https://traderepublic.com/en-de (header wordmark, inline SVG) | 2026-08-08 | Copied verbatim from the page |
| `1komma5.svg` | https://1komma5.com/en/about-us/ (header mark, inline SVG) | 2026-08-08 | Copied verbatim; see note |
| `enpal.svg` | https://www.enpal.de/ueber-uns (header wordmark, inline SVG) | 2026-08-08 | Copied verbatim from the page |
| `proxima-fusion.png` | https://cdn.prod.website-files.com/65b10cc303e570e609b235c8/66163bb5ce1eda0f3c9cecdc_webclip.png | 2026-08-08 | Downloaded unchanged; see note |
| `scalable-capital.png` | https://assets.scalable.capital/touch-icons/apple-touch-icon.png | 2026-08-08 | Downloaded unchanged; see note |
| `sennder.svg` | https://a.storyblok.com/f/341309/ce59cf62f1/logo.svg | 2026-08-08 | Downloaded unchanged; see note |
| `flix.svg` | https://corporate.flix.com/wp-content/uploads/2024/04/Logo.svg | 2026-08-09 | Downloaded unchanged |
| `finn.svg` | https://www.finn.com/en-DE (header wordmark, inline SVG) | 2026-08-09 | Copied verbatim; see note |
| `cmblu.png` | https://cdn.prod.website-files.com/69cbaf5e811b5d975e23932c/69cbf10a32d894b7f979062e_webclip.png | 2026-08-09 | Downloaded unchanged; see note |
| `dash0.png` | https://www.dash0.com/apple-touch-icon.png | 2026-08-09 | Downloaded unchanged; see note |
| `n8n.png` | https://n8n.io/apple-touch-icon.png | 2026-08-09 | Downloaded unchanged; see note |
| `stark.svg` | https://stark-defence.com (preloader mark, inline SVG) | 2026-08-09 | Copied verbatim from the page |

## Notes

- **Helsing** publishes only the square "H" mark, not a wordmark, so that is what is stored.
- **Moss** publishes no wordmark file. The mark in its site header
  (`mosslogomark.svg`) is drawn at 17 × 14 px and is illegible on the register's plate,
  so the stored file is Moss's own brand tile as served at `/favicon/icon.svg` — the same
  mark, in Moss's own colours, at a size that reads. Neither file was edited.
- Several files use `fill="currentColor"`. Rendered as an `<img>` on the register's light
  plate, that resolves to black, which is how each company shows the mark on light
  backgrounds. No colour value was edited.
- **Choco** serves its wordmark inline with two attributes an HTML parser tolerates but a
  standalone SVG file does not: `viewbox` in lowercase, and a leading space inside the
  `xmlns` value. Both were corrected (`viewBox`, and the space removed) so the file parses
  as XML; nothing else — no path, no colour, no dimension — was touched. Its fill comes
  from the page's `fill-current` class, which a standalone file does not carry, so it
  renders black, as Choco shows the mark on white.
- **Staffbase** serves its wordmark as an SVG `<symbol>` inside a hidden sprite, referenced
  by `<use>`. The symbol's contents were copied verbatim into a standalone `<svg>` carrying
  that symbol's own `viewBox` and the required `xmlns`. No path data or colour was changed.
- **FINN** serves its wordmark inline in the site header, already the black variant (the
  file its own markup calls `FINN-black`). The `<svg>` element was copied verbatim,
  including the `<defs><clipPath>` its paths reference — without that block the mark
  clips to nothing in a standalone file. Nothing was recoloured or redrawn.
- **CMBlu** and **Dash0** both publish only a light-on-dark wordmark, invisible on the
  register's light plate: CMBlu's letters are `#FFF9FB` and Dash0's single path is
  `fill="white"`. Neither company serves a dark variant anywhere the site exposes —
  CMBlu's press page links the same white file as its header. The stored files are
  therefore each company's own site icon, served from its own property, in its own
  colours, unaltered. This is the osapiens case again, and the same rule applies: use a
  smaller official mark rather than edit a logo to make it legible.

- **osapiens** publishes only white and on-dark logo files (`osapiens_logo_white.png`,
  `osapiens_logo_onDark_horzR-1.png`), both of which are invisible on the register's light
  plate. The stored file is therefore osapiens's own site icon — the same teal mark, in the
  company's own colour, unaltered. It is a 32 × 32 raster and so renders smaller than the
  other marks; the plate does not upscale it, so it stays crisp.
- **commercetools** and **Razor Group** serve their logos from the Webflow CDN their own
  sites run on rather than from their own domain. The URL recorded above is the exact asset
  each company's own page loads. The same is true of **Proxima Fusion** (Webflow) and
  **sennder** (Storyblok): each URL above is the file that company's own page requests.
- **1KOMMA5°** takes its colour from the page's `fill-brand-aubergine-500` class rather than
  from a `fill` attribute, so a standalone file — which does not carry that class — renders
  black. No colour value was edited, and the same is true of the `currentColor` files above.
  The company also serves an `/icon.svg`, but that file is byte-broken: the degree sign in
  "1K5°" is a raw `0xB0`, which is not valid UTF-8 and so fails to parse as XML at all.
- **Proxima Fusion** and **Scalable Capital** both publish their wordmarks only as light
  artwork for dark backgrounds — Proxima's `Typo.svg` is `#cedde8`, and Scalable's header
  mark is drawn by script rather than served as a file. The stored files are therefore each
  company's own webclip/touch icon: the same mark, in the company's own colours, on the
  company's own tile, unaltered. Both are rasters (256 × 256 and 180 × 180) and so render
  smaller than the vector marks; the plate does not upscale them, so they stay crisp.
- **sennder** serves two variants; the stored file is the orange-on-transparent
  `logo.svg` its own site uses, not the all-white `logo-invert.svg` for dark backgrounds.
- **n8n** serves its header mark as an inline SVG (icon + "n8n" wordmark, both as vector
  paths) whose paths carry no `fill` of their own — colour comes entirely from a
  `.path-icon`/`.path-name` class pair the site's own stylesheet resolves per `data-theme`,
  and in every theme the homepage uses, `.path-name` resolves to white or near-white
  (`fill:#fff`, `fill:#fffc`), meant for a dark navbar. Copied out of that stylesheet's
  context the paths inherit the root `<svg>`'s `fill="none"` and render nothing at all, so a
  verbatim copy was not viable the way it was for Helsing or FINN. The stored file is instead
  n8n's own `apple-touch-icon.png` — its pink flame mark, unaltered, on n8n's own opaque white
  tile — the same precedent as Proxima Fusion and Scalable Capital's touch icons above. It is
  a 180 × 180 raster and so renders smaller than the vector wordmarks; the plate does not
  upscale it, so it stays crisp.
- **Stark** serves its mark only inside the loading-screen preloader of its own homepage, as
  an inline SVG; there is no separate downloadable file and no mark in the page's permanent
  header. The `<svg>` element was copied verbatim, including its native `xmlns` (no attribute
  needed adding, unlike the sprite- and fragment-served marks above). Nothing was recoloured
  or redrawn.
