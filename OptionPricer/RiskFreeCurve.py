
import yfinance as yf

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
        self._data = yf.download(self.tickers, start=self.start_date, end=self.end_date)
        if self._data is not None and not self._data.empty:
            self._last_date = self._data.index[-1]
        else:
            raise ValueError("No data retrieved for the specified period.")



tickers = ["^IRX", "^FVX", "^TNX", "^TYX"]  # 3 mois, 5 ans, 10, 30
start_date = "2023-01-01"
end_date = "2023-03-01"

datafetcher = MarketDataFetcher(tickers, start_date, end_date)
print(datafetcher._data)

