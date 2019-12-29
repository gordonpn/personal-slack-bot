import time


class RedditPost:

    def __init__(self, title, post_id, votes, link, unix_time, seen):
        self.title: str = title
        self.id: str = post_id
        self.votes: int = votes
        self.link: str = link
        self.unix_time: time = unix_time
        self.seen: bool = seen

    @classmethod
    def from_json(cls, json_data: dict):
        return cls(json_data.get('title'),
                   json_data.get('id'),
                   json_data.get('votes'),
                   json_data.get('link'),
                   json_data.get('unix_time'),
                   json_data.get('seen'))
