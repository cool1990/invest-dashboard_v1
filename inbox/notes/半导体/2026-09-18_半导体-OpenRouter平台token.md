---
src_code: OR
src_type: 其他数据表
src_layer: 事实层
src_name: OpenRouter平台token跟踪
src_schema: 2
published_at: "2026-09-18T09:52:12+08:00"
window_start: "2026-09-11T00:00:00+00:00"
window_end: "2026-09-17T23:59:59+00:00"
fetch_status: OK
run_date: 2026-09-18
data_date: 2026-09-17
item_count: 3
window_1d: 2026-09-17
window_7d: 2026-09-11~2026-09-17
window_30d: 2026-08-19~2026-09-17
as_of: "2026-09-18T01:52:13.414Z"
---

# OpenRouter 平台 token 跟踪 2026-09-17

抓取时间：2026-09-18 09:52:12 北京时间

### 1. token 总消费
| 指标 | 当前值 | 环比 | 历史提示 |
|---|---:|---:|---|
| 1日 | 19.95T | 8.4% | 高于历史70%分位（4.5%） |
| 7日 | 125.76T | 2.1% | 正常区间（30%分位 1.0%） |
| 30日 | 496.81T | 74.2% | 高于历史70%分位（45.8%） |

### 2. 模型 Top 5（最近7日）
| 排名 | 模型 | Token | 占比 |
|---:|---|---:|---:|
| 1 | openai/gpt-5.6-luna-20260709 | 15.82T | 12.6% |
| 2 | deepseek/deepseek-v4.1-flash-20260910 | 11.84T | 9.4% |
| 3 | tencent/hy4-preview-20260827 | 11.61T | 9.2% |
| 4 | z-ai/glm-5.3-flash-20260826 | 11.41T | 9.1% |
| 5 | deepseek/deepseek-v4-flash-20260731 | 10.62T | 8.4% |

### 3. Provider Top 5（最近7日）
| 排名 | Provider | Token | 占比 |
|---:|---|---:|---:|
| 1 | deepseek | 29.46T | 23.4% |
| 2 | openai | 20.81T | 16.5% |
| 3 | tencent | 16.30T | 13.0% |
| 4 | z-ai | 15.49T | 12.3% |
| 5 | xiaomi | 7.56T | 6.0% |

### 4. 用途结构（最近7日）
| 排名 | 用途 | 数据 | 占比 |
|---:|---|---:|---:|
| 1 | Code | 约 47.16T | 37.5% |
| 2 | Agent | 约 43.51T | 34.6% |
| 3 | General | 约 27.54T | 21.9% |
| 4 | Data | 约 7.67T | 6.1% |
| 1 | Workflow Execution（细分） | 约 30.43T | 24.2% |
| 2 | Code Generation（细分） | 约 15.22T | 12.1% |
| 3 | Debugging（细分） | 约 9.18T | 7.3% |
| 4 | Multi-step Planning（细分） | 约 8.55T | 6.8% |
| 5 | Classification（细分） | 约 7.55T | 6.0% |

简评：30D 仍处于高增速区间，但7D增速明显低于30D，短期更像高位盘整；用途上 Code+Agent 仍是主导。
口径：rankings-daily 为 OpenRouter 公共聚合数据，token=prompt+completion；用途结构只公开 share，表中用途 token 为按7D总量折算的近似值。私有/ZDR/隐藏流量不含在内。
Source: OpenRouter (openrouter.ai/rankings), as of 2026-09-18T01:52:13.414Z. Licensed under CC BY 4.0.
本地历史：/workspace/semiconductor-data-tracker/openrouter_platform_usage_history.csv
