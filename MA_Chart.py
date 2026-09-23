import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

file_path = "xauusd_d.csv"

df = pd.read_csv(file_path)
df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values("Date")
df = df.set_index("Date")

df["MA20"] = df["Close"].rolling(20).mean()
df["MA60"] = df["Close"].rolling(60).mean()
df["MA120"] = df["Close"].rolling(120).mean()
df["MA240"] = df["Close"].rolling(240).mean()

plt.figure(figsize=(15, 7))

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
    df["MA120"],
    label="MA120"
)

plt.plot(
    df.index,
    df["MA240"],
    label="MA240"
)

plt.title("XAUUSD Moving Average")
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()

