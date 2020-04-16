import concurrent.futures
import logging
import sys
import time
from random import random
from typing import List

import psutil
from uptime import uptime

from Monitor.monitor_bot import MonitorBot
from Reddit.reddit_bot import RedditBot, RedditWatcher

logger = logging.getLogger("slack_bot")


class Bot:
    def __init__(self, data, web_client):
        self.data = data
        self.web_client = web_client
        self.data["channel"] = self.config.slack_config.bot_channel
        self.data["user"] = self.config.slack_config.bot_id
        self.channel_id = data.get("channel")
        self.user = data.get("user")

    def reply_with_message(self, message: str = None):
        if not message:
            message = "Let me check that for you."

        self.web_client.chat_postMessage(
            channel=self.channel_id, text=message, as_user=True
        )

    def parse_message(self, message_received: str = None):
        message = "I do not recognize that command"

        if "hello" in message_received:
            message = f"Hi <@{self.config.slack_config.user_id}>!"
        elif "reddit" in message_received:
            reddit_bot = RedditBot()
            message = reddit_bot.parse_message(message_received)

        if type(message) == list:
            for a_message in message:
                self.reply_with_message(a_message)
                time.sleep(3)
        else:
            self.reply_with_message(message)

    def reddit_watch(self) -> None:
        logger.debug("Checking subreddits on watchlist")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(RedditWatcher().check_new)
            messages: List[str] = future.result()

        if type(messages) == list and messages:
            for a_message in messages:
                self.reply_with_message(a_message)
                time.sleep(3)

        time.sleep(15 * 60)
        self.reddit_watch()

    def site_watch(self) -> None:
        logger.debug("Monitoring sites")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(MonitorBot().check_sites)
            messages: List[str] = future.result()

        if type(messages) == list and messages:
            for a_message in messages:
                self.reply_with_message(a_message)
                time.sleep(3)

        time.sleep(90 * 60)
        self.site_watch()
