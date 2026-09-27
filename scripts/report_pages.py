#!/usr/bin/env python3
"""把 inbox/reports 里的 Obsidian 笔记渲染成静态阅读页。"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import markdown

KINDS = ("日报", "宏观周报", "产业周报")
KIND_ORDER = {name: index for index, name in enumerate(KINDS)}
DAILY_SUBTYPE = {"市场观点汇总": 0, "主题跟踪": 1}
CALLOUT_LABEL = {
    "note": "注",
    "info": "说明",
    "tip": "提示",
    "warning": "注意",
    "caution": "注意",
    "abstract": "摘要",
    "summary": "摘要",
    "quote": "引用",
    "example": "例子",
    "danger": "危险",
    "bug": "问题",
    "success": "完成",
    "failure": "失败",
    "question": "问题",
}
EMBED_RE = re.compile(r"!\[\[([^\[\]|#]+)(?:#[^\[\]|]*)?(?:\|([^\[\]]+))?\]\]")
WIKI_RE = re.compile(r"\[\[([^\[\]|#]+)(?:#[^\[\]|]*)?(?:\|([^\[\]]+))?\]\]")
COLOR_SPAN_RE = re.compile(
    r"<span\b([^>]*)>((?:(?!</?span\b).)*)</span>",
    re.IGNORECASE | re.DOTALL,
)
FENCE_RE = re.compile(r"```.*?```|`[^`\n]+`", re.DOTALL)
CALLOUT_HEAD_RE = re.compile(r"^\[!([A-Za-z0-9_-]+)\][+-]?\s*(.*)$")
HEADING_RE = re.compile(r"<h([23])>(.*?)</h\1>", re.DOTALL)
ISO_WEEK_RE = re.compile(r"(\d{4})-W(\d{2})", re.IGNORECASE)
DAY_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")


@dataclass
class Report:
    kind: str
    stem: str
    title: str
    date_label: str
    sort_date: date
    subtype: int
    slug: str
    source: str
    body_md: str
    body_html: str = ""
    outline: list[tuple[int, str, str]] = field(default_factory=list)

    @property
    def href(self) -> str:
        return self.slug + ".html"


def norm_key(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).casefold()


def slugify(stem: str) -> str:
    text = stem.strip()
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"[/\\#?%&]+", "-", text)
    text = text.strip("-")
    return text or "report"


def split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    end = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end = index
            break
    if end is None:
        return {}, text
    meta: dict[str, str] = {}
    for line in lines[1:end]:
        if ":" not in line or line.startswith((" ", "\t", "-")):
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip().strip("\"'")
    body = "\n".join(lines[end + 1 :]).lstrip("\n")
    return meta, body


def display_title(stem: str, meta: dict[str, str]) -> str:
    if meta.get("title"):
        return meta["title"].strip()
    return stem.strip() or stem


def parse_when(stem: str, meta: dict[str, str]) -> tuple[date, str]:
    raw = (meta.get("date") or "").strip()
    day = DAY_RE.search(raw)
    if day:
        found = date.fromisoformat(day.group(1))
        return found, found.isoformat()
    week = ISO_WEEK_RE.search(raw)
    if week:
        year, number = int(week.group(1)), int(week.group(2))
        monday = date.fromisocalendar(year, number, 1)
        return monday, f"{year}-W{number:02d}"
    day = DAY_RE.search(stem)
    if day:
        found = date.fromisoformat(day.group(1))
        return found, found.isoformat()
    week = ISO_WEEK_RE.search(stem)
    if week:
        year, number = int(week.group(1)), int(week.group(2))
        monday = date.fromisocalendar(year, number, 1)
        return monday, f"{year}-W{number:02d}"
    return date.min, ""


def load_reports(root: Path) -> list[Report]:
    if not root.exists():
        return []
    found: list[Report] = []
    used_slugs: dict[str, int] = {}
    for kind in KINDS:
        folder = root / kind
        if not folder.is_dir():
            continue
        for path in sorted(folder.glob("*.md")):
            if path.name.startswith("._"):
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            meta, body = split_frontmatter(text)
            stem = path.stem
            title = display_title(stem, meta)
            sort_date, date_label = parse_when(stem, meta)
            suffix = DAY_RE.sub("", stem)
            suffix = ISO_WEEK_RE.sub("", suffix).strip(" _-")
            subtype = DAILY_SUBTYPE.get(suffix, DAILY_SUBTYPE.get(title, 9))
            if kind != "日报":
                subtype = 0
            base = slugify(stem)
            count = used_slugs.get(base, 0)
            used_slugs[base] = count + 1
            slug = base if count == 0 else f"{base}-{count + 1}"
            found.append(
                Report(
                    kind=kind,
                    stem=stem,
                    title=title,
                    date_label=date_label,
                    sort_date=sort_date,
                    subtype=subtype,
                    slug=slug,
                    source=str(path),
                    body_md=body,
                )
            )
    return found


def reading_order(reports: list[Report]) -> list[Report]:
    return sorted(
        reports,
        key=lambda item: (KIND_ORDER.get(item.kind, 9), -item.sort_date.toordinal(), item.subtype, item.title),
    )


def latest_daily(reports: list[Report]) -> Report | None:
    dailies = [item for item in reading_order(reports) if item.kind == "日报"]
    if dailies:
        return dailies[0]
    ordered = reading_order(reports)
    return ordered[0] if ordered else None


def link_index(reports: list[Report]) -> dict[str, Report]:
    buckets: dict[str, list[Report]] = {}

    def add(key: str, report: Report) -> None:
        cleaned = key.strip()
        if not cleaned:
            return
        buckets.setdefault(norm_key(cleaned), []).append(report)

    for report in reports:
        add(report.stem, report)
        add(report.title, report)
        add(report.slug, report)
        add(report.stem.replace("_", " "), report)
    exact: dict[str, Report] = {}
    for key, group in buckets.items():
        unique = {id(item): item for item in group}
        if len(unique) == 1:
            exact[key] = next(iter(unique.values()))
    return exact


def lookup_report(target: str, index: dict[str, Report]) -> Report | None:
    raw = target.strip()
    raw = re.sub(r"\.md$", "", raw, flags=re.IGNORECASE)
    raw = raw.split("#", 1)[0].strip()
    options = [raw, raw.replace("\\", "/").split("/")[-1]]
    for option in options:
        hit = index.get(norm_key(option))
        if hit:
            return hit
    return None


def unwrap_color_spans(text: str) -> str:
    def style_has_color(attrs: str) -> bool:
        match = re.search(
            r"""style\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'>]+))""",
            attrs,
            flags=re.IGNORECASE,
        )
        if not match:
            return False
        style = next(group for group in match.groups() if group)
        return "color" in style.lower()

    previous = None
    while previous != text:
        previous = text

        def replace(match: re.Match[str]) -> str:
            if style_has_color(match.group(1)):
                return match.group(2)
            return match.group(0)

        text = COLOR_SPAN_RE.sub(replace, text)
    return text


