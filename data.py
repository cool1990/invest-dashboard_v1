import streamlit as st
import pandas as pd
import pandas_datareader.data as web
import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ---------------------------------------------------------
# 1. 页面配置
# ---------------------------------------------------------
st.set_page_config(page_title="US Macro Dashboard", layout="wide")
st.title("🇺🇸 美国宏观经济数据看板")
st.markdown("数据来源: **FRED (St. Louis Fed)** | 自动更新")

# ---------------------------------------------------------
# 2. 数据获取与清洗函数
# ---------------------------------------------------------
@st.cache_data(ttl=3600)  # 缓存数据1小时，避免重复请求
def load_data():
    start_date = datetime.datetime(1990, 1, 1)
    end_date = datetime.datetime.now()

    # 定义 FRED Series ID
    indicators = {
        'CPI': 'CPIAUCSL',           # 消费价格指数
        'Core CPI': 'CPILFESL',      # 核心 CPI
        'Unemployment': 'UNRATE',    # 失业率 (修正点)
        'Nonfarm': 'PAYEMS',         # 非农就业总人数
        'Fed Rate': 'FEDFUNDS'       # 联邦基金利率
    }

    # 从 FRED 获取数据
    try:
        df = web.DataReader(list(indicators.values()), 'fred', start_date, end_date)
        
        # 重命名列
        inv_map = {v: k for k, v in indicators.items()}
        df.rename(columns=inv_map, inplace=True)

        # --- 数据预处理 ---
        # 1. 计算 CPI 和 Core CPI 的同比 (YoY %)
        df['CPI YoY'] = df['CPI'].pct_change(12) * 100
        df['Core CPI YoY'] = df['Core CPI'].pct_change(12) * 100

        # 2. 计算非农就业的月度增量 (MoM Change)
        df['Nonfarm Change'] = df['Nonfarm'].diff()

        return df.dropna()
    except Exception as e:
        st.error(f"数据抓取失败: {e}")
        return pd.DataFrame()

df = load_data()

# ---------------------------------------------------------
# 3. 侧边栏：时间拖动控制器
# ---------------------------------------------------------
if not df.empty:
    st.sidebar.header("⏳ 时间范围选择")
    
    min_date = df.index.min().to_pydatetime()
    max_date = df.index.max().to_pydatetime()

    # 创建时间滑块
    start_time, end_time = st.sidebar.slider(
        "选择时间段:",
        min_value=min_date,
        max_value=max_date,
        value=(datetime.datetime(2010, 1, 1), max_date),
        format="YYYY-MM"
    )

    # 根据滑块过滤数据
    mask = (df.index >= start_time) & (df.index <= end_time)
    df_filtered = df.loc[mask]

    # ---------------------------------------------------------
    # 4. 面板绘制 (使用 Plotly 实现交互和双轴)
    # ---------------------------------------------------------
    
    # 创建 3 行 1 列的子图
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=("通胀与利率 (Inflation & Rates)", "非农就业增减 (Nonfarm Payrolls Change)", "失业率 (Unemployment Rate)"),
        row_heights=[0.4, 0.3, 0.3]
    )

    # --- 第一张图：通胀 vs 利率 ---
    # CPI YoY
    fig.add_trace(go.Scatter(x=df_filtered.index, y=df_filtered['CPI YoY'], 
                             name="CPI 同比 (%)", line=dict(color='blue', width=2)), row=1, col=1)
    # Core CPI YoY
    fig.add_trace(go.Scatter(x=df_filtered.index, y=df_filtered['Core CPI YoY'], 
                             name="核心 CPI 同比 (%)", line=dict(color='cyan', width=1, dash='dot')), row=1, col=1)
    # 联邦基金利率 (填充线下区域，突出流动性紧缩)
    fig.add_trace(go.Scatter(x=df_filtered.index, y=df_filtered['Fed Rate'], 
                             name="联邦基金利率 (%)", line=dict(color='black', width=1.5), fill='tozeroy', fillcolor='rgba(0,0,0,0.1)'), row=1, col=1)

    # --- 第二张图：非农就业 (柱状图) ---
    # 根据正负值设置颜色
    colors = ['green' if x >= 0 else 'red' for x in df_filtered['Nonfarm Change']]
    fig.add_trace(go.Bar(x=df_filtered.index, y=df_filtered['Nonfarm Change'], 
                         name="非农新增 (人)", marker_color=colors), row=2, col=1)

    # --- 第三张图：失业率 ---
    fig.add_trace(go.Scatter(x=df_filtered.index, y=df_filtered['Unemployment'], 
                             name="失业率 (%)", line=dict(color='purple', width=2)), row=3, col=1)
    # 添加 4% 的自然失业率参考线
    fig.add_hline(y=4.0, line_dash="dash", line_color="gray", annotation_text="4% 警戒线", row=3, col=1)

    # 更新布局
    fig.update_layout(height=800, hovermode="x unified", showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

    # 显示原始数据预览
    with st.expander("查看原始数据"):
        st.dataframe(df_filtered.sort_index(ascending=False))

else:
    st.warning("暂无数据，请检查网络连接。")