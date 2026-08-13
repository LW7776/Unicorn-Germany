"""Build the Claude Design bundle out of the shipped stylesheets.

One preview file per component, each self-contained, each carrying the @dsCard
marker the Design System pane builds its index from. Written into
design-system/claude-design/ and pushed from there by the DesignSync tool.

The point of generating rather than hand-writing these: the tokens block in
every preview is read out of assets/css/tokens.css, so a card in Claude Design
cannot drift from the site it documents. Re-run this after any token change and
push again.
"""
import base64
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "design-system" / "claude-design"

# IBM Plex Mono is 10 KiB and carries most of this system's character, so it
# goes into every preview. Archivo and Source Serif are 90 and 122 KiB and go
# only where the specimen is about them.
FONT_FILES = {
    "mono": "ibm-plex-mono-400.woff2",
    "display": "archivo-variable.woff2",
    "prose": "source-serif-4-variable.woff2",
}


def data_uri(path, mime):
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"


def font_face(role):
    path = ROOT / "assets" / "fonts" / FONT_FILES[role]
    uri = data_uri(path, "font/woff2")
    families = {
        "mono": ('"IBM Plex Mono"', "400", ""),
        "display": ('"Archivo"', "400 800", "font-stretch:62% 125%;"),
        "prose": ('"Source Serif 4"', "300 700", ""),
    }
    family, weight, extra = families[role]
    return (f'@font-face{{font-family:{family};src:url({uri}) format("woff2");'
            f"font-weight:{weight};{extra}font-display:swap}}")


def logo(slug):
    return data_uri(ROOT / "assets" / "logos" / f"{slug}.svg", "image/svg+xml")


def tokens_block():
    """The :root block straight out of the shipped stylesheet, comments stripped."""
    css = (ROOT / "assets" / "css" / "tokens.css").read_text(encoding="utf-8")
    root = re.search(r":root\s*\{(.*?)\n\}", css, re.DOTALL).group(1)
    root = re.sub(r"/\*.*?\*/", "", root, flags=re.DOTALL)
    lines = [line.strip() for line in root.splitlines() if line.strip()]
    return ":root{\n  " + "\n  ".join(lines) + "\n}"


BASE_CSS = """
*,*::before,*::after{box-sizing:border-box}
body{margin:0;background:var(--void);color:var(--ink);
  font-family:var(--font-mono);font-size:var(--step-0);line-height:1.55;
  -webkit-font-smoothing:antialiased;padding:var(--space-6)}
h1,h2,h3{font-family:var(--font-display);font-weight:800;font-stretch:112%;
  letter-spacing:-.02em;line-height:.95;margin:0}
p{margin:0}
a{color:var(--beam-text)}
.label{font-size:var(--step--1);letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
.spec{display:grid;gap:var(--space-6);max-width:60rem}
.spec__head{display:grid;gap:var(--space-2)}
.spec__head h1{font-size:var(--step-2)}
.spec__note{color:var(--muted);font-size:var(--step--1);max-width:44rem}
.rules{margin:0;padding-left:1.1rem;display:grid;gap:var(--space-2);
  color:var(--muted);font-size:var(--step--1);max-width:44rem}
.rules b{color:var(--ink);font-weight:400}
.frame{padding:var(--space-6);border:1px solid var(--stroke);border-radius:var(--radius);
  background:var(--deep)}
"""


def page(path, group, name, subtitle, title, note, body, extra_css="",
         fonts=("mono",), rules=()):
    """One preview file. The @dsCard marker has to be the first line."""
    faces = "".join(font_face(role) for role in fonts)
    rule_list = ""
    if rules:
        items = "".join(f"<li>{rule}</li>" for rule in rules)
        rule_list = f'<ul class="rules">{items}</ul>'
    html = f"""<!-- @dsCard group="{group}" name="{name}" subtitle="{subtitle}" -->
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
{faces}
{tokens_block()}
{BASE_CSS}{extra_css}
</style>
</head>
<body>
<div class="spec">
  <div class="spec__head">
    <p class="label">{group}</p>
    <h1>{title}</h1>
    <p class="spec__note">{note}</p>
  </div>
  {body}
  {rule_list}
</div>
</body>
</html>
"""
    target = OUT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding="utf-8")
    return target


# --------------------------------------------------------------------------
# Foundations
# --------------------------------------------------------------------------
BASE_TOKENS = [
    ("--void", "#07080B", "Page ground"),
    ("--deep", "#0C0E14", "Raised surfaces, dialogs"),
    ("--panel", "rgba(255,255,255,.045)", "Cards over the ground"),
    ("--panel-hover", "rgba(255,255,255,.075)", "The same on hover"),
    ("--stroke", "rgba(255,255,255,.10)", "Hairlines and card borders"),
    ("--ink", "#ECEEF3", "Primary text"),
    ("--muted", "#9AA1B1", "Metadata, labels, captions"),
    ("--beam", "#4C7DFF", "Graphics, focus ring, bar fills. Never type"),
    ("--beam-text", "#8FB0FF", "Link and accent text only"),
    ("--violet", "#A97BFF", "Gradient partner, the crossing marker"),
    ("--amber", "#E0A24B", "Every caveat, and never a third accent"),
    ("--plate", "#F7F8FA", "The white plate a logo sits on"),
    ("--plate-ink", "#14161A", "Text on the plate, and nowhere else"),
]

