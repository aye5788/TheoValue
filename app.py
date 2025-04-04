import streamlit as st
import numpy as np
from scipy.stats import norm
from datetime import date

st.set_page_config(page_title="Option Theoretical Value", layout="centered")

st.title("🧮 Option Theoretical Value Calculator")
st.caption("Black-Scholes Model for European-Style Options (like SPX)")

# --- User Inputs ---
col1, col2 = st.columns(2)
with col1:
    S = st.number_input("Underlying Price (Spot)", min_value=0.0, value=5000.0)
    K = st.number_input("Strike Price", min_value=0.0, value=5050.0)
    r = st.number_input("Risk-Free Rate (annual, e.g. 0.045 for 4.5%)", min_value=0.0, value=0.045)
    option_type = st.selectbox("Option Type", ['call', 'put'])
with col2:
    iv = st.number_input("Implied Volatility (e.g. 0.18 for 18%)", min_value=0.01, value=0.18)
    expiry = st.date_input("Expiration Date", value=date.today())
    today = date.today()
    T = max((expiry - today).days / 365, 0.0001)

# --- Pricing Logic ---
def black_scholes(S, K, T, r, sigma, option_type='call'):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    if option_type == 'call':
        return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:
        return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

# --- Result ---
if st.button("Calculate Theoretical Value"):
    theo_price = black_scholes(S, K, T, r, iv, option_type)
    st.success(f"Theoretical {option_type.capitalize()} Price: ${theo_price:.2f}")

# Optional: Spread Builder in future version
