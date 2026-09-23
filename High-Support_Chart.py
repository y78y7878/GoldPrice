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

df["Resistance"] = df["High"].where(
    df["High"]
    ==
    df["High"].rolling(
        window,
        center=True
    ).max()
)

df["Support"] = df["Low"].where(
    df["Low"]
    ==
    df["Low"].rolling(
        window,
        center=True
    ).min()
)


plt.figure(figsize=(15, 7))
plt.plot(
    df.index,
    df["Close"],
    label="Close"
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
    "XAUUSD Support & Resistance"
)

plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()