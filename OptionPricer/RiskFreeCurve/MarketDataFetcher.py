import yfinance as yf
import numpy as np

class MarketDataFetcher:
    """
    Handles rate data fetching from Yahoo Finance,
    and prepares the latest available rate values for the most recent date.
    """

    def __init__(self, tickers, start_date, end_date):
        """
        :param tickers: List of Yahoo Finance tickers, e.g. ["^IRX", "^FVX", "^TNX", "^TYX"].
        :param start_date: Start date in format "YYYY-MM-DD".
        :param end_date:   End date in format "YYYY-MM-DD".
        """
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date
        self._data = None
        self._last_date = None

    def fetch_data(self):
        """
        Downloads market data for the selected tickers,
        stores the associated DataFrame in self._data and records the last available date.
        """
        self._data = yf.download(self.tickers, start=self.start_date, end=self.end_date, progress=False)
        if self._data is not None and not self._data.empty:
            self._last_date = self._data.index[-1]
        else:
            raise ValueError("No data retrieved for the specified period.")

    
    def get_latest_rates(self):
        """
        Extracts the latest interest rate points (in percentage) and converts them to decimal.
        :return: (maturities, rates) as (np.array, np.array).
        """
        assert self._data is not None, "fetch_data() method must be first."

        # Select the DataFrame with closing prices
        adj_close = self._data['Close'].copy()

        # Retrieve the rates (in %) at the last date
        last_rates_percent = adj_close.loc[self._last_date, self.tickers]

        # Convert to decimal
        last_rates_decimal = last_rates_percent / 100.0

        # Define our maturities (approx.) in years
        # Corresponding to tickers: ^IRX (3 months), ^FVX (5 years), ^TNX (10 years), ^TYX (30 years)
        maturities = np.array([0.25, 5.0, 10.0, 30.0])
        rates = last_rates_decimal.values

        return maturities, rates

    @property
    def last_date(self):
        return self._last_date
