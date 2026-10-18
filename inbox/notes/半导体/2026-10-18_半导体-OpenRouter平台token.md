---
src_code: OR
src_type: 其他数据表
src_layer: 事实层
src_name: OpenRouter平台token跟踪
src_schema: 2
published_at: "2026-10-18T08:12:35+08:00"
window_start: "2026-10-11T00:00:00+00:00"
window_end: "2026-10-17T23:59:59+00:00"
fetch_status: OK
run_date: 2026-10-18
data_date: 2026-10-17
item_count: 3
window_1d: 2026-10-17
window_7d: 2026-10-11~2026-10-17
window_30d: 2026-09-18~2026-10-17
as_of: "2026-10-18T00:12:35.615Z"
---

# OpenRouter 平台 token 跟踪 2026-10-17

抓取时间：2026-10-18 08:12:35 北京时间

### 1. token 总消费
| 指标 | 当前值 | 环比 | 历史提示 |
|---|---:|---:|---|
| 1日 | 18.34T | -18.2% | 低于历史30%分位（-2.8%） |
| 7日 | 168.34T | -1.6% | 低于历史30%分位（1.3%） |
| 30日 | 682.93T | 37.5% | 正常区间（30%分位 18.1%） |

### 2. 模型 Top 5（最近7日）
| 排名 | 模型 | Token | 占比 |
|---:|---|---:|---:|
| 1 | deepseek/deepseek-v4.1-flash-20260910 | 35.89T | 21.3% |
| 2 | stepfun/step-5-preview-20261008 | 13.92T | 8.3% |
| 3 | z-ai/glm-5.3-flash-20260826 | 12.60T | 7.5% |
| 4 | xiaomi/mimo-v2.6-flash-20260921 | 10.34T | 6.1% |
| 5 | tencent/hy4-preview-20260827 | 7.55T | 4.5% |

### 3. Provider Top 5（最近7日）
| 排名 | Provider | Token | 占比 |
|---:|---|---:|---:|
| 1 | deepseek | 46.06T | 27.4% |
| 2 | z-ai | 18.97T | 11.3% |
| 3 | stepfun | 13.92T | 8.3% |
| 4 | xiaomi | 12.58T | 7.5% |
| 5 | anthropic | 12.27T | 7.3% |

### 4. 用途结构（最近7日）
| 排名 | 用途 | 数据 | 占比 |
|---:|---|---:|---:|
| 1 | Agent | 约 55.38T | 32.9% |
| 2 | Code | 约 53.36T | 31.7% |
| 3 | General | 约 47.81T | 28.4% |
| 4 | Data | 约 11.78T | 7.0% |
| 1 | Workflow Execution（细分） | 约 36.87T | 21.9% |
| 2 | Code Generation（细分） | 约 18.01T | 10.7% |
| 3 | Classification（细分） | 约 12.96T | 7.7% |
| 4 | Multi-step Planning（细分） | 约 12.96T | 7.7% |
| 5 | Debugging（细分） | 约 10.27T | 6.1% |

简评：30D 仍处于高增速区间，但7D增速明显低于30D，短期更像高位盘整；用途上 Code+Agent 仍是主导。
口径：rankings-daily 为 OpenRouter 公共聚合数据，token=prompt+completion；用途结构只公开 share，表中用途 token 为按7D总量折算的近似值。私有/ZDR/隐藏流量不含在内。
Source: OpenRouter (openrouter.ai/rankings), as of 2026-10-18T00:12:35.615Z. Licensed under CC BY 4.0.
本地历史：/workspace/semiconductor-data-tracker/openrouter_platform_usage_history.csv
