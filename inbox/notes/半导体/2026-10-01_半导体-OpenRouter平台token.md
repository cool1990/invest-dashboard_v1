---
src_code: OR
src_type: 其他数据表
src_layer: 事实层
src_name: OpenRouter平台token跟踪
src_schema: 2
published_at: "2026-10-01T08:05:48+08:00"
window_start: "2026-09-24T00:00:00+00:00"
window_end: "2026-09-30T23:59:59+00:00"
fetch_status: OK
run_date: 2026-10-01
data_date: 2026-09-30
item_count: 3
window_1d: 2026-09-30
window_7d: 2026-09-24~2026-09-30
window_30d: 2026-09-01~2026-09-30
as_of: "2026-10-01T00:05:49.262Z"
---

# OpenRouter 平台 token 跟踪 2026-09-30

抓取时间：2026-10-01 08:05:48 北京时间

### 1. token 总消费
| 指标 | 当前值 | 环比 | 历史提示 |
|---|---:|---:|---|
| 1日 | 24.38T | -2.2% | 正常区间（30%分位 -2.8%） |
| 7日 | 157.96T | 16.3% | 高于历史70%分位（12.6%） |
| 30日 | 575.90T | 54.7% | 高于历史70%分位（47.8%） |

### 2. 模型 Top 5（最近7日）
| 排名 | 模型 | Token | 占比 |
|---:|---|---:|---:|
| 1 | stealth/space-bunny-alpha | 28.43T | 18.0% |
| 2 | deepseek/deepseek-v4.1-flash-20260910 | 22.71T | 14.4% |
| 3 | z-ai/glm-5.3-flash-20260826 | 10.63T | 6.7% |
| 4 | xiaomi/mimo-v2.6-flash-20260921 | 9.10T | 5.8% |
| 5 | openai/gpt-5.6-luna-20260709 | 7.75T | 4.9% |

### 3. Provider Top 5（最近7日）
| 排名 | Provider | Token | 占比 |
|---:|---|---:|---:|
| 1 | deepseek | 34.87T | 22.1% |
| 2 | stealth | 28.43T | 18.0% |
| 3 | openai | 17.80T | 11.3% |
| 4 | z-ai | 14.75T | 9.3% |
| 5 | xiaomi | 11.60T | 7.3% |

### 4. 用途结构（最近7日）
| 排名 | 用途 | 数据 | 占比 |
|---:|---|---:|---:|
| 1 | Code | 约 57.81T | 36.6% |
| 2 | Agent | 约 55.92T | 35.4% |
| 3 | General | 约 34.75T | 22.0% |
| 4 | Data | 约 9.64T | 6.1% |
| 1 | Workflow Execution（细分） | 约 37.44T | 23.7% |
| 2 | Code Generation（细分） | 约 19.27T | 12.2% |
| 3 | Multi-step Planning（细分） | 约 12.95T | 8.2% |
| 4 | Debugging（细分） | 约 11.53T | 7.3% |
| 5 | Classification（细分） | 约 10.74T | 6.8% |

简评：30D 仍处于高增速区间，但7D增速明显低于30D，短期更像高位盘整；用途上 Code+Agent 仍是主导。
口径：rankings-daily 为 OpenRouter 公共聚合数据，token=prompt+completion；用途结构只公开 share，表中用途 token 为按7D总量折算的近似值。私有/ZDR/隐藏流量不含在内。
Source: OpenRouter (openrouter.ai/rankings), as of 2026-10-01T00:05:49.262Z. Licensed under CC BY 4.0.
本地历史：/workspace/semiconductor-data-tracker/openrouter_platform_usage_history.csv
