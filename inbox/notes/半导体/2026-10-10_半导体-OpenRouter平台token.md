---
src_code: OR
src_type: 其他数据表
src_layer: 事实层
src_name: OpenRouter平台token跟踪
src_schema: 2
published_at: "2026-10-10T08:13:03+08:00"
window_start: "2026-10-03T00:00:00+00:00"
window_end: "2026-10-09T23:59:59+00:00"
fetch_status: OK
run_date: 2026-10-10
data_date: 2026-10-09
item_count: 3
window_1d: 2026-10-09
window_7d: 2026-10-03~2026-10-09
window_30d: 2026-09-10~2026-10-09
as_of: "2026-10-10T00:13:03.959Z"
---

# OpenRouter 平台 token 跟踪 2026-10-09

抓取时间：2026-10-10 08:13:03 北京时间

### 1. token 总消费
| 指标 | 当前值 | 环比 | 历史提示 |
|---|---:|---:|---|
| 1日 | 26.64T | 8.9% | 高于历史70%分位（4.5%） |
| 7日 | 169.30T | 5.1% | 正常区间（30%分位 1.2%） |
| 30日 | 635.51T | 43.6% | 正常区间（30%分位 17.5%） |

### 2. 模型 Top 5（最近7日）
| 排名 | 模型 | Token | 占比 |
|---:|---|---:|---:|
| 1 | deepseek/deepseek-v4.1-flash-20260910 | 37.60T | 22.2% |
| 2 | stealth/space-bunny-alpha | 16.95T | 10.0% |
| 3 | z-ai/glm-5.3-flash-20260826 | 11.20T | 6.6% |
| 4 | xiaomi/mimo-v2.6-flash-20260921 | 10.93T | 6.5% |
| 5 | tencent/hy4-preview-20260827 | 7.96T | 4.7% |

### 3. Provider Top 5（最近7日）
| 排名 | Provider | Token | 占比 |
|---:|---|---:|---:|
| 1 | deepseek | 47.87T | 28.3% |
| 2 | stealth | 16.95T | 10.0% |
| 3 | z-ai | 16.25T | 9.6% |
| 4 | openai | 14.57T | 8.6% |
| 5 | xiaomi | 12.95T | 7.6% |

### 4. 用途结构（最近7日）
| 排名 | 用途 | 数据 | 占比 |
|---:|---|---:|---:|
| 1 | Code | 约 60.95T | 36.0% |
| 2 | Agent | 约 56.88T | 33.6% |
| 3 | General | 约 40.12T | 23.7% |
| 4 | Data | 约 11.34T | 6.7% |
| 1 | Workflow Execution（细分） | 约 38.43T | 22.7% |
| 2 | Code Generation（细分） | 约 21.16T | 12.5% |
| 3 | Multi-step Planning（细分） | 约 13.04T | 7.7% |
| 4 | Classification（细分） | 约 12.19T | 7.2% |
| 5 | Debugging（细分） | 约 11.51T | 6.8% |

简评：30D 仍处于高增速区间，但7D增速明显低于30D，短期更像高位盘整；用途上 Code+Agent 仍是主导。
口径：rankings-daily 为 OpenRouter 公共聚合数据，token=prompt+completion；用途结构只公开 share，表中用途 token 为按7D总量折算的近似值。私有/ZDR/隐藏流量不含在内。
Source: OpenRouter (openrouter.ai/rankings), as of 2026-10-10T00:13:03.959Z. Licensed under CC BY 4.0.
本地历史：/workspace/semiconductor-data-tracker/openrouter_platform_usage_history.csv
