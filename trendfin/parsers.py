# -*- coding: utf-8 -*-
"""Module for parsing text, stock tickers, and option contracts.

Includes three classes:
1. `TextParser`
2. `TickerParser`
3. `ContractParser`

"""
import collections
import re

import emoji
import pandas as pd


class TextParser():
    """Class for parsing text.

    Args:
        stop_words (list, optional): Capital words to exclude. Defaults
            to a list of common English words and slang.

    Attributes:
        stop_words (list): Capital words to exclude.

    """

    _STOP_WORDS = [
        'ABOUT', 'ACTUALLY', 'AFTER', 'AGAIN', 'ALREADY', 'ALSO', 'ALWAYS', 'AND', 'ANOTHER',
        'ANYONE', 'ANYTHING', 'AROUND', 'AS', 'AUTOMATICALLY', 'BACK', 'BECAUSE', 'BEEN', 'BEFORE',
        'BEING', 'BETTER', 'BOT', 'BUT', 'CANT', 'COME', 'COMPANIES', 'COMPANY', 'COULD', 'DAY',
        'DAYS', 'DELETED', 'DID', 'DIDNT', 'DO', 'DOES', 'DOESNT', 'DOING', 'EVEN', 'EVERY',
        'EVERYONE', 'FEEL', 'FEW', 'FIND', 'FIRST', 'FROM', 'FUCK', 'FUCKING', 'GET', 'GETTING',
        'GONNA', 'GOT', 'HAD', 'HAVE', 'HERE', 'HIS', 'HOW', 'I', 'IF', 'ILL', 'IM', 'IN', 'INTO',
        'IS', 'ISNT', 'ITS', 'KEEP', 'KNOW', 'LAST', 'LOL', 'LOOK', 'LOOKING', 'LOT', 'MADE',
        'MAKE', 'MANY', 'MARKET', 'MAYBE', 'ME', 'MEAN', 'MIGHT', 'MONTHS', 'MOST', 'MUCH', 'MY',
        'NEED', 'NEWS', 'OF', 'ONLY', 'OPTIONS', 'OTHER', 'PEOPLE', 'PLEASE', 'POINT', 'PRETTY',
        'PROBABLY', 'QUESTIONS', 'REALLY', 'REMOVED', 'SAID', 'SAME', 'SAY', 'SHOULD', 'SINCE',
        'SOME', 'SOMETHING', 'STILL', 'SURE', 'TAKE', 'THAN', 'THANKS', 'THAT', 'THATS', 'THE',
        'THEIR', 'THEM', 'THEN', 'THERE', 'THERES', 'THESE', 'THEY', 'THEYRE', 'THING', 'THINK',
        'THIS', 'THOSE', 'THOUGH', 'TIME', 'TO', 'TODAY', 'TOMORROW', 'TOO', 'TRADING', 'UNTIL',
        'US', 'USE', 'WAS', 'WAY', 'WE', 'WEEK', 'WERE', 'WHAT', 'WHEN', 'WHERE', 'WHICH', 'WHILE',
        'WHO', 'WHY', 'WILL', 'WITH', 'WOULD', 'YEAH', 'YEAR', 'YEARS', 'YES', 'YOU', 'YOUR',
        'YOURE'
    ]

    def __init__(self, stop_words=_STOP_WORDS):
        self.stop_words = stop_words

    def alpha(self, text):
        """Parses alphabetical characters from text.

        Preserves spaces and their location.

        Args:
            text (str): Text to parse alphabetical characters from.

        Returns:
            str: The alphabetical characters in the `text` parameter.

        """
        return re.sub(r'[^A-Za-z ]+', r'', text)

    def numeric(self, text):
        """Parses numbers from text.

        Preserves spaces and their location.

        Args:
            text (str): Text to parse numbers from.

        Returns:
            str: The numbers in the `text` parameter.

        """
        return re.sub(r'[^0-9 ]+', r'', text)

    def alphanumeric(self, text):
        """Parses alphabetical characters and numbers from text.

        Preserves spaces and their location.

        Args:
            text (str): Text to parse alphabetical characters and
                numbers from.

        Returns:
            str: The alphabetical characters and numbers in the `text`
                parameter.

        """
        return re.sub(r'[^A-Za-z0-9 ]+', r'', text)

    def replace_emojis(self, text):
        """Replaces emojis with their text representations.

        Colons enclose each emoji representation.

        Args:
            text (str): Text to replace emojis in.

        Returns:
            str: The `text` parameter with text representations
                replacing emojis.

        """
        text = emoji.demojize(text)
        return re.sub(r'(:[A-Za-z_]+:)', r' \1 ', text)

    def remove_stop_words(self, text):
        """Removes undesireable words from text.

        Args:
            text (str): Text to remove words from.

        Returns:
            str: The `text` parameter without undesireable words.

        """
        words = text.split()
        words = [w for w in words if w.upper() not in self.stop_words]
        return ' '.join(words)

    def words(self, text):
        """Splits text into capital words.

        Letters of all words become capitals.

        Args:
            text (str): Text to split into capital words.

        Returns:
            list: Words in the `text` parameter.

        """
        text = self.replace_emojis(text)
        text = self.alpha(text)
        text = text.upper()
        return text.split()


