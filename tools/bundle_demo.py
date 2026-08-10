#!/usr/bin/env python3
"""Bundle the German Unicorns site into one self-contained demo HTML file.

Writes dist/demo.html: a single fragment (no <!doctype>/<html>/<head>/<body> —
it is injected into a page skeleton at publish time) containing:

  - every CSS file index.html links, concatenated into one <style>, in the
    same order, plus page.css (needed only by the Policy/About/Impressum
    content this script inlines as extra sections — index.html itself never
    links it). @font-face url(...) references are rewritten to base64
    data: URIs.
  - every ES module main.js transitively imports, resolved by parsing each
    file's own `import ... from "./x.js"` statements (not a hard-coded
    list), concatenated in dependency order into one <script type="module">
    with import/export syntax stripped.
  - data/companies.json, data/funding.json and data/geo/germany.json,
    embedded as window.__DEMO_DATA__, with every company logo path rewritten
    to a data: URI. The three runtime fetch() calls that would otherwise
    load those files are patched, in the emitted copy only, to read from
    window.__DEMO_DATA__ instead.
  - policy.html, about.html and impressum.html's <main> content, inlined as
    hidden <section>s. The nav links that used to navigate to those pages
    are rewritten to a `#page/<name>` hash instead; a small router shows the
    matching section. That hash namespace never collides with detail.js's
    `#/<slug>` or funding.js's `#funding/<week>` routers, so deep links into
    a company or a funding week keep working unchanged.
  - a small fixed banner marking the page as a demo build, dated.

This script only reads the repository's real source files; it never edits
them, and the real site is unaffected by running it.
"""
from __future__ import annotations

import base64
import datetime
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS_JS = ROOT / "assets" / "js"
ASSETS_CSS = ROOT / "assets" / "css"
ASSETS_LOGOS = ROOT / "assets" / "logos"
DATA = ROOT / "data"
DIST = ROOT / "dist"
OUT = DIST / "demo.html"

# The exact set index.html links, in the exact order it links them.
CSS_FILES = ["tokens.css", "base.css", "hero.css", "register.css", "funding.css", "detail.css"]
# Not linked by index.html — needed only because this script inlines the
# Policy/About/Imprint content, which is normally styled by page.css on its
# own pages. Appended after the index.html set so their order is preserved
# exactly as specified.
EXTRA_CSS_FILES = ["page.css"]

LOGO_MIME = {".svg": "image/svg+xml", ".png": "image/png"}


def fail(message: str) -> "SystemExit":
    return SystemExit(f"bundle_demo: {message}")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# --------------------------------------------------------------------------
# CSS
# --------------------------------------------------------------------------

FONT_URL_RE = re.compile(r'url\("(\.\./fonts/[^"]+\.woff2)"\)')


def inline_fonts(css: str, css_path: Path) -> str:
    def repl(match: re.Match) -> str:
        rel = match.group(1)
        font_path = (css_path.parent / rel).resolve()
        if not font_path.is_file():
            raise fail(f"font file referenced by {css_path.name} not found: {font_path}")
        data = font_path.read_bytes()
        if data[:4] != b"wOF2":
            raise fail(f"{font_path} does not start with the WOFF2 magic bytes (wOF2) -- refusing to embed")
        b64 = base64.b64encode(data).decode("ascii")
        return f'url("data:font/woff2;base64,{b64}")'

    new_css, count = FONT_URL_RE.subn(repl, css)
    if count == 0:
        raise fail(f"no @font-face url(...) references found in {css_path.name} -- expected at least one")
    return new_css


def build_css() -> str:
    parts = []
    for name in CSS_FILES + EXTRA_CSS_FILES:
        path = ASSETS_CSS / name
        css = read(path)
        if name == "base.css":
            css = inline_fonts(css, path)
        parts.append(f"/* --- assets/css/{name} --- */\n{css.strip()}")
    parts.append(DEMO_BANNER_CSS)
    return "\n\n".join(parts)


DEMO_BANNER_CSS = """\
/* --- demo build banner (tools/bundle_demo.py) --- */
.demo-banner {
  position: fixed; top: 0; left: 0; right: 0; z-index: 100;
  height: 32px; line-height: 32px; padding: 0 var(--space-4);
  background: var(--amber); color: var(--void);
  font-family: var(--font-mono); font-size: var(--step--1);
  letter-spacing: .06em; text-align: center; text-transform: uppercase;
  overflow: hidden; white-space: nowrap; text-overflow: ellipsis;
}
/* Pushes the site's own fixed topbar down below the banner instead of
   letting the two overlap -- same specificity as base.css's `.topbar` rule,
   wins because it is later in the cascade, and only touches `top` so the
   left/right/bottom the original `inset` shorthand set are untouched. */
.topbar { top: 32px; }
.demo-page[hidden] { display: none; }
"""


