import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go


def build_iv_surface(ticker: yf.ticker.Ticker):
    """
    Builds an implied volatility surface from an underlying
    
    Parameters:
    - ticker: yfinance Ticker object, represents a stock
    Returns:
    - pd.DataFrame with columns: Strike, Maturity, IV
    """
    iv_surface_data = []
    now = datetime.now()
    ticker._download_options() # important to get expiration dates from ticker._expiratoins
    expirations = ticker._expirations # dict: {'2025-03-28': epoch_time, ...}

    for expiry_str in expirations.keys():
        try:
            df = ticker.option_chain(expiry_str).puts # strikes and vols for calls are about the same
            maturity_date = datetime.strptime(expiry_str, "%Y-%m-%d")
            T = (maturity_date - now).days / 365.0

            strikes = df["strike"]
            vols = df["impliedVolatility"]

            for K, iv in zip(strikes, vols):
                if not np.isnan(iv):
                    iv_surface_data.append((K, T, iv))

        except Exception as e:
            print(f"Error processing {expiry_str}: {e}")
            continue # go to next iteration

    return pd.DataFrame(iv_surface_data, columns=["Strike", "Maturity", "IV"])


def plot_iv_surface(iv_df: pd.DataFrame):
    """
    Builds implied volatility surface from a  plots it as a 3D surface using Plotly
    Parameters:
    - iv_df: pd.DataFrame of the volatility surface to plot
    """
    
    assert not iv_df.empty, "No implied volatility data found. Cannot plot"

    df_pivot = iv_df.pivot(index="Strike", columns="Maturity", values="IV") # pivot the DataFrame to extract fields domains

    fig = go.Figure(data=[
        go.Surface(
            x = df_pivot.index.values, # strike
            y = df_pivot.columns.values, # maturity in years
            z = df_pivot.values # implied vol
        )
    ])

    fig.update_layout(
        title="Implied Volatility Surface",
        scene=dict(
            xaxis_title="Strike",
            yaxis_title="Time to Maturity (Years)",
            zaxis_title="Implied Volatility"
        ),
        autosize=True
    )

    fig.show()
