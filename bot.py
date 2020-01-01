import sys
import concurrent.futures

import slack

from Configuration.bot import get_bot
from Configuration.config import get_config
from Configuration.logger import get_logger


@slack.RTMClient.run_on(event='message')
def exit_bot(**payload):
    data = payload['data']
    web_client = payload['web_client']

    is_human: bool = data.get('user') == config.slack_config.user_id
    bot = get_bot(data, web_client)

    if is_human:
        text_received: str = data.get('text').lower()
        logger.debug(f"Passing: {text_received}")
        concurrent.futures.ThreadPoolExecutor().submit(bot.parse_message, text_received)


@slack.RTMClient.run_on(event='hello')
def start_bot(**payload):
    data = payload['data']
    web_client = payload['web_client']

    bot = get_bot(data, web_client)
    bot.reply_with_message("Hello, here I am")
    concurrent.futures.ThreadPoolExecutor().submit(bot.reddit_watch)


@slack.RTMClient.run_on(event='goodbye')
def reply_bot(**payload):
    data = payload['data']
    web_client = payload['web_client']

    bot = get_bot(data, web_client)
    bot.reply_with_message("Aight imma head out")
    sys.exit()


if __name__ == '__main__':
    logger = get_logger()
    config = get_config()
    rtm_client = slack.RTMClient(token=config.slack_config.token)
    rtm_client.start()
