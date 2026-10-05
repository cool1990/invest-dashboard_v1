---
src_code: OR
src_type: 其他数据表
src_layer: 事实层
src_name: OpenRouter平台token跟踪
src_schema: 2
published_at: "2026-10-05T08:05:38+08:00"
window_start: "2026-09-28T00:00:00+00:00"
window_end: "2026-10-04T23:59:59+00:00"
fetch_status: OK
run_date: 2026-10-05
data_date: 2026-10-04
item_count: 3
window_1d: 2026-10-04
window_7d: 2026-09-28~2026-10-04
window_30d: 2026-09-05~2026-10-04
as_of: "2026-10-05T00:05:14.660Z"
---

# OpenRouter 平台 token 跟踪 2026-10-04

抓取时间：2026-10-05 08:05:38 北京时间

### 1. token 总消费
| 指标 | 当前值 | 环比 | 历史提示 |
|---|---:|---:|---|
| 1日 | 22.78T | 2.1% | 正常区间（30%分位 -2.8%） |
| 7日 | 165.86T | 13.7% | 高于历史70%分位（12.7%） |
| 30日 | 596.98T | 46.8% | 正常区间（30%分位 17.3%） |

### 2. 模型 Top 5（最近7日）
| 排名 | 模型 | Token | 占比 |
|---:|---|---:|---:|
| 1 | stealth/space-bunny-alpha | 38.66T | 23.3% |
| 2 | deepseek/deepseek-v4.1-flash-20260910 | 25.61T | 15.4% |
| 3 | z-ai/glm-5.3-flash-20260826 | 9.73T | 5.9% |
| 4 | xiaomi/mimo-v2.6-flash-20260921 | 9.63T | 5.8% |
| 5 | tencent/hy4-preview-20260827 | 6.51T | 3.9% |

### 3. Provider Top 5（最近7日）
| 排名 | Provider | Token | 占比 |
|---:|---|---:|---:|
| 1 | stealth | 38.66T | 23.3% |
| 2 | deepseek | 36.65T | 22.1% |
| 3 | openai | 16.54T | 10.0% |
| 4 | z-ai | 14.07T | 8.5% |
| 5 | xiaomi | 11.88T | 7.2% |

### 4. 用途结构（最近7日）
| 排名 | 用途 | 数据 | 占比 |
|---:|---|---:|---:|
| 1 | Code | 约 59.38T | 35.8% |
| 2 | Agent | 约 59.21T | 35.7% |
| 3 | General | 约 36.99T | 22.3% |
| 4 | Data | 约 10.45T | 6.3% |
| 1 | Workflow Execution（细分） | 约 39.47T | 23.8% |
| 2 | Code Generation（细分） | 约 19.24T | 11.6% |
| 3 | Multi-step Planning（细分） | 约 13.93T | 8.4% |
| 4 | Classification（细分） | 约 11.94T | 7.2% |
| 5 | Debugging（细分） | 约 11.44T | 6.9% |

简评：30D 仍处于高增速区间，但7D增速明显低于30D，短期更像高位盘整；用途上 Code+Agent 仍是主导。
口径：rankings-daily 为 OpenRouter 公共聚合数据，token=prompt+completion；用途结构只公开 share，表中用途 token 为按7D总量折算的近似值。私有/ZDR/隐藏流量不含在内。
Source: OpenRouter (openrouter.ai/rankings), as of 2026-10-05T00:05:14.660Z. Licensed under CC BY 4.0.
本地历史：/workspace/semiconductor-data-tracker/openrouter_platform_usage_history.csv
