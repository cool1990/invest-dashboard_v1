---
src_code: OR
src_type: 其他数据表
src_layer: 事实层
src_name: OpenRouter平台token跟踪
src_schema: 2
published_at: "2026-09-22T08:38:26+08:00"
window_start: "2026-09-15T00:00:00+00:00"
window_end: "2026-09-21T23:59:59+00:00"
fetch_status: OK
run_date: 2026-09-22
data_date: 2026-09-21
item_count: 3
window_1d: 2026-09-21
window_7d: 2026-09-15~2026-09-21
window_30d: 2026-08-23~2026-09-21
as_of: "2026-09-22T00:38:27.085Z"
---

# OpenRouter 平台 token 跟踪 2026-09-21

抓取时间：2026-09-22 08:38:26 北京时间

### 1. token 总消费
| 指标 | 当前值 | 环比 | 历史提示 |
|---|---:|---:|---|
| 1日 | 20.84T | 20.2% | 高于历史70%分位（4.5%） |
| 7日 | 131.61T | 4.6% | 正常区间（30%分位 1.1%） |
| 30日 | 520.10T | 71.7% | 高于历史70%分位（46.5%） |

### 2. 模型 Top 5（最近7日）
| 排名 | 模型 | Token | 占比 |
|---:|---|---:|---:|
| 1 | deepseek/deepseek-v4.1-flash-20260910 | 16.92T | 12.9% |
| 2 | z-ai/glm-5.3-flash-20260826 | 16.86T | 12.8% |
| 3 | tencent/hy4-preview-20260827 | 12.68T | 9.6% |
| 4 | deepseek/deepseek-v4-flash-20260731 | 8.91T | 6.8% |
| 5 | openai/gpt-5.6-luna-20260709 | 8.48T | 6.4% |

### 3. Provider Top 5（最近7日）
| 排名 | Provider | Token | 占比 |
|---:|---|---:|---:|
| 1 | deepseek | 33.11T | 25.2% |
| 2 | z-ai | 21.77T | 16.5% |
| 3 | tencent | 17.18T | 13.1% |
| 4 | openai | 13.78T | 10.5% |
| 5 | xiaomi | 6.94T | 5.3% |

### 4. 用途结构（最近7日）
| 排名 | 用途 | 数据 | 占比 |
|---:|---|---:|---:|
| 1 | Code | 约 47.64T | 36.2% |
| 2 | Agent | 约 46.99T | 35.7% |
| 3 | General | 约 28.82T | 21.9% |
| 4 | Data | 约 8.16T | 6.2% |
| 1 | Workflow Execution（细分） | 约 32.24T | 24.5% |
| 2 | Code Generation（细分） | 约 16.06T | 12.2% |
| 3 | Multi-step Planning（细分） | 约 10.00T | 7.6% |
| 4 | Debugging（细分） | 约 8.95T | 6.8% |
| 5 | Classification（细分） | 约 7.77T | 5.9% |

简评：30D 仍处于高增速区间，但7D增速明显低于30D，短期更像高位盘整；用途上 Code+Agent 仍是主导。
口径：rankings-daily 为 OpenRouter 公共聚合数据，token=prompt+completion；用途结构只公开 share，表中用途 token 为按7D总量折算的近似值。私有/ZDR/隐藏流量不含在内。
Source: OpenRouter (openrouter.ai/rankings), as of 2026-09-22T00:38:27.085Z. Licensed under CC BY 4.0.
本地历史：/workspace/semiconductor-data-tracker/openrouter_platform_usage_history.csv
