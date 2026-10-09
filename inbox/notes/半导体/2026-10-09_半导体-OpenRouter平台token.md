---
src_code: OR
src_type: 其他数据表
src_layer: 事实层
src_name: OpenRouter平台token跟踪
src_schema: 2
published_at: "2026-10-09T08:05:26+08:00"
window_start: "2026-10-02T00:00:00+00:00"
window_end: "2026-10-08T23:59:59+00:00"
fetch_status: OK
run_date: 2026-10-09
data_date: 2026-10-08
item_count: 3
window_1d: 2026-10-08
window_7d: 2026-10-02~2026-10-08
window_30d: 2026-09-09~2026-10-08
as_of: "2026-10-09T00:05:27.214Z"
---

# OpenRouter 平台 token 跟踪 2026-10-08

抓取时间：2026-10-09 08:05:26 北京时间

### 1. token 总消费
| 指标 | 当前值 | 环比 | 历史提示 |
|---|---:|---:|---|
| 1日 | 24.45T | -2.7% | 正常区间（30%分位 -2.8%） |
| 7日 | 166.72T | 4.5% | 正常区间（30%分位 1.2%） |
| 30日 | 626.82T | 44.0% | 正常区间（30%分位 17.4%） |

### 2. 模型 Top 5（最近7日）
| 排名 | 模型 | Token | 占比 |
|---:|---|---:|---:|
| 1 | deepseek/deepseek-v4.1-flash-20260910 | 35.59T | 21.3% |
| 2 | stealth/space-bunny-alpha | 22.84T | 13.7% |
| 3 | z-ai/glm-5.3-flash-20260826 | 10.84T | 6.5% |
| 4 | xiaomi/mimo-v2.6-flash-20260921 | 10.51T | 6.3% |
| 5 | tencent/hy4-preview-20260827 | 7.36T | 4.4% |

### 3. Provider Top 5（最近7日）
| 排名 | Provider | Token | 占比 |
|---:|---|---:|---:|
| 1 | deepseek | 46.05T | 27.6% |
| 2 | stealth | 22.84T | 13.7% |
| 3 | z-ai | 15.80T | 9.5% |
| 4 | openai | 14.62T | 8.8% |
| 5 | xiaomi | 12.55T | 7.5% |

### 4. 用途结构（最近7日）
| 排名 | 用途 | 数据 | 占比 |
|---:|---|---:|---:|
| 1 | Code | 约 60.52T | 36.3% |
| 2 | Agent | 约 56.68T | 34.0% |
| 3 | General | 约 38.51T | 23.1% |
| 4 | Data | 约 11.00T | 6.6% |
| 1 | Workflow Execution（细分） | 约 38.18T | 22.9% |
| 2 | Code Generation（细分） | 约 21.01T | 12.6% |
| 3 | Multi-step Planning（细分） | 约 13.17T | 7.9% |
| 4 | Classification（细分） | 约 12.00T | 7.2% |
| 5 | Debugging（细分） | 约 11.50T | 6.9% |

简评：30D 仍处于高增速区间，但7D增速明显低于30D，短期更像高位盘整；用途上 Code+Agent 仍是主导。
口径：rankings-daily 为 OpenRouter 公共聚合数据，token=prompt+completion；用途结构只公开 share，表中用途 token 为按7D总量折算的近似值。私有/ZDR/隐藏流量不含在内。
Source: OpenRouter (openrouter.ai/rankings), as of 2026-10-09T00:05:27.214Z. Licensed under CC BY 4.0.
本地历史：/workspace/semiconductor-data-tracker/openrouter_platform_usage_history.csv