def protect_code(text: str) -> tuple[str, list[str]]:
    slots: list[str] = []

    def replace(match: re.Match[str]) -> str:
        slots.append(match.group(0))
        return f"\x00CODE{len(slots) - 1}\x00"

    return FENCE_RE.sub(replace, text), slots


def restore_code(text: str, slots: list[str]) -> str:
    for index, chunk in enumerate(slots):
        text = text.replace(f"\x00CODE{index}\x00", chunk)
    return text


def extract_callouts(text: str) -> tuple[str, list[tuple[str, str, str]]]:
    lines = text.split("\n")
    output: list[str] = []
    callouts: list[tuple[str, str, str]] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.startswith(">"):
            output.append(line)
            index += 1
            continue
        block: list[str] = []
        while index < len(lines):
            current = lines[index]
            if current.startswith(">"):
                block.append(current)
                index += 1
                continue
            if current.strip() == "" and index + 1 < len(lines) and lines[index + 1].startswith(">"):
                block.append(current)
                index += 1
                continue
            break
        first = re.sub(r"^>\s?", "", block[0]).strip()
        match = CALLOUT_HEAD_RE.match(first)
        if not match:
            output.extend(block)
            continue
        kind = match.group(1).lower()
        title = match.group(2).strip()
        inner_lines: list[str] = []
        for raw in block[1:]:
            if raw.startswith(">"):
                raw = raw[1:]
                if raw.startswith(" "):
                    raw = raw[1:]
            inner_lines.append(raw)
        callouts.append((kind, title, "\n".join(inner_lines).strip("\n")))
        output.append(f"%%CALLOUT{len(callouts) - 1}%%")
    return "\n".join(output), callouts


