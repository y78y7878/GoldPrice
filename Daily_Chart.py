import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

file_path = "xauusd_d.csv"

df = pd.read_csv(file_path)
df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values("Date")
df = df.set_index("Date")

plt.figure(figsize=(15, 7))

plt.plot(
    df.index,
    df["Close"],
    label="XAUUSD Close"
)

plt.title("XAUUSD Daily Price")

plt.xlabel("Date")
plt.ylabel("Price (USD)")

plt.legend()
plt.grid()

plt.tight_layout()

plt.show()