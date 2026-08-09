/* Local editor for one company record. Renders data/companies/<slug>.json's schema into a
   form, checks it as you type, and produces a JSON file to commit — it never writes to the
   repository itself (see download()/copy below).

   The rules in validateRecord()/quoteStatesFigure() mirror tools/validate.py and tools/
   schema.py's quote_states_figure, so the operator sees errors while typing rather than
   after committing. tools/validate.py remains the sole authority and the only gate that can
   block a publish (rebuild.yml runs it before tools/build.py ever touches
   data/companies.json). If this file and the Python validator ever disagree, CI catches it
   there and the published site is never wrong — this copy can only be over- or
   under-helpful, never dangerous. That duplication is deliberate, not an oversight — see the
   matching comment at the top of tools/validate.py. */
import { escapeHtml, isSafeUrl } from "./html.js";

// Same allowlist as tools/schema.py's SOURCE_ALLOWLIST, kept as an ordered array here so it
// can drive a <select>'s option order.
export const PUBLICATIONS = [
  "Company press release", "Investor press release", "Handelsregister", "Bundesanzeiger",
  "Gründerszene", "Sifted", "EU-Startups", "Tech.eu", "TechCrunch",
  "Handelsblatt", "Reuters", "Bloomberg", "Financial Times",
];

// Descriptor list for every top-level (or dotted-path) scalar/list field. Grouped under
// `group` labels that renderGroups() turns into <fieldset>s, in GROUP_ORDER below. rounds/
// founders/sources are array-of-object fields with their own repeatable row editors
// (ROUND_FIELDS/FOUNDER_FIELDS/SOURCE_FIELDS further down) — deliberately not part of this
// list, matching the brief's "FIELDS ... plus repeatable row editors" split.
export const FIELDS = [
  { key: "slug", label: "Slug", hint: "lowercase-with-hyphens, matches the filename", group: "Company" },
  { key: "name", label: "Company name", group: "Company" },
  { key: "website", label: "Website", hint: "must start with https://", group: "Company", previewKey: "website" },
  { key: "logo", label: "Logo path", hint: "assets/logos/<slug>.svg", group: "Company" },

  { key: "hq.city", label: "HQ city", group: "Location & founding" },
  { key: "hq.country", label: "HQ country", hint: "two-letter code, e.g. DE", group: "Location & founding" },
  { key: "alsoBasedIn", label: "Also based in", hint: "comma separated, optional — e.g. a dual HQ", list: true, pruneWhenEmpty: true, group: "Location & founding" },
  { key: "foundedCountry", label: "Founded in (country)", group: "Location & founding" },
  { key: "foundedYear", label: "Founded year", type: "number", step: "1", group: "Location & founding" },

  { key: "sectors", label: "Sectors", hint: "comma separated", list: true, group: "Sectors & story" },
  { key: "thesis.problem", label: "The problem", type: "textarea", group: "Sectors & story" },
  { key: "thesis.solution", label: "Technology & business model", type: "textarea", group: "Sectors & story" },

  { key: "valuation.amount", label: "Valuation (millions)", type: "number", hint: "in the currency below", group: "Valuation" },
  { key: "valuation.currency", label: "Currency", hint: "EUR or USD", group: "Valuation" },
  { key: "valuation.approximate", label: "Approximate", type: "checkbox", group: "Valuation" },
  { key: "valuation.asOf", label: "As of", hint: "YYYY or YYYY-MM", group: "Valuation" },
  { key: "valuation.round", label: "Round label", hint: "e.g. Series C", group: "Valuation" },
  { key: "valuation.source", label: "Source id", hint: "matches a source id below", group: "Valuation" },
  { key: "valuation.disputed.note", label: "Disputed note", hint: "optional — leave both disputed fields blank if not disputed", group: "Valuation" },
  { key: "valuation.disputed.source", label: "Disputed source id", hint: "optional — required together with the note above", group: "Valuation" },

  { key: "becameUnicorn.date", label: "Became a unicorn on", hint: "YYYY or YYYY-MM", group: "Became a unicorn" },
  { key: "becameUnicorn.roundId", label: "Crossing round id", hint: "must match a round id below", group: "Became a unicorn" },
  { key: "becameUnicorn.source", label: "Source id", group: "Became a unicorn" },

  { key: "totalRaised.amount", label: "Total raised (millions)", type: "number", hint: "leave blank if unknown", group: "Total raised" },
  { key: "totalRaised.currency", label: "Currency", hint: "EUR or USD", group: "Total raised" },
  { key: "totalRaised.approximate", label: "Approximate", type: "checkbox", group: "Total raised" },
  { key: "totalRaised.source", label: "Source id", group: "Total raised" },

  { key: "investors", label: "Investors", hint: "comma separated", list: true, group: "Investors" },
];

const GROUP_ORDER = [
  "Company", "Location & founding", "Sectors & story", "Valuation", "Became a unicorn",
  "Total raised", "Funding rounds", "Founders", "Investors", "Sources",
];

