# 黃金價格分析專題

以 XAUUSD 黃金價格為核心，結合基本面與技術面資料，整理 2021 至 2026 年的市場變化，並提供互動式圖表與研究觀察。

**線上網站：**[黃金價格分析專題 · Streamlit](https://goldprice-analysis.streamlit.app/)

## 網站內容

- **首頁**：介紹研究範圍與分析主題。
- **基本面分析**：依年份檢視黃金收盤價、美元指數、全球央行黃金儲備、聯邦基金利率（DFF）與 CPI 資料及年度分析。
- **技術面分析**：選擇日期區間與均線、布林通道、支撐／阻力位、KD、MACD 等指標，查看 XAUUSD 價格走勢。
- **價格預測與展望**：整理不同期間報酬率、技術支撐與阻力觀察、基本面因素及情境展望；內容為研究整理，不代表投資建議或未來保證。
- **製作過程**：瀏覽資料爬蟲、各類圖表及 Streamlit 網頁的 Python 程式碼。
- **專題結論**：總結資料分析與網站內容。

## 資料

主要資料檔需放在 `Chart_Streamlit.py` 同一層目錄：

- `xauusd_d.csv`：XAUUSD 日線 OHLC 價格，欄位為 `Date`、`Open`、`High`、`Low`、`Close`。
- `2021-09-01~2026-08-31美元指數.csv`：美元指數價格資料。
- `2021-09~2026-05全球央行黃金儲備.csv`：全球央行黃金儲備資料。
- `DFF.csv`：聯邦基金有效利率。
- `MEDCPIM158SFRBCLE.csv`：CPI 資料。

若本地的 DFF 或 CPI CSV 沒有有效資料，網站會嘗試從 FRED 讀取；這項備援需要網路連線。XAUUSD、美元指數及央行黃金儲備資料則使用上述本地 CSV。

## 本機執行

專案要求 Python 3.14 或更新版本。於專案根目錄安裝專案及其依賴，再啟動 Streamlit：

```bash
python -m pip install -e .
streamlit run Chart_Streamlit.py
```

啟動後，Streamlit 會在終端機顯示本機網址。
