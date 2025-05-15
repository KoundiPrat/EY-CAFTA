import streamlit as st
import numpy as np
import matplotlib.pyplot as plt


np.random.seed(42)

st.title(" Treasury Investment Strategy Simulator (India - 10 Year Horizon)")

st.sidebar.header("Investment Inputs")


total_corpus = st.sidebar.number_input("Total Corpus (in ₹ crore)", value=2000)
short_pct = st.sidebar.slider("Short-term Allocation (%)", 0, 100, 70)
medium_pct = st.sidebar.slider("Medium-term Allocation (%)", 0, 100 - short_pct, 15)
long_pct = 100 - short_pct - medium_pct
st.sidebar.markdown(f"**Long-term Allocation (%)**: {long_pct}")

years = st.sidebar.slider("Investment Horizon (Years)", 5, 20, 10)
inflation_rate = st.sidebar.slider("Annual Inflation Rate (%)", 0.0, 10.0, 5.0) / 100
risk_free_rate = st.sidebar.slider("Risk-Free Rate (%)", 0.0, 10.0, 6.0) / 100
rebalance_annually = st.sidebar.checkbox("Enable Annual Rebalancing", value=True)
simulations = st.sidebar.slider("Number of Simulations", 100, 5000, 1000)


allocations = {
    "short_term": short_pct / 100 * total_corpus,
    "medium_term": medium_pct / 100 * total_corpus,
    "long_term": long_pct / 100 * total_corpus
}


investment_profiles = {
    "short_term": {"mean_return": 0.06, "volatility": 0.01},
    "medium_term": {"mean_return": 0.07, "volatility": 0.015},
    "long_term": {"mean_return": 0.11, "volatility": 0.05}
}


def monte_carlo_simulation(allocs, profiles, years, sims, rebalance, inflation):
    final_results = []
    annual_returns_all = []
    drawdowns_all = []

    for _ in range(sims):
        portfolio = allocs.copy()
        values = []
        annual_returns = []

        for _ in range(years):
            total_before = sum(portfolio.values())
            yearly_return = 0

            for mode in portfolio:
                r = np.random.normal(profiles[mode]["mean_return"], profiles[mode]["volatility"])
                portfolio[mode] *= (1 + r)
                yearly_return += r * (portfolio[mode] / sum(portfolio.values()))

            values.append(sum(portfolio.values()))
            annual_returns.append(yearly_return)

            if rebalance:
                total_now = sum(portfolio.values())
                portfolio = {
                    "short_term": (short_pct / 100) * total_now,
                    "medium_term": (medium_pct / 100) * total_now,
                    "long_term": (long_pct / 100) * total_now
                }

        
        values = np.array(values)
        peak = np.maximum.accumulate(values)
        drawdown = (peak - values) / peak
        max_drawdown = np.max(drawdown)
        drawdowns_all.append(max_drawdown)

        final_value = values[-1] / ((1 + inflation) ** years)
        final_results.append(final_value)
        annual_returns_all.extend(annual_returns)

    return np.array(final_results), np.array(annual_returns_all), np.array(drawdowns_all)


results, annual_returns, drawdowns = monte_carlo_simulation(
    allocations, investment_profiles, years, simulations, rebalance_annually, inflation_rate
)


mean_val = np.mean(results)
cagr = (mean_val / total_corpus) ** (1 / years) - 1
target_val = total_corpus * ((1 + 0.072) ** years) / ((1 + inflation_rate) ** years)
percent_above_target = np.sum(results >= target_val) / simulations * 100


excess_returns = annual_returns - risk_free_rate
sharpe_ratio = np.mean(excess_returns) / np.std(excess_returns)


fig, ax = plt.subplots(figsize=(10, 5))
ax.hist(results, bins=50, color='skyblue', edgecolor='black')
ax.axvline(np.percentile(results, 5), color='red', linestyle='--', label='5th percentile')
ax.axvline(np.percentile(results, 95), color='green', linestyle='--', label='95th percentile')
ax.axvline(target_val, color='black', linestyle='-', label='Target Return (Real)')
ax.set_title("Monte Carlo Simulation: Portfolio Value After 10 Years (Real, Inflation-adjusted)")
ax.set_xlabel("Portfolio Value (₹ crore)")
ax.set_ylabel("Frequency")
ax.legend()
st.pyplot(fig)


st.subheader("📈 Results Summary")
st.write(f"**Average Final Portfolio Value (real): ₹{mean_val:.2f} Cr**")
st.write(f"**Expected CAGR (real): {cagr * 100:.2f}%**")
st.write(f"**Probability of ≥7.2% Real Return Target: {percent_above_target:.1f}%**")
st.write(f"**Average Sharpe Ratio (vs {risk_free_rate*100:.1f}% risk-free): {sharpe_ratio:.2f}**")
st.write(f"**Average Max Drawdown: {np.mean(drawdowns) * 100:.2f}%**")
