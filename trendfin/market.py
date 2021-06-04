# -*- coding: utf-8 -*-
"""Module for getting finanical data from the FMP API.

Includes one class:
1. Market

"""
import json

import pandas as pd
import requests


class Market():
    """Class for interacting with the Financial Modeling Prep API.

    Args:
        fmp_api_key (str): A developer key for the FMP API.

    """

    def __init__(self, fmp_api_key):
        self.fmp_api_key = fmp_api_key

    def quote(self, ticker):
        """Returns limited information on a stock ticker."""
        return self._request_fmp(f'quote/{ticker}?')

    def tickers(self):
        """Returns requestable stock tickers."""
        return self._request_fmp('stock/list?')

    def gainers(self):
        """Returns stock tickers with the highest daily gains."""
        return self._request_fmp('gainers?')

    def losers(self):
        """Returns stock tickers with the highest daily losses."""
        return self._request_fmp('losers?')

    def sectors(self):
        """Returns the performance of market sectors."""
        return self._request_fmp('sectors-performance?')

    def indices(self):
        """Returns the performance of market indices."""
        return self._request_fmp('quotes/index?')

    def ratios(self, ticker):
        """Returns valuation ratios for a stock ticker."""
        return self._request_fmp(f'ratios-ttm/{ticker}?')

    def commodities(self):
        """Returns the performance of commodities."""
        return self._request_fmp(f'quotes/commodity?')

    def etfs(self):
        """Returns the performance of ETFs."""
        return self._request_fmp(f'quotes/etf?')

    def crypto(self):
        """Returns the performance of cryptocurrencies."""
        return self._request_fmp(f'quotes/crypto?')

    def news(self, tickers=None, limit=50):
        """Returns the most recent news articles."""
        target = f'stock_news?'
        target += f'limit={limit}'
        if tickers:
            tickers = ','.join(tickers)
            target += f'&tickers={tickers}'
        return self._request_fmp(target + f'&')

    def screen(self, screener):
        """Interface for using the FMP screener."""
        target = f'stock-screener?'
        for key, value in screener.items():
            target += f'&{key}={value}'
        return self._request_fmp(target + f'&')

    def _request_fmp(self, target):
        api = f'https://financialmodelingprep.com/api/v3/{target}apikey={self.fmp_api_key}'
        r = requests.get(api).json()
        return pd.DataFrame(r)
