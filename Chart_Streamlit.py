from pathlib import Path
import io

import altair as alt
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import pandas as pd
import requests
import streamlit as st


DATA_FILE = Path(__file__).with_name("xauusd_d.csv")
REQUIRED_COLUMNS = {"Date", "Open", "High", "Low", "Close"}
plt.rcParams["font.sans-serif"] = ["Microsoft JhengHei", "Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


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


def normalize_date_column(frame: pd.DataFrame, column_name: str) -> pd.DataFrame:
	result = frame.copy()
	result[column_name] = pd.to_datetime(result[column_name], errors="coerce", utc=True)
	result[column_name] = result[column_name].dt.tz_localize(None)
	return result


@st.cache_data
def load_local_series_csv(file_name: str, date_column: str, value_column: str, label: str) -> pd.DataFrame:
	file_path = Path(__file__).with_name(file_name)
	if not file_path.exists():
		return pd.DataFrame(columns=["Date", label])

	data = pd.read_csv(file_path)
	if date_column not in data.columns:
		if "DATE" in data.columns:
			data = data.rename(columns={"DATE": date_column})
		elif "Date" in data.columns:
			data = data.rename(columns={"Date": date_column})
		elif "observation_date" in data.columns:
			data = data.rename(columns={"observation_date": date_column})
	if value_column not in data.columns:
		value_candidates = [column for column in data.columns if column != date_column]
		if not value_candidates:
			return pd.DataFrame(columns=["Date", label])
		value_column = value_candidates[0]
	data = data[[date_column, value_column]].dropna().copy()
	data = normalize_date_column(data, date_column)
	data = data.rename(columns={date_column: "Date", value_column: label})
	return data[["Date", label]].sort_values("Date").reset_index(drop=True)


@st.cache_data
def load_fred_series(series_id: str, label: str) -> pd.DataFrame:
	url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
	try:
		response = requests.get(url, timeout=30)
		response.raise_for_status()
	except requests.RequestException:
		return pd.DataFrame(columns=["Date", label])

	try:
		data = pd.read_csv(io.StringIO(response.text))
	except Exception:
		return pd.DataFrame(columns=["Date", label])

	if "DATE" in data.columns:
		data = data.rename(columns={"DATE": "Date"})
	if "Date" not in data.columns:
		return pd.DataFrame(columns=["Date", label])

	data = normalize_date_column(data, "Date")
	value_columns = [column for column in data.columns if column != "Date"]
	if not value_columns:
		return pd.DataFrame(columns=["Date", label])
	value_column = value_columns[0]
	data = data[["Date", value_column]].dropna()
	data = data.rename(columns={value_column: label})
	return data.sort_values("Date").reset_index(drop=True)


@st.cache_data
def load_gold_close_data() -> pd.DataFrame:
	data = pd.read_csv(DATA_FILE)
	if "Date" not in data.columns:
		raise ValueError("XAUUSD 資料缺少 Date 欄位")
	data = normalize_date_column(data, "Date")
	data = data[["Date", "Close"]].dropna().sort_values("Date").reset_index(drop=True)
	data = data.rename(columns={"Close": "黃金 Close"})
	return data


@st.cache_data
def load_usdx_data() -> pd.DataFrame:
	usdx_file = Path(__file__).with_name("2021-09-01~2026-08-31美元指數.csv")
	data = pd.read_csv(usdx_file)
	if "Date" not in data.columns:
		data = data.rename(columns={"日期": "Date"})
	if "Close" not in data.columns:
		if "收盤" in data.columns:
			data = data.rename(columns={"收盤": "Close"})
		else:
			raise ValueError("美元指數資料缺少 Close 欄位")
	data = normalize_date_column(data, "Date")
	data = data[["Date", "Close"]].dropna().sort_values("Date").reset_index(drop=True)
	data = data.rename(columns={"Close": "美元指數 Close"})
	return data


@st.cache_data
def load_reserve_data() -> pd.DataFrame:
	reserve_file = Path(__file__).with_name("2021-09~2026-05全球央行黃金儲備.csv")
	data = pd.read_csv(reserve_file)
	if "日期" not in data.columns:
		raise ValueError("全球央行黃金儲備資料缺少 日期 欄位")
	data = data.rename(columns={"日期": "Date", "全球央行總持金量": "全球央行總持金量"})
	data = normalize_date_column(data, "Date")
	return data[["Date", "全球央行總持金量"]].dropna().sort_values("Date").reset_index(drop=True)


@st.cache_data
def load_macro_comparison_data() -> dict[str, pd.DataFrame]:
	series: dict[str, pd.DataFrame] = {
		"黃金 Close": load_gold_close_data(),
		"美元指數 Close": load_usdx_data(),
		"全球央行總持金量": load_reserve_data(),
		"DFF": load_local_series_csv("DFF.csv", "observation_date", "DFF", "DFF"),
		"MEDCPIM158SFRBCLE": load_local_series_csv(
			"MEDCPIM158SFRBCLE.csv", "observation_date", "MEDCPIM158SFRBCLE", "MEDCPIM158SFRBCLE"
		),
	}
	for name, frame in list(series.items()):
		if frame.empty and name == "DFF":
			series[name] = load_fred_series("DFF", "DFF")
		if frame.empty and name == "MEDCPIM158SFRBCLE":
			series[name] = load_fred_series("MEDCPIM158SFRBCLE", "MEDCPIM158SFRBCLE")
	return {name: frame for name, frame in series.items() if not frame.empty}


def add_indicators(data: pd.DataFrame) -> pd.DataFrame:
	result = data.copy()
	close = result["Close"]
	result["MA5"] = close.rolling(5).mean()
	result["MA10"] = close.rolling(10).mean()
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


def format_x_axis(axis: plt.Axes, data: pd.DataFrame, show_candles: bool) -> None:
	if data.empty:
		return
	step = max(1, len(data) // 10)
	positions = sorted(set([0, *range(0, len(data), step), len(data) - 1]))
	if show_candles:
		tick_positions = positions
	else:
		tick_positions = [data.index[position] for position in positions]
	axis.set_xticks(tick_positions)
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
	title: str = "XAUUSD",
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
		price_axis.plot([], [], color="#16a085", linewidth=6, label="K線")
	else:
		price_axis.plot(data.index, data["Close"], label="Close", color="#1f4e79")

	x_values = range(len(data)) if show_candles else data.index
	if show_candles:
		price_axis.set_xlim(-1, len(data))
	else:
		price_axis.set_xlim(data.index.min(), data.index.max())

	def plot_price(column: str, label: str, **kwargs: object) -> None:
		price_axis.plot(x_values, data[column], label=label, **kwargs)

	if "布林通道" in selected_indicators:
		plot_price("BB_Middle", "BB Middle", color="#f39c12")
		plot_price("BB_Upper", "BB Upper", color="#8e44ad", linestyle="--")
		plot_price("BB_Lower", "BB Lower", color="#8e44ad", linestyle="--")
		price_axis.fill_between(
			list(x_values), data["BB_Lower"], data["BB_Upper"], color="#8e44ad", alpha=0.08
		)

	active_ma_columns = [
		"MA5", "MA10", "MA20", "MA60", "MA120", "MA240"
	]
	if "均線" in selected_indicators:
		selected_ma = active_ma_columns
	else:
		selected_ma = [column for column in active_ma_columns if column in selected_indicators]
	colors = {
		"MA5": "#f1c40f",
		"MA10": "#2ecc71",
		"MA20": "#d35400",
		"MA60": "#27ae60",
		"MA120": "#2980b9",
		"MA240": "#8e44ad",
	}
	for column in selected_ma:
		if column in data.columns:
			plot_price(column, column, color=colors.get(column, "#7f8c8d"))

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

	price_axis.set_title(title, pad=12)
	price_axis.set_ylabel("Price (USD)")
	price_axis.grid(alpha=0.25)
	price_axis.legend(loc="upper left", ncol=4)
	label_axis = lower_axes[-1] if lower_axes else price_axis
	format_x_axis(label_axis, data, show_candles)
	for axis in [price_axis, *lower_axes]:
		axis.tick_params(axis="x", labelbottom=axis is label_axis)
	figure.tight_layout(rect=(0.02, 0.05, 0.99, 0.96), pad=1.2)
	return figure


YEAR_OPTIONS = [str(year) for year in range(2021, 2027)]
TECHNICAL_CHARTS = {
	"布林通道": ("日線", ["布林通道"], False),
	"日線": ("日線", [], False),
	"支撐/阻力位": ("日線", ["支撐位/阻力位"], False),
	"K線": ("日線", [], True),
	"KD": ("日線", ["KD"], False),
	"均線": ("日線", ["均線"], False),
	"MACD": ("日線", ["MACD"], False),
	"月線": ("月線", [], True),
	"週線": ("週線", [], True),
}
SOURCE_FILES = {
	"全球央行黃金儲備爬蟲": "goldreserves.py",
	"美元指數爬蟲": "USDX.py",
	"布林通道": "Bollinger_Chart.py",
	"日線": "Daily_Chart.py",
	"支撐/阻力位": "High-Support_Chart.py",
	"K線": "K-line_Chart.py",
	"KD": "KD_Chart.py",
	"均線": "MA_Chart.py",
	"MACD": "MACD_Chart.py",
	"月線": "Monthly_Chart.py",
	"週線": "Weekly_Chart.py",
	"Streamlit網頁": "Chart_Streamlit.py",
}


def filter_by_dates(frame: pd.DataFrame, start_date: pd.Timestamp, end_date: pd.Timestamp) -> pd.DataFrame:
	return frame[(frame.index >= start_date) & (frame.index <= end_date)]


def show_macro_charts(macro_data: dict[str, pd.DataFrame], start_date: pd.Timestamp, end_date: pd.Timestamp) -> None:
	if not macro_data:
		st.info("目前沒有可顯示的基本面資料，請確認本地 CSV 或 FRED 連線可用。")
		return

	chart_columns = st.columns(2)
	for index, (label, frame) in enumerate(macro_data.items()):
		filtered = frame.copy()
		filtered["Date"] = pd.to_datetime(filtered["Date"])
		filtered = filtered[
			(filtered["Date"] >= start_date) & (filtered["Date"] <= end_date)
		].set_index("Date")
		if filtered.empty:
			continue
		with chart_columns[index % 2]:
			st.markdown(f"**{label}**")
			if label == "全球央行總持金量":
				value_column = filtered.columns[0]
				value_min = filtered[value_column].min()
				value_max = filtered[value_column].max()
				value_range = value_max - value_min
				padding = max(value_range * 0.12, abs(value_max) * 0.001, 1)
				reserve_chart_data = filtered.reset_index()
				reserve_chart = alt.Chart(reserve_chart_data).mark_line().encode(
					x=alt.X("Date:T", title=None),
					y=alt.Y(
						f"{value_column}:Q",
						title=None,
						scale=alt.Scale(domain=[value_min - padding, value_max + padding]),
					),
					tooltip=[
						alt.Tooltip("Date:T", title="日期"),
						alt.Tooltip(f"{value_column}:Q", title=value_column),
					],
				).properties(height=250)
				st.altair_chart(reserve_chart, use_container_width=True)
			else:
				st.line_chart(filtered, use_container_width=True)


def show_fundamental_page(macro_data: dict[str, pd.DataFrame]) -> None:
	st.header("黃金基本面分析")
	st.write("整合黃金價格、美元指數、全球央行黃金儲備、利率與 CPI，觀察 2021 至 2026 年的宏觀變化。")
	selected_year = st.radio("選擇年份", YEAR_OPTIONS, horizontal=True, key="fundamental_year")
	start_date = pd.Timestamp(f"{selected_year}-01-01")
	end_date = pd.Timestamp(f"{selected_year}-12-31")
	show_macro_charts(macro_data, start_date, end_date)


def show_technical_page(raw_data: pd.DataFrame) -> None:
	st.header("黃金技術面分析")
	chart_name = st.selectbox("選擇技術圖表", list(TECHNICAL_CHARTS), key="technical_chart")
	selected_year = st.radio("選擇年份", YEAR_OPTIONS, horizontal=True, key="technical_year")
	timeframe, indicators, show_candles = TECHNICAL_CHARTS[chart_name]
	period_data = resample_ohlc(raw_data, timeframe)
	start_date = pd.Timestamp(f"{selected_year}-01-01")
	end_date = pd.Timestamp(f"{selected_year}-12-31")
	chart_data = add_indicators(period_data).loc[start_date:end_date]
	if chart_data.empty:
		st.warning("這個年份沒有可用的價格資料。")
		return
	figure = make_chart(
		chart_data,
		timeframe,
		indicators,
		show_candles,
		title=f"XAUUSD {chart_name} ({selected_year})",
	)
	st.pyplot(figure, use_container_width=True)
	plt.close(figure)


def show_total_analysis(raw_data: pd.DataFrame, macro_data: dict[str, pd.DataFrame]) -> None:
	st.header("綜合分析")
	st.write("在同一個日期區間對照黃金價格、技術指標與宏觀因素，協助整理市場趨勢。")
	selected_indicators = st.multiselect(
		"選擇分析內容",
		[
			"MA5", "MA10", "MA20", "MA60", "MA120", "MA240",
			"布林通道", "支撐/阻力位", "KD", "MACD",
		],
		default=["MA20", "MA60", "布林通道", "支撐/阻力位"],
		key="total_indicators",
	)
	available_start = raw_data.index.min().date()
	available_end = raw_data.index.max().date()
	selected_dates = st.date_input(
		"選擇分析日期範圍",
		value=(max(available_start, pd.Timestamp("2021-09-01").date()), available_end),
		min_value=available_start,
		max_value=available_end,
		key="total_dates",
	)
	if len(selected_dates) != 2:
		st.warning("請選取完整的開始日期與結束日期。")
		return
	start_date, end_date = map(pd.Timestamp, selected_dates)
	chart_data = add_indicators(raw_data).loc[start_date:end_date]
	if chart_data.empty:
		st.warning("這個日期範圍沒有可用的價格資料。")
		return
	if not selected_indicators:
		st.info("請至少選擇一項分析內容。")
		return
	figure = make_chart(
		chart_data,
		"日線",
		selected_indicators,
		False,
		title="XAUUSD 綜合分析",
	)
	st.pyplot(figure, use_container_width=True)
	plt.close(figure)
	st.subheader("基本面對照")
	show_macro_charts(macro_data, start_date, end_date)


def show_source_code(title: str, file_name: str) -> None:
	st.subheader(title)
	file_path = Path(__file__).with_name(file_name)
	if not file_path.exists():
		st.error(f"找不到程式碼檔案：{file_name}")
		return
	st.code(file_path.read_text(encoding="utf-8"), language="python")


def render_navbar() -> None:
	st.markdown(
		"""
		<style>
		:root {
			--gold-nav: #17324d;
			--gold-nav-hover: #24557d;
			--gold-nav-border: rgba(255, 255, 255, 0.16);
			--gold-menu-shadow: 0 14px 32px rgba(15, 35, 55, 0.22);
		}

		.stApp > header {
			background: transparent;
		}

		.block-container {
			padding-top: 5.75rem;
		}

		.gold-navbar {
			position: fixed;
			top: 0;
			left: 0;
			right: 0;
			z-index: 999999;
			display: flex;
			align-items: center;
			justify-content: space-between;
			min-height: 4.25rem;
			padding: 0.65rem clamp(1rem, 4vw, 4rem);
			box-sizing: border-box;
			background: var(--gold-nav);
			border-bottom: 1px solid var(--gold-nav-border);
			box-shadow: 0 4px 18px rgba(15, 35, 55, 0.18);
			overflow: visible;
		}

		.gold-brand,
		.gold-nav-link {
			color: #f8fbff !important;
			text-decoration: none !important;
			white-space: nowrap;
		}

		.gold-brand {
			font-size: 1.05rem;
			font-weight: 700;
			letter-spacing: 0.01em;
		}

		.gold-nav-links {
			display: flex;
			align-items: stretch;
			gap: 0.2rem;
			height: 100%;
		}

		.gold-nav-item,
		.gold-dropdown {
			position: relative;
			display: flex;
			align-items: center;
		}

		.gold-nav-link {
			display: inline-flex;
			align-items: center;
			gap: 0.35rem;
			padding: 0.72rem 0.8rem;
			border-radius: 0.45rem;
			font-size: 0.94rem;
			transition: background 160ms ease, color 160ms ease;
		}

		.gold-nav-link:hover,
		.gold-nav-link:focus-visible,
		.gold-dropdown:hover > .gold-nav-link,
		.gold-dropdown:focus-within > .gold-nav-link {
			background: var(--gold-nav-hover);
			outline: none;
		}

		.gold-chevron {
			font-size: 0.75rem;
			line-height: 1;
		}

		.gold-dropdown-menu {
			position: absolute;
			top: 100%;
		right: 0;
			min-width: 10.5rem;
			padding: 0.4rem;
			visibility: hidden;
			opacity: 0;
			transform: translateY(-0.35rem);
			pointer-events: none;
			background: #ffffff;
			border: 1px solid #d7e0e8;
			border-radius: 0.55rem;
			box-shadow: var(--gold-menu-shadow);
			transition: opacity 220ms ease, transform 220ms ease, visibility 220ms ease;
		}

		.gold-dropdown-menu::before {
			content: "";
			position: absolute;
			top: -0.45rem;
			left: 0;
			right: 0;
			height: 0.45rem;
		}

		.gold-dropdown:hover .gold-dropdown-menu,
		.gold-dropdown:focus-within .gold-dropdown-menu {
			visibility: visible;
			opacity: 1;
			transform: translateY(0);
			pointer-events: auto;
		}

		.gold-dropdown-menu a {
			display: block;
			padding: 0.65rem 0.75rem;
			color: #17324d !important;
			border-radius: 0.35rem;
			font-size: 0.9rem;
			text-decoration: none !important;
			white-space: nowrap;
		}

		.gold-dropdown-menu a:hover,
		.gold-dropdown-menu a:focus-visible {
			background: #eaf2f8;
			outline: none;
		}

		@media (max-width: 760px) {
			.gold-navbar {
				align-items: flex-start;
				flex-wrap: wrap;
				gap: 0.25rem;
				padding-block: 0.5rem;
			}

			.gold-brand {
				width: 100%;
			}

			.gold-nav-links {
				width: 100%;
				justify-content: space-between;
			}

			.gold-nav-link {
				padding: 0.55rem 0.45rem;
				font-size: 0.82rem;
			}
		}
		</style>
		<nav class="gold-navbar" aria-label="主要導覽">
			<a class="gold-brand" href="?page=home" target="_self">🥇 黃金價格分析專題</a>
			<div class="gold-nav-links">
				<div class="gold-nav-item">
					<a class="gold-nav-link" href="?page=home" target="_self">首頁</a>
				</div>
				<div class="gold-dropdown">
					<a class="gold-nav-link" href="?page=fundamental" target="_self">專題分析 <span class="gold-chevron">▼</span></a>
					<div class="gold-dropdown-menu">
						<a href="?page=fundamental" target="_self">基本面分析</a>
						<a href="?page=technical" target="_self">技術面分析</a>
						<a href="?page=total" target="_self">綜合分析</a>
					</div>
				</div>
				<div class="gold-dropdown">
					<a class="gold-nav-link" href="?page=scraping" target="_self">製作過程 <span class="gold-chevron">▼</span></a>
					<div class="gold-dropdown-menu">
						<a href="?page=scraping" target="_self">爬蟲</a>
						<a href="?page=charts" target="_self">各圖表製作</a>
						<a href="?page=streamlit" target="_self">Streamlit 網頁製作</a>
					</div>
				</div>
				<div class="gold-nav-item">
					<a class="gold-nav-link" href="?page=conclusion" target="_self">專題結論</a>
				</div>
			</div>
		</nav>
		""",
		unsafe_allow_html=True,
	)


def show_process_page(section: str) -> None:
	chart_source_files = [
		("布林通道", "Bollinger_Chart.py"),
		("日線", "Daily_Chart.py"),
		("支撐位與阻力位", "High-Support_Chart.py"),
		("K線", "K-line_Chart.py"),
		("KD", "KD_Chart.py"),
		("均線", "MA_Chart.py"),
		("MACD", "MACD_Chart.py"),
		("月線", "Monthly_Chart.py"),
		("週線", "Weekly_Chart.py"),
	]
	if section == "scraping":
		st.header("爬蟲")
		source_files = {
			"全球央行黃金儲備爬蟲": "goldreserves.py",
			"美元指數爬蟲": "USDX.py",
		}
		selected_source = st.selectbox("選擇程式碼", list(source_files), key="scraping_source")
		show_source_code(selected_source, source_files[selected_source])
	elif section == "charts":
		st.header("各圖表製作")
		source_files = dict(chart_source_files)
		selected_source = st.selectbox("選擇程式碼", list(source_files), key="chart_source")
		show_source_code(selected_source, source_files[selected_source])
	else:
		st.header("Streamlit 網頁製作")
		show_source_code("Streamlit 網頁製作", "Chart_Streamlit.py")


def show_conclusion_page() -> None:
	st.header("專題結論")
	st.write("本專題透過基本面與技術面資料，整理 XAUUSD 在研究期間的價格變化與可能影響因素。")
	st.write("使用者可以從專題分析查看不同年份與日期範圍，並搭配製作過程了解資料蒐集、資料處理、資料分析、視覺化與網站整合流程。")


def show_home_page() -> None:
	st.markdown(
		"""
		<style>
		.home-hero {
			padding: 2.3rem 2.5rem;
			margin-bottom: 1.5rem;
			background: linear-gradient(115deg, #17324d 0%, #24557d 100%);
			border-radius: 0.75rem;
			color: #f8fbff;
		}

		.home-kicker {
			margin: 0 0 0.55rem;
			color: #b8d7e8;
			font-size: 0.82rem;
			font-weight: 700;
			letter-spacing: 0.14em;
		}

		.home-hero h1 {
			margin: 0;
			font-size: clamp(2rem, 4vw, 3.2rem);
			line-height: 1.12;
		}

		.home-hero p:last-child {
			max-width: 52rem;
			margin: 1rem 0 0;
			color: #e1edf4;
			font-size: 1rem;
			line-height: 1.8;
		}

		.home-section-title {
			margin: 1.7rem 0 0.8rem;
			color: #17324d;
			font-size: 1.35rem;
			font-weight: 700;
		}

		.home-card {
			min-height: 9.5rem;
			padding: 1.15rem 1.2rem;
			border: 1px solid #d7e0e8;
			border-radius: 0.55rem;
			background: #ffffff;
			box-shadow: 0 5px 16px rgba(15, 35, 55, 0.07);
		}

		.home-card h3 {
			margin: 0 0 0.55rem;
			color: #17324d;
			font-size: 1.05rem;
		}

		.home-card p {
			margin: 0;
			color: #52606d;
			line-height: 1.65;
		}

		.home-note {
			margin-top: 1.5rem;
			padding: 1rem 1.2rem;
			border-left: 4px solid #b7791f;
			background: #f7f9fb;
			color: #52606d;
		}

		@media (max-width: 760px) {
			.home-hero {
				padding: 1.7rem 1.35rem;
			}
		}
		</style>
		<section class="home-hero">
			<p class="home-kicker">XAUUSD MARKET RESEARCH</p>
			<h1>黃金價格分析專題</h1>
			<p>以 XAUUSD 黃金價格為核心，結合基本面與技術面資料，整理 2021 至 2026 年的市場變化，提供一個可查閱、可比較的分析入口。</p>
		</section>
		""",
		unsafe_allow_html=True,
	)

	st.markdown('<p class="home-section-title">這個網站可以看什麼？</p>', unsafe_allow_html=True)
	intro_columns = st.columns(3)
	for column, title, description in zip(
		intro_columns,
		["基本面分析", "技術面分析", "綜合分析"],
		[
			"比較美元指數、利率、CPI 與全球央行黃金儲備，觀察宏觀因素與金價的關聯。",
			"透過日線、週線、月線、均線、KD、布林通道與支撐阻力位檢視價格趨勢。",
			"選擇多項指標與日期範圍，把技術訊號與基本面資料放在同一個分析脈絡中。",
		],
	):
		with column:
			st.markdown(
				f'<div class="home-card"><h3>{title}</h3><p>{description}</p></div>',
				unsafe_allow_html=True,
			)

	st.markdown('<p class="home-section-title">研究範圍</p>', unsafe_allow_html=True)
	summary_columns = st.columns(3)
	with summary_columns[0]:
		st.metric("分析期間", "2021/09 - 2026/08")
	with summary_columns[1]:
		st.metric("核心市場", "XAUUSD")
	with summary_columns[2]:
		st.metric("分析角度", "基本面 × 技術面")

	st.markdown(
		'<div class="home-note"><strong>開始探索</strong><br>從上方「專題分析」選擇基本面、技術面或綜合分析；也可以在「製作過程」查看本專題實際使用的程式碼。</div>',
		unsafe_allow_html=True,
	)


def main() -> None:
	st.set_page_config(page_title="黃金價格分析專題", page_icon="📈", layout="wide")
	try:
		raw_data = load_data()
		macro_data = load_macro_comparison_data()
	except (OSError, ValueError) as error:
		st.error(f"無法載入資料：{error}")
		st.stop()

	render_navbar()
	page = st.query_params.get("page", "home")
	if page == "home":
		show_home_page()
	elif page == "fundamental":
		show_fundamental_page(macro_data)
	elif page == "technical":
		show_technical_page(raw_data)
	elif page == "total":
		show_total_analysis(raw_data, macro_data)
	elif page in {"scraping", "charts", "streamlit"}:
		show_process_page(page)
	elif page == "conclusion":
		show_conclusion_page()
	else:
		st.query_params["page"] = "home"
		show_home_page()

	st.divider()
	st.caption("製作團隊：賴長佑、楊智偉、黃子恩")
	st.markdown("[Github](https://github.com/y78y7878/GoldPrice)")


if __name__ == "__main__":
	main()