DEPTH_TOKENS = [
    ("--rule", "--ink at 16%", "The hairline under a figure"),
    ("--track", "--ink at 7%", "The unfilled part of a threshold bar"),
    ("--ghost-ink", "--ink at 5%", "The oversized wordmark behind the hero"),
    ("--ambient-beam", "--beam at 8%", "Pool one of the field behind the register"),
    ("--ambient-violet", "--violet at 6%", "Pool two"),
    ("--plate-inset", "--plate-ink at 20%", "Seats a logo plate into its card"),
    ("--plate-inset-ring", "--plate-ink at 9%", "The ring around that plate"),
]

SWATCH_CSS = """
.swatches{display:grid;gap:var(--space-3)}
.swatch{display:grid;grid-template-columns:4.5rem 1fr;gap:var(--space-4);align-items:center;
  padding:var(--space-3);border:1px solid var(--stroke);border-radius:10px}
.swatch__chip{height:3rem;border-radius:8px;border:1px solid var(--stroke)}
.swatch__meta{display:grid;gap:2px;min-width:0}
.swatch__name{font-size:var(--step-0);color:var(--ink)}
.swatch__value{font-size:var(--step--1);color:var(--muted)}
.swatch__use{font-size:var(--step--1);color:var(--muted)}
"""


def swatch_rows(rows):
    out = []
    for name, value, use in rows:
        out.append(f"""
      <div class="swatch">
        <span class="swatch__chip" style="background:var({name})"></span>
        <span class="swatch__meta">
          <span class="swatch__name">{name}</span>
          <span class="swatch__value">{value}</span>
          <span class="swatch__use">{use}</span>
        </span>
      </div>""")
    return f'<div class="swatches">{"".join(out)}</div>'


page("foundations/colour.html", "Foundations", "Colour", "13 base tokens, dark only",
     "Colour",
     "Dark only, and that is a decision. There is no light theme, no prefers-color-scheme "
     "branch and no toggle. --plate and --plate-ink are the one light surface and exist "
     "solely so company logos sit on the white they were drawn for.",
     swatch_rows(BASE_TOKENS), SWATCH_CSS,
     rules=[
       "<b>Two accents, blue and violet.</b> Amber is not a third: it carries every caveat "
       "on the site, and a second warm colour used decoratively would make a reader work "
       "out which warm thing is a warning.",
       "<b>Never set type in --beam.</b> It fails 4.5:1 as text, which is why --beam-text "
       "exists.",
       "<b>Glow is a signal</b>, meaning hover or the crossing marker, and it never "
       "attaches to an object that is not signalling.",
       "If something needs emphasis, reach for weight, size or space before colour.",
       "Raw hex appears in the token file and nowhere else.",
     ])

page("foundations/depth.html", "Foundations", "Depth", "7 cues, each a strength of a base token",
     "Depth",
     "The page is layered rather than flat, and every layer is a new strength of a colour "
     "already in the base table. Blue and violet stay the only accents.",
     swatch_rows(DEPTH_TOKENS), SWATCH_CSS,
     rules=[
       "<b>A depth cue is never legible as a colour.</b> The moment one reads as blue "
       "rather than as distance it has started competing with the content in front of it.",
       "<b>Each one is carried in the contrast checker.</b> Glass over both ambient pools "
       "is the lightest surface any body text meets, and it still has to clear 4.5:1. "
       "Changing a percentage here means changing it there.",
     ])

TYPE_CSS = """
.faces{display:grid;gap:var(--space-5)}
.face{display:grid;gap:var(--space-2);padding:var(--space-5);
  border:1px solid var(--stroke);border-radius:var(--radius)}
.face__sample{font-size:var(--step-3);line-height:1.1}
.face--display .face__sample{font-family:var(--font-display);font-weight:800;font-stretch:112%;
  letter-spacing:-.02em}
.face--prose .face__sample{font-family:var(--font-prose);font-size:var(--step-1);line-height:1.6}
.face--mono .face__sample{font-family:var(--font-mono);font-size:var(--step-1)}
.face__role{color:var(--muted);font-size:var(--step--1)}
.scale{display:grid;gap:var(--space-4);margin-top:var(--space-4)}
.scale__row{display:grid;grid-template-columns:6rem 1fr;gap:var(--space-4);align-items:baseline;
  padding-bottom:var(--space-3);border-bottom:1px solid var(--stroke)}
.scale__token{color:var(--muted);font-size:var(--step--1)}
.scale__sample{line-height:1.1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
"""

SCALE = [("--step--1", "Labels, metadata, captions"), ("--step-0", "Body"),
         ("--step-1", "Card figures"), ("--step-2", "Section headings"),
         ("--step-3", "Dialog titles"), ("--step-4", "Page titles, headline figures"),
         ("--step-5", "Section openers"), ("--step-6", "The hero statement")]

scale_rows = "".join(
    f'<div class="scale__row"><span class="scale__token">{token}</span>'
    f'<span class="scale__sample" style="font-size:var({token})">{use}</span></div>'
    for token, use in SCALE)