const ROUND_FIELDS = [
  { key: "id", label: "Round id", hint: "e.g. r1" },
  { key: "date", label: "Date", hint: "YYYY or YYYY-MM" },
  { key: "stage", label: "Stage", hint: "e.g. Series C" },
  { key: "amount", label: "Amount raised (millions)", type: "number", hint: "blank if undisclosed" },
  { key: "currency", label: "Currency", hint: "EUR or USD" },
  { key: "approximate", label: "Approximate", type: "checkbox" },
  { key: "postMoney", label: "Post-money (millions)", type: "number", hint: "blank if undisclosed" },
  { key: "leadInvestors", label: "Lead investors", hint: "comma separated", list: true },
  { key: "investors", label: "Investors", hint: "comma separated (includes leads)", list: true },
  { key: "source", label: "Source id", hint: "matches a source id below" },
];
const FOUNDER_FIELDS = [
  { key: "name", label: "Name" },
  { key: "role", label: "Role", hint: "e.g. CEO" },
  { key: "current", label: "Still with the company", type: "checkbox" },
];
const SOURCE_FIELDS = [
  { key: "id", label: "Source id", hint: "e.g. s1" },
  { key: "publication", label: "Publication", type: "select", options: PUBLICATIONS },
  { key: "title", label: "Title" },
  { key: "url", label: "URL", hint: "https://…" },
  { key: "publishedOn", label: "Published on", type: "date", hint: "the article's own publication date" },
  { key: "quote", label: "Verbatim quote", type: "textarea", hint: "must contain every figure cited to this source" },
];

/* ---------------------------------------------------------------------------------------
   Dotted-path get/set. setPath mutates the *existing* object at each step rather than
   rebuilding it, so a field the operator never touches keeps its original key order and
   value — the property on the round-trip test in the task brief. Only genuinely new
   sub-objects (e.g. the first time "Disputed note" is filled in) get a fresh key appended,
   exactly like a hand edit adding a field would.
   --------------------------------------------------------------------------------------- */
function getPath(obj, path) {
  return path.split(".").reduce((node, key) => (node == null ? undefined : node[key]), obj);
}
function setPath(obj, path, value) {
  const keys = path.split(".");
  let node = obj;
  for (let i = 0; i < keys.length - 1; i++) {
    const key = keys[i];
    if (typeof node[key] !== "object" || node[key] === null) node[key] = {};
    node = node[key];
  }
  node[keys[keys.length - 1]] = value;
}

function parseList(value) {
  return String(value ?? "").split(",").map((s) => s.trim()).filter(Boolean);
}
function parseNumberOrNull(value) {
  const raw = String(value ?? "").trim();
  if (raw === "") return null;
  const n = Number(raw);
  return Number.isFinite(n) ? n : null;
}
function describe(value) {
  return value === undefined ? "undefined" : JSON.stringify(value);
}

/* ---------------------------------------------------------------------------------------
   The quote-contains-the-figure mirror. Ported from tools/schema.py's quote_states_figure
   (digit-boundary matching, a scale word required beside a billion-scale figure, the
   currency required to appear somewhere in the quote) — verified against every case in
   tests/test_schema.py plus the figure-related cases in tests/test_validate.py under a real
   JS engine before this file was written; see task-13-report.md for the exact run.

   One real fix over a naive port: computing billions as `millions / 1000` and then
   `.toFixed(1)` (the obvious translation, and what the task brief's own sketch does) lands
   on a binary-inexact fraction for ordinary values like 1150 -> 1.15, and at an exact half
   the resulting string can round the wrong way — 1150.toFixed at one decimal comes out
   "1.1", not "1.2". roundHalfUp() below avoids that by rounding an integer quotient instead
   of a fractional one, which lands exactly on n/2 at the boundary cases (always exact in
   binary) rather than on n/10 or n/1000 (usually not). Checked against Python's
   Decimal(...).quantize(..., ROUND_HALF_UP) across 35 values including every half-boundary
   from .05 to .95; all matched exactly.
   --------------------------------------------------------------------------------------- */
const SCALE_EN = "(?:billions|billion|bn)(?![a-z])";
const SCALE_DE = "(?:milliarden|milliarde|mrd\\.?)(?![a-z])";
const CURRENCY_SYMBOLS = "[$€]";
const CURRENCY_TOKENS = { EUR: ["€", "eur", "euro"], USD: ["$", "usd", "dollar"] };
// NBSP, thin space, narrow NBSP, ideographic space — the same four code points
// tools/schema.py normalises (press releases and PDFs use them as figure separators).
const SPACE_CHARS = [" ", " ", " ", "　"];

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function normaliseQuote(quote) {
  let text = quote || "";
  for (const ch of SPACE_CHARS) text = text.split(ch).join(" ");
  return text;
}

function roundHalfUp(millions, places) {
  const scale = Math.pow(10, 3 - places);
  const units = Math.round(millions / scale);        // billions * 10^places, as an integer
  const negative = units < 0;
  const digits = String(Math.abs(units)).padStart(places + 1, "0");
  const cut = digits.length - places;
  return (negative ? "-" : "") + digits.slice(0, cut) + (places ? "." + digits.slice(cut) : "");
}

function billionForms(millions) {
  const forms = new Set();
  for (const places of [2, 1]) {
    forms.add(roundHalfUp(millions, places).replace(/0+$/, "").replace(/\.$/, ""));
  }
  return forms;
}

/** (form, needsScaleWord) pairs a source might use for this amount — mirrors
    tools/schema.py's _figure_forms exactly (including which forms need an adjacent scale
    word and which don't). */
