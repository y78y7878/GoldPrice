import pandas as pd
import matplotlib.pyplot as plt


file_path = "xauusd_d.csv"

def load_data() -> pd.DataFrame:
    df = pd.read_csv(file_path)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").set_index("Date")
    for column in ["Open", "High", "Low", "Close"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    return df.dropna(subset=["Open", "High", "Low", "Close"])


def add_macd(data: pd.DataFrame) -> pd.DataFrame:
    result = data.copy()
    ema_12 = result["Close"].ewm(span=12, adjust=False).mean()
    ema_26 = result["Close"].ewm(span=26, adjust=False).mean()
    result["MACD"] = ema_12 - ema_26
    result["Signal"] = result["MACD"].ewm(span=9, adjust=False).mean()
    result["Histogram"] = result["MACD"] - result["Signal"]
    return result


def draw_macd_chart() -> None:
    data = add_macd(load_data())
    x_values = list(range(len(data)))
    figure, (price_axis, macd_axis) = plt.subplots(
        2,
        1,
        figsize=(15, 8),
        sharex=True,
        gridspec_kw={"height_ratios": [3, 1]},
    )

    price_axis.plot(x_values, data["Close"], label="Close", color="#1f4e79")
    price_axis.set_title("XAUUSD MACD")
    price_axis.set_ylabel("Price (USD)")
    price_axis.grid(alpha=0.25)
    price_axis.legend(loc="upper left")

    macd_axis.plot(x_values, data["MACD"], label="MACD", color="#d35400", linewidth=1.5)
    macd_axis.plot(x_values, data["Signal"], label="Signal", color="#2980b9", linewidth=1.2)
    macd_axis.axhline(0, color="#7f8c8d", linestyle="--", linewidth=0.8)
    macd_axis.bar(
        x_values,
        data["Histogram"],
        width=0.8,
        color=["#16a085" if value >= 0 else "#e05d44" for value in data["Histogram"]],
        alpha=0.75,
    )
    macd_axis.set_ylabel("MACD")
    macd_axis.set_xlabel("Date")
    macd_axis.grid(alpha=0.25)
    macd_axis.legend(loc="upper left")

    step = max(1, len(data) // 10)
    positions = list(range(0, len(data), step))
    macd_axis.set_xticks(positions)
    macd_axis.set_xticklabels(
        [data.index[position].strftime("%Y-%m-%d") for position in positions],
        rotation=30,
        ha="right",
    )

    figure.tight_layout()
    plt.show()


if __name__ == "__main__":
    draw_macd_chart()
