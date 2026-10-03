---
src_code: OR
src_type: 其他数据表
src_layer: 事实层
src_name: OpenRouter平台token跟踪
src_schema: 2
published_at: "2026-10-03T08:05:57+08:00"
window_start: "2026-09-26T00:00:00+00:00"
window_end: "2026-10-02T23:59:59+00:00"
fetch_status: OK
run_date: 2026-10-03
data_date: 2026-10-02
item_count: 3
window_1d: 2026-10-02
window_7d: 2026-09-26~2026-10-02
window_30d: 2026-09-03~2026-10-02
as_of: "2026-10-03T00:05:13.971Z"
---

# OpenRouter 平台 token 跟踪 2026-10-02

抓取时间：2026-10-03 08:05:57 北京时间

### 1. token 总消费
| 指标 | 当前值 | 环比 | 历史提示 |
|---|---:|---:|---|
| 1日 | 24.06T | 2.6% | 正常区间（30%分位 -2.8%） |
| 7日 | 161.14T | 14.6% | 高于历史70%分位（12.6%） |
| 30日 | 588.72T | 50.7% | 高于历史70%分位（48.0%） |

### 2. 模型 Top 5（最近7日）
| 排名 | 模型 | Token | 占比 |
|---:|---|---:|---:|
| 1 | stealth/space-bunny-alpha | 33.53T | 20.8% |
| 2 | deepseek/deepseek-v4.1-flash-20260910 | 24.17T | 15.0% |
| 3 | z-ai/glm-5.3-flash-20260826 | 9.67T | 6.0% |
| 4 | xiaomi/mimo-v2.6-flash-20260921 | 9.38T | 5.8% |
| 5 | tencent/hy4-preview-20260827 | 6.65T | 4.1% |

### 3. Provider Top 5（最近7日）
| 排名 | Provider | Token | 占比 |
|---:|---|---:|---:|
| 1 | deepseek | 35.81T | 22.2% |
| 2 | stealth | 33.53T | 20.8% |
| 3 | openai | 18.05T | 11.2% |
| 4 | z-ai | 13.59T | 8.4% |
| 5 | xiaomi | 11.67T | 7.2% |

### 4. 用途结构（最近7日）
| 排名 | 用途 | 数据 | 占比 |
|---:|---|---:|---:|
| 1 | Code | 约 58.17T | 36.1% |
| 2 | Agent | 约 56.88T | 35.3% |
| 3 | General | 约 36.10T | 22.4% |
| 4 | Data | 约 9.83T | 6.1% |
| 1 | Workflow Execution（细分） | 约 37.87T | 23.5% |
| 2 | Code Generation（细分） | 约 19.82T | 12.3% |
| 3 | Multi-step Planning（细分） | 约 13.37T | 8.3% |
| 4 | Classification（细分） | 约 11.44T | 7.1% |
| 5 | Debugging（细分） | 约 11.44T | 7.1% |

简评：30D 仍处于高增速区间，但7D增速明显低于30D，短期更像高位盘整；用途上 Code+Agent 仍是主导。
口径：rankings-daily 为 OpenRouter 公共聚合数据，token=prompt+completion；用途结构只公开 share，表中用途 token 为按7D总量折算的近似值。私有/ZDR/隐藏流量不含在内。
Source: OpenRouter (openrouter.ai/rankings), as of 2026-10-03T00:05:13.971Z. Licensed under CC BY 4.0.
本地历史：/workspace/semiconductor-data-tracker/openrouter_platform_usage_history.csv