function figureForms(millions) {
  const forms = [];
  if (millions >= 1000) {
    for (const billions of billionForms(millions)) {
      forms.push([billions, true]);
      forms.push([billions.replace(".", ","), true]);
    }
    const whole = Math.round(millions);
    const grouped = whole.toLocaleString("en-US");    // 13,000
    forms.push([String(whole), false]);
    forms.push([grouped, false]);
    forms.push([grouped.replace(/,/g, "."), false]);  // 13.000
    forms.push([grouped.replace(/,/g, " "), false]);  // 13 000
  } else {
    // Fractional sub-billion rounds (a €102.5m Series A) are printed with their
    // decimal, English "102.5" or German "102,5" — mirrors the same two forms in
    // tools/schema.py's _figure_forms, including its refusal to round a
    // fractional amount to a bare integer that is a different number.
    const decimal = String(millions);
    forms.push([decimal, false]);
    if (!Number.isInteger(millions)) forms.push([decimal.replace(".", ","), false]);
  }
  return forms;
}

/** True when `quote` states `millions` (and, if given, mentions `currency` somewhere) —
    mirrors tools/schema.py's quote_states_figure(). Currency matching is presence-based
    there too: it proves the quote names the currency, not that it names it *for this
    number*, so it catches a mislabelled record rather than a subtly wrong one. */
export function quoteStatesFigure(quote, millions, currency) {
  if (millions == null) return true;   // nothing to check — mirrors checkFigure's own guard
  const text = normaliseQuote(quote).toLowerCase();
  if (currency) {
    const tokens = CURRENCY_TOKENS[currency];
    if (tokens && !tokens.some((token) => text.includes(token))) return false;
  }
  for (const [form, needsScale] of figureForms(millions)) {
    const escaped = escapeRegExp(form);
    if (needsScale) {
      const patterns = [
        new RegExp(`(?<![\\d.,])${escaped}[\\s\\-–—]*${SCALE_EN}`),
        new RegExp(`(?<![\\d.,])${escaped}[\\s\\-–—]*${SCALE_DE}`),
        new RegExp(`${CURRENCY_SYMBOLS}\\s?${escaped}b(?![a-z0-9])`),
      ];
      if (patterns.some((pattern) => pattern.test(text))) return true;
    } else if (new RegExp(`(?<![\\d.,])${escaped}(?!\\d)(?![.,]\\d)`).test(text)) {
      return true;
    }
  }
  return false;
}

/** Example strings the operator could add to a quote to satisfy quoteStatesFigure() for
    this amount — shown next to a figure-mismatch error. Built from the same figureForms()
    used to check the quote, so every hint shown is guaranteed to actually pass. */
export function figureVariants(millions) {
  return new Set(figureForms(millions).map(([form]) => form));
}

/* ---------------------------------------------------------------------------------------
   Date helpers — mirrors tools/schema.py's parse_date (YYYY or YYYY-MM, month checked to be
   1-12) and is_full_date (plain YYYY-MM-DD regex, no calendar validation — matched exactly,
   not tightened, so this never rejects something the real validator would accept).
   --------------------------------------------------------------------------------------- */
const DATE_RE = /^(\d{4})(?:-(\d{2}))?$/;
export const FULL_DATE_RE = /^\d{4}-\d{2}-\d{2}$/;

function parseDateLoose(value) {
  const match = DATE_RE.exec(value || "");
  if (!match) throw new Error(`date must be YYYY or YYYY-MM, got ${describe(value)}`);
  const month = match[2] ? Number(match[2]) : 0;
  if (match[2] && (month < 1 || month > 12)) throw new Error(`month out of range in ${describe(value)}`);
  return [Number(match[1]), month];
}
function cmpDate(a, b) { return a[0] - b[0] || a[1] - b[1]; }

/* ---------------------------------------------------------------------------------------
   Record shape: blank template, and stripping build.py's derived fields back off a
   data/companies.json entry so "load, change nothing, download" reproduces the original
   data/companies/<slug>.json byte-for-byte (see tools/build.py's derive_company: it adds
   display/sort/investorsOrdered and, per round, dateLabel/amountLabel — everything else
   passes through with its original key order untouched via **record).
   --------------------------------------------------------------------------------------- */
export function createBlankRecord() {
  return {
    slug: "", name: "", website: "", logo: "",
    hq: { city: "", country: "" },
    foundedCountry: "", foundedYear: null,
    sectors: [],
    thesis: { problem: "", solution: "" },
    valuation: { amount: null, currency: "", approximate: false, asOf: "", round: "", source: "" },
    becameUnicorn: { date: "", roundId: "", source: "" },
    totalRaised: { amount: null, currency: "", approximate: false, source: "" },
    rounds: [],
    founders: [],
    investors: [],
    sources: [],
  };
}

export function stripDerived(builtCompany) {
  const record = structuredClone(builtCompany);
  delete record.display;
  delete record.sort;
  delete record.investorsOrdered;
  for (const round of record.rounds || []) {
    delete round.dateLabel;
    delete round.amountLabel;
  }
  return record;
}

/* ---------------------------------------------------------------------------------------
   Validation. Mirrors tools/validate.py's validate_company: presence, then type/shape
   (returning early on either, exactly as validate.py does — the type pass exists there so
   later code can assume a field has the shape it needs; the same applies here), then the
   content rules. Every message names the field it is about — never a single generic
   "invalid" — per the brief's required behaviour.
   --------------------------------------------------------------------------------------- */
const REQUIRED_KEYS = ["slug", "name", "website", "logo", "hq", "foundedCountry", "foundedYear",
  "sectors", "thesis", "valuation", "becameUnicorn", "totalRaised",
  "rounds", "founders", "investors", "sources"];