page("foundations/type.html", "Foundations", "Typography", "3 faces, 8 steps",
     "Typography",
     "Three faces, three jobs. Self-hosted woff2, never a font CDN: embedding one has been "
     "ruled a GDPR breach in German courts and this site carries an Impressum.",
     f"""
  <div class="faces">
    <div class="face face--display">
      <p class="face__sample">Made in Germany</p>
      <p class="face__role">Display · Archivo Variable · 700 to 800 · font-stretch 112% · tracking -.02em</p>
    </div>
    <div class="face face--prose">
      <p class="face__sample">Germany has always known how to build. What has changed is who is doing the building now.</p>
      <p class="face__role">Prose · Source Serif 4 · running argument only</p>
    </div>
    <div class="face face--mono">
      <p class="face__sample">€12.5 bn · Dec 2025 · 32 companies</p>
      <p class="face__role">Data · IBM Plex Mono · every figure, label and date, and the body default</p>
    </div>
  </div>
  <div class="scale">{scale_rows}</div>""",
     TYPE_CSS, fonts=("mono", "display", "prose"),
     rules=[
       "The serif is what makes the site read as reported rather than generated. It is "
       "never used for a label, a figure or a date.",
       "The mono is never used for a paragraph of argument.",
       "Every size comes from the scale. Nothing is set outside it.",
       "One label treatment everywhere: --step--1, .14em tracking, uppercase, --muted, "
       "always mono even on a page whose running text is serif.",
     ])

SPACE_CSS = """
.bars{display:grid;gap:var(--space-3)}
.bar{display:grid;grid-template-columns:6rem 1fr;gap:var(--space-4);align-items:center}
.bar__token{color:var(--muted);font-size:var(--step--1)}
.bar__fill{height:1.5rem;border-radius:3px;
  background:color-mix(in srgb,var(--beam) 35%,transparent);
  border:1px solid color-mix(in srgb,var(--beam) 55%,transparent)}
.shapes{display:flex;gap:var(--space-4);flex-wrap:wrap;margin-top:var(--space-5)}
.shape{display:grid;place-items:center;width:8rem;height:5rem;background:var(--panel);
  border:1px solid var(--stroke);color:var(--muted);font-size:var(--step--1)}
.shape--radius{border-radius:var(--radius)}
.shape--nested{border-radius:10px}
.shape--pill{border-radius:999px}
"""

space_bars = "".join(
    f'<div class="bar"><span class="bar__token">--space-{i}</span>'
    f'<span class="bar__fill" style="width:var(--space-{i})"></span></div>'
    for i in range(1, 9))

page("foundations/space.html", "Foundations", "Space and shape", "8 steps, 3 radii, one measure",
     "Space, shape, layout",
     "One content width for every block on the site: --content, 84rem, centred, with a "
     "--space-6 gutter inside it. The reading measure is held on the text rather than by "
     "giving a section a narrower container.",
     f"""
  <div class="bars">{space_bars}</div>
  <div class="shapes">
    <span class="shape shape--radius">--radius 14px</span>
    <span class="shape shape--nested">10px nested</span>
    <span class="shape shape--pill">999px controls</span>
  </div>""",
     SPACE_CSS,
     rules=[
       "<b>--content is a border-box width</b>, so a block's own gutter sits inside it. "
       "Anything aligning from outside adds that gutter itself: "
       "<code>padding-inline: max(var(--space-6), calc((100% - var(--content)) / 2 + var(--space-6)))</code>.",
       "Layout is grid or flex with gap, never per-element margins that collapse or double.",
       "Wide content gets overflow-x on its own container so the page body never scrolls "
       "sideways.",
       "Breakpoints are layout decisions, not devices: 480px one column, 560px ledger "
       "collapse, 600px dialog, 992px two-column lede.",
     ])

MOTION_CSS = """
.moves{display:grid;gap:var(--space-4)}
.move{display:grid;grid-template-columns:9rem 1fr;gap:var(--space-4);align-items:center;
  padding:var(--space-3) 0;border-top:1px solid var(--stroke)}
.move__token{color:var(--muted);font-size:var(--step--1)}
.move__what{font-size:var(--step--1)}
.move__what b{color:var(--ink);font-weight:400}
"""

MOVES = [
    ("--dur-fast", "180ms", "Colour and border changes"),
    ("--dur-med", "240ms", "A hover that travels: a card lifting, a halo swelling"),
    ("--dur-slow", "1200ms", "Reserved for the page-scale move"),
    ("--ease-out", "cubic-bezier(.22, 1, .36, 1)", "Anything arriving"),
    ("hero to register", "820ms cubic-bezier(.65, 0, .35, 1)",
     "Hero and content locked to one distance, one duration and one curve"),
]

page("foundations/motion.html", "Foundations", "Motion", "4 tokens, 4 set pieces",
     "Motion",
     "Hand-rolled: Web Animations API and requestAnimationFrame, no animation library. "
     "Micro-interactions sit in a 150 to 250ms band.",
     '<div class="moves">' + "".join(
         f'<div class="move"><span class="move__token">{token}</span>'
         f'<span class="move__what"><b>{value}</b><br>{use}</span></div>'
         for token, value, use in MOVES) + "</div>",
     MOTION_CSS,
     rules=[
       "<b>The reduced-motion contract.</b> A CSS media query cannot stop a JavaScript "
       "loop, so every animated module checks matchMedia itself and skips scheduling. "
       "Verify by counting, not by looking: with the query forced, both "
       "requestAnimationFrame and Element.animate must stay at zero.",
       "<b>animation-delay is zeroed too</b>, not only animation-duration. Staggering by "
       "timing rather than by motion still fails the requirement.",
       "Anything hidden for a reveal needs a path that reveals it when the animation "
       "cannot run: no observer, a thrown error, no JavaScript, printing.",
       "<b>Body copy is never animated.</b> Anywhere.",
       "The headline arrival plays once a session. An arrival on every visit is a tic.",
     ])

