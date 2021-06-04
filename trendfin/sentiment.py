# -*- coding: utf-8 -*-
"""Module for analyzing sentiment regarding financial markets.

Includes one class:
1. SentimentAnalyzer

"""
import os
import pickle
import re

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd

from socfin.parsers import TextParser


class SentimentAnalyzer(TextParser):
    """Class for analyzing sentiment of text.

    Inherits from `TextParser`.

    Args:
        **kwargs: Arbitrary keyword arguments.

    """

    def __init__(self, classifier='classifier.pickle', **kwargs):
        super().__init__(**kwargs)
        with open(os.path.join('socfin', 'data', classifier), 'rb') as file:
            self._sia = pickle.load(file)

    def sentiment(self, text):
        """Calucates sentiment scores for text.

        Args:
            text (str): Text to calcuate sentiment for.

        Returns:
            `Pandas`_ dataframe of sentiment scores for the `text`
            parameter. Columns include neg, neu, pos, and compound.
            Compound is the overall sentiment score.

        .. _Pandas:
            https://pandas.pydata.org/

        """
        text = self.replace_emojis(text)
        text = self.alpha(text)
        sentiment = self._sia.polarity_scores(text)
        return pd.DataFrame(sentiment, index=[0])

    def ticker_sentiment(self, text, ticker):
        """Calucates sentiment scores for text regarding a stock ticker.

        Args:
            text (str): Text to calcuate sentiment for.
            ticker (str): Ticker to calculate sentiment for.

        Returns:
            `Pandas`_ dataframe of sentiment scores for the `text`
            parameter, specifically regarding the `ticker` parameter.
            Columns include ticker, neg, neu, pos, and compound.
            Compound is the overall sentiment score.

        .. _Pandas:
            https://pandas.pydata.org/

        """
        words = self.words(text)
        if ticker not in words:
            sentiment = {'ticker': ticker, 'neg': 0.0, 'neu': 1.0, 'pos': 0.0, 'compound': 0.0}
            return pd.DataFrame(sentiment, index=[0])

        if len(words) > 20:
            ticker_index = words.index(ticker)
            text = ' '.join(words[ticker_index - 10:ticker_index + 10])

        sentiment = self._sia.polarity_scores(text)
        sentiment_df = pd.DataFrame(sentiment, index=[0])
        sentiment_df.insert(0, 'ticker', ticker)
        return sentiment_df