const THRESHOLD_MILLIONS = 1000;
/** Mirrors tools/schema.py KNOWN_CURRENCIES and tools/validate.py ROUND_KEYS. An
    unknown code renders as "GBP 1bn" rather than failing, and a misspelled optional
    key (postMoneyCurency) silently falls back to `currency` — both reach the reader
    as a figure in a currency no source used, so both are rejected by name. */
const KNOWN_CURRENCIES = ["EUR", "USD"];
const ROUND_KEYS = ["id", "date", "stage", "amount", "currency", "approximate", "postMoney",
  "postMoneyCurrency", "postMoneySource", "leadInvestors", "investors", "source", "disputed"];
const SLUG_RE = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

function isNonEmptyString(value) {
  return typeof value === "string" && value.trim() !== "";
}
function requireString(errors, label, value) {
  if (!isNonEmptyString(value)) errors.push(`${label} must be a non-empty string`);
}
function isPlainObject(value) {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function typeErrors(record) {
  const errors = [];
  for (const [label, key] of [["name", "name"], ["website", "website"], ["logo", "logo"], ["slug", "slug"]]) {
    requireString(errors, label, record[key]);
  }

  const sectors = record.sectors;
  if (!Array.isArray(sectors) || sectors.length === 0) {
    errors.push("sectors must be a non-empty list");
  } else {
    for (const entry of sectors) {
      if (typeof entry !== "string" || !entry.trim()) errors.push(`sectors contains a non-string or empty entry: ${describe(entry)}`);
    }
  }

  if (!isPlainObject(record.hq)) {
    errors.push("hq must be an object with city and country");
  } else {
    requireString(errors, "hq.city", record.hq.city);
    requireString(errors, "hq.country", record.hq.country);
  }

  // Optional dual-HQ list (Celonis is Munich and New York, for example). Matches
  // validate.py exactly: an explicit null is treated the same as the key being absent
  // (both skip the check) — only a *present, non-list* value is an error.
  const alsoBasedIn = record.alsoBasedIn;
  if (alsoBasedIn !== undefined && alsoBasedIn !== null) {
    if (!Array.isArray(alsoBasedIn)) {
      errors.push("alsoBasedIn must be a list of non-empty strings");
    } else {
      for (const entry of alsoBasedIn) {
        if (typeof entry !== "string" || !entry.trim()) errors.push(`alsoBasedIn contains a non-string or empty entry: ${describe(entry)}`);
      }
    }
  }

  for (const field of ["founders", "investors", "rounds", "sources"]) {
    if (!Array.isArray(record[field])) errors.push(`${field} must be a list`);
  }

  if (!Number.isInteger(record.foundedYear)) errors.push("foundedYear must be an integer");

  // validate.py does not yet shape-check these three (tracked as a known gap in the SDD
  // ledger — Task 7 deferred it; a malformed one currently crashes validate.py with a raw
  // traceback rather than a clean message, though CI still correctly refuses to publish
  // either way). Checking here is purely defensive: it keeps *this* tool from throwing
  // partway through a render, without ever accepting anything Python would reject —
  // over-helpful, not dangerous, per the ruling this file's rules operate under.
  for (const key of ["valuation", "becameUnicorn", "totalRaised"]) {
    if (!isPlainObject(record[key])) errors.push(`${key} must be an object`);
  }

  return errors;
}

export function validateRecord(record) {
  record = record || {};
  const errors = [];
  for (const key of REQUIRED_KEYS) {
    if (!(key in record)) errors.push(`missing required field: ${key}`);
  }
  if (errors.length) return errors;

  const shapeErrors = typeErrors(record);
  if (shapeErrors.length) return shapeErrors;

  if (!SLUG_RE.test(record.slug)) errors.push(`slug must be lowercase and hyphenated: ${describe(record.slug)}`);
  if (!String(record.website).startsWith("https://")) errors.push("website must be an https URL");

  const sourcesById = {};
  for (const source of record.sources) {
    for (const field of ["id", "publication", "title", "url", "publishedOn", "quote"]) {
      if (!source[field]) errors.push(`source ${source.id ?? "?"} is missing ${field}`);
    }
    if (!PUBLICATIONS.includes(source.publication)) {
      errors.push(`source ${source.id ?? "?"}: publication is not on the allowlist: ${describe(source.publication)}`);
    }
    if (!FULL_DATE_RE.test(source.publishedOn || "")) {
      errors.push(`source ${source.id ?? "?"} publishedOn must be a real YYYY-MM-DD publication date`);
    }
    sourcesById[source.id] = source;
  }

  /** `currencyKey`/`sourceKey` mirror tools/validate.py's check_figure: a round's
      post-money is routinely stated in a different currency, and sometimes by a
      different sentence, than the money raised. Both fall back to `currency`/`source`. */
  const checkFigure = (label, figure, amountKey = "amount", currencyKey = "currency", sourceKey = "source") => {
    if (!figure) return;
    const sourceId = figure[sourceKey] || figure.source;
    if (!Object.prototype.hasOwnProperty.call(sourcesById, sourceId)) {
      errors.push(`${label} cites unknown source ${describe(sourceId)}`);
      return;
    }
    const amount = figure[amountKey];
    if (amount === null || amount === undefined) return;
    const currency = figure[currencyKey] || figure.currency;
    if (!quoteStatesFigure(sourcesById[sourceId].quote, amount, currency)) {
      errors.push(`${label}: quote for source ${sourceId} does not state the figure ${amount} `
        + `and its currency — extend the quote to a sentence naming both`);
    }
  };

  checkFigure("valuation", record.valuation);
  checkFigure("totalRaised", record.totalRaised);

  /** Optional everywhere it appears — on `valuation`, and on any round whose amount the
      sources disagree about. Mirrors tools/validate.py's check_disputed(). */
  const checkDisputed = (label, container) => {
    const disputed = container.disputed;
    if (disputed === undefined || disputed === null) return;
    if (!isPlainObject(disputed)) {
      errors.push(`${label}.disputed must be an object with note and source`);
      return;
    }
    if (!isNonEmptyString(disputed.note)) errors.push(`${label}.disputed.note must be a non-empty string`);
    if (!Object.prototype.hasOwnProperty.call(sourcesById, disputed.source)) {
      errors.push(`${label}.disputed cites unknown source ${describe(disputed.source)}`);
    }
  };

  const checkCurrency = (label, value) => {
    if (value !== null && value !== undefined && !KNOWN_CURRENCIES.includes(value)) {
      errors.push(`${label} is not a currency this register can render: ${describe(value)} `
        + `(known: ${KNOWN_CURRENCIES.join(", ")})`);
    }
  };

  checkDisputed("valuation", record.valuation);
  checkCurrency("valuation.currency", record.valuation.currency);
  checkCurrency("totalRaised.currency", record.totalRaised && record.totalRaised.currency);

  for (const [label, value] of [["valuation.asOf", record.valuation.asOf], ["becameUnicorn.date", record.becameUnicorn.date]]) {
    try { parseDateLoose(value); } catch (exc) { errors.push(`${label}: ${exc.message}`); }
  }

  const rounds = record.rounds;
  let previous = null;
  for (const entry of rounds) {
    let key;
    try {
      key = parseDateLoose(entry.date);
    } catch (exc) {
      errors.push(`round ${entry.id ?? "?"}: bad date (${exc.message})`);
      continue;
    }
    if (previous !== null && cmpDate(key, previous) < 0) {
      errors.push(`rounds must be in chronological order: ${entry.id ?? "?"} is out of order`);
    }
    previous = key;
    checkFigure(`round ${entry.id ?? "?"}`, entry);
    checkFigure(`round ${entry.id ?? "?"} post-money`, entry, "postMoney", "postMoneyCurrency", "postMoneySource");
    checkDisputed(`round ${entry.id ?? "?"}`, entry);
    checkCurrency(`round ${entry.id ?? "?"}.currency`, entry.currency);
    checkCurrency(`round ${entry.id ?? "?"}.postMoneyCurrency`, entry.postMoneyCurrency);
    for (const keyName of Object.keys(entry).filter((k) => !ROUND_KEYS.includes(k)).sort()) {
      errors.push(`round ${entry.id ?? "?"}: unknown field ${describe(keyName)} — a misspelled `
        + "optional field is silently ignored, so it is rejected by name");
    }
  }

  const roundsById = Object.fromEntries(rounds.map((entry) => [entry.id, entry]));
  const unicornRound = roundsById[record.becameUnicorn.roundId];
  if (!unicornRound) {
    errors.push(`becameUnicorn.roundId ${describe(record.becameUnicorn.roundId)} matches no round`);
  } else if ((unicornRound.postMoney || 0) < THRESHOLD_MILLIONS) {
    errors.push(`round ${unicornRound.id}: post-money is below the ${THRESHOLD_MILLIONS}m inclusion threshold`);
  } else {
    // An earlier round already over the threshold means the company crossed there, not
    // here — mirrors tools/validate.py, which explains why nothing else catches it.
    let unicornKey = null;
    try { unicornKey = parseDateLoose(unicornRound.date); } catch { /* reported above */ }
    if (unicornKey !== null) {
      for (const entry of rounds) {
        if (entry === unicornRound || (entry.postMoney || 0) < THRESHOLD_MILLIONS) continue;
        try {
          if (cmpDate(parseDateLoose(entry.date), unicornKey) >= 0) continue;
        } catch { continue; }
        errors.push(`round ${entry.id ?? "?"} (${entry.date}) already has a post-money at or above `
          + `the ${THRESHOLD_MILLIONS}m threshold, so becameUnicorn cannot be round `
          + `${unicornRound.id} (${unicornRound.date}) — the company crossed earlier`);
      }
    }
  }

  if (rounds.length) {
    // Mirrors tools/validate.py, which this had fallen behind. The old rule here
    // compared valuation.asOf against rounds[last] on dates alone and rejected any
    // valuation older than the most recent round. That is right only when the newer
    // round said what the company was worth; when it disclosed no price — ordinary
    // and honest — the last publicly reported figure genuinely is still the earlier
    // one. The stale copy flagged Enpal, Scalable Capital and 1KOMMA5°, all three of
    // which are published, so the form editor was reporting an error on records the
    // authority accepts. Every round after asOf is checked, not just the last: a
    // disclosed post-money mid-history supersedes the headline just as surely.
    let valuationKey = null;
    try { valuationKey = parseDateLoose(record.valuation.asOf); } catch { /* reported above */ }
    if (valuationKey !== null) {
      for (const entry of rounds) {
        if (entry.postMoney === null || entry.postMoney === undefined) continue;
        try {
          if (cmpDate(parseDateLoose(entry.date), valuationKey) <= 0) continue;
        } catch { continue; }
        errors.push(`valuation.asOf (${record.valuation.asOf}) predates round `
          + `${entry.id ?? "?"} (${entry.date}), which discloses a post-money of its own `
          + "— that newer figure is the one to publish");
      }
    }
  }

  return errors;
}

/** formState is the live record object (see mount() below — form controls mutate it in
    place via setPath so untouched fields never move). buildRecord() prunes `disputed` back to
    "absent" when it ends up empty — e.g. a disputed note typed in and then cleared again —
    rather than publishing a stray {} a hand-reader would misread as a deliberate claim. That
    check is safe to run unconditionally on every call because a *loaded* record can never
    legitimately arrive with both fields blank: tools/validate.py itself rejects a present
    `disputed` whose note is empty, so blank-both can only ever be something the operator just
    typed and cleared in this session, never something that was already on disk.

    `alsoBasedIn` doesn't have that same guarantee — validate.py accepts an explicit
    `"alsoBasedIn": []` as a valid, on-disk state (unlike `disputed`), so buildRecord() cannot
    tell "the operator just cleared it" apart from "it was already empty when loaded" — that
    distinction depends on *when* it became empty, which this function, seeing only a single
    snapshot, structurally cannot know. So it isn't handled here: see mount()'s
    handleControlChange(), which prunes it at the moment the operator's own edit to that field
    empties it, and leaves an untouched (possibly already-empty) array alone otherwise.

    Everything else passes through untouched, which is what keeps an unmodified
    load-then-download byte-identical to the source file. */
export function buildRecord(formState) {
  const record = structuredClone(formState);
  if (record.valuation && record.valuation.disputed) {
    const { note, source } = record.valuation.disputed;
    if (!isNonEmptyString(note) && !isNonEmptyString(source)) delete record.valuation.disputed;
  }
  return record;
}

export function download(record) {
  const blob = new Blob([JSON.stringify(record, null, 1)], { type: "application/json" });
  const link = Object.assign(document.createElement("a"), {
    href: URL.createObjectURL(blob), download: `${record.slug || "company"}.json`,
  });
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(link.href);
}

/* =========================================================================================
   DOM. Below this line is rendering and event wiring — buildRecord/validateRecord/FIELDS
   above are the testable core; this half turns them into the actual page.
   ========================================================================================= */

function datasetAttrs(data) {
  return Object.entries(data).map(([key, value]) => ` data-${key}="${escapeHtml(String(value))}"`).join("");
}

function controlMarkup(descriptor, value, id, dataset) {
  const attrs = datasetAttrs(dataset);
  if (descriptor.type === "textarea") {
    return `<textarea id="${id}"${attrs} rows="3">${escapeHtml(value ?? "")}</textarea>`;
  }
  if (descriptor.type === "select") {
    const options = [`<option value="">— choose —</option>`].concat(
      (descriptor.options || []).map((option) =>
        `<option value="${escapeHtml(option)}"${option === value ? " selected" : ""}>${escapeHtml(option)}</option>`));
    return `<select id="${id}"${attrs}>${options.join("")}</select>`;
  }
  const type = descriptor.type === "number" ? "number" : descriptor.type === "date" ? "date" : "text";
  const display = descriptor.list ? (value || []).join(", ") : (value ?? "");
  const step = type === "number" ? ` step="${descriptor.step || "any"}"` : "";
  return `<input type="${type}" id="${id}"${attrs}${step} value="${escapeHtml(display)}">`;
}

function fieldBlock(descriptor, value, dataset, extraMarkup = "") {
  const id = "f-" + Object.entries(dataset).map(([, v]) => v).join("-").replace(/[^a-zA-Z0-9_-]/g, "_");
  const hint = descriptor.hint ? `<p class="field__hint">${escapeHtml(descriptor.hint)}</p>` : "";
  if (descriptor.type === "checkbox") {
    return `<div class="field field--checkbox">
      <label><input type="checkbox" id="${id}"${datasetAttrs(dataset)}${value ? " checked" : ""}> ${escapeHtml(descriptor.label)}</label>
      ${hint}</div>`;
  }
  return `<div class="field">
    <label for="${id}">${escapeHtml(descriptor.label)}</label>
    ${controlMarkup(descriptor, value, id, dataset)}${extraMarkup}
    ${hint}
  </div>`;
}

function rowHeader(arrayKey, index, title) {
  return `<div class="admin__row-head">
    <span class="admin__row-title">${escapeHtml(title)}</span>
    <button type="button" class="admin__row-remove" data-remove="${arrayKey}:${index}">Remove</button>
  </div>`;
}

function roundRow(item, index) {
  const controls = ROUND_FIELDS.map((f) => fieldBlock(f, item[f.key], { array: "rounds", index, field: f.key })).join("");
  return `<div class="admin__row" data-row="rounds:${index}">
    ${rowHeader("rounds", index, `Round ${index + 1}${item.id ? " · " + item.id : ""}`)}
    <div class="admin__grid">${controls}</div>
  </div>`;
}
function founderRow(item, index) {
  const controls = FOUNDER_FIELDS.map((f) => fieldBlock(f, item[f.key], { array: "founders", index, field: f.key })).join("");
  return `<div class="admin__row" data-row="founders:${index}">
    ${rowHeader("founders", index, `Founder ${index + 1}${item.name ? " · " + item.name : ""}`)}
    <div class="admin__grid">${controls}</div>
  </div>`;
}
function sourceRow(item, index) {
  const controls = SOURCE_FIELDS.map((f) => {
    const extra = f.key === "url" ? `<span class="field__preview" data-preview="sources:${index}"></span>` : "";
    return fieldBlock(f, item[f.key], { array: "sources", index, field: f.key }, extra);
  }).join("");
  return `<div class="admin__row" data-row="sources:${index}">
    ${rowHeader("sources", index, `Source ${index + 1}${item.id ? " · " + item.id : ""}`)}
    <div class="admin__grid">${controls}</div>
  </div>`;
}

const ROW_GROUPS = {
  "Funding rounds": { array: "rounds", noun: "a round", renderRow: roundRow },
  "Founders": { array: "founders", noun: "a founder", renderRow: founderRow },
  "Sources": { array: "sources", noun: "a source", renderRow: sourceRow },
};

function groupMarkup(name, record) {
  if (ROW_GROUPS[name]) {
    const { array, noun, renderRow } = ROW_GROUPS[name];
    const rows = (record[array] || []).map(renderRow).join("");
    return `<fieldset class="admin__group"><legend>${escapeHtml(name)}</legend>
      <div class="admin__rows" data-rows="${array}">${rows}</div>
      <button type="button" class="admin__add" data-add="${array}">+ Add ${escapeHtml(noun)}</button>
    </fieldset>`;
  }
  const fields = FIELDS.filter((f) => f.group === name);
  const controls = fields.map((f) => {
    const extra = f.previewKey ? `<span class="field__preview" data-preview="${f.previewKey}"></span>` : "";
    return fieldBlock(f, getPath(record, f.key), { field: f.key }, extra);
  }).join("");
  return `<fieldset class="admin__group"><legend>${escapeHtml(name)}</legend>
    <div class="admin__grid">${controls}</div>
  </fieldset>`;
}

const ROW_TEMPLATES = {
  rounds: (n) => ({ id: `r${n}`, date: "", stage: "", amount: null, currency: "", approximate: false,
    postMoney: null, leadInvestors: [], investors: [], source: "" }),
  founders: () => ({ name: "", role: "", current: true }),
  sources: (n) => ({ id: `s${n}`, publication: "", title: "", url: "", publishedOn: "", quote: "" }),
};

function fieldsFor(arrayKey) {
  return { rounds: ROUND_FIELDS, founders: FOUNDER_FIELDS, sources: SOURCE_FIELDS }[arrayKey];
}

function readControlValue(el, descriptor) {
  if (descriptor.type === "checkbox") return el.checked;
  if (descriptor.list) return parseList(el.value);
  if (descriptor.type === "number") return parseNumberOrNull(el.value);
  return el.value;
}

function setPreviewLink(span, url) {
  if (!span) return;
  if (url && isSafeUrl(url)) {
    span.innerHTML = `<a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer">open ↗</a>`;
  } else {
    span.textContent = url ? "not a safe http(s) link" : "";
  }
}

export function mount(root = document) {
  let record = createBlankRecord();
  let companies = [];
  let lastBuilt = null;

  const groupsEl = root.querySelector("[data-groups]");
  const form = root.querySelector("[data-form]");
  const loadSelect = root.querySelector("[data-load]");
  const errorsEl = root.querySelector("[data-errors]");
  const previewEl = root.querySelector("[data-preview]");
  const downloadBtn = root.querySelector("[data-download]");
  const copyBtn = root.querySelector("[data-copy]");
  const reasonEl = root.querySelector("[data-reason]");

  function renderGroups() {
    groupsEl.innerHTML = GROUP_ORDER.map((name) => groupMarkup(name, record)).join("");
  }

  function refreshLinkPreviews() {
    setPreviewLink(form.querySelector('[data-preview="website"]'), record.website);
    form.querySelectorAll('[data-preview^="sources:"]').forEach((span) => {
      const index = Number(span.dataset.preview.split(":")[1]);
      setPreviewLink(span, record.sources?.[index]?.url);
    });
  }

  function renderErrors(errors) {
    errorsEl.classList.toggle("admin__errors--ok", errors.length === 0);
    if (!errors.length) {
      errorsEl.textContent = "No errors — ready to download.";
      return;
    }
    const list = document.createElement("ul");
    for (const message of errors) {
      const item = document.createElement("li");
      item.textContent = message;
      list.appendChild(item);
    }
    errorsEl.replaceChildren(list);
  }

  function setActionsState(ok, errorCount) {
    downloadBtn.disabled = !ok;
    copyBtn.disabled = !ok;
    reasonEl.textContent = ok ? "" : `Fix ${errorCount} error${errorCount === 1 ? "" : "s"} below before downloading or copying.`;
  }

  // Runs on every keystroke, so it must never leave the page half-rendered: if a record's
  // shape is too far outside anything the form itself would produce (e.g. a hand-corrupted
  // companies.json), fail closed — disable the actions and say so — rather than throwing and
  // freezing the preview/errors on stale content.
  function refreshPreviewAndErrors() {
    try {
      lastBuilt = buildRecord(record);
      const errors = validateRecord(lastBuilt);
      previewEl.textContent = JSON.stringify(lastBuilt, null, 1);
      renderErrors(errors);
      setActionsState(errors.length === 0, errors.length);
      refreshLinkPreviews();
    } catch (error) {
      console.error(error);
      lastBuilt = null;
      errorsEl.classList.remove("admin__errors--ok");
      errorsEl.textContent = "This record's shape is too unusual for the in-browser checker "
        + "(see the console). Fix the offending field, or check the file with "
        + "tools/validate.py once you've saved it.";
      setActionsState(false, 1);
    }
  }

  form.addEventListener("input", (event) => handleControlChange(event.target));
  form.addEventListener("change", (event) => handleControlChange(event.target));

  function handleControlChange(el) {
    if (el.dataset.field === undefined) return;
    const descriptor = el.dataset.array
      ? fieldsFor(el.dataset.array).find((f) => f.key === el.dataset.field)
      : FIELDS.find((f) => f.key === el.dataset.field);
    if (!descriptor) return;
    const value = readControlValue(el, descriptor);
    if (el.dataset.array) {
      const index = Number(el.dataset.index);
      record[el.dataset.array] = record[el.dataset.array] || [];
      record[el.dataset.array][index] = record[el.dataset.array][index] || {};
      record[el.dataset.array][index][el.dataset.field] = value;
    } else if (descriptor.pruneWhenEmpty && Array.isArray(value) && value.length === 0) {
      // Collapse back to "absent" only at the moment *this* edit empties it — not on every
      // later render, which can't distinguish "the operator just cleared it" from "it was
      // already an empty array when loaded" (see buildRecord()'s comment on why that check
      // can't live there for this field the way it safely can for `disputed`).
      delete record[el.dataset.field];
    } else {
      setPath(record, el.dataset.field, value);
    }
    refreshPreviewAndErrors();
  }

  // renderGroups() rebuilds the whole fieldset's innerHTML, so the button that was just
  // clicked no longer exists afterward — re-find its replacement and refocus it, rather
  // than silently dropping focus back to <body> after Remove (there is no new row to
  // send focus to there — the row is gone — so the Add button is the sensible landing
  // spot, same as before).
  function refocusAdd(arrayKey) {
    form.querySelector(`[data-add="${arrayKey}"]`)?.focus();
  }

  // Task 19 fix: after Add, focus used to land back on the Add button itself, which
  // makes an operator using a screen reader or keyboard Tab past the very row they
  // just asked to fill in — they'd have to tab through every field of every existing
  // row again to reach it. The new row's first field (its data-row markup comes from
  // roundRow/founderRow/sourceRow, in the same FIELDS order used elsewhere) is the
  // useful place to land, so an operator can start typing immediately. Falls back to
  // the Add button only if the row somehow isn't found — never drops focus silently.
  function focusFirstFieldInRow(arrayKey, index) {
    const row = form.querySelector(`[data-row="${arrayKey}:${index}"]`);
    const field = row?.querySelector("input, textarea, select");
    if (field) field.focus();
    else refocusAdd(arrayKey);
  }

  form.addEventListener("click", (event) => {
    const addKey = event.target.closest("[data-add]")?.dataset.add;
    if (addKey) {
      event.preventDefault();
      record[addKey] = record[addKey] || [];
      record[addKey].push(ROW_TEMPLATES[addKey](record[addKey].length + 1));
      const newIndex = record[addKey].length - 1;
      renderGroups();
      refreshPreviewAndErrors();
      focusFirstFieldInRow(addKey, newIndex);
      return;
    }
    const removeKey = event.target.closest("[data-remove]")?.dataset.remove;
    if (removeKey) {
      event.preventDefault();
      const [arrayKey, indexStr] = removeKey.split(":");
      record[arrayKey].splice(Number(indexStr), 1);
      renderGroups();
      refreshPreviewAndErrors();
      refocusAdd(arrayKey);
    }
  });

  function loadRecord(next) {
    record = next;
    renderGroups();
    refreshPreviewAndErrors();
  }

  loadSelect.addEventListener("change", () => {
    const slug = loadSelect.value;
    const found = slug ? companies.find((c) => c.slug === slug) : null;
    loadRecord(found ? stripDerived(found) : createBlankRecord());
  });

  downloadBtn.addEventListener("click", () => {
    if (!downloadBtn.disabled && lastBuilt) download(lastBuilt);
  });
  copyBtn.addEventListener("click", async () => {
    if (copyBtn.disabled || !lastBuilt) return;
    try {
      await navigator.clipboard.writeText(JSON.stringify(lastBuilt, null, 1));
      reasonEl.textContent = "Copied to the clipboard.";
      setTimeout(() => { if (!downloadBtn.disabled) reasonEl.textContent = ""; }, 2500);
    } catch (error) {
      console.error(error);
      reasonEl.textContent = "Could not copy — your browser blocked clipboard access. Use Download instead.";
    }
  });

  async function loadCompanyList() {
    try {
      const response = await fetch("data/companies.json", { cache: "no-cache" });
      if (!response.ok) throw new Error(`companies.json ${response.status}`);
      const data = await response.json();
      companies = data.companies || [];
    } catch (error) {
      // A missing/unreachable companies.json must not block editing a blank record —
      // only the "load an existing company" convenience is unavailable.
      console.error(error);
      companies = [];
    }
    for (const company of [...companies].sort((a, b) => a.name.localeCompare(b.name))) {
      const option = document.createElement("option");
      option.value = company.slug;
      option.textContent = company.name;
      loadSelect.appendChild(option);
    }
  }

  renderGroups();
  refreshPreviewAndErrors();
  loadCompanyList();

  // Debugging/testing hook, same convention as main.js's window.__data/__sky/__controls.
  return {
    get record() { return record; },
    get lastBuilt() { return lastBuilt; },
    loadRecord,
  };
}

if (document.querySelector("[data-form]")) {
  window.__admin = mount(document);
}