# --------------------------------------------------------------------------
# JS: dependency resolution + concatenation
# --------------------------------------------------------------------------

IMPORT_RE = re.compile(r'^import\s+(?:\{[^}]*\}|[\w$]+)\s+from\s+["\'](\./[^"\']+)["\'];?\s*$', re.MULTILINE)
IMPORT_NAMED_RE = re.compile(r'^import\s+\{([^}]*)\}\s+from\s+["\'](\./[^"\']+)["\'];?\s*$', re.MULTILINE)
BARE_IMPORT_RE = re.compile(r'^import\s+(?!\{)\S', re.MULTILINE)
EXPORT_RE = re.compile(r'^export\s+', re.MULTILINE)
EXPORT_DECL_RE = re.compile(r'^export\s+(?:async\s+)?(?:function|class)\s+([\w$]+)', re.MULTILINE)
EXPORT_CONST_RE = re.compile(r'^export\s+const\s+([\w$]+)', re.MULTILINE)


def resolve_js_order(entry: Path) -> list[Path]:
    """Post-order DFS over each file's own `import ... from "./x.js"` lines,
    so dependencies always land before their dependents -- discovered from
    the source itself, not a maintained list."""
    order: list[Path] = []
    visited: set[Path] = set()
    visiting: set[Path] = set()

    def visit(path: Path) -> None:
        path = path.resolve()
        if path in visited:
            return
        if path in visiting:
            raise fail(f"circular import detected at {path}")
        visiting.add(path)
        src = read(path)
        for match in IMPORT_RE.finditer(src):
            dep_path = (path.parent / match.group(1)).resolve()
            if not dep_path.is_file():
                raise fail(f"{path.name} imports {match.group(1)!r}, which does not exist at {dep_path}")
            visit(dep_path)
        visiting.discard(path)
        visited.add(path)
        order.append(path)

    visit(entry)
    return order


def module_var(path: Path) -> str:
    return "__mod_" + re.sub(r"[^0-9a-zA-Z_]", "_", path.stem)


def parse_exports(src: str, path: Path) -> list[str]:
    names = EXPORT_DECL_RE.findall(src) + EXPORT_CONST_RE.findall(src)
    if not names and re.search(r'^export\s+', src, re.MULTILINE):
        raise fail(f"{path.name} has an `export` this bundler doesn't recognise (expected `export function`, `export async function`, `export class` or `export const`)")
    return names


def transform_module(path: Path, src: str) -> tuple[str, list[str]]:
    """Rewrites one module's source for concatenation: every named import
    becomes a destructure off that dependency's own namespace object (built
    below) instead of relying on a shared global scope, so this module's
    top-level bindings can never collide with another module's -- e.g.
    transition.js, detail.js and constellation.js each declare their own
    module-scoped `const REDUCED`, which is exactly the kind of collision a
    flat concatenation would hit. Returns (transformed source, export names)."""
    if BARE_IMPORT_RE.search(src):
        raise fail(f"{path.name} has an import form this bundler doesn't handle (expected `import {{ a, b }} from \"./x.js\";`)")

    exports = parse_exports(src, path)

    def repl_import(match: re.Match) -> str:
        names_raw, dep_rel = match.group(1), match.group(2)
        dep_path = (path.parent / dep_rel).resolve()
        return f"const {{{names_raw}}} = {module_var(dep_path)};"

    src = IMPORT_NAMED_RE.sub(repl_import, src)
    src = EXPORT_RE.sub("", src)
    if re.search(r'\bexport\b', src):
        raise fail(f"{path.name} still contains `export` after stripping -- inspect it, the concatenation would be broken JS")
    return src, exports


