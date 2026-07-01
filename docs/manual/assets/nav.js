(() => {
  const here = location.pathname.replace(/\\/g, "/").split("/docs/manual/").pop() || "index.html";
  for (const link of document.querySelectorAll(".sidebar a")) {
    const href = link.getAttribute("href");
    if (!href) continue;
    const normalized = new URL(href, location.href).pathname.replace(/\\/g, "/").split("/docs/manual/").pop();
    if (normalized === here) link.classList.add("active");
  }
})();
