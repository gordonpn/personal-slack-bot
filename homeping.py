import subprocess
import logging
import os
import re
import time
import json
import psutil
import slack

addresses = {
    "Mum": 30,
    "Titi": 50,
    "Vicki": 202,
    "Dad": 214,
    "Gordon": 216
}


def ping_phones():
    with open(os.devnull, "wb") as limbo:
        for name, value in addresses.items():
            ip = "192.168.1.{0}".format(value)
            result = subprocess.Popen(["ping", "-c", "1", "-n", "-W", "2", ip], stdout=limbo, stderr=limbo).wait()
            # if result is anything but 1, ping returns 0 when successful
            # in python, 1 is true
            if result:
                print(name, "inactive")
            else:
                print(name, "active")


def reply_hello(data, web_client):
    channel_id = data['channel']
    thread_ts = data['ts']
    user = data['user']

    web_client.chat_postMessage(
        channel=channel_id,
        text=f"Hi <@{user}>!"
        # thread_ts=thread_ts
    )


@slack.RTMClient.run_on(event='message')
def say_hello(**payload):
    data = payload['data']
    web_client = payload['web_client']
    rtm_client = payload['rtm_client']
    if 'Hello' in data['text']:
        reply_hello(data, web_client)

if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    slack_token = os.environ["SLACK_API_TOKEN"]
    rtm_client = slack.RTMClient(token=slack_token)
    rtm_client.start()
