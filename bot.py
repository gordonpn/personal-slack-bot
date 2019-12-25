import sys

import slack

from Configuration.config import get_config
from Configuration.logger import get_logger
from SlackBot.slack_bot import Bot


@slack.RTMClient.run_on(event='message')
def exit_bot(**payload):
    data = payload['data']
    web_client = payload['web_client']

    is_human: bool = data.get('user') == config.slack_config.user_id
    bot = Bot(data, web_client)

    if is_human:
        text_received: str = data.get('text').lower()
        logger.debug(f"Passing: {text_received}")
        bot.parse_message(text_received)


@slack.RTMClient.run_on(event='hello')
def start_bot(**payload):
    data = payload['data']
    web_client = payload['web_client']

    bot = Bot(data, web_client)
    bot.reply_with_message("Hello, here I am")


@slack.RTMClient.run_on(event='goodbye')
def reply_bot(**payload):
    data = payload['data']
    web_client = payload['web_client']

    bot = Bot(data, web_client)
    bot.reply_with_message("Aight imma head out")
    sys.exit()


if __name__ == '__main__':
    logger = get_logger()
    config = get_config()
    rtm_client = slack.RTMClient(token=config.slack_config.token)
    rtm_client.start()
