import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def plot_market_data(df_plot, title="S&P 500 Index and VIX Over Time"):
    """Plots S&P 500 and VIX on a dual-axis chart."""
    if df_plot.empty:
        print("Cannot plot market data: DataFrame is empty.")
        return
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(x=df_plot['date'], y=df_plot['S&P500'], name="S&P 500 Index", line=dict(color='blue')),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=df_plot['date'], y=df_plot['VIX'], name="VIX Index", line=dict(color='red')),
        secondary_y=True,
    )
    fig.update_layout(
        title_text=title,
        xaxis_rangeslider_visible=True
    )
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="<b>S&P 500 Index Value</b>", secondary_y=False, color="blue")
    fig.update_yaxes(title_text="<b>VIX Level</b>", secondary_y=True, color="red")
    fig.show()

def plot_portfolio_performance(df_plot, title="Portfolio Performance", color_map=None):
    """Plots portfolio performance over time."""
    if df_plot.empty:
        print("Cannot plot portfolio performance: DataFrame is empty.")
        return

    fig = px.line(df_plot, x='date', y='Value', color='Portfolio', title=title, color_discrete_map=color_map)
    fig.show()

def plot_covid_recovery(df_plot, trough_A_date, trough_A_value, trough_B_date, trough_B_value, 
                        portfolio_A_label, portfolio_B_label, 
                        color_A, color_B, title="COVID Crisis & Recovery Performance"):
    """Plots portfolio performance during COVID crisis and recovery, highlighting troughs."""
    if df_plot.empty:
        print("Cannot plot COVID recovery: DataFrame is empty.")
        return

    fig = px.line(df_plot, x='date', y='Value', color='Portfolio', 
                  title=title,
                  color_discrete_map={portfolio_A_label: color_A, portfolio_B_label: color_B})

    # Add markers for troughs if data is available
    if trough_A_date and trough_A_value is not None:
        fig.add_trace(go.Scatter(
            x=[trough_A_date], y=[trough_A_value],
            mode='markers', name=f'Trough {portfolio_A_label}',
            marker=dict(color=color_A, size=10, symbol='circle-open')
        ))
    if trough_B_date and trough_B_value is not None:
        fig.add_trace(go.Scatter(
            x=[trough_B_date], y=[trough_B_value],
            mode='markers', name=f'Trough {portfolio_B_label}',
            marker=dict(color=color_B, size=10, symbol='diamond-open')
        ))
    fig.show()