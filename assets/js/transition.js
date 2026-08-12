/* The landing page leaves and the register arrives, as one vertical move.

   Hero and register are locked to the same distance, the same duration and the
   same curve, so what a viewer sees is one page travelling upward by exactly
   one screen rather than two elements animating near each other. The hero
   starts on top of the register and slides out through the top edge while the
   register comes up from below the fold into the space it leaves.

   This replaced a FLIP flight that sent one spark per company from its star to
   its grid cell. That move was about the dataset; this one is about the
   navigation, which is the thing the button actually does. */
const REDUCED = matchMedia("(prefers-reduced-motion: reduce)");

const DURATION = 820;
// Symmetric ease-in-out. The old flight used the site's --ease-out, which is
// right for something arriving from nowhere and wrong for something that is
// already on screen and has to start moving: an ease-out lift jumps at the
// first frame. This accelerates the departure and settles the arrival.
const EASING = "cubic-bezier(.65,0,.35,1)";

// The CTA stays clickable for the duration of the move (hero.hidden only flips
// at the very end), so a double-click is entirely foreseeable — it would stack
// a second lift on top of the first and leave the register mid-slide.
// Module-level, not per-call: enterRegister is only ever meant to run once for
// the page's lifetime.
let inFlight = false;

export async function enterRegister({ hero, register, sky }) {
  if (inFlight) return;
  inFlight = true;
  const enterButton = document.querySelector("[data-enter]");
  const topbar = document.querySelector("[data-topbar]");
  if (enterButton) enterButton.disabled = true;
  // Declared out here so the cleanup can reach both. A forwards fill left by a
  // throw mid-move would park the register a screen below itself and drop the
  // hero back into flow halfway off the top, which is the one failure that
  // would be worse than no animation at all.
  let lift = null;
  let rise = null;

  try {
    register.hidden = false;

    // hero.css gives .hero a full 100svh in normal document flow, so the instant
    // .register unhides it is pushed below the fold. Taking hero out of flow puts
    // the register at the top of the document immediately, which is where it has
    // to end up; a positioned element stacks above in-flow content, so hero still
    // covers it completely for as long as it is there.
    // A class (not an inline style) so the lift can never survive as a stray
    // inline style — the finally below always removes it, throw or no throw.
    hero.classList.add("hero--lifted");
    // The register is about to be pushed a screen below its own position. Without
    // this the document grows by that screen for the duration, the scrollbar
    // jumps, and a scroll wheel turned mid-move fights the animation.
    document.documentElement.classList.add("is-entering");

    if (REDUCED.matches) {
      hero.hidden = true;
      topbar.hidden = false;
      sky.stop();
      return;
    }

    // In pixels rather than `100svh`, so both halves are guaranteed to be the
    // same number. Read once, before anything animates: an address bar that
    // collapses mid-move would otherwise give the two elements two different
    // definitions of one screen and leave a seam between them.
    const screen = window.innerHeight;
    const timing = { duration: DURATION, easing: EASING, fill: "forwards" };
    lift = hero.animate(
      { transform: ["translateY(0)", `translateY(${-screen}px)`] }, timing);
    rise = register.animate(
      { transform: [`translateY(${screen}px)`, "translateY(0)"] }, timing);

    await Promise.all([lift.finished, rise.finished]);

    hero.hidden = true;
    sky.stop();
    // Held back until now. The topbar is fixed, so through the move it would
    // have hung in the viewport over the departing hero, the one element not
    // travelling with the page.
    topbar.hidden = false;
    topbar.animate({ opacity: [0, 1] }, { duration: 240, easing: "cubic-bezier(.22,1,.36,1)" });
    // .cell__open is the focusable thing now that the card itself is a <div>.
    register.querySelector(".cell__open")?.focus({ preventScroll: true });
  } finally {
    // Runs on every exit — success, the reduced-motion early return, or a throw
    // partway through the move — so a mid-transition failure can never strand
    // the page: no permanently full-viewport hero, no register parked a screen
    // below where it belongs, no page that cannot be scrolled. A stuck overlay
    // is a worse outcome than a slightly imperfect animation ending, so this
    // cleanup is unconditional rather than trying to distinguish failure modes.
    hero.classList.remove("hero--lifted");
    document.documentElement.classList.remove("is-entering");
    // Both resting states are untransformed, so cancelling hands each element
    // back to CSS at exactly the position it was ending on. On the success path
    // this drops two forwards fills that would otherwise sit on top of every
    // later layout the page does; on the failure path it is what puts the page
    // back. Order matters only in that hero is already hidden by then when the
    // move completed, so its snap back to zero is never seen.
    lift?.cancel();
    rise?.cancel();
    if (enterButton) enterButton.disabled = false;
    inFlight = false;
  }
}
