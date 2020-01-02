import json
from typing import Dict, List, Set, Union

import praw
from praw import Reddit
from praw.models import ListingGenerator

from Configuration.config import get_config
from Configuration.logger import get_logger
from Reddit.reddit_post import RedditPost


class RedditScraper:
    PATH = 'posts.json'
    ARCHIVE = 'posts_archive.json'

    def __init__(self):
        self.config = get_config()
        self.reddit: Reddit = self.get_reddit()
        self.logger = get_logger()

    def run(self):
        previous_posts: List[RedditPost] = self.read_from_file()
        fresh_hot_posts: List[RedditPost] = self.get_fresh_hot_posts()
        merged_posts: List[RedditPost] = self.merge(new_list=fresh_hot_posts, existing_list=previous_posts)
        self.write_to_file(merged_posts)

    def clean_up(self):
        # todo: to be implemented
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
        all_subreddits: List[str] = list(
            set(self.config.reddit_config.subreddits + self.config.reddit_config.watchlist))

        for subreddit in all_subreddits:
            submissions: ListingGenerator = self.reddit.subreddit(subreddit).top(limit=limit, time_filter=time_filter)
            for submission in submissions:
                if not submission.stickied:
                    title = submission.title
                    post_id = submission.id
                    votes = submission.score
                    link = submission.url
                    is_self = submission.is_self
                    unix_time = int(submission.created_utc)
                    self.logger.debug(f"Parsing: post_id={post_id}")
                    a_reddit_post = RedditPost(title, subreddit, post_id, votes, link, unix_time, is_self, False)
                    reddit_posts.append(a_reddit_post)

        return reddit_posts

    @staticmethod
    def merge(new_list: List[RedditPost], existing_list: List[RedditPost]) -> List[RedditPost]:
        strictly_new_posts: Set[RedditPost] = set(new_list) - set(existing_list)
        dict_posts: Dict[str, RedditPost] = {post.id: post for post in existing_list}

        if len(dict_posts) > 0:
            for post in new_list:
                if dict_posts.get(post.id) is not None:
                    dict_posts.get(post.id).votes = post.votes

        return list(strictly_new_posts) + list(dict_posts.values())

    @staticmethod
    def update(unseen_list: List[RedditPost], existing_list: List[RedditPost]) -> List[RedditPost]:
        dict_posts: Dict[str, RedditPost] = {post.id: post for post in existing_list}

        for post in unseen_list:
            dict_posts.get(post.id).seen = True

        return list(dict_posts.values())

    @staticmethod
    def write_to_file(data: List[RedditPost], where: str = None) -> None:
        path = RedditScraper.ARCHIVE if where else RedditScraper.PATH
        with open(path, 'w+') as write_file:
            write_file.write(json.dumps([post.__dict__ for post in data], indent=4))

    @staticmethod
    def read_from_file(where: str = None) -> List[RedditPost]:
        path = RedditScraper.ARCHIVE if where else RedditScraper.PATH
        with open(path, 'r') as read_file:
            posts = json.load(read_file)

        return [RedditPost.from_json(post) for post in posts]


class RedditBot:
    OLDEST = 'oldest'
    TOP = 'top'

    def __init__(self):
        self.config = get_config()
        self.logger = get_logger()

    def parse_message(self, message_received: str) -> Union[list, str]:
        message = "Unrecognized command, the syntax is: reddit [oldest or top] [an integer]"
        message_as_list: List[str] = message_received.split()

        if len(message_as_list) != 3:
            return message

        if RedditBot.OLDEST in message_received:
            message = self.return_posts(RedditBot.OLDEST, self.clean_message(message_as_list))
        elif RedditBot.TOP in message_received:
            message = self.return_posts(RedditBot.TOP, self.clean_message(message_as_list))

        return message

    def clean_message(self, message: List[str]) -> int:
        self.logger.debug("Sanitizing string for further processing")
        temp_integer = [value for value in message if value.isdigit()]
        if len(temp_integer) != 1:
            return 1
        return int(temp_integer[0])

    def return_posts(self, criteria: str, amount: int) -> List[str]:
        self.logger.debug(f"The criteria: {criteria} has been picked")
        posts: List[RedditPost] = RedditScraper.read_from_file()
        unseen_posts: List[RedditPost] = [post for post in posts if not post.seen]
        formatted_list: List[str] = []

        if criteria == RedditBot.OLDEST:
            unseen_posts.sort(key=lambda x: x.unix_time)
        if criteria == RedditBot.TOP:
            unseen_posts.sort(key=lambda x: x.votes, reverse=True)

        for post in unseen_posts[:amount]:
            if post.is_self:
                string = f"{post.title} posted in <https://www.reddit.com/r/{post.subreddit}|{post.subreddit}>\n<https://redd.it/{post.id}>"
            else:
                string = f"<{post.link}|{post.title}> posted in <https://www.reddit.com/r/{post.subreddit}|{post.subreddit}>\n<https://redd.it/{post.id}>"
            formatted_list.append(string)
            post.seen = True

        RedditScraper.write_to_file(RedditScraper.update(unseen_list=unseen_posts[:amount], existing_list=posts))

        return formatted_list


class RedditWatcher:

    def __init__(self):
        self.config = get_config()
        self.logger = get_logger()

    def check_new(self) -> List[str]:
        subs: List[str] = self.config.reddit_config.watchlist
        posts: List[RedditPost] = RedditScraper.read_from_file()
        unseen_posts: List[RedditPost] = [post for post in posts if not post.seen and post.subreddit in subs]
        formatted_list: List[str] = []

        for post in unseen_posts:
            if post.is_self:
                string = f"{post.title} posted in <https://www.reddit.com/r/{post.subreddit}|{post.subreddit}>\n<https://redd.it/{post.id}>"
            else:
                string = f"<{post.link}|{post.title}> posted in <https://www.reddit.com/r/{post.subreddit}|{post.subreddit}>\n<https://redd.it/{post.id}>"
            formatted_list.append(string)
            post.seen = True

        RedditScraper.write_to_file(RedditScraper.update(unseen_list=unseen_posts, existing_list=posts))

        return formatted_list


if __name__ == '__main__':
    reddit_scraper = RedditScraper()
    reddit_scraper.run()
