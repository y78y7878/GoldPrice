import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

file_path = "xauusd_d.csv"

df = pd.read_csv(file_path)
df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values("Date")
df = df.set_index("Date")

weekly = df.resample("W").agg({
    "Open": "first",
    "High": "max",
    "Low": "min",
    "Close": "last"
})

def plot_candlestick(data, title):

    fig, ax = plt.subplots(figsize=(15, 7))

    # 每根 K 線的寬度
    width = 0.6

    for i, (date, row) in enumerate(data.iterrows()):

        open_price = row["Open"]
        high_price = row["High"]
        low_price = row["Low"]
        close_price = row["Close"]

        # 最高價到最低價的影線
        ax.plot(
            [i, i],
            [low_price, high_price],
            linewidth=1
        )

        # K 線實體
        bottom = min(open_price, close_price)
        height = abs(close_price - open_price)

        # 避免 Open = Close 時看不到
        if height == 0:
            height = 0.01

        if close_price >= open_price:
            face_color = "green"
        else:
            face_color = "red"

        rect = Rectangle(
            (i - width / 2, bottom),
            width,
            height,
            facecolor=face_color,
            edgecolor="white"
        )

        ax.add_patch(rect)

    # 日期不要全部顯示
    step = max(1, len(data) // 10)

    ax.set_xticks(
        range(0, len(data), step)
    )

    ax.set_xticklabels(
        [
            data.index[i].strftime("%Y-%m-%d")
            for i in range(0, len(data), step)
        ],
        rotation=45
    )

    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.grid()

    plt.tight_layout()
    plt.show()

plot_candlestick(
    weekly.tail(100),
    "XAUUSD Weekly Candlestick"
)