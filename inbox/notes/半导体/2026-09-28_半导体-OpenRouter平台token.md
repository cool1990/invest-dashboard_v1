---
src_code: OR
src_type: 其他数据表
src_layer: 事实层
src_name: OpenRouter平台token跟踪
src_schema: 2
published_at: "2026-09-28T08:05:02+08:00"
window_start: "2026-09-21T00:00:00+00:00"
window_end: "2026-09-27T23:59:59+00:00"
fetch_status: OK
run_date: 2026-09-28
data_date: 2026-09-27
item_count: 3
window_1d: 2026-09-27
window_7d: 2026-09-21~2026-09-27
window_30d: 2026-08-29~2026-09-27
as_of: "2026-09-28T00:05:02.919Z"
---

# OpenRouter 平台 token 跟踪 2026-09-27

抓取时间：2026-09-28 08:05:02 北京时间

### 1. token 总消费
| 指标 | 当前值 | 环比 | 历史提示 |
|---|---:|---:|---|
| 1日 | 20.53T | 3.4% | 正常区间（30%分位 -2.8%） |
| 7日 | 145.84T | 13.1% | 高于历史70%分位（12.5%） |
| 30日 | 543.48T | 53.0% | 高于历史70%分位（47.4%） |

### 2. 模型 Top 5（最近7日）
| 排名 | 模型 | Token | 占比 |
|---:|---|---:|---:|
| 1 | deepseek/deepseek-v4.1-flash-20260910 | 19.58T | 13.4% |
| 2 | z-ai/glm-5.3-flash-20260826 | 16.32T | 11.2% |
| 3 | stealth/space-bunny-alpha | 13.86T | 9.5% |
| 4 | tencent/hy4-preview-20260827 | 9.64T | 6.6% |
| 5 | openai/gpt-5.6-luna-20260709 | 8.53T | 5.8% |

### 3. Provider Top 5（最近7日）
| 排名 | Provider | Token | 占比 |
|---:|---|---:|---:|
| 1 | deepseek | 32.77T | 22.5% |
| 2 | z-ai | 20.75T | 14.2% |
| 3 | openai | 16.13T | 11.1% |
| 4 | stealth | 13.86T | 9.5% |
| 5 | tencent | 12.21T | 8.4% |

### 4. 用途结构（最近7日）
| 排名 | 用途 | 数据 | 占比 |
|---:|---|---:|---:|
| 1 | Code | 约 53.52T | 36.7% |
| 2 | Agent | 约 52.21T | 35.8% |
| 3 | General | 约 31.50T | 21.6% |
| 4 | Data | 约 8.60T | 5.9% |
| 1 | Workflow Execution（细分） | 约 35.29T | 24.2% |
| 2 | Code Generation（细分） | 约 18.08T | 12.4% |
| 3 | Multi-step Planning（细分） | 约 12.11T | 8.3% |
| 4 | Debugging（细分） | 约 10.21T | 7.0% |
| 5 | Classification（细分） | 约 9.33T | 6.4% |

简评：30D 仍处于高增速区间，但7D增速明显低于30D，短期更像高位盘整；用途上 Code+Agent 仍是主导。
口径：rankings-daily 为 OpenRouter 公共聚合数据，token=prompt+completion；用途结构只公开 share，表中用途 token 为按7D总量折算的近似值。私有/ZDR/隐藏流量不含在内。
Source: OpenRouter (openrouter.ai/rankings), as of 2026-09-28T00:05:02.919Z. Licensed under CC BY 4.0.
本地历史：/workspace/semiconductor-data-tracker/openrouter_platform_usage_history.csv
