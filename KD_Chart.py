import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

file_path = "xauusd_d.csv"

df = pd.read_csv(file_path)
df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values("Date")
df = df.set_index("Date")


low_9 = df["Low"].rolling(9).min()
high_9 = df["High"].rolling(9).max()


df["RSV"] = (
    (df["Close"] - low_9)
    /
    (high_9 - low_9)
) * 100


df["K"] = df["RSV"].ewm(
    alpha=1 / 3,
    adjust=False
).mean()


df["D"] = df["K"].ewm(
    alpha=1 / 3,
    adjust=False
).mean()


plt.figure(figsize=(15, 6))

plt.plot(
    df.index,
    df["K"],
    label="K"
)

plt.plot(
    df.index,
    df["D"],
    label="D"
)

plt.axhline(
    80,
    linestyle="--",
    label="80"
)

plt.axhline(
    20,
    linestyle="--",
    label="20"
)

plt.title("XAUUSD KD Indicator")
plt.xlabel("Date")
plt.ylabel("Value")
plt.ylim(0, 100)
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()