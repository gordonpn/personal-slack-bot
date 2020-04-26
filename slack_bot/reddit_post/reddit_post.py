import json
from dataclasses import dataclass


@dataclass
class RedditPost:
    title: str
    subreddit: str
    post_id: str
    votes: int
    link: str
    unix_time: int
    is_self: bool
    seen: bool

    def to_json(self):
        return json.dumps(self.__dict__, default=lambda x: x.__dict__, indent=2)
