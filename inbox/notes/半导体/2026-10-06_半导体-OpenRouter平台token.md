---
src_code: OR
src_type: 其他数据表
src_layer: 事实层
src_name: OpenRouter平台token跟踪
src_schema: 2
published_at: "2026-10-06T08:05:39+08:00"
window_start: "2026-09-29T00:00:00+00:00"
window_end: "2026-10-05T23:59:59+00:00"
fetch_status: OK
run_date: 2026-10-06
data_date: 2026-10-05
item_count: 3
window_1d: 2026-10-05
window_7d: 2026-09-29~2026-10-05
window_30d: 2026-09-06~2026-10-05
as_of: "2026-10-06T00:05:39.486Z"
---

# OpenRouter 平台 token 跟踪 2026-10-05

抓取时间：2026-10-06 08:05:39 北京时间

### 1. token 总消费
| 指标 | 当前值 | 环比 | 历史提示 |
|---|---:|---:|---|
| 1日 | 25.87T | 13.6% | 高于历史70%分位（4.5%） |
| 7日 | 167.79T | 12.7% | 正常区间（30%分位 1.2%） |
| 30日 | 607.51T | 47.8% | 正常区间（30%分位 17.4%） |

### 2. 模型 Top 5（最近7日）
| 排名 | 模型 | Token | 占比 |
|---:|---|---:|---:|
| 1 | stealth/space-bunny-alpha | 38.54T | 23.0% |
| 2 | deepseek/deepseek-v4.1-flash-20260910 | 28.39T | 16.9% |
| 3 | z-ai/glm-5.3-flash-20260826 | 10.02T | 6.0% |
| 4 | xiaomi/mimo-v2.6-flash-20260921 | 9.72T | 5.8% |
| 5 | tencent/hy4-preview-20260827 | 6.36T | 3.8% |

### 3. Provider Top 5（最近7日）
| 排名 | Provider | Token | 占比 |
|---:|---|---:|---:|
| 1 | deepseek | 39.30T | 23.4% |
| 2 | stealth | 38.54T | 23.0% |
| 3 | openai | 15.54T | 9.3% |
| 4 | z-ai | 14.38T | 8.6% |
| 5 | xiaomi | 11.97T | 7.1% |

### 4. 用途结构（最近7日）
| 排名 | 用途 | 数据 | 占比 |
|---:|---|---:|---:|
| 1 | Code | 约 59.73T | 35.6% |
| 2 | Agent | 约 59.40T | 35.4% |
| 3 | General | 约 37.92T | 22.6% |
| 4 | Data | 约 10.74T | 6.4% |
| 1 | Workflow Execution（细分） | 约 39.43T | 23.5% |
| 2 | Code Generation（细分） | 约 19.97T | 11.9% |
| 3 | Multi-step Planning（细分） | 约 13.93T | 8.3% |
| 4 | Classification（细分） | 约 12.08T | 7.2% |
| 5 | Debugging（细分） | 约 11.58T | 6.9% |

简评：30D 仍处于高增速区间，但7D增速明显低于30D，短期更像高位盘整；用途上 Code+Agent 仍是主导。
口径：rankings-daily 为 OpenRouter 公共聚合数据，token=prompt+completion；用途结构只公开 share，表中用途 token 为按7D总量折算的近似值。私有/ZDR/隐藏流量不含在内。
Source: OpenRouter (openrouter.ai/rankings), as of 2026-10-06T00:05:39.486Z. Licensed under CC BY 4.0.
本地历史：/workspace/semiconductor-data-tracker/openrouter_platform_usage_history.csv
