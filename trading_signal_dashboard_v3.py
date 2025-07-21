
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from random import choice, randint

# -------- PAGE CONFIG --------
st.set_page_config(page_title="Trading Signal Dashboard v3", layout="wide")
st.title("🔐 Trading Signal Dashboard – Version 3")

# -------- SECURITY (PIN ACCESS) --------
password = st.text_input("Enter PIN to access the dashboard:", type="password")
if password != "1234":
    st.warning("Please enter the correct PIN to unlock the app.")
    st.stop()

# -------- MOCK DATA GENERATION --------
dates = pd.date_range(end=pd.Timestamp.today(), periods=10).strftime('%Y-%m-%d').tolist()
instruments = ['S&P E-mini', 'Nasdaq E-mini', 'WTI Crude Oil', 'Gold Futures']
indicators = ['RSI', 'Stochastic', 'Proj Osc', 'Volatility', 'Momentum', 'MACD', 'DMI', 'CCI']

def generate_mock_data():
    data = []
    for date in dates:
        for instrument in instruments:
            values = [choice(['Long', 'Short', 'Neutral']) for _ in indicators]
            longs = values.count('Long')
            shorts = values.count('Short')
            overall = 'LONG' if longs > shorts else 'SHORT' if shorts > longs else 'NEUTRAL'
            data.append([date, instrument, overall] + values)
    columns = ['Date', 'Instrument', 'Overall Signal'] + indicators
    return pd.DataFrame(data, columns=columns)

def generate_intraday_data():
    times = pd.date_range(start="09:30", end="16:00", freq="15min").strftime('%H:%M')
    prices = np.cumsum(np.random.randn(len(times)) * 0.5) + 100
    signal_values = [choice([-1, 0, 1]) for _ in times]
    return pd.DataFrame({'Time': times, 'Price': prices, 'Signal': signal_values})

df_history = generate_mock_data()
intraday_data_map = {inst: generate_intraday_data() for inst in instruments}

# -------- DASHBOARD UI --------
menu = st.sidebar.radio("Select View", ["Instrument View", "Market Dashboard"])

if menu == "Instrument View":
    instrument = st.selectbox("Choose Instrument", instruments)
    df_instrument = df_history[df_history['Instrument'] == instrument].sort_values('Date', ascending=False)

    st.subheader(f"📋 Signal Table – {instrument}")
    signal_colors = {"Long": "green", "Short": "red", "Neutral": "gray", "LONG": "green", "SHORT": "red", "NEUTRAL": "gray"}

    def colorize(val):
        color = signal_colors.get(val, "black")
        return f'color: {color}; font-weight: bold'

    st.dataframe(df_instrument.style.applymap(colorize, subset=df_instrument.columns[2:]))

    st.subheader("📈 Historical Price (Mocked)")
    fig1, ax1 = plt.subplots(figsize=(10, 3))
    ax1.plot(df_instrument['Date'], np.linspace(100, 110, len(df_instrument)), label='Mock Price')
    ax1.set_ylabel("Price")
    ax1.set_title("Historical Price")
    st.pyplot(fig1)

    st.subheader("📊 Overall Signal History")
    signal_map = {"LONG": 1, "NEUTRAL": 0, "SHORT": -1}
    signal_bar = df_instrument['Overall Signal'].map(signal_map)
    fig2, ax2 = plt.subplots(figsize=(10, 2))
    ax2.bar(df_instrument['Date'], signal_bar, color=['green' if x == 1 else 'red' if x == -1 else 'gray' for x in signal_bar])
    ax2.set_ylabel("Signal")
    ax2.set_title("Daily Signal Strength (1 = Long, -1 = Short, 0 = Neutral)")
    st.pyplot(fig2)

    st.subheader("📉 Intraday Price & Signal Preview")
    intraday = intraday_data_map[instrument]
    fig3, ax3 = plt.subplots(figsize=(10, 3))
    ax3.plot(intraday['Time'], intraday['Price'], label="Intraday Price")
    for i, row in intraday.iterrows():
        if row['Signal'] == 1:
            ax3.axvspan(row['Time'], row['Time'], color='green', alpha=0.3)
        elif row['Signal'] == -1:
            ax3.axvspan(row['Time'], row['Time'], color='red', alpha=0.3)
    ax3.set_title("Intraday Price with Signal Zones")
    ax3.set_ylabel("Price")
    ax3.set_xlabel("Time")
    st.pyplot(fig3)

elif menu == "Market Dashboard":
    st.subheader("🌐 Market Overview – Intraday Signals")
    for instrument in instruments:
        st.markdown(f"### {instrument}")
        intraday = intraday_data_map[instrument]
        fig, ax = plt.subplots(figsize=(9, 2.5))
        ax.plot(intraday['Time'], intraday['Price'], label="Intraday Price")
        for i, row in intraday.iterrows():
            if row['Signal'] == 1:
                ax.axvspan(row['Time'], row['Time'], color='green', alpha=0.3)
            elif row['Signal'] == -1:
                ax.axvspan(row['Time'], row['Time'], color='red', alpha=0.3)
        ax.set_ylabel("Price")
        ax.set_xlabel("Time")
        ax.set_title(f"{instrument} – Intraday Signal Zones")
        st.pyplot(fig)
