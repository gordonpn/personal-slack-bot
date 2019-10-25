import logging
import os
from configparser import ConfigParser
from typing import Dict, List

import praw
from praw import Reddit
from praw.models import ListingGenerator, Submission


def _get_instance() -> Reddit:
    config: Dict[str, str] = _get_config()
    reddit: Reddit = praw.Reddit(client_id=config["client_id"],
                                 client_secret=config["client_secret"],
                                 password=config["password"],
                                 user_agent=config["user_agent"],
                                 username=config["username"])
    return reddit


def _get_config() -> Dict[str, str]:
    config_parser: ConfigParser = _get_config_parser()

    options_list: List[str] = ["client_id",
                               "client_secret",
                               "password",
                               "user_agent",
                               "username"]
    configuration: Dict[str, str] = {}

    for option in options_list:
        if not config_parser.has_option(section, option):
            raise Exception("config file missing option: {}".format(option))
        elif not config_parser.get(section, option):
            raise Exception("config file is missing information for {}".format(option))
        else:
            configuration[option] = config_parser.get(section, option)

    return configuration


def _get_config_parser() -> ConfigParser:
    config_parser = ConfigParser()
    config_file: str = '../bot.conf'
    if not os.path.exists(config_file):
        raise Exception("config file not found")
    else:
        config_parser.read(config_file)

    if not config_parser.has_section(section):
        raise Exception("config file missing reddit section")

    return config_parser


def _get_subreddits() -> List[str]:
    config_parser: ConfigParser = _get_config_parser()
    subreddits_as_string: str
    # subreddits: List[str] = []

    if not config_parser.has_option(section, 'subreddits'):
        raise Exception("config file missing subreddits watchlist")
    elif not config_parser.get(section, 'subreddits'):
        raise Exception("config file doesn't have list of subreddits to watch")
    else:
        subreddits_as_string = config_parser.get(section, 'subreddits')

    subreddits: List[str] = subreddits_as_string.lower().split(",")
    subreddits = [text.strip() for text in subreddits]

    return subreddits


def _read_seen():
    pass


def _write_seen():
    pass


def _mark_as_seen():
    pass


def get_hot_posts() -> List[Submission]:
    instance = _get_instance()
    subreddits = _get_subreddits()
    limit: int = 15
    submissions_list: List[Submission] = []

    for subreddit in subreddits:
        submissions: ListingGenerator = instance.subreddit(subreddit).hot(limit=limit)
        for submission in submissions:
            submissions_list.append(submission)

    return submissions_list


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
section: str = 'reddit'
