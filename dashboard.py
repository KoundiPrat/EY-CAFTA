import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import ast

# Load the output CSV from previous simulation (assumed path)
@st.cache_data
def load_data():
    df = pd.read_csv("treasury_returns_dummy.csv", parse_dates=['Date'])
    return df

@st.cache_data
def load_portfolio():
    # Dummy portfolio data structure
    return pd.DataFrame([
        {"Start_Date": "2025-01-01", "End_Date": "2025-06-30", "Allocation": {"Short_Term": 0.70, "Medium_Term": 0.15, "Long_Term": 0.15}, "Portfolio_Value": 2100, "6M_Return": 5.0},
        {"Start_Date": "2025-07-01", "End_Date": "2025-12-31", "Allocation": {"Short_Term": 0.68, "Medium_Term": 0.15, "Long_Term": 0.17}, "Portfolio_Value": 2185, "6M_Return": 4.0},
        {"Start_Date": "2026-01-01", "End_Date": "2026-06-30", "Allocation": {"Short_Term": 0.66, "Medium_Term": 0.14, "Long_Term": 0.20}, "Portfolio_Value": 2280, "6M_Return": 4.3},
    ])

st.title("📊 Treasury Investment AI Dashboard")

portfolio_df = load_portfolio()
latest = portfolio_df.iloc[-1]
st.metric("📈 Latest Portfolio Value (₹ Cr)", f"{latest['Portfolio_Value']} Cr")
st.metric("📅 Period Return", f"{latest['6M_Return']}%")

# Portfolio Growth
st.subheader("💹 Portfolio Value Over Time")
portfolio_df['Start_Date'] = pd.to_datetime(portfolio_df['Start_Date'])
fig, ax = plt.subplots()
ax.plot(portfolio_df['Start_Date'], portfolio_df['Portfolio_Value'], marker='o')
ax.set_ylabel("Value (₹ Cr)")
ax.set_xlabel("Date")
ax.set_title("Portfolio Growth")
st.pyplot(fig)

# Allocation Change
st.subheader("📊 Allocation Changes Over Time")
allocations = pd.DataFrame(portfolio_df['Allocation'].tolist())
allocations['Period'] = portfolio_df['Start_Date'].dt.strftime('%b %Y')
allocations.set_index('Period', inplace=True)
st.bar_chart(allocations)

# Stress Tests
def simulate_stress_scenarios(base_value):
    stress_scenarios = {
        "Interest Rate Spike": -0.03,
        "Equity Drawdown": -0.10,
        "Inflation Shock": -0.02
    }
    results = {}
    for scenario, impact in stress_scenarios.items():
        if scenario == "Interest Rate Spike":
            adjusted = base_value * (1 + allocations.iloc[-1]['Short_Term'] * impact + allocations.iloc[-1]['Medium_Term'] * impact)
        elif scenario == "Equity Drawdown":
            adjusted = base_value * (1 + allocations.iloc[-1]['Long_Term'] * impact)
        elif scenario == "Inflation Shock":
            adjusted = base_value * (1 + impact)
        results[scenario] = round(adjusted, 2)
    return results

st.subheader("⚠️ Stress Test: Adverse Market Scenarios")
base_val = latest['Portfolio_Value']
stress_results = simulate_stress_scenarios(base_val)
st.bar_chart(pd.DataFrame.from_dict(stress_results, orient='index', columns=['Value After Shock']))

# Radar Chart Comparison
st.subheader("📌 Radar Chart: Compare AI Strategies")
metrics = ['Sharpe Ratio', 'Alpha', 'Beta', 'Volatility', 'Max Drawdown']
angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
angles += angles[:1]

# Dummy comparison data
strategies = {
    "AI Model A": [0.85, 0.07, 0.95, 0.12, 0.10],
    "AI Model B": [0.80, 0.05, 0.90, 0.13, 0.11],
    "Benchmark (NIFTY)": [0.60, 0.00, 1.00, 0.15, 0.12]
}

fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
for name, vals in strategies.items():
    vals += vals[:1]
    ax.plot(angles, vals, label=name)
    ax.fill(angles, vals, alpha=0.1)

ax.set_xticks(angles[:-1])
ax.set_xticklabels(metrics)
ax.set_yticklabels([])
ax.set_title('AI Strategy Performance Comparison', y=1.1)
ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))

st.pyplot(fig)

with st.expander("🔍 Show Raw Portfolio Data"):
    st.dataframe(portfolio_df)

st.caption("Powered by AI-driven Portfolio Optimization Model")
