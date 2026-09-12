const header = document.querySelector("[data-header]");
const menuButton = document.querySelector("[data-menu-button]");
const mobileMenu = document.querySelector("[data-mobile-menu]");
const copyButton = document.querySelector("[data-copy-email]");
const cursorGlow = document.querySelector(".cursor-glow");
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

const setMenu = (open) => {
  if (!menuButton || !mobileMenu) return;
  menuButton.setAttribute("aria-expanded", String(open));
  menuButton.setAttribute("aria-label", open ? "Close navigation" : "Open navigation");
  mobileMenu.classList.toggle("is-open", open);
  document.body.classList.toggle("menu-open", open);
};

menuButton?.addEventListener("click", () => {
  setMenu(menuButton.getAttribute("aria-expanded") !== "true");
});

mobileMenu?.querySelectorAll("a").forEach((link) => {
  link.addEventListener("click", () => setMenu(false));
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") setMenu(false);
});

const updateHeader = () => {
  header?.classList.toggle("is-scrolled", window.scrollY > 24);
};

updateHeader();
window.addEventListener("scroll", updateHeader, { passive: true });

const revealElements = document.querySelectorAll("[data-reveal]");
if (reducedMotion.matches || !("IntersectionObserver" in window)) {
  revealElements.forEach((element) => element.classList.add("is-visible"));
} else {
  const revealObserver = new IntersectionObserver(
    (entries, observer) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    },
    { threshold: 0.12, rootMargin: "0px 0px -40px" },
  );
  revealElements.forEach((element) => revealObserver.observe(element));
}

const navLinks = document.querySelectorAll(".desktop-nav a");
const sections = [...navLinks]
  .map((link) => document.querySelector(link.getAttribute("href")))
  .filter(Boolean);

if ("IntersectionObserver" in window) {
  const navObserver = new IntersectionObserver(
    (entries) => {
      const active = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
      if (!active) return;
      navLinks.forEach((link) => {
        const selected = link.getAttribute("href") === `#${active.target.id}`;
        link.classList.toggle("is-active", selected);
        if (selected) link.setAttribute("aria-current", "true");
        else link.removeAttribute("aria-current");
      });
    },
    { threshold: [0.2, 0.45, 0.7], rootMargin: "-15% 0px -55%" },
  );
  sections.forEach((section) => navObserver.observe(section));
}

if (cursorGlow && !reducedMotion.matches) {
  window.addEventListener(
    "pointermove",
    (event) => {
      cursorGlow.style.transform = `translate(${event.clientX - 240}px, ${event.clientY - 240}px)`;
    },
    { passive: true },
  );
}

copyButton?.addEventListener("click", async () => {
  const label = copyButton.querySelector("[data-copy-label]");
  try {
    await navigator.clipboard.writeText("sujoyghosh7584@gmail.com");
    if (label) label.textContent = "Email copied";
  } catch {
    if (label) label.textContent = "sujoyghosh7584@gmail.com";
  }
  window.setTimeout(() => {
    if (label) label.textContent = "Copy email";
  }, 2200);
});

document.querySelectorAll("[data-year]").forEach((element) => {
  element.textContent = String(new Date().getFullYear());
});

window.addEventListener("resize", () => {
  if (window.innerWidth > 980) setMenu(false);
});
