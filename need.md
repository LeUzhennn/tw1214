2025 年末最重要的一堂 Python 課。

昨天 NeuralNine 發布了最新神作，展示了如何用 Python 打造一個「不只會說話，還會畫圖」的股票分析 Agent。這代表了 2026 年的開發標準：Generative UI (GenUI)。

這不是傳統的 Chatbot，它是能即時渲染 K 線圖、撈取財報、分析新聞的 AI 助理。以下是這套架構的極速實作筆記。

致敬原創：本架構源自 NeuralNine 的教學影片，強烈建議觀看原片：Advanced AI Stock Analysis Assistant in Python

⚡ 核心亮點：為什麼這很強？
動態介面 (GenUI)：你不用預先寫好前端圖表，AI 會根據數據自動生成 UI (Chart, Table, Dashboard)。
極速工具鏈：拋棄 pip，全面採用 Rust 編寫的 uv，環境建置快 10 倍。
Agentic Workflow：AI 自主判斷何時查股價、何時看新聞，而非死板的指令。
🛠️ 開發架構全解密 (Tech Stack)
套件管理：uv (The Future of Python Packaging)
後端框架：FastAPI (Async & High Performance)
AI 邏輯：LangChain + LangGraph
數據來源：yfinance
前端渲染：React + Thesis GenUI SDK
🚀 實作四步曲
Step 1. 極速環境建置 (使用 uv)
別再等 pip install 了，2026 標準起手式：

Bash

# 初始化專案
uv init stock-agent
cd stock-agent

# 安裝依賴 (秒殺)
uv add fastapi uvicorn pydantic-settings yfinance langchain langchain-openai langgraph python-dotenv
Step 2. 後端核心 (The Brain)
這是關鍵。我們定義「工具」，讓 Agent 自己決定怎麼用。

backend/main.py

Python

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
import yfinance as yf

app = FastAPI()

# 1. 定義工具：賦予 AI 抓取股市的能力
@tool
def get_stock_price(ticker: str):
    return yf.Ticker(ticker).history(period="1d")['Close'].iloc[-1]

@tool
def get_historical_data(ticker: str, period: str = "6mo"):
    # 回傳 JSON，讓前端 GenUI 自動渲染成 K 線圖
    return yf.Ticker(ticker).history(period=period).to_json()

tools = [get_stock_price, get_historical_data]

# 2. 初始化模型 (指向支援 GenUI 的 API)
model = ChatOpenAI(model="gpt-4o", base_url="https://api.thesis.ai/v1").bind_tools(tools)
agent_executor = create_react_agent(model, tools)

# 3. 串流 API：即時回傳思考過程與 UI 結構
@app.post("/api/chat")
async def chat(request: Request):
    data = await request.json()
    async def generator():
        async for chunk in agent_executor.astream_events(
            {"messages": [("user", data.get("prompt"))]}, version="v1"
        ):
            yield chunk
    return StreamingResponse(generator(), media_type="text/event-stream")
Step 3. 前端介面 (Zero-Design UI)
後端工程師福音：不用寫 CSS。直接用 GenUI SDK 接管畫面。

Bash

npm create vite@latest frontend -- --template react-ts
npm install @thesis-ai/genui-sdk @crayon-ai/react-ui
frontend/src/App.tsx

TypeScript

import { C1Chat } from "@thesis-ai/genui-sdk";
import "@crayon-ai/react-ui/styles.css";

function App() {
  // 自動解析後端回傳的數據，渲染成圖表或對話
  return <C1Chat apiUrl="http://localhost:8000/api/chat" />;
}
export default App;
Step 4. 2026 佈署策略 (Dockerfile)
為了 Python 3.13+ (No-GIL) 做準備，並保持 Image 極小化。

Dockerfile

# 使用 Multi-stage build
FROM python:3.13-slim-bookworm AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
WORKDIR /app
COPY pyproject.toml .
RUN uv sync --frozen --no-cache

FROM python:3.13-slim-bookworm
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY backend /app/backend
ENV PATH="/app/.venv/bin:$PATH"
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]