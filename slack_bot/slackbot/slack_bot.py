import concurrent.futures
import logging
import os
import time
from re import Match
from typing import Any, Dict, List

from bson.json_util import dumps
from pymongo.cursor import Cursor
from requests import Response

import requests
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from ..reddit_post.reddit_post import RedditPost

logger = logging.getLogger("slack_bot")


class Bot:
    def __init__(self, data, web_client):
        self.data = data
        self.web_client = web_client
        self.data["channel"] = os.getenv("BOT_CHANNEL")
        self.data["user"] = os.getenv("BOT_ID")
        self.channel_id = data.get("channel")
        self.user = data.get("user")
        self.db_name = os.getenv("MONGO_INITDB_DATABASE")
        self.db_username = os.getenv("MONGO_NON_ROOT_USERNAME")
        self.db_password = os.getenv("MONGO_NON_ROOT_PASSWORD")
        self.db_collection = os.getenv("MONGO_COLLECTION")
        self.db_settings = os.getenv("MONGO_SETTINGS")

    def reply(self, message: str = None):
        if not message:
            message = "Let me check that for you."

        self.web_client.chat_postMessage(
            channel=self.channel_id, text=message, as_user=True
        )

    def parse_command(self, text_match: Match):
        command: str = text_match.group(2)
        if command == "subs":
            self.list_subscriptions()
        else:
            subreddit_name: str = text_match.group(3)

            if command == "sub":
                self.subscribe(subreddit_name)
            elif command == "unsub":
                self.unsubscribe(subreddit_name)

    def reddit_watch(self) -> None:
        logger.debug("Checking subreddits on watchlist")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(RedditWatcher().check_new)
            messages: List[str] = future.result()

        if type(messages) == list and messages:
            for a_message in messages:
                self.reply(a_message)
                time.sleep(3)

        time.sleep(30 * 60)
        self.reddit_watch()

    def subscribe(self, subreddit: str) -> None:
        collection = self.get_settings_collection()
        if not self.validate_subreddit(subreddit):
            self.reply("Invalid subreddit, please check the subreddit name")
            return
        collection.update_one(upsert=True)
        # todo find one and append the subreddit

    def unsubscribe(self, subreddit: str) -> None:
        collection = self.get_settings_collection()
        # todo find one and pop the matching subreddit if exists

    def list_subscriptions(self) -> None:
        collection = self.get_settings_collection()
        cursor: Cursor = collection.find_one()
        if cursor is None:
            self.reply("You are currently not subscribed to any subreddits")
            return
        doc: Dict[str, Any] = dumps(cursor)
        subs: List[str] = doc.get("subreddits", [])
        self.reply(f"You are subscribed to {', '.join(subs)}")

    def check_subscriptions(self) -> None:
        collection = self.get_data_collection()
        # todo automate checking the database for any unseen posts

    def validate_subreddit(self, subreddit: str) -> bool:
        res: Response = requests.head(url=f"https://reddit.com/r/{subreddit}")
        return bool(res.ok)

    def format_message(self, posts: List[RedditPost]) -> List[str]:
        formatted_list: List[str] = []
        for post in posts:
            if post.is_self:
                string = f"{post.title} posted in <https://www.reddit.com/r/{post.subreddit}|{post.subreddit}>\n<https://redd.it/{post.id}>"
            else:
                string = f"<{post.link}|{post.title}> posted in <https://www.reddit.com/r/{post.subreddit}|{post.subreddit}>\n<https://redd.it/{post.id}> "
            formatted_list.append(string)
        return formatted_list

    def connect_to_db(self) -> Database:
        logger.debug("Making connection to mongodb")
        uri: str = f"mongodb://{self.db_username}:{self.db_password}@mongo-db:27017/{self.db_name}"
        connection: MongoClient = MongoClient(uri)
        db: Database = connection[self.db_name]
        return db

    def get_settings_collection(self) -> Collection:
        db = self.connect_to_db()
        return db.collection[self.db_settings]

    def get_data_collection(self) -> Collection:
        db = self.connect_to_db()
        return db.collection[self.db_collection]
