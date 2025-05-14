# simulation_engine.py

import pandas as pd
import numpy as np
from scripts import cfd_cost_model as costs
from scripts import hedging_strategy as strategy

def simulate_classic_portfolio(df, config):
    """Simulates the classic buy-and-hold portfolio (Model A)."""
    initial_capital = config['initial_capital']
    equity_alloc = config['equity_allocation']
    sp500_col = config['sp500_column'] # Used for info if needed, logic uses return col

    equity_A = initial_capital * equity_alloc
    cash_A = initial_capital * (1.0 - equity_alloc)
    portfolio_A_values = []
    dates_A = []

    # Use pre-calculated SP500_Return column
    sim_data = df[['SP500_Return']].copy()
    current_equity = equity_A # Initialize

    # Add initial state
    if not sim_data.empty:
        initial_date = sim_data.index[0]
        portfolio_A_values.append(initial_capital)
        # Use previous day for initial state timestamp if possible
        dates_A.append(initial_date - pd.Timedelta(days=1))

    for date, row in sim_data.iterrows():
        # Equity value changes with market return
        return_val = row['SP500_Return']
        if pd.isna(return_val): # Handle potential NaNs in returns
            print(f"Warning: NaN return found on {date}. Holding equity constant.")
        else:
            current_equity *= (1 + return_val)

        portfolio_value = current_equity + cash_A # Cash is constant
        if pd.isna(portfolio_value): # Failsafe
            print(f"Warning: NaN portfolio value on {date}. Reverting.")
            portfolio_value = portfolio_A_values[-1] if portfolio_A_values else initial_capital

        portfolio_A_values.append(portfolio_value)
        dates_A.append(date)

    if not dates_A: return pd.Series(name="Portfolio_A", dtype=float)

    portfolio_A = pd.Series(portfolio_A_values, index=pd.DatetimeIndex(dates_A), name="Portfolio_A")
    print("Classic portfolio (Model A) simulation complete.")
    return portfolio_A


