# Design system — German Unicorns

Locked. This file supersedes `design-system/german-unicorns/MASTER.md`, whose generated
defaults (light background, pink accent, Orbitron) contradict the approved brief.

## Direction: Constellation

Near-black, cinematic, institutional. The constellation is the dataset — each point of
light is one company — and it becomes the grid in one continuous motion. That transition
is the signature; everything else stays quiet.

## Colour

| Token | Hex | Use |
|---|---|---|
| `--void` | `#07080B` | Page |
| `--deep` | `#0C0E14` | Raised surfaces |
| `--panel` | `rgba(255,255,255,.045)` | Glass cells over `--deep` |
| `--stroke` | `rgba(255,255,255,.10)` | Hairlines, cell borders |
| `--ink` | `#ECEEF3` | Primary text |
| `--muted` | `#9AA1B1` | Metadata and labels (4.5:1 on `--void`) |
| `--beam` | `#4C7DFF` | Graphics, particles, focus ring |
| `--beam-text` | `#8FB0FF` | Link and accent **text** only (4.5:1 on `--void`) |
| `--violet` | `#A97BFF` | Gradient partner; the €1bn marker |
| `--amber` | `#E0A24B` | Aged and disputed signals |
| `--plate` | `#F7F8FA` | The white plate logos sit on |

Two accents exist because `--beam` is a graphics colour and fails 4.5:1 as text. Never set
type in `--beam`.

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
opacity fade.

## Discipline

Glow is a signal — hover, the €1bn marker — never ambient. Logos are never altered. Numbers are
always mono, always beside their date. One bold element per screen; everything else recedes.
