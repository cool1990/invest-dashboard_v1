---
src_code: OR
src_type: 其他数据表
src_layer: 事实层
src_name: OpenRouter平台token跟踪
src_schema: 2
published_at: "2026-10-07T08:05:08+08:00"
window_start: "2026-09-30T00:00:00+00:00"
window_end: "2026-10-06T23:59:59+00:00"
fetch_status: OK
run_date: 2026-10-07
data_date: 2026-10-06
item_count: 3
window_1d: 2026-10-06
window_7d: 2026-09-30~2026-10-06
window_30d: 2026-09-07~2026-10-06
as_of: "2026-10-07T00:05:08.794Z"
---

# OpenRouter 平台 token 跟踪 2026-10-06

抓取时间：2026-10-07 08:05:08 北京时间

### 1. token 总消费
| 指标 | 当前值 | 环比 | 历史提示 |
|---|---:|---:|---|
| 1日 | 22.11T | -14.5% | 低于历史30%分位（-2.8%） |
| 7日 | 164.97T | 7.5% | 正常区间（30%分位 1.2%） |
| 30日 | 615.34T | 48.3% | 高于历史70%分位（48.3%） |

### 2. 模型 Top 5（最近7日）
| 排名 | 模型 | Token | 占比 |
|---:|---|---:|---:|
| 1 | stealth/space-bunny-alpha | 33.33T | 20.2% |
| 2 | deepseek/deepseek-v4.1-flash-20260910 | 29.58T | 17.9% |
| 3 | z-ai/glm-5.3-flash-20260826 | 10.19T | 6.2% |
| 4 | xiaomi/mimo-v2.6-flash-20260921 | 9.87T | 6.0% |
| 5 | openai/gpt-6-luna-20260922 | 6.44T | 3.9% |

### 3. Provider Top 5（最近7日）
| 排名 | Provider | Token | 占比 |
|---:|---|---:|---:|
| 1 | deepseek | 40.46T | 24.5% |
| 2 | stealth | 33.33T | 20.2% |
| 3 | openai | 15.28T | 9.3% |
| 4 | z-ai | 14.67T | 8.9% |
| 5 | xiaomi | 12.07T | 7.3% |

### 4. 用途结构（最近7日）
| 排名 | 用途 | 数据 | 占比 |
|---:|---|---:|---:|
| 1 | Code | 约 58.40T | 35.4% |
| 2 | Agent | 约 58.23T | 35.3% |
| 3 | General | 约 37.78T | 22.9% |
| 4 | Data | 约 10.56T | 6.4% |
| 1 | Workflow Execution（细分） | 约 38.77T | 23.5% |
| 2 | Code Generation（细分） | 约 19.47T | 11.8% |
| 3 | Multi-step Planning（细分） | 约 13.69T | 8.3% |
| 4 | Classification（细分） | 约 12.04T | 7.3% |
| 5 | Debugging（细分） | 约 11.22T | 6.8% |

简评：30D 仍处于高增速区间，但7D增速明显低于30D，短期更像高位盘整；用途上 Code+Agent 仍是主导。
口径：rankings-daily 为 OpenRouter 公共聚合数据，token=prompt+completion；用途结构只公开 share，表中用途 token 为按7D总量折算的近似值。私有/ZDR/隐藏流量不含在内。
Source: OpenRouter (openrouter.ai/rankings), as of 2026-10-07T00:05:08.794Z. Licensed under CC BY 4.0.
本地历史：/workspace/semiconductor-data-tracker/openrouter_platform_usage_history.csv
