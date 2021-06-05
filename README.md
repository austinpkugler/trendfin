# trendfin

The ultimate package for analyzing online finance communities (ex: r/wallstreetbets).

The trendfin package utilizes the Reddit and Pushshift APIs to provide detailed analysis of retail investor discussions. The [Financial Modeling Prep API](https://financialmodelingprep.com/developer) is used for market data. Functionality exists for parsing stock tickers and option contracts, as well as calculating sentiment values that reflect a user's bearish or bullish outlook. Both trending and historical Reddit posts and comments can be collected.

## Setup

1. Clone or download the repository.

`$ git clone https://github.com/austinpkugler/trendfin.git`

2. Create a virtual environment inside the repository.

`$ python3 -m venv env`

3. Install dependencies.

`pip install -r requirements.txt`

4. Create a personal Reddit app.

Login to Reddit and create an application [here](https://ssl.reddit.com/prefs/apps/). This will provide you with a client ID and client secret.

5. Get a free developer key for the [Financial Modeling Prep API](https://financialmodelingprep.com/developer).

Note: This step is not required if you plan to forgo using trendfin's market data functionality. The free version of the Financial Modeling Prep API has request limits.

## Examples

### Getting Hot Posts and Comments

```
ACCOUNT = Account(
    username="YOUR REDDIT USERNAME",
    password="YOUR REDDIT PASSWORD",
    user_agent="YOUR REDDIT USER AGENT",
    client_id="YOUR REDDIT CLIENT ID",
    client_secret="YOUR REDDIT CLIENT SECRET"
)

scraper = CommentScraper(account=ACCOUNT, valid_tickers=['AAPL', 'MSFT'])

hot_posts, hot_comments = scraper.hot_comments(subreddits=['wallstreetbets'], post_limit=25)
```

### Using the Financial Modeling Prep Screener

```
market = Market("YOUR FMP API KEY")

screener = {'country': 'US', 'marketCapMoreThan': 300000000, 'priceMoreThan': 1, 'isActivelyTrading': 'true'}

companies = market.screen(screener)
```

### Parsing Stock Tickers and Options Contracts

```
ticker_parser = TickerParser(valid_tickers=['AAPL', 'MSFT'], ignore_duplicates=False)
contract_parser = ContractParser(valid_tickers=['AAPL', 'MSFT'], ignore_duplicates=False)

found_tickers = ticker_parser.tickers("I like AAPL.")
found_contracts = contract_parser.contracts("I am holding AAPL $500C for 9/12.
```

## Sentiment Analysis

```
analyzer = SentimentAnalyzer()

sentiment = analyzer.sentiment("I like AAPL.")
ticker_sentiment = analyzer.ticker_sentiment("I like AAPL.", "AAPL")
```

## Documentation

Documentation for specific functions or classes can be found inline as docstrings.