# Patches applied to a module's source (before import/export stripping) so
# the emitted copy reads embedded data instead of fetching it. Each is a
# regex matched with an explicit count assertion, so a future change to the
# real site's source makes this script fail loudly instead of silently
# shipping a demo that still tries to fetch().
JS_PATCHES: dict[str, list[tuple[re.Pattern, str]]] = {
    "main.js": [
        (
            re.compile(
                r'async function loadData\(\) \{.*?\n\}\n\nasync function loadFunding\(\) \{.*?\n\}',
                re.DOTALL,
            ),
            'async function loadData() {\n'
            '  // Patched by tools/bundle_demo.py for the single-file demo build:\n'
            '  // the real site fetches data/companies.json here; this copy reads\n'
            '  // the same data embedded as window.__DEMO_DATA__, since the demo\n'
            '  // runs under a CSP that blocks every network request.\n'
            '  return window.__DEMO_DATA__.companies;\n'
            '}\n\n'
            'async function loadFunding() {\n'
            '  return window.__DEMO_DATA__.funding;\n'
            '}',
        ),
    ],
    "map.js": [
        (
            re.compile(
                r'export async function renderMap\(container, companies, \{ onSelectCity \}\) \{\n'
                r'  const response = await fetch\("data/geo/germany\.json", \{ cache: "no-cache" \}\);\n'
                r'  if \(!response\.ok\) throw new Error\(`data/geo/germany\.json \$\{response\.status\}`\);\n'
                r'  const geo = await response\.json\(\);',
            ),
            'export async function renderMap(container, companies, { onSelectCity }) {\n'
            '  // Patched by tools/bundle_demo.py: reads the embedded copy instead\n'
            '  // of fetching data/geo/germany.json.\n'
            '  const geo = window.__DEMO_DATA__.geo;',
        ),
    ],
    "register.js": [
        (
            re.compile(re.escape('href="about.html#built"')),
            'href="#page/about/about-built"',
        ),
    ],
}


def apply_js_patches(path: Path, src: str) -> str:
    patches = JS_PATCHES.get(path.name, [])
    for pattern, replacement in patches:
        new_src, count = pattern.subn(replacement, src)
        if count != 1:
            raise fail(
                f"expected exactly one match for a patch in {path.name}, found {count} -- "
                "the source has drifted from what this bundler expects, update the patch"
            )
        src = new_src
    return src


def build_js() -> str:
    entry = ASSETS_JS / "main.js"
    order = resolve_js_order(entry)
    pieces = []
    for path in order:
        src = read(path)
        src = apply_js_patches(path, src)
        transformed, exports = transform_module(path, src)
        rel = path.relative_to(ROOT)
        var = module_var(path)
        export_obj = ", ".join(exports)
        pieces.append(
            f"// --- {rel} ---\n"
            f"const {var} = (function () {{\n"
            f"{transformed.strip()}\n"
            f"return {{ {export_obj} }};\n"
            f"}})();"
        )
    return "\n\n".join(pieces)


# --------------------------------------------------------------------------
# Data: companies.json / funding.json / germany.json, with logos inlined
# --------------------------------------------------------------------------


def load_json(path: Path):
    return json.loads(read(path))


def logo_data_uri(logo_rel: str) -> str:
    path = (ROOT / logo_rel).resolve()
    if not path.is_file():
        raise fail(f"logo referenced by data/companies.json not found: {path}")
    mime = LOGO_MIME.get(path.suffix.lower())
    if mime is None:
        raise fail(f"unrecognised logo extension for {path} -- expected .svg or .png")
    data = path.read_bytes()
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{b64}"


def build_demo_data() -> str:
    companies_doc = load_json(DATA / "companies.json")
    companies = companies_doc.get("companies", [])
    if not companies:
        raise fail("data/companies.json has no companies -- refusing to bundle an empty demo")
    for company in companies:
        logo = company.get("logo")
        if logo:
            company["logo"] = logo_data_uri(logo)
    funding_doc = load_json(DATA / "funding.json")
    geo_doc = load_json(DATA / "geo" / "germany.json")

    payload = {"companies": companies_doc, "funding": funding_doc, "geo": geo_doc}
    raw = json.dumps(payload, ensure_ascii=False)
    # Every value in this payload comes from data/companies.json and its
    # siblings -- hand-written and pipeline-generated, untrusted the same way
    # the client already treats it (assets/js/html.js's escapeHtml). Defanging
    # "</" means a stray "</script>" in, say, a source title can never
    # terminate this <script> tag early.
    raw = raw.replace("</", "<\\/")
    return raw


# --------------------------------------------------------------------------
# HTML: index.html's body, plus policy/about/impressum inlined as sections
# --------------------------------------------------------------------------

TITLE_RE = re.compile(r"<title>(.*?)</title>", re.DOTALL)
BODY_RE = re.compile(r"<body>(.*)</body>", re.DOTALL)
MAIN_RE = re.compile(r"<main\s+([^>]*)>(.*?)</main>", re.DOTALL)
ID_RE = re.compile(r'id="([\w-]+)"')


