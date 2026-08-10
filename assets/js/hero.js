/* The punchline arrives rather than simply being there.

   Six words rise a third of a line and come out of a blur, one after the next,
   with the last one landing at 700ms. That is the whole of it. Body copy is
   never animated anywhere on this site — a paragraph that assembles itself is a
   paragraph the reader has to wait for — and this is the one headline that gets
   the treatment, for the same reason .intro__accent is the one gradient phrase:
   a signature used twice is a habit.

   Two gates, and they are the interesting part:

   Reduced motion. base.css's blanket `animation-duration: .01ms` cannot touch a
   Web Animations call, exactly as DESIGN.md warns, so this checks the media
   query itself and simply never starts — the words are already in place, so
   "no animation" is the correct static state with nothing to fall back to.

   Once per session. A rise-and-clear is an arrival, and an arrival that happens
   every time you come back from the About page is a tic. sessionStorage is the
   right scope: it is the visit, it clears itself, and it costs no consent
   banner because it is not tracking (no id, no network, no persistence past the
   tab). Every access is guarded because sessionStorage throws outright in a
   sandboxed or storage-blocked context, and a decorative animation must never
   be the thing that takes the hero down. */
const REDUCED = matchMedia("(prefers-reduced-motion: reduce)");
const SEEN_KEY = "gu:hero-headline";

const WORD_MS = 520;
const STAGGER_MS = 36;   // 520 + 5 x 36 = 700ms from first move to last landing

function playedThisSession() {
  try {
    return sessionStorage.getItem(SEEN_KEY) === "1";
  } catch {
    // Storage unavailable: treat the visit as fresh. Playing the animation once
    // too often is a far smaller failure than the hero throwing on load.
    return false;
  }
}

function rememberPlayed() {
  try {
    sessionStorage.setItem(SEEN_KEY, "1");
  } catch {
    // Nothing to do and nothing worth reporting — see above.
  }
}

/** Returns whether it actually ran, which is what the reduced-motion check in
    the browser verification counts. */
export function playHeroHeadline(title = document.querySelector("[data-hero-title]")) {
  if (!title || REDUCED.matches || playedThisSession()) return false;
  const words = [...title.querySelectorAll(".hero__word")];
  if (!words.length) return false;

  rememberPlayed();
  title.classList.add("hero__title--kinetic");

  const animations = words.map((word, index) => word.animate(
    {
      opacity: [0, 1],
      filter: ["blur(10px)", "blur(0px)"],
      transform: ["translateY(.34em)", "translateY(0)"],
    },
    {
      duration: WORD_MS,
      delay: index * STAGGER_MS,
      easing: "cubic-bezier(.22,1,.36,1)",
      // `both` so a word is held at its start state through its own delay
      // rather than flashing in at full strength and then animating from zero.
      fill: "both",
    }));

  Promise.all(animations.map((animation) => animation.finished))
    .then(() => {
      // Order matters. The class is what holds a word at opacity 0, and the
      // fill is what overrides it while the animation exists — cancel first and
      // every word blinks out for a frame before the class comes off. So the
      // class goes first, and only then is the fill released, which also stops
      // six animations holding computed styles for the life of the page.
      title.classList.remove("hero__title--kinetic");
      animations.forEach((animation) => animation.cancel());
    })
    .catch(() => {
      // A cancelled animation rejects. Whatever the cause, the headline must
      // end up readable, which means the class must come off.
      title.classList.remove("hero__title--kinetic");
    });

  return true;
}
