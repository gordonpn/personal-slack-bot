import concurrent.futures
import logging
import os
import sys
from logging.config import fileConfig

from slack import RTMClient

from .slackbot.slack_bot import Bot

logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger("slack_bot")


@RTMClient.run_on(event="message")
def reply_bot(**payload):
    data = payload["data"]
    web_client = payload["web_client"]

    is_human: bool = data.get("user") == os.getenv("USER_ID")
    bot = Bot(data, web_client)
    # todo parse the message with regex
    if is_human:
        text_received: str = data.get("text").lower()
        logger.debug(f"Passing: {text_received}")
        concurrent.futures.ThreadPoolExecutor().submit(bot.parse_command, text_received)


@RTMClient.run_on(event="hello")
def start_bot(**payload):
    data = payload["data"]
    web_client = payload["web_client"]

    bot = Bot(data, web_client)

    concurrent.futures.ThreadPoolExecutor().submit(bot.reddit_watch)


@RTMClient.run_on(event="goodbye")
def exit_bot():
    sys.exit()


if __name__ == "__main__":
    rtm_client = RTMClient(token=os.getenv("SLACK_TOKEN"))
    rtm_client.start()
