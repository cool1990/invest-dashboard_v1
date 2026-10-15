---
src_code: OR
src_type: 其他数据表
src_layer: 事实层
src_name: OpenRouter平台token跟踪
src_schema: 2
published_at: "2026-10-15T08:13:15+08:00"
window_start: "2026-10-08T00:00:00+00:00"
window_end: "2026-10-14T23:59:59+00:00"
fetch_status: OK
run_date: 2026-10-15
data_date: 2026-10-14
item_count: 3
window_1d: 2026-10-14
window_7d: 2026-10-08~2026-10-14
window_30d: 2026-09-15~2026-10-14
as_of: "2026-10-15T00:13:16.204Z"
---

# OpenRouter 平台 token 跟踪 2026-10-14

抓取时间：2026-10-15 08:13:15 北京时间

### 1. token 总消费
| 指标 | 当前值 | 环比 | 历史提示 |
|---|---:|---:|---|
| 1日 | 26.37T | 0.6% | 正常区间（30%分位 -2.8%） |
| 7日 | 178.27T | 7.6% | 正常区间（30%分位 1.2%） |
| 30日 | 673.85T | 41.2% | 正常区间（30%分位 17.9%） |

### 2. 模型 Top 5（最近7日）
| 排名 | 模型 | Token | 占比 |
|---:|---|---:|---:|
| 1 | deepseek/deepseek-v4.1-flash-20260910 | 37.43T | 21.0% |
| 2 | stepfun/step-5-preview-20261008 | 18.79T | 10.5% |
| 3 | z-ai/glm-5.3-flash-20260826 | 12.94T | 7.3% |
| 4 | xiaomi/mimo-v2.6-flash-20260921 | 11.46T | 6.4% |
| 5 | tencent/hy4-preview-20260827 | 7.84T | 4.4% |

### 3. Provider Top 5（最近7日）
| 排名 | Provider | Token | 占比 |
|---:|---|---:|---:|
| 1 | deepseek | 47.17T | 26.5% |
| 2 | stepfun | 18.79T | 10.5% |
| 3 | z-ai | 18.58T | 10.4% |
| 4 | openai | 13.57T | 7.6% |
| 5 | xiaomi | 13.56T | 7.6% |

### 4. 用途结构（最近7日）
| 排名 | 用途 | 数据 | 占比 |
|---:|---|---:|---:|
| 1 | Code | 约 59.01T | 33.1% |
| 2 | Agent | 约 58.47T | 32.8% |
| 3 | General | 约 48.49T | 27.2% |
| 4 | Data | 约 12.30T | 6.9% |
| 1 | Workflow Execution（细分） | 约 39.22T | 22.0% |
| 2 | Code Generation（细分） | 约 20.14T | 11.3% |
| 3 | Multi-step Planning（细分） | 约 13.37T | 7.5% |
| 4 | Classification（细分） | 约 12.30T | 6.9% |
| 5 | Debugging（细分） | 约 11.05T | 6.2% |

简评：30D 仍处于高增速区间，但7D增速明显低于30D，短期更像高位盘整；用途上 Code+Agent 仍是主导。
口径：rankings-daily 为 OpenRouter 公共聚合数据，token=prompt+completion；用途结构只公开 share，表中用途 token 为按7D总量折算的近似值。私有/ZDR/隐藏流量不含在内。
Source: OpenRouter (openrouter.ai/rankings), as of 2026-10-15T00:13:16.204Z. Licensed under CC BY 4.0.
本地历史：/workspace/semiconductor-data-tracker/openrouter_platform_usage_history.csv
