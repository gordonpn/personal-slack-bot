import json
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


def _get_path() -> str:
    return "seen_reddit_posts.json"


def _read_seen() -> List[Submission]:
    if os.path.exists(_get_path()):
        try:
            with open(_get_path(), 'r') as read_file:
                submissions_list: List[Submission] = []
                id_list = json.load(read_file)
                for post_id in id_list:
                    submissions_list.append(Submission(reddit=_get_instance(), id=post_id))
                return submissions_list
        except ValueError:
            return []
    else:
        return []


def _write_seen(submissions_list: List[Submission] = None):
    list_to_write: List[str] = []
    for sub in submissions_list:
        list_to_write.append(sub.id)
    with open(_get_path(), 'w+') as write_file:
        json.dump(list_to_write, write_file, indent=4)


def _mark_as_seen(new_list: List[Submission] = None):
    old_list: List[Submission] = _read_seen()
    for sub in new_list:
        old_list.append(sub)
    _write_seen(old_list)


def _get_new() -> List[Submission]:
    fresh_list = _get_hot_posts()
    old_list: List[Submission] = _read_seen()
    temp_set = set(old_list)
    new_list = [item for item in fresh_list if item not in temp_set]

    _mark_as_seen(fresh_list)
    return new_list


def _populate_submissions(list_of_submissions: List[Submission] = None) -> Dict[str, str]:
    hot_posts: Dict[str, str] = {}

    for sub in list_of_submissions:
        hot_posts[sub.title] = sub.url

    return hot_posts


def _get_hot_posts() -> List[Submission]:
    instance = _get_instance()
    subreddits = _get_subreddits()
    limit: int = 15
    submissions_list: List[Submission] = []

    for subreddit in subreddits:
        submissions: ListingGenerator = instance.subreddit(subreddit).hot(limit=limit)
        for submission in submissions:
            submissions_list.append(submission)

    return submissions_list


def get_unseen_hot_posts() -> Dict[str, str]:
    hot_posts = _populate_submissions(_get_new())
    return hot_posts


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
section: str = 'reddit'
