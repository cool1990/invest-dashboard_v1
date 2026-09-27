---
src_code: OR
src_type: 其他数据表
src_layer: 事实层
src_name: OpenRouter平台token跟踪
src_schema: 2
published_at: "2026-09-25T08:05:15+08:00"
window_start: "2026-09-18T00:00:00+00:00"
window_end: "2026-09-24T23:59:59+00:00"
fetch_status: OK
run_date: 2026-09-25
data_date: 2026-09-24
item_count: 3
window_1d: 2026-09-24
window_7d: 2026-09-18~2026-09-24
window_30d: 2026-08-26~2026-09-24
as_of: "2026-09-25T00:05:16.830Z"
---

# OpenRouter 平台 token 跟踪 2026-09-24

抓取时间：2026-09-25 08:05:15 北京时间

### 1. token 总消费
| 指标 | 当前值 | 环比 | 历史提示 |
|---|---:|---:|---|
| 1日 | 21.88T | 10.3% | 高于历史70%分位（4.5%） |
| 7日 | 137.69T | 9.5% | 正常区间（30%分位 1.1%） |
| 30日 | 530.01T | 59.8% | 高于历史70%分位（47.1%） |

### 2. 模型 Top 5（最近7日）
| 排名 | 模型 | Token | 占比 |
|---:|---|---:|---:|
| 1 | z-ai/glm-5.3-flash-20260826 | 19.03T | 13.8% |
| 2 | deepseek/deepseek-v4.1-flash-20260910 | 18.91T | 13.7% |
| 3 | tencent/hy4-preview-20260827 | 12.35T | 9.0% |
| 4 | openai/gpt-5.6-luna-20260709 | 8.70T | 6.3% |
| 5 | deepseek/deepseek-v4-flash-20260731 | 8.30T | 6.0% |

### 3. Provider Top 5（最近7日）
| 排名 | Provider | Token | 占比 |
|---:|---|---:|---:|
| 1 | deepseek | 33.87T | 24.6% |
| 2 | z-ai | 24.05T | 17.5% |
| 3 | tencent | 15.91T | 11.6% |
| 4 | openai | 14.27T | 10.4% |
| 5 | xiaomi | 7.32T | 5.3% |

### 4. 用途结构（最近7日）
| 排名 | 用途 | 数据 | 占比 |
|---:|---|---:|---:|
| 1 | Code | 约 49.98T | 36.3% |
| 2 | Agent | 约 49.43T | 35.9% |
| 3 | General | 约 29.88T | 21.7% |
| 4 | Data | 约 8.40T | 6.1% |
| 1 | Workflow Execution（细分） | 约 33.73T | 24.5% |
| 2 | Code Generation（细分） | 约 17.07T | 12.4% |
| 3 | Multi-step Planning（细分） | 约 11.01T | 8.0% |
| 4 | Debugging（细分） | 约 9.23T | 6.7% |
| 5 | Classification（细分） | 约 8.40T | 6.1% |

简评：30D 仍处于高增速区间，但7D增速明显低于30D，短期更像高位盘整；用途上 Code+Agent 仍是主导。
口径：rankings-daily 为 OpenRouter 公共聚合数据，token=prompt+completion；用途结构只公开 share，表中用途 token 为按7D总量折算的近似值。私有/ZDR/隐藏流量不含在内。
Source: OpenRouter (openrouter.ai/rankings), as of 2026-09-25T00:05:16.830Z. Licensed under CC BY 4.0.
本地历史：/workspace/semiconductor-data-tracker/openrouter_platform_usage_history.csv
