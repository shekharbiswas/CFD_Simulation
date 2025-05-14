# cfd_cost_model.py

import numpy as np

def calculate_margin(num_contracts, index_price, config):
    """Calculates margin based on tiered structure in config."""
    if num_contracts <= 0 or index_price <= 0 or np.isnan(num_contracts) or np.isnan(index_price):
        return 0.0

    lot_size = config['lot_size']
    margin_tiers = config['margin_tiers']
    notional_value = num_contracts * index_price * lot_size
    margin = 0.0
    contracts_remaining = num_contracts
    last_limit = 0.0

    for tier in sorted(margin_tiers, key=lambda x: x['limit']):
        tier_limit_contracts = tier['limit'] - last_limit
        contracts_in_this_tier = min(contracts_remaining, tier_limit_contracts)

        if contracts_in_this_tier > 0:
            margin += contracts_in_this_tier * index_price * lot_size * tier['rate']
            contracts_remaining -= contracts_in_this_tier
            last_limit = tier['limit']

        if contracts_remaining <= 0:
            break # Stop if all contracts are accounted for

    # Failsafe for NaN/inf and ensure margin <= notional
    if np.isnan(margin) or np.isinf(margin):
        print(f"Warning: Invalid margin calculated ({margin}). Falling back.")
        return min(notional_value, config.get('initial_capital', 1e9)) # Or another failsafe
    return min(margin, notional_value)


def calculate_daily_financing_cost(contracts, price, sofr_rate, config, is_short):
    """ Calculates daily financing cost/credit based on config """
    if contracts <= 0 or price <= 0 or np.isnan(contracts) or np.isnan(price) or np.isnan(sofr_rate):
        return 0.0

    lot_size = config['lot_size']
    fee = config['broker_annual_financing_fee']
    days = config['days_in_year_financing']
    notional = contracts * lot_size * price

    if is_short:
        # Short positions: receive (SOFR - fee) if positive, pay if negative
        annual_rate = sofr_rate - fee
        # Note: Cost is negative if it's a credit (rate > 0), positive if cost (rate < 0)
        financing_adjustment = (notional * annual_rate) / days
        # Return value: positive = cost to portfolio, negative = credit to portfolio
        return -financing_adjustment # Flip sign to match convention
    else:
        # Long positions: pay (SOFR + fee)
        annual_rate = sofr_rate + fee
        financing_cost = (notional * annual_rate) / days
        return financing_cost


def calculate_daily_borrowing_cost(contracts, price, config, is_short):
    """ Calculates daily borrowing cost for short positions based on config """
    if not is_short or contracts <= 0 or price <= 0 or np.isnan(contracts) or np.isnan(price):
        return 0.0

    lot_size = config['lot_size']
    borrow_rate = config['borrowing_cost_annual']
    days = config['days_in_year_financing'] # Or maybe 365? Source used 360.
    notional = contracts * lot_size * price
    borrowing_cost = (notional * borrow_rate) / days
    return borrowing_cost

def calculate_spread_cost(contracts_closed, config):
    """ Calculates spread cost for closing contracts """
    if contracts_closed <= 0 or np.isnan(contracts_closed):
        return 0.0
    return contracts_closed * config['lot_size'] * config['avg_spread_points']

if __name__ == '__main__':
     # Example requires config_loader
    from config_loader import load_config
    try:
        cfg = load_config('../../config/params.yaml') # Adjust path
        print("\nCost Model Examples:")
        print(f"Margin for 10 contracts at 4000: {calculate_margin(10, 4000, cfg):.2f}")
        print(f"Margin for 30 contracts at 4000: {calculate_margin(30, 4000, cfg):.2f}")
        print(f"Financing (short, SOFR=0.015): {calculate_daily_financing_cost(10, 4000, 0.015, cfg, True):.2f}") # Should be credit
        print(f"Financing (short, SOFR=0.05): {calculate_daily_financing_cost(10, 4000, 0.05, cfg, True):.2f}") # Should be more credit
        print(f"Financing (long, SOFR=0.015): {calculate_daily_financing_cost(10, 4000, 0.015, cfg, False):.2f}") # Should be cost
        print(f"Borrowing (short): {calculate_daily_borrowing_cost(10, 4000, cfg, True):.2f}")
        print(f"Borrowing (long): {calculate_daily_borrowing_cost(10, 4000, cfg, False):.2f}")
        print(f"Spread cost closing 10 contracts: {calculate_spread_cost(10, cfg):.2f}")
    except Exception as e:
        print(f"Failed cost model tests: {e}")