def extract_title(html: str, path: Path) -> str:
    match = TITLE_RE.search(html)
    if not match:
        raise fail(f"no <title> found in {path.name}")
    return match.group(1)


def extract_index_body() -> str:
    html = read(ROOT / "index.html")
    match = BODY_RE.search(html)
    if not match:
        raise fail("no <body>...</body> found in index.html")
    body = match.group(1)

    script_tag = '<script type="module" src="assets/js/main.js"></script>'
    if script_tag not in body:
        raise fail(f"expected {script_tag!r} in index.html's body")
    body = body.replace(script_tag, "")

    # The two nav links that would otherwise navigate away to a second page;
    # the demo's own router (in the appended bootstrap script) shows the
    # matching inlined section on this same hash instead.
    for label, target in (("Policy", "policy"), ("About", "about")):
        old = f'<a href="{target}.html">{label}</a>'
        new = f'<a href="#page/{target}">{label}</a>'
        if old not in body:
            raise fail(f"expected the {label} nav link {old!r} in index.html")
        body = body.replace(old, new)

    return body


def namespace_ids(fragment: str, prefix: str) -> str:
    """Prefixes every `id="x"` (and matching `aria-labelledby="x"`) in a page
    fragment with `prefix`, so ids that collide across policy.html/about.html
    (both have a `#corrections` section) don't collide once the three pages
    share one document."""
    ids = sorted(set(ID_RE.findall(fragment)))
    for old in ids:
        new = f"{prefix}-{old}"
        fragment = fragment.replace(f'id="{old}"', f'id="{new}"')
        fragment = fragment.replace(f'aria-labelledby="{old}"', f'aria-labelledby="{new}"')
    return fragment


def build_page_section(filename: str, section_id: str, prefix: str, aria_label: str) -> str:
    path = ROOT / filename
    html = read(path)
    match = MAIN_RE.search(html)
    if not match:
        raise fail(f"no <main> element found in {filename}")
    attrs, inner = match.group(1), match.group(2)
    class_match = re.search(r'class="([^"]*)"', attrs)
    classes = class_match.group(1) if class_match else "page"
    inner = namespace_ids(inner, prefix)
    return (
        f'<section id="{section_id}" class="{classes} demo-page" hidden aria-label="{aria_label}">\n'
        f"{inner.strip()}\n"
        f"</section>"
    )


FOOTER_TAG = '<footer class="footer" data-footer></footer>'


def splice_before_footer(body: str, insertion: str) -> str:
    """index.html's body already carries the one <footer data-footer> the
    real site renders once, at the very end -- boot()'s renderFooter() call
    uses querySelector, so a second <footer data-footer> anywhere else would
    silently sit unpopulated while duplicating the first. Rather than append
    a second footer after the inlined Policy/About/Impressum sections (which
    left the *populated* original footer sitting right after the dialog,
    ahead of that inlined content, since it was still the last element of
    index.html's own body), insert those sections into index.html's body
    just before its existing footer -- so there is exactly one footer, and
    it stays last."""
    if FOOTER_TAG not in body:
        raise fail(f"expected {FOOTER_TAG!r} in index.html's body")
    return body.replace(FOOTER_TAG, f"{insertion}\n\n{FOOTER_TAG}")


FOOTER_JS_PATCH = (
    re.compile(
        r'<a href="policy\.html">Policy</a> · <a href="about\.html">About</a> ·\n'
        r'      <a href="impressum\.html">Impressum</a> ·',
    ),
    '<a href="#page/policy">Policy</a> · <a href="#page/about">About</a> ·\n'
    '      <a href="#page/impressum">Impressum</a> ·',
)

JS_PATCHES["footer.js"] = [FOOTER_JS_PATCH]


