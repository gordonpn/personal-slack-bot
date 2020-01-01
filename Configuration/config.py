import os
from configparser import ConfigParser
from typing import Dict, List

configs = []


def get_config(file_path: str = 'bot.conf'):
    global configs

    if configs:
        return configs[0]
    else:
        config = Config(file_path)
        config.load_config()
        configs.append(config)
        return config


def as_list(string: str) -> List[str]:
    string: List[str] = string.split(',')
    return [text.strip() for text in string]


class Config:

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.slack_config = SlackConfig()
        self.ping_config = PingConfig()
        self.jenkins_config = JenkinsConfig()
        self.reddit_config = RedditConfig()
        self.darksky_config = DarkSkyConfig()

    def load_config(self):
        config_parser = ConfigParser()
        config_file: str = self.file_path
        config_sections: Dict[str, List[str]] = {
            'slack': ['token', 'bot_id', 'bot_channel', 'user_id'],
            'ping': ['friendly_name', 'addresses'],
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

        self.slack_config.load_config(config_parser)
        self.ping_config.load_config(config_parser)
        self.jenkins_config.load_config(config_parser)
        self.reddit_config.load_config(config_parser)
        self.darksky_config.load_config(config_parser)


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
        self.user_id: str = ""

    def __setitem__(self, key, value):
        if key == 'token':
            self.token = value
        elif key == 'bot_id':
            self.bot_id = value
        elif key == 'bot_channel':
            self.bot_channel = value
        elif key == 'user_id':
            self.user_id = value

    def load_config(self, config_parser: ConfigParser, **kwargs):
        super().load_config(config_parser, self.section)


class PingConfig(ConfigLoader):
    section: str = 'ping'

    def __init__(self):
        self.friendly_name: List[str] = []
        self.addresses: List[str] = []

    def __setitem__(self, key, value):
        value = as_list(value)
        if key == 'addresses':
            self.addresses = value
        elif key is 'friendly_name':
            self.friendly_name = value

    def load_config(self, config_parser: ConfigParser, **kwargs):
        super().load_config(config_parser, self.section)


class JenkinsConfig(ConfigLoader):
    section: str = 'jenkins'

    def __init__(self):
        self.username: str = ""
        self.password: str = ""
        self.server_url: str = ""
        self.job_url: List[str] = []

    def __setitem__(self, key, value):
        if key == 'username':
            self.username = value
        elif key == 'password':
            self.password = value
        elif key == 'server_url':
            self.server_url = value
        elif key == 'job_url':
            self.job_url = as_list(value)

    def load_config(self, config_parser: ConfigParser, **kwargs):
        super().load_config(config_parser, self.section)


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
        if key == 'client_id':
            self.client_id = value
        elif key == 'client_secret':
            self.client_secret = value
        elif key == 'username':
            self.username = value
        elif key == 'password':
            self.password = value
        elif key == 'user_agent':
            self.user_agent = value
        elif key == 'subreddits':
            self.subreddits = as_list(value)
        elif key == 'watchlist':
            self.watchlist = as_list(value)

    def load_config(self, config_parser: ConfigParser, **kwargs):
        super().load_config(config_parser, self.section)


class DarkSkyConfig(ConfigLoader):
    section: str = 'darksky'

    def __init__(self):
        self.key: str = ""
        self.location: str = ""

    def __setitem__(self, key, value):
        if key == 'key':
            self.key = value
        elif key == 'location':
            self.location = value

    def load_config(self, config_parser: ConfigParser, **kwargs):
        super().load_config(config_parser, self.section)
