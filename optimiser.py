import pandas as pd
import numpy as np
from pypfopt import EfficientFrontier, risk_models, expected_returns

# Load data
df = pd.read_csv("treasury_returns_dummy.csv", parse_dates=['Date'])
df.set_index('Date', inplace=True)

rebalance_window = 13  # 6 months (bi-weekly returns)
initial_investment = 2000
current_value = initial_investment
portfolio_history = []

for start in range(0, len(df) - rebalance_window, rebalance_window):
    end = start + rebalance_window
    window_returns = df.iloc[start:end]

    mu = expected_returns.mean_historical_return(window_returns, frequency=26)
    S = risk_models.sample_cov(window_returns, frequency=26)

    ef = EfficientFrontier(mu, S)
    ef.add_constraint(lambda w: w[0] <= 0.70)  # Short-Term
    ef.add_constraint(lambda w: w[1] <= 0.15)  # Medium-Term
    ef.add_constraint(lambda w: w[2] <= 0.15)  # Long-Term

    weights = ef.max_sharpe()
    cleaned_weights = ef.clean_weights()

    next_window = df.iloc[end:end + rebalance_window]
    if not next_window.empty:
        returns = next_window[list(cleaned_weights.keys())]
        weighted_returns = returns.dot(np.array(list(cleaned_weights.values())))
        total_return = np.prod(1 + weighted_returns) - 1
        current_value *= (1 + total_return)

        portfolio_history.append({
            "Start_Date": window_returns.index[0],
            "End_Date": next_window.index[-1],
            "Allocation": cleaned_weights,
            "Portfolio_Value": round(current_value, 2),
            "6M_Return": round(total_return * 100, 2)
        })

portfolio_df = pd.DataFrame(portfolio_history)
print(portfolio_df)
