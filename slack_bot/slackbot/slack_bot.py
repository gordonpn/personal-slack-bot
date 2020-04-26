import concurrent.futures
import logging
import os
import time
from typing import Dict, List, Union

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

    def parse_command(self, message_received: str = None):
        message = "I do not recognize that command"
        # todo parse the message a second time here to see which option user wants
        if "reddit" in message_received:
            reddit_bot = RedditBot()
            message = reddit_bot.parse_command(message_received)

        if type(message) == list:
            for a_message in message:
                self.reply(a_message)
                time.sleep(3)
        else:
            self.reply(message)

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

    def subscribe(self):
        collection = self.get_settings_collection()
        # todo

    def unsubscribe(self):
        collection = self.get_settings_collection()
        # todo

    def list_subscriptions(self):
        collection = self.get_settings_collection()
        # todo

    def format_message(self, posts: List[RedditPost]) -> List[str]:
        formatted_list: List[str] = []
        for post in posts:
            if post.is_self:
                string = f"{post.title} posted in <https://www.reddit.com/r/{post.subreddit}|{post.subreddit}>\n<https://redd.it/{post.id}>"
            else:
                string = f"<{post.link}|{post.title}> posted in <https://www.reddit.com/r/{post.subreddit}|{post.subreddit}>\n<https://redd.it/{post.id}> "
            formatted_list.append(string)
        return formatted_list

    def check_subscriptions(self):
        collection = self.get_data_collection()
        # todo

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
