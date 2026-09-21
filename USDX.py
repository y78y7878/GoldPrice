import yfinance as yf
from pprint import pp, pprint


ticker_symbol = "DX-Y.NYB"  # 美元指數代碼
ticker = yf.Ticker(ticker_symbol)
#pprint(ticker.history(period="3mo" , interval="1wk")) 
data = ticker.history(start="2021-09-01", end="2026-08-31")
pprint(data) # 顯示美元指數的歷史股價數據。
data.to_csv("2021-09-01~2026-08-31美元指數.csv", encoding="utf-8-sig")