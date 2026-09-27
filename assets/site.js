function sitePrefix() {
  const path = window.location.pathname.replace(/\/[^/]+\.html$/, "/");
  return path.endsWith("/") ? path : path + "/";
}

function $(id) {
  return document.getElementById(id);
}

async function loadText(rel) {
  const res = await fetch(sitePrefix() + rel);
  if (!res.ok) throw new Error("读不到 " + rel + "（" + res.status + "）");
  return res.text();
}

function parseCSV(text) {
  const rows = [];
  let row = [];
  let cell = "";
  let inQuotes = false;
  const src = text.replace(/^\uFEFF/, "");
  for (let i = 0; i < src.length; i++) {
    const ch = src[i];
    if (inQuotes) {
      if (ch === '"') {
        if (src[i + 1] === '"') { cell += '"'; i += 1; }
        else inQuotes = false;
      } else cell += ch;
    } else if (ch === '"') {
      inQuotes = true;
    } else if (ch === ",") {
      row.push(cell);
      cell = "";
    } else if (ch === "\n") {
      row.push(cell);
      rows.push(row);
      row = [];
      cell = "";
    } else if (ch !== "\r") {
      cell += ch;
    }
  }
  if (cell.length || row.length) {
    row.push(cell);
    rows.push(row);
  }
  const header = rows.shift();
  if (!header || !header[0]) return [];
  return rows.filter((item) => item.some((value) => value !== "")).map((item) => {
    const obj = {};
    header.forEach((key, index) => { obj[key] = item[index] ?? ""; });
    return obj;
  });
}

function num(value) {
  if (value == null || value === "") return null;
  const n = Number(value);
  return Number.isFinite(n) ? n : null;
}

function fmt(n, digits) {
  if (n == null) return "—";
  return n.toLocaleString("en-US", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}

function fmtSigned(n, digits) {
  if (n == null) return "—";
  const body = fmt(Math.abs(n), digits);
  if (n > 0) return "+" + body;
  if (n < 0) return "−" + body;
  return body;
}

function el(tag, cls, text) {
  const node = document.createElement(tag);
  if (cls) node.className = cls;
  if (text != null) node.textContent = text;
  return node;
}

function addChart(parent, spec) {
  const card = el("article", "chart-card" + (spec.full ? " full" : ""));
  card.appendChild(el("h3", null, spec.title));
  card.appendChild(el("p", "sub", spec.sub));
  const box = el("div", "chart-box");
  const canvas = document.createElement("canvas");
  canvas.setAttribute("role", "img");
  canvas.setAttribute("aria-label", spec.title);
  box.appendChild(canvas);
  card.appendChild(box);
  parent.appendChild(card);
  if (!window.Chart) return null;
  const digits = spec.digits;
  const format = (value) => fmt(Number(value), digits);
  return new Chart(canvas, {
    type: "line",
    data: {
      labels: spec.labels,
      datasets: spec.datasets.map((ds) => ({
        label: ds.label,
        data: ds.data,
        borderColor: ds.color,
        backgroundColor: ds.fill || "transparent",
        borderWidth: 1.8,
        pointRadius: spec.labels.length < 4 ? 3 : 0,
        pointHitRadius: 10,
        tension: 0,
        spanGaps: false,
        fill: Boolean(ds.fill),
      })),
    },
    options: {
      animation: false,
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: {
          display: spec.datasets.length > 1,
          labels: { boxWidth: 10, boxHeight: 10, usePointStyle: true },
        },
        tooltip: {
          callbacks: {
            label(ctx) {
              const value = ctx.parsed.y;
              if (value == null) return ctx.dataset.label;
              return ctx.dataset.label + "  " + format(value);
            },
          },
        },
      },
      scales: {
        x: {
          ticks: { maxTicksLimit: 6, maxRotation: 0, autoSkip: true },
          grid: { display: false },
        },
        y: {
          ticks: { maxTicksLimit: 5, callback: (value) => format(value) },
          grid: { color: "rgba(28, 25, 22, 0.08)" },
        },
      },
    },
  });
}

function renderBriefing(page) {
  const box = document.getElementById("briefing");
  if (!box) return Promise.resolve();
  return loadText("data/briefing.json").then((text) => {
    const data = JSON.parse(text);
    const lines = (data.pages && data.pages[page]) || ["今日无变动"];
    box.hidden = false;
    box.textContent = "";
    box.appendChild(el("p", "label", "今日小结"));
    const list = el("ul", "brief-list");
    lines.forEach((line) => {
      const item = document.createElement("li");
      item.textContent = line;
      list.appendChild(item);
    });
    box.appendChild(list);
  }).catch(() => {
    box.hidden = true;
  });
}

if (window.Chart) {
  Chart.defaults.font.family = '"Noto Sans SC", "Noto Sans CJK SC", "PingFang SC", "Microsoft YaHei", "WenQuanYi Micro Hei", sans-serif';
  Chart.defaults.color = "#6d655c";
  Chart.defaults.font.size = 12;
}
