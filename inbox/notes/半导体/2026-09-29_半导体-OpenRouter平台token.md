---
src_code: OR
src_type: 其他数据表
src_layer: 事实层
src_name: OpenRouter平台token跟踪
src_schema: 2
published_at: "2026-09-29T08:05:39+08:00"
window_start: "2026-09-22T00:00:00+00:00"
window_end: "2026-09-28T23:59:59+00:00"
fetch_status: OK
run_date: 2026-09-29
data_date: 2026-09-28
item_count: 3
window_1d: 2026-09-28
window_7d: 2026-09-22~2026-09-28
window_30d: 2026-08-30~2026-09-28
as_of: "2026-09-29T00:05:39.987Z"
---

# OpenRouter 平台 token 跟踪 2026-09-28

抓取时间：2026-09-29 08:05:39 北京时间

### 1. token 总消费
| 指标 | 当前值 | 环比 | 历史提示 |
|---|---:|---:|---|
| 1日 | 23.93T | 16.6% | 高于历史70%分位（4.5%） |
| 7日 | 148.94T | 13.2% | 高于历史70%分位（12.5%） |
| 30日 | 554.21T | 53.9% | 高于历史70%分位（47.5%） |

### 2. 模型 Top 5（最近7日）
| 排名 | 模型 | Token | 占比 |
|---:|---|---:|---:|
| 1 | deepseek/deepseek-v4.1-flash-20260910 | 20.83T | 14.0% |
| 2 | stealth/space-bunny-alpha | 18.18T | 12.2% |
| 3 | z-ai/glm-5.3-flash-20260826 | 13.27T | 8.9% |
| 4 | tencent/hy4-preview-20260827 | 8.97T | 6.0% |
| 5 | openai/gpt-5.6-luna-20260709 | 8.49T | 5.7% |

### 3. Provider Top 5（最近7日）
| 排名 | Provider | Token | 占比 |
|---:|---|---:|---:|
| 1 | deepseek | 33.67T | 22.6% |
| 2 | stealth | 18.18T | 12.2% |
| 3 | z-ai | 17.56T | 11.8% |
| 4 | openai | 17.07T | 11.5% |
| 5 | tencent | 11.47T | 7.7% |

### 4. 用途结构（最近7日）
| 排名 | 用途 | 数据 | 占比 |
|---:|---|---:|---:|
| 1 | Code | 约 54.81T | 36.8% |
| 2 | Agent | 约 52.73T | 35.4% |
| 3 | General | 约 32.47T | 21.8% |
| 4 | Data | 约 8.94T | 6.0% |
| 1 | Workflow Execution（细分） | 约 35.75T | 24.0% |
| 2 | Code Generation（细分） | 约 18.02T | 12.1% |
| 3 | Multi-step Planning（细分） | 约 12.06T | 8.1% |
| 4 | Debugging（细分） | 约 10.72T | 7.2% |
| 5 | Classification（细分） | 约 9.83T | 6.6% |

简评：30D 仍处于高增速区间，但7D增速明显低于30D，短期更像高位盘整；用途上 Code+Agent 仍是主导。
口径：rankings-daily 为 OpenRouter 公共聚合数据，token=prompt+completion；用途结构只公开 share，表中用途 token 为按7D总量折算的近似值。私有/ZDR/隐藏流量不含在内。
Source: OpenRouter (openrouter.ai/rankings), as of 2026-09-29T00:05:39.987Z. Licensed under CC BY 4.0.
本地历史：/workspace/semiconductor-data-tracker/openrouter_platform_usage_history.csv
