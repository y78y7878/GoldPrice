from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import pandas as pd
import streamlit as st


DATA_FILE = Path(__file__).with_name("xauusd_d.csv")
REQUIRED_COLUMNS = {"Date", "Open", "High", "Low", "Close"}


@st.cache_data
def load_data() -> pd.DataFrame:
	data = pd.read_csv(DATA_FILE)
	missing_columns = REQUIRED_COLUMNS.difference(data.columns)
	if missing_columns:
		missing = ", ".join(sorted(missing_columns))
		raise ValueError(f"資料缺少必要欄位：{missing}")

	data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
	for column in ("Open", "High", "Low", "Close"):
		data[column] = pd.to_numeric(data[column], errors="coerce")

	data = data.dropna(subset=list(REQUIRED_COLUMNS)).sort_values("Date")
	if data.empty:
		raise ValueError("找不到有效的 XAUUSD 資料")
	return data.set_index("Date")


def resample_ohlc(data: pd.DataFrame, frequency: str) -> pd.DataFrame:
	if frequency == "日線":
		return data.copy()

	rule = {"週線": "W", "月線": "ME"}[frequency]
	return data.resample(rule).agg(
		{"Open": "first", "High": "max", "Low": "min", "Close": "last"}
	).dropna()


def add_indicators(data: pd.DataFrame) -> pd.DataFrame:
	result = data.copy()
	close = result["Close"]
	result["MA20"] = close.rolling(20).mean()
	result["MA60"] = close.rolling(60).mean()
	result["MA120"] = close.rolling(120).mean()
	result["MA240"] = close.rolling(240).mean()

	middle = close.rolling(20).mean()
	standard_deviation = close.rolling(20).std()
	result["BB_Middle"] = middle
	result["BB_Upper"] = middle + 2 * standard_deviation
	result["BB_Lower"] = middle - 2 * standard_deviation

	result["Resistance"] = result["High"].where(
		result["High"] == result["High"].rolling(20, center=True).max()
	)
	result["Support"] = result["Low"].where(
		result["Low"] == result["Low"].rolling(20, center=True).min()
	)

	low_9 = result["Low"].rolling(9).min()
	high_9 = result["High"].rolling(9).max()
	price_range = high_9 - low_9
	rsv = ((close - low_9) / price_range.replace(0, pd.NA)) * 100
	result["K"] = rsv.ewm(alpha=1 / 3, adjust=False).mean()
	result["D"] = result["K"].ewm(alpha=1 / 3, adjust=False).mean()

	ema_12 = close.ewm(span=12, adjust=False).mean()
	ema_26 = close.ewm(span=26, adjust=False).mean()
	result["MACD"] = ema_12 - ema_26
	result["Signal"] = result["MACD"].ewm(span=9, adjust=False).mean()
	result["Histogram"] = result["MACD"] - result["Signal"]
	return result


def draw_candlesticks(axis: plt.Axes, data: pd.DataFrame) -> None:
	width = 0.6
	for position, (_, row) in enumerate(data.iterrows()):
		axis.vlines(position, row["Low"], row["High"], color="#52606d", linewidth=0.8)
		bottom = min(row["Open"], row["Close"])
		height = max(abs(row["Close"] - row["Open"]), 0.01)
		color = "#16a085" if row["Close"] >= row["Open"] else "#e05d44"
		axis.add_patch(
			Rectangle(
				(position - width / 2, bottom),
				width,
				height,
				facecolor=color,
				edgecolor=color,
			)
		)


