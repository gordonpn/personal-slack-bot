import json
from typing import List, Union

import praw
from praw import Reddit
from praw.models import ListingGenerator

from Configuration.config import get_config
from Configuration.logger import get_logger
from Reddit.reddit_post import RedditPost


class RedditScraper:
    def __init__(self):
        self.config = get_config('../bot.conf')
        self.reddit: Reddit = self.get_reddit()
        self.logger = get_logger()

    def run(self):
        fresh_hot_posts: List[RedditPost] = self.get_fresh_hot_posts()
        self.write_to_file(fresh_hot_posts)
        posts: List[RedditPost] = self.read_from_file()
        self.logger.debug("Done!")

    def clean_up(self):
        pass

    def get_reddit(self) -> Reddit:
        return praw.Reddit(client_id=self.config.reddit_config.client_id,
                           client_secret=self.config.reddit_config.client_secret,
                           username=self.config.reddit_config.username,
                           password=self.config.reddit_config.password,
                           user_agent=self.config.reddit_config.user_agent)

    def get_fresh_hot_posts(self) -> List[RedditPost]:
        limit: int = 5
        time_filter: str = 'day'
        reddit_posts: List[RedditPost] = []

        for subreddit in self.config.reddit_config.subreddits:
            submissions: ListingGenerator = self.reddit.subreddit(subreddit).top(limit=limit, time_filter=time_filter)
            for submission in submissions:
                title = submission.title
                post_id = submission.id
                votes = submission.score
                # shortlink example: 'https://redd.it/egud6i'
                link = submission.url
                unix_time = submission.created_utc
                self.logger.debug(f"Parsing: post_id={post_id}")
                a_reddit_post = RedditPost(title, post_id, votes, link, unix_time, False)
                reddit_posts.append(a_reddit_post)

        return reddit_posts

    @staticmethod
    def write_to_file(data: List[RedditPost], where: str = None) -> None:
        if not where:
            path = 'posts.json'
        else:
            path = 'archive.json'

        with open(path, 'w+') as write_file:
            write_file.write(json.dumps([post.__dict__ for post in data], indent=4))

    @staticmethod
    def read_from_file(where: str = None) -> List[RedditPost]:
        if not where:
            path = 'posts.json'
        else:
            path = 'archive.json'

        with open(path, 'r') as read_file:
            posts = json.load(read_file)

        return [RedditPost.from_json(post) for post in posts]


class RedditBot:
    def __init__(self):
        self.config = get_config()
        self.logger = get_logger()

    def parse_message(self, message_received: str) -> Union[list, str]:
        message = "Unrecognized command, the syntax is: reddit [oldest or top] [an integer]"
        message_as_list: List[str] = message_received.split()

        if len(message_as_list) is not 3:
            return message

        if 'oldest' in message_received:
            message = self.return_posts('oldest', self.clean_message(message_as_list))
        elif 'top' in message_received:
            message = self.return_posts('top', self.clean_message(message_as_list))

        return message

    def clean_message(self, message: List[str]) -> int:
        self.logger.debug("Sanitizing string for further processing")
        temp_integer = [value for value in message if value.isdigit()]
        if len(temp_integer) is not 1:
            return 1
        return int(temp_integer[0])

    def return_posts(self, criteria: str, amount: int) -> List[str]:
        pass


if __name__ == '__main__':
    reddit_scraper = RedditScraper()
    reddit_scraper.run()