class TickerParser(TextParser):
    """Class for parsing stock tickers from text.

    Inherits from `TextParser`.

    Args:
        valid_tickers (list, optional): Stock tickers to search for
            when parsing. Defaults to empty list.
        ignore_duplicates (bool, optional): Determines whether duplicate
            tickers, and contracts if using `ContractParser`, are
            ignored. Defaults to False.
        **kwargs: Arbitrary keyword arguments.

    Attributes:
        valid_tickers (list): Stock tickers to search for
            when parsing.

    """

    def __init__(self, valid_tickers=[], ignore_duplicates=True, **kwargs):
        super().__init__(**kwargs)
        self.valid_tickers = valid_tickers
        self.ignore_duplicates = ignore_duplicates
        self._TICKER_COUNT_COLUMNS = ['ticker', 'count']

    def tickers(self, text):
        """Parses stock tickers from text.

        Args:
            text (str): Text to parse stock tickers from.

        Returns:
            list: Stock tickers found in the `text` parameter.

        """
        words = self.words(text)
        if self.ignore_duplicates:
            tickers = list(set(words) & set(self.valid_tickers))
        else:
            tickers = [w for w in words if w in self.valid_tickers]

        return tickers

    def ticker_counts(self, text):
        """Parses stock tickers and their counts from text.

        Args:
            text (str): Text to parse stock tickers and counts from.

        Returns:
            `Pandas`_ dataframe of stock tickers found in the `text`
            parameter. Includes a count of occurences for each ticker.
            Columns include ticker and count.

        .. _Pandas:
            https://pandas.pydata.org/

        """
        words = self.words(text)
        tickers = list(set(words) & set(self.valid_tickers))
        word_counts = collections.Counter(words)
        ticker_counts = {t: word_counts[t] for t in tickers}
        return pd.DataFrame(ticker_counts.items(), columns=self._TICKER_COUNT_COLUMNS)


class ContractParser(TickerParser):
    """Class for parsing option contracts from text.

    Inherits from `TickerParser`.

    Args:
        **kwargs: Arbitrary keyword arguments.

    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._CONTRACT_COLUMNS = ['ticker', 'strike', 'type', 'date']

    def contracts(self, text):
        """Parses option contracts from text.

        Args:
            text (str): Text to parse option contracts from.

        Returns:
            `Pandas`_ dataframe of option contracts found in the `text`
            parameter. Columns include ticker, strike, type, and date.

        .. _Pandas:
            https://pandas.pydata.org/

        """
        contracts_df = pd.DataFrame(columns=self._CONTRACT_COLUMNS)
        contract_elements = self._contract_elements(text)
        ticker, strike, date = None, None, None
        for element in contract_elements:
            if element[0] == 'ticker':
                ticker = element[1]
            elif element[0] == 'strike':
                strike = element[1]
            elif element[0] == 'date':
                date = element[1]

            if ticker and strike and date:
                contract_type = 'call' if 'C' in strike else 'put'
                try:
                    strike = float(strike[:-1])

                    contract = {
                        'ticker': ticker,
                        'strike': strike,
                        'type': contract_type,
                        'date': date
                    }
                    if strike > 5:
                        contracts_df = contracts_df.append(contract, ignore_index=True)
                except:
                    pass
                ticker, strike, date = None, None, None

        if self.ignore_duplicates:
            return contracts_df.drop_duplicates()
        return contracts_df

    def contract_counts(self, text):
        """Parses option contracts and their counts from text.

        Args:
            text (str): Text to parse option contracts and counts from.

        Returns:
            `Pandas`_ dataframe of option contracts found in the `text`
            parameter. Columns include ticker, strike, type, date, and
            count. Includes a count of occurences for each ticker.

        .. _Pandas:
            https://pandas.pydata.org/

        """
        contracts_df = self.contracts(text)
        contracts_df = contracts_df.groupby(contracts_df.columns.tolist(), as_index=False).size()
        contracts_df = contracts_df.rename(columns={'size': 'count'})
        return contracts_df

    def _contract_elements(self, text):
        """Parses elements of option contracts from text.

        Private helper function.

        Args:
            text (str): Text to parse option contract elements from.

        Returns:
            A 2D list of tickers, strike prices, contract types, and
            dates. Preserves their order in the `text` parameter.

        """
        # Uppercase
        text = text.upper()

        # Remove urls
        text = re.sub(r'HTTP\S+', ' ', text)

        # Replace newline and @ with space
        text = re.sub(r'[\n@]', r' ', text)

        # Remove embedded periods
        text = re.sub(r'([^0-9]|^)\.([^0-9]|$)', r'\1\2', text)

        # Remove special characters
        text = re.sub(r'[^A-Za-z0-9\/. ]+', r'', text)

        # Remove excesseive spaces
        text = re.sub(r' +', r' ', text)

        # Remove padding in dates
        text = re.sub(r'(^| )0(\d+\/)', r'\1\2', text)
        text = re.sub(r'(\/)0(\d+)', r'\1\2', text)

        # Replace verbose contract type
        text = re.sub(r'([.| ]\d+) ?(CALL(S)?)|CS', r'\1C', text)
        text = re.sub(r'([.| ]\d+) ?(PUT(S)?)|PS', r'\1P', text)

        # Remove spaces between strike price and contract type
        text = re.sub(r'(\d+) ([CP])( |[^A-Z]|$)', r'\1\2\3', text)

        contract_elements = []
        for word in text.split():
            if word in self.valid_tickers:
                contract_elements.append(['ticker', word])
            elif re.search(r'\d+[CP]', word):
                contract_elements.append(['strike', word])
            elif '/' not in word and re.search(r'\d+', word):
                if re.search(r'CALL', text):
                    contract_elements.append(['strike', word + 'C'])
                elif re.search(r'PUT', text):
                    contract_elements.append(['strike', word + 'P'])
            elif re.search(r'(\d+\/\d+(?:\/\d+)?)', word):
                contract_elements.append(['date', word])

        return contract_elements
