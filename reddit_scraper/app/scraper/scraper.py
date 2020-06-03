import json
import logging
import os
import time
from typing import List

import praw
from praw import Reddit
from praw.models import ListingGenerator
from pymongo import MongoClient
from pymongo.collection import Collection, ReturnDocument
from pymongo.cursor import Cursor
from pymongo.database import Database

from ..reddit_post.reddit_post import RedditPost

logger = logging.getLogger("reddit_scraper")


class RedditScraper:
    def __init__(self):
        self.client_id = os.getenv("REDDIT_CLIENT_ID")
        self.client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        self.username = os.getenv("REDDIT_USERNAME")
        self.password = os.getenv("REDDIT_PASSWORD")
        self.user_agent = "Python script written by @gordonpn on GitHub"
        self.db_name = os.getenv("MONGO_INITDB_DATABASE")
        self.db_username = os.getenv("MONGO_NON_ROOT_USERNAME")
        self.db_password = os.getenv("MONGO_NON_ROOT_PASSWORD")
        self.db_settings = os.getenv("MONGO_SETTINGS")
        self.db_collection = os.getenv("MONGO_COLLECTION")

    def run(self):
        subscriptions = self.check_subscriptions()
        reddit = self.get_reddit()
        posts = self.scrape(reddit, subscriptions)
        self.update_db(posts)

    def get_reddit(self) -> Reddit:
        return praw.Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            username=self.username,
            password=self.password,
            user_agent=self.user_agent,
        )

    def connect_to_db(self) -> Database:
        logger.debug("Making connection to mongodb")
        host = "mongodb"
        uri: str = f"mongodb://{self.db_username}:{self.db_password}@{host}:27017/{self.db_name}"
        connection: MongoClient = MongoClient(uri)
        db: Database = connection[self.db_name]
        return db

    def get_settings_collection(self) -> Collection:
        db = self.connect_to_db()
        return db.collection[self.db_settings]

    def get_data_collection(self) -> Collection:
        db = self.connect_to_db()
        return db.collection[self.db_collection]

    def check_subscriptions(self) -> List[str]:
        logger.debug("Checking subscriptions")
        collection = self.get_settings_collection()
        cursor: Cursor = collection.find_one()
        logger.debug(f"{cursor=}")

        if cursor is None:
            return []
        subs: List[str] = cursor["subreddits"]
        logger.debug(f"{subs=}")
        return subs

    def scrape(self, reddit: Reddit, subscriptions: List[str]) -> List[RedditPost]:
        logger.debug("Scraping Reddit for hot posts")
        limit: int = 5
        time_filter: str = "day"
        reddit_posts: List[RedditPost] = []

        for subscription in subscriptions:
            logger.debug(f"{subscription=}")
            submissions: ListingGenerator = reddit.subreddit(subscription).top(
                limit=limit, time_filter=time_filter
            )
            for submission in submissions:
                if submission.stickied:
                    continue
                title = submission.title
                post_id = submission.id
                votes = submission.score
                link = submission.url
                is_self = submission.is_self
                unix_time = int(submission.created_utc)
                logger.debug(f"Parsing: {post_id=}")
                a_reddit_post = RedditPost(
                    title=title,
                    subreddit=subscription,
                    post_id=post_id,
                    votes=votes,
                    link=link,
                    unix_time=unix_time,
                    is_self=is_self,
                    seen=False,
                )
                reddit_posts.append(a_reddit_post)

        return reddit_posts

    def update_db(self, posts: List[RedditPost]):
        logger.debug("Updating scrapings collections")
        collection = self.get_data_collection()

        for post in posts:
            query = {"post_id": post.post_id}
            logger.debug(f"Looking for {query}")
            data = json.loads(post.to_json())
            res = collection.find_one(filter=query)
            if res is None:
                logger.debug(f"Did not find {query}, inserting one")
                result = collection.insert_one(document=data)
                logger.debug(f"Insertion ID: {result.inserted_id}")
            else:
                logger.debug(f"Found {query}, updating one")
                data.pop("seen", None)
                result = collection.find_one_and_update(
                    filter=query,
                    update={"$set": data},
                    return_document=ReturnDocument.AFTER,
                )
                logger.debug(f"Update result: {result}")

    def clean_up_old(self):
        logger.debug("Cleaning up old posts")
        collection = self.get_data_collection()

        two_months: int = 5184000
        unix_time_now: int = int(time.time())
        two_months_ago: int = unix_time_now - two_months

        collection.delete_many(filter={"unix_time": {"$lte": two_months_ago}})
