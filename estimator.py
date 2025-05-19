import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# --- Monte Carlo Simulation Section ---
def monte_carlo_simulation():
    np.random.seed(42)
    initial_investment = 2000  # Cr
    n_years = 10
    n_simulations = 500
    mean_return = 0.072
    volatility = 0.12

    simulated_end_values = []

    for _ in range(n_simulations):
        returns = np.random.normal(
            loc=mean_return / n_years,
            scale=volatility / np.sqrt(n_years),
            size=n_years * 12
        )
        growth = initial_investment * np.cumprod(1 + returns)
        simulated_end_values.append(growth[-1])

    # Plotting
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(simulated_end_values, bins=40, color='skyblue', edgecolor='black')
    ax.axvline(np.percentile(simulated_end_values, 5), color='red', linestyle='dashed', linewidth=2, label='5th Percentile (Downside Risk)')
    ax.axvline(np.mean(simulated_end_values), color='green', linestyle='dashed', linewidth=2, label='Mean Expected Value')
    ax.axvline(np.percentile(simulated_end_values, 95), color='orange', linestyle='dashed', linewidth=2, label='95th Percentile (Optimistic)')

    ax.set_title("📈 Monte Carlo Simulated Return Distribution (10 Years)")
    ax.set_xlabel("Portfolio Value (₹ Cr)")
    ax.set_ylabel("Frequency")
    ax.legend()
    ax.grid(True)

    return fig

# Display Monte Carlo Simulation
st.subheader("📊 Monte Carlo Simulation – Return Forecast (10 Years)")
st.pyplot(monte_carlo_simulation())

# --- Sankey Diagram Section ---
st.subheader("🔄 Treasury Fund Flow Allocation (Interactive)")

# Input Sliders for user-defined allocations (total = 2000 Cr)
short_term = st.slider("Short-Term Allocation (Cr)", 0, 2000, 1400, step=100)
medium_term = st.slider("Medium-Term Allocation (Cr)", 0, 2000 - short_term, 300, step=100)
long_term = 2000 - short_term - medium_term

st.markdown(f"**Long-Term Allocation Auto-Adjusted: ₹{long_term} Cr**")

# Allocation within categories
fd = int(short_term * 0.57)
cp = short_term - fd

gsec = int(medium_term * 0.6)
corp_bond = medium_term - gsec

mf = int(long_term * 0.6)
etf = long_term - mf

labels = [
    "Treasury ₹2000 Cr",
    "Short-Term", "Medium-Term", "Long-Term",
    "FDs", "CPs", "G-Secs", "Corporate Bonds", "Mutual Funds", "ETFs"
]

source = [0, 0, 0, 1, 1, 2, 2, 3, 3]
target = [1, 2, 3, 4, 5, 6, 7, 8, 9]
values = [short_term, medium_term, long_term, fd, cp, gsec, corp_bond, mf, etf]

hover_text = [
    f"From {labels[s]} to {labels[t]}<br>₹{v} Cr<br>{(v/2000)*100:.1f}% of total"
    for s, t, v in zip(source, target, values)
]

fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=20,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=labels,
        color=["#1f77b4"] + ["#2ca02c"] * 3 + ["#ff7f0e"] * 6
    ),
    link=dict(
        source=source,
        target=target,
        value=values,
        hovertemplate=hover_text
    )
)])

fig.update_layout(title_text="Dynamic Treasury Allocation Sankey", font_size=12)
st.plotly_chart(fig, use_container_width=True)
