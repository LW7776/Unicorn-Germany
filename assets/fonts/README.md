# Self-hosted fonts

These `woff2` files are vendored into the repository and served from this site's own origin.
The site must **never** link to the Google Fonts CDN (`fonts.googleapis.com` /
`fonts.gstatic.com`) at request time — embedding it has been ruled a GDPR breach by German
courts (LG München I, 20 O 13058/20), and this site carries an Impressum. The files below were
downloaded once, on the date noted, and are committed as static assets.

Each file is the **latin** subset (`unicode-range: U+0000-00FF …`) served by the Google Fonts
CSS API for the given family, fetched with a browser-like User-Agent so the API returned
`woff2` rather than a legacy format.

| File | Family | Source URL | Date | Licence |
|---|---|---|---|---|
| `archivo-variable.woff2` | Archivo (variable: `wdth` 62–125, `wght` 400–800) | https://fonts.gstatic.com/s/archivo/v25/k3kQo8UDI-1M0wlSfdnoLmvDIaI.woff2 | 2026-08-06 | SIL Open Font License 1.1 |
| `source-serif-4-variable.woff2` | Source Serif 4 (variable: `opsz` 8–60, `wght` 300–700) | https://fonts.gstatic.com/s/sourceserif4/v14/vEFI2_tTDB4M7-auWDN0ahZJW1gb8te1Xb7G.woff2 | 2026-08-06 | SIL Open Font License 1.1 |
| `ibm-plex-mono-400.woff2` | IBM Plex Mono (weight 400) | https://fonts.gstatic.com/s/ibmplexmono/v20/-F63fjptAgt5VM-kVkqdyU8n1i8q131nj-o.woff2 | 2026-08-06 | SIL Open Font License 1.1 |

All three URLs were resolved from the Google Fonts CSS API request:

```
https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..800&family=Source+Serif+4:opsz,wght@8..60,300..700&family=IBM+Plex+Mono:wght@400&display=swap
```

Each downloaded file was verified to be a genuine WOFF2 (first four bytes `wOF2`, `0x77 0x4F
0x46 0x32`) before being committed:

- `archivo-variable.woff2` — 90,096 bytes
- `source-serif-4-variable.woff2` — 122,168 bytes
- `ibm-plex-mono-400.woff2` — 10,052 bytes

`assets/css/base.css` declares `@font-face` rules pointing at these three files by relative
path (`../fonts/…` from `assets/css/`). No other CSS or HTML in this project may reference a
Google Fonts URL.
