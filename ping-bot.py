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

addresses = {
    "Mum": 30,
    "Titi": 50,
    "Vicki": 202,
    "Dad": 214,
    "Gordon": 216
}


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
        "You're very welcome",
        "Yeah, whatever",
        "You got it bro",
        "I gotchu bruh",
        "Anything for you",
        "Don't mention it",
        "No problem",
        "Don't worry about it"
    ]
    message = random.choice(list_replies)

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
        message = "Nobody is home currently."
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
        text="Let me check that for you.",
        as_user=True
    )


def reply_watch_ping(data, web_client):
    channel_id = data['channel']
    text = data['text'].lower()

    for name, value in addresses.items():
        if name.lower() in text:
            web_client.chat_postMessage(
                channel=channel_id,
                text="I will keep a watch on {} for you.".format(name),
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

    if 'hello' in text:
        reply_hello(data, web_client)

    if 'thanks' in text or 'thank you' in text:
        reply_np(data, web_client)

    if 'who' in text and 'home' in text:
        reply_ping_all(data, web_client)
    elif 'currently' not in text:
        if 'home' in text:
            reply_ping_subset(data, web_client)
        elif 'watch' in text and 'for you' not in text:
            reply_watch_ping(data, web_client)


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    slack_token = os.environ["SLACK_API_TOKEN"]
    rtm_client = slack.RTMClient(token=slack_token)
    rtm_client.start()
