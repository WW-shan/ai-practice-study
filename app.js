const lessons = window.LESSONS || [];
let activeId = lessons.find((lesson) => lesson.status === "ready")?.id || lessons[0]?.id;
const completed = new Set(JSON.parse(localStorage.getItem("ai-review-progress") || "[]"));

const roadmapGrid = document.querySelector("#roadmapGrid");
const lessonList = document.querySelector("#lessonList");
const lessonCard = document.querySelector("#lessonCard");
const searchInput = document.querySelector("#lessonSearch");
const progressCount = document.querySelector("#progressCount");
const progressBar = document.querySelector("#progressBar");
const resetProgress = document.querySelector("#resetProgress");

function escapeHtml(value = "") {
  return String(value).replace(/[&<>"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[char]));
}

function saveProgress() {
  localStorage.setItem("ai-review-progress", JSON.stringify([...completed]));
}

function updateProgress() {
  const ready = lessons.filter((lesson) => lesson.status === "ready");
  const done = ready.filter((lesson) => completed.has(lesson.id)).length;
  progressCount.textContent = `${done} / ${ready.length}`;
  progressBar.style.width = ready.length ? `${(done / ready.length) * 100}%` : "0%";
}

function renderRoadmap() {
  roadmapGrid.innerHTML = lessons.map((lesson) => `
    <div class="roadmap-item ${lesson.status}" data-id="${lesson.id}">
      <span class="tag">${escapeHtml(lesson.chapter)} · ${escapeHtml(lesson.order)} · ${lesson.status === "ready" ? "已发布" : "待补"}</span>
      <h3>${escapeHtml(lesson.title)}</h3>
    </div>
  `).join("");
}

function renderLessonList() {
  const keyword = searchInput.value.trim().toLowerCase();
  const filtered = lessons.filter((lesson) => !keyword || `${lesson.title} ${lesson.subtitle} ${lesson.chapter}`.toLowerCase().includes(keyword));
  lessonList.innerHTML = filtered.map((lesson) => `
    <button class="lesson-pill ${lesson.id === activeId ? "active" : ""}" data-id="${lesson.id}" ${lesson.status !== "ready" ? "disabled" : ""} type="button">
      <small>${escapeHtml(lesson.chapter)} · 考点 ${escapeHtml(lesson.order)} · ${lesson.status === "ready" ? "可学习" : "待更新"}</small>
      ${escapeHtml(lesson.title)}
    </button>
  `).join("");
}

function renderReadyLesson(lesson) {
  const evidence = lesson.sourceEvidence.map((item) => `
    <div class="evidence">
      <code>${escapeHtml(item.ref)}</code>
      <p>${escapeHtml(item.quote)}</p>
    </div>
  `).join("");

  const learning = lesson.learning.map((section, index) => `
    <details ${index === 0 ? "open" : ""}>
      <summary>${escapeHtml(section.heading)}</summary>
      <div class="details-content">
        ${section.body.map((p) => `<p>${escapeHtml(p)}</p>`).join("")}
        <ul>${section.bullets.map((b) => `<li>${escapeHtml(b)}</li>`).join("")}</ul>
      </div>
    </details>
  `).join("");

  const pptDeepDive = (lesson.pptDeepDive || []).map((item) => `
    <div class="deep-card">
      <strong>${escapeHtml(item.title)}</strong>
      <ul>${(item.points || []).map((point) => `<li>${escapeHtml(point)}</li>`).join("")}</ul>
    </div>
  `).join("");

  const supplements = (lesson.supplementItems || []).map((item) => `
    <details>
      <summary>${escapeHtml(item.title)} <span class="source-mini">${escapeHtml(item.source || "")}</span></summary>
      <div class="details-content">
        ${(item.content || []).map((line) => `<p>${escapeHtml(line)}</p>`).join("")}
      </div>
    </details>
  `).join("");

  const imageSupplements = (lesson.imageSupplements || []).map((item) => `
    <figure class="image-supplement">
      <img src="${escapeHtml(item.src)}" alt="${escapeHtml(item.alt || item.title || "补充图")}" loading="lazy">
      <figcaption>${escapeHtml(item.title || item.alt || "")}</figcaption>
    </figure>
  `).join("");

  const exam = lesson.exam.map((item) => `
    <details>
      <summary>${escapeHtml(item.type)}：${escapeHtml(item.question)}</summary>
      <div class="details-content"><strong>答案：</strong>${escapeHtml(item.answer)}</div>
    </details>
  `).join("");

  const answers = lesson.answers.map((item) => `
    <div class="answer-card">
      <strong>${escapeHtml(item.title)}</strong>
      <p>${escapeHtml(item.text)}</p>
    </div>
  `).join("");

  const quiz = lesson.quiz.map((item, qIndex) => `
    <div class="quiz-item" data-correct="${item.correct}">
      <strong>${qIndex + 1}. ${escapeHtml(item.question)}</strong>
      <div class="quiz">
        ${item.options.map((option, index) => `<button type="button" data-index="${index}">${escapeHtml(option)}</button>`).join("")}
      </div>
      <p class="quiz-explain" hidden>${escapeHtml(item.explain)}</p>
    </div>
  `).join("");

  const practice = (lesson.practiceItems || []).map((item, index) => `
    <div class="practice-item">
      <p class="practice-source">${index + 1}. ${escapeHtml(item.source || "样例题")} · ${escapeHtml(item.type || "题目")}</p>
      <p class="practice-question">${escapeHtml(item.question)}</p>
      ${item.options && item.options.length ? `<ol class="option-list">${item.options.map((option) => `<li>${escapeHtml(option)}</li>`).join("")}</ol>` : `<p class="source-mini">原题提取文本未包含完整选项。</p>`}
      <details>
        <summary>查看答案、解析与归位原因</summary>
        <div class="details-content">
          <p><strong>答案：</strong>${escapeHtml(item.answer || "见解析")}</p>
          <p><strong>放在这里的原因：</strong>${escapeHtml(item.placementReason || "与本考点直接对应。")}</p>
          ${item.note ? `<p><strong>备注：</strong>${escapeHtml(item.note)}</p>` : ""}
        </div>
      </details>
    </div>
  `).join("");

  const review = lesson.review ? `
    <section class="block green">
      <h3>本考点自审</h3>
      <ul>
        <li>课件证据核对：${lesson.review.sourceChecked ? "通过" : "待补"}</li>
        <li>从零讲解完整：${lesson.review.teachesFromScratch ? "通过" : "待补"}</li>
        <li>考试考法对齐：${lesson.review.examAligned ? "通过" : "待补"}</li>
        <li>进入下一考点前 review：${lesson.review.selfReviewed ? "通过" : "待补"}</li>
      </ul>
      <p>${escapeHtml(lesson.review.reviewNote || "")}</p>
    </section>
  ` : "";

  lessonCard.innerHTML = `
    <header class="lesson-hero">
      <div class="lesson-meta">
        <span class="chip">${escapeHtml(lesson.chapter)}</span>
        <span class="chip">考点 ${escapeHtml(lesson.order)}</span>
        <span class="chip">课件核对版</span>
      </div>
      <h2 id="lesson-title">${escapeHtml(lesson.title)}</h2>
      <p>${escapeHtml(lesson.subtitle)}</p>
    </header>
    <div class="lesson-body">
      <section class="block gold">
        <h3>课件证据</h3>
        <div class="evidence-grid">${evidence}</div>
      </section>
      <section class="block green">
        <h3>课件到底想让你掌握什么</h3>
        <ol>${lesson.intent.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ol>
      </section>
      <section class="block">
        <h3>从零讲清楚</h3>
        <div class="lesson-sections">${learning}</div>
      </section>
      ${pptDeepDive ? `<section class="block green"><h3>PPT 严格补充</h3><div class="lesson-sections">${pptDeepDive}</div></section>` : ""}
      ${supplements ? `<section class="block"><h3>补充材料放置</h3><div class="lesson-sections">${supplements}</div></section>` : ""}
      ${imageSupplements ? `<section class="block gold"><h3>补充图片题</h3><div class="image-grid">${imageSupplements}</div></section>` : ""}
      <section class="block gold" id="exam-panel">
        <h3>考试怎么考</h3>
        <div class="lesson-sections">${exam}</div>
      </section>
      ${practice ? `<section class="block"><h3>老师/样例题放到这里</h3><div class="lesson-sections">${practice}</div></section>` : ""}
      <section class="block">
        <h3>易错点</h3>
        <ul>${lesson.traps.map((trap) => `<li>${escapeHtml(trap)}</li>`).join("")}</ul>
      </section>
      <section class="block green">
        <h3>标准答案模板</h3>
        <div class="lesson-sections">${answers}</div>
      </section>
      <section class="block gold">
        <h3>小自测</h3>
        <div class="lesson-sections">${quiz}</div>
      </section>
      ${review}
      <div class="progress-action">
        <button class="mark-btn" id="markDone" type="button">${completed.has(lesson.id) ? "已掌握，取消标记" : "标记为已掌握"}</button>
      </div>
    </div>
  `;
}

function renderLesson() {
  const lesson = lessons.find((item) => item.id === activeId) || lessons[0];
  if (!lesson || lesson.status !== "ready") {
    lessonCard.innerHTML = `<div class="lesson-body"><section class="block"><h3>这个考点还没写</h3><p>我会按顺序逐个核对课件后补上，不会一次性生成大段未经核对的内容。</p></section></div>`;
    return;
  }
  renderReadyLesson(lesson);
}

function renderAll() {
  renderRoadmap();
  renderLessonList();
  renderLesson();
  updateProgress();
}

lessonList.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-id]");
  if (!button || button.disabled) return;
  activeId = button.dataset.id;
  renderAll();
  document.querySelector("#lesson").scrollIntoView({ behavior: "smooth", block: "start" });
});

searchInput.addEventListener("input", renderLessonList);

lessonCard.addEventListener("click", (event) => {
  const quizButton = event.target.closest(".quiz button");
  if (quizButton) {
    const item = quizButton.closest(".quiz-item");
    const correct = Number(item.dataset.correct);
    item.querySelectorAll("button").forEach((button) => {
      const isCorrect = Number(button.dataset.index) === correct;
      button.classList.toggle("correct", isCorrect);
      button.classList.toggle("wrong", button === quizButton && !isCorrect);
    });
    item.querySelector(".quiz-explain").hidden = false;
  }

  if (event.target.id === "markDone") {
    if (completed.has(activeId)) completed.delete(activeId);
    else completed.add(activeId);
    saveProgress();
    renderAll();
  }
});

resetProgress.addEventListener("click", () => {
  completed.clear();
  saveProgress();
  renderAll();
});

renderAll();
