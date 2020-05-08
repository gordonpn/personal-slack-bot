import concurrent.futures
import logging
import os
import time
from re import Match
from typing import List

import schedule

import requests
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.cursor import Cursor
from pymongo.database import Database
from requests import Response

from ..healthcheck.healthcheck import HealthCheck, Status

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
        if text_match.group(7) == "subs":
            self.list_subscriptions()
        else:
            subreddit_name: str = text_match.group(4)

            if text_match.group(3) == "sub":
                self.subscribe(subreddit_name)
            elif text_match.group(3) == "unsub":
                self.unsubscribe(subreddit_name)

    def subscribe(self, subreddit: str) -> None:
        collection = self.get_settings_collection()
        if not self.validate_subreddit(subreddit):
            self.reply("Invalid subreddit, please check the subreddit name")
            return
        cursor: Cursor = collection.find_one()
        if cursor is None:
            res = collection.insert_one({"subreddits": [subreddit]})
            if res.acknowledged:
                self.reply(f"Successfully subscribed to {subreddit}")
            else:
                self.reply(f"Unsuccessfully subscribed to {subreddit}")
            return
        doc_id: str = cursor["_id"]
        res = collection.find_one_and_update(
            filter={"_id": doc_id}, update={"$push": {"subreddits": subreddit}}
        )
        if res is not None:
            self.reply("Subscription successful")
            self.list_subscriptions()
        else:
            self.reply("Subscription unsuccessful")

    def unsubscribe(self, subreddit: str) -> None:
        collection = self.get_settings_collection()
        cursor: Cursor = collection.find_one()
        if cursor is None:
            self.reply("You are not currently subscribed to any subreddit")
            return
        doc_id: str = cursor["_id"]
        res = collection.find_one_and_update(
            filter={"_id": doc_id}, update={"$pull": {"subreddits": subreddit}}
        )
        if res is not None:
            self.reply("Unsubscription successful")
            self.list_subscriptions()
        else:
            self.reply("Unsubscription unsuccessful")

    def list_subscriptions(self) -> None:
        collection = self.get_settings_collection()
        cursor: Cursor = collection.find_one()
        if cursor is None:
            self.reply("You are currently not subscribed to any subreddits")
            return
        subs: List[str] = cursor["subreddits"]
        self.reply(f"You are subscribed to {', '.join(subs)}")

    def reddit_watch(self) -> None:
        logger.debug("Setting schedule")
        if "DEV_RUN" in os.environ:
            schedule.every(1).minutes.do(self.reddit_watch_job)
        else:
            schedule.every(30).to(40).minutes.do(self.reddit_watch_job)

        logger.debug("Pending scheduled job")
        while True:
            schedule.run_pending()
            time.sleep(1)

    def reddit_watch_job(self) -> None:
        HealthCheck.ping_status(Status.START)
        logger.debug("Checking database for unseen posts")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(self.check_subscriptions)
            messages: List[str] = future.result()

        if type(messages) == list and messages:
            for a_message in messages:
                self.reply(a_message)
                time.sleep(3)
        HealthCheck.ping_status(Status.SUCCESS)

    def check_subscriptions(self) -> List[str]:
        logger.debug("Checking subscriptions")
        collection = self.get_data_collection()
        cursor: Cursor = collection.find(filter={"seen": {"$eq": False}})
        if cursor is None:
            return []
        messages: List[str] = []
        for doc in cursor:
            logger.debug(doc)
            messages.append(self.format_message(doc))
            _id: str = doc["_id"]
            collection.find_one_and_update(
                filter={"_id": _id}, update={"$set": {"seen": True}}
            )
        return messages

    def validate_subreddit(self, subreddit: str) -> bool:
        res: Response = requests.head(url=f"https://reddit.com/r/{subreddit}")
        return bool(res.ok)

    def format_message(self, post) -> str:
        if post["is_self"]:
            string = f"{post['title']} posted in <https://www.reddit.com/r/{post['subreddit']}|{post['subreddit']}>\n<https://redd.it/{post['post_id']}>"
        else:
            string = f"<{post['link']}|{post['title']}> posted in <https://www.reddit.com/r/{post['subreddit']}|{post['subreddit']}>\n<https://redd.it/{post['post_id']}> "
        return string

    def connect_to_db(self) -> Database:
        logger.debug("Making connection to mongodb")
        host = "slack-bot_mongo-db"
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
