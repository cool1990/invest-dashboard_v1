---
src_code: OR
src_type: 其他数据表
src_layer: 事实层
src_name: OpenRouter平台token跟踪
src_schema: 2
published_at: "2026-09-26T08:05:58+08:00"
window_start: "2026-09-19T00:00:00+00:00"
window_end: "2026-09-25T23:59:59+00:00"
fetch_status: OK
run_date: 2026-09-26
data_date: 2026-09-25
item_count: 3
window_1d: 2026-09-25
window_7d: 2026-09-19~2026-09-25
window_30d: 2026-08-27~2026-09-25
as_of: "2026-09-26T00:05:14.020Z"
---

# OpenRouter 平台 token 跟踪 2026-09-25

抓取时间：2026-09-26 08:05:58 北京时间

### 1. token 总消费
| 指标 | 当前值 | 环比 | 历史提示 |
|---|---:|---:|---|
| 1日 | 22.44T | 2.6% | 正常区间（30%分位 -2.8%） |
| 7日 | 140.61T | 10.3% | 正常区间（30%分位 1.1%） |
| 30日 | 534.01T | 56.4% | 高于历史70%分位（47.3%） |

### 2. 模型 Top 5（最近7日）
| 排名 | 模型 | Token | 占比 |
|---:|---|---:|---:|
| 1 | deepseek/deepseek-v4.1-flash-20260910 | 19.25T | 13.7% |
| 2 | z-ai/glm-5.3-flash-20260826 | 19.22T | 13.7% |
| 3 | tencent/hy4-preview-20260827 | 11.15T | 7.9% |
| 4 | openai/gpt-5.6-luna-20260709 | 8.60T | 6.1% |
| 5 | deepseek/deepseek-v4-flash-20260731 | 8.23T | 5.9% |

### 3. Provider Top 5（最近7日）
| 排名 | Provider | Token | 占比 |
|---:|---|---:|---:|
| 1 | deepseek | 33.28T | 23.7% |
| 2 | z-ai | 24.06T | 17.1% |
| 3 | openai | 14.72T | 10.5% |
| 4 | tencent | 14.19T | 10.1% |
| 5 | xiaomi | 8.09T | 5.8% |

### 4. 用途结构（最近7日）
| 排名 | 用途 | 数据 | 占比 |
|---:|---|---:|---:|
| 1 | Code | 约 51.32T | 36.5% |
| 2 | Agent | 约 50.62T | 36.0% |
| 3 | General | 约 30.37T | 21.6% |
| 4 | Data | 约 8.44T | 6.0% |
| 1 | Workflow Execution（细分） | 约 34.31T | 24.4% |
| 2 | Code Generation（细分） | 约 17.30T | 12.3% |
| 3 | Multi-step Planning（细分） | 约 11.53T | 8.2% |
| 4 | Debugging（细分） | 约 9.70T | 6.9% |
| 5 | Classification（细分） | 约 8.58T | 6.1% |

简评：30D 仍处于高增速区间，但7D增速明显低于30D，短期更像高位盘整；用途上 Code+Agent 仍是主导。
口径：rankings-daily 为 OpenRouter 公共聚合数据，token=prompt+completion；用途结构只公开 share，表中用途 token 为按7D总量折算的近似值。私有/ZDR/隐藏流量不含在内。
Source: OpenRouter (openrouter.ai/rankings), as of 2026-09-26T00:05:14.020Z. Licensed under CC BY 4.0.
本地历史：/workspace/semiconductor-data-tracker/openrouter_platform_usage_history.csv
