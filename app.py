import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
from datetime import datetime

# --- 中文顯示設定 ---
font_path = "TaipeiSansTCBeta-Regular.ttf"

# 檢查字體是否存在，如果不存在則顯示錯誤
if not os.path.exists(font_path):
    st.error(f"錯誤：找不到中文字體檔案 '{font_path}'。請確保字體檔案位於專案根目錄下。")
    st.info("您可以從以下來源下載「台北思源黑體」：[GitHub](https://github.com/google/fonts/tree/main/ofl/taipeisanstcbeta)")
    # 停止執行以避免後續的字體設定錯誤
    st.stop()

# 載入並設定中文字體
try:
    fm.fontManager.addfont(font_path)
    plt.rcParams['font.family'] = 'Taipei Sans TC Beta'
    plt.rcParams['axes.unicode_minus'] = False # 解決負號顯示問題
except Exception as e:
    st.error(f"設定中文字體失敗：{e}。中文可能無法正常顯示。")

# --- 基本設定 ---
st.set_page_config(page_title="股票分析工具", layout="wide")
st.title("📈 股票技術分析")


# --- 主要功能 ---

def get_stock_data(ticker, start_date, end_date):
    """獲取股票數據"""
    # 防禦性程式設計：只取第一個股票代碼並去除多餘空格
    ticker_id = ticker.split(" ")[0].strip()
    if not ticker_id:
        st.error("請輸入有效的股票代碼。")
        return None

    st.info(f"正在從 Yahoo Finance 獲取 {ticker_id} 的數據...")
    # 下載原始數據
    stock_data = yf.download(ticker_id, start=start_date, end=end_date)
    
    if stock_data.empty:
        st.error("無法獲取股票數據，請檢查股票代碼是否正確或更換日期範圍。")
        return None

    # 新的關鍵修復：如果欄位是多層級索引(MultiIndex)，則將其扁平化
    if isinstance(stock_data.columns, pd.MultiIndex):
        # 對於單一股票，第一層通常是我們需要的 ('Open', 'High', etc.)
        stock_data.columns = stock_data.columns.get_level_values(0)
        # 移除可能因扁平化產生的重複欄位
        stock_data = stock_data.loc[:,~stock_data.columns.duplicated()]

    st.success("數據獲取成功！")
    return stock_data

def calculate_technical_indicators(data):
    """計算技術指標 (RSI, MACD)"""
    data.ta.rsi(append=True)
    data.ta.macd(append=True)
    return data

def plot_charts(data, ticker):
    """繪製股價與技術指標圖表"""
    st.subheader(f"{ticker} 技術分析圖表")

    # 股價圖
    fig1, ax1 = plt.subplots(figsize=(12, 6))
    ax1.plot(data.index, data['Close'], label='收盤價')
    ax1.set_title(f'{ticker} 收盤價', fontsize=16)
    ax1.set_xlabel('日期')
    ax1.set_ylabel('價格')
    ax1.legend()
    ax1.grid(True)
    st.pyplot(fig1)

    # RSI 圖
    fig2, ax2 = plt.subplots(figsize=(12, 4))
    ax2.plot(data.index, data['RSI_14'], label='RSI (14天)', color='orange')
    ax2.axhline(70, linestyle='--', color='red', label='超買 (70)')
    ax2.axhline(30, linestyle='--', color='green', label='超賣 (30)')
    ax2.set_title('相對強弱指數 (RSI)', fontsize=16)
    ax2.set_xlabel('日期')
    ax2.set_ylabel('RSI')
    ax2.legend()
    ax2.grid(True)
    st.pyplot(fig2)

    # MACD 圖
    fig3, ax3 = plt.subplots(figsize=(12, 4))
    ax3.plot(data.index, data['MACD_12_26_9'], label='MACD', color='blue')
    ax3.plot(data.index, data['MACDs_12_26_9'], label='信號線', color='red')
    ax3.bar(data.index, data['MACDh_12_26_9'], label='柱狀圖', color='grey', alpha=0.5)
    ax3.set_title('平滑異同移動平均線 (MACD)', fontsize=16)
    ax3.set_xlabel('日期')
    ax3.set_ylabel('MACD')
    ax3.legend()
    ax3.grid(True)
    st.pyplot(fig3)


# --- Streamlit UI 佈局 ---
st.sidebar.header("分析設定")
ticker_input = st.sidebar.text_input("請輸入台股代碼 (例如: 2330.TW)", "2330.TW")
start_date = st.sidebar.date_input("開始日期", datetime(2024, 1, 1))
end_date = st.sidebar.date_input("結束日期", datetime.now())

if st.sidebar.button("開始分析"):
    if ticker_input:
        # 1. 獲取數據
        stock_data = get_stock_data(ticker_input, start_date, end_date)

        if stock_data is not None:
            # 2. 計算指標
            stock_data_with_indicators = calculate_technical_indicators(stock_data)

            # 3. 繪製圖表
            plot_charts(stock_data_with_indicators, ticker_input)

    else:
        st.sidebar.warning("請輸入股票代碼。")

st.sidebar.info("這是一個使用技術指標進行股票分析的範例專案。所有分析僅供參考，不構成任何投資建議。")
