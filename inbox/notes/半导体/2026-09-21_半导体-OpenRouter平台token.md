---
src_code: OR
src_type: 其他数据表
src_layer: 事实层
src_name: OpenRouter平台token跟踪
src_schema: 2
published_at: "2026-09-21T08:30:56+08:00"
window_start: "2026-09-14T00:00:00+00:00"
window_end: "2026-09-20T23:59:59+00:00"
fetch_status: OK
run_date: 2026-09-21
data_date: 2026-09-20
item_count: 3
window_1d: 2026-09-20
window_7d: 2026-09-14~2026-09-20
window_30d: 2026-08-22~2026-09-20
as_of: "2026-09-21T00:30:57.163Z"
---

# OpenRouter 平台 token 跟踪 2026-09-20

抓取时间：2026-09-21 08:30:56 北京时间

### 1. token 总消费
| 指标 | 当前值 | 环比 | 历史提示 |
|---|---:|---:|---|
| 1日 | 17.33T | -2.8% | 正常区间（30%分位 -2.8%） |
| 7日 | 128.90T | 1.7% | 正常区间（30%分位 1.1%） |
| 30日 | 513.34T | 72.5% | 高于历史70%分位（46.1%） |

### 2. 模型 Top 5（最近7日）
| 排名 | 模型 | Token | 占比 |
|---:|---|---:|---:|
| 1 | deepseek/deepseek-v4.1-flash-20260910 | 15.77T | 12.2% |
| 2 | z-ai/glm-5.3-flash-20260826 | 14.07T | 10.9% |
| 3 | tencent/hy4-preview-20260827 | 12.52T | 9.7% |
| 4 | openai/gpt-5.6-luna-20260709 | 9.72T | 7.5% |
| 5 | deepseek/deepseek-v4-flash-20260731 | 9.44T | 7.3% |

### 3. Provider Top 5（最近7日）
| 排名 | Provider | Token | 占比 |
|---:|---|---:|---:|
| 1 | deepseek | 32.70T | 25.4% |
| 2 | z-ai | 18.74T | 14.5% |
| 3 | tencent | 17.30T | 13.4% |
| 4 | openai | 15.01T | 11.6% |
| 5 | xiaomi | 7.11T | 5.5% |

### 4. 用途结构（最近7日）
| 排名 | 用途 | 数据 | 占比 |
|---:|---|---:|---:|
| 1 | Code | 约 46.66T | 36.2% |
| 2 | Agent | 约 45.50T | 35.3% |
| 3 | General | 约 28.61T | 22.2% |
| 4 | Data | 约 8.12T | 6.3% |
| 1 | Workflow Execution（细分） | 约 31.58T | 24.5% |
| 2 | Code Generation（细分） | 约 15.34T | 11.9% |
| 3 | Multi-step Planning（细分） | 约 9.28T | 7.2% |
| 4 | Debugging（细分） | 约 8.89T | 6.9% |
| 5 | Classification（细分） | 约 7.73T | 6.0% |

简评：30D 仍处于高增速区间，但7D增速明显低于30D，短期更像高位盘整；用途上 Code+Agent 仍是主导。
口径：rankings-daily 为 OpenRouter 公共聚合数据，token=prompt+completion；用途结构只公开 share，表中用途 token 为按7D总量折算的近似值。私有/ZDR/隐藏流量不含在内。
Source: OpenRouter (openrouter.ai/rankings), as of 2026-09-21T00:30:57.163Z. Licensed under CC BY 4.0.
本地历史：/workspace/semiconductor-data-tracker/openrouter_platform_usage_history.csv