def simulate_hedged_portfolio(df, config):
    """Simulates the CFD-hedged portfolio (Model B)."""
    initial_capital = config['initial_capital']
    equity_alloc = config['equity_allocation']
    sp500_col = config['sp500_column']
    vix_col = config['vix_column']
    sofr_col = config['sofr_column']

    equity_B = initial_capital * equity_alloc
    cash_B = initial_capital * (1.0 - equity_alloc)
    portfolio_B_values = []
    dates_B = []
    cost_data = [] # Store detailed daily costs

    current_equity = equity_B # Track equity portion

    # Hedging state variables
    current_contracts = 0.0 # Number of short CFD contracts held
    margin_held = 0.0

    # Add initial state
    if not df.empty:
        initial_date = df.index[0]
        portfolio_B_values.append(initial_capital)
        dates_B.append(initial_date - pd.Timedelta(days=1))
        cost_data.append({'date': initial_date - pd.Timedelta(days=1), 'Financing': 0, 'Borrowing': 0, 'Spread': 0, 'Total': 0, 'Contracts': 0, 'Margin': 0})

    # Iterate through data
    sim_data = df[['SP500_Return', sp500_col, 'Prev_S&P500', vix_col, sofr_col]].copy()

    for date, row in sim_data.iterrows():
        # --- 1. Update Equity Value ---
        sp_return = row['SP500_Return']
        if pd.notna(sp_return):
            equity_gain_loss = current_equity * sp_return
            current_equity += equity_gain_loss
        else:
            print(f"Warning: NaN S&P500 return on {date}. Equity value held constant.")
            equity_gain_loss = 0

        # --- 2. Calculate P&L and Costs for Existing Hedge (from yesterday) ---
        daily_cfd_pnl = 0.0
        financing_cost = 0.0
        borrowing_cost = 0.0
        spread_cost_today = 0.0

        prev_price = row['Prev_S&P500']
        current_price = row[sp500_col]
        sofr_rate = row[sofr_col]
        vix_level = row[vix_col]

        # Check for valid data needed for cost/PnL calcs
        if current_contracts > 0 and pd.notna(prev_price) and prev_price > 0 and pd.notna(current_price) and current_price > 0 and pd.notna(sofr_rate):
            # P&L on short CFD (based on price change from prev close to current close)
            daily_cfd_pnl = current_contracts * config['lot_size'] * (prev_price - current_price)

            # Overnight financing cost/credit (applied for holding position into today)
            financing_cost = costs.calculate_daily_financing_cost(
                current_contracts, prev_price, sofr_rate, config, is_short=True
            )
            # Overnight borrowing cost
            borrowing_cost = costs.calculate_daily_borrowing_cost(
                current_contracts, prev_price, config, is_short=True
            )

            # Update cash *before* deciding today's action
            cash_B += daily_cfd_pnl - financing_cost - borrowing_cost
        else:
            # Handle cases where PnL/costs cannot be calculated (e.g., first day, missing data)
             if current_contracts > 0:
                 print(f"Warning: Could not calculate PnL/Costs on {date} for {current_contracts} contracts. Missing data?")


        # --- 3. Determine Target Hedge for Today ---
        target_contracts = 0.0
        if pd.notna(vix_level) and pd.notna(current_price) and current_price > 0 and pd.notna(current_equity):
             is_currently_hedged = current_contracts > 0
             target_contracts = strategy.get_hedge_action(vix_level, current_equity, current_price, is_currently_hedged, config)
        else:
             print(f"Warning: Cannot determine hedge action on {date}. Missing VIX/Price/Equity?")
             target_contracts = current_contracts # Maintain current state if decision data missing

        # --- 4. Execute Hedge Changes ---
        contracts_change = target_contracts - current_contracts

        if abs(contracts_change) > 1e-6: # If there's a change needed (using tolerance for float comparison)
            if contracts_change < 0: # Closing some or all contracts
                contracts_closed = abs(contracts_change)
                # Apply spread cost for contracts being closed
                spread_cost_today = costs.calculate_spread_cost(contracts_closed, config)
                cash_B -= spread_cost_today
                # print(f"{date}: Closing {-contracts_change:.2f} contracts. Spread Cost: {spread_cost_today:.2f}")

            # Update contract count to the target
            current_contracts = target_contracts

        # --- 5. Calculate and Adjust Margin ---
        new_margin_required = 0.0
        if current_contracts > 0 and pd.notna(current_price) and current_price > 0:
             new_margin_required = costs.calculate_margin(current_contracts, current_price, config)
        else: # Ensure current_contracts is explicitly 0 if price is invalid
             current_contracts = 0.0


        margin_change = new_margin_required - margin_held

        if abs(margin_change) > 1e-6:
            # Check if sufficient cash for margin increase
            if margin_change > 0 and cash_B < margin_change:
                # Insufficient cash! Force close position or handle differently.
                # Simple approach: Cannot meet margin call, assume we close the position.
                print(f"WARN {date}: Insufficient cash ({cash_B:.2f}) for margin increase ({margin_change:.2f}). Forcing close hedge.")
                spread_cost_today += costs.calculate_spread_cost(current_contracts, config) # Cost to close
                cash_B -= spread_cost_today
                cash_B += margin_held # Release old margin
                current_contracts = 0.0
                margin_held = 0.0
                new_margin_required = 0.0
                margin_change = new_margin_required - margin_held # Now margin_change is likely negative or zero

            # Adjust cash and margin held
            cash_B -= margin_change # If margin increases, cash decreases. If margin decreases, cash increases.
            margin_held = new_margin_required


        # --- 6. Store Daily Costs & State ---
        cost_data.append({
            'date': date,
            'Financing': financing_cost,
            'Borrowing': borrowing_cost,
            'Spread': spread_cost_today,
            'Total': financing_cost + borrowing_cost + spread_cost_today,
            'Contracts': current_contracts,
            'Margin': margin_held
        })

        # --- 7. Calculate Total Portfolio Value ---
        portfolio_value = current_equity + cash_B + margin_held # Equity + Free Cash + Margin Cash
        if pd.isna(portfolio_value): # Failsafe
            print(f"Warning: NaN portfolio value on {date}. Equity:{current_equity}, Cash:{cash_B}, Margin:{margin_held}. Reverting.")
            portfolio_value = portfolio_B_values[-1] if portfolio_B_values else initial_capital

        portfolio_B_values.append(portfolio_value)
        dates_B.append(date)


    if not dates_B: return pd.Series(name="Portfolio_B", dtype=float), pd.DataFrame()

    portfolio_B = pd.Series(portfolio_B_values, index=pd.DatetimeIndex(dates_B), name="Portfolio_B")
    cost_df = pd.DataFrame(cost_data).set_index('date')

    print("Hedged portfolio (Model B) simulation complete.")
    return portfolio_B, cost_df
