# plotting.py

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import os
import numpy as np # Import numpy

def plot_portfolio_comparison(portfolio_a, portfolio_b, config):
    """Generates the portfolio value comparison plot."""
    fig, ax = plt.subplots(figsize=(14, 7))
    initial_capital = config['initial_capital']

    if portfolio_a.empty or portfolio_b.empty:
        ax.text(0.5, 0.5, 'No simulation data to plot', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
        return fig

    comparison = pd.concat([portfolio_a, portfolio_b], axis=1).ffill().dropna() # Forward fill for plotting continuity
    if comparison.empty:
        ax.text(0.5, 0.5, 'No common dates to plot', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
        return fig

    # Normalize values for comparison
    ax.plot(comparison.index, comparison['Portfolio_A'] / initial_capital, label='Model A (Classic)', linewidth=1.5)
    ax.plot(comparison.index, comparison['Portfolio_B'] / initial_capital, label='Model B (CFD-Hedged)', linewidth=1.5, alpha=0.8)

    # Highlight crisis periods
    for name, period in config.get('crisis_periods', {}).items():
        color = 'red' if 'covid' in name.lower() else 'orange'
        label = f"{name.replace('_',' ').title()} Crisis"
        ax.axvspan(period['start'], period['end'], color=color, alpha=0.15, label=label)

    ax.set_title('Portfolio Value Comparison (Normalized)', fontsize=16)
    ax.set_ylabel('Portfolio Value / Initial Capital', fontsize=12)
    ax.set_xlabel('Date', fontsize=12)
    # Avoid duplicate labels in legend
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), fontsize=10)

    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(x, ',.2f')))
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.xaxis.set_minor_locator(mdates.MonthLocator(interval=3))
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig

def plot_vix(df_data, config):
    """Generates the VIX index plot."""
    fig, ax = plt.subplots(figsize=(14, 4))
    vix_col = config['vix_column']
    threshold = config['hedging_strategy']['vix_threshold']

    if vix_col not in df_data.columns:
        ax.text(0.5, 0.5, 'VIX data not found', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
        return fig

    vix_series = df_data[vix_col].dropna()
    if vix_series.empty:
        ax.text(0.5, 0.5, 'No VIX data to plot', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
        return fig

    ax.plot(vix_series.index, vix_series, label='VIX Index', color='purple', linewidth=1)
    ax.axhline(threshold, color='red', linestyle='--', linewidth=1, label=f'VIX Threshold ({threshold})')
    ax.set_title('VIX Index and Hedging Threshold', fontsize=14)
    ax.set_ylabel('VIX Value', fontsize=10)
    ax.set_xlabel('Date', fontsize=10)
    ax.legend(fontsize=9)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.xaxis.set_minor_locator(mdates.MonthLocator(interval=3))
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig

def plot_costs(cost_df):
    """Generates the cumulative costs plot for Model B."""
    fig, ax = plt.subplots(figsize=(14, 4))

    if cost_df.empty or not all(col in cost_df.columns for col in ['Financing', 'Borrowing', 'Spread', 'Total']):
         ax.text(0.5, 0.5, 'Cost data not available or incomplete', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
         return fig

    # Ensure costs are numeric and handle potential NaNs
    cost_df_numeric = cost_df[['Financing', 'Borrowing', 'Spread', 'Total']].apply(pd.to_numeric, errors='coerce').fillna(0)

    # Check if Series are empty after potential dropping/filling
    if cost_df_numeric.empty:
         ax.text(0.5, 0.5, 'No valid cost data to plot', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
         return fig

    ax.plot(cost_df_numeric.index, cost_df_numeric['Financing'].cumsum(), label='Cumulative Financing Costs', linewidth=1)
    ax.plot(cost_df_numeric.index, cost_df_numeric['Borrowing'].cumsum(), label='Cumulative Borrowing Costs', linewidth=1)
    ax.plot(cost_df_numeric.index, cost_df_numeric['Spread'].cumsum(), label='Cumulative Spread Costs', linewidth=1)
    ax.plot(cost_df_numeric.index, cost_df_numeric['Total'].cumsum(), label='Total Cumulative Costs', linewidth=1.5, color='black')
    ax.set_title('Cumulative Trading Costs for Model B', fontsize=14)
    ax.set_ylabel('Cumulative Cost (USD)', fontsize=10)
    ax.set_xlabel('Date', fontsize=10)
    ax.legend(fontsize=9)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.xaxis.set_minor_locator(mdates.MonthLocator(interval=3))
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig

def plot_contracts_margin(cost_df):
    """ Plots the number of contracts and margin held over time for Model B """
    fig, ax1 = plt.subplots(figsize=(14, 4))

    if cost_df.empty or not all(col in cost_df.columns for col in ['Contracts', 'Margin']):
         ax1.text(0.5, 0.5, 'Contracts/Margin data not available', horizontalalignment='center', verticalalignment='center', transform=ax1.transAxes)
         return fig

    cost_df_numeric = cost_df[['Contracts', 'Margin']].apply(pd.to_numeric, errors='coerce').fillna(0)
    if cost_df_numeric.empty:
         ax1.text(0.5, 0.5, 'No valid Contracts/Margin data to plot', horizontalalignment='center', verticalalignment='center', transform=ax1.transAxes)
         return fig


    color = 'tab:red'
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Number of Short Contracts', color=color, fontsize=10)
    # Ensure index is datetime
    ax1.plot(pd.to_datetime(cost_df_numeric.index), cost_df_numeric['Contracts'], color=color, label='Short Contracts', linewidth=1.5)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True, which='both', linestyle='--', linewidth=0.5, axis='x') # Grid only for x-axis from first plot

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    color = 'tab:blue'
    ax2.set_ylabel('Margin Held (USD)', color=color, fontsize=10)  # we already handled the x-label with ax1
    ax2.plot(pd.to_datetime(cost_df_numeric.index), cost_df_numeric['Margin'], color=color, label='Margin Held', linewidth=1.5, alpha=0.7)
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))

    # Add legends - get handles and labels from both axes
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='upper left', fontsize=9)

    ax1.set_title('Hedged Portfolio (Model B): Contracts Held and Margin', fontsize=14)
    ax1.xaxis.set_major_locator(mdates.YearLocator())
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax1.xaxis.set_minor_locator(mdates.MonthLocator(interval=3))
    plt.xticks(rotation=45)
    fig.tight_layout() # Otherwise the right y-label is slightly clipped
    return fig


def save_plot(fig, filename, config):
    """Saves a matplotlib figure."""
    if config.get('save_plots', False):
        output_dir = config.get('plot_output_dir', 'outputs/plots')
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        try:
            fig.savefig(filepath, bbox_inches='tight')
            print(f"Plot saved to {filepath}")
        except Exception as e:
            print(f"Error saving plot {filename}: {e}")
