import logging
import os
from typing import List

import pymongo
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

logger = logging.getLogger("reddit_scraper")


class RedditScraper:
    def __init__(self):
        self.client_id = os.getenv("REDDIT_CLIENT_ID")
        self.client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        self.username = os.getenv("REDDIT_USERNAME")
        self.password = os.getenv("REDDIT_PASSWORD")
        self.user_agent = os.getenv("REDDIT_USER_AGENT")
        self.db_name = os.getenv("MONGO_INITDB_DATABASE")
        self.db_username = os.getenv("MONGO_NON_ROOT_USERNAME")
        self.db_password = os.getenv("MONGO_NON_ROOT_PASSWORD")
        self.db_settings = os.getenv("MONGO_SETTINGS")
        self.db_collection = os.getenv("MONGO_COLLECTION")

    def run(self):
        pass

    def connect_to_db(self) -> Database:
        logger.debug("Making connection to mongodb")
        uri: str = f"mongodb://{self.db_username}:{self.db_password}@mongo-db:27017/{self.db_name}"
        connection: MongoClient = MongoClient(uri)
        db: Database = connection[self.db_name]
        return db

    def check_subscriptions(self, db: Database) -> List[str]:
        collection: Collection = db[self.db_settings]

        # todo get list of subreddits subscribed to and return said list

    def scrape(self) -> None:
        pass

    def insert(self, db: Database, posts):
        collection: Collection = db[self.db_collection]

        # todo insert data into collection
        # if using dataclass then
        # json_data = json.loads(dataclass.to_json())

    def clean_up_old(self):
        pass
