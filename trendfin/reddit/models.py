# -*- coding: utf-8 -*-
"""Module for representing Reddit accounts.

Includes one class:
1. `Account`

"""
import praw


class Account():
    """Class for representing a Reddit account and posting to Reddit.

    Args:
        username (str): Reddit account username.
        password (str): Reddit account password.
        user_agent (str): Short message that includes the name and
            version of your `Reddit App`_ and your Reddit username.
        client_id (str): The unique 14-character identifier for your
            `Reddit App`_.
        client_secret (str): The unique 27-character authentication
            token for your `Reddit App`_.

    Attributes:
        username (str): Reddit account username.
        password (str): Reddit account password.
        user_agent (str): Short message that includes the name and
            version of your `Reddit App`_ and your Reddit username.
        client_id (str): The unique 14-character identifier for your
            `Reddit App`_.
        client_secret (str): The unique 27-character authentication
            token for your `Reddit App`_.

    .. _Reddit App:
        https://www.reddit.com/prefs/apps

    """

    def __init__(self, username, password, user_agent, client_id, client_secret):
        self.username = username
        self.password = password
        self.user_agent = user_agent
        self.client_id = client_id
        self.client_secret = client_secret
        self._reddit = praw.Reddit(
            username=username,
            password=password,
            user_agent=user_agent,
            client_secret=client_secret,
            client_id=client_id
        )
        self._reddit.validate_on_submit = True

    def __repr__(self):
        """Represents `Account` class."""
        return f'<Account(username={self.username})>'

    def submit_text_post(self, subreddit, title, content=None, flair_id=None):
        """Submits a new Reddit text post."""
        self._reddit.subreddit(subreddit).submit(
            title=title,
            selftext=content,
            flair_id=flair_id
        )

    def submit_link_post(self, subreddit, title, url, flair_id=None):
        """Submits a new Reddit link post"""
        self._reddit.subreddit(subreddit).submit(
            title=title,
            url=url,
            flair_id=flair_id
        )

    def submit_comment(self, post_id, content):
        """Submits a new Reddit comment."""
        self._reddit.submission(post_id).reply(content)


class PushshiftException(Exception):
    """Class for exceptions related to the `Pushshift API`_.

    Args:
        message (str): Error message specifying the exception.

    Attributes:
        message (str): Error message specifying the exception.

    .. _Pushshift API:
            https://pushshift.io/

    """
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
