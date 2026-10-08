---
src_code: OR
src_type: 其他数据表
src_layer: 事实层
src_name: OpenRouter平台token跟踪
src_schema: 2
published_at: "2026-10-08T08:05:14+08:00"
window_start: "2026-10-01T00:00:00+00:00"
window_end: "2026-10-07T23:59:59+00:00"
fetch_status: OK
run_date: 2026-10-08
data_date: 2026-10-07
item_count: 3
window_1d: 2026-10-07
window_7d: 2026-10-01~2026-10-07
window_30d: 2026-09-08~2026-10-07
as_of: "2026-10-08T00:05:15.179Z"
---

# OpenRouter 平台 token 跟踪 2026-10-07

抓取时间：2026-10-08 08:05:14 北京时间

### 1. token 总消费
| 指标 | 当前值 | 环比 | 历史提示 |
|---|---:|---:|---|
| 1日 | 25.12T | 13.6% | 高于历史70%分位（4.5%） |
| 7日 | 165.71T | 4.9% | 正常区间（30%分位 1.2%） |
| 30日 | 621.41T | 46.1% | 正常区间（30%分位 17.4%） |

### 2. 模型 Top 5（最近7日）
| 排名 | 模型 | Token | 占比 |
|---:|---|---:|---:|
| 1 | deepseek/deepseek-v4.1-flash-20260910 | 33.60T | 20.3% |
| 2 | stealth/space-bunny-alpha | 28.00T | 16.9% |
| 3 | z-ai/glm-5.3-flash-20260826 | 10.49T | 6.3% |
| 4 | xiaomi/mimo-v2.6-flash-20260921 | 10.10T | 6.1% |
| 5 | tencent/hy4-preview-20260827 | 6.74T | 4.1% |

### 3. Provider Top 5（最近7日）
| 排名 | Provider | Token | 占比 |
|---:|---|---:|---:|
| 1 | deepseek | 44.26T | 26.7% |
| 2 | stealth | 28.00T | 16.9% |
| 3 | z-ai | 15.24T | 9.2% |
| 4 | openai | 15.00T | 9.1% |
| 5 | xiaomi | 12.20T | 7.4% |

### 4. 用途结构（最近7日）
| 排名 | 用途 | 数据 | 占比 |
|---:|---|---:|---:|
| 1 | Code | 约 60.15T | 36.3% |
| 2 | Agent | 约 57.50T | 34.7% |
| 3 | General | 约 37.62T | 22.7% |
| 4 | Data | 约 10.61T | 6.4% |
| 1 | Workflow Execution（细分） | 约 38.44T | 23.2% |
| 2 | Code Generation（细分） | 约 20.55T | 12.4% |
| 3 | Multi-step Planning（细分） | 约 13.42T | 8.1% |
| 4 | Classification（细分） | 约 11.93T | 7.2% |
| 5 | Debugging（细分） | 约 11.43T | 6.9% |

简评：30D 仍处于高增速区间，但7D增速明显低于30D，短期更像高位盘整；用途上 Code+Agent 仍是主导。
口径：rankings-daily 为 OpenRouter 公共聚合数据，token=prompt+completion；用途结构只公开 share，表中用途 token 为按7D总量折算的近似值。私有/ZDR/隐藏流量不含在内。
Source: OpenRouter (openrouter.ai/rankings), as of 2026-10-08T00:05:15.179Z. Licensed under CC BY 4.0.
本地历史：/workspace/semiconductor-data-tracker/openrouter_platform_usage_history.csv
