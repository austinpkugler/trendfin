# -*- coding: utf-8 -*-
"""Module for getting posts and comments from Reddit.

Uses the `Python Reddit API Wrapper`_ and `Pushshift API`_.

Includes two classes:
1. `PostScraper`
2. `CommentScraper`

.. _Python Reddit API Wrapper:
    https://pypi.org/project/praw/

.. _Pushshift API:
    https://pushshift.io/

"""
import json
import time

import pandas as pd
import praw
import requests

from socfin.parsers import ContractParser
from socfin.sentiment import SentimentAnalyzer
from socfin.reddit.models import PushshiftException


class PostScraper(ContractParser, SentimentAnalyzer):
    """Class for scraping posts from Reddit.

    Inherits from `ContractParser`.

    Args:
        account (socfin.reddit.models.Account): The Reddit account to
            use when scraping posts.
        attempts (int, optional): Number of times to attempt scraping
            per request before raising an exception. Defaults to 5.
        analyze (bool, optional): Whether tickers, contracts, and
            sentiment are returned with posts, and comments if using
            `CommentScraper`. Defaults to True.
        **kwargs: Arbitrary keyword arguments.

    Attributes:
        account (socfin.reddit.models.Account): The Reddit account to
            use when scraping posts.
        attempts (int, optional): Number of times to attempt scraping
            per request before raising an exception.

    """

    def __init__(self, account, attempts=5, analyze=True, **kwargs):
        super().__init__(**kwargs)
        self.account = account
        self.attempts = attempts
        self.analyze = analyze
        self._POST_COLUMNS = [
            'author', 'subreddit', 'title', 'content', 'post_id', 'score', 'created_utc',
            'num_comments', 'link_flair_text'
        ]

    def hot_posts(self, subreddits, post_limit=25):
        """Scrapes hot posts.

        Uses the `Python Reddit API Wrapper`_.

        Args:
            subreddits (list): Subreddits to scrape hot posts from.
            post_limit (int, optional): Number of posts to scrape from
                each subreddit while sorting by hot. Defaults to 25.

        Returns:
            `Pandas`_ dataframe of hot Reddit posts. Columns include
            author, subreddit, title, content, post_id, score,
            created_utc, num_comments, and link_flair_text.

        .. _Pandas:
            https://pandas.pydata.org/

        .. _Python Reddit API Wrapper:
            https://pypi.org/project/praw/

        """
        hot_posts = pd.DataFrame(columns=self._POST_COLUMNS)
        for subreddit in subreddits:
            subreddit = self.account._reddit.subreddit(subreddit)
            for post in subreddit.hot(limit=post_limit):
                post_dict = self._praw_post_to_dict(post)
                if self.analyze:
                    post_dict = self._analyze_post_dict(post_dict)
                hot_posts = hot_posts.append(post_dict, ignore_index=True)

        return hot_posts

    def new_posts(self, subreddits, post_limit=25):
        """Scrapes new posts.

        Uses the `Python Reddit API Wrapper`_.

        Args:
            subreddits (list): Subreddits to scrape new posts from.
            post_limit (int, optional): Number of posts to scrape from
                each subreddit while sorting by new. Defaults to 25.

        Returns:
            `Pandas`_ dataframe of new Reddit posts. Columns include
            author, subreddit, title, content, post_id, score,
            created_utc, num_comments, and link_flair_text.

        .. _Pandas:
            https://pandas.pydata.org/

        .. _Python Reddit API Wrapper:
            https://pypi.org/project/praw/

        """
        new_posts = pd.DataFrame(columns=self._POST_COLUMNS)
        for subreddit in subreddits:
            subreddit = self.account._reddit.subreddit(subreddit)
            for post in subreddit.new(limit=post_limit):
                post_dict = self._praw_post_to_dict(post_dict)
                if self.analyze:
                    post_dict = self._analyze_post_dict(post_dict)
                new_posts = new_posts.append(post, ignore_index=True)

        return new_posts

    def historic_posts(self, subreddits, start, end, post_limit=None):
        """Scrapes historic posts from a time range.

        Uses the `Pushshift API`_. Pushift may contain delayed data; use
        the `hot_posts` and `new_posts` methods to get the most recent
        posts.

        Args:
            subreddits (list): Subreddits to scrape historic posts from.
            start (int): Unix timestamp to begin scraping posts from.
            end (int): Unix timestamp to stop scraping posts at.
            post_limit (int, optional): Number of posts to scrape from
                each subreddit while sorting by historic. Defaults to
                None, meaning all posts in the time range will be
                scraped.

        Returns:
            `Pandas`_ dataframe of historic Reddit posts. Columns
            include author, subreddit, title, content, post_id, score,
            created_utc, num_comments, and link_flair_text.

            `Pandas`_ dataframe of historic Reddit comments. Columns
            include author, subreddit, content, post_id, comment_id,
            score, and created_utc.

        Raises:
            PushshiftException: Raised when a `Pushshift API`_ request
                fails.

        .. _Pandas:
            https://pandas.pydata.org/

        .. _Pushshift API:
            https://pushshift.io/

        """
        if start > end:
            raise PushshiftException('Start cannot be greater than end')

        API_BASE = 'https://api.pushshift.io/reddit/search/submission/?'
        API_PARAMS = '&limit=100&fields=created_utc,{}&after={}&before={}&subreddit={}'
        FIELDS = 'author,subreddit,title,selftext,id,score,num_comments,link_flair_text'

        historic_posts = pd.DataFrame(columns=self._POST_COLUMNS)
        querying = True
        while querying:
            target = API_BASE + API_PARAMS.format(FIELDS, start, end, ','.join(subreddits))
            for attempt in range(self.attempts):
                try:
                    posts = requests.get(target).json()['data']
                    break
                except:
                    if attempt + 1 == self.attempts:
                        raise PushshiftException(f'Request to {target} failed after final attempt')
                    else:
                        time.sleep(2)

            for post in posts:
                post_dict = self._pushshift_post_to_dict(post_dict)
                if self.analyze:
                    post_dict = self._analyze_post_dict(post_dict)
                historic_posts = historic_posts.append(post_dict, ignore_index=True)

                post_count = len(historic_posts.index)
                if post_limit and post_count >= post_limit:
                    querying = False

            if posts:
                start = posts[-1]['created_utc']
            else:
                querying = False

        return historic_posts

    def _praw_post_to_dict(self, post):
        """Converts a `Python Reddit API Wrapper`_ post to dict.

        Private helper function.

        Args:
            post (praw.models.Submission): `Python Reddit API Wrapper`_
                post to convert to dictionary form.

        Returns:
            dict: A Reddit post in dictionary form. Includes author,
            subreddit, title, content, post_id, score, created_utc,
            num_comments, and link_flair_text.

        """
        try:
            author = str(post.author.name)
        except:
            author = '[deleted]'
        post_dict = {
            'author': author,
            'subreddit': post.subreddit.display_name,
            'title': post.title,
            'content': post.selftext,
            'post_id': post.id,
            'score': int(post.score),
            'created_utc': int(post.created_utc),
            'num_comments': int(post.num_comments),
            'link_flair_text': post.link_flair_text
        }
        return post_dict

    def _pushshift_post_to_dict(self, post):
        """Converts a `Pushshift API`_ post to dict.

        Private helper function.

        Args:
            post (dict): `Pushshift API`_ post to convert to dictionary
                form. Although it is already dict, conversion is
                still required.

        Returns:
            dict: A Reddit post in dictionary form. Includes author,
            subreddit, title, content, post_id, score, created_utc,
            num_comments, and link_flair_text.

        """
        try:
            author = str(post['author'])
        except:
            author = '[deleted]'
        try:
            content = str(post['selftext'])
        except:
            content = None
        try:
            link_flair_text = str(post['link_flair_text'])
        except:
            link_flair_text = None
        post_dict = {
            'author': author,
            'subreddit': post['subreddit'],
            'title': post['title'],
            'content': content,
            'post_id': post['id'],
            'score': int(post['score']),
            'created_utc': int(post['created_utc']),
            'num_comments': int(post['num_comments']),
            'link_flair_text': link_flair_text
        }
        return post_dict

    def _analyze_post_dict(self, post_dict):
        post_dict['tickers'] = self.tickers(post_dict['title'] + '\n' + post_dict['content'])
        post_dict['contracts'] = self.contracts(post_dict['content'])
        post_dict['sentiment'] = self.sentiment(post_dict['content'])
        return post_dict


