import logging
from typing import List

from reddit.reddit_post import RedditPost

logger = logging.getLogger("slack_bot")


class RedditWatcher:
    def __init__(self):
        self.config = get_config()
        self.logger = get_logger()

    def check_new(self) -> List[str]:
        subs: List[str] = self.config.reddit_config.watchlist
        posts: List[RedditPost] = RedditScraper.read_from_file()
        unseen_posts: List[RedditPost] = [
            post for post in posts if not post.seen and post.subreddit in subs
        ]
        formatted_list: List[str] = []

        for post in unseen_posts:
            if post.is_self:
                string = f"{post.title} posted in <https://www.reddit.com/r/{post.subreddit}|{post.subreddit}>\n<https://redd.it/{post.id}>"
            else:
                string = f"<{post.link}|{post.title}> posted in <https://www.reddit.com/r/{post.subreddit}|{post.subreddit}>\n<https://redd.it/{post.id}>"
            formatted_list.append(string)
            post.seen = True

        RedditScraper.write_to_file(
            RedditScraper.update(unseen_list=unseen_posts, existing_list=posts)
        )

        return formatted_list
