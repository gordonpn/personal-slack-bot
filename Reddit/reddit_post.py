import time


class RedditPost:

    def __init__(self, title, subreddit, post_id, votes, link, unix_time, is_self, seen):
        self.title: str = title
        self.subreddit: str = subreddit
        self.id: str = post_id
        self.votes: int = votes
        self.link: str = link
        self.unix_time: time = unix_time
        self.is_self: bool = is_self
        self.seen: bool = seen

    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    @classmethod
    def from_json(cls, json_data: dict):
        return cls(json_data.get('title'),
                   json_data.get('subreddit'),
                   json_data.get('id'),
                   json_data.get('votes'),
                   json_data.get('link'),
                   json_data.get('unix_time'),
                   json_data.get('is_self'),
                   json_data.get('seen'))