DEMO_ROUTER_JS = """
// --- demo bundle: page-section router (tools/bundle_demo.py) ---
// Switches between the register and the inlined Policy/About/Impressum
// sections on a `#page/<name>` (optionally `#page/<name>/<id>`) hash. This
// namespace never matches detail.js's `#/<slug>` pattern or funding.js's
// `#funding/<week>` pattern, so company and funding-week deep links keep
// working unchanged alongside it.
(function () {
  const sections = {
    policy: document.getElementById("page-policy"),
    about: document.getElementById("page-about"),
    impressum: document.getElementById("page-impressum"),
  };
  const registerMain = document.querySelector("[data-register]");
  const roundup = document.querySelector("[data-roundup]");
  const PAGE_HASH = /^#page\\/(policy|about|impressum)(?:\\/([\\w-]+))?$/;

  function setCurrentNav(activeId) {
    document.querySelectorAll('a[href^="#page/"]').forEach((a) => {
      const target = a.getAttribute("href").slice("#page/".length).split("/")[0];
      if (target === activeId) a.setAttribute("aria-current", "page");
      else a.removeAttribute("aria-current");
    });
  }

  function showRegisterView() {
    Object.values(sections).forEach((el) => { if (el) el.hidden = true; });
    if (registerMain) registerMain.hidden = false;
    if (roundup) roundup.hidden = false;
    setCurrentNav(null);
  }

  function showPage(id, scrollToId) {
    const el = sections[id];
    if (!el) return;
    if (registerMain) registerMain.hidden = true;
    if (roundup) roundup.hidden = true;
    Object.entries(sections).forEach(([key, node]) => { if (node) node.hidden = key !== id; });
    setCurrentNav(id);
    const target = scrollToId && document.getElementById(scrollToId);
    if (target) target.scrollIntoView();
    else window.scrollTo(0, 0);
  }

  function hashRoute() {
    const hash = location.hash;
    const pageMatch = PAGE_HASH.exec(hash);
    if (pageMatch) { showPage(pageMatch[1], pageMatch[2]); return; }
    if (hash === "#register") { showRegisterView(); return; }
    if (hash === "#funding" && registerMain && registerMain.hidden) {
      // The Funding nav link is a plain #funding anchor scroll on the real
      // site, which only works while the register is in the document flow.
      // From inside an inlined page section that target is hidden -- switch
      // back first, then scroll to it by hand.
      showRegisterView();
      document.getElementById("funding")?.scrollIntoView();
    }
  }

  addEventListener("hashchange", hashRoute);

  // A cold load straight onto a #page/... deep link: skip the hero the same
  // way main.js already skips it for a #funding deep link, since the
  // topbar (and therefore any way back to the register) is hidden until
  // then. window.__sky may not exist yet this early (it is only assigned
  // partway through boot(), after its own first await) -- leaving its
  // animation running invisibly behind a hidden hero costs nothing.
  const initialMatch = PAGE_HASH.exec(location.hash);
  if (initialMatch) {
    document.querySelector("[data-hero]")?.setAttribute("hidden", "");
    document.querySelector("[data-topbar]")?.removeAttribute("hidden");
    window.__sky?.stop();
    showPage(initialMatch[1], initialMatch[2]);
  }
})();
"""


def build_banner(build_date: str) -> str:
    return (
        f'<div class="demo-banner" role="note">'
        f"Demo build &middot; {build_date} &middot; a self-contained snapshot for click-through only, not the live site"
        f"</div>"
    )


# --------------------------------------------------------------------------
# Assembly
# --------------------------------------------------------------------------


def build() -> str:
    index_html = read(ROOT / "index.html")
    title = extract_title(index_html, ROOT / "index.html")

    css = build_css()

    body = extract_index_body()

    policy_section = build_page_section("policy.html", "page-policy", "policy", "Policy")
    about_section = build_page_section("about.html", "page-about", "about", "About")
    impressum_section = build_page_section("impressum.html", "page-impressum", "impressum", "Impressum")

    # index.html's body already carries the one <footer data-footer> the site
    # renders once; splice the inlined sections in just ahead of it so there
    # is still exactly one footer, and it stays last in the document.
    body = splice_before_footer(
        body.strip(),
        "\n\n".join([policy_section, about_section, impressum_section]),
    )

    js = build_js()
    demo_data = build_demo_data()

    build_date = datetime.date.today().isoformat()
    banner = build_banner(build_date)

    html_parts = [
        f"<title>{title}</title>",
        f"<style>\n{css}\n</style>",
        banner,
        body,
        f'<script>window.__DEMO_DATA__ = {demo_data};</script>',
        f"<script type=\"module\">\n{js}\n\n{DEMO_ROUTER_JS.strip()}\n</script>",
    ]
    return "\n\n".join(html_parts) + "\n"


def main() -> None:
    DIST.mkdir(parents=True, exist_ok=True)
    output = build()
    OUT.write_text(output, encoding="utf-8")
    size = OUT.stat().st_size
    print(f"wrote {OUT.relative_to(ROOT)} ({size:,} bytes, {size / 1024 / 1024:.2f} MiB)")
    if size > 16 * 1024 * 1024:
        print("bundle_demo: WARNING -- exceeds the 16 MiB artifact ceiling", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
