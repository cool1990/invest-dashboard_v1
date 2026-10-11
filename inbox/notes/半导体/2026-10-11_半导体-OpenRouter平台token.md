---
src_code: OR
src_type: 其他数据表
src_layer: 事实层
src_name: OpenRouter平台token跟踪
src_schema: 2
published_at: "2026-10-11T08:05:15+08:00"
window_start: "2026-10-04T00:00:00+00:00"
window_end: "2026-10-10T23:59:59+00:00"
fetch_status: OK
run_date: 2026-10-11
data_date: 2026-10-10
item_count: 3
window_1d: 2026-10-10
window_7d: 2026-10-04~2026-10-10
window_30d: 2026-09-11~2026-10-10
as_of: "2026-10-11T00:05:16.792Z"
---

# OpenRouter 平台 token 跟踪 2026-10-10

抓取时间：2026-10-11 08:05:15 北京时间

### 1. token 总消费
| 指标 | 当前值 | 环比 | 历史提示 |
|---|---:|---:|---|
| 1日 | 24.02T | -9.8% | 低于历史30%分位（-2.8%） |
| 7日 | 171.00T | 4.5% | 正常区间（30%分位 1.2%） |
| 30日 | 640.35T | 42.0% | 正常区间（30%分位 17.6%） |

### 2. 模型 Top 5（最近7日）
| 排名 | 模型 | Token | 占比 |
|---:|---|---:|---:|
| 1 | deepseek/deepseek-v4.1-flash-20260910 | 38.71T | 22.6% |
| 2 | z-ai/glm-5.3-flash-20260826 | 11.63T | 6.8% |
| 3 | xiaomi/mimo-v2.6-flash-20260921 | 11.33T | 6.6% |
| 4 | stealth/space-bunny-alpha | 10.92T | 6.4% |
| 5 | tencent/hy4-preview-20260827 | 8.41T | 4.9% |

### 3. Provider Top 5（最近7日）
| 排名 | Provider | Token | 占比 |
|---:|---|---:|---:|
| 1 | deepseek | 48.81T | 28.5% |
| 2 | z-ai | 16.65T | 9.7% |
| 3 | openai | 14.71T | 8.6% |
| 4 | xiaomi | 13.30T | 7.8% |
| 5 | stealth | 10.92T | 6.4% |

### 4. 用途结构（最近7日）
| 排名 | 用途 | 数据 | 占比 |
|---:|---|---:|---:|
| 1 | Code | 约 60.87T | 35.6% |
| 2 | Agent | 约 56.77T | 33.2% |
| 3 | General | 约 41.72T | 24.4% |
| 4 | Data | 约 11.63T | 6.8% |
| 1 | Workflow Execution（细分） | 约 38.30T | 22.4% |
| 2 | Code Generation（细分） | 约 21.37T | 12.5% |
| 3 | Multi-step Planning（细分） | 约 13.00T | 7.6% |
| 4 | Classification（细分） | 约 12.14T | 7.1% |
| 5 | Debugging（细分） | 约 11.29T | 6.6% |

简评：30D 仍处于高增速区间，但7D增速明显低于30D，短期更像高位盘整；用途上 Code+Agent 仍是主导。
口径：rankings-daily 为 OpenRouter 公共聚合数据，token=prompt+completion；用途结构只公开 share，表中用途 token 为按7D总量折算的近似值。私有/ZDR/隐藏流量不含在内。
Source: OpenRouter (openrouter.ai/rankings), as of 2026-10-11T00:05:16.792Z. Licensed under CC BY 4.0.
本地历史：/workspace/semiconductor-data-tracker/openrouter_platform_usage_history.csv