# --------------------------------------------------------------------------
# The signature
# --------------------------------------------------------------------------
FIGURE_CSS = """
.figs{display:grid;gap:var(--space-7);grid-template-columns:repeat(auto-fit,minmax(14rem,1fr));
  align-items:end}
.fig{display:grid;gap:var(--space-2);justify-items:start}
.fig__value{font-family:var(--font-mono);color:var(--ink);font-variant-numeric:tabular-nums;
  line-height:1}
.fig--lg .fig__value{font-family:var(--font-display);font-weight:800;font-stretch:112%;
  font-size:var(--step-4);letter-spacing:-.03em}
.fig--md .fig__value{font-size:var(--step-1)}
.fig--sm .fig__value{font-size:var(--step-0)}
.fig__rule{height:1px;width:100%;background:var(--rule)}
.fig__meta{color:var(--muted);font-size:var(--step--1);white-space:nowrap}
.fig__cap{color:var(--muted);font-size:var(--step--1);margin-top:var(--space-3)}
"""

page("signature/sourced-figure.html", "Signature", "The sourced figure",
     "One unit, three sizes", "The sourced figure",
     "No figure on this site appears without the date it was true and a link to the page "
     "that reports it. That rule is also the visual unit, and it is the one thing this "
     "system is recognised by.",
     """
  <div class="figs">
    <div>
      <div class="fig fig--lg">
        <span class="fig__value">~€110 bn</span>
        <span class="fig__rule"></span>
        <span class="fig__meta">29 of 32 disclosed · 7 Aug 2026</span>
      </div>
      <p class="fig__cap">Large. Display face. A headline aggregate.</p>
    </div>
    <div>
      <div class="fig fig--md">
        <span class="fig__value">$18 bn</span>
        <span class="fig__rule"></span>
        <span class="fig__meta">Jul 2026 · helsing.ai ↗</span>
      </div>
      <p class="fig__cap">Medium. Mono. A company valuation on a card.</p>
    </div>
    <div>
      <div class="fig fig--sm">
        <span class="fig__value">€35 m</span>
        <span class="fig__rule"></span>
        <span class="fig__meta">Aug 2026 · EU-Startups ↗</span>
      </div>
      <p class="fig__cap">Small. Mono. A round in the weekly ledger.</p>
    </div>
  </div>""",
     FIGURE_CSS, fonts=("mono", "display"),
     rules=[
       "The value is mono and --ink. The meta line is --step--1 and --muted. Never the "
       "reverse.",
       "<b>The rule is a hairline.</b> It joins the value to its date and that is its only "
       "job. A rigid repeated unit executed loosely stops being a signature and becomes a "
       "table.",
       "Figures always carry font-variant-numeric: tabular-nums.",
       "<b>On a card the link goes to the company</b>, because a card is an index. The "
       "evidence lives on the detail surface. Never present a navigational link as if it "
       "were a citation.",
       "A figure nobody published prints <b>Undisclosed</b>, one step down and in --muted, "
       "with an amber >1bn marker beside it. Never a zero, never a dash, never an empty box.",
     ])

# --------------------------------------------------------------------------
# Components
# --------------------------------------------------------------------------
CARD_CSS = """
.grid{display:grid;gap:var(--space-4);grid-template-columns:repeat(auto-fill,minmax(15rem,1fr))}
.cell{position:relative;display:grid;gap:var(--space-3);padding:var(--space-4);
  align-content:start;background:var(--panel);border:1px solid var(--stroke);
  border-radius:var(--radius);
  transition:transform var(--dur-fast) var(--ease-out),
             border-color var(--dur-fast) var(--ease-out),
             box-shadow var(--dur-fast) var(--ease-out)}
.cell:hover{transform:translateY(-3px);
  border-color:color-mix(in srgb,var(--beam) 55%,transparent);
  box-shadow:0 12px 40px -12px color-mix(in srgb,var(--beam) 45%,transparent)}
.cell__plate{display:grid;place-items:center;background:var(--plate);border-radius:10px;
  padding:var(--space-4);height:5.5rem;
  box-shadow:inset 0 1px 3px var(--plate-inset),inset 0 0 0 1px var(--plate-inset-ring)}
.cell__plate img{max-height:3rem;max-width:100%;width:auto;object-fit:contain}
.cell__figure{font-size:var(--step-1);line-height:1.55;min-height:calc(1.55 * var(--step-1));
  display:flex;flex-wrap:nowrap;align-items:center;gap:var(--space-2);
  font-variant-numeric:tabular-nums;min-width:0}
.cell__value{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.cell__figure--undisclosed{color:var(--muted)}
.cell__figure--undisclosed .cell__value{font-size:var(--step-0)}
.cell__rule{height:1px;background:var(--rule)}
.cell__asof{font-size:var(--step--1);color:var(--muted);
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.cell__site{justify-self:start;max-width:100%;color:var(--beam-text);text-decoration:none;
  padding:var(--space-2) 0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;
  font-size:var(--step--1)}
.cell__site:hover{text-decoration:underline}
.cell__bar{position:relative;height:3px;background:var(--track);border-radius:2px}
.cell__fill{position:absolute;inset:0 auto 0 0;width:var(--fill);border-radius:2px;
  background:linear-gradient(90deg,var(--beam),var(--violet))}
.cell__tick{position:absolute;top:-3px;bottom:-3px;left:var(--at);width:1px;
  background:var(--ink);opacity:.55}
.cell__bar--unknown{background:repeating-linear-gradient(90deg,
  color-mix(in srgb,var(--amber) 45%,transparent) 0 4px,transparent 4px 9px);
  -webkit-mask-image:linear-gradient(90deg,transparent 0,#000 6%,#000 55%,transparent 100%);
  mask-image:linear-gradient(90deg,transparent 0,#000 6%,#000 55%,transparent 100%)}
.cell__foot{display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:baseline;
  gap:var(--space-2);font-size:var(--step--1);color:var(--muted)}
.cell__sector,.cell__year{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.cell__year{font-variant-numeric:tabular-nums}
.badge{flex:none;padding:0 var(--space-2);border-radius:4px;font-size:var(--step--1);
  color:var(--amber);border:1px solid color-mix(in srgb,var(--amber) 45%,transparent)}
"""


