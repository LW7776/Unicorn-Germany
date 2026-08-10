/* Blocks rise a little and fade in as they reach the viewport.

   This is the effect most likely to make a site feel generic, so it is kept
   deliberately small: fourteen pixels, one fade, once per element, and never a
   second time. Nothing scales, nothing slides in from the side, nothing repeats
   when you scroll back up. If a reader notices it happening, it is too much.

   The hidden starting state lives in base.css rather than being applied here, so
   an element is never painted at full strength and then snatched back for a
   frame while a module boots. The cost of that choice is that a failure in this
   file would leave content invisible, which is unacceptable for a register, so
   every path that cannot animate reveals everything instead:

     - prefers-reduced-motion, checked here because base.css's blanket rule
       flattens the transition but would still leave the element at opacity 0,
     - no IntersectionObserver,
     - a throw anywhere in setup (the callers wrap this),
     - JavaScript off entirely, which each page's <noscript> covers.

   base.css also scopes the hidden state to `prefers-reduced-motion:
   no-preference`, so under reduced motion the content is never hidden in the
   first place and this module simply does nothing. Two independent guards for
   the one failure that actually matters. */
const REDUCED = matchMedia("(prefers-reduced-motion: reduce)");

const REVEALED = "is-revealed";
// A few tens of milliseconds between neighbours, capped: a batch of eleven rows
// arriving all at once must not make the last one wait two thirds of a second,
// which stops reading as a stagger and starts reading as a queue.
const STAGGER_MS = 55;
const STAGGER_CAP = 4;

let observer = null;

function revealNow(element) {
  element.classList.add(REVEALED);
}

function ensureObserver() {
  if (observer) return observer;
  observer = new IntersectionObserver((entries, self) => {
    // Only the entries that actually crossed in, re-indexed, so the stagger
    // counts arriving elements rather than everything the callback was handed.
    entries
      .filter((entry) => entry.isIntersecting)
      .forEach((entry, index) => {
        const delay = Math.min(index, STAGGER_CAP) * STAGGER_MS;
        entry.target.style.transitionDelay = `${delay}ms`;
        revealNow(entry.target);
        self.unobserve(entry.target);
      });
  }, {
    // A block counts as arrived a little before its top edge reaches the
    // bottom of the viewport, so the movement finishes as it comes into
    // reading position rather than starting there.
    rootMargin: "0px 0px -6% 0px",
    threshold: 0.05,
  });
  return observer;
}

/** Wires every unwired [data-reveal] inside `root`. Safe to call again after
    rendering more of the page: an element is marked once and never re-observed,
    which is what keeps this from re-running on a re-render. */
export function revealWithin(root = document) {
  const targets = [...root.querySelectorAll("[data-reveal]:not([data-revealed])")];
  if (!targets.length) return;
  targets.forEach((element) => { element.dataset.revealed = ""; });

  if (REDUCED.matches || typeof IntersectionObserver === "undefined") {
    targets.forEach(revealNow);
    return;
  }
  try {
    const io = ensureObserver();
    targets.forEach((element) => io.observe(element));
  } catch (error) {
    // Whatever went wrong, the content is the product.
    console.error(error);
    targets.forEach(revealNow);
  }
}
