# 美国流动性

这个仓库保存一组美国流动性数据，并用一个静态网页展示。面向自己每周看一眼，页面文字是简体中文。

数据从圣路易斯联储 FRED 的公开 CSV 拉取，不需要 API 密钥，也不调用任何模型。

网页地址（需要先按文末步骤打开 GitHub Pages）：

https://cool1990.github.io/macro-dashboard/

## 文件夹

- `data/series/`：每个 FRED 序列一个 CSV，从 2022-01-01 起。`value` 是 FRED 的原始单位。
- `data/derived/weekly.csv`：按周三对齐的总资产、财政部账户、隔夜逆回购、准备金、净流动性、周变动、准备金分位，以及该周三的融资利差。金额单位是十亿美元。
- `data/derived/spreads.csv`：每个交易日的 SOFR、EFFR、IORB，以及 SOFR−IORB、EFFR−IORB，利差单位是基点。
- `data/meta.json`：中文名、单位、频率、来源链接、最近观测日、本库更新时间。
- `scripts/fetch_liquidity.py`：拉取并计算。只用 Python 标准库。
- `index.html`：网页。图表库从 CDN 加载，没有构建步骤。
- `.github/workflows/fetch-data.yml`：每天 22:00 UTC（大约北京时间次日 06:00）更新数据，也可以手动运行。成功后把 `data/` 提交回 `main`。
- `.github/workflows/pages.yml`：把网页发布到 GitHub Pages。

`data/` 里只放数据。脚本、网页和工作流都在外面。

## 本地查看

```bash
python3 scripts/fetch_liquidity.py
python3 -m http.server 8000
```

浏览器打开 http://localhost:8000/ 。不要直接双击 `index.html`，浏览器不允许页面用这种方式读取旁边的数据文件。

## 指标和单位

净流动性使用市场常用算法，**不是官方指标**：

美联储总资产（WALCL）− 财政部账户周三水平（WDTGAL）− 隔夜逆回购（RRPONTSYD）

FRED 里 WALCL、WDTGAL、准备金（WRBWFRBL）的单位是百万美元，写入周度文件时除以 1000，变成十亿美元。隔夜逆回购本身就是十亿美元，不再缩放。

周变动是与上一条周三观测相比的差额。

SOFR−IORB 和 EFFR−IORB 的单位是基点：(利率 − IORB) × 100。

准备金分位是 2022-01-01 起、到该周三为止的周三观测中，准备金余额不高于当前值的占比。它只说明当前水平在这段历史里的位置，**不是准备金短缺的度量**。

另外保存了三条辅助序列：芝加哥联储 NFCI、美国高收益债利差（BAMLH0A0HYM2）、VIX。高收益债利差在 FRED 里的单位是百分点，不是基点。

## 数据怎么更新

GitHub Actions 里的「更新数据」每天 22:00 UTC 跑一次，也可以在 Actions 页面手动运行。

脚本会重新下载全部序列。某一条下载失败、返回的不是 CSV，或算不出周三表格时，脚本以非零状态退出，并且**不会改写** `data/`。这样失败的一轮不会悄悄留下旧数据冒充新数据。工作流变红，就说明这一轮没有刷新成功。

不要给 FRED 的请求加自定义 User-Agent。2026-09-27 实测：自定义 UA 在 HTTP/2 上会立刻报 `INTERNAL_ERROR`，在 HTTP/1.1 上会挂起直到超时；Python 和 curl 的默认请求头可以正常下载。脚本因此不设置 User-Agent，并最多重试 3 次。

## 怎么加一条新序列

1. 打开 `scripts/fetch_liquidity.py`，在 `SERIES` 里照着现有条目加一条：`id`、中文 `name`、原始 `unit`、`frequency`。
2. 如果原始单位是百万美元、页面上要按十亿美元显示，把 `to_bn` 设为 `Decimal("0.001")`。已经是十亿美元就设为 `Decimal("1")`。利率和指数设为 `None`，它们只进 `data/series/`，不参与净流动性。
3. 运行 `python3 scripts/fetch_liquidity.py`。成功后会出现 `data/series/你的ID.csv`，`data/meta.json` 里也会有这一条。任何一条拉不下来，整个命令失败，`data/` 保持原样。
4. 要在网页上画出来，就在 `index.html` 里加一张图或一格数字。页面读的是 `data/` 里的文件。
5. 提交脚本、`data/` 和页面。

净流动性、周变动、利差和准备金分位是脚本里单独算的。新序列如果只是多存一条原始数据，改 `SERIES` 再跑脚本就够了。

## 打开 GitHub Pages

仓库设置没法从这里改。请在 GitHub 上做一次：

1. 打开仓库的 **Settings → Pages**。
2. 在 **Build and deployment** 里，把 **Source** 选成 **GitHub Actions**。
3. 保存后，到 **Actions** 里打开「发布网页」，手动运行一次；之后每次 `main` 上的网页或 `data/` 有更新，也会自动发布。

如果第一次运行停在等待批准，在那次运行的页面上批准 `github-pages` 环境。

发布成功后的地址是：

https://cool1990.github.io/macro-dashboard/
