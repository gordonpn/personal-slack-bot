import concurrent.futures
import logging
import os
import time
from typing import List

logger = logging.getLogger("slack_bot")


class Bot:
    def __init__(self, data, web_client):
        self.data = data
        self.web_client = web_client
        self.data["channel"] = os.getenv("BOT_CHANNEL")
        self.data["user"] = os.getenv("BOT_ID")
        self.channel_id = data.get("channel")
        self.user = data.get("user")

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
        pass

    def unsubscribe(self):
        pass

    def list_subscriptions(self):
        pass

    def format_message(self):
        pass

    def check_subscriptions(self):
        pass
