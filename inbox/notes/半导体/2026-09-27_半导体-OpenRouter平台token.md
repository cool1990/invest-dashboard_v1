---
src_code: OR
src_type: 其他数据表
src_layer: 事实层
src_name: OpenRouter平台token跟踪
src_schema: 2
published_at: "2026-09-27T08:48:52+08:00"
window_start: "2026-09-20T00:00:00+00:00"
window_end: "2026-09-26T23:59:59+00:00"
fetch_status: OK
run_date: 2026-09-27
data_date: 2026-09-26
item_count: 3
window_1d: 2026-09-26
window_7d: 2026-09-20~2026-09-26
window_30d: 2026-08-28~2026-09-26
as_of: "2026-09-27T00:48:53.660Z"
---

# OpenRouter 平台 token 跟踪 2026-09-26

抓取时间：2026-09-27 08:48:52 北京时间

### 1. token 总消费
| 指标 | 当前值 | 环比 | 历史提示 |
|---|---:|---:|---|
| 1日 | 19.86T | -11.5% | 低于历史30%分位（-2.8%） |
| 7日 | 142.65T | 11.2% | 正常区间（30%分位 1.1%） |
| 30日 | 538.07T | 54.5% | 高于历史70%分位（47.4%） |

### 2. 模型 Top 5（最近7日）
| 排名 | 模型 | Token | 占比 |
|---:|---|---:|---:|
| 1 | deepseek/deepseek-v4.1-flash-20260910 | 18.63T | 13.1% |
| 2 | z-ai/glm-5.3-flash-20260826 | 17.81T | 12.5% |
| 3 | tencent/hy4-preview-20260827 | 10.61T | 7.4% |
| 4 | stealth/space-bunny-alpha | 9.87T | 6.9% |
| 5 | openai/gpt-5.6-luna-20260709 | 8.62T | 6.0% |

### 3. Provider Top 5（最近7日）
| 排名 | Provider | Token | 占比 |
|---:|---|---:|---:|
| 1 | deepseek | 32.13T | 22.5% |
| 2 | z-ai | 22.45T | 15.7% |
| 3 | openai | 15.52T | 10.9% |
| 4 | tencent | 13.41T | 9.4% |
| 5 | stealth | 9.87T | 6.9% |

### 4. 用途结构（最近7日）
| 排名 | 用途 | 数据 | 占比 |
|---:|---|---:|---:|
| 1 | Code | 约 51.78T | 36.3% |
| 2 | Agent | 约 51.35T | 36.0% |
| 3 | General | 约 30.95T | 21.7% |
| 4 | Data | 约 8.56T | 6.0% |
| 1 | Workflow Execution（细分） | 约 34.81T | 24.4% |
| 2 | Code Generation（细分） | 约 17.40T | 12.2% |
| 3 | Multi-step Planning（细分） | 约 11.84T | 8.3% |
| 4 | Debugging（细分） | 约 9.84T | 6.9% |
| 5 | Classification（细分） | 约 9.27T | 6.5% |

简评：30D 仍处于高增速区间，但7D增速明显低于30D，短期更像高位盘整；用途上 Code+Agent 仍是主导。
口径：rankings-daily 为 OpenRouter 公共聚合数据，token=prompt+completion；用途结构只公开 share，表中用途 token 为按7D总量折算的近似值。私有/ZDR/隐藏流量不含在内。
Source: OpenRouter (openrouter.ai/rankings), as of 2026-09-27T00:48:53.660Z. Licensed under CC BY 4.0.
本地历史：/workspace/semiconductor-data-tracker/openrouter_platform_usage_history.csv
