# hedging_strategy.py

import numpy as np

def get_hedge_action(vix_level, current_equity, current_price, is_currently_hedged, config):
    """
    Determines the target hedge action based on VIX level and configuration.
    Returns the target number of short CFD contracts.
    """
    vix_threshold = config['hedging_strategy']['vix_threshold']
    hedge_ratio = config['hedging_strategy']['hedge_ratio']
    lot_size = config['lot_size']

    target_contracts = 0.0 # Default: no hedge

    if vix_level > vix_threshold:
        # Condition to hedge is met
        if current_equity > 0 and current_price > 0 and lot_size > 0:
            target_notional = current_equity * hedge_ratio
            target_contracts = target_notional / (current_price * lot_size)
            if np.isnan(target_contracts) or np.isinf(target_contracts):
                 target_contracts = 0.0 # Safety check
                 print(f"Warning: Invalid target contracts calculated. Setting to 0.")
        else:
            target_contracts = 0.0 # Cannot hedge if price or equity is zero/negative
            # print(f"Debug: Cannot calculate hedge contracts. Equity={current_equity}, Price={current_price}")
    else:
        # Condition to hedge is NOT met, target is zero contracts
        target_contracts = 0.0

    # Simple logic: Hedge if VIX > threshold, otherwise target zero hedge.
    # More complex logic (persistence, trends) could be added here.

    return target_contracts

if __name__ == '__main__':
    # Example requires config_loader
    from config_loader import load_config
    try:
        cfg = load_config('../../config/params.yaml') # Adjust path
        print("\nHedging Strategy Examples:")
        # Should hedge
        print(f"VIX=30, Equity=1M, Price=4000: Target Contracts = {get_hedge_action(30, 1000000, 4000, False, cfg):.2f}")
        # Should NOT hedge
        print(f"VIX=20, Equity=1M, Price=4000: Target Contracts = {get_hedge_action(20, 1000000, 4000, True, cfg):.2f}")
        # Edge case
        print(f"VIX=30, Equity=0, Price=4000: Target Contracts = {get_hedge_action(30, 0, 4000, False, cfg):.2f}")

    except Exception as e:
        print(f"Failed hedging strategy tests: {e}")
