import os

from dotenv import load_dotenv

from socfin.reddit.models import Account


load_dotenv()
ACCOUNT = Account(
    username=os.getenv('REDDIT_USERNAME'),
    password=os.getenv('REDDIT_PASSWORD'),
    user_agent=os.getenv('REDDIT_USER_AGENT'),
    client_id=os.getenv('REDDIT_CLIENT_ID'),
    client_secret=os.getenv('REDDIT_CLIENT_SECRET')
)
SUBREDDITS = os.getenv('REDDIT_SUBREDDITS').split(',')
POST_LIMIT = int(os.getenv('REDDIT_POST_LIMIT'))
SAMPLE_COMMENTS = bool(os.getenv('SAMPLE_COMMENTS'))
FMP_API_KEY = os.getenv('FMP_API_KEY')