def apply_obsidian(text: str, index: dict[str, Report]) -> str:
    def embed(match: re.Match[str]) -> str:
        target = match.group(1).strip()
        alias = (match.group(2) or "").strip()
        label = alias or target.replace("\\", "/").split("/")[-1]
        return label

    def wiki(match: re.Match[str]) -> str:
        target = match.group(1).strip()
        alias = (match.group(2) or "").strip()
        label = alias or target.replace("\\", "/").split("/")[-1]
        report = lookup_report(target, index)
        if report is None:
            return label
        safe = label.replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")
        return f"[{safe}]({report.href})"

    text = EMBED_RE.sub(embed, text)
    return WIKI_RE.sub(wiki, text)


def escape_raw_html(text: str) -> str:
    """只转义会变成标签的字符，保留 Markdown 的 > 引用。"""
    return text.replace("&", "&amp;").replace("<", "&lt;")


def loosen_tables(text: str) -> str:
    """Obsidian 表格常常紧贴上一段。Python-Markdown 需要空行才认表格。"""
    lines = text.split("\n")

    def is_row(line: str) -> bool:
        stripped = line.strip()
        return stripped.startswith("|") and stripped.endswith("|") and stripped.count("|") >= 2

    output: list[str] = []
    index = 0
    while index < len(lines):
        if is_row(lines[index]) and not (output and is_row(output[-1])):
            if output and output[-1].strip() != "":
                output.append("")
            while index < len(lines) and is_row(lines[index]):
                output.append(lines[index])
                index += 1
            if index < len(lines) and lines[index].strip() != "":
                output.append("")
            continue
        output.append(lines[index])
        index += 1
    return "\n".join(output)


def render_markdown(text: str, index: dict[str, Report]) -> str:
    protected, slots = protect_code(text)
    protected = unwrap_color_spans(protected)
    protected, callouts = extract_callouts(protected)
    protected = escape_raw_html(protected)
    protected = apply_obsidian(protected, index)
    protected = loosen_tables(protected)
    protected = restore_code(protected, slots)
    rendered = markdown.markdown(
        protected,
        extensions=["tables", "fenced_code", "sane_lists"],
        output_format="html",
    )
    for number, (kind, title, inner) in enumerate(callouts):
        inner_html = render_markdown(inner, index) if inner.strip() else ""
        label = html.escape(title or CALLOUT_LABEL.get(kind, kind))
        safe_kind = re.sub(r"[^a-z0-9_-]", "", kind) or "note"
        block = (
            f'<div class="callout callout-{safe_kind}">'
            f'<p class="callout-title">{label}</p>{inner_html}</div>'
        )
        rendered = re.sub(rf"<p>\s*%%CALLOUT{number}%%\s*</p>", block, rendered)
        rendered = rendered.replace(f"%%CALLOUT{number}%%", block)
    return wrap_tables(rendered)


def annotate_headings(source: str) -> tuple[str, list[tuple[int, str, str]]]:
    outline: list[tuple[int, str, str]] = []

    def replace(match: re.Match[str]) -> str:
        level = int(match.group(1))
        inner = match.group(2)
        text = re.sub(r"<[^>]+>", "", inner)
        text = html.unescape(text).strip()
        heading_id = f"s{len(outline) + 1}"
        outline.append((level, heading_id, text))
        return f'<h{level} id="{heading_id}">{inner}</h{level}>'

    return HEADING_RE.sub(replace, source), outline


def wrap_tables(source: str) -> str:
    return source.replace("<table>", '<div class="table-scroll"><table class="report-table">').replace(
        "</table>", "</table></div>"
    )


def render_bodies(reports: list[Report]) -> None:
    index = link_index(reports)
    for report in reports:
        body = report.body_md
        first = body.lstrip("\n").splitlines()[:1]
        if first and first[0].strip() in {f"# {report.title}", f"# {report.stem}"}:
            body = "\n".join(body.lstrip("\n").splitlines()[1:]).lstrip("\n")
        html_body = render_markdown(body, index)
        html_body, outline = annotate_headings(html_body)
        report.body_html = html_body
        report.outline = outline


def sidebar_label(item: Report, grouped: bool) -> str:
    title = item.title
    if item.date_label and title.startswith(item.date_label):
        title = title[len(item.date_label) :].strip(" -_") or item.title
    if grouped:
        return title
    if item.date_label and not item.title.startswith(item.date_label):
        return f"{item.date_label} {title}"
    return item.title


