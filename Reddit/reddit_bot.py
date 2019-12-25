from Configuration.config import get_config


class RedditScraper:
    def __init__(self):
        self.config = get_config()


class RedditBot:
    def __init__(self):
        self.config = get_config()

    def parse_message(self, message_received: str) -> str:
        pass


if __name__ == '__main__':
    reddit_scraper = RedditScraper()
