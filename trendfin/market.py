import json

import pandas as pd
import requests


class Market():

    def __init__(self, api_key):
        self.api_key = api_key

    def quote(self, ticker):
        return self._request_fmp(f'quote/{ticker}?')

    def tickers(self):
        return self._request_fmp('stock/list?')

    def gainers(self):
        return self._request_fmp('gainers?')

    def losers(self):
        return self._request_fmp('losers?')

    def sectors(self):
        return self._request_fmp('sectors-performance?')

    def indices(self):
        return self._request_fmp('quotes/index?')

    def ratios(self, ticker):
        return self._request_fmp(f'ratios-ttm/{ticker}?')

    def commodities(self):
        return self._request_fmp(f'quotes/commodity?')

    def etfs(self):
        return self._request_fmp(f'quotes/etf?')

    def crypto(self):
        return self._request_fmp(f'quotes/crypto?')

    def news(self, tickers=None, limit=50):
        target = f'stock_news?'
        target += f'limit={limit}'
        if tickers:
            tickers = ','.join(tickers)
            target += f'&tickers={tickers}'
        return self._request_fmp(target + f'&')

    def screen(self, screener):
        target = f'stock-screener?'
        for key, value in screener.items():
            target += f'&{key}={value}'
        return self._request_fmp(target + f'&')

    def _request_fmp(self, target):
        api = f'https://financialmodelingprep.com/api/v3/{target}apikey={self.api_key}'
        r = requests.get(api).json()
        return pd.DataFrame(r)
