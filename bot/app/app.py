import concurrent.futures
import logging
import os
import re
import sys
import time
from logging.config import fileConfig
from re import Match

from aiohttp import ClientConnectorError
from slack_sdk.rtm import RTMClient

from .slackbot.slack_bot import Bot

logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger("slack_bot")


@RTMClient.run_on(event="message")
def reply_bot(**payload):
    data = payload["data"]
    web_client = payload["web_client"]

    is_human: bool = data.get("user") == os.getenv("USER_ID")
    bot = Bot(data, web_client)
    if is_human:
        text_received: str = data.get("text").lower().strip()
        pattern: str = r"((reddit)\s+(unsub|sub)\s+(\w*)$)|((reddit)\s+(subs)$)"
        match: Match = re.match(pattern, text_received)
        if match is None:
            bot.reply("Invalid syntax\nSyntax: reddit [sub|unsub|subs] [SUBREDDIT]")
        else:
            logger.debug(f"{match.groups()=}")
            concurrent.futures.ThreadPoolExecutor().submit(bot.parse_command, match)


@RTMClient.run_on(event="hello")
def start_bot(**payload):
    data = payload["data"]
    web_client = payload["web_client"]

    bot = Bot(data, web_client)

    concurrent.futures.ThreadPoolExecutor().submit(bot.reddit_watch)


@RTMClient.run_on(event="goodbye")
def exit_bot(**payload):
    sys.exit()


def run():
    try:
        rtm_client = RTMClient(token=os.getenv("SLACK_TOKEN"))
        rtm_client.start()
    except ClientConnectorError as e:
        logger.error("Possibly no internet connection available")
        logger.error(str(e))
        time.sleep(5 * 60)
        exit(1)
