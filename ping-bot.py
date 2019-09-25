import subprocess
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
from gpiozero import CPUTemperature

addresses = {
    "Mum": 30,
    "Titi": 50,
    "Vicki": 202,
    "Dad": 214,
    "Gordon": 216
}
bot_id = "UN99BD0CR"


def ping_all(addresses):
    active = set()
    logger.debug("attempting to ping all addresses")
    with open(os.devnull, "wb") as limbo:
        for name, value in addresses.items():
            ip = "192.168.1.{0}".format(value)
            result = subprocess.Popen(["ping", "-c", "1", "-n", "-W", "5", ip], stdout=limbo, stderr=limbo).wait()
            if result == 0:
                active.add(name)
    return active


def reply_hello(data, web_client):
    channel_id = data['channel']
    user = data['user']

    web_client.chat_postMessage(
        channel=channel_id,
        text=f"Hi <@{user}>!",
        as_user=True
    )


def reply_np(data, web_client):
    channel_id = data['channel']
    user = data['user']
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

    web_client.chat_postMessage(
        channel=channel_id,
        text=message,
        as_user=True
    )


def reply_what(data, web_client):
    channel_id = data['channel']
    user = data['user']
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

    web_client.chat_postMessage(
        channel=channel_id,
        text=message,
        as_user=True
    )


def reply_cpu_load(data, web_client):
    channel_id = data['channel']
    user = data['user']

    cpu_load = [x / psutil.cpu_count() * 100 for x in psutil.getloadavg()]

    message = "i've been working at {}% in the last 15 minutes".format(cpu_load[2])

    web_client.chat_postMessage(
        channel=channel_id,
        text=message,
        as_user=True
    )


def reply_uptime(data, web_client):
    channel_id = data['channel']
    user = data['user']

    uptime_text = round((uptime() / 86400), 2)

    message = "i've up for {} days man".format(uptime_text)

    web_client.chat_postMessage(
        channel=channel_id,
        text=message,
        as_user=True
    )


def reply_temp(data, web_client):
    channel_id = data['channel']
    user = data['user']

    cpu_temp = CPUTemperature()

    message = "current temperatue is {} degrees Celsius".format(cpu_temp.temperature)

    web_client.chat_postMessage(
        channel=channel_id,
        text=message,
        as_user=True
    )


def reply_ping_all(data, web_client):
    channel_id = data['channel']

    post_generic_message(channel_id, web_client)

    active = ping_all(addresses)

    post_ping_reply(channel_id, web_client, active)


def post_ping_reply(channel_id, web_client, active):
    if not active:
        message = "nobody is home currently."
    elif len(active) == 1:
        message = "".join(active) + " is home currently."
    else:
        seperator = ', '
        active_string = seperator.join(active)
        message = active_string + " are home currently."

    web_client.chat_postMessage(
        channel=channel_id,
        text=message,
        as_user=True
    )


def reply_ping_subset(data, web_client):
    channel_id = data['channel']
    text = data['text'].lower()

    post_generic_message(channel_id, web_client)

    subset_addresses = {}

    for name, value in addresses.items():
        if name.lower() in text:
            subset_addresses[name] = value

    active = ping_all(subset_addresses)

    post_ping_reply(channel_id, web_client, active)


def post_generic_message(channel_id, web_client):
    web_client.chat_postMessage(
        channel=channel_id,
        text="let me check that for you.",
        as_user=True
    )


def reply_reboot(data, web_client):
    channel_id = data['channel']
    user = data['user']

    web_client.chat_postMessage(
        channel=channel_id,
        text="ight imma head out",
        as_user=True
    )


def reply_watch_ping(data, web_client):
    channel_id = data['channel']
    text = data['text'].lower()

    for name, value in addresses.items():
        if name.lower() in text:
            web_client.chat_postMessage(
                channel=channel_id,
                text="i will keep a watch on {} for you.".format(name),
                as_user=True
            )
            logger.debug("starting watch thread for {}".format(name))
            watch_thread = threading.Thread(target=watch_ping, args=(data, web_client, name, value))
            watch_thread.start()


def watch_ping(data, web_client, name, value):
    success=False
    while (not success):
        with open(os.devnull, "wb") as limbo:
            ip = "192.168.1.{0}".format(value)
            logger.debug("attempting to ping {}".format(name))
            result = subprocess.Popen(["ping", "-c", "1", "-n", "-W", "5", ip], stdout=limbo, stderr=limbo).wait()
            if result == 0:
                active = set()
                active.add(name)
                post_ping_reply(data['channel'], web_client, active)
                success=True
            logger.debug("no success, retrying in 10 seconds...")
            time.sleep(10)


@slack.RTMClient.run_on(event='message')
def reply_to_message(**payload):
    data = payload['data']
    web_client = payload['web_client']
    rtm_client = payload['rtm_client']
    text = data['text'].lower()
    logger.debug("parsing: {}".format(text))
    is_not_bot = data['user'] != bot_id

    if is_not_bot:
        if 'hello' in text:
            reply_hello(data, web_client)
        elif 'thanks' in text or 'thank you' in text:
            reply_np(data, web_client)
        elif 'cpu' in text and 'load' in text:
            reply_cpu_load(data, web_client)
        elif 'uptime' in text:
            reply_uptime(data, web_client)
        elif 'fuck you bender' in text or 'reboot' in text:
            reply_reboot(data, web_client)
            exit()
        elif 'who' in text and 'home' in text:
            reply_ping_all(data, web_client)
        elif 'home' in text:
            reply_ping_subset(data, web_client)
        elif 'watch' in text:
            reply_watch_ping(data, web_client)
        else:
            reply_what(data, web_client)


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    slack_token = os.environ["SLACK_API_TOKEN"]
    rtm_client = slack.RTMClient(token=slack_token)
    rtm_client.start()