def card(slug, value, asof, site, fill, sector, year, badge="", undisclosed=False):
    mark = f'<span class="badge">{badge}</span>' if badge else ""
    bar = (f'<span class="cell__bar cell__bar--unknown"><span class="cell__tick" style="--at:6%"></span></span>'
           if fill is None else
           f'<span class="cell__bar"><span class="cell__fill" style="--fill:{fill}%"></span>'
           f'<span class="cell__tick" style="--at:6%"></span></span>')
    dim = " cell__figure--undisclosed" if undisclosed else ""
    return f"""
      <div class="cell">
        <span class="cell__plate"><img src="{logo(slug)}" alt=""></span>
        <span class="cell__figure{dim}"><span class="cell__value">{value}</span>{mark}</span>
        <span class="cell__rule"></span>
        <span class="cell__asof">{asof}</span>
        <a class="cell__site" href="#0">{site} ↗</a>
        {bar}
        <span class="cell__foot"><span class="cell__sector">{sector}</span>
          <span class="cell__year">{year}</span></span>
      </div>"""


page("components/grid-card.html", "Components", "Grid card", "Uniform height, 6 rows",
     "Grid card",
     "The register's unit. Every card is exactly the same height and every row inside sits "
     "at the same offset as the equivalent row in every other card.",
     f"""<div class="frame"><div class="grid">
       {card('helsing', '$18 bn', 'Jul 2026', 'helsing.ai', 100, 'Defence and Aerospace', '2023')}
       {card('trade-republic', '€12.5 bn', 'Dec 2025', 'traderepublic.com', 75.5, 'Fintech', '2021')}
       {card('moss', '€1 bn', 'Aug 2026', 'getmoss.com', 6, 'Fintech', '2026')}
     </div></div>""",
     CARD_CSS,
     rules=[
       "<b>Every text row is one line tall.</b> Text that will not fit is cut with an "
       "ellipsis, never wrapped. A card that wraps is taller than the one beside it and the "
       "grid stops being a grid.",
       "The figure row carries a min-height of a full-size line, so a value set one step "
       "down does not shorten it.",
       "<b>align-content: start</b> on the card. A grid container defaults to stretch, "
       "which distributes slack into every row of a card stretched to match a neighbour.",
       "The date and the link get separate rows. Sharing one means the layout depends on "
       "how long a domain happens to be.",
       "<b>Optional elements never disappear.</b> A row that cannot render its link renders "
       "it as plain text: a card one line shorter than its neighbours is worse than an "
       "unclickable domain.",
       "<b>The card is a container, not a control.</b> A transparent button is stretched "
       "across it and carries the accessible name, and the link is raised above with "
       "z-index. An anchor inside a button is invalid markup that browsers repair by "
       "discarding one of the two. Handlers key on the button, never the card.",
     ])

page("components/threshold-bar.html", "Components", "Threshold bar", "3px, with an unknown state",
     "Threshold bar",
     "A hairline chart, not a chart. The track runs from zero to the largest value in the "
     "whole set, so every bar is that item against the biggest one, and the tick marks the "
     "threshold that qualified all of them.",
     f"""<div class="frame"><div class="grid">
       {card('helsing', '$18 bn', 'Jul 2026', 'helsing.ai', 100, 'Defence and Aerospace', '2023')}
       {card('moss', '€1 bn', 'Aug 2026', 'getmoss.com', 6, 'Fintech', '2026')}
       {card('helsing', 'Undisclosed', 'reported Sep 2025', 'isaraerospace.com', None,
             'Defence and Aerospace', '2025', badge='&gt;1bn', undisclosed=True)}
     </div></div>""",
     CARD_CSS,
     rules=[
       "<b>Scale is settled server-side, never in the browser.</b> The tick does not move "
       "when the set is filtered: it is a property of the register, not of the view.",
       "<b>A value nobody published gets no fill.</b> It gets dashed amber, masked to fade "
       "out to the right: over the line, ending nowhere in particular. A bar of zero length "
       "says worth nothing, which is the exact misreading the system exists to prevent.",
       "aria-hidden. It is a second reading of the figure printed directly above it, so it "
       "owes a screen reader nothing.",
       "Mixed currencies are converted for the bar only. The printed figure stays in the "
       "currency its source used.",
     ])

