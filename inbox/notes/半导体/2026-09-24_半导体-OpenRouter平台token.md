---
src_code: OR
src_type: 其他数据表
src_layer: 事实层
src_name: OpenRouter平台token跟踪
src_schema: 2
published_at: "2026-09-24T08:05:53+08:00"
window_start: "2026-09-17T00:00:00+00:00"
window_end: "2026-09-23T23:59:59+00:00"
fetch_status: OK
run_date: 2026-09-24
data_date: 2026-09-23
item_count: 3
window_1d: 2026-09-23
window_7d: 2026-09-17~2026-09-23
window_30d: 2026-08-25~2026-09-23
as_of: "2026-09-24T00:05:53.824Z"
---

# OpenRouter 平台 token 跟踪 2026-09-23

抓取时间：2026-09-24 08:05:53 北京时间

### 1. token 总消费
| 指标 | 当前值 | 环比 | 历史提示 |
|---|---:|---:|---|
| 1日 | 19.84T | -3.0% | 低于历史30%分位（-2.8%） |
| 7日 | 135.76T | 8.6% | 正常区间（30%分位 1.1%） |
| 30日 | 526.90T | 64.5% | 高于历史70%分位（46.9%） |

### 2. 模型 Top 5（最近7日）
| 排名 | 模型 | Token | 占比 |
|---:|---|---:|---:|
| 1 | z-ai/glm-5.3-flash-20260826 | 19.04T | 14.0% |
| 2 | deepseek/deepseek-v4.1-flash-20260910 | 18.40T | 13.5% |
| 3 | tencent/hy4-preview-20260827 | 12.99T | 9.6% |
| 4 | openai/gpt-5.6-luna-20260709 | 8.74T | 6.4% |
| 5 | deepseek/deepseek-v4-flash-20260731 | 8.49T | 6.3% |

### 3. Provider Top 5（最近7日）
| 排名 | Provider | Token | 占比 |
|---:|---|---:|---:|
| 1 | deepseek | 33.68T | 24.8% |
| 2 | z-ai | 23.93T | 17.6% |
| 3 | tencent | 16.90T | 12.4% |
| 4 | openai | 14.40T | 10.6% |
| 5 | xiaomi | 6.77T | 5.0% |

### 4. 用途结构（最近7日）
| 排名 | 用途 | 数据 | 占比 |
|---:|---|---:|---:|
| 1 | Code | 约 49.14T | 36.2% |
| 2 | Agent | 约 48.60T | 35.8% |
| 3 | General | 约 29.73T | 21.9% |
| 4 | Data | 约 8.28T | 6.1% |
| 1 | Workflow Execution（细分） | 约 33.26T | 24.5% |
| 2 | Code Generation（细分） | 约 16.83T | 12.4% |
| 3 | Multi-step Planning（细分） | 约 10.59T | 7.8% |
| 4 | Debugging（细分） | 约 9.10T | 6.7% |
| 5 | Classification（细分） | 约 8.28T | 6.1% |

简评：30D 仍处于高增速区间，但7D增速明显低于30D，短期更像高位盘整；用途上 Code+Agent 仍是主导。
口径：rankings-daily 为 OpenRouter 公共聚合数据，token=prompt+completion；用途结构只公开 share，表中用途 token 为按7D总量折算的近似值。私有/ZDR/隐藏流量不含在内。
Source: OpenRouter (openrouter.ai/rankings), as of 2026-09-24T00:05:53.824Z. Licensed under CC BY 4.0.
本地历史：/workspace/semiconductor-data-tracker/openrouter_platform_usage_history.csv
