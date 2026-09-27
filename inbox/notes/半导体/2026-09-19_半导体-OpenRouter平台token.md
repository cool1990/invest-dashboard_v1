---
src_code: OR
src_type: 其他数据表
src_layer: 事实层
src_name: OpenRouter平台token跟踪
src_schema: 2
published_at: "2026-09-19T08:30:36+08:00"
window_start: "2026-09-12T00:00:00+00:00"
window_end: "2026-09-18T23:59:59+00:00"
fetch_status: OK
run_date: 2026-09-19
data_date: 2026-09-18
item_count: 3
window_1d: 2026-09-18
window_7d: 2026-09-12~2026-09-18
window_30d: 2026-08-20~2026-09-18
as_of: "2026-09-19T00:30:36.642Z"
---

# OpenRouter 平台 token 跟踪 2026-09-18

抓取时间：2026-09-19 08:30:36 北京时间

### 1. token 总消费
| 指标 | 当前值 | 环比 | 历史提示 |
|---|---:|---:|---|
| 1日 | 19.52T | -2.2% | 正常区间（30%分位 -2.8%） |
| 7日 | 127.52T | 4.0% | 正常区间（30%分位 1.0%） |
| 30日 | 504.21T | 74.5% | 高于历史70%分位（45.8%） |

### 2. 模型 Top 5（最近7日）
| 排名 | 模型 | Token | 占比 |
|---:|---|---:|---:|
| 1 | openai/gpt-5.6-luna-20260709 | 15.20T | 11.9% |
| 2 | deepseek/deepseek-v4.1-flash-20260910 | 12.93T | 10.1% |
| 3 | tencent/hy4-preview-20260827 | 12.01T | 9.4% |
| 4 | z-ai/glm-5.3-flash-20260826 | 11.62T | 9.1% |
| 5 | deepseek/deepseek-v4-flash-20260731 | 9.90T | 7.8% |

### 3. Provider Top 5（最近7日）
| 排名 | Provider | Token | 占比 |
|---:|---|---:|---:|
| 1 | deepseek | 30.26T | 23.7% |
| 2 | openai | 20.37T | 16.0% |
| 3 | tencent | 16.75T | 13.1% |
| 4 | z-ai | 16.00T | 12.5% |
| 5 | xiaomi | 7.33T | 5.7% |

### 4. 用途结构（最近7日）
| 排名 | 用途 | 数据 | 占比 |
|---:|---|---:|---:|
| 1 | Code | 约 47.69T | 37.4% |
| 2 | Agent | 约 44.38T | 34.8% |
| 3 | General | 约 27.80T | 21.8% |
| 4 | Data | 约 7.65T | 6.0% |
| 1 | Workflow Execution（细分） | 约 31.12T | 24.4% |
| 2 | Code Generation（细分） | 约 15.56T | 12.2% |
| 3 | Debugging（细分） | 约 9.18T | 7.2% |
| 4 | Multi-step Planning（细分） | 约 8.67T | 6.8% |
| 5 | File I/O（细分） | 约 7.65T | 6.0% |

简评：30D 仍处于高增速区间，但7D增速明显低于30D，短期更像高位盘整；用途上 Code+Agent 仍是主导。
口径：rankings-daily 为 OpenRouter 公共聚合数据，token=prompt+completion；用途结构只公开 share，表中用途 token 为按7D总量折算的近似值。私有/ZDR/隐藏流量不含在内。
Source: OpenRouter (openrouter.ai/rankings), as of 2026-09-19T00:30:36.642Z. Licensed under CC BY 4.0.
本地历史：/workspace/semiconductor-data-tracker/openrouter_platform_usage_history.csv
