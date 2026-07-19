/* Shared result / history rendering for 知识测评 */
window.QuizReview = (function () {
  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function formatDuration(ms) {
    const totalSec = Math.max(0, Math.floor(ms / 1000));
    const m = Math.floor(totalSec / 60);
    const s = totalSec % 60;
    if (m > 0) return m + " 分 " + String(s).padStart(2, "0") + " 秒";
    return s + " 秒";
  }

  function formatDateTime(ts) {
    const d = new Date(ts);
    const pad = function (n) { return String(n).padStart(2, "0"); };
    return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate()) +
      " " + pad(d.getHours()) + ":" + pad(d.getMinutes());
  }

  function computeStats(exam, answers) {
    let correct = 0;
    let wrong = 0;
    let answered = 0;
    exam.questions.forEach(function (q) {
      const userKey = answers[q.number];
      if (!userKey) return;
      answered++;
      if (userKey === q.correctKey) correct++;
      else wrong++;
    });
    const unanswered = exam.questions.length - answered;
    const accuracy = answered ? Math.round((correct / answered) * 100) : 0;
    return { correct: correct, wrong: wrong, answered: answered, unanswered: unanswered, accuracy: accuracy };
  }

  function buildDetail(exam, answers) {
    return exam.questions.map(function (q) {
      const userKey = answers[q.number];
      if (!userKey) {
        return { q: q, userKey: null, isCorrect: null, unanswered: true };
      }
      const isCorrect = userKey === q.correctKey;
      return { q: q, userKey: userKey, isCorrect: isCorrect, unanswered: false };
    });
  }

  function renderOptions(q, item) {
    return q.options.map(function (o) {
      let ocls = "";
      if (!item.unanswered) {
        if (o.key === q.correctKey) ocls = " correct-opt";
        else if (o.key === item.userKey && !item.isCorrect) ocls = " wrong-opt";
      } else if (o.key === q.correctKey) {
        ocls = " correct-opt";
      }
      return (
        '<div class="option' + ocls + '">' +
        '<span class="option-key">' + o.key + ".</span>" +
        "<span>" + escapeHtml(o.text) + "</span></div>"
      );
    }).join("");
  }

  function renderQuestionBody(item, timesSnapshot) {
    const q = item.q;
    const userAns = item.userKey || "未答";
    const correctAns = q.correctKey || "—";
    const expl = q.explanation && q.explanation !== "暂无解析"
      ? escapeHtml(q.explanation)
      : escapeHtml("正确答案：" + correctAns);
    const ms = timesSnapshot && timesSnapshot[q.number] != null ? timesSnapshot[q.number] : 0;
    return (
      '<div class="snap-body">' +
      '<p class="snap-stem">' + escapeHtml(q.stem) + "</p>" +
      '<div class="options">' + renderOptions(q, item) + "</div>" +
      '<div class="explanation">' +
      "<h4>你的答案：" + userAns + " · 正确答案：" + correctAns +
      (ms ? " · 用时 " + formatDuration(ms) : "") + "</h4>" +
      expl + "</div></div>"
    );
  }

  function statusBadge(item) {
    if (item.unanswered) return '<span class="snap-badge unanswered">未答</span>';
    if (item.isCorrect) return '<span class="snap-badge correct">正确</span>';
    return '<span class="snap-badge wrong">错误</span>';
  }

  function buildResultBanner(stats, totalMs, opts) {
    opts = opts || {};
    const title = opts.title || "测评完成";
    const subtitle = opts.subtitle || (
      "本次共作答 " + stats.answered + " 题，正确 " + stats.correct + " 题" +
      (totalMs != null ? " · 总用时 " + formatDuration(totalMs) : "")
    );
    return (
      '<div class="result-banner">' +
      "<h2>" + escapeHtml(title) + "</h2>" +
      '<p class="result-sub">' + escapeHtml(subtitle) + "</p>" +
      '<div class="result-stats">' +
      '<div class="stat"><div class="stat-val good">' + stats.answered + '</div><div class="stat-label">已答</div></div>' +
      '<div class="stat"><div class="stat-val mid">' + stats.unanswered + '</div><div class="stat-label">未答</div></div>' +
      '<div class="stat"><div class="stat-val">' + stats.accuracy + '%</div><div class="stat-label">正确率</div></div>' +
      "</div>" +
      (opts.actionsHtml || "") +
      "</div>"
    );
  }

  function buildTimeAccordion(exam, answers, timesSnapshot) {
    const detail = buildDetail(exam, answers);
    const times = timesSnapshot || {};
    const sorted = detail.slice().sort(function (a, b) {
      return (times[b.q.number] || 0) - (times[a.q.number] || 0);
    });
    const maxMs = Math.max.apply(null, sorted.map(function (r) {
      return times[r.q.number] || 0;
    }).concat([1]));

    const rows = sorted.map(function (item, idx) {
      const num = item.q.number;
      const ms = times[num] || 0;
      const pct = Math.round((ms / maxMs) * 100);
      const slowCls = ms > 0 && idx < 5 ? " slow" : "";
      const stemPreview = escapeHtml(item.q.stem.length > 36
        ? item.q.stem.slice(0, 36) + "…"
        : item.q.stem);
      return (
        '<details class="time-acc' + slowCls + '">' +
        '<summary class="time-acc-head">' +
        '<span class="time-acc-num">' + num + "</span>" +
        statusBadge(item) +
        '<span class="time-acc-preview">' + stemPreview + "</span>" +
        '<span class="time-acc-bar-wrap"><span class="time-acc-bar" style="width:' + pct + '%"></span></span>' +
        '<span class="time-acc-val">' + formatDuration(ms) + "</span>" +
        '<span class="time-acc-chevron" aria-hidden="true">▾</span>' +
        "</summary>" +
        renderQuestionBody(item, times) +
        "</details>"
      );
    }).join("");

    return (
      '<section class="time-section">' +
      "<h3>答题快照</h3>" +
      "<p>按用时从高到低排列，点击展开查看题目、你的作答与解析。用时越久，通常越需要复习。</p>" +
      '<div class="time-list">' + rows + "</div></section>"
    );
  }

  function totalTime(timesSnapshot) {
    if (!timesSnapshot) return 0;
    return Object.keys(timesSnapshot).reduce(function (s, k) {
      return s + (timesSnapshot[k] || 0);
    }, 0);
  }

  function renderSnapshot(exam, record, opts) {
    opts = opts || {};
    const answers = record.answers || {};
    const times = record.questionTimes || {};
    const stats = {
      correct: record.correct != null ? record.correct : computeStats(exam, answers).correct,
      wrong: record.wrong != null ? record.wrong : computeStats(exam, answers).wrong,
      answered: record.answered != null ? record.answered : computeStats(exam, answers).answered,
      unanswered: record.unanswered != null ? record.unanswered : computeStats(exam, answers).unanswered,
      accuracy: record.accuracy != null ? record.accuracy : computeStats(exam, answers).accuracy,
    };
    const totalMs = QuizReview.totalTime(times);
    const subtitle = opts.subtitle || (
      formatDateTime(record.timestamp) + " · 共作答 " + stats.answered +
      " 题，正确 " + stats.correct + " 题 · 总用时 " + formatDuration(totalMs)
    );
    return (
      buildResultBanner(stats, totalMs, {
        title: opts.title || exam.title,
        subtitle: subtitle,
        actionsHtml: opts.actionsHtml || "",
      }) +
      buildTimeAccordion(exam, answers, times)
    );
  }

  return {
    escapeHtml: escapeHtml,
    formatDuration: formatDuration,
    formatDateTime: formatDateTime,
    computeStats: computeStats,
    buildResultBanner: buildResultBanner,
    buildTimeAccordion: buildTimeAccordion,
    renderSnapshot: renderSnapshot,
    totalTime: totalTime,
  };
})();
