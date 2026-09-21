import requests
import re
import json
import pandas as pd

url = "https://www.goldlegend.com/central-bank-gold"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)
response.raise_for_status()

html = response.text

# 找出 history
pattern = r'"history"\s*:\s*(\[\[.*?\]\])'
match = re.search(pattern, html)

if not match:
    print("找不到 history")
else:
    history = json.loads(match.group(1))

    # 建立 DataFrame
    df = pd.DataFrame(
        history,
        columns=["日期", "全球央行總持金量"]
    )

    # 日期轉成 datetime
    df["日期"] = pd.to_datetime(df["日期"])

    # 篩選 2021-09 ~ 2026-05
    df = df[
        (df["日期"] >= "2021-09-01") &
        (df["日期"] <= "2026-05-01")
    ]

    # 按日期排序
    df = df.sort_values("日期").reset_index(drop=True)

    print(df)

    # 輸出 CSV
    df.to_csv(
        "global_central_bank_gold_2021-09_2026-05.csv",
        index=False,
        encoding="utf-8-sig"
    )