---
src_code: OR
src_type: 其他数据表
src_layer: 事实层
src_name: OpenRouter平台token跟踪
src_schema: 2
published_at: "2026-10-13T08:57:56+08:00"
window_start: "2026-10-06T00:00:00+00:00"
window_end: "2026-10-12T23:59:59+00:00"
fetch_status: OK
run_date: 2026-10-13
data_date: 2026-10-12
item_count: 3
window_1d: 2026-10-12
window_7d: 2026-10-06~2026-10-12
window_30d: 2026-09-13~2026-10-12
as_of: "2026-10-13T00:57:56.934Z"
---

# OpenRouter 平台 token 跟踪 2026-10-12

抓取时间：2026-10-13 08:57:56 北京时间

### 1. token 总消费
| 指标 | 当前值 | 环比 | 历史提示 |
|---|---:|---:|---|
| 1日 | 26.94T | 14.1% | 高于历史70%分位（4.5%） |
| 7日 | 172.91T | 3.1% | 正常区间（30%分位 1.2%） |
| 30日 | 656.11T | 41.6% | 正常区间（30%分位 17.7%） |

### 2. 模型 Top 5（最近7日）
| 排名 | 模型 | Token | 占比 |
|---:|---|---:|---:|
| 1 | deepseek/deepseek-v4.1-flash-20260910 | 40.53T | 23.4% |
| 2 | z-ai/glm-5.3-flash-20260826 | 12.67T | 7.3% |
| 3 | stepfun/step-5-preview-20261008 | 12.09T | 7.0% |
| 4 | xiaomi/mimo-v2.6-flash-20260921 | 11.54T | 6.7% |
| 5 | tencent/hy4-preview-20260827 | 8.31T | 4.8% |

### 3. Provider Top 5（最近7日）
| 排名 | Provider | Token | 占比 |
|---:|---|---:|---:|
| 1 | deepseek | 50.34T | 29.1% |
| 2 | z-ai | 18.16T | 10.5% |
| 3 | openai | 14.46T | 8.4% |
| 4 | xiaomi | 13.48T | 7.8% |
| 5 | stepfun | 12.09T | 7.0% |

### 4. 用途结构（最近7日）
| 排名 | 用途 | 数据 | 占比 |
|---:|---|---:|---:|
| 1 | Code | 约 60.52T | 35.0% |
| 2 | Agent | 约 56.54T | 32.7% |
| 3 | General | 约 44.27T | 25.6% |
| 4 | Data | 约 11.76T | 6.8% |
| 1 | Workflow Execution（细分） | 约 38.04T | 22.0% |
| 2 | Code Generation（细分） | 约 21.44T | 12.4% |
| 3 | Multi-step Planning（细分） | 约 12.80T | 7.4% |
| 4 | Classification（细分） | 约 11.93T | 6.9% |
| 5 | Debugging（细分） | 约 11.24T | 6.5% |

简评：30D 仍处于高增速区间，但7D增速明显低于30D，短期更像高位盘整；用途上 Code+Agent 仍是主导。
口径：rankings-daily 为 OpenRouter 公共聚合数据，token=prompt+completion；用途结构只公开 share，表中用途 token 为按7D总量折算的近似值。私有/ZDR/隐藏流量不含在内。
Source: OpenRouter (openrouter.ai/rankings), as of 2026-10-13T00:57:56.934Z. Licensed under CC BY 4.0.
本地历史：/workspace/semiconductor-data-tracker/openrouter_platform_usage_history.csv
