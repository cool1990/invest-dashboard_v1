# 宏观看板

这个仓库保存自己看的宏观数据，并用静态网页展示。页面是简体中文。现在有五页：

- [流动性](https://cool1990.github.io/macro-dashboard/)
- [市场情绪](https://cool1990.github.io/macro-dashboard/sentiment.html)
- [半导体景气](https://cool1990.github.io/macro-dashboard/semis.html)
- [盈利跟踪](https://cool1990.github.io/macro-dashboard/earnings.html)
- [研报](https://cool1990.github.io/macro-dashboard/reports/)

网页地址：https://cool1990.github.io/macro-dashboard/

流动性来自圣路易斯联储 FRED 的公开 CSV，不需要密钥。情绪、半导体、盈利来自每天早晨的笔记，笔记由自己的服务器推到 `inbox/notes/`。研报是自己的 Obsidian 笔记，推到 `inbox/reports/`。

站点用一条命令构建到 `dist/`，页面之间用相对路径，不写死 `/macro-dashboard/`。每页都有 `<meta name="robots" content="noindex">`，`dist/robots.txt` 禁止抓取。准备改成私有仓库、放到 Cloudflare Pages 后面用 Access 时，按下面的构建说明即可。在那之前，GitHub Pages 仍会发布 `dist/`。

## 文件夹

- `data/series/`：流动性原始序列，从 2022-01-01 起，列是 `date,value`，数值是 FRED 原文。百万美元和十亿美元看 `meta.json` 里的 `unit`。
- `data/derived/`：周三派生表。金额单位是十亿美元。
- `data/sentiment/`：市场情绪时间序列和综合评价。
- `data/earnings/`：观察名单每日一行，以及笔记里写明的未来财报。
- `data/semis/`：存储价格、GPU 租金、OpenRouter 用量、SiliconData 指数、韩国芯片出口。
- `data/meta.json`：名称、单位、来源、各块数据的起止日期。
- `data/notes_skipped.csv`：单元格写了「未更新」或「抓取失败」、因而没有当成数字的记录。
- `inbox/notes/`：服务器推上来的原始 Markdown。网页不直接读这里。
- `inbox/reports/`：研报原文。构建时渲染进 `dist/reports/`，不另存一份 HTML 进 git。
- `ingest/parse_notes.py`：把指标笔记整理进 `data/`。只用 Python 标准库。
- `scripts/fetch_liquidity.py`：拉取 FRED。
- `scripts/build_site.py`：构建整个站点到 `dist/`。
- `index.html`、`sentiment.html`、`semis.html`、`earnings.html`：四个数据页的源文件。研报页由构建生成。
- `.github/workflows/fetch-data.yml`：每天 22:00 UTC 更新流动性，有变化时提交 `data/` 并发布网页。
- `.github/workflows/ingest-notes.yml`：`inbox/notes/` 或 `inbox/reports/` 有推送时整理数据、在需要时提交，并发布网页。
- `.github/workflows/pages.yml`：发布 GitHub Pages。源文件或数据有变动时构建 `dist/` 再发布。

用 `GITHUB_TOKEN` 推上去的提交不会再触发别的工作流。所以「更新数据」和「收录笔记」在提交之后，会检出这个新提交，自己再跑一遍发布，而不是干等「发布网页」被触发。直接改网页或合并到 `main` 时，仍由「发布网页」发布。

## 本地查看

```bash
pip install -r requirements.txt
python3 scripts/build_site.py
python3 -m http.server 8000 -d dist
```

浏览器打开 http://localhost:8000/ 。Python 3.12。不要直接双击 html，浏览器不允许页面那样读取旁边的数据文件。

## Cloudflare Pages

仓库改成私有、改由 Cloudflare Pages 托管时：

| 项 | 值 |
| --- | --- |
| 构建命令 | `pip install -r requirements.txt && python scripts/build_site.py` |
| 输出目录 | `dist` |
| 根目录 | 仓库根目录 |
| Python | 3.12，环境变量 `PYTHON_VERSION` = `3.12` |

构建产物里的链接都是相对路径，站点挂在域名根上即可。Access 放在这个站点前面。GitHub Pages 的工作流先留着，切换完成后再停。

## 笔记怎么推进来

服务器每天早晨把新笔记提交到 `main` 的 `inbox/notes/`。目录和文件名按下面放，解析脚本靠文件名判断种类，日期优先用文首的 `data_date`，没有就用文件名里的 `YYYY-MM-DD`。

```
inbox/notes/每日/宏观指标_YYYY-MM-DD.md
inbox/notes/每日/盈利跟踪_YYYY-MM-DD.md
inbox/notes/每日/美港股盈利跟踪_YYYY-MM-DD.md
inbox/notes/半导体/YYYY-MM-DD_半导体-存储价格.md
inbox/notes/半导体/YYYY-MM-DD_半导体-GPU租赁价格.md
inbox/notes/半导体/YYYY-MM-DD_半导体-OpenRouter平台token.md
inbox/notes/半导体/YYYY-MM-DD_半导体-SiliconData-LLMToken.md
inbox/notes/半导体/YYYY-MM-DD_半导体-韩国出口.md
```

笔记是带 YAML 头的 Markdown，正文里是表格。同一天再推一次会按主键覆盖，不会多出一行。单元格如果就是「未更新」或「抓取失败」，不当成数字；备注里写明沿用最近价格、格子里仍有数字的，会保留数字并标成沿用。缺列、多列都可以，认不出的列会跳过。

推送用仓库的 **Deploy key**，并且要勾选 **Allow write access**。GitHub 的 deploy key 不能限制只写某一个目录，所以这把钥匙只给这台服务器用，服务器只提交 `inbox/notes/` 里的文件。

设置步骤：

1. 在服务器上生成一把专用 SSH 密钥，不要复用别的钥匙。
2. 打开仓库 **Settings → Deploy keys → Add deploy key**。
3. 贴上公钥，勾选 **Allow write access**，保存。
4. 服务器用这把私钥 `git push origin main`。`main` 需要允许这把钥匙直接推送；如果开了分支保护、禁止直接推送，这次推送会被拒绝。

推上去之后，「收录笔记」工作流会跑。也可以在 Actions 里手动运行它。

## 研报怎么推进来

服务器把 Obsidian 笔记推到 `main` 的 `inbox/reports/`。文件名用来识别种类，日期优先用文首的 `date`，标题优先用 `title`，没有就从文件名取。

```
inbox/reports/日报/YYYY-MM-DD_市场观点汇总.md
inbox/reports/日报/YYYY-MM-DD_主题跟踪.md
inbox/reports/宏观周报/2026-W39 宏观周报.md
inbox/reports/宏观周报/YYYY-MM-DD 美国宏观流动性周报.md
inbox/reports/产业周报/2026-W39 产业周报.md
```

每天的日报在目录里按日期放在一起，新的在前。打开「研报」先看到最新一篇日报。每篇有自己的地址，在 `dist/reports/` 下，文件名来自笔记文件名。`[[笔记名]]` 如果对得上已发布的一篇，就变成站内链接，否则只留下文字。`![[...]]` 只留下文字。带颜色的 `<span>` 会去掉，留下里面的字。

推送用同一把可以写仓库的 Deploy key，服务器只提交 `inbox/reports/` 里的文件。「收录笔记」看到 `inbox/reports/**` 有变化就会重新构建并发布，即使指标数据没有改动。

## 流动性

净流动性使用市场常用算法，不是官方指标：

美联储总资产（WALCL）− 财政部账户周三水平（WDTGAL）− 隔夜逆回购（RRPONTSYD）

FRED 里 WALCL、WDTGAL、准备金（WRBWFRBL）的单位是百万美元，写入周度文件时除以 1000。隔夜逆回购本身就是十亿美元。

周变动是与上一条周三观测相比的差额。SOFR−IORB 和 EFFR−IORB 的单位是基点。准备金分位是 2022-01-01 起、到该周三为止的周三观测中，准备金不高于当前值的占比，不是准备金短缺的度量。

「更新数据」每天 22:00 UTC 跑一次，也可以手动运行。每条序列单独下载。成功就覆盖 `data/series/<id>.csv`；失败就把原来的文件放进这一次的暂存目录，一起留下。`publish()` 只替换 `data/series` 和 `data/derived`，再合并 `data/meta.json` 里的流动性字段。情绪、盈利、半导体和 `notes_skipped.csv` 不会被这次发布删掉。每条写下 `last_fetch_ok`、`last_obs_date`（文件里最后一个日期，没有旧文件则为 null）和 `fetched_at`。失败时 `last_fetch_ok` 为 false，成功为 true。周报读 CSV 时看这三项，就能判断这条是不是刚拉到的。整理笔记时反过来：只更新情绪、盈利、半导体和 `notes_asof`，流动性字段原样保留。工作流仍会把这次的 `data/` 提交上去，所以新鲜度标记不会丢。不要给 FRED 请求加自定义 User-Agent：自定义 UA 在 HTTP/2 上会立刻报错，在 HTTP/1.1 上会挂起；Python 默认请求头可以下载。

周三表和每日利差只在 WALCL、WDTGAL、RRPONTSYD、WRBWFRBL、SOFR、IORB、EFFR 这次都成功时重算。否则 `data/derived/` 保持原文件，`derived_refresh.ok` 为 false，并写明是哪几条没刷新。

旧版金融压力指数 STLFSI 若在 2022-01-01 之后没有观测，就视为已停更：不写 CSV，`status` 为 `discontinued`，`last_obs_date` 是 FRED 上的最后观测日。目前这条停在 2020-03-13。

周报会用到、并已放进 `data/series/` 的序列，除了原来的 WALCL、WDTGAL、RRPONTSYD、WRBWFRBL、SOFR、IORB、EFFR、NFCI、BAMLH0A0HYM2、VIXCLS，还有：ANFCI、STLFSI4、WRESBAL、WTREGEN、WLRRAOL、WCURCIR、SOFR1、SOFR25、SOFR75、SOFR99、SOFRVOL、TOTBKCR、TOTCI、TLAACBW027SBOG、CCLACBW027SBOG、CREACBW027SBOG、DPSACBW027SBOG、DPSLCBW027SBOG。中文名和单位在 `meta.json`。

要加一条 FRED 序列：编辑 `scripts/fetch_liquidity.py` 的 `SERIES`，百万美元用 `to_bn = Decimal("0.001")`，已经是十亿美元的用 `Decimal("1")`，利率和指数用 `None`，然后运行 `python3 scripts/fetch_liquidity.py`。要显示在流动性页上，再改 `index.html`。

## 另外三页的历史有多长

情绪、盈利、半导体目前只有 2026 年 9 月中下旬的笔记，页面会写明起始日期和点数，不会把短历史画成一条很长的线。