def format_x_axis(axis: plt.Axes, data: pd.DataFrame) -> None:
	step = max(1, len(data) // 10)
	positions = list(range(0, len(data), step))
	axis.set_xticks(positions)
	axis.set_xticklabels(
		[data.index[position].strftime("%Y-%m-%d") for position in positions],
		rotation=30,
		ha="right",
	)


def make_chart(
	data: pd.DataFrame,
	timeframe: str,
	selected_indicators: list[str],
	show_candles: bool,
) -> plt.Figure:
	has_kd = "KD" in selected_indicators
	has_macd = "MACD" in selected_indicators
	lower_count = int(has_kd) + int(has_macd)
	figure, axes = plt.subplots(
		1 + lower_count,
		1,
		figsize=(15, 6 + lower_count * 2.2),
		sharex=True,
		gridspec_kw={"height_ratios": [3] + [1] * lower_count} if lower_count else None,
	)
	if lower_count == 0:
		price_axis = axes
		lower_axes: list[plt.Axes] = []
	else:
		price_axis = axes[0]
		lower_axes = list(axes[1:])

	if show_candles:
		draw_candlesticks(price_axis, data)
	else:
		price_axis.plot(data.index, data["Close"], label="Close", color="#1f4e79")

	x_values = range(len(data)) if show_candles else data.index
	if show_candles:
		price_axis.set_xlim(-1, len(data))

	def plot_price(column: str, label: str, **kwargs: object) -> None:
		price_axis.plot(x_values, data[column], label=label, **kwargs)

	if "布林通道" in selected_indicators:
		plot_price("BB_Middle", "BB Middle", color="#f39c12")
		plot_price("BB_Upper", "BB Upper", color="#8e44ad", linestyle="--")
		plot_price("BB_Lower", "BB Lower", color="#8e44ad", linestyle="--")
		price_axis.fill_between(
			list(x_values), data["BB_Lower"], data["BB_Upper"], color="#8e44ad", alpha=0.08
		)

	if "均線" in selected_indicators:
		colors = {"MA20": "#d35400", "MA60": "#27ae60", "MA120": "#2980b9", "MA240": "#8e44ad"}
		for column, color in colors.items():
			plot_price(column, column, color=color)

	if "支撐位/阻力位" in selected_indicators:
		plot_price("Support", "Support", color="#16a085", marker="o", linestyle="None", markersize=4)
		plot_price("Resistance", "Resistance", color="#e05d44", marker="o", linestyle="None", markersize=4)

	if has_kd:
		kd_axis = lower_axes.pop(0)
		kd_x_values = range(len(data)) if show_candles else data.index
		kd_axis.plot(kd_x_values, data["K"], label="K", color="#d35400")
		kd_axis.plot(kd_x_values, data["D"], label="D", color="#2980b9")
		kd_axis.axhline(80, color="#e05d44", linestyle="--", linewidth=0.8, label="80")
		kd_axis.axhline(20, color="#16a085", linestyle="--", linewidth=0.8, label="20")
		kd_axis.set_ylim(0, 100)
		kd_axis.set_ylabel("KD")
		kd_axis.grid(alpha=0.25)
		kd_axis.legend(loc="upper left", ncol=4)

	if has_macd:
		macd_axis = lower_axes.pop(0)
		macd_x_values = range(len(data)) if show_candles else data.index
		macd_axis.plot(macd_x_values, data["MACD"], label="MACD", color="#d35400", linewidth=1.5)
		macd_axis.plot(macd_x_values, data["Signal"], label="Signal", color="#2980b9", linewidth=1.2)
		macd_axis.axhline(0, color="#7f8c8d", linestyle="--", linewidth=0.8)
		macd_axis.bar(
			list(macd_x_values),
			data["Histogram"],
			width=0.8,
			color=["#16a085" if value >= 0 else "#e05d44" for value in data["Histogram"]],
			alpha=0.75,
		)
		macd_axis.set_ylabel("MACD")
		macd_axis.grid(alpha=0.25)
		macd_axis.legend(loc="upper left")

	price_axis.set_title("XAUUSD")
	price_axis.set_ylabel("Price (USD)")
	price_axis.grid(alpha=0.25)
	price_axis.legend(loc="upper left", ncol=4)
	format_x_axis(price_axis, data)
	figure.tight_layout()
	return figure


def main() -> None:
	st.set_page_config(page_title="XAUUSD 技術分析", layout="wide")
	st.title("XAUUSD 技術分析")
	st.caption("選取不同週期與技術指標，在同一張圖表中比較價格走勢。")

	try:
		raw_data = load_data()
	except (OSError, ValueError) as error:
		st.error(f"無法載入資料：{error}")
		st.stop()

	with st.sidebar:
		st.header("圖表設定")
		timeframe = st.selectbox("時間週期", ["日線", "週線", "月線"])
		selected_indicators = st.multiselect(
			"技術指標（可複選）",
			["布林通道", "均線", "KD", "MACD", "支撐位/阻力位"],
			default=["均線"],
		)
		show_candles = st.checkbox("顯示 K 線", value=True)
		available_start = raw_data.index.min().date()
		available_end = raw_data.index.max().date()
		selected_dates = st.date_input(
			"選取日期範圍",
			value=(available_start, available_end),
			min_value=available_start,
			max_value=available_end,
		)

	if len(selected_dates) != 2:
		st.warning("請選取完整的開始日期與結束日期。")
		st.stop()

	start_date, end_date = map(pd.Timestamp, selected_dates)
	period_data = resample_ohlc(raw_data, timeframe)
	chart_data = add_indicators(period_data).loc[start_date:end_date]

	figure = make_chart(chart_data, timeframe, selected_indicators, show_candles)
	st.pyplot(figure, use_container_width=True)
	plt.close(figure)


if __name__ == "__main__":
	main()
