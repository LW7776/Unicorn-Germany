import { escapeHtml } from "./html.js";

// sort.valuationEur is null for a company whose valuation no source has published
// (tools/build.py declines to invent a stand-in figure just to make this comparator
// simpler). Those sort to the end of "Highest valuation" — "at least a billion, amount
// unknown" belongs below every known figure, not above them — and A–Z amongst
// themselves so the tail is stable rather than arbitrary. Subtracting null would have
// coerced it to 0 and produced the same tail by accident, which is not the same thing
// as producing it on purpose: any future non-EUR-zero handling would have silently
// broken it.
function byValuation(a, b) {
  const left = a.sort.valuationEur, right = b.sort.valuationEur;
  if (left === null && right === null) return a.sort.name.localeCompare(b.sort.name);
  if (left === null) return 1;
  if (right === null) return -1;
  return right - left;
}

const SORTS = {
  newest: (a, b) => cmp(b.sort.newest, a.sort.newest),
  valuation: byValuation,
  latest: (a, b) => cmp(b.sort.latestRound, a.sort.latestRound),
  name: (a, b) => a.sort.name.localeCompare(b.sort.name),
};

function cmp(a, b) { return a[0] - b[0] || a[1] - b[1]; }

export function applyState(companies, state) {
  const query = state.query.trim().toLowerCase();
  return companies
    .filter((c) => !state.sector || (c.sectors || []).includes(state.sector))
    .filter((c) => !state.city || (c.hq?.city ?? "") === state.city)
    .filter((c) => !query
      || c.name.toLowerCase().includes(query)
      || (c.sectors || []).join(" ").toLowerCase().includes(query)
      // `sectors` is now a handful of broad industries shared across the register
      // (the chips), so the specific term a searcher is likelier to type — "Process
      // Mining", "Spend Management" — lives in `niche` instead. Both stay
      // searchable; only `sectors` drives the chips below.
      || (c.niche ?? "").toLowerCase().includes(query)
      || (c.hq?.city ?? "").toLowerCase().includes(query)
      || (c.investors || []).join(" ").toLowerCase().includes(query))
    .sort(SORTS[state.sort]);
}

