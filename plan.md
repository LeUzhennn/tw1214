# AI 股票分析 Streamlit 專案計畫

本計畫旨在根據 `need.md` 的核心邏輯，建立一個使用 Streamlit 進行股票分析的應用程式。

## 任務清單

1.  **[X] 初始化專案架構**
    *   [X] 建立 `requirements.txt`，包含 `streamlit`, `yfinance`, `pandas`, `google-generativeai`, `matplotlib`, `pandas-ta`
    *   [X] 建立 `.gitignore` 檔案
    *   [X] 建立主應用程式檔案 `app.py`

2.  **[X] 開發 Streamlit 應用程式 (`app.py`)**
    *   [X] 建立使用者介面 (UI)：標題、股票代碼輸入框、分析按鈕。
    *   [X] 實作股票數據獲取功能：使用 `yfinance` 根據使用者輸入的代碼抓取歷史數據。
    *   [X] 實作技術指標計算：使用 `pandas-ta` 計算 RSI 和 MACD。
    *   [X] 實作數據可視化：使用 `matplotlib` 或 `plotly` 繪製股價與技術指標圖表。
    *   [X] 串接 Gemini AI 進行分析：
        *   [X] 建立一個函式，將股票數據和技術指標整理成 Prompt。
        *   [X] 發送請求至 Gemini API。
        *   [X] 在介面上顯示 AI 生成的分析報告。
    *   [X] 處理 API Key：引導使用者設定環境變數 `GEMINI_API_KEY`。
    *   **[X] 修正中文顯示問題：加入 `matplotlib` 中文字體設定與下載邏輯。**

3.  **[ ] 完成與測試**
    *   [X] 撰寫完整程式碼。
    *   [ ] 提供執行說，指導使用者如何啟動應用程式。
    *   [ ] 進行最終測試，確保所有功能正常。