STATS_CSS = """
.stats{display:grid;gap:var(--space-6)}
.stats__lead{display:grid;gap:var(--space-6);grid-template-columns:1fr 1fr}
.headstat{display:grid;gap:var(--space-3)}
.headstat__value{font-family:var(--font-display);font-weight:800;font-stretch:112%;
  font-size:var(--step-4);line-height:.95;letter-spacing:-.03em;color:var(--ink);
  font-variant-numeric:tabular-nums}
.headstat__rule{height:1px;background:var(--rule)}
.stats__rank{display:grid}
.rankrow{display:flex;justify-content:space-between;align-items:baseline;gap:var(--space-5);
  padding:var(--space-4) 0;border-top:1px solid var(--stroke);color:inherit;text-decoration:none}
.stats__rank>:last-child{border-bottom:1px solid var(--stroke)}
.rankrow__label{color:var(--muted);font-size:var(--step--1)}
.rankrow__value{font-size:var(--step-0);color:var(--ink);font-variant-numeric:tabular-nums}
.rankrow--link{min-height:44px;align-items:center}
.rankrow--link .rankrow__value{color:var(--beam-text);white-space:nowrap}
.rankrow--link:hover .rankrow__label{color:var(--ink)}
"""

page("components/summary-row.html", "Components", "Summary row", "Two ranks, one link",
     "Summary row",
     "Two figures a visitor came for, set in the display face at headline scale, then the "
     "figures that qualify them as rows underneath. Never a row of equal tiles.",
     """<div class="frame"><div class="stats">
       <div class="stats__lead">
         <div class="headstat">
           <span class="headstat__value">32</span>
           <span class="headstat__rule"></span>
           <span class="label">German unicorns</span>
         </div>
         <div class="headstat">
           <span class="headstat__value">~€110 bn</span>
           <span class="headstat__rule"></span>
           <span class="label">Combined · 29 of 32 disclosed</span>
         </div>
       </div>
       <div class="stats__rank">
         <div class="rankrow"><span class="rankrow__label">New in the last twelve months</span>
           <span class="rankrow__value">11</span></div>
         <div class="rankrow"><span class="rankrow__label">Median years to a billion</span>
           <span class="rankrow__value">6</span></div>
         <a class="rankrow rankrow--link" href="#0"><span class="rankrow__label">Data checked ↗</span>
           <span class="rankrow__value">7 Aug 2026</span></a>
       </div>
     </div></div>""",
     STATS_CSS, fonts=("mono", "display"),
     rules=[
       "The headline figures are the only numbers on the site not set in mono. That is what "
       "makes them read as a headline rather than as two more data points.",
       "<b>Only one row is a link, so only that row carries a mark</b>, takes --beam-text "
       "on its value and answers the pointer. A tile that lifts under the cursor and then "
       "does nothing is a promise the design cannot keep.",
       "tabular-nums, so a rebuild that moves 32 to 33 does not shift the label under it.",
     ])

LEDGER_CSS = """
.ledger{display:grid}
.ledger__row{display:grid;grid-template-columns:1fr auto;align-items:baseline;
  gap:var(--space-1) var(--space-5);padding:var(--space-4) 0;
  border-top:1px solid var(--stroke)}
.ledger__row:last-child{border-bottom:1px solid var(--stroke)}
.ledger__co{color:var(--ink)}
.ledger__amt{text-align:right;white-space:nowrap;color:var(--ink);font-variant-numeric:tabular-nums}
.ledger__sub{grid-column:1;color:var(--muted);font-size:var(--step--1)}
.ledger__src{grid-column:2;text-align:right;font-size:var(--step--1);color:var(--muted);
  white-space:nowrap}
.tracked{color:var(--beam-text);font-size:var(--step--1);margin-left:var(--space-2)}
"""

page("components/ledger-row.html", "Components", "Ledger row", "Money in a column",
     "Ledger row",
     "For lists of money. The company against its amount, with the qualifying detail and "
     "the source on a second line under each. Prose is the wrong shape here: five sentences "
     "put the figure in a different place five times.",
     """<div class="frame"><div class="ledger">
       <div class="ledger__row">
         <span class="ledger__co">PadelCity</span>
         <span class="ledger__amt">€12 m</span>
         <span class="ledger__sub">Investment · Munich · Jonathan Sierck, Sebastian Weil and Markus Englert</span>
         <span class="ledger__src">Tech.eu · 3 Aug 2026 ↗</span>
       </div>
       <div class="ledger__row">
         <span class="ledger__co">EVERSION</span>
         <span class="ledger__amt">€2.3 m</span>
         <span class="ledger__sub">Seed · Konstanz · Julia Zimmermann and Wolfgang Triebstein</span>
         <span class="ledger__src">Tech.eu · 3 Aug 2026 ↗</span>
       </div>
       <div class="ledger__row">
         <span class="ledger__co">Enpal <span class="tracked">in the register</span></span>
         <span class="ledger__amt">€1.2 m</span>
         <span class="ledger__sub">Investment · Munich</span>
         <span class="ledger__src">Tech.eu · 3 Aug 2026 ↗</span>
       </div>
     </div></div>""",
     LEDGER_CSS,
     rules=[
       "Amounts are right-aligned, nowrap and tabular, so the eye runs down the column and "
       "stops where it wants.",
       "<b>Citations go compact:</b> publication and date as the link text, the headline on "
       "the title attribute. A right-hand column of forty-word headlines buries the column "
       "of figures beside it.",
       "Below 560px it becomes one column and everything aligns left. A publication pinned "
       "to the right of a company name has nowhere to go at that width.",
       "A clause with no source is dropped and the sentence closes up around it. Never "
       "invent a value to fill a template.",
     ])