export function mountControls({ container, companies, onChange }) {
  const state = { query: "", sector: "", city: "", sort: "newest" };
  // data/companies.json is validated (tools/validate.py) before it can be
  // committed, but the browser has no such guarantee at runtime — a bad
  // deploy or a manually edited file could still ship a record with a null
  // `sectors` or a `hq` missing `city`. flatMap/map over the raw field would
  // throw synchronously here, before boot() even reaches the [data-enter]
  // listener, taking the whole page down with it. Falling back to `[]` / ""
  // instead means that one record just contributes no filter value.
  const sectors = [...new Set(companies.flatMap((c) => c.sectors || []))].sort();
  const cities = [...new Set(companies.map((c) => c.hq?.city ?? ""))]
    .filter(Boolean).sort();

  // Every sector and city string below comes from data/companies.json — hand-
  // written and pipeline-generated, so untrusted like every other company
  // value. escapeHtml() is safe inside these quoted attributes and text
  // nodes (but not inside an unquoted attribute), so every attribute here
  // stays quoted.
  container.innerHTML = `
    <div class="controls__row">
      <label class="controls__search">
        <span class="visually-hidden">Search companies</span>
        <input type="search" data-query placeholder="Search company, city or investor"
               autocomplete="off">
        <kbd aria-hidden="true">⌘K</kbd>
      </label>
      <label class="controls__select">
        <span class="label">Sort</span>
        <select data-sort>
          <option value="newest">Newest unicorn</option>
          <option value="valuation">Highest valuation</option>
          <option value="latest">Latest round</option>
          <option value="name">A–Z</option>
        </select>
      </label>
      <label class="controls__select">
        <span class="label">City</span>
        <select data-city>
          <option value="">All cities</option>
          ${cities.map((c) => `<option value="${escapeHtml(c)}">${escapeHtml(c)}</option>`).join("")}
        </select>
      </label>
      ${/* The only way into the map. It used to be a nav entry beside Companies,
            which sold it as a separate destination; it is a second way of looking
            at the same 32 records, so it lives with the other controls that decide
            what the register shows. main.js wires both buttons by [data-view]
            after this markup is written. */""}
      <div class="controls__select controls__view">
        <span class="label" id="controls-view">View</span>
        <div class="viewtoggle" role="group" aria-labelledby="controls-view">
          <button class="viewtoggle__btn" type="button" data-view="grid" aria-pressed="true">Grid</button>
          <button class="viewtoggle__btn" type="button" data-view="map" aria-pressed="false">Map</button>
        </div>
      </div>
    </div>
    <div class="chips" role="radiogroup" aria-label="Filter by sector">
      <button class="chip" type="button" role="radio" data-sector="" aria-checked="true" tabindex="0">All sectors</button>
      ${sectors.map((s) => `<button class="chip" type="button" role="radio" data-sector="${escapeHtml(s)}" aria-checked="false" tabindex="-1">${escapeHtml(s)}</button>`).join("")}
    </div>
    <p class="controls__count" role="status" data-count></p>`;

  const queryInput = container.querySelector("[data-query]");

  const emit = () => {
    const visible = applyState(companies, state);
    // companies.length can be 0 before Tasks 15–18 populate data/companies.json;
    // "0 of 0 companies" still reads sensibly, no NaN or blank string.
    container.querySelector("[data-count]").textContent =
      `${visible.length} of ${companies.length} companies`;
    onChange(visible);
  };

  queryInput.addEventListener("input", (event) => {
    state.query = event.target.value; emit();
  });
  container.querySelector("[data-sort]").addEventListener("change", (event) => {
    state.sort = event.target.value; emit();
  });
  container.querySelector("[data-city]").addEventListener("change", (event) => {
    state.city = event.target.value; emit();
  });
  // The sector chips are a single-select group — exactly one filter value is
  // ever active — so they follow the WAI-ARIA radiogroup pattern rather than
  // a set of independent toggle buttons: role="radio"/aria-checked instead
  // of aria-pressed, and a roving tabindex (only the checked chip is a Tab
  // stop; Arrow keys move focus *and* selection among the rest), matching
  // how a native <input type="radio"> group behaves for keyboard and
  // screen-reader users.
  const chips = () => [...container.querySelectorAll("[data-sector]")];

  const selectChip = (chip) => {
    state.sector = chip.dataset.sector;
    chips().forEach((other) => {
      const checked = other === chip;
      other.setAttribute("aria-checked", String(checked));
      other.tabIndex = checked ? 0 : -1;
    });
    emit();
  };

  chips().forEach((chip) => {
    chip.addEventListener("click", () => selectChip(chip));
  });

  container.querySelector(".chips").addEventListener("keydown", (event) => {
    const list = chips();
    const current = list.indexOf(document.activeElement);
    if (current === -1) return;
    const moves = {
      ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1,
    };
    let next;
    if (event.key in moves) {
      next = (current + moves[event.key] + list.length) % list.length;
    } else if (event.key === "Home") {
      next = 0;
    } else if (event.key === "End") {
      next = list.length - 1;
    } else {
      return;
    }
    event.preventDefault();
    list[next].focus();
    selectChip(list[next]);
  });

  addEventListener("keydown", (event) => {
    if (!(event.metaKey || event.ctrlKey) || event.key.toLowerCase() !== "k") return;
    // Skip while the search field already has focus: macOS text fields bind
    // Ctrl+K natively to "delete to end of line", and the input is already
    // where ⌘K would send focus, so there is nothing useful to preempt.
    // Hijacking it here would silently eat that native editing shortcut
    // while someone is mid-edit in the very field the shortcut targets.
    if (document.activeElement === queryInput) return;
    event.preventDefault();
    queryInput.focus();
  });
  document.querySelector("[data-open-search]")?.addEventListener("click", () => {
    queryInput.focus();
  });

  emit();
  return { state, setCity: (city) => { state.city = city; container.querySelector("[data-city]").value = city; emit(); } };
}
