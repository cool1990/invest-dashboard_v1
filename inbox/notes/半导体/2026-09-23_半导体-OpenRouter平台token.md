---
src_code: OR
src_type: 其他数据表
src_layer: 事实层
src_name: OpenRouter平台token跟踪
src_schema: 2
published_at: "2026-09-23T08:05:31+08:00"
window_start: "2026-09-16T00:00:00+00:00"
window_end: "2026-09-22T23:59:59+00:00"
fetch_status: OK
run_date: 2026-09-23
data_date: 2026-09-22
item_count: 3
window_1d: 2026-09-22
window_7d: 2026-09-16~2026-09-22
window_30d: 2026-08-24~2026-09-22
as_of: "2026-09-23T00:05:15.875Z"
---

# OpenRouter 平台 token 跟踪 2026-09-22

抓取时间：2026-09-23 08:05:31 北京时间

### 1. token 总消费
| 指标 | 当前值 | 环比 | 历史提示 |
|---|---:|---:|---|
| 1日 | 20.46T | -1.8% | 正常区间（30%分位 -2.8%） |
| 7日 | 134.32T | 7.9% | 正常区间（30%分位 1.1%） |
| 30日 | 525.42T | 69.8% | 高于历史70%分位（46.7%） |

### 2. 模型 Top 5（最近7日）
| 排名 | 模型 | Token | 占比 |
|---:|---|---:|---:|
| 1 | z-ai/glm-5.3-flash-20260826 | 18.42T | 13.7% |
| 2 | deepseek/deepseek-v4.1-flash-20260910 | 17.83T | 13.3% |
| 3 | tencent/hy4-preview-20260827 | 12.94T | 9.6% |
| 4 | openai/gpt-5.6-luna-20260709 | 8.67T | 6.5% |
| 5 | deepseek/deepseek-v4-flash-20260731 | 8.64T | 6.4% |

### 3. Provider Top 5（最近7日）
| 排名 | Provider | Token | 占比 |
|---:|---|---:|---:|
| 1 | deepseek | 33.47T | 24.9% |
| 2 | z-ai | 23.34T | 17.4% |
| 3 | tencent | 17.15T | 12.8% |
| 4 | openai | 13.89T | 10.3% |
| 5 | xiaomi | 6.81T | 5.1% |

### 4. 用途结构（最近7日）
| 排名 | 用途 | 数据 | 占比 |
|---:|---|---:|---:|
| 1 | Code | 约 48.76T | 36.3% |
| 2 | Agent | 约 48.09T | 35.8% |
| 3 | General | 约 29.28T | 21.8% |
| 4 | Data | 约 8.33T | 6.2% |
| 1 | Workflow Execution（细分） | 约 32.91T | 24.5% |
| 2 | Code Generation（细分） | 约 16.66T | 12.4% |
| 3 | Multi-step Planning（细分） | 约 10.48T | 7.8% |
| 4 | Debugging（细分） | 约 9.13T | 6.8% |
| 5 | Classification（细分） | 约 7.93T | 5.9% |

简评：30D 仍处于高增速区间，但7D增速明显低于30D，短期更像高位盘整；用途上 Code+Agent 仍是主导。
口径：rankings-daily 为 OpenRouter 公共聚合数据，token=prompt+completion；用途结构只公开 share，表中用途 token 为按7D总量折算的近似值。私有/ZDR/隐藏流量不含在内。
Source: OpenRouter (openrouter.ai/rankings), as of 2026-09-23T00:05:15.875Z. Licensed under CC BY 4.0.
本地历史：/workspace/semiconductor-data-tracker/openrouter_platform_usage_history.csv
