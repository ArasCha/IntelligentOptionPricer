import yfinance as yf
import pandas as pd
import numpy as np
from datetime import date

# Les tickers Yahoo Finance pour certains taux US:
# ^IRX : 13-week T-Bill yield (3 mois)
# ^FVX : 5-year T-Note yield  (5 ans)
# ^TNX : 10-year T-Note yield (10 ans)
# ^TYX : 30-year T-Bond yield (30 ans)
tickers = ["^IRX", "^FVX", "^TNX", "^TYX"]

start_date = "2023-01-01"
end_date   = "2023-03-01"

# On récupère les taux sur la période définie
# La colonne 'Adj Close' correspond au taux de clôture (en % annuel)
data = yf.download(tickers, start=start_date, end=end_date)
data.head()