
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import datetime as dt
import ta
from sklearn.linear_model import LinearRegression

# CONFIG
st.set_page_config(page_title="Trading Signal App v6.5", layout="wide")
st.title("📈 Trading Signal App – Version 6.5 (Final DMI Assignment Fix)")

# PIN LOCK
password = st.text_input("Enter PIN to access the dashboard:", type="password")
if password != "1234":
    st.warning("Please enter the correct PIN to continue.")
    st.stop()

# SYMBOLS
symbols = {
    "S&P E-mini Futures": "ES=F",
    "Nasdaq E-mini Futures": "NQ=F"
}

# INDICATORS
indicators = ["RSI", "Stochastic", "ProjOsc", "Volatility", "Momentum", "MACD", "DMI", "CCI"]

# FUNCTIONS
def fetch_data(symbol, days=60):
    end = dt.datetime.now()
    start = end - dt.timedelta(days=days)
    df = yf.download(symbol, start=start, end=end, interval='1d')
    df.dropna(inplace=True)
    return df

def projection_oscillator(close, period=14):
    x = np.arange(period).reshape(-1, 1)
    proj_osc = []
    for i in range(period, len(close)):
        y = close[i - period:i].values.reshape(-1, 1)
        model = LinearRegression().fit(x, y)
        forecast = model.predict([[period]])[0][0]
        curr_close = close.iloc[i]
        osc_val = 100 * (curr_close - forecast) / forecast
        proj_osc.append(np.clip(osc_val, -100, 100))
    return [np.nan]*period + proj_osc

def calculate_adx(df, window=14):
    high = df['High']
    low = df['Low']
    close = df['Close']

    plus_dm = high.diff()
    minus_dm = low.diff().abs()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0

    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = tr.rolling(window=window).mean()

    plus_di = 100 * (plus_dm.rolling(window=window).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(window=window).mean() / atr)

    dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
    adx = dx.rolling(window=window).mean()

    adx.name = "DMI"
    adx = adx.reindex(df.index)
    adx = pd.Series(adx, index=df.index)

    return adx

def calculate_indicators(df):
    close = df['Close'].squeeze().astype(float)
    high = df['High'].squeeze().astype(float)
    low = df['Low'].squeeze().astype(float)

    df['RSI'] = ta.momentum.RSIIndicator(close=close, window=14).rsi()
    df['Stochastic'] = ta.momentum.StochasticOscillator(high=high, low=low, close=close, window=14).stoch()
    df['Momentum'] = ta.momentum.ROCIndicator(close=close, window=5).roc()
    df['MACD'] = ta.trend.MACD(close=close).macd_diff()
    df['CCI'] = ta.trend.CCIIndicator(high=high, low=low, close=close, window=20).cci()
    df['Volatility'] = np.log(close / close.shift(1)).rolling(10).std() * np.sqrt(252) * 100
    df['ProjOsc'] = projection_oscillator(close, period=14)
    df['DMI'] = calculate_adx(df)
    return df

def generate_signals(df):
    signals = []
    for i in range(1, len(df)):
        today = df.iloc[i]
        yesterday = df.iloc[i - 1]
        row = [df.index[i].strftime('%Y-%m-%d')]
        signal_status = []
        for ind in indicators:
            if pd.isna(today[ind]) or pd.isna(yesterday[ind]):
                signal_status.append("Neutral")
            elif today[ind] > yesterday[ind]:
                signal_status.append("Long")
            elif today[ind] < yesterday[ind]:
                signal_status.append("Short")
            else:
                signal_status.append("Neutral")
        long_count = signal_status.count("Long")
        short_count = signal_status.count("Short")
        overall = "LONG" if long_count > short_count else "SHORT" if short_count > long_count else "NEUTRAL"
        row.append(overall)
        row.extend(signal_status)
        signals.append(row)
    return pd.DataFrame(signals, columns=["Date", "Overall Signal"] + indicators)

# UI
instrument = st.selectbox("Choose an Instrument", list(symbols.keys()))
symbol = symbols[instrument]

df_price = fetch_data(symbol)
df_price = calculate_indicators(df_price)
df_signals = generate_signals(df_price)

st.subheader("📋 Signal Table")
st.dataframe(df_signals.style.applymap(
    lambda val: f"color: {'green' if val=='Long' or val=='LONG' else 'red' if val=='Short' or val=='SHORT' else 'gray'}; font-weight: bold",
    subset=df_signals.columns[1:]))

st.subheader("📈 Historical Price")
fig1, ax1 = plt.subplots(figsize=(10, 3))
ax1.plot(df_price.index, df_price['Close'])
ax1.set_title(f"{instrument} – Close Price")
st.pyplot(fig1)

st.subheader("📊 Overall Signal Strength")
signal_map = {"LONG": 1, "NEUTRAL": 0, "SHORT": -1}
df_signals['Score'] = df_signals['Overall Signal'].map(signal_map)
fig2, ax2 = plt.subplots(figsize=(10, 2))
ax2.bar(df_signals['Date'], df_signals['Score'], color=df_signals['Score'].map({1: 'green', -1: 'red', 0: 'gray'}))
ax2.set_title("Daily Trading Signal")
st.pyplot(fig2)
