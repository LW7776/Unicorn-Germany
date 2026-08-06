/* The signature move: every point of light flies to the cell that represents it.
   Hand-rolled FLIP — measure the target, animate a clone from the star's position. */
const REDUCED = matchMedia("(prefers-reduced-motion: reduce)");

export async function enterRegister({ hero, register, sky, grid }) {
  register.hidden = false;
  document.querySelector("[data-topbar]").hidden = false;

  // hero.css gives .hero a full 100svh in normal document flow, so the instant
  // .register unhides it is pushed below the fold — every grid cell would land
  // off-screen and the flight would be invisible. Taking hero out of flow puts
  // the register at the top of the document immediately; a positioned element
  // stacks above in-flow content, so hero still visually overlays it while it
  // fades, and the flight lands somewhere the viewer can actually see.
  hero.style.position = "fixed";
  hero.style.inset = "0";

  if (REDUCED.matches) {
    hero.hidden = true;
    sky.stop();
    return;
  }

  const cells = [...grid.querySelectorAll(".cell")];
  const flights = cells.map((cell, index) => {
    const box = cell.getBoundingClientRect();
    const star = sky.pointAt(index);
    const spark = document.createElement("span");
    spark.className = "spark";
    spark.style.left = `${star.x}px`;
    spark.style.top = `${star.y}px`;
    document.body.append(spark);
    cell.style.opacity = "0";
    return { spark, cell, dx: box.left + box.width / 2 - star.x, dy: box.top + box.height / 2 - star.y };
  });

  hero.animate(
    { opacity: [1, 0], filter: ["blur(0px)", "blur(12px)"], transform: ["translateY(0)", "translateY(-4vh)"] },
    { duration: 600, easing: "cubic-bezier(.22,1,.36,1)", fill: "forwards" });

  await Promise.all(flights.map(({ spark, dx, dy }, index) =>
    spark.animate(
      { transform: ["translate(0,0) scale(1)", `translate(${dx}px, ${dy}px) scale(.4)`], opacity: [1, 0] },
      { duration: 900, delay: index * 12, easing: "cubic-bezier(.22,1,.36,1)", fill: "forwards" }
    ).finished));

  flights.forEach(({ spark, cell }, index) => {
    spark.remove();
    cell.style.opacity = "";
    cell.animate({ opacity: [0, 1], transform: ["scale(.94)", "scale(1)"] },
      { duration: 320, delay: index * 8, easing: "cubic-bezier(.22,1,.36,1)" });
  });

  hero.hidden = true;
  sky.stop();
  register.querySelector(".cell")?.focus({ preventScroll: true });
}