def sidebar_html(reports: list[Report], current: Report | None) -> str:
    ordered = reading_order(reports)
    parts: list[str] = []
    for kind in KINDS:
        items = [item for item in ordered if item.kind == kind]
        parts.append(f"<h2>{html.escape(kind)}</h2>")
        if not items:
            parts.append('<p class="toc-date">还没有</p>')
            continue
        if kind == "日报":
            by_label: list[tuple[str, list[Report]]] = []
            for item in items:
                if not by_label or by_label[-1][0] != item.date_label:
                    by_label.append((item.date_label, []))
                by_label[-1][1].append(item)
            for label, group in by_label:
                parts.append('<div class="toc-day">')
                parts.append(f'<p class="toc-date">{html.escape(label or "未标日期")}</p>')
                for item in group:
                    current_attr = ' aria-current="page"' if current is not None and item.slug == current.slug else ""
                    parts.append(
                        f'<a href="{html.escape(item.href)}"{current_attr}>{html.escape(sidebar_label(item, grouped=True))}</a>'
                    )
                parts.append("</div>")
        else:
            for item in items:
                current_attr = ' aria-current="page"' if current is not None and item.slug == current.slug else ""
                parts.append(
                    f'<a href="{html.escape(item.href)}"{current_attr}>{html.escape(sidebar_label(item, grouped=False))}</a>'
                )
    return "\n".join(parts)


def outline_html(outline: list[tuple[int, str, str]]) -> str:
    if not outline:
        return ""
    links = ['<p class="label">本篇</p>']
    for level, heading_id, text in outline:
        css = "lv3" if level == 3 else "lv2"
        links.append(
            f'<a class="{css}" href="#{html.escape(heading_id)}">{html.escape(text)}</a>'
        )
    return '<nav class="outline" aria-label="本篇目录">' + "\n".join(links) + "</nav>"


def pager_html(reports: list[Report], current: Report) -> str:
    ordered = reading_order(reports)
    index = next(position for position, item in enumerate(ordered) if item.slug == current.slug)
    chunks = ['<nav class="pager">']
    if index > 0:
        previous = ordered[index - 1]
        chunks.append(
            f'<a class="prev" href="{html.escape(previous.href)}">上一篇<span>{html.escape(previous.title)}</span></a>'
        )
    else:
        chunks.append("<span></span>")
    if index + 1 < len(ordered):
        nxt = ordered[index + 1]
        chunks.append(
            f'<a class="next" href="{html.escape(nxt.href)}">下一篇<span>{html.escape(nxt.title)}</span></a>'
        )
    chunks.append("</nav>")
    return "\n".join(chunks)


NAV = """<nav class="nav" aria-label="页面">
      <a href="../index.html">流动性</a>
      <a href="../sentiment.html">市场情绪</a>
      <a href="../semis.html">半导体景气</a>
      <a href="../earnings.html">盈利跟踪</a>
      <a href="index.html" aria-current="page">研报</a>
    </nav>"""


def page_html(reports: list[Report], current: Report | None) -> str:
    side = sidebar_html(reports, current)
    if current is None:
        sheet = """<article class="sheet">
      <header>
        <p class="kicker">研报</p>
        <h1>还没有研报</h1>
        <p class="lede">服务器把笔记推进 inbox/reports/ 之后，这里会列出日报和周报。</p>
      </header>
    </article>"""
        outline = ""
        title = "研报"
        css = "reader no-outline"
    else:
        meta_bits = [current.kind]
        if current.date_label:
            meta_bits.append(current.date_label)
        outline = outline_html(current.outline)
        css = "reader" if outline else "reader no-outline"
        sheet = f"""<article class="sheet">
      <header>
        <p class="kicker">{html.escape(" · ".join(meta_bits))}</p>
        <h1>{html.escape(current.title)}</h1>
      </header>
      <div class="prose">{current.body_html}</div>
      {pager_html(reports, current)}
    </article>"""
        title = f"{current.title} · 研报"
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex">
  <title>{html.escape(title)}</title>
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Crect width='16' height='16' rx='3' fill='%231a4d45'/%3E%3C/svg%3E">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../assets/site.css">
</head>
<body>
  <div class="reader-wrap">
    {NAV}
    <div class="{css}">
      <details class="toc-drawer">
        <summary>目录</summary>
        <div class="toc-inner">{side}</div>
      </details>
      <aside class="toc-side" aria-label="研报目录">{side}</aside>
      {sheet}
      {outline}
    </div>
  </div>
</body>
</html>
"""


def write_report_site(reports: list[Report], dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    render_bodies(reports)
    landing = latest_daily(reports)
    for report in reports:
        (dest / report.href).write_text(page_html(reports, report), encoding="utf-8")
    (dest / "index.html").write_text(page_html(reports, landing), encoding="utf-8")