BADGE_CSS = """
.badges{display:flex;flex-wrap:wrap;gap:var(--space-4);align-items:center}
.badge{padding:0 var(--space-2);border-radius:4px;font-size:var(--step--1);color:var(--amber);
  border:1px solid color-mix(in srgb,var(--amber) 45%,transparent)}
.note{display:block;font-size:var(--step--1);color:var(--muted);margin-top:var(--space-5);
  padding:var(--space-2) var(--space-3);
  border-left:2px solid color-mix(in srgb,var(--amber) 55%,transparent);background:var(--panel)}
.note__badge{color:var(--amber);text-transform:uppercase;letter-spacing:.12em;
  font-size:var(--step--1);margin-right:var(--space-2)}
.note__text{color:var(--ink)}
"""

page("components/markers.html", "Components", "Markers and notes", "4 markers, one note block",
     "Markers and notes",
     "Every caveat on the site is amber and shares one shape. A marker is a qualification "
     "on a figure, never an error state.",
     """<div class="frame">
       <div class="badges">
         <span class="badge">aged</span>
         <span class="badge">&gt;1bn</span>
         <span class="badge">disputed</span>
         <span class="badge">undisclosed</span>
       </div>
       <span class="note">
         <span class="note__badge">disputed</span>
         <span class="note__text">The $1.7bn often quoted is enterprise value, counting about
         $400m of debt.</span> · <a href="#0">Source ↗</a>
       </span>
     </div>""",
     BADGE_CSS,
     rules=[
       "<b>aged</b>: positive reason to think the figure has been overtaken. "
       "<b>&gt;1bn</b>: over the threshold, amount unpublished. "
       "<b>disputed</b>: sources disagree and both are shown. "
       "<b>undisclosed</b>: no figure was ever published.",
       "<b>Keep them rare.</b> A marker on half the set is wallpaper, and the register "
       "deliberately flags 4 of 32.",
       "A note stays under fifteen words and always carries its own source link.",
       "Amber is not a third accent. It is reserved for exactly this.",
     ])

CONTROL_CSS = """
.row{display:flex;flex-wrap:wrap;gap:var(--space-4);align-items:center;margin-bottom:var(--space-5)}
.btn{display:inline-flex;gap:var(--space-3);align-items:center;min-height:44px;
  padding:var(--space-4) var(--space-6);border-radius:999px;border:1px solid var(--stroke);
  background:var(--panel);color:var(--ink);font:inherit;font-size:var(--step--1);
  letter-spacing:.14em;text-transform:uppercase;cursor:pointer;
  transition:background var(--dur-fast) var(--ease-out),border-color var(--dur-fast) var(--ease-out)}
.btn:hover{background:var(--panel-hover);border-color:var(--beam)}
.chip{min-height:44px;padding:var(--space-2) var(--space-4);border-radius:999px;
  background:transparent;border:1px solid var(--stroke);color:var(--muted);font:inherit;
  font-size:var(--step--1);cursor:pointer;
  transition:color var(--dur-fast) var(--ease-out),border-color var(--dur-fast) var(--ease-out),
             background var(--dur-fast) var(--ease-out),transform var(--dur-fast) var(--ease-out)}
.chip:hover{color:var(--ink);background:var(--panel);
  border-color:color-mix(in srgb,var(--beam) 45%,transparent);transform:translateY(-1px)}
.chip[aria-checked="true"]{color:var(--ink);border-color:var(--beam);background:var(--panel)}
.search{position:relative;flex:1 1 20rem}
.search input{width:100%;min-height:44px;padding:var(--space-3) var(--space-5);
  background:var(--panel);border:1px solid var(--stroke);border-radius:999px;color:var(--ink);
  font:inherit}
.search kbd{position:absolute;right:var(--space-4);top:50%;transform:translateY(-50%);
  color:var(--muted);font-size:var(--step--1)}
.toggle{display:flex;border:1px solid var(--stroke);border-radius:999px;background:var(--panel);
  overflow:hidden}
.toggle button{min-height:44px;padding:var(--space-2) var(--space-5);background:transparent;
  border:0;color:var(--muted);font:inherit;font-size:var(--step--1);letter-spacing:.1em;
  text-transform:uppercase;cursor:pointer}
.toggle button[aria-pressed="true"]{color:var(--ink);background:var(--panel-hover)}
:focus-visible{outline:2px solid var(--beam);outline-offset:3px;border-radius:4px}
"""

page("components/controls.html", "Components", "Controls", "Button, chip, search, toggle",
     "Controls",
     "Every control is at least 44px tall and every one of them is a pill. A secondary "
     "inline link inside a larger primary target may be smaller, with 24px the floor.",
     """<div class="frame">
       <div class="row">
         <button class="btn" type="button">Enter the register
           <svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true">
             <path d="M7 1v12M2 8l5 5 5-5" fill="none" stroke="currentColor" stroke-width="1.5"/>
           </svg>
         </button>
         <span class="toggle">
           <button type="button" aria-pressed="true">Grid</button>
           <button type="button" aria-pressed="false">Map</button>
         </span>
       </div>
       <div class="row">
         <span class="search"><input type="search" placeholder="Search companies"><kbd>⌘K</kbd></span>
       </div>
       <div class="row">
         <button class="chip" type="button" aria-checked="true" role="radio">All</button>
         <button class="chip" type="button" aria-checked="false" role="radio">Fintech</button>
         <button class="chip" type="button" aria-checked="false" role="radio">Defence and Aerospace</button>
         <button class="chip" type="button" aria-checked="false" role="radio">Climate and Energy</button>
       </div>
     </div>""",
     CONTROL_CSS,
     rules=[
       "<b>Focus is always visible:</b> 2px solid --beam, offset 3px. Tab through this card "
       "to see it.",
       "Roving tabindex for tablists and radiogroups: one Tab stop, arrows move within.",
       "Named transition properties, never <code>all</code>. <code>all</code> sweeps up "
       "whatever anyone adds to the rule later.",
       "A control says exactly what happens and keeps the same word through the flow.",
     ])

