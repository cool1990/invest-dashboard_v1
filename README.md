# 宏观看板

这个仓库保存自己看的宏观数据，并用静态网页展示。页面是简体中文。现在有四页：

- [流动性](https://cool1990.github.io/macro-dashboard/)
- [市场情绪](https://cool1990.github.io/macro-dashboard/sentiment.html)
- [半导体景气](https://cool1990.github.io/macro-dashboard/semis.html)
- [盈利跟踪](https://cool1990.github.io/macro-dashboard/earnings.html)

网页地址：https://cool1990.github.io/macro-dashboard/

流动性来自圣路易斯联储 FRED 的公开 CSV，不需要密钥。另外三页来自每天早晨的笔记，笔记由自己的服务器推到 `inbox/notes/`。

## 文件夹

- `data/series/`、`data/derived/`：流动性原始序列和周三派生表。金额单位是十亿美元。
- `data/sentiment/`：市场情绪时间序列和综合评价。
- `data/earnings/`：观察名单每日一行，以及笔记里写明的未来财报。
- `data/semis/`：存储价格、GPU 租金、OpenRouter 用量、SiliconData 指数、韩国芯片出口。
- `data/meta.json`：名称、单位、来源、各块数据的起止日期。
- `data/notes_skipped.csv`：单元格写了「未更新」或「抓取失败」、因而没有当成数字的记录。
- `inbox/notes/`：服务器推上来的原始 Markdown。网页不直接读这里。
- `ingest/parse_notes.py`：把笔记整理进 `data/`。只用 Python 标准库。
- `scripts/fetch_liquidity.py`：拉取 FRED。
- `index.html`、`sentiment.html`、`semis.html`、`earnings.html`：四个页面。图表库从 CDN 加载，没有构建步骤。
- `.github/workflows/fetch-data.yml`：每天 22:00 UTC 更新流动性，有变化时提交 `data/` 并发布网页。
- `.github/workflows/ingest-notes.yml`：`inbox/notes/` 有推送时整理数据、提交，并发布网页。
- `.github/workflows/pages.yml`：发布 GitHub Pages。可以被上面两个工作流调用。

用 `GITHUB_TOKEN` 推上去的提交不会再触发别的工作流。所以「更新数据」和「收录笔记」在提交之后，会检出这个新提交，自己再跑一遍发布，而不是干等「发布网页」被触发。直接改网页或合并到 `main` 时，仍由「发布网页」发布。

## 本地查看

```bash
python3 -m http.server 8000
```

浏览器打开 http://localhost:8000/ 。不要直接双击 html，浏览器不允许页面那样读取旁边的数据文件。

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

## 流动性

净流动性使用市场常用算法，不是官方指标：

美联储总资产（WALCL）− 财政部账户周三水平（WDTGAL）− 隔夜逆回购（RRPONTSYD）

FRED 里 WALCL、WDTGAL、准备金（WRBWFRBL）的单位是百万美元，写入周度文件时除以 1000。隔夜逆回购本身就是十亿美元。

周变动是与上一条周三观测相比的差额。SOFR−IORB 和 EFFR−IORB 的单位是基点。准备金分位是 2022-01-01 起、到该周三为止的周三观测中，准备金不高于当前值的占比，不是准备金短缺的度量。

「更新数据」每天 22:00 UTC 跑一次。某一条下载失败就退出，并且不改写 `data/`。不要给 FRED 请求加自定义 User-Agent：自定义 UA 在 HTTP/2 上会立刻报错，在 HTTP/1.1 上会挂起；Python 默认请求头可以下载。

要加一条 FRED 序列：编辑 `scripts/fetch_liquidity.py` 的 `SERIES`，百万美元用 `to_bn = Decimal("0.001")`，利率和指数用 `None`，然后运行 `python3 scripts/fetch_liquidity.py`。要显示在流动性页上，再改 `index.html`。

## 另外三页的历史有多长

情绪、盈利、半导体目前只有 2026 年 9 月中下旬的笔记，页面会写明起始日期和点数，不会把短历史画成一条很长的线。
