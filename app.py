import streamlit as st
import numpy as np
from scipy.stats import norm
from datetime import date

st.set_page_config(page_title="Option Spread Theoretical Value", layout="wide")

st.title("📊 Option Spread Theoretical Value Calculator")
st.caption("Black-Scholes model (European-style). Supports multi-leg strategies like verticals, calendars, condors.")

# ------------------------------
# Initialize session state for legs
# ------------------------------
if "legs" not in st.session_state:
    st.session_state.legs = [{}]  # Start with one leg

# ------------------------------
# Black-Scholes Pricing Function
# ------------------------------
def black_scholes(S, K, T, r, sigma, option_type='call'):
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if option_type == 'call':
        return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:
        return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

# ------------------------------
# Global Inputs
# ------------------------------
st.sidebar.header("🔧 Global Parameters")
S = st.sidebar.number_input("Spot Price", min_value=0.0, value=5000.0)
r = st.sidebar.number_input("Risk-Free Rate (e.g. 0.045 = 4.5%)", min_value=0.0, value=0.045)
today = date.today()

st.markdown("---")
st.subheader("🧱 Build Your Option Spread")

# ------------------------------
# Option Leg Inputs
# ------------------------------
cols = st.columns([1, 1, 1, 1, 1, 1, 1])

for idx, leg in enumerate(st.session_state.legs):
    with st.container():
        st.markdown(f"**Leg {idx + 1}**")
        col1, col2, col3, col4, col5, col6, col7 = cols

        with col1:
            leg['type'] = st.selectbox(f"Type {idx}", ['call', 'put'], key=f"type_{idx}")
        with col2:
            leg['action'] = st.selectbox(f"Action {idx}", ['buy', 'sell'], key=f"action_{idx}")
        with col3:
            leg['strike'] = st.number_input(f"Strike {idx}", value=5000.0, key=f"strike_{idx}")
        with col4:
            leg['iv'] = st.number_input(f"IV (e.g. 0.18) {idx}", value=0.18, min_value=0.01, key=f"iv_{idx}")
        with col5:
            leg['expiry'] = st.date_input(f"Expiry {idx}", value=today, key=f"expiry_{idx}")
        with col6:
            leg['qty'] = st.number_input(f"Contracts {idx}", min_value=1, value=1, key=f"qty_{idx}")

        st.session_state.legs[idx] = leg

# ------------------------------
# Add/Remove Legs Buttons
# ------------------------------
col_add, col_remove = st.columns(2)
with col_add:
    if st.button("➕ Add Option Leg"):
        st.session_state.legs.append({})
with col_remove:
    if st.button("➖ Remove Last Leg") and len(st.session_state.legs) > 1:
        st.session_state.legs.pop()

# ------------------------------
# Calculate Theoretical Spread Value
# ------------------------------
if st.button("💰 Calculate Theoretical Value"):
    total_value = 0.0
    st.subheader("🧾 Leg Breakdown")

    for idx, leg in enumerate(st.session_state.legs):
        T = max((leg['expiry'] - today).days / 365, 0.0001)
        theo_price = black_scholes(S, leg['strike'], T, r, leg['iv'], leg['type'])

        # Sign logic: sell = collect premium = +, buy = pay premium = -
        if leg['action'] == 'sell':
            net = +theo_price * leg['qty']
        else:  # buy
            net = -theo_price * leg['qty']

        total_value += net

        st.write(
            f"**Leg {idx + 1}** | {leg['action'].capitalize()} {leg['type']} @ {leg['strike']} | "
            f"IV: {leg['iv']*100:.1f}% | Time: {(T*365):.0f} days → "
            f"Theo: ${theo_price:.2f} → Value: {'+' if net >=0 else ''}{net:.2f}"
        )

    # Final result
    result_color = "🟢" if total_value >= 0 else "🔴"
    st.success(f"{result_color} Net Theoretical Value of Spread: ${total_value:.2f}")

