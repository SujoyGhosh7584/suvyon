(() => {
  const guide = window.SUVYON_GUIDE;
  const repoBase = "https://github.com/SujoyGhosh7584/suvyon/blob/Interview-Prep/";
  const progressKey = "suvyon-project-explorer-progress-v1";
  const chapters = document.querySelector("#chapters");
  const nav = document.querySelector("#topic-nav");
  const dialog = document.querySelector("#source-dialog");

  const escapeHtml = (value) =>
    String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");

  const statusLabel = (status) =>
    status === "implemented" ? "Implemented" : status === "partial" ? "Partial" : "Planned";

  const sourceUrl = (item) =>
    `${repoBase}${item.path}${item.line ? `#L${item.line}` : ""}`;

  const uniqueSources = (topic) => {
    const seen = new Set();
    return topic.flow.steps.flatMap((step) => step.sources || []).filter((item) => {
      const key = `${item.path}:${item.line}`;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  };

  const renderSources = (sources) =>
    sources.map((item) => `
      <a class="source-link" href="${sourceUrl(item)}" target="_blank" rel="noreferrer">
        <span><strong>${escapeHtml(item.label)}</strong>${item.note ? `<br><small>${escapeHtml(item.note)}</small>` : ""}</span>
        <span class="source-path">${escapeHtml(item.path)}${item.line ? `:${item.line}` : ""} ↗</span>
      </a>
    `).join("");

  const renderFlow = (topic) => topic.flow.steps.map((step, index) => `
    ${index ? '<span class="flow-arrow" aria-hidden="true">→</span>' : ""}
    <div class="flow-step">
      <div><small>${escapeHtml(step.label)}</small><strong>${escapeHtml(step.title)}</strong></div>
      <p>${escapeHtml(step.copy)}</p>
      <button data-source-topic="${topic.id}" data-source-step="${index}">Open code (${step.sources.length}) ↗</button>
    </div>
  `).join("");

  const renderTruths = (truths) => truths.map((truth) => `
    <div class="truth-item">
      <span class="status ${truth.status}">${statusLabel(truth.status)}</span>
      <p>${escapeHtml(truth.text)}</p>
    </div>
  `).join("");

  chapters.innerHTML = guide.topics.map((topic, index) => `
    <section class="chapter" id="${topic.id}" data-title="${escapeHtml(`${topic.title} ${topic.summary} ${topic.group}`.toLowerCase())}">
      <div class="chapter-header">
        <span class="chapter-number">${String(index + 1).padStart(2, "0")}</span>
        <div>
          <span class="status ${topic.status}">${statusLabel(topic.status)}</span>
          <h2>${escapeHtml(topic.title)}</h2>
          <p class="chapter-summary">${escapeHtml(topic.summary)}</p>
        </div>
        <button class="complete-button" data-complete="${topic.id}">Mark understood</button>
      </div>

      <div class="chapter-body">
        <article class="explanation">
          <h3>Easy mental model</h3>
          <p class="simple-model"><strong>Remember it like this:</strong> ${escapeHtml(topic.mentalModel)}</p>
          <h3>What actually happens</h3>
          ${topic.explanation.map((paragraph) => `<p>${escapeHtml(paragraph)}</p>`).join("")}
          <h3>Details that interviewers probe</h3>
          <ul>${topic.bullets.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
          <button class="secondary" data-all-sources="${topic.id}">Browse all chapter code ↗</button>
        </article>

        <aside class="interview-card">
          <h3>Say this in the interview</h3>
          <p class="speak-answer">${escapeHtml(topic.speak)}</p>
          <h3>Follow-up checks</h3>
          <ul>${topic.questions.map((question) => `<li>${escapeHtml(question)}</li>`).join("")}</ul>
          <h3>Implementation truth</h3>
          <div class="truth-grid">${renderTruths(topic.truths)}</div>
        </aside>

        <div class="flow-section">
          <h3>Step-by-step flow chart</h3>
          <p class="flow-note">${escapeHtml(topic.flow.note)}</p>
          <div class="flow-chart">${renderFlow(topic)}</div>
        </div>
      </div>
    </section>
  `).join("");

  let previousGroup = "";
  nav.innerHTML = guide.topics.map((topic, index) => {
    const heading = topic.group !== previousGroup
      ? `<div class="nav-group">${escapeHtml(topic.group)}</div>`
      : "";
    previousGroup = topic.group;
    return `${heading}<a class="nav-link" href="#${topic.id}" data-nav="${topic.id}"><span class="nav-index">${String(index + 1).padStart(2, "0")}</span>${escapeHtml(topic.title)}</a>`;
  }).join("");

  document.querySelector("#final-questions").innerHTML = guide.finalQuestions
    .map((question, index) => `<div class="check-item"><strong>${index + 1}.</strong> ${escapeHtml(question)}</div>`)
    .join("");

  document.querySelector("#api-catalog").innerHTML = guide.apiCatalog.map((group, index) => `
    <details class="api-group" ${index === 0 ? "open" : ""}>
      <summary>${escapeHtml(group.group)}<span class="api-count">${group.endpoints.length} endpoints</span></summary>
      <table class="api-table"><tbody>
        ${group.endpoints.map(([method, path, purpose]) => `
          <tr><td class="api-method">${escapeHtml(method)}</td><td class="api-path">${escapeHtml(path)}</td><td class="api-purpose">${escapeHtml(purpose)}</td></tr>
        `).join("")}
      </tbody></table>
      <a class="api-source" href="${sourceUrl(group.source)}" target="_blank" rel="noreferrer">Open route file at line ${group.source.line} ↗</a>
    </details>
  `).join("");

  const getProgress = () => {
    try { return new Set(JSON.parse(localStorage.getItem(progressKey) || "[]")); }
    catch { return new Set(); }
  };

  const updateProgress = () => {
    const done = getProgress();
    document.querySelectorAll("[data-complete]").forEach((button) => {
      const isDone = done.has(button.dataset.complete);
      button.classList.toggle("done", isDone);
      button.textContent = isDone ? "Understood" : "Mark understood";
    });
    const percent = Math.round((done.size / guide.topics.length) * 100);
    document.querySelector("#progress-label").textContent = `${percent}%`;
    document.querySelector("#progress-bar").style.width = `${percent}%`;
  };

  const openSources = (title, copy, sources) => {
    document.querySelector("#dialog-title").textContent = title;
    document.querySelector("#dialog-copy").textContent = copy;
    document.querySelector("#dialog-links").innerHTML = renderSources(sources);
    if (typeof dialog.showModal === "function") dialog.showModal();
    else dialog.setAttribute("open", "");
  };

  document.addEventListener("click", (event) => {
    const complete = event.target.closest("[data-complete]");
    if (complete) {
      const progress = getProgress();
      const id = complete.dataset.complete;
      progress.has(id) ? progress.delete(id) : progress.add(id);
      localStorage.setItem(progressKey, JSON.stringify([...progress]));
      updateProgress();
      return;
    }

    const stepButton = event.target.closest("[data-source-step]");
    if (stepButton) {
      const topic = guide.topics.find((item) => item.id === stepButton.dataset.sourceTopic);
      const step = topic.flow.steps[Number(stepButton.dataset.sourceStep)];
      openSources(step.title, step.copy, step.sources);
      return;
    }

    const allSources = event.target.closest("[data-all-sources]");
    if (allSources) {
      const topic = guide.topics.find((item) => item.id === allSources.dataset.allSources);
      openSources(topic.title, "Every source location referenced by this chapter.", uniqueSources(topic));
      return;
    }

    const jump = event.target.closest("[data-jump]");
    if (jump) {
      document.querySelector(`#${jump.dataset.jump}`)?.scrollIntoView({ behavior: "smooth" });
    }
  });

  document.querySelector("#close-dialog").addEventListener("click", () => dialog.close());
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) dialog.close();
  });

  document.querySelector("#search").addEventListener("input", (event) => {
    const query = event.target.value.trim().toLowerCase();
    guide.topics.forEach((topic) => {
      const chapter = document.querySelector(`#${topic.id}`);
      const navLink = document.querySelector(`[data-nav="${topic.id}"]`);
      const text = `${chapter.dataset.title} ${topic.explanation.join(" ")} ${topic.bullets.join(" ")} ${topic.questions.join(" ")}`.toLowerCase();
      const visible = !query || text.includes(query);
      chapter.classList.toggle("hidden", !visible);
      navLink.classList.toggle("hidden", !visible);
    });
  });

  const sidebar = document.querySelector("#sidebar");
  document.querySelector("#menu-button").addEventListener("click", () => sidebar.classList.toggle("open"));
  nav.addEventListener("click", () => sidebar.classList.remove("open"));

  const observer = new IntersectionObserver((entries) => {
    const visible = entries
      .filter((entry) => entry.isIntersecting)
      .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
    if (!visible) return;
    document.querySelectorAll(".nav-link").forEach((link) =>
      link.classList.toggle("active", link.dataset.nav === visible.target.id)
    );
  }, { rootMargin: "-15% 0px -72%", threshold: [0, 0.1, 0.4] });
  document.querySelectorAll(".chapter").forEach((chapter) => observer.observe(chapter));

  updateProgress();
})();
