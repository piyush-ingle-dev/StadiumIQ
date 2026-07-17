// StadiumIQ shared front-end behavior.
// Individual pages load their own script for page-specific logic;
// this file is for behavior shared across every page.

document.addEventListener("DOMContentLoaded", () => {
  // Auto-dismiss flash messages after a few seconds without removing
  // them from the accessibility tree abruptly (fade, then remove).
  const flashes = document.querySelectorAll(".flash");
  flashes.forEach((el) => {
    setTimeout(() => {
      el.style.transition = "opacity 0.4s ease";
      el.style.opacity = "0";
      setTimeout(() => el.remove(), 500);
    }, 6000);
  });
});
