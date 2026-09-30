---
src_code: OR
src_type: 其他数据表
src_layer: 事实层
src_name: OpenRouter平台token跟踪
src_schema: 2
published_at: "2026-09-30T08:05:52+08:00"
window_start: "2026-09-23T00:00:00+00:00"
window_end: "2026-09-29T23:59:59+00:00"
fetch_status: OK
run_date: 2026-09-30
data_date: 2026-09-29
item_count: 3
window_1d: 2026-09-29
window_7d: 2026-09-23~2026-09-29
window_30d: 2026-08-31~2026-09-29
as_of: "2026-09-30T00:05:53.707Z"
---

# OpenRouter 平台 token 跟踪 2026-09-29

抓取时间：2026-09-30 08:05:52 北京时间

### 1. token 总消费
| 指标 | 当前值 | 环比 | 历史提示 |
|---|---:|---:|---|
| 1日 | 24.94T | 4.2% | 正常区间（30%分位 -2.8%） |
| 7日 | 153.42T | 14.2% | 高于历史70%分位（12.6%） |
| 30日 | 565.84T | 55.0% | 高于历史70%分位（47.6%） |

### 2. 模型 Top 5（最近7日）
| 排名 | 模型 | Token | 占比 |
|---:|---|---:|---:|
| 1 | stealth/space-bunny-alpha | 23.38T | 15.2% |
| 2 | deepseek/deepseek-v4.1-flash-20260910 | 22.03T | 14.4% |
| 3 | z-ai/glm-5.3-flash-20260826 | 11.62T | 7.6% |
| 4 | openai/gpt-5.6-luna-20260709 | 8.31T | 5.4% |
| 5 | xiaomi/mimo-v2.6-flash-20260921 | 8.21T | 5.4% |

### 3. Provider Top 5（最近7日）
| 排名 | Provider | Token | 占比 |
|---:|---|---:|---:|
| 1 | deepseek | 34.48T | 22.5% |
| 2 | stealth | 23.38T | 15.2% |
| 3 | openai | 17.73T | 11.6% |
| 4 | z-ai | 15.91T | 10.4% |
| 5 | xiaomi | 10.85T | 7.1% |

### 4. 用途结构（最近7日）
| 排名 | 用途 | 数据 | 占比 |
|---:|---|---:|---:|
| 1 | Code | 约 56.46T | 36.8% |
| 2 | Agent | 约 54.00T | 35.2% |
| 3 | General | 约 33.60T | 21.9% |
| 4 | Data | 约 9.36T | 6.1% |
| 1 | Workflow Execution（细分） | 约 36.36T | 23.7% |
| 2 | Code Generation（细分） | 约 18.56T | 12.1% |
| 3 | Multi-step Planning（细分） | 约 12.43T | 8.1% |
| 4 | Debugging（细分） | 约 11.20T | 7.3% |
| 5 | Classification（细分） | 约 10.28T | 6.7% |

简评：30D 仍处于高增速区间，但7D增速明显低于30D，短期更像高位盘整；用途上 Code+Agent 仍是主导。
口径：rankings-daily 为 OpenRouter 公共聚合数据，token=prompt+completion；用途结构只公开 share，表中用途 token 为按7D总量折算的近似值。私有/ZDR/隐藏流量不含在内。
Source: OpenRouter (openrouter.ai/rankings), as of 2026-09-30T00:05:53.707Z. Licensed under CC BY 4.0.
本地历史：/workspace/semiconductor-data-tracker/openrouter_platform_usage_history.csv
