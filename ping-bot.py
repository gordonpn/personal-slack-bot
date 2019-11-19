import json
import logging
import os
import random
import subprocess
import sys
import threading
import time
from configparser import ConfigParser
from typing import Dict, List, Set

import jenkins
import psutil
import slack
from uptime import uptime

from reddit import reddit


class Bot:
    def __init__(self, data, web_client):
        self.data = data
        self.web_client = web_client
        self.channel_id = data.get('channel')
        self.user = data.get('user')

    def ping_all(self, addresses_list) -> Set[str]:
        active: Set[str] = set()
        logger.debug("attempting to ping all addresses")
        with open(os.devnull, "wb") as limbo:
            for name, value in addresses_list.items():
                ip = f"192.168.1.{value}"
                result = subprocess.Popen(["ping", "-c", "1", "-n", "-W", "5", ip], stdout=limbo, stderr=limbo).wait()
                if result == 0:
                    active.add(name)
        return active

    def reply_hello(self):
        self.post_generic_message(message=f"Hi <@{self.user}>!")

    def reply_np(self):
        list_replies: List[str] = [
            "you're very welcome",
            "yeah, whatever",
            "you got it bro",
            "i gotchu bruh",
            "anything for you",
            "don't mention it",
            "no problem",
            "don't worry about it"
        ]
        message: str = random.choice(list_replies)
        self.post_generic_message(message=message)

    def reply_what(self):
        list_replies: List[str] = [
            "what the hell are you saying man",
            "what language is this?",
            "wat?",
            "huh?",
            "i don't get it",
            "say what now?",
            "yeah... no",
            "just gonna ignore that"
        ]
        message: str = random.choice(list_replies)
        self.post_generic_message(message=message)

    def reply_cpu_load(self):
        cpu_load = [x / psutil.cpu_count() * 100 for x in psutil.getloadavg()]

        message: str = f"i've been working at {cpu_load[2]}% in the last 15 minutes"
        self.post_generic_message(message=message)

    def reply_uptime(self):
        uptime_text: float = round((uptime() / 86400), 2)

        message: str = f"i've up for {uptime_text} days"
        self.post_generic_message(message=message)

    def reply_ping_all(self):
        self.post_generic_message()

        active: Set[str] = self.ping_all(addresses)

        self.post_ping_reply(active)

    def post_ping_reply(self, active: Set[str] = None):
        if not active:
            message: str = "nobody is home currently."
        elif len(active) == 1:
            message: str = "".join(active) + " is home currently."
        else:
            separator = ', '
            active_string = separator.join(active)
            message: str = active_string + " are home currently."

        self.post_generic_message(message=message)

    def reply_ping_subset(self):
        text: str = self.data['text'].lower()

        self.post_generic_message()

        subset_addresses: Dict[str, int] = {}

        for name, value in addresses.items():
            if name.lower() in text:
                subset_addresses[name] = value

        active: Set[str] = self.ping_all(subset_addresses)

        self.post_ping_reply(active)

    def post_generic_message(self, message: str = None):
        if not message:
            message = "let me check that for you."

        self.web_client.chat_postMessage(
            channel=self.channel_id,
            text=message,
            as_user=True
        )

    def reply_reboot(self):
        self.post_generic_message(message="ight imma head out")
        exit()

    def reply_watch_ping(self):
        text = self.data['text'].lower()
        everyone: bool = False
        if 'everyone' in text:
            everyone = True

        for name, value in addresses.items():
            if name.lower() in text or everyone:
                message = f"i will keep a watch on {name} for you."
                self.post_generic_message(message=message)
                logger.debug(f"starting watch thread for {name}")
                threading.Thread(target=self.watch_ping, args=(name, value)).start()

    def watch_ping(self, name, value):
        success: bool = False
        while not success:
            with open(os.devnull, "wb") as limbo:
                ip = f"192.168.1.{value}"
                logger.debug(f"attempting to ping {name}")
                result = subprocess.Popen(["ping", "-c", "1", "-n", "-W", "5", ip], stdout=limbo, stderr=limbo).wait()
                if result == 0:
                    active = set()
                    active.add(name)
                    self.post_ping_reply(active)
                    success = True
                logger.debug("no success, retrying in 10 seconds...")
                time.sleep(10)

    def reply_scrape(self):
        self.post_generic_message(message="updating your moodle courses folder...")

        server = jenkins.Jenkins(jenkins_config['server'], username=jenkins_config['username'],
                                 password=jenkins_config['password'])
        job_name = 'moodle-scraper'
        server.build_job(name=job_name)
        jenkins_channel = 'CNGGCRU21|jenkins-ci'

        message = f"starting {job_name}, check <#{jenkins_channel}>"
        self.post_generic_message(message=message)

    def reply_ram(self):
        with open('/proc/meminfo') as file:
            for line in file:
                if 'MemFree' in line:
                    free_mem_in_kb = line.split()[1]
                    break

        free_mem_in_mb = int(int(free_mem_in_kb, 10) / 1000)
        message = f"i have {free_mem_in_mb} MB free in memory"
        self.post_generic_message(message=message)

    def start_job_watch(self):
        self.post_generic_message(message="starting watch on speedtest jenkins job")
        threading.Thread(target=self._check_speedtest_job).start()

    def _check_speedtest_job(self):
        while True:
            logger.info("checking if speedtest is running")
            server = jenkins.Jenkins(jenkins_config['server'], username=jenkins_config['username'],
                                     password=jenkins_config['password'])
            info = server.get_job_info(name='speedtest-collector')

            if '_anime' not in info['color']:
                self.post_generic_message(message="hey buddy, you might wanna check your speedtest jenkins job")
                self.post_generic_message(message=jenkins_config['job_url'])
            else:
                logger.info("speedtest job still running, not notifying")

            thirty_minutes = 1800
            time.sleep(thirty_minutes)

    def start_reddit_polling(self):
        self.post_generic_message(message="starting reddit polling")
        threading.Thread(target=self._reddit_polling).start()

    def _reddit_polling(self):
        while True:
            logger.info("polling reddit for new hot posts")
            new_posts: Dict[str, str] = reddit.get_unseen_hot_posts()

            for title, url in new_posts.items():
                self.post_generic_message(message=f"<{url}|{title}>")
                time.sleep(10)

            ten_minutes = 600
            time.sleep(ten_minutes)


