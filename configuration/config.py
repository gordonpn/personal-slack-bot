import os
from configparser import ConfigParser
from typing import List, Dict


class Config:

    def __init__(self):
        self.slack_config = SlackConfig()
        self.ping_config = PingConfig()
        self.jenkins_config = JenkinsConfig()
        self.reddit_config = RedditConfig()

    def load_config(self):
        config_parser = ConfigParser()
        config_file: str = '../bot.conf'
        config_sections: Dict[str, List[str]] = {
            'slack': ['token', 'bot_id', 'bot_channel'],
            'ping': ['addresses'],
            'jenkins': ['username', 'password', 'server_url', 'job_url'],
            'reddit': ['client_id', 'client_secret', 'username', 'password', 'user_agent', 'subreddits', 'watchlist']
        }
        if not os.path.exists(config_file):
            raise Exception(f"{config_file} not found")
        config_parser.read(config_file)

        for section, options in config_sections.items():
            if not config_parser.has_section(section):
                raise Exception(f"Missing section: {section}")
            for option in options:
                if not config_parser.has_option(section, option):
                    raise Exception(f"Missing option: {option} under {section}")

        self.slack_config.load_config(config_parser, 'slack')
        self.ping_config.load_config(config_parser, 'ping')
        self.jenkins_config.load_config(config_parser, 'jenkins')
        self.reddit_config.load_config(config_parser, 'reddit')


class ConfigLoader:
    def __setitem__(self, key, value):
        pass

    def load_config(self, config_parser: ConfigParser, section: str):
        for attr in self.__dict__.keys():
            self[attr] = config_parser.get(section, attr)


class SlackConfig(ConfigLoader):
    section: str = 'slack'

    def __init__(self):
        self.token: str = ""
        self.bot_id: str = ""
        self.bot_channel: str = ""

    def __setitem__(self, key, value):
        if key == 'token':
            self.token = value
        elif key == 'bot_id':
            self.bot_id = value
        elif key == 'bot_channel':
            self.bot_channel = value


class PingConfig(ConfigLoader):
    section: str = 'ping'

    def __init__(self):
        self.addresses: List[str] = []

    def __setitem__(self, key, value):
        if key is 'addresses':
            self.addresses = value


class JenkinsConfig(ConfigLoader):
    section: str = 'jenkins'

    def __init__(self):
        self.username: str = ""
        self.password: str = ""
        self.server_url: str = ""
        self.job_url: List[str] = []

    def __setitem__(self, key, value):
        if key is 'username':
            self.username = value
        elif key is 'password':
            self.password = value
        elif key is 'server_url':
            self.server_url = value
        elif key is 'job_url':
            self.job_url = value


class RedditConfig(ConfigLoader):
    section: str = 'reddit'

    def __init__(self):
        self.client_id: str = ""
        self.client_secret: str = ""
        self.username: str = ""
        self.password: str = ""
        self.user_agent: str = ""
        self.subreddits: List[str] = []
        self.watchlist: List[str] = []

    def __setitem__(self, key, value):
        if key is 'client_id':
            self.client_id = value
        elif key is 'client_secret':
            self.client_secret = value
        elif key is 'username':
            self.username = value
        elif key is 'password':
            self.password = value
        elif key is 'user_agent':
            self.user_agent = value
        elif key is 'subreddits':
            self.subreddits = value
        elif key is 'watchlist':
            self.watchlist = value