class CommentScraper(PostScraper):

    def __init__(self, **kwargs):
        """Class for scraping comments and their posts from Reddit.

        Inherits from `PostScraper`.

        Args:
            **kwargs: Arbitrary keyword arguments.

        """
        super().__init__(**kwargs)
        self._COMMENT_COLUMNS = [
            'author', 'subreddit', 'content', 'post_id', 'comment_id', 'score', 'created_utc'
        ]

    def hot_comments(self, subreddits, post_limit=25, sample_comments=False):
        """Scrapes hot posts and comments.

        Uses the `Python Reddit API Wrapper`_.

        Args:
            subreddits (list): Subreddits to scrape hot posts and
                comments from.
            post_limit (int, optional): Number of posts to scrape from
                each subreddit while sorting by hot. Defaults to 25.
            sample_comments (bool): Determines whether all comments are scraped.
                Defaults to False.

        Returns:
            `Pandas`_ dataframe of hot Reddit posts. Columns include
            author, subreddit, title, content, post_id, score,
            created_utc, num_comments, and link_flair_text.

            `Pandas`_ dataframe of hot Reddit comments. Columns include
            author, subreddit, content, post_id, comment_id, score, and
            created_utc.

        .. _Pandas:
            https://pandas.pydata.org/

        .. _Python Reddit API Wrapper:
            https://pypi.org/project/praw/

        """
        hot_posts = self.hot_posts(subreddits, post_limit)
        hot_post_ids = list(hot_posts['post_id'])
        if sample_comments:
            hot_comments = self._praw_comments_to_df(hot_post_ids, True)
        else:
            hot_comments = self._praw_comments_to_df(hot_post_ids)
        return hot_posts, hot_comments

    def new_comments(self, subreddits, post_limit=25, sample_comments=False):
        """Scrapes new posts and comments.

        Uses the `Python Reddit API Wrapper`_.

        Args:
            subreddits (list): Subreddits to scrape new posts and
                comments from.
            post_limit (int, optional): Number of posts to scrape from
                each subreddit while sorting by new. Defaults to 25.
            sample_comments (bool): Determines whether all comments are scraped.
                Defaults to False.

        Returns:
            `Pandas`_ dataframe of new Reddit posts. Columns include
            author, subreddit, title, content, post_id, score,
            created_utc, num_comments, and link_flair_text.

            `Pandas`_ dataframe of new Reddit comments. Columns include
            author, subreddit, content, post_id, comment_id, score, and
            created_utc.

        .. _Pandas:
            https://pandas.pydata.org/

        .. _Python Reddit API Wrapper:
            https://pypi.org/project/praw/

        """
        new_posts = self.new_posts(subreddits, post_limit)
        new_post_ids = list(new_posts['post_id'])
        new_comments = self._praw_comments_to_df(new_post_ids)
        return new_posts, new_comments

    def historic_comments(self, subreddits, start, end, post_limit=None):
        """Scrapes historic posts and comments from a time range.

        Uses the `Pushshift API`_. Pushift may contain delayed data; use
        the `hot_posts` and `new_posts` methods to get the most recent
        posts and comments.

        Args:
            subreddits (list): Subreddits to scrape historic posts and
                comments from.
            start (int): Unix timestamp to begin scraping posts and
                comments from.
            end (int): Unix timestamp to stop scraping posts and
                comments at.
            post_limit (int, optional): Number of posts to scrape from
                each subreddit while sorting by historic. Defaults to
                None, meaning all posts in the time range will be
                scraped.

        Returns:
            `Pandas`_ dataframe of historic Reddit posts. Columns
            include author, subreddit, title, content, post_id, score,
            created_utc, num_comments, and link_flair_text.

            `Pandas`_ dataframe of historic Reddit comments. Columns
            include author, subreddit, content, post_id, comment_id,
            score, and created_utc.

        Raises:
            PushshiftException: Raised when a `Pushshift API`_ request
                fails.

        .. _Pandas:
            https://pandas.pydata.org/

        .. _Pushshift API:
            https://pushshift.io/

        """
        if start > end:
            raise PushshiftException('Start cannot be greater than end')

        API_BASE = 'https://api.pushshift.io/reddit/comment/search/?'
        API_PARAMS = '&limit=100&fields=created_utc,{}&after={}&before={}&link_id={}'
        FIELDS = 'author,subreddit,body,link_id,id,score,created_utc'

        historic_posts = self.historic_posts(subreddits, start, end, post_limit)
        historic_post_ids = list(historic_posts['post_id'])
        historic_comments = pd.DataFrame(columns=self._COMMENT_COLUMNS)
        querying = True
        while querying:
            target = API_BASE + API_PARAMS.format(FIELDS, start, end, ','.join(historic_post_ids))
            for attempt in range(self.attempts):
                try:
                    comments = requests.get(target).json()['data']
                    break
                except:
                    if attempt + 1 == self.attempts:
                        raise PushshiftException(f'Request to {target} failed after final attempt')
                    else:
                        time.sleep(2)

            for comment in comments:
                comment_dict = self._pushshift_comment_to_dict(comment)
                if self.analyze:
                    comment_dict = self._analyze_comment_dict(comment_dict)
                historic_comments = historic_comments.append(comment_dict, ignore_index=True)

            if comments:
                start = comments[-1]['created_utc']
            else:
                querying = False

        return historic_posts, historic_comments

    def _praw_comments_to_df(self, post_ids, sample_comments=False):
        """Populates dataframe with comments scraped from post ids.

        Uses the `Python Reddit API Wrapper`_. Private helper function.

        Args:
            post_ids (list): Reddit post ids to scrape comments from.
            sample_comments (bool): Determines whether all comments are scraped.
                Defaults to False.

        Returns:
            `Pandas`_ dataframe of Reddit comments from posts in the
            `post_ids` parameter. Columns include author, subreddit,
            content, post_id, comment_id, score, and created_utc.

        .. _Pandas:
            https://pandas.pydata.org/

        .. _Python Reddit API Wrapper:
            https://pypi.org/project/praw/

        """
        comments = pd.DataFrame(columns=self._COMMENT_COLUMNS)
        for post_id in post_ids:
            post = self.account._reddit.submission(post_id)
            if sample_comments:
                for attempt in range(self.attempts):
                    try:
                        post.comments.replace_more(limit=20, threshold=50)
                        break
                    except Exception as e:
                        if attempt + 1 == self.attempts:
                            raise e
                        else:
                            time.sleep(2)
            for comment in post.comments:
                comments = self._praw_flatten_comments(comment, comments)
        return comments

    def _praw_flatten_comments(self, comment, comments):
        """Recursively flattens the comment tree of a Reddit post.

        Uses the `Python Reddit API Wrapper`_. Private helper function.

        Args:
            comment (praw.Models.Comment): Current comment to flatten.
            comments (pandas.DataFrame): `Pandas`_ dataframe to append
                flattened comments to.

        Returns:
            `Pandas`_ dataframe of flattened Reddit comments. Columns
            include author, subreddit, content, post_id, comment_id,
            score, and created_utc.

        .. _Pandas:
            https://pandas.pydata.org/

        .. _Python Reddit API Wrapper:
            https://pypi.org/project/praw/

        """
        # Handle MoreComments expansion
        if isinstance(comment, praw.models.MoreComments):
            for comment in comment.comments():
                comments = self._praw_flatten_comments(comment, comments)

        # Handle replies to comment and add comment to dataframe
        elif isinstance(comment, praw.models.Comment):
            comment_dict = self._praw_comment_to_dict(comment)
            if self.analyze:
                comment_dict = self._analyze_comment_dict(comment_dict)
            comments = comments.append(comment_dict, ignore_index=True)
            if hasattr(comment, 'replies'):
                for comment in comment.replies:
                    comments = self._praw_flatten_comments(comment, comments)

        return comments

    def _praw_comment_to_dict(self, comment):
        """Converts a `Python Reddit API Wrapper`_ comment to dict.

        Private helper function.

        Args:
            comment (praw.models.Comment): `Python Reddit API Wrapper`_
                comment to convert to dictionary form.

        Returns:
            dict: A Reddit comment in dictionary form. Includes author,
            subreddit, content, post_id, comment_id, score, and
            created_utc.

        .. _Python Reddit API Wrapper:
            https://pypi.org/project/praw/

        """
        try:
            author = str(comment.author.name)
        except:
            author = '[deleted]'
        comment_dict = {
            'author': author,
            'subreddit': comment.subreddit.display_name,
            'content': comment.body,
            'post_id': comment.submission.id,
            'comment_id': comment.id,
            'score': int(comment.score),
            'created_utc': int(comment.created_utc)
        }
        return comment_dict

    def _pushshift_comment_to_dict(self, comment):
        """Converts a `Pushshift API`_ comment to dict.

        Private helper function.

        Args:
            comment (dict): `Pushshift API`_ comment to convert to
                dictionary form. Although it is already dict, conversion
                is still required.

        Returns:
            dict: A Reddit comment in dictionary form. Includes author,
            subreddit, content, post_id, comment_id, score, and
            created_utc.

        .. _Pushshift API:
            https://pushshift.io/

        """
        try:
            author = str(comment['author'])
        except:
            author = '[deleted]'
        comment_dict = {
            'author': author,
            'subreddit': comment['subreddit'],
            'content': comment['body'],
            'post_id': comment['link_id'].split('_')[1],
            'comment_id': comment['id'],
            'score': int(comment['score']),
            'created_utc': int(comment['created_utc'])
        }
        return comment_dict

    def _analyze_comment_dict(self, comment_dict):
        comment_dict['tickers'] = self.tickers(comment_dict['content'])
        comment_dict['contracts'] = list(self.contracts(comment_dict['content']).T.to_dict().values())
        sentiment = self.sentiment(comment_dict['content'])
        comment_dict['sentiment'] = sentiment['compound']
        return comment_dict
