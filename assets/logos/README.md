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
| `celonis.svg` | https://www.celonis.com/src/assets/icons/logo.svg | 2026-08-08 | Downloaded unchanged |
| `deepl.svg` | https://www.deepl.com/img/logo/deepl-logo-text-blue.svg | 2026-08-08 | Downloaded unchanged |
| `helsing.svg` | https://helsing.ai/ (header mark, inline SVG) | 2026-08-08 | Copied verbatim from the page |
| `moss.svg` | https://www.getmoss.com/favicon/icon.svg | 2026-08-08 | Downloaded unchanged |
| `n26.svg` | https://n26.com/en-eu/press (header wordmark, inline SVG) | 2026-08-08 | Copied verbatim; `xmlns` added |
| `parloa.svg` | https://www.parloa.com/ (header wordmark, inline SVG) | 2026-08-08 | Copied verbatim from the page |
| `personio.svg` | https://www.personio.com/ (header wordmark, inline SVG) | 2026-08-08 | Copied verbatim from the page |
| `trade-republic.svg` | https://traderepublic.com/en-de (header wordmark, inline SVG) | 2026-08-08 | Copied verbatim from the page |

## Notes

- **Helsing** publishes only the square "H" mark, not a wordmark, so that is what is stored.
- **Moss** publishes no wordmark file. The mark in its site header
  (`mosslogomark.svg`) is drawn at 17 × 14 px and is illegible on the register's plate,
  so the stored file is Moss's own brand tile as served at `/favicon/icon.svg` — the same
  mark, in Moss's own colours, at a size that reads. Neither file was edited.
- Several files use `fill="currentColor"`. Rendered as an `<img>` on the register's light
  plate, that resolves to black, which is how each company shows the mark on light
  backgrounds. No colour value was edited.
