import logging
import os
from configparser import ConfigParser
from typing import Dict, List

import praw


def authenticate():
    reddit = praw.Reddit(client_id=config["client_id"],
                         client_secret=config["client_secret"],
                         password=config["password"],
                         user_agent=config["user_agent"],
                         username=config["username"])
    return reddit


def get_config() -> Dict[str, str]:
    config_parser = ConfigParser()
    config_file: str = '../bot.conf'

    if not os.path.exists(config_file):
        raise Exception("config file not found")
    else:
        config_parser.read(config_file)

    section: str = 'reddit'
    options_list: List[str] = ["client_id",
                               "client_secret",
                               "password",
                               "user_agent",
                               "username"]
    configuration: Dict[str, str] = {}

    if not config_parser.has_section(section):
        raise Exception("config file missing reddit section")

    for option in options_list:
        if not config_parser.has_option(section, option):
            raise Exception("config file missing option: {}".format(option))
        else:
            configuration[option] = config_parser.get(section, option)

    return configuration


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

if __name__ == '__main__':
    config = get_config()
    ayy = authenticate()
    print(ayy.user.me())
