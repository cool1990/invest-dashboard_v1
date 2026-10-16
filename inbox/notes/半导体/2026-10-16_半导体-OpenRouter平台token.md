---
src_code: OR
src_type: 其他数据表
src_layer: 事实层
src_name: OpenRouter平台token跟踪
src_schema: 2
published_at: "2026-10-16T08:14:04+08:00"
window_start: "2026-10-09T00:00:00+00:00"
window_end: "2026-10-15T23:59:59+00:00"
fetch_status: OK
run_date: 2026-10-16
data_date: 2026-10-15
item_count: 3
window_1d: 2026-10-15
window_7d: 2026-10-09~2026-10-15
window_30d: 2026-09-16~2026-10-15
as_of: "2026-10-16T00:13:11.152Z"
---

# OpenRouter 平台 token 跟踪 2026-10-15

抓取时间：2026-10-16 08:14:04 北京时间

### 1. token 总消费
| 指标 | 当前值 | 环比 | 历史提示 |
|---|---:|---:|---|
| 1日 | 24.44T | -7.4% | 低于历史30%分位（-2.8%） |
| 7日 | 178.25T | 6.9% | 正常区间（30%分位 1.3%） |
| 30日 | 680.53T | 40.5% | 正常区间（30%分位 17.9%） |

### 2. 模型 Top 5（最近7日）
| 排名 | 模型 | Token | 占比 |
|---:|---|---:|---:|
| 1 | deepseek/deepseek-v4.1-flash-20260910 | 37.06T | 20.8% |
| 2 | stepfun/step-5-preview-20261008 | 19.48T | 10.9% |
| 3 | z-ai/glm-5.3-flash-20260826 | 12.95T | 7.3% |
| 4 | xiaomi/mimo-v2.6-flash-20260921 | 11.22T | 6.3% |
| 5 | tencent/hy4-preview-20260827 | 7.88T | 4.4% |

### 3. Provider Top 5（最近7日）
| 排名 | Provider | Token | 占比 |
|---:|---|---:|---:|
| 1 | deepseek | 46.68T | 26.2% |
| 2 | stepfun | 19.48T | 10.9% |
| 3 | z-ai | 18.86T | 10.6% |
| 4 | xiaomi | 13.38T | 7.5% |
| 5 | openai | 13.05T | 7.3% |

### 4. 用途结构（最近7日）
| 排名 | 用途 | 数据 | 占比 |
|---:|---|---:|---:|
| 1 | Code | 约 58.47T | 32.8% |
| 2 | Agent | 约 58.47T | 32.8% |
| 3 | General | 约 49.02T | 27.5% |
| 4 | Data | 约 12.30T | 6.9% |
| 1 | Workflow Execution（细分） | 约 39.21T | 22.0% |
| 2 | Code Generation（细分） | 约 19.61T | 11.0% |
| 3 | Multi-step Planning（细分） | 约 13.55T | 7.6% |
| 4 | Classification（细分） | 约 12.48T | 7.0% |
| 5 | Debugging（细分） | 约 11.05T | 6.2% |

简评：30D 仍处于高增速区间，但7D增速明显低于30D，短期更像高位盘整；用途上 Code+Agent 仍是主导。
口径：rankings-daily 为 OpenRouter 公共聚合数据，token=prompt+completion；用途结构只公开 share，表中用途 token 为按7D总量折算的近似值。私有/ZDR/隐藏流量不含在内。
Source: OpenRouter (openrouter.ai/rankings), as of 2026-10-16T00:13:11.152Z. Licensed under CC BY 4.0.
本地历史：/workspace/semiconductor-data-tracker/openrouter_platform_usage_history.csv
