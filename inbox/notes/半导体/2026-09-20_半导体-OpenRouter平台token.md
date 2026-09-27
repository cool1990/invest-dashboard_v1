---
src_code: OR
src_type: 其他数据表
src_layer: 事实层
src_name: OpenRouter平台token跟踪
src_schema: 2
published_at: "2026-09-20T08:30:11+08:00"
window_start: "2026-09-13T00:00:00+00:00"
window_end: "2026-09-19T23:59:59+00:00"
fetch_status: OK
run_date: 2026-09-20
data_date: 2026-09-19
item_count: 3
window_1d: 2026-09-19
window_7d: 2026-09-13~2026-09-19
window_30d: 2026-08-21~2026-09-19
as_of: "2026-09-20T00:30:13.269Z"
---

# OpenRouter 平台 token 跟踪 2026-09-19

抓取时间：2026-09-20 08:30:11 北京时间

### 1. token 总消费
| 指标 | 当前值 | 环比 | 历史提示 |
|---|---:|---:|---|
| 1日 | 17.82T | -8.7% | 低于历史30%分位（-2.8%） |
| 7日 | 128.29T | 3.2% | 正常区间（30%分位 1.1%） |
| 30日 | 509.90T | 74.2% | 高于历史70%分位（45.8%） |

### 2. 模型 Top 5（最近7日）
| 排名 | 模型 | Token | 占比 |
|---:|---|---:|---:|
| 1 | deepseek/deepseek-v4.1-flash-20260910 | 14.57T | 11.4% |
| 2 | z-ai/glm-5.3-flash-20260826 | 12.96T | 10.1% |
| 3 | openai/gpt-5.6-luna-20260709 | 12.44T | 9.7% |
| 4 | tencent/hy4-preview-20260827 | 11.93T | 9.3% |
| 5 | deepseek/deepseek-v4-flash-20260731 | 9.77T | 7.6% |

### 3. Provider Top 5（最近7日）
| 排名 | Provider | Token | 占比 |
|---:|---|---:|---:|
| 1 | deepseek | 31.99T | 24.9% |
| 2 | openai | 17.67T | 13.8% |
| 3 | z-ai | 17.51T | 13.6% |
| 4 | tencent | 16.68T | 13.0% |
| 5 | xiaomi | 7.21T | 5.6% |

### 4. 用途结构（最近7日）
| 排名 | 用途 | 数据 | 占比 |
|---:|---|---:|---:|
| 1 | Code | 约 47.47T | 37.0% |
| 2 | Agent | 约 44.77T | 34.9% |
| 3 | General | 约 28.22T | 22.0% |
| 4 | Data | 约 7.83T | 6.1% |
| 1 | Workflow Execution（细分） | 约 31.30T | 24.4% |
| 2 | Code Generation（细分） | 约 15.52T | 12.1% |
| 3 | Debugging（细分） | 约 9.11T | 7.1% |
| 4 | Multi-step Planning（细分） | 约 8.98T | 7.0% |
| 5 | Classification（细分） | 约 7.70T | 6.0% |

简评：30D 仍处于高增速区间，但7D增速明显低于30D，短期更像高位盘整；用途上 Code+Agent 仍是主导。
口径：rankings-daily 为 OpenRouter 公共聚合数据，token=prompt+completion；用途结构只公开 share，表中用途 token 为按7D总量折算的近似值。私有/ZDR/隐藏流量不含在内。
Source: OpenRouter (openrouter.ai/rankings), as of 2026-09-20T00:30:13.269Z. Licensed under CC BY 4.0.
本地历史：/workspace/semiconductor-data-tracker/openrouter_platform_usage_history.csv