TIMELINE_CSS = """
.timeline{list-style:none;margin:0;padding:0;display:grid;gap:var(--space-4);max-width:26rem}
.timeline__node{display:grid;grid-template-columns:1fr auto;gap:var(--space-1) var(--space-3);
  padding-left:var(--space-5);position:relative;border-left:1px solid var(--stroke)}
.timeline__dot{position:absolute;left:-5px;top:.45rem;width:9px;height:9px;border-radius:50%;
  background:var(--muted)}
.is-unicorn .timeline__dot{background:var(--violet);
  box-shadow:0 0 0 4px color-mix(in srgb,var(--violet) 25%,transparent)}
.timeline__date{grid-column:1;font-size:var(--step--1);color:var(--muted)}
.timeline__amount{grid-column:2;grid-row:1;text-align:right;white-space:nowrap;
  font-size:var(--step-0);color:var(--ink);font-variant-numeric:tabular-nums}
.timeline__stage,.timeline__lead,.timeline__flag{grid-column:1 / -1;font-size:var(--step--1);
  color:var(--muted)}
.timeline__flag{color:var(--violet)}
"""


def node(date, stage, amount, lead="", crossing=False):
    flag = '<span class="timeline__flag">crossed €1bn</span>' if crossing else ""
    lead_html = f'<span class="timeline__lead">{lead}</span>' if lead else ""
    return f"""
      <li class="timeline__node {'is-unicorn' if crossing else ''}">
        <span class="timeline__dot"></span>
        <span class="timeline__date">{date}</span>
        <span class="timeline__amount">{amount}</span>
        <span class="timeline__stage">{stage}</span>
        {lead_html}{flag}
      </li>"""


page("components/timeline.html", "Components", "Timeline", "One node per round",
     "Timeline",
     "A vertical hairline with a dot per entry. The marked entry takes --violet with a glow "
     "ring, which is one of only two places on the site glow is allowed.",
     f"""<div class="frame"><ol class="timeline">
       {node('2021', 'Series A', '€102.5 m', 'Prima Materia')}
       {node('Sep 2023', 'Series B', '€209 m', 'General Catalyst', crossing=True)}
       {node('Jul 2024', 'Series C', '€450 m')}
       {node('Jun 2025', 'Series D', '€600 m', 'Prima Materia')}
       {node('Jul 2026', 'Series E', '$1.8 bn')}
     </ol></div>""",
     TIMELINE_CSS,
     rules=[
       "The date pairs with its amount on one line, and the stage and lead investors sit "
       "under both. One line shorter per round than a full stack.",
       "Nodes stagger in at <code>calc(var(--i) * 70ms)</code>, and under reduced motion "
       "<b>animation-delay is zeroed as well as duration</b>.",
       "The crossing flag names the threshold the round actually cleared. A company that "
       "crossed at $1.1 billion did not cross €1bn.",
     ])

PLATE_CSS = """
.plates{display:flex;gap:var(--space-5);flex-wrap:wrap;align-items:start}
.plate{display:grid;place-items:center;background:var(--plate);border-radius:10px;
  padding:var(--space-4);height:5.5rem;width:13rem;
  box-shadow:inset 0 1px 3px var(--plate-inset),inset 0 0 0 1px var(--plate-inset-ring)}
.plate img{max-height:3rem;max-width:100%;width:auto;object-fit:contain}
"""

page("components/logo-plate.html", "Components", "Logo plate", "The one light surface",
     "Logo plate",
     "The only light surface in the system. It exists so company logos sit on the white "
     "they were drawn for, and for no other reason.",
     f"""<div class="frame"><div class="plates">
       <span class="plate"><img src="{logo('helsing')}" alt=""></span>
       <span class="plate"><img src="{logo('trade-republic')}" alt=""></span>
       <span class="plate"><img src="{logo('moss')}" alt=""></span>
     </div></div>""",
     PLATE_CSS,
     rules=[
       "<b>Logos are never altered.</b> No recolouring, no monochrome treatment, no mask.",
       "Seated into its card with an inset shadow and a hairline ring, both mixes of "
       "--plate-ink, so the plate reads as set into the surface rather than laid on it.",
       "<b>Inside a card the plate takes an exact height, not a minimum.</b> Some logos have "
       "no intrinsic aspect ratio and resolve a fraction taller, which is enough to put a "
       "card out of step with its neighbours.",
       "--plate-ink is the only ink token for a light surface, and the contrast checker "
       "asserts that the dark inks <b>fail</b> on it.",
     ])

# The specification itself, alongside the cards.
spec = (ROOT / "docs" / "DESIGN-SYSTEM.md").read_text(encoding="utf-8")
(OUT / "DESIGN-SYSTEM.md").write_text(spec, encoding="utf-8")

written = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file())
total = sum((OUT / p).stat().st_size for p in written)
for name in written:
    print(f"{(OUT / name).stat().st_size / 1024:8.1f} KiB  {name}")
print(f"{total / 1024:8.1f} KiB  total, {len(written)} files")
