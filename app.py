import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import google.generativeai as genai
import os
from datetime import datetime
import requests # 新增requests for 下載字體

# --- 中文顯示設定 ---
font_path = "TaipeiSansTCBeta-Regular.ttf"
font_url = "https://drive.google.com/uc?id=1eGAsTN1HBpJAkeVM57_C7ccp7hbgSz3_&export=download"

# 檢查字體是否存在，如果不存在則下載
if not os.path.exists(font_path):
    st.info("偵測到缺少中文字體，正在下載「台北思源黑體」以正確顯示中文。")
    try:
        response = requests.get(font_url, stream=True)
        response.raise_for_status() # 檢查請求是否成功
        with open(font_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        st.success("字體下載完成！")
    except Exception as e:
        st.error(f"下載字體失敗：{e}。中文可能無法正常顯示。")

# 載入並設定中文字體
try:
    fm.fontManager.addfont(font_path)
    plt.rcParams['font.family'] = 'Taipei Sans TC Beta'
    plt.rcParams['axes.unicode_minus'] = False # 解決負號顯示問題
except Exception as e:
    st.error(f"設定中文字體失敗：{e}。中文可能無法正常顯示。")

# --- 基本設定 ---
st.set_page_config(page_title="AI 股票分析助理", layout="wide")
st.title("📈 AI 股票分析助理")


# --- Gemini API 設定 ---
# 從 Streamlit secrets 或環境變數獲取 API 金鑰
api_key_configured = False
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    api_key_configured = True
except (FileNotFoundError, KeyError):
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        api_key_configured = True

if api_key_configured:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.warning("您尚未設定 Gemini API 金鑰，AI 分析功能將被停用。")
    st.markdown("""
        若要啟用 AI 分析，請設定您的 API 金鑰。有兩種方式：
        1.  **（建議）** 在專案中建立一個 `.streamlit/secrets.toml` 檔案，並加入以下內容：
            ```toml
            GEMINI_API_KEY = "您的API金鑰"
            ```
        2.  設定名為 `GEMINI_API_KEY` 的環境變數。

        您可以從 [Google AI Studio](https://aistudio.google.com/app/apikey) 的免費方案獲取金鑰。
    """)


# --- 主要功能 (將在後續步驟中實作) ---

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


def get_ai_analysis(stock_data, ticker):
    """使用 Gemini AI 分析股票數據"""
    st.info("🤖 AI 正在分析數據，請稍候...")

    # 準備給 AI 的數據摘要
    latest_data = stock_data.iloc[-1]
    data_summary = f"""
    - **最新收盤價**: {latest_data['Close']:.2f}
    - **最新成交量**: {latest_data['Volume']:.0f}
    - **52週高點**: {stock_data['Close'].max():.2f}
    - **52週低點**: {stock_data['Close'].min():.2f}
    - **最新 RSI (14天)**: {latest_data['RSI_14']:.2f}
    - **最新 MACD**: {latest_data['MACD_12_26_9']:.2f}
    - **MACD 信號線**: {latest_data['MACDs_12_26_9']:.2f}
    """

    prompt = f"""
    您是一位專業的台股分析師。請根據以下股票數據和技術指標，為股票 {ticker} 提供一份專業、條理分明、且客觀的分析報告。

    **分析重點:**
    1.  **基本趨勢**: 根據收盤價和成交量，判斷目前的市場趨勢（多頭、空頭、盤整）。
    2.  **技術指標解讀**:
        *   **RSI**: 解釋目前的 RSI 值所代表的市場情緒（超買、超賣、中性），並評估其對未來股價的可能影響。
        *   **MACD**: 解釋 MACD 線、信號線和柱狀圖的關係（黃金交叉、死亡交叉），並判斷動能的增強或減弱。
    3.  **綜合評論與展望**: 結合以上分析，提供一個簡潔的綜合評論，並對短期內的股價走勢做出合理展望。請以中立、客觀的角度進行分析，並避免提供直接的買賣建議。

    **數據摘要:**
    {data_summary}

    請以 Markdown 格式輸出您的分析報告，包含標題和分點說明。
    """

    try:
        response = model.generate_content(prompt)
        st.success("AI 分析完成！")
        return response.text
    except Exception as e:
        st.error(f"AI 分析失敗：{e}")
        return None


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

            # 4. AI 分析 (僅當 API 金鑰已設定時)
            if api_key_configured:
                ai_report = get_ai_analysis(stock_data_with_indicators, ticker_input)
                if ai_report:
                    st.subheader("🤖 AI 投資分析報告")
                    st.markdown(ai_report)
    else:
        st.sidebar.warning("請輸入股票代碼。")

st.sidebar.info("這是一個使用 AI 進行股票分析的範例專案。所有分析僅供參考，不構成任何投資建議。")
