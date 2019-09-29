import subprocess
from subprocess import call
import logging
import os
import re
import time
import json
import psutil
import slack
import threading
import random
from uptime import uptime
from psutil import virtual_memory

addresses = {
    "Mum": 30,
    "Titi": 50,
    "Vicki": 202,
    "Dad": 214,
    "Gordon": 216
}
bot_id = "UN99BD0CR"


class Bot:
    def __init__(self, data, web_client):
        self.data = data
        self.web_client = web_client
        self.channel_id = data['channel']
        self.user = data['user']

    def ping_all(self, addresses):
        active = set()
        logger.debug("attempting to ping all addresses")
        with open(os.devnull, "wb") as limbo:
            for name, value in addresses.items():
                ip = "192.168.1.{0}".format(value)
                result = subprocess.Popen(["ping", "-c", "1", "-n", "-W", "5", ip], stdout=limbo, stderr=limbo).wait()
                if result == 0:
                    active.add(name)
        return active

    def reply_hello(self):
        self.web_client.chat_postMessage(
            channel=self.channel_id,
            text=f"Hi <@{self.user}>!",
            as_user=True
        )

    def reply_np(self):
        list_replies = [
            "you're very welcome",
            "yeah, whatever",
            "you got it bro",
            "i gotchu bruh",
            "anything for you",
            "don't mention it",
            "no problem",
            "don't worry about it"
        ]
        message = random.choice(list_replies)

        self.web_client.chat_postMessage(
            channel=self.channel_id,
            text=message,
            as_user=True
        )

    def reply_what(self):
        list_replies = [
            "what the hell are you saying man",
            "what language is this?",
            "wat?",
            "huh?",
            "i don't get it",
            "say what now?",
            "yeah... no",
            "just gonna ignore that"
        ]
        message = random.choice(list_replies)

        self.web_client.chat_postMessage(
            channel=self.channel_id,
            text=message,
            as_user=True
        )

    def reply_cpu_load(self):
        cpu_load = [x / psutil.cpu_count() * 100 for x in psutil.getloadavg()]

        message = "i've been working at {}% in the last 15 minutes".format(cpu_load[2])

        self.web_client.chat_postMessage(
            channel=self.channel_id,
            text=message,
            as_user=True
        )

    def reply_uptime(self):
        uptime_text = round((uptime() / 86400), 2)

        message = "i've up for {} days man".format(uptime_text)

        self.web_client.chat_postMessage(
            channel=self.channel_id,
            text=message,
            as_user=True
        )

    def reply_ping_all(self):
        self.post_generic_message()

        active = self.ping_all(addresses)

        self.post_ping_reply(active)

    def post_ping_reply(self, active):
        if not active:
            message = "nobody is home currently."
        elif len(active) == 1:
            message = "".join(active) + " is home currently."
        else:
            seperator = ', '
            active_string = seperator.join(active)
            message = active_string + " are home currently."

        self.web_client.chat_postMessage(
            channel=self.channel_id,
            text=message,
            as_user=True
        )

    def reply_ping_subset(self):
        text = self.data['text'].lower()

        self.post_generic_message()

        subset_addresses = {}

        for name, value in addresses.items():
            if name.lower() in text:
                subset_addresses[name] = value

        active = self.ping_all(subset_addresses)

        self.post_ping_reply(active)

    def post_generic_message(self):
        self.web_client.chat_postMessage(
            channel=self.channel_id,
            text="let me check that for you.",
            as_user=True
        )

    def reply_reboot(self):
        self.web_client.chat_postMessage(
            channel=self.channel_id,
            text="ight imma head out",
            as_user=True
        )
        exit()

    def reply_watch_ping(self):
        text = self.data['text'].lower()
        if 'everyone' in text:
            everyone = True
        else:
            everyone: False

        for name, value in addresses.items():
            if name.lower() in text or everyone:
                self.web_client.chat_postMessage(
                    channel=self.channel_id,
                    text="i will keep a watch on {} for you.".format(name),
                    as_user=True
                )
                logger.debug("starting watch thread for {}".format(name))
                watch_thread = threading.Thread(target=self.watch_ping, args=(name, value))
                watch_thread.start()

    def watch_ping(self, name, value):
        success = False
        while (not success):
            with open(os.devnull, "wb") as limbo:
                ip = "192.168.1.{0}".format(value)
                logger.debug("attempting to ping {}".format(name))
                result = subprocess.Popen(["ping", "-c", "1", "-n", "-W", "5", ip], stdout=limbo, stderr=limbo).wait()
                if result == 0:
                    active = set()
                    active.add(name)
                    self.post_ping_reply(active)
                    success = True
                logger.debug("no success, retrying in 10 seconds...")
                time.sleep(10)


    def reply_scrape(self):
        self.web_client.chat_postMessage(
            channel=self.channel_id,
            text="updating your moodle courses folder...",
            as_user=True
        )
        moodle_scraper = '/mnt/pidrive/resilio-sync/jenkins/moodle-scraper/moodle-scraper.py'
        call(['python3', moodle_scraper])

    def reply_ram(self):
        with open('/proc/meminfo') as file:
            for line in file:
                if 'MemFree' in line:
                    free_mem_in_kb = line.split()[1]
                    break

        free_mem_in_mb = int(int(free_mem_in_kb, 10) / 1000);
        message = "i have {} MB free in memory".format(free_mem_in_mb)

        self.web_client.chat_postMessage(
            channel=self.channel_id,
            text=message,
            as_user=True
        )


@slack.RTMClient.run_on(event='message')
def reply_to_message(**payload):
    data = payload['data']
    web_client = payload['web_client']
    rtm_client = payload['rtm_client']
    text = data['text'].lower()
    logger.debug("parsing: {}".format(text))
    is_not_bot = data['user'] != bot_id

    bot = Bot(data, web_client)

    if is_not_bot:
        if 'hello' in text:
            bot.reply_hello()
        elif 'thanks' in text or 'thank you' in text:
            bot.reply_np()
        elif 'cpu' in text and 'load' in text:
            bot.reply_cpu_load()
        elif 'uptime' in text:
            bot.reply_uptime()
        elif 'fuck you bender' in text or 'reboot' in text:
            bot.reply_reboot()
        elif 'who' in text and 'home' in text:
            bot.reply_ping_all()
        elif 'home' in text:
            bot.reply_ping_subset()
        elif 'watch' in text:
            bot.reply_watch_ping()
        elif 'scrape' in text:
            bot.reply_scrape()
        elif 'ram' in text:
            bot.reply_ram()
        else:
            bot.reply_what()


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    slack_token = os.environ["SLACK_API_TOKEN"]
    rtm_client = slack.RTMClient(token=slack_token)
    rtm_client.start()
