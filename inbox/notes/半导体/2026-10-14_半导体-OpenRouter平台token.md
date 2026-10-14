---
src_code: OR
src_type: 其他数据表
src_layer: 事实层
src_name: OpenRouter平台token跟踪
src_schema: 2
published_at: "2026-10-14T08:13:42+08:00"
window_start: "2026-10-07T00:00:00+00:00"
window_end: "2026-10-13T23:59:59+00:00"
fetch_status: OK
run_date: 2026-10-14
data_date: 2026-10-13
item_count: 3
window_1d: 2026-10-13
window_7d: 2026-10-07~2026-10-13
window_30d: 2026-09-14~2026-10-13
as_of: "2026-10-14T00:13:11.182Z"
---

# OpenRouter 平台 token 跟踪 2026-10-13

抓取时间：2026-10-14 08:13:42 北京时间

### 1. token 总消费
| 指标 | 当前值 | 环比 | 历史提示 |
|---|---:|---:|---|
| 1日 | 26.21T | -2.7% | 正常区间（30%分位 -2.8%） |
| 7日 | 177.01T | 7.3% | 正常区间（30%分位 1.2%） |
| 30日 | 665.59T | 42.1% | 正常区间（30%分位 17.8%） |

### 2. 模型 Top 5（最近7日）
| 排名 | 模型 | Token | 占比 |
|---:|---|---:|---:|
| 1 | deepseek/deepseek-v4.1-flash-20260910 | 40.47T | 22.9% |
| 2 | stepfun/step-5-preview-20261008 | 15.05T | 8.5% |
| 3 | z-ai/glm-5.3-flash-20260826 | 12.87T | 7.3% |
| 4 | xiaomi/mimo-v2.6-flash-20260921 | 11.61T | 6.6% |
| 5 | tencent/hy4-preview-20260827 | 8.13T | 4.6% |

### 3. Provider Top 5（最近7日）
| 排名 | Provider | Token | 占比 |
|---:|---|---:|---:|
| 1 | deepseek | 50.03T | 28.3% |
| 2 | z-ai | 18.45T | 10.4% |
| 3 | stepfun | 15.05T | 8.5% |
| 4 | openai | 13.92T | 7.9% |
| 5 | xiaomi | 13.65T | 7.7% |

### 4. 用途结构（最近7日）
| 排名 | 用途 | 数据 | 占比 |
|---:|---|---:|---:|
| 1 | Code | 约 61.07T | 34.5% |
| 2 | Agent | 约 57.71T | 32.6% |
| 3 | General | 约 46.20T | 26.1% |
| 4 | Data | 约 12.04T | 6.8% |
| 1 | Workflow Execution（细分） | 约 38.94T | 22.0% |
| 2 | Code Generation（细分） | 约 21.42T | 12.1% |
| 3 | Multi-step Planning（细分） | 约 13.10T | 7.4% |
| 4 | Classification（细分） | 约 12.04T | 6.8% |
| 5 | Debugging（细分） | 约 11.51T | 6.5% |

简评：30D 仍处于高增速区间，但7D增速明显低于30D，短期更像高位盘整；用途上 Code+Agent 仍是主导。
口径：rankings-daily 为 OpenRouter 公共聚合数据，token=prompt+completion；用途结构只公开 share，表中用途 token 为按7D总量折算的近似值。私有/ZDR/隐藏流量不含在内。
Source: OpenRouter (openrouter.ai/rankings), as of 2026-10-14T00:13:11.182Z. Licensed under CC BY 4.0.
本地历史：/workspace/semiconductor-data-tracker/openrouter_platform_usage_history.csv
