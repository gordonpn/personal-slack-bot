import time
from random import random
from typing import List

import psutil
from uptime import uptime

from Configuration.config import get_config
from Configuration.logger import get_logger
from Jenkins.jenkins_bot import JenkinsBot
from PingBot.ping_bot import PingBot
from Reddit.reddit_bot import RedditBot
from Weather.weather_bot import WeatherBot


class Bot:
    def __init__(self, data, web_client):
        self.logger = get_logger()
        self.data = data
        self.web_client = web_client
        self.config = get_config()
        self.data['channel'] = self.config.slack_config.bot_channel
        self.data['user'] = self.config.slack_config.bot_id
        self.channel_id = data.get('channel')
        self.user = data.get('user')

    def reply_with_message(self, message: str = None):
        if not message:
            message = "Let me check that for you."

        self.web_client.chat_postMessage(
            channel=self.channel_id,
            text=message,
            as_user=True
        )

    def parse_message(self, message_received: str = None):
        message = "I do not recognize that command"

        if 'thank' in message_received:
            message = self.reply_welcome()
        elif 'hello' in message_received:
            message = f"Hi <@{self.config.slack_config.user_id}>!"
        elif 'reboot' in message_received:
            self.reply_with_message("Aight imma head out")
            exit()
        elif 'ram' in message_received:
            message = self.reply_ram()
        elif 'cpu' in message_received and 'load' in message_received:
            message = self.reply_cpu_load()
        elif 'uptime' in message_received:
            message = self.reply_uptime()
        elif 'ping' in message_received:
            pinger = PingBot()
            message = pinger.parse_message(message_received)
        elif 'jenkins' in message_received:
            jenkins_bot = JenkinsBot()
            message = jenkins_bot.parse_message(message_received)
        elif 'reddit' in message_received:
            reddit_bot = RedditBot()
            message = reddit_bot.parse_message(message_received)
        elif 'weather' in message_received:
            weather_bot = WeatherBot()
            message = weather_bot.parse_message(message_received)

        if type(message) == list:
            for a_message in message:
                self.reply_with_message(a_message)
                time.sleep(3)

        self.reply_with_message(message)

    def reply_welcome(self) -> str:
        list_replies: List[str] = [
            "You're welcome",
            "Yeah, whatever",
            "You got it bro",
            "I gotchu bruh",
            "Anything for you",
            "Don't mention it",
            "No problem",
            "Don't worry about it"
        ]
        message: str = random.choice(list_replies)
        self.logger.debug(f"Returning: {message}")
        return message

    def reply_cpu_load(self) -> str:
        cpu_load = [x / psutil.cpu_count() * 100 for x in psutil.getloadavg()]

        message: str = f"I've been working at {cpu_load[2]}% in the last 15 minutes"
        self.logger.debug(f"Returning: {message}")
        return message

    def reply_uptime(self) -> str:
        uptime_text: float = round((uptime() / 86400), 2)

        message: str = f"I've up for {uptime_text} days"
        self.logger.debug(f"Returning: {message}")
        return message

    def reply_ram(self) -> str:
        with open('/proc/meminfo') as file:
            for line in file:
                if 'MemFree' in line:
                    free_mem_in_kb = line.split()[1]
                    break

        free_mem_in_mb = int(int(free_mem_in_kb, 10) / 1000)
        message = f"I have {free_mem_in_mb} MB free in memory"
        self.logger.debug(f"Returning: {message}")
        return message