def get_addresses() -> Dict[str, int]:
    config_addresses: Dict[str, int] = {}
    file_name = "addresses.json"
    if os.path.exists(file_name):
        try:
            logger.info("loading addresses")
            with open(file_name, "r") as read_file:
                config_addresses = json.load(read_file)
                logger.info("loaded addresses successfully")
        except Exception as e:
            logger.error(f"Error getting addresses | {str(e)}")
            sys.exit(-1)

    return config_addresses


def get_config():
    config_parser = ConfigParser()
    file: str = "bot.conf"
    jenkins_conf: Dict[str, str] = {}
    if os.path.exists(file):
        config_parser.read(file)
        logger.info("found config file successfully")
    else:
        raise Exception("config file not found")

    options_list: List[str] = ["username",
                               "password",
                               "server",
                               "job_url"]
    section: str = 'jenkins'

    for option in options_list:
        if not config_parser.has_option(section, option):
            raise Exception(f"config file missing option: {option}")
        elif not config_parser.get(section, option):
            raise Exception(f"config file is missing information for {option}")
        else:
            jenkins_conf[option] = config_parser.get(section, option)

    return jenkins_conf


def get_logger():
    this_logger = logging.getLogger()
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    this_logger.setLevel(logging.DEBUG)
    this_logger.addHandler(console_handler)
    return this_logger


@slack.RTMClient.run_on(event='message')
def reply_to_message(**payload):
    data = payload['data']
    web_client = payload['web_client']
    bot = Bot(data, web_client)
    is_human = data.get('user') == 'UNHGUEDN3'

    if is_human:
        # todo make this a method inside the object Bot
        text = data.get('text').lower()
        logger.debug(f"parsing: {text}")

        if 'hello' in text:
            bot.reply_hello()
        elif 'thanks' in text or 'thank you' in text:
            bot.reply_np()
        elif 'cpu' in text and 'load' in text:
            bot.reply_cpu_load()
        elif 'uptime' in text:
            bot.reply_uptime()
        elif 'reboot' in text:
            bot.reply_reboot()
        elif 'who' in text and 'home' in text:
            bot.reply_ping_all()
        elif 'home' in text:
            bot.reply_ping_subset()
        elif 'watch' in text:
            bot.reply_watch_ping()
        elif 'watch' in text and 'jenkins' in text:
            bot.start_job_watch()
        elif 'scrape' in text:
            bot.reply_scrape()
        elif 'ram' in text:
            bot.reply_ram()
        else:
            bot.reply_what()


@slack.RTMClient.run_on(event='hello')
def say_hi(**payload):
    data = payload['data']
    web_client = payload['web_client']
    data['channel'] = 'DNHTJCXQE'
    data['user'] = bot_id
    # todo how to get this information without hardcoding?

    bot = Bot(data, web_client)
    bot.post_generic_message(message="wassup i'm here")
    bot.start_reddit_polling()


@slack.RTMClient.run_on(event='goodbye')
def say_exit(**payload):
    data = payload['data']
    web_client = payload['web_client']
    data['channel'] = 'DNHTJCXQE'
    data['user'] = bot_id

    bot = Bot(data, web_client)
    bot.post_generic_message(message="aight i'm out")
    sys.exit()


if __name__ == "__main__":
    logger = get_logger()

    slack_token = os.environ["SLACK_API_TOKEN"]
    bot_id = "UN99BD0CR"
    addresses = get_addresses()  # todo move these two inside the object Bot
    jenkins_config = get_config()
    rtm_client = slack.RTMClient(token=slack_token)
    rtm_client.start()
