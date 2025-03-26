import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
from scipy.interpolate import griddata


class ImpliedVolSurfaceBuilder:
    """
    A class to build and plot an implied volatility surface using data from
    a yfinance Ticker object.

    Attributes
    ----------
    ticker : yf.Ticker
        YFinance Ticker object.
    iv_df : Optional[pd.DataFrame]
        Internal storage for the fetched and cleaned IV data. Once you call
        build_surface(), the data are stored here.
    """

    def __init__(self, ticker_name: str):
        """
        Initialize the ImpliedVolSurfaceBuilder with a Ticker object.

        Parameters
        ----------
        ticker_name : str
            Ticker name of a stock
        """

        ticker = yf.Ticker(ticker_name)

        df_raw = self._fetch_raw_data(ticker)
        df_cleaned = self._clean_data(df_raw)
        self.dataframe = df_cleaned

    def _fetch_raw_data(self, ticker: yf.Ticker) -> pd.DataFrame:
        """
        Internal method to fetch raw implied volatility data from the Ticker object.

        Parameters
        ----------
        ticker : yf.Ticker
            YFinance Ticker object from which option data will be fetched.

        Returns
        -------
        pd.DataFrame
            A DataFrame containing Strike, Maturity (in years), and IV.
        """
        now = datetime.now()
        ticker._download_options() # important in order to get expiration dates

        expirations = ticker._expirations # dict: {'2025-03-28': epoch_time, ...}

        surface_data = []
        for expiry_str in expirations.keys():  # dict: {'yyyy-mm-dd': epoch_time, ...}:
            try:
                maturity_date = datetime.strptime(expiry_str, "%Y-%m-%d")
                T = (maturity_date - now).days / 365.0
                df_chain = ticker.option_chain(expiry_str).puts

                for K, iv in zip(df_chain["strike"], df_chain["impliedVolatility"]):
                    surface_data.append((K, T, iv))

            except Exception as e:
                print(f"Error processing {expiry_str}: {e}")
                continue

        return pd.DataFrame(surface_data, columns=["Strike", "Maturity", "IV"])

    def _clean_data(self, df: pd.DataFrame, jump_threshold: float = 0.1) -> pd.DataFrame:
        """
        Internal method to clean the raw data by removing jumps in volatility.
        yfinance implied vol data sometimes contains jumps.

        Parameters
        ----------
        df : pd.DataFrame
            Raw DataFrame containing columns ["Strike", "Maturity", "IV"].
        threshold : float
            Threshold above which changes in IV are considered a jump and removed.

        Returns
        -------
        pd.DataFrame
            Cleaned DataFrame.
        """
        df = df.sort_values(by=["Maturity", "Strike"]).reset_index(drop=True)

        # Calculate the absolute differences in consecutive implied volatilities
        df["IV_diff"] = df["IV"].diff().abs()

        # Remove rows where the jump is too large
        df_cleaned = df[df["IV_diff"] < jump_threshold].copy()
        df_cleaned.drop(columns=["IV_diff"], inplace=True)

        return df_cleaned

    def build_surface(self) -> pd.DataFrame:
        """
        High-level method to fetch, clean, and store implied vol data into an internal DataFrame.

        Parameters
        ----------
        jump_threshold : float, optional
            Threshold for IV jumps. Rows with absolute changes above this threshold are removed. Default is 0.1.

        Returns
        -------
        pd.DataFrame
            The cleaned implied volatility surface data with columns: ["Strike", "Maturity", "IV"].
        """
        df_raw = self._fetch_raw_data()
        df_cleaned = self._clean_data(df_raw)
        self.dataframe = df_cleaned
        return df_cleaned

    def interpolate_surface(
        self,
        num_strike_points: int = 50,
        num_maturity_points: int = 50,
        strike_bounds: tuple[float, float] = (65, 100)
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Interpolate the implied vol surface (stored in self.dataframe) on a grid.

        Parameters
        ----------
        num_strike_points : int, optional
            Number of discrete strike points in the interpolation grid.
        num_maturity_points : int, optional
            Number of discrete maturity points in the interpolation grid.
        strike_bounds : tuple, optional
            The minimum and maximum strikes to consider in the interpolation grid.
            If we take strike.min() and strike.max() we won't have the volatility surface

        Returns
        -------
        (K_mesh, T_mesh, Z) : Tuple[np.ndarray, np.ndarray, np.ndarray]
            The meshgrid for strikes, maturities, and interpolated implied volatilities.
        """
        if self.dataframe is None:
            raise ValueError("IV data not built yet. Please call build_surface() first.")

        strikes = self.dataframe["Strike"].values
        maturities = self.dataframe["Maturity"].values
        ivs = self.dataframe["IV"].values

        # Create target grid
        K_min, K_max = strike_bounds
        T_min, T_max = maturities.min(), maturities.max()

        K_vals = np.linspace(K_min, K_max, num=num_strike_points)
        T_vals = np.linspace(T_min, T_max, num=num_maturity_points)

        # Create 2D mesh for interpolation
        K_mesh, T_mesh = np.meshgrid(K_vals, T_vals)

        # Interpolate
        Z = griddata(
            points=(strikes, maturities),
            values=ivs,
            xi=(K_mesh, T_mesh),
            method="cubic" # cubic interpolation
        )

        return K_mesh, T_mesh, Z


    def plot_surface(self) -> None:
        """
        Plot the 3D implied volatility surface using Plotly.

        Parameters
        ----------
        K_mesh : np.ndarray
            2D mesh of strike prices.
        T_mesh : np.ndarray
            2D mesh of maturities.
        Z : np.ndarray
            2D mesh of implied volatilities at each (K, T).
        """
        K_vals, T_vals, Z = self.interpolate_surface()
        fig = go.Figure(
            data=[
                go.Surface(
                    x=K_vals,   # 1D array of strike values
                    y=T_vals,   # 1D array of maturity values
                    z=Z               # 2D array of implied vol
                )
            ]
        )

        fig.update_layout(
            title="Implied Volatility Surface",
            scene=dict(
                xaxis_title="Strike",
                yaxis_title="Maturity (Years)",
                zaxis_title="Implied Volatility"
            ),
            autosize=True
        )

        fig.show()
