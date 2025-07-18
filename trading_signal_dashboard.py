
import streamlit as st
import pandas as pd
import numpy as np
from random import choice

# Mock data setup
dates = pd.date_range(end=pd.Timestamp.today(), periods=10).strftime('%Y-%m-%d').tolist()
instruments = ['S&P E-mini', 'Nasdaq E-mini', 'WTI Crude Oil', 'Gold Futures']
indicators = ['RSI', 'Stochastic', 'Proj Osc', 'Volatility', 'Momentum', 'MACD', 'DMI', 'CCI']

def generate_mock_signals():
    return [choice(['Long', 'Short', 'Neutral']) for _ in indicators]

# Mock database
mock_data = []
for date in dates:
    for instrument in instruments:
        signals = generate_mock_signals()
        long_count = signals.count('Long')
        short_count = signals.count('Short')
        if long_count > short_count:
            overall = 'LONG'
        elif short_count > long_count:
            overall = 'SHORT'
        else:
            overall = 'NEUTRAL'
        mock_data.append([date, instrument] + signals + [overall])

columns = ['Date', 'Instrument'] + indicators + ['Overall Signal']
df = pd.DataFrame(mock_data, columns=columns)

# Streamlit App UI
st.set_page_config(page_title="Daily Trading Signal Dashboard", layout="wide")
st.title("📊 Daily Trading Signal Dashboard (Mock Preview)")

password = st.text_input("Enter PIN to access:", type="password")
if password != "1234":
    st.warning("Enter the correct PIN to unlock the dashboard.")
    st.stop()

instrument = st.selectbox("Choose an instrument:", instruments)
filtered_df = df[df['Instrument'] == instrument].sort_values('Date', ascending=False)

st.subheader(f"Signal Table for {instrument}")
signal_colors = {"Long": "green", "Short": "red", "Neutral": "gray", "LONG": "green", "SHORT": "red", "NEUTRAL": "gray"}

def colorize(val):
    color = signal_colors.get(val, "black")
    return f'color: {color}; font-weight: bold'

st.dataframe(filtered_df.style.applymap(colorize, subset=indicators + ['Overall Signal']))

st.subheader("Historical Overall Signal Trend")
signal_map = {"LONG": 1, "NEUTRAL": 0, "SHORT": -1}
filtered_df['Signal Score'] = filtered_df['Overall Signal'].map(signal_map)
st.line_chart(filtered_df.set_index('Date')['Signal Score'])
