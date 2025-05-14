# config_loader.py

import yaml
import os

def load_config(config_path='config/params.yaml'):
    """Loads the YAML configuration file."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found at {config_path}")
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        print("Configuration loaded successfully.")
        return config
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        raise
    except Exception as e:
        print(f"An error occurred while loading config: {e}")
        raise

if __name__ == '__main__':
    # Example usage
    try:
        cfg = load_config()
        print("\nLoaded Config Example:")
        print(f"Initial Capital: {cfg.get('initial_capital')}")
        print(f"VIX Threshold: {cfg.get('hedging_strategy', {}).get('vix_threshold')}")
        print(f"Data file: {cfg.get('data_file')}")
    except Exception as e:
        print(f"Failed to load config: {e}")
