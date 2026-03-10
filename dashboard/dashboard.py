import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚲",
    layout="wide"
)

sns.set_theme(style="whitegrid")

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data():
    df = pd.read_csv("dashboard/main_data.csv")
    df["date"] = pd.to_datetime(df["date"])
    return df

df = load_data()

# =========================
# HEADER
# =========================
st.title("🚲 Bike Sharing Dashboard")
st.markdown(
    "Dashboard interaktif untuk mengeksplorasi pola penyewaan sepeda berdasarkan waktu, musim, cuaca, dan tipe pengguna."
)

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.header("⚙️ Filter & Pengaturan")

    st.markdown("### Filter Data")

    selected_year = st.multiselect(
        "Pilih Tahun",
        options=sorted(df["year"].unique()),
        default=sorted(df["year"].unique())
    )

    selected_season = st.multiselect(
        "Pilih Musim",
        options=sorted(df["season"].unique()),
        default=sorted(df["season"].unique())
    )

    selected_weather = st.multiselect(
        "Pilih Kondisi Cuaca",
        options=sorted(df["weather_condition"].unique()),
        default=sorted(df["weather_condition"].unique())
    )

    selected_day_type = st.multiselect(
        "Pilih Tipe Hari",
        options=sorted(df["day_type"].unique()),
        default=sorted(df["day_type"].unique())
    )

    date_min = df["date"].min()
    date_max = df["date"].max()

    selected_date_range = st.date_input(
        "Pilih Rentang Tanggal",
        value=(date_min, date_max),
        min_value=date_min,
        max_value=date_max
    )

    st.markdown("---")
    st.markdown("### Pilih Visualisasi")

    chart_options = {
        "Tren Penyewaan Bulanan": "monthly_trend",
        "Rata-rata Penyewaan Berdasarkan Musim": "season_chart",
        "Rata-rata Penyewaan Berdasarkan Cuaca": "weather_chart",
        "Pola Penyewaan per Jam": "hourly_pattern",
        "Perbandingan Casual vs Registered": "user_type_chart",
        "Penyewaan Berdasarkan Hari dalam Seminggu": "weekday_chart"
    }

    selected_charts = st.multiselect(
        "Grafik yang Ditampilkan",
        options=list(chart_options.keys()),
        default=list(chart_options.keys())[:4]
    )

    st.markdown("---")
    st.info(
        "Gunakan filter untuk mempersempit data, lalu pilih sendiri grafik yang ingin dianalisis."
    )

# =========================
# FILTER DATA
# =========================
filtered_df = df[
    (df["year"].isin(selected_year)) &
    (df["season"].isin(selected_season)) &
    (df["weather_condition"].isin(selected_weather)) &
    (df["day_type"].isin(selected_day_type))
].copy()

# Filter tanggal
if isinstance(selected_date_range, tuple) and len(selected_date_range) == 2:
    start_date, end_date = selected_date_range
    filtered_df = filtered_df[
        (filtered_df["date"] >= pd.to_datetime(start_date)) &
        (filtered_df["date"] <= pd.to_datetime(end_date))
    ]

if filtered_df.empty:
    st.warning("Tidak ada data yang sesuai dengan filter yang dipilih.")
    st.stop()

# =========================
# METRIC CARDS
# =========================
daily_total = filtered_df.groupby("date")["total_rentals"].sum()
total_rentals = int(filtered_df["total_rentals"].sum())
avg_daily_rentals = int(daily_total.mean())
avg_hourly_rentals = round(filtered_df["total_rentals"].mean(), 2)

