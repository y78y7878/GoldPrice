import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

file_path = "xauusd_d.csv"

df = pd.read_csv(file_path)
df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values("Date")
df = df.set_index("Date")

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

plt.figure(figsize=(15, 7))

plt.plot(
    df.index,
    df["Close"],
    label="Close"
)

plt.plot(
    df.index,
    df["BB_Middle"],
    label="Middle"
)

plt.plot(
    df.index,
    df["BB_Upper"],
    label="Upper"
)

plt.plot(
    df.index,
    df["BB_Lower"],
    label="Lower"
)

plt.fill_between(
    df.index,
    df["BB_Lower"],
    df["BB_Upper"],
    alpha=0.1
)

plt.title("XAUUSD Bollinger Bands")
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()