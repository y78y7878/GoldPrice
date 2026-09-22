import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

file_path = "xauusd_d.csv"

df = pd.read_csv(file_path)
df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values("Date")
df = df.set_index("Date")

window = 20

df["Support"] = df["Low"].where(
    df["Low"]
    ==
    df["Low"].rolling(
        window,
        center=True
    ).min()
)

df["Resistance"] = df["High"].where(
    df["High"]
    ==
    df["High"].rolling(
        window,
        center=True
    ).max()
)

df["MA20"] = df["Close"].rolling(20).mean()
df["MA60"] = df["Close"].rolling(60).mean()
df["MA120"] = df["Close"].rolling(120).mean()
df["MA240"] = df["Close"].rolling(240).mean()


df["BB_Middle"] = df["Close"].rolling(20).mean()
df["BB_STD"] = df["Close"].rolling(20).std()
df["BB_Upper"] = (
    df["BB_Middle"]
    +
    2 * df["BB_STD"]
)

df["BB_Lower"] = (
    df["BB_Middle"]
    -
    2 * df["BB_STD"]
)


plt.figure(figsize=(16, 8))

plt.plot(
    df.index,
    df["Close"],
    label="Close"
)

plt.plot(
    df.index,
    df["MA20"],
    label="MA20"
)

plt.plot(
    df.index,
    df["MA60"],
    label="MA60"
)

plt.plot(
    df.index,
    df["BB_Upper"],
    label="BB Upper"
)

plt.plot(
    df.index,
    df["BB_Lower"],
    label="BB Lower"
)

plt.scatter(
    df.index,
    df["Support"],
    label="Support",
    marker="o"
)

plt.scatter(
    df.index,
    df["Resistance"],
    label="Resistance",
    marker="o"
)

plt.title(
    "XAUUSD Technical Analysis"
)

plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()