top_season = (
    filtered_df.groupby("season")["total_rentals"]
    .mean()
    .sort_values(ascending=False)
    .index[0]
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Penyewaan", f"{total_rentals:,}")
col2.metric("Rata-rata Harian", f"{avg_daily_rentals:,}")
col3.metric("Rata-rata per Jam", f"{avg_hourly_rentals}")
col4.metric("Musim Terbaik", top_season)

st.markdown("---")

# =========================
# CHART FUNCTIONS
# =========================
def show_monthly_trend(data):
    st.subheader("📈 Tren Penyewaan Bulanan")
    monthly_trend = (
        data.groupby(["year", "month", "month_name"])["total_rentals"]
        .sum()
        .reset_index()
        .sort_values(["year", "month"])
    )

    monthly_trend["month_label"] = (
        monthly_trend["month_name"] + "-" + monthly_trend["year"].astype(str)
    )

    fig, ax = plt.subplots(figsize=(14, 6))
    sns.lineplot(
        data=monthly_trend,
        x="month_label",
        y="total_rentals",
        marker="o",
        linewidth=2.5,
        ax=ax
    )
    ax.set_title("Total Penyewaan Sepeda per Bulan")
    ax.set_xlabel("Bulan")
    ax.set_ylabel("Total Penyewaan")
    plt.xticks(rotation=45)
    st.pyplot(fig)


def show_season_chart(data):
    st.subheader("🌤️ Rata-rata Penyewaan Berdasarkan Musim")
    season_avg = (
        data.groupby("season")["total_rentals"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(
        data=season_avg,
        x="season",
        y="total_rentals",
        palette="Blues_r",
        ax=ax
    )
    ax.set_title("Rata-rata Penyewaan Berdasarkan Musim")
    ax.set_xlabel("Musim")
    ax.set_ylabel("Rata-rata Penyewaan")
    st.pyplot(fig)


def show_weather_chart(data):
    st.subheader("🌦️ Rata-rata Penyewaan Berdasarkan Cuaca")
    weather_avg = (
        data.groupby("weather_condition")["total_rentals"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(
        data=weather_avg,
        x="weather_condition",
        y="total_rentals",
        palette="Greens_r",
        ax=ax
    )
    ax.set_title("Rata-rata Penyewaan Berdasarkan Kondisi Cuaca")
    ax.set_xlabel("Kondisi Cuaca")
    ax.set_ylabel("Rata-rata Penyewaan")
    plt.xticks(rotation=20)
    st.pyplot(fig)


def show_hourly_pattern(data):
    st.subheader("🕒 Pola Penyewaan per Jam")
    hourly_pattern = (
        data.groupby(["hour", "day_type"])["total_rentals"]
        .mean()
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(14, 6))
    sns.lineplot(
        data=hourly_pattern,
        x="hour",
        y="total_rentals",
        hue="day_type",
        marker="o",
        linewidth=2,
        ax=ax
    )
    ax.set_title("Pola Rata-rata Penyewaan per Jam")
    ax.set_xlabel("Jam")
    ax.set_ylabel("Rata-rata Penyewaan")
    ax.set_xticks(range(24))
    st.pyplot(fig)


def show_user_type_chart(data):
    st.subheader("👥 Perbandingan Pengguna Casual vs Registered")
    user_type = data[["casual_users", "registered_users"]].sum().reset_index()
    user_type.columns = ["user_type", "total"]

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(
        data=user_type,
        x="user_type",
        y="total",
        palette="Set2",
        ax=ax
    )
    ax.set_title("Total Penyewaan Berdasarkan Tipe Pengguna")
    ax.set_xlabel("Tipe Pengguna")
    ax.set_ylabel("Total Penyewaan")
    st.pyplot(fig)


def show_weekday_chart(data):
    st.subheader("📅 Penyewaan Berdasarkan Hari dalam Seminggu")

    weekday_order = [
        "Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday"
    ]

    weekday_avg = (
        data.groupby("weekday")["total_rentals"]
        .mean()
        .reindex(weekday_order)
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(12, 5))
    sns.barplot(
        data=weekday_avg,
        x="weekday",
        y="total_rentals",
        palette="Purples_r",
        ax=ax
    )
    ax.set_title("Rata-rata Penyewaan Berdasarkan Hari")
    ax.set_xlabel("Hari")
    ax.set_ylabel("Rata-rata Penyewaan")
    plt.xticks(rotation=20)
    st.pyplot(fig)

# =========================
# SHOW CHARTS BASED ON CHOICE
# =========================
if not selected_charts:
    st.info("Pilih minimal satu grafik dari sidebar untuk ditampilkan.")
else:
    for chart_name in selected_charts:
        chart_key = chart_options[chart_name]

        if chart_key == "monthly_trend":
            show_monthly_trend(filtered_df)

        elif chart_key == "season_chart":
            show_season_chart(filtered_df)

        elif chart_key == "weather_chart":
            show_weather_chart(filtered_df)

        elif chart_key == "hourly_pattern":
            show_hourly_pattern(filtered_df)

        elif chart_key == "user_type_chart":
            show_user_type_chart(filtered_df)

        elif chart_key == "weekday_chart":
            show_weekday_chart(filtered_df)

        st.markdown("---")

# =========================
# INSIGHT SECTION
# =========================
season_avg = (
    filtered_df.groupby("season")["total_rentals"]
    .mean()
    .sort_values(ascending=False)
    .reset_index()
)

weather_avg = (
    filtered_df.groupby("weather_condition")["total_rentals"]
    .mean()
    .sort_values(ascending=False)
    .reset_index()
)

st.subheader("📝 Insight Ringkas")
st.markdown(f"""
- Total penyewaan pada data terfilter mencapai **{total_rentals:,}**.
- Rata-rata penyewaan harian berada di angka **{avg_daily_rentals:,}**.
- Musim dengan rata-rata penyewaan tertinggi adalah **{season_avg.iloc[0]['season']}**.
- Kondisi cuaca paling mendukung penyewaan adalah **{weather_avg.iloc[0]['weather_condition']}**.
- Dataset menunjukkan bahwa pengguna **registered** umumnya berkontribusi lebih besar dibanding pengguna casual.
""")