---
src_code: OR
src_type: 其他数据表
src_layer: 事实层
src_name: OpenRouter平台token跟踪
src_schema: 2
published_at: "2026-10-04T08:06:10+08:00"
window_start: "2026-09-27T00:00:00+00:00"
window_end: "2026-10-03T23:59:59+00:00"
fetch_status: OK
run_date: 2026-10-04
data_date: 2026-10-03
item_count: 3
window_1d: 2026-10-03
window_7d: 2026-09-27~2026-10-03
window_30d: 2026-09-04~2026-10-03
as_of: "2026-10-04T00:05:10.717Z"
---

# OpenRouter 平台 token 跟踪 2026-10-03

抓取时间：2026-10-04 08:06:10 北京时间

### 1. token 总消费
| 指标 | 当前值 | 环比 | 历史提示 |
|---|---:|---:|---|
| 1日 | 22.32T | -7.2% | 低于历史30%分位（-2.8%） |
| 7日 | 163.60T | 14.7% | 高于历史70%分位（12.6%） |
| 30日 | 592.47T | 48.4% | 高于历史70%分位（48.4%） |

### 2. 模型 Top 5（最近7日）
| 排名 | 模型 | Token | 占比 |
|---:|---|---:|---:|
| 1 | stealth/space-bunny-alpha | 35.93T | 22.0% |
| 2 | deepseek/deepseek-v4.1-flash-20260910 | 25.63T | 15.7% |
| 3 | z-ai/glm-5.3-flash-20260826 | 9.57T | 5.8% |
| 4 | xiaomi/mimo-v2.6-flash-20260921 | 9.54T | 5.8% |
| 5 | tencent/hy4-preview-20260827 | 6.54T | 4.0% |

### 3. Provider Top 5（最近7日）
| 排名 | Provider | Token | 占比 |
|---:|---|---:|---:|
| 1 | deepseek | 36.82T | 22.5% |
| 2 | stealth | 35.93T | 22.0% |
| 3 | openai | 17.28T | 10.6% |
| 4 | z-ai | 13.77T | 8.4% |
| 5 | xiaomi | 11.81T | 7.2% |

### 4. 用途结构（最近7日）
| 排名 | 用途 | 数据 | 占比 |
|---:|---|---:|---:|
| 1 | Code | 约 59.06T | 36.1% |
| 2 | Agent | 约 57.92T | 35.4% |
| 3 | General | 约 36.48T | 22.3% |
| 4 | Data | 约 10.14T | 6.2% |
| 1 | Workflow Execution（细分） | 约 38.61T | 23.6% |
| 2 | Code Generation（细分） | 约 19.63T | 12.0% |
| 3 | Multi-step Planning（细分） | 约 13.58T | 8.3% |
| 4 | Classification（细分） | 约 11.45T | 7.0% |
| 5 | Debugging（细分） | 约 11.45T | 7.0% |

简评：30D 仍处于高增速区间，但7D增速明显低于30D，短期更像高位盘整；用途上 Code+Agent 仍是主导。
口径：rankings-daily 为 OpenRouter 公共聚合数据，token=prompt+completion；用途结构只公开 share，表中用途 token 为按7D总量折算的近似值。私有/ZDR/隐藏流量不含在内。
Source: OpenRouter (openrouter.ai/rankings), as of 2026-10-04T00:05:10.717Z. Licensed under CC BY 4.0.
本地历史：/workspace/semiconductor-data-tracker/openrouter_platform_usage_history.csv